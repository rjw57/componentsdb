import "graphiql/graphiql.min.css";

import { Layout } from "antd";
import { GraphiQL } from "graphiql";
import { createGraphiQLFetcher } from "@graphiql/toolkit";

import { Page, PageHeader } from ".";

const fetcher = createGraphiQLFetcher({
  url: "/graphql",
});

export const GraphiQLPage = () => {
  return (
    <Page>
      <Layout style={{ height: "100vh" }}>
        <Layout.Header>
          <PageHeader />
        </Layout.Header>
        <Layout.Content>
          <GraphiQL fetcher={fetcher} />
        </Layout.Content>
      </Layout>
    </Page>
  );
};

export default GraphiQLPage;
