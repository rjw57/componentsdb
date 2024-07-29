import { createBrowserRouter } from "react-router-dom";

import { GraphiQLPage } from "./components";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <GraphiQLPage />,
  },
]);

export default router;
