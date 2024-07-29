import "graphiql/graphiql.min.css";

import { Layout, theme } from "antd";
import { GraphiQL } from "graphiql";
import { createGraphiQLFetcher } from "@graphiql/toolkit";

import { Page, PageHeader } from ".";

import { unauthenticatedClient } from "../apolloClient";
import { useFederatedIdentitiyProviders } from "../hooks";

const fetcher = createGraphiQLFetcher({
  url: "/graphql",
});

export const GraphiQLPage: React.FC = () => {
  const {
    token: { borderRadiusLG },
  } = theme.useToken();
  const { data: providers } = useFederatedIdentitiyProviders({ client: unauthenticatedClient });
  console.log(providers);
  return (
    <Page>
      <Layout style={{ height: "100vh" }}>
        <Layout.Header>
          <PageHeader />
        </Layout.Header>
        <Layout.Content
          style={{ margin: "32px 48px", overflow: "auto", borderRadius: borderRadiusLG }}
        >
          <GraphiQL fetcher={fetcher} />
        </Layout.Content>
      </Layout>
    </Page>
  );
};

export default GraphiQLPage;
