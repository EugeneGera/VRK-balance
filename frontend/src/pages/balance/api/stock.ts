// Need to use the React-specific entry point to import createApi

import { BASE_URL } from "@/shared/config/consts";

import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

interface StockMarketData {
  percent: {
    month: string;
    data: { type: string; value: number; category?: string }[];
  }[];
  absolute: {
    month: string;
    data: { type: string; value: number; category?: string }[];
  }[];
}

// Define a service using a base URL and expected endpoints
export const stockAPI = createApi({
  reducerPath: "stock",
  baseQuery: fetchBaseQuery({ baseUrl: `${BASE_URL}/sankey` }),
  endpoints: (builder) => ({
    getStockDetalization: builder.query<StockMarketData, string>({
      query(query: string) {
        return {
          url: `/stock_details?${query}`,
        };
      },
    }),
  }),
});

export const { useGetStockDetalizationQuery } = stockAPI;
