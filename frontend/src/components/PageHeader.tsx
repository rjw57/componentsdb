import { Row, Col, Button, Space, Menu, MenuProps, Typography } from "antd";
import { Link, useMatches } from "react-router-dom";

import { useAuth, useSignInOrSignUpModal } from "../hooks";

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

  const [showSignInOrUp, signInOrUpContextHolder] = useSignInOrSignUpModal();

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
      {isSignedIn && (
        <Col>
          <Typography.Text>{auth.user?.displayName}</Typography.Text>
        </Col>
      )}
      <Col>
        <Space size="middle">
          {!isSignedIn && (
            <>
              <Button
                size="large"
                type="text"
                onClick={() => {
                  auth && auth.dismissSignInError();
                  showSignInOrUp("sign_in");
                }}
              >
                Sign in
              </Button>
              <Button
                size="large"
                onClick={() => {
                  auth && auth.dismissSignUpError();
                  showSignInOrUp("sign_up");
                }}
              >
                Sign up
              </Button>
              {signInOrUpContextHolder}
            </>
          )}
          {isSignedIn && (
            <>
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
      </Col>
    </Row>
  );
};

export default PageHeader;
