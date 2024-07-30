import { createBrowserRouter } from "react-router-dom";

import { GraphiQLPage, IndexPage, SignInPage, SignUpPage } from "./components";

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
    element: <SignInPage />,
    handle: "signin",
  },
  {
    path: "/signup",
    element: <SignUpPage />,
    handle: "signup",
  },
]);

export default router;
