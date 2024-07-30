import React from "react";
import { GoogleOAuthProvider, GoogleLogin } from "@react-oauth/google";
import { Divider, theme, Typography, Flex, Alert } from "antd";
import { useResizeObserver } from "usehooks-ts";

import { AuthContextError } from "../contexts";
import { useAuth } from "../hooks";
import { AuthErrorType } from "../__generated__/gql/graphql";

export interface SignInOrUpFormProps {
  initialType?: "sign_in" | "sign_up";
  onSuccess?: () => void;
}

const SignInOrUpFormContent: React.FC<SignInOrUpFormProps> = ({
  initialType = "sign_in",
  onSuccess = () => {},
}) => {
  const [type, underlyingSetType] = React.useState<"sign_in" | "sign_up">(initialType);
  const { token } = theme.useToken();
  const auth = useAuth();

  const setType = (type: "sign_in" | "sign_up") => {
    auth && auth.dismissSignUpError();
    auth && auth.dismissSignInError();
    underlyingSetType(type);
  };

  // Since the Google sign in button size needs to be set explicitly, we use a horrible
  // ResizeObserver hack to compute the width.
  const googleHackRef = React.useRef<HTMLDivElement>(null);
  const { width: googleButtonWidth = 50 } = useResizeObserver({ ref: googleHackRef });

  const isGoogleSignInSupported = !!auth?.google;

  const errorDescriptions = new Map<AuthErrorType, React.ReactNode>([
    [
      AuthErrorType.UserAlreadySignedUp,
      <>
        A user has already signed up with that account. You can try{" "}
        <Typography.Link
          onClick={() => {
            setType("sign_in");
          }}
        >
          signing in
        </Typography.Link>{" "}
        instead.
      </>,
    ],
    [
      AuthErrorType.UserNotSignedUp,
      <>
        There is no account associated with that sign in. You can try{" "}
        <Typography.Link
          onClick={() => {
            setType("sign_up");
          }}
        >
          signing up
        </Typography.Link>{" "}
        instead.
      </>,
    ],
    [
      AuthErrorType.InvalidFederatedCredential,
      <>There as a problem with the response from the sign in provider. Please try again.</>,
    ],
  ]);

  const describeError = ({ error, detail }: AuthContextError) =>
    errorDescriptions.get(error) ?? detail;

  return (
    <Flex vertical gap={4 * token.sizeUnit}>
      <div style={{ textAlign: "center" }} ref={googleHackRef}>
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
      <Flex vertical align="center" gap={4 * token.sizeUnit} style={{ marginTop: token.margin }}>
        {isGoogleSignInSupported && (
          <GoogleLogin
            theme="outline"
            size="large"
            text={type === "sign_in" ? "continue_with" : "signup_with"}
            context={type === "sign_in" ? "signin" : "signup"}
            width={googleButtonWidth}
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
            Don't have an account?{" "}
            <Typography.Link
              onClick={() => {
                setType("sign_up");
              }}
            >
              Sign up now.
            </Typography.Link>
          </Typography.Text>
        )}
        {type === "sign_up" && (
          <Typography.Text>
            Already registered?{" "}
            <Typography.Link
              onClick={() => {
                setType("sign_in");
              }}
            >
              Sign in now.
            </Typography.Link>
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
