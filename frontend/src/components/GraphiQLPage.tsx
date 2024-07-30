import React from "react";
import "graphiql/graphiql.min.css";
import { GraphiQL } from "graphiql";
import { createGraphiQLFetcher } from "@graphiql/toolkit";

import { DefaultPage } from ".";
import { useAuth } from "../hooks";

export const GraphiQLPage: React.FC = () => {
  const { authenticatedFetch } = useAuth() ?? {};

  const fetcher = React.useMemo(() => {
    return createGraphiQLFetcher({
      url: "/graphql",
      fetch: authenticatedFetch,
    });
  }, [authenticatedFetch]);

  return (
    <DefaultPage>
      <GraphiQL fetcher={fetcher} />
    </DefaultPage>
  );
};

export default GraphiQLPage;
