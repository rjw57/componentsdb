import React from "react";

import { AuthErrorType } from "../__generated__/gql/graphql";
import { useFederatedIdentitiyProviders, useCredentialsFromFederatedCredential } from "../hooks";
import { unauthenticatedClient } from "../apolloClient";

/*
    <GoogleOAuthProvider clientId={process.env.REACT_APP_GOOGLE_CLIENT_ID ?? ""}>
      <App />
    </GoogleOAuthProvider>
  */
const GOOGLE_CLIENT_ID = process.env.REACT_APP_GOOGLE_CLIENT_ID ?? "";

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

export interface AuthState {}

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

export interface AuthProviderProps {
  children?: React.ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [credentials, setCredentials] = React.useState<Credentials | undefined>();
  const [signInError, setSignInError] = React.useState<AuthError | undefined>();
  const [signUpError, setSignUpError] = React.useState<AuthError | undefined>();
  const [user, setUser] = React.useState<User | undefined>();

  const { data: federatedIdentityProviders, loading: isLoadingFederatedIdentitiyProviders } =
    useFederatedIdentitiyProviders({
      client: unauthenticatedClient,
    });

  const googleProvider = React.useMemo(() => {
    let provider = "";
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

  const signInOrSignUpWithFederatedCredentials = (
    provider: string,
    credential: string,
    isNewUser: boolean,
  ) => {
    if (isNewUser) {
      setSignUpError(undefined);
    } else {
      setSignInError(undefined);
    }
    setUser(undefined);
    credentialsFromFederatedCredential({
      variables: {
        input: {
          provider,
          credential,
          isNewUser,
        },
      },

      onCompleted: ({ auth: { credentialsFromFederatedCredential: result } }) => {
        if (result.__typename === "AuthError") {
          if (isNewUser) {
            setSignUpError({ error: result.error, detail: result.detail });
          } else {
            setSignInError({ error: result.error, detail: result.detail });
          }
        } else {
          const {
            user: { id, displayName, avatarUrl },
            accessToken,
            refreshToken,
            expiresIn,
          } = result;
          const expiresAt = new Date();
          expiresAt.setSeconds(expiresAt.getSeconds() + expiresIn);
          setCredentials({
            accessToken,
            refreshToken,
            expiresAt,
          });
          setUser({
            id,
            displayName,
            avatarUrl,
          });
        }
      },
    });
  };

  return (
    <AuthContext.Provider
      value={{
        credentials,
        user,

        isLoading: isLoadingCredentials || isLoadingFederatedIdentitiyProviders,

        signInError,
        signUpError,

        google: {
          clientId: GOOGLE_CLIENT_ID,
          provider: googleProvider,
        },

        signInWithFederatedCredential: (provider: string, credential: string) => {
          signInOrSignUpWithFederatedCredentials(provider, credential, false);
        },

        signUpWithFederatedCredential: (provider: string, credential: string) => {
          signInOrSignUpWithFederatedCredentials(provider, credential, true);
        },
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export default AuthProvider;
