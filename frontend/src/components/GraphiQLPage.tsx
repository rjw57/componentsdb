import "graphiql/graphiql.min.css";

import { Layout } from "antd";
import { GraphiQL } from "graphiql";
import { createGraphiQLFetcher } from "@graphiql/toolkit";

import { Page, PageHeader } from ".";

import { unauthenticatedClient } from "../apolloClient";
import { useFederatedIdentitiyProviders } from "../hooks";

const fetcher = createGraphiQLFetcher({
  url: "/graphql",
});

export const GraphiQLPage = () => {
  const { data: providers } = useFederatedIdentitiyProviders({ client: unauthenticatedClient });
  return (
    <Page>
      <Layout style={{ height: "100vh" }}>
        <Layout.Header>
          <PageHeader />
        </Layout.Header>
        <Layout.Content>
          <div>{JSON.stringify(providers)}</div>
          <GraphiQL fetcher={fetcher} />
        </Layout.Content>
      </Layout>
    </Page>
  );
};

export default GraphiQLPage;
