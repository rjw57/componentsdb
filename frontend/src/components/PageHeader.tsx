import { Row, Col, Button, Space, Menu, MenuProps, Typography } from "antd";

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
              <Button size="large" type="text">
                <Link to="/signin">Sign in</Link>
              </Button>
              <Button size="large">
                <Link to="/signup">Sign up</Link>
              </Button>
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
