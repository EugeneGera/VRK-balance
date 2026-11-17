import { BASE_URL } from "@/shared/config/consts";
import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

export const journalApi = createApi({
  reducerPath: "journal",
  baseQuery: fetchBaseQuery({
    baseUrl: BASE_URL + "/journal",
  }),
  endpoints: (builder) => ({
    getApplications: builder.query({
      query(query: string) {
        return {
          url: `/applications?${query}`,
        };
      },
    }),

    updateApplicationsValues: builder.mutation({
      query: (body) => {
        return {
          url: `/applications`,
          method: "PUT",
          body,
        };
      },
    }),

    getPlans: builder.query({
      query(query: string) {
        return {
          url: `/plans?${query}`,
        };
      },
    }),

    updatePlansValues: builder.mutation({
      query: (body) => {
        return {
          url: "/plans",
          method: "PUT",
          body,
        };
      },
    }),

    getLeftovers: builder.query({
      query(query: string) {
        return {
          url: `/leftovers?${query}`,
        };
      },
    }),

    getLimits: builder.query({
      query(query: string) {
        return {
          url: `/limits?${query}`,
        };
      },
    }),

    updateLeftoversValues: builder.mutation({
      query: (body) => {
        return {
          url: "/leftovers",
          method: "PUT",
          body,
        };
      },
    }),

    updateLimitsValues: builder.mutation({
      query: (body) => {
        return {
          url: "/limits",
          method: "PUT",
          body,
        };
      },
    }),
  }),
});

export const {
  useGetApplicationsQuery,
  useGetPlansQuery,
  useGetLeftoversQuery,
  useGetLimitsQuery,
  useUpdateApplicationsValuesMutation,
  useUpdatePlansValuesMutation,
  useUpdateLeftoversValuesMutation,
  useUpdateLimitsValuesMutation
} = journalApi;
