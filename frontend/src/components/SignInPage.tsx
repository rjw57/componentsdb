import React from "react";
import { GoogleOAuthProvider, GoogleLogin } from "@react-oauth/google";
import { Typography, Flex, Divider } from "antd";

import { DefaultPage } from ".";
import { useAuth } from "../hooks";

export const SignInPage: React.FC = () => {
  const auth = useAuth();

  return (
    <DefaultPage>
      <Typography.Title>Sign in</Typography.Title>
      <Typography.Text>
        Use one of the sign in providers below to sign in to the application.
      </Typography.Text>
      <Divider />
      <Flex vertical gap={16}>
        {auth?.google && (
          <>
            <GoogleOAuthProvider clientId={`${auth.google.clientId}`}>
              <GoogleLogin
                text="signin_with"
                onSuccess={({ credential }) => {
                  credential &&
                    auth.google &&
                    auth.signInWithFederatedCredential(auth.google.provider, credential);
                }}
              />
            </GoogleOAuthProvider>
          </>
        )}
      </Flex>
    </DefaultPage>
  );
};

export default SignInPage;
