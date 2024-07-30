import { createBrowserRouter } from "react-router-dom";

import { GraphiQLPage, IndexPage, SignInOrUpPage } from "./components";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <IndexPage />,
    handle: "index",
  },
  {
    path: "/api",
    element: <GraphiQLPage />,
    handle: "api",
  },
  {
    path: "/signin",
    element: <SignInOrUpPage type="sign_in" />,
    handle: "signin",
  },
  {
    path: "/signup",
    element: <SignInOrUpPage type="sign_up" />,
    handle: "signup",
  },
]);

export default router;
