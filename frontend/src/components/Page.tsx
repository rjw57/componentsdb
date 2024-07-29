import React from "react";
import { ConfigProvider } from "antd";
import { ApolloProvider } from "@apollo/client";

import { useThemeConfig, useAuth } from "../hooks";
import { makeClient } from "../apolloClient";

export interface PageProps {
  children?: React.ReactNode;
}

export const Page: React.FC<PageProps> = ({ children }) => {
  const theme = useThemeConfig();
  const { credentials } = useAuth() ?? {};

  const apolloClient = React.useMemo(() => {
    return makeClient({ accessToken: credentials?.accessToken });
  }, [credentials?.accessToken]);

  return (
    <ApolloProvider client={apolloClient}>
      <ConfigProvider theme={theme}>{children}</ConfigProvider>
    </ApolloProvider>
  );
};

export default Page;
