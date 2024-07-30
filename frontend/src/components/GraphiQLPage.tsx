import React from "react";
import "graphiql/graphiql.min.css";
import { GraphiQL } from "graphiql";
import { createGraphiQLFetcher } from "@graphiql/toolkit";
import { theme } from "antd";

import { DefaultPage } from ".";
import { useAuth } from "../hooks";

export const GraphiQLPage: React.FC = () => {
  const { authenticatedFetch } = useAuth() ?? {};
  const { token } = theme.useToken();

  const fetcher = React.useMemo(() => {
    return createGraphiQLFetcher({
      url: "/graphql",
      fetch: authenticatedFetch,
    });
  }, [authenticatedFetch]);

  return (
    <DefaultPage>
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          overflow: "auto",
          borderRadius: token.borderRadiusLG,
        }}
      >
        <GraphiQL fetcher={fetcher} />
      </div>
    </DefaultPage>
  );
};

export default GraphiQLPage;
