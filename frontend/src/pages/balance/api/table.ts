// Need to use the React-specific entry point to import createApi

import { BASE_URL } from "@/shared/config/consts";

import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

export type MainTableData = [string, ...Array<number | null>][];

// Define a service using a base URL and expected endpoints
export const mainTableAPI = createApi({
  reducerPath: "mainTable",
  baseQuery: fetchBaseQuery({ baseUrl: `${BASE_URL}/sankey` }),
  endpoints: (builder) => ({
    getMainTableData: builder.query<MainTableData, string>({
      query(query: string) {
        return {
          url: `/table?${query}`,
        };
      },
    }),
  }),
});

export const { useGetMainTableDataQuery } = mainTableAPI;
