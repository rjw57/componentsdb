import React from "react";

import { Layout, theme } from "antd";

import { Page, PageHeader } from ".";

export interface DefaultPageProps {
  children?: React.ReactNode;
}

export const DefaultPage: React.FC<DefaultPageProps> = ({ children }) => {
  const {
    token: { borderRadiusLG },
  } = theme.useToken();

  return (
    <Page>
      <Layout style={{ height: "100vh" }}>
        <Layout.Header>
          <PageHeader />
        </Layout.Header>
        <Layout.Content
          style={{ margin: "24px 50px", overflow: "auto", borderRadius: borderRadiusLG }}
        >
          {children}
        </Layout.Content>
      </Layout>
    </Page>
  );
};

export default DefaultPage;
