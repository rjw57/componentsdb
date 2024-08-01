import React from "react";
import { GoogleOAuthProvider, GoogleLogin } from "@react-oauth/google";
import { useResizeObserver } from "usehooks-ts";
import { Alert, Button } from "flowbite-react";

import { AuthErrorType } from "../__generated__/gql/graphql";
import useSignIn from "../hooks/useSignIn";
import type { SignInError } from "../hooks/useSignIn";
import { googleClientId } from "../config";

export interface SignInOrUpFormProps {
  initialType?: "sign_in" | "sign_up";
  onSuccess?: () => void;
}

export const SignInOrUpForm: React.FC<SignInOrUpFormProps> = ({
  initialType = "sign_in",
  onSuccess = () => {},
}) => {
  const [signInError, setSignInError] = React.useState<SignInError | null>(null);
  const [type, setType] = React.useState<"sign_in" | "sign_up">(initialType);
  const { googleProviderName, signInWithFederatedCredential } = useSignIn();

  // Since the Google sign in button size needs to be set explicitly, we use a horrible
  // ResizeObserver hack to compute the width.
  const googleHackRef = React.useRef<HTMLDivElement>(null);
  const { width: googleButtonWidth = 50 } = useResizeObserver({ ref: googleHackRef });

  const errorDescriptions = new Map<AuthErrorType, React.ReactNode>([
    [
      AuthErrorType.UserAlreadySignedUp,
      <>
        <div className="mb-4">A user has already signed up with that account.</div>
        <Button
          size="xs"
          onClick={() => {
            setSignInError(null);
            setType("sign_in");
          }}
        >
          Sign in instead
        </Button>
      </>,
    ],
    [
      AuthErrorType.UserNotSignedUp,
      <>
        <div className="mb-4">There is no account associated with that sign in.</div>
        <Button
          size="xs"
          onClick={() => {
            setSignInError(null);
            setType("sign_up");
          }}
        >
          Sign up instead
        </Button>
      </>,
    ],
    [
      AuthErrorType.InvalidFederatedCredential,
      <>There is a problem with the response from the sign in provider. Please try again.</>,
    ],
  ]);

  const describeError = (error: SignInError): React.ReactNode => {
    if (error.type === "auth") {
      return errorDescriptions.get(error.authError.error) ?? error.authError.detail;
    }
    console.error("Unknown error signing in.", error);
    return "There was a problem with sign in. Please try again.";
  };

  return (
    <div className="space-y-6">
      <h4 className="text-xl font-medium text-gray-900 dark:text-white">
        {type === "sign_in" && "Sign in"}
        {type === "sign_up" && "Sign up"}
      </h4>
      {type === "sign_in" && (
        <div className="text-sm">
          Use one of the providers below to sign in with an existing account.
        </div>
      )}
      {type === "sign_up" && (
        <div className="text-sm">Use one of the providers below to register a new account.</div>
      )}
      {signInError && (
        <Alert
          color="failure"
          additionalContent={describeError(signInError)}
          onDismiss={() => {
            setSignInError(null);
          }}
        >
          {type === "sign_in" && (
            <span className="font-medium">There was a problem signing in.</span>
          )}
          {type === "sign_up" && (
            <span className="font-medium">There was a problem signing up.</span>
          )}
        </Alert>
      )}
      {googleProviderName && (
        <>
          <div className="w-full" ref={googleHackRef} />
          <GoogleOAuthProvider clientId={googleClientId}>
            <GoogleLogin
              theme="outline"
              size="large"
              text={type === "sign_in" ? "continue_with" : "signup_with"}
              context={type === "sign_in" ? "signin" : "signup"}
              width={googleButtonWidth}
              onSuccess={({ credential }) => {
                if (!credential) {
                  console.error("Did not receive a Google credential despite sign in succeeding.");
                  return;
                }
                signInWithFederatedCredential(googleProviderName, credential, {
                  isNewUser: type === "sign_up",
                  onSuccess,
                  onError: setSignInError,
                });
              }}
            />
          </GoogleOAuthProvider>
        </>
      )}
      {type == "sign_in" && (
        <div className="flex justify-between text-sm font-medium text-gray-500 dark:text-gray-300">
          Not registered?&nbsp;
          <a
            href="#"
            onClick={(e) => {
              setType("sign_up");
              e.preventDefault();
            }}
            className="text-cyan-700 hover:underline dark:text-cyan-500"
          >
            Create a new account
          </a>
        </div>
      )}
      {type == "sign_up" && (
        <div className="flex justify-between text-sm font-medium text-gray-500 dark:text-gray-300">
          Already registered?&nbsp;
          <a
            href="#"
            onClick={(e) => {
              setType("sign_in");
              e.preventDefault();
            }}
            className="text-cyan-700 hover:underline dark:text-cyan-500"
          >
            Sign in
          </a>
        </div>
      )}
    </div>
  );
};

export default SignInOrUpForm;
