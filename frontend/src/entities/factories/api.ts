// Need to use the React-specific entry point to import createApi
import { BASE_URL } from "@/shared/config/consts";

import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

interface Factories  {
  factories: {value: string}[];
};


// Define a service using a base URL and expected endpoints
export const factoriesAPI = createApi({
  reducerPath: "factories",
  baseQuery: fetchBaseQuery({ baseUrl: `${BASE_URL}/info` }),
  endpoints: (builder) => ({
    getAllFactories: builder.query<Factories, string>({
      query(query) {
        return {
          url: `/shipping_basises?${query}`,
        };
      },
      transformResponse: (res: { shipping_basises: string[] }): Factories =>  {
        const transfomedData = {factories: res.shipping_basises.map(i => ({value: i}))}
        return transfomedData
      },
    }),
  }),
});

export const { useGetAllFactoriesQuery } = factoriesAPI;
