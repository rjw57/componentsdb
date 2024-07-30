import React from "react";
import { GoogleOAuthProvider, GoogleLogin } from "@react-oauth/google";
import { Divider, theme, Typography, Flex, Alert } from "antd";
import { Link } from "react-router-dom";

import { AuthContextError } from "../contexts";
import { useAuth } from "../hooks";
import { AuthErrorType } from "../__generated__/gql/graphql";

const errorDescriptions = new Map<AuthErrorType, React.ReactNode>([
  [
    AuthErrorType.UserAlreadySignedUp,
    <>
      A user has already signed up with that account. You can try{" "}
      <Link to="/signin">signing in</Link> instead.
    </>,
  ],
  [
    AuthErrorType.UserNotSignedUp,
    <>
      There is no account associated with that sign in. You can try{" "}
      <Link to="/signup">signing up</Link> instead.
    </>,
  ],
  [
    AuthErrorType.InvalidFederatedCredential,
    <>There as a problem with the response from the sign in provider. Please try again.</>,
  ],
]);

export interface SignInOrUpFormProps {
  type?: "sign_in" | "sign_up";
  onSuccess?: () => void;
}

const SignInOrUpFormContent: React.FC<SignInOrUpFormProps> = ({
  type = "sign_in",
  onSuccess = () => {},
}) => {
  const { token } = theme.useToken();
  const auth = useAuth();

  const isGoogleSignInSupported = !!auth?.google;

  const describeError = ({ error, detail }: AuthContextError) =>
    errorDescriptions.get(error) ?? detail;

  return (
    <Flex vertical gap={4 * token.sizeUnit}>
      <div style={{ textAlign: "center" }}>
        {type === "sign_in" && (
          <>
            <Typography.Title>Sign in</Typography.Title>
            <Typography.Text>Use one of the providers below to sign in.</Typography.Text>
          </>
        )}
        {type === "sign_up" && (
          <>
            <Typography.Title>Sign up</Typography.Title>
            <Typography.Text>
              Use one of the providers below to create a new account.
            </Typography.Text>
          </>
        )}
      </div>
      {type === "sign_in" && auth?.signInError && (
        <Alert
          message="There was a problem signing you in"
          description={describeError(auth.signInError)}
          type="error"
          closable
          onClose={auth.dismissSignInError}
        />
      )}
      {type === "sign_up" && auth?.signUpError && (
        <Alert
          message="There was a problem signing you up"
          description={describeError(auth.signUpError)}
          type="error"
          closable
          onClose={auth.dismissSignUpError}
        />
      )}
      <Flex vertical gap={4 * token.sizeUnit} style={{ marginTop: token.marginLG }}>
        {isGoogleSignInSupported && (
          <GoogleLogin
            theme="outline"
            size="large"
            text={type === "sign_in" ? "continue_with" : "signup_with"}
            context={type === "sign_in" ? "signin" : "signup"}
            width={Math.floor(0.8 * token.screenSM - token.paddingLG * 2)}
            onSuccess={({ credential }) => {
              if (!credential || !auth.google) {
                return;
              }
              if (type === "sign_in") {
                auth.signInWithFederatedCredential(auth.google.provider, credential, {
                  onSuccess,
                });
              }
              if (type === "sign_up") {
                auth.signUpWithFederatedCredential(auth.google.provider, credential, {
                  onSuccess,
                });
              }
            }}
          />
        )}
      </Flex>
      <Divider>OR</Divider>
      <div style={{ textAlign: "center" }}>
        {type === "sign_in" && (
          <Typography.Text>
            Don't have an account? <Link to="/signup">Sign up now.</Link>
          </Typography.Text>
        )}
        {type === "sign_up" && (
          <Typography.Text>
            Already registered? <Link to="/signin">Sign in now.</Link>
          </Typography.Text>
        )}
      </div>
    </Flex>
  );
};

export const SignInOrUpForm: React.FC<SignInOrUpFormProps> = (props) => {
  const auth = useAuth();
  return (
    <GoogleOAuthProvider clientId={`${auth?.google?.clientId}`}>
      <SignInOrUpFormContent {...props} />
    </GoogleOAuthProvider>
  );
};

export default SignInOrUpForm;
