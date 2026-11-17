// Need to use the React-specific entry point to import createApi
import { BASE_URL } from "@/shared/config/consts";
import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

interface Categories {
    category_product: {value: string}[]
}

interface LatestPeriod {
  year: number;
  month_start: number;
  category_product: string;
}

// Define a service using a base URL and expected endpoints
export const categoryAPI = createApi({
  reducerPath: "categories",
  baseQuery: fetchBaseQuery({ baseUrl: `${BASE_URL}/info` }),
  endpoints: (builder) => ({
    getLatestPeriod: builder.query<LatestPeriod | null, void>({
      query: () => "/latest_period",
    }),
    getAllCategories: builder.query< Categories, void>({
      query() {
        return {
          url: `/category_product`,
        };
      },
      transformResponse: (res: { category_product: string[] }): Categories=>  {
        const transfomedData = {category_product: res.category_product.map(i => ({value: i}))}
        return transfomedData
      },
    }),
  }),
});

export const { useGetAllCategoriesQuery, useGetLatestPeriodQuery } = categoryAPI;
