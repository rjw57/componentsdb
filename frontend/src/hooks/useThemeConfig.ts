import { useMediaQuery } from "usehooks-ts";
import { ThemeConfig, theme } from "antd";

export const useThemeConfig = (): ThemeConfig => {
  const prefersDarkMode = useMediaQuery("(prefers-color-scheme:dark)");
  return {
    algorithm: prefersDarkMode ? theme.darkAlgorithm : theme.defaultAlgorithm,
  };
};

export default useThemeConfig;
