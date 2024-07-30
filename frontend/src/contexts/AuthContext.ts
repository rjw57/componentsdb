import React from "react";

import { AuthErrorType } from "../__generated__/gql/graphql";

interface Credentials {
  accessToken?: string;
  refreshToken?: string;
  expiresAt?: Date;
}

interface User {
  id: string;
  displayName: string;
  avatarUrl?: string | null;
}

interface AuthError {
  error: AuthErrorType;
  detail: string;
}

export interface AuthContextValue {
  credentials?: Credentials;
  user?: User;

  isLoading: boolean;

  signInError?: AuthError;
  signUpError?: AuthError;

  google: {
    clientId: string;
    provider: string;
  };

  signUpWithFederatedCredential: (provider: string, credential: string) => void;
  signInWithFederatedCredential: (provider: string, credential: string) => void;
}

export const AuthContext = React.createContext<AuthContextValue | null>(null);

export default AuthContext;
