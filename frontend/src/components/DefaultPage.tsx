import React from "react";

import { Layout, theme } from "antd";

import { PageHeader } from ".";

export interface DefaultPageProps {
  children?: React.ReactNode;
}

export const DefaultPage: React.FC<DefaultPageProps> = ({ children }) => {
  const { token } = theme.useToken();

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Layout.Header>
        <PageHeader />
      </Layout.Header>
      <Layout.Content
        style={{ marginLeft: 50, marginRight: 50, marginTop: token.marginXL, position: "relative" }}
      >
        {children}
      </Layout.Content>
    </Layout>
  );
};

export default DefaultPage;
