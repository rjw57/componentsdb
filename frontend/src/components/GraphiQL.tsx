import React from "react";
import "graphiql/graphiql.min.css";
import { GraphiQL as WrappedGraphiQL } from "graphiql";
import { createGraphiQLFetcher } from "@graphiql/toolkit";

import { graphQLUrl } from "../config";
import useSignIn from "../hooks/useSignIn";

export const GraphiQL: React.FC<Omit<React.ComponentProps<typeof WrappedGraphiQL>, "fetcher">> = (
  props,
) => {
  const { authenticatedFetch } = useSignIn();
  const fetcher = React.useMemo(() => {
    return createGraphiQLFetcher({
      url: graphQLUrl,
      fetch: authenticatedFetch,
    });
  }, [authenticatedFetch]);

  return <WrappedGraphiQL fetcher={fetcher} {...props} />;
};

export default GraphiQL;
