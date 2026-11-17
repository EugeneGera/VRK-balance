// Need to use the React-specific entry point to import createApi

import { BASE_URL } from "@/shared/config/consts";

import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

export type Data = Record<string, any>;

// Define a service using a base URL and expected endpoints
export const sankeyAPI = createApi({
  reducerPath: "sankey",
  baseQuery: fetchBaseQuery({ baseUrl: `${BASE_URL}/sankey` }),
  endpoints: (builder) => ({
    getChartData: builder.query< {data: Data, product: string, trans_dirs: string[]}, string>({
      query(query: string) {
        return {
          url: `/graph?${query}`,
        };
      },
    }),
  }),
});

export const { useGetChartDataQuery } = sankeyAPI;
