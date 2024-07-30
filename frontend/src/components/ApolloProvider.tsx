import React from "react";
import { ApolloProvider as BaseApolloProvider } from "@apollo/client";

import { useApolloClient } from "../hooks";

export const ApolloProvider: React.FC<
  Omit<React.ComponentProps<typeof BaseApolloProvider>, "client">
> = ({ children, ...props }) => {
  const apolloClient = useApolloClient();
  return (
    <BaseApolloProvider client={apolloClient} {...props}>
      {children}
    </BaseApolloProvider>
  );
};

export default ApolloProvider;
