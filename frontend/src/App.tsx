import React from "react";
import { RouterProvider } from "react-router-dom";
import { App as AntApp } from "antd";

import router from "./router";
import { AuthProvider, ApolloProvider, AntConfigProvider } from "./components";

interface AppProps {
  children?: React.ReactNode;
}

export const App: React.FC<AppProps> = ({ children }) => (
  <React.StrictMode>
    <AuthProvider>
      <ApolloProvider>
        <AntConfigProvider>
          <AntApp>{children ?? <RouterProvider router={router} />}</AntApp>
        </AntConfigProvider>
      </ApolloProvider>
    </AuthProvider>
  </React.StrictMode>
);

export default App;
