import React from "react";
import { ConfigProvider } from "antd";

import { useThemeConfig } from "../hooks";

export const AntConfigProvider: React.FC<
  Omit<React.ComponentProps<typeof ConfigProvider>, "theme">
> = ({ children, ...props }) => {
  const theme = useThemeConfig();

  return (
    <ConfigProvider theme={theme} {...props}>
      {children}
    </ConfigProvider>
  );
};

export default AntConfigProvider;
