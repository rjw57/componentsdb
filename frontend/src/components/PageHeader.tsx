import { Row, Col, Button, Space } from "antd";

export const PageHeader = () => {
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
