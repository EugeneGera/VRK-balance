import { useGetLatestPeriodQuery } from "@/entities/categories/api";
import { SplashScreen } from "@/pages/SplashScreen";
import { ReactNode } from "react";
import { Navigate, useLocation } from "react-router";

const filterKeys = [
  "year",
  "month_start",
  "month_end",
  "category_product",
  "product",
  "basises",
];

export const InitialFilters = ({ children }: { children: ReactNode }) => {
  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const hasFilters = filterKeys.some((key) => params.get(key)?.trim());
  const { data, isFetching, isUninitialized, isError } = useGetLatestPeriodQuery(undefined, {
    skip: hasFilters,
    refetchOnMountOrArgChange: true,
  });

  if (hasFilters) return <>{children}</>;

  // The dashboard mounts after the date is resolved, so it never requests the
  // current month while the initial filters are still loading.
  if (isFetching || isUninitialized) return <SplashScreen />;
  if (isError || !data) return <>{children}</>;

  filterKeys.forEach((key) => {
    if (!params.get(key)?.trim()) params.delete(key);
  });
  params.set("year", String(data.year));
  params.set("month_start", String(data.month_start));
  if (location.pathname.includes("business-journal")) {
    params.set("month_end", String(data.month_start));
  } else {
    params.set("category_product", data.category_product);
  }

  return (
    <Navigate
      state={location.state}
      to={{ pathname: location.pathname, search: `?${params.toString()}`, hash: location.hash }}
      replace
    />
  );
};
