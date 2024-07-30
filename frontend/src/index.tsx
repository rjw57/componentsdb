import React from "react";
import ReactDOM from "react-dom/client";
import { RouterProvider } from "react-router-dom";
import { App as AntApp } from "antd";

import "./index.css";
import reportWebVitals from "./reportWebVitals";
import router from "./router";
import { AuthProvider, ApolloProvider, AntConfigProvider } from "./components";

const root = ReactDOM.createRoot(document.getElementById("root") as HTMLElement);

root.render(
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
  </React.StrictMode>,
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
