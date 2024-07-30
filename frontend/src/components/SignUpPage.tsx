import React from "react";
import { GoogleOAuthProvider, GoogleLogin } from "@react-oauth/google";
import { Typography, Flex, Divider, Alert, Row, Col } from "antd";
import { Link } from "react-router-dom";

import { DefaultPage } from ".";
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
]);

export const SignUpPage: React.FC = () => {
  const auth = useAuth();

  return (
    <DefaultPage>
      <Row>
        <Col xs={0} md={6} xl={7} />
        <Col xs={24} md={12} xl={10}>
          <Typography.Title>Sign up</Typography.Title>
          <Typography.Text>
            Use one of the sign in providers below to sign up to the application.
          </Typography.Text>
          <Divider />
          <Flex vertical gap={24}>
            {auth?.signUpError && (
              <>
                <Alert
                  message="There was a problem signing you up"
                  description={
                    errorDescriptions.get(auth.signUpError.error) ?? auth.signUpError.detail
                  }
                  type="error"
                  closable
                  onClose={() => {
                    auth.dismissSignUpError();
                  }}
                />
              </>
            )}
            {auth?.google && (
              <>
                <GoogleOAuthProvider clientId={`${auth.google.clientId}`}>
                  <GoogleLogin
                    text="signup_with"
                    onSuccess={({ credential }) => {
                      credential &&
                        auth.google &&
                        auth.signUpWithFederatedCredential(auth.google.provider, credential);
                    }}
                  />
                </GoogleOAuthProvider>
              </>
            )}
          </Flex>
        </Col>
        <Col xs={0} md={6} xl={7} />
      </Row>
    </DefaultPage>
  );
};

export default SignUpPage;
