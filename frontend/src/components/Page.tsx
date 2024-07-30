import React from "react";
import { ConfigProvider } from "antd";
import { ApolloProvider } from "@apollo/client";

import { useThemeConfig, useApolloClient } from "../hooks";

export interface PageProps {
  children?: React.ReactNode;
}

export const Page: React.FC<PageProps> = ({ children }) => {
  const theme = useThemeConfig();
  const apolloClient = useApolloClient();

  return (
    <ApolloProvider client={apolloClient}>
      <ConfigProvider theme={theme}>{children}</ConfigProvider>
    </ApolloProvider>
  );
};

export default Page;
