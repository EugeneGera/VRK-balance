import { createBrowserRouter } from "react-router";

import { ErrorPage } from "@/pages/ErrorPage/ui/ErrorPage";

import { PrivateRoute } from "./PrivateRoute";
import { Balance } from "@/pages/balance";
import { Journal } from "@/pages/journal";
// import { DirectoryPage } from "@/pages/DirectoryPage";

export const router = createBrowserRouter([
  {
    path: "/balance_comission/error",
    element: <ErrorPage />,
  },
  {
    path: "/balance_comission",
    element: <PrivateRoute component={Balance} />,
  },
  {
    path: "/balance_comission/business-journal",
    element: <PrivateRoute component={Journal} />,
  },
  // {
  //   path: "/balance_comission/directory",
  //   element: <PrivateRoute component={DirectoryPage} />,
  // }
]);
