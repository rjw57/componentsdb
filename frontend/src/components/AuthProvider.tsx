import React from "react";

import { useTimeout } from "usehooks-ts";

import {
  useFederatedIdentitiyProviders,
  useCredentialsFromFederatedCredential,
  useRefreshCredentials,
} from "../hooks";
import { unauthenticatedClient } from "../apolloClient";
import {
  AuthContext,
  AuthContextValue,
  AuthContextCredentialFetchOptions,
  AuthContextCredentials,
  AuthContextUser,
} from "../contexts";

const GOOGLE_CLIENT_ID = process.env.REACT_APP_GOOGLE_CLIENT_ID ?? "";

export interface AuthProviderProps {
  children?: React.ReactNode;
}

interface CredentialsResponse {
  credentials: AuthContextCredentials;
  user: AuthContextUser;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  // A promise which is defined if there is a credentials request in flight.
  const [credentialsPromise, setCredentialsPromise] =
    React.useState<Promise<CredentialsResponse>>();

  const [credentials, setCredentials] = React.useState<AuthContextValue["credentials"]>();
  const [signInError, setSignInError] = React.useState<AuthContextValue["signInError"]>();
  const [signUpError, setSignUpError] = React.useState<AuthContextValue["signUpError"]>();
  const [user, setUser] = React.useState<AuthContextValue["user"]>();

  // Set expiresIn to null to disable refresh timeout.
  const [expiresInMs, setExpiresInMs] = React.useState<number | null>(null);
  useTimeout(() => {
    refreshCredentials();
  }, expiresInMs);

  const { data: federatedIdentityProviders, loading: isLoadingFederatedIdentitiyProviders } =
    useFederatedIdentitiyProviders({
      client: unauthenticatedClient,
    });

  const googleProvider = React.useMemo(() => {
    let provider;
    (federatedIdentityProviders?.auth.federatedIdentityProviders ?? []).forEach(
      ({ name, issuer, audience }) => {
        if (audience === GOOGLE_CLIENT_ID && issuer === "https://accounts.google.com") {
          provider = name;
        }
      },
    );
    return provider;
  }, [federatedIdentityProviders]);

  const [credentialsFromFederatedCredential, { loading: isLoadingCredentials }] =
    useCredentialsFromFederatedCredential({
      client: unauthenticatedClient,
    });

  const [refreshCredentialsMutation, { loading: isRefreshingCredentials }] = useRefreshCredentials({
    client: unauthenticatedClient,
  });

  const handleAuthResult = (result: {
    user: { id: string; displayName: string; avatarUrl?: string | null };
    accessToken: string;
    refreshToken: string;
    expiresIn: number;
  }): CredentialsResponse => {
    const {
      user: { id, displayName, avatarUrl },
      accessToken,
      refreshToken,
      expiresIn,
    } = result;
    const expiresAt = new Date();
    expiresAt.setSeconds(expiresAt.getSeconds() + expiresIn);
    const credentials = {
      accessToken,
      refreshToken,
      expiresAt,
    };
    const user = {
      id,
      displayName,
      avatarUrl,
    };

    setCredentials(credentials);
    setUser(user);

    // Schedule credential reset up to a minute before expected expiry to ensure we refresh in good
    // time. Note that it is safe for us to miss the refresh window because authenticatedFetch()
    // will refresh credentials "just in time" if necessary.
    setExpiresInMs(Math.max(expiresIn - 60, 60) * 1e3);

    return { credentials, user };
  };

  const signOut = () => {
    setCredentialsPromise(undefined);
    setUser(undefined);
    setCredentials(undefined);
    setExpiresInMs(null);
  };

