import { BASE_URL } from "@/shared/config/consts";
import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

export const uploadApi = createApi({
  reducerPath: "upload",
  baseQuery: fetchBaseQuery({
    baseUrl: BASE_URL + "/upload",
  }),
  endpoints: (builder) => ({
    uploadApplications: builder.mutation({
      query(data) {
        return {
          method: "POST",
          url: `/applications`,
          body: data
        };
      },
    }),

  }),
});

export const {
    useUploadApplicationsMutation
} = uploadApi;
