import React from "react";
import { RouterProvider } from "react-router-dom";
import { App as AntApp } from "antd";

import router from "./router";
import { AuthProvider, ApolloProvider, AntConfigProvider } from "./components";

export const App = () => (
  <React.StrictMode>
    <AuthProvider>
      <ApolloProvider>
        <AntConfigProvider>
          <AntApp>
            <RouterProvider router={router} />
          </AntApp>
        </AntConfigProvider>
      </ApolloProvider>
    </AuthProvider>
  </React.StrictMode>
);

export default App;