  const refreshCredentials = (
    options?: AuthContextCredentialFetchOptions,
  ): Promise<CredentialsResponse> => {
    const { onError, onSuccess } = options ?? {};

    if (!credentials || !credentials.refreshToken) {
      throw new Error("Attempt to refresh credentials when no credentials active.");
    }
    if (isRefreshingCredentials) {
      throw new Error("Attempt to refresh credentials when refresh is in flight.");
    }
    if (isLoadingCredentials) {
      throw new Error("Attempt to refresh credentials when sigining in.");
    }

    // Reset expires in so that we will re-start the timer when we get new credentials.
    setExpiresInMs(null);

    // Update the credentials promise.
    const { refreshToken } = credentials;
    const credentialsPromise = new Promise<CredentialsResponse>((resolve, reject) => {
      refreshCredentialsMutation({
        variables: {
          input: {
            refreshToken,
          },
        },

        onError: (apolloError) => {
          onError && onError({ apolloError });
          reject({ apolloError });
        },

        onCompleted: ({ auth: { refreshCredentials: result } }) => {
          if (result.__typename === "AuthError") {
            signOut();
            const { error, detail } = result;
            onError && onError({ authError: { error, detail } });
            reject({ authError: { error, detail } });
          } else {
            const credentialsResponse = handleAuthResult(result);
            setCredentialsPromise(undefined);
            onSuccess && onSuccess(credentialsResponse);
            resolve(credentialsResponse);
          }
        },
      });
    });
    setCredentialsPromise(credentialsPromise);
    return credentialsPromise;
  };

  const signInOrSignUpWithFederatedCredentials = (
    provider: string,
    credential: string,
    isNewUser: boolean,
    options?: AuthContextCredentialFetchOptions,
  ): Promise<CredentialsResponse> => {
    const { onError, onSuccess } = options ?? {};
    signOut();
    if (isNewUser) {
      setSignUpError(undefined);
    } else {
      setSignInError(undefined);
    }
    // Update the credentials promise.
    const credentialsPromise = new Promise<CredentialsResponse>((resolve, reject) => {
      credentialsFromFederatedCredential({
        variables: {
          input: {
            provider,
            credential,
            isNewUser,
          },
        },

        onError: (apolloError) => {
          onError && onError({ apolloError });
          reject({ apolloError });
        },

        onCompleted: ({ auth: { credentialsFromFederatedCredential: result } }) => {
          if (result.__typename === "AuthError") {
            if (isNewUser) {
              setSignUpError({ error: result.error, detail: result.detail });
            } else {
              setSignInError({ error: result.error, detail: result.detail });
            }
            const { error, detail } = result;
            onError && onError({ authError: { error, detail } });
            reject({ authError: { error, detail } });
          } else {
            const credentialsResponse = handleAuthResult(result);
            setCredentialsPromise(undefined);
            onSuccess && onSuccess(credentialsResponse);
            resolve(credentialsResponse);
          }
        },
      });
    });
    setCredentialsPromise(credentialsPromise);
    return credentialsPromise;
  };

  // A wrapper around fetch() which uses the current authentication credentials and attempts to
  // transparently refresh credentials on 403 errors. The transparent refresh should only happen
  // rarely since we pro-actively refresh credentials via a timer.
  const authenticatedFetch = async (
    input: RequestInfo | URL,
    init?: RequestInit,
  ): Promise<Response> => {
    const response = await fetch(input, {
      ...init,
      headers: {
        ...(init?.headers ?? {}),
        ...(credentials ? { Authorization: `Bearer ${credentials.accessToken}` } : {}),
      },
    });

    // If the response was not 403, or if we have no credentials, we can return it immediately.
    if (response.status !== 403 || !credentials) {
      return response;
    }

    // Otherwise we need to try and kick off a refresh. (Or wait for the one in-flight.)
    const credentialsResponse = await (credentialsPromise || refreshCredentials());

    // Retry the request with the new credentials.
    return await fetch(input, {
      ...init,
      headers: {
        ...(init?.headers ?? {}),
        Authorization: `Bearer ${credentialsResponse.credentials.accessToken}`,
      },
    });
  };

  return (
    <AuthContext.Provider
      value={{
        credentials,
        user,

        isLoading: isLoadingCredentials || isLoadingFederatedIdentitiyProviders,
        isRefreshingCredentials,

        signInError,
        signUpError,

        ...(googleProvider
          ? {
              google: {
                clientId: GOOGLE_CLIENT_ID,
                provider: googleProvider,
              },
            }
          : {}),

        signInWithFederatedCredential: (
          provider: string,
          credential: string,
          options?: AuthContextCredentialFetchOptions,
        ) => {
          signInOrSignUpWithFederatedCredentials(provider, credential, false, options);
        },
        signUpWithFederatedCredential: (
          provider: string,
          credential: string,
          options?: AuthContextCredentialFetchOptions,
        ) => {
          signInOrSignUpWithFederatedCredentials(provider, credential, true, options);
        },
        signOut,
        refreshCredentials,
        authenticatedFetch,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export default AuthProvider;
