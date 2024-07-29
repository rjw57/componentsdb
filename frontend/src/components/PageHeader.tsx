import { Row, Col, Button, Space } from "antd";

import { GoogleOAuthProvider, GoogleLogin } from "@react-oauth/google";
import { useAuth } from "../hooks";

export const PageHeader = () => {
  const auth = useAuth();
  const googleClientId = auth?.google.clientId ?? "";

  if (auth?.signUpError) {
    console.log("sign up error", auth?.signUpError);
  }
  if (auth?.signInError) {
    console.log("sign in error", auth?.signInError);
  }
  if (auth?.credentials) {
    console.log("credentials", auth.credentials);
  }

  return (
    <Row>
      <Col flex="auto" />
      <Col>
        <GoogleOAuthProvider clientId={googleClientId}>
          <Space>
            {auth !== null && auth?.google.provider !== "" && (
              <>
                {auth?.user && <div>{auth.user.displayName}</div>}
                <GoogleLogin
                  text="signin_with"
                  onSuccess={({ credential }) => {
                    credential &&
                      auth.signInWithFederatedCredential(auth.google.provider, credential);
                  }}
                />
                <GoogleLogin
                  text="signup_with"
                  onSuccess={({ credential }) => {
                    credential &&
                      auth.signUpWithFederatedCredential(auth.google.provider, credential);
                  }}
                />
              </>
            )}
            <Button size="large" type="text">
              Sign in
            </Button>
            <Button size="large">Sign up</Button>
          </Space>
        </GoogleOAuthProvider>
      </Col>
    </Row>
  );
};

export default PageHeader;
