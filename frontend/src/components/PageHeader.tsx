import { Row, Col, Button, Space } from "antd";

import { useFederatedIdentitiyProviders } from "../hooks";

export const PageHeader = () => {
  const { data } = useFederatedIdentitiyProviders();
  console.log(data);
  return (
    <Row>
      <Col flex="auto" />
      <Col>
        <Space>
          <Button size="large" type="text">
            Sign in
          </Button>
          <Button size="large">Sign up</Button>
        </Space>
      </Col>
    </Row>
  );
};

export default PageHeader;
