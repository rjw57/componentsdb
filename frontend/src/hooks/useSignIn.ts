import React from "react";
import { atom } from "nanostores";
import { useStore } from "@nanostores/react";
import { persistentMap } from "@nanostores/persistent";
import type { ApolloError } from "@apollo/client";

import { unauthenticatedClient } from "../apolloClient";
import { googleClientId } from "../config";
import useCredentialsFromFederatedCredential from "./useCredentialsFromFederatedCredential";
import useFederatedIdentitiyProviders from "./useFederatedIdentitiyProviders";
import useRefreshCredentials from "./useRefreshCredentials";
import type { AuthError } from "../__generated__/gql/graphql";

// State which is global to the application. We persist the access and refresh tokens so that the
// user sign is is not lost between page loads.
const $credentials = persistentMap<{
  userId?: string;
  userDisplayName?: string;
  userAvatarUrl?: string;
  userEmail?: string;
  accessToken?: string;
  refreshToken?: string;
}>("auth.credentials", {});
const $googleProviderName = atom<string | null>(null);

interface CredentialResponse {
  user: { id: string; displayName: string; avatarUrl?: string | null; email?: string | null };
  accessToken: string;
  refreshToken: string;
}

export type SignInError =
  | {
      type: "graphql";
      graphQLError: ApolloError;
    }
  | {
      type: "auth";
      authError: AuthError;
    };

// A global promise which represents any in-flight credential refresh request. We use a global
// promise so that the authenticated fetch can make sure it only attempts to refresh the token once
// even if there are parallel fetch requests.
let inFlightRefresh: Promise<CredentialResponse> | null;

export const useSignIn = () => {
  const credentials = useStore($credentials);
  const googleProviderName = useStore($googleProviderName);
  const { accessToken, refreshToken } = credentials;
  const isSignedIn = !!(accessToken && refreshToken && credentials.userId);
  const authenticatedUser = isSignedIn
    ? {
        id: credentials.userId,
        displayName: credentials.userDisplayName,
        avatarUrl: credentials.userAvatarUrl,
        email: credentials.userEmail,
      }
    : null;

  const [credentialsFromFederatedCredential] = useCredentialsFromFederatedCredential({
    client: unauthenticatedClient,
  });

  const [refreshCredentials] = useRefreshCredentials({
    client: unauthenticatedClient,
  });

  // Query the federated identity providers supported by the backend.
  useFederatedIdentitiyProviders({
    client: unauthenticatedClient,
    onCompleted: (result) => {
      result.auth.federatedIdentityProviders.forEach(({ name, issuer, audience }) => {
        if (issuer === "https://accounts.google.com" && audience === googleClientId) {
          $googleProviderName.set(name);
        }
      });
    },
  });

  const handleCredentialResponse = ({
    accessToken,
    refreshToken,
    user: { id: userId, displayName: userDisplayName, avatarUrl: userAvatarUrl, email: userEmail },
  }: CredentialResponse) => {
    $credentials.set({
      accessToken,
      refreshToken,
      userId,
      userDisplayName,
      userEmail: userEmail !== null ? userEmail : undefined,
      userAvatarUrl: userAvatarUrl !== null ? userAvatarUrl : undefined,
    });
  };

  const signOut = () => {
    $credentials.set({});
  };

  const signInWithFederatedCredential = async (
    provider: string,
    credential: string,
    options?: {
      isNewUser?: boolean;
      onSuccess?: () => void;
      onError?: (error: SignInError) => void;
    },
  ) => {
    const { isNewUser = false, onSuccess = () => {}, onError = () => {} } = options ?? {};
    // Make sure we're not signed in.
    signOut();

    // Kick off the sign in process.
    const result = await credentialsFromFederatedCredential({
      variables: {
        input: {
          provider,
          credential,
          isNewUser,
        },
      },
    });
    result.errors;

    if (!result.data) {
      throw new Error("Error calling sign in");
    }

    const response = result.data.auth.credentialsFromFederatedCredential;
    if (response.__typename === "AuthError") {
      onError({ type: "auth", authError: response });
    } else {
      handleCredentialResponse(response);
      onSuccess();
    }
  };

  // A wrapper around fetch() which uses the current authentication credentials and attempts to
  // transparently refresh credentials on 403 errors. The transparent refresh should only happen
  // rarely since we pro-actively refresh credentials via a timer.
  const authenticatedFetch = React.useMemo(
    () =>
      async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
        const response = await fetch(input, {
          ...init,
          headers: {
            ...(init?.headers ?? {}),
            ...(isSignedIn ? { Authorization: `Bearer ${accessToken}` } : {}),
          },
        });

        if (!isSignedIn || response.status !== 403) {
          return response;
        }

        // If we got here, the original request was forbidden but we are signed in so we can attempt
        // to use the refresh token.

        // Kick off a refresh request if one is not already in flight.
        if (!inFlightRefresh) {
          inFlightRefresh = new Promise((resolve, reject) => {
            refreshCredentials({
              variables: {
                input: {
                  refreshToken,
                },
              },
              onError: (errors) => {
                reject(errors);
              },
              onCompleted: ({ auth: { refreshCredentials: response } }) => {
                if (response.__typename == "AuthError") {
                  // If we can't refresh, the best we can do is sign the user out.
                  signOut();
                  reject(response);
                } else {
                  handleCredentialResponse(response);
                  const { accessToken, refreshToken, user } = response;
                  resolve({ accessToken, refreshToken, user });
                }
              },
            });
          });
        }

        // Await the result of the in-flight refresh request.
        const { accessToken: newAccessToken } = await inFlightRefresh;
        inFlightRefresh = null;

        // Retry the request with the new credentials. This time any 403 errors will be reported
        // back to the caller.
        return await fetch(input, {
          ...init,
          headers: {
            ...(init?.headers ?? {}),
            Authorization: `Bearer ${newAccessToken}`,
          },
        });
      },
    [isSignedIn, accessToken],
  );

  return {
    authenticatedUser,
    accessToken,
    refreshToken,
    isSignedIn,
    signOut,
    signInWithFederatedCredential,
    googleProviderName,
    authenticatedFetch,
  };
};

export default useSignIn;
