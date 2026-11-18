import { createBrowserRouter, Navigate, useLocation } from "react-router";

import { ErrorPage } from "@/pages/ErrorPage/ui/ErrorPage";

import { PrivateRoute } from "./PrivateRoute";
import { Balance } from "@/pages/balance";
import { Journal } from "@/pages/journal";
// import { DirectoryPage } from "@/pages/DirectoryPage";

function LegacyReportRedirect() {
  const { search } = useLocation();
  return <Navigate replace to={{pathname: "/balance_comission", search}} state={{openReport: true}} />;
}

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
    path: "/balance_comission/analytics",
    element: <LegacyReportRedirect />,
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
