import React from "react";
import { ConfigProvider } from "antd";

import { useThemeConfig } from "../hooks";

export interface PageProps {
  children?: React.ReactNode;
}

export const Page: React.FC<PageProps> = ({ children }) => {
  const theme = useThemeConfig();
  return <ConfigProvider theme={theme}>{children}</ConfigProvider>;
};

export default Page;
