import React from "react";

import { ApolloError } from "@apollo/client";
import { AuthErrorType } from "../__generated__/gql/graphql";

export interface AuthContextCredentials {
  accessToken?: string;
  refreshToken?: string;
  expiresAt?: Date;
}

export interface AuthContextUser {
  id: string;
  displayName: string;
  avatarUrl?: string | null;
}

export interface AuthContextError {
  error: AuthErrorType;
  detail: string;
}

export interface AuthContextCredentialFetchOptions {
  onError?: (response: { apolloError?: ApolloError; authError?: AuthContextError }) => void;
  onSuccess?: (response: { user: AuthContextUser; credentials: AuthContextCredentials }) => void;
}

export interface AuthContextValue {
  // Access credentials for the API.
  credentials?: AuthContextCredentials;

  // The current authenticated user.
  user?: AuthContextUser;

  // Flags indicating when authentication requests are in flight.
  isLoading: boolean;
  isRefreshingCredentials: boolean;

  // Errors from sign-in or sign-up.
  signInError?: AuthContextError;
  signUpError?: AuthContextError;

  // Google Federated Identity Provider details. This is not defined if the API does not support
  // using Google id tokens for authentication.
  google?: {
    clientId: string;
    provider: string;
  };

  // Sign out if currently authenticated. Does nothing if not authenticated.
  signOut: () => void;

  signUpWithFederatedCredential: (
    provider: string,
    credential: string,
    options?: AuthContextCredentialFetchOptions,
  ) => void;

  signInWithFederatedCredential: (
    provider: string,
    credential: string,
    options?: AuthContextCredentialFetchOptions,
  ) => void;

  // Force a refresh of access credentials.
  refreshCredentials: (options?: AuthContextCredentialFetchOptions) => void;

  authenticatedFetch: (info: RequestInfo | URL, init?: RequestInit) => Promise<Response>;
}

export const AuthContext = React.createContext<AuthContextValue | null>(null);

export default AuthContext;
