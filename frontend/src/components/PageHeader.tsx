import { Row, Col, Button, Space, Menu, MenuProps, Typography } from "antd";

import { GoogleOAuthProvider, GoogleLogin } from "@react-oauth/google";
import { useAuth } from "../hooks";
import { Link, useMatches } from "react-router-dom";

type MenuItem = Required<MenuProps>["items"][number];

const navMenuItems: MenuItem[] = [
  {
    label: <Link to="/">Index</Link>,
    key: "index",
  },
  {
    label: <Link to="/api">GraphQL</Link>,
    key: "api",
  },
];

export const PageHeader = () => {
  const auth = useAuth();
  const routeMatches = useMatches();

  const user = auth?.user;
  const isSignedIn = !!user;
  const googleClientId = auth?.google?.clientId ?? "";
  console.log("auth", isSignedIn, user);

  if (auth?.signUpError) {
    console.log("sign up error", auth?.signUpError);
  }
  if (auth?.signInError) {
    console.log("sign in error", auth?.signInError);
  }

  return (
    <Row gutter={16}>
      <Col>
        <Typography.Text strong>Components Database</Typography.Text>
      </Col>
      <Col flex="auto">
        <Menu
          mode="horizontal"
          items={navMenuItems}
          theme="dark"
          selectedKeys={routeMatches.map(({ handle }) => `${handle}`)}
        />
      </Col>
      <Col>
        <GoogleOAuthProvider clientId={googleClientId}>
          <Space>
            {auth?.google && (
              <>
                <GoogleLogin
                  text="signin_with"
                  onSuccess={({ credential }) => {
                    credential &&
                      auth.signInWithFederatedCredential(auth?.google?.provider ?? "", credential);
                  }}
                />
                <GoogleLogin
                  text="signup_with"
                  onSuccess={({ credential }) => {
                    credential &&
                      auth.signUpWithFederatedCredential(auth?.google?.provider ?? "", credential);
                  }}
                />
              </>
            )}
            {!isSignedIn && (
              <>
                <Button size="large" type="text">
                  Sign in
                </Button>
                <Button size="large">Sign up</Button>
              </>
            )}
            {isSignedIn && (
              <>
                {auth?.user && <div>{auth.user.displayName}</div>}
                <Button
                  size="large"
                  onClick={() => {
                    auth && auth.signOut();
                  }}
                >
                  Sign out
                </Button>
              </>
            )}
          </Space>
        </GoogleOAuthProvider>
      </Col>
    </Row>
  );
};

export default PageHeader;
