import React from "react";
import { ConfigProvider } from "antd";
import { ApolloProvider, ApolloClient, InMemoryCache } from "@apollo/client";

import { useThemeConfig } from "../hooks";

export interface PageProps {
  children?: React.ReactNode;
}

const client = new ApolloClient({
  cache: new InMemoryCache(),
  uri: "/graphql",
});

export const Page: React.FC<PageProps> = ({ children }) => {
  const theme = useThemeConfig();
  return (
    <ApolloProvider client={client}>
      <ConfigProvider theme={theme}>{children}</ConfigProvider>
    </ApolloProvider>
  );
};

export default Page;
