import { theme, Row, Col, Button, Space, Menu, MenuProps, Typography } from "antd";
import { Link, useMatches } from "react-router-dom";

import { useAuth, useSignInOrSignUpModal } from "../hooks";
import { UserDropdown } from ".";

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
  const { token } = theme.useToken();

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
      <Col>
        <Space size="middle">
          {!isSignedIn && (
            <>
              <Button
                type="text"
                onClick={() => {
                  auth && auth.dismissSignInError();
                  showSignInOrUp("sign_in");
                }}
              >
                Sign in
              </Button>
              <Button
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
            <UserDropdown
              avatarUrl={auth.user?.avatarUrl ? auth.user.avatarUrl : undefined}
              avatarLabel={`${auth.user?.displayName}`.substring(0, 1)}
              displayName={auth.user?.displayName}
              style={{ marginRight: -token.padding }}
            />
          )}
        </Space>
      </Col>
    </Row>
  );
};

export default PageHeader;
