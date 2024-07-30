import { createBrowserRouter } from "react-router-dom";

import { GraphiQLPage, IndexPage } from "./components";

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
]);

export default router;
