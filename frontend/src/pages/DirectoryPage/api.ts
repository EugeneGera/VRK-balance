import { BASE_URL } from "@/shared/config/consts";
import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

type DirectoriesList = {
  table_id: string;
  table_name: string;
  fields_count: number;
}[];

type FieldsList = {
  id: string | number;
  name: string;
}[];

type UpdateModel = {
  [key: string]: {
    id: string | number;
    name: string;
  }[];
};

export const directoriesApi = createApi({
  reducerPath: "directories",
  baseQuery: fetchBaseQuery({
    baseUrl: BASE_URL + "/directories",
  }),
  endpoints: (builder) => ({
    getDirectories: builder.query<{ directories: DirectoriesList }, void>({
      query() {
        return {
          url: ``,
        };
      },
    }),
    getDirectoryInfo: builder.query<
      { table: string; fields: FieldsList },
      string | number
    >({
      query(id) {
        return {
          url: `/${id}`,
        };
      },
    }),
    updateDirectoryFields: builder.mutation<
      string,
      { id: string | number; fields: UpdateModel }
    >({
      query(data) {
        return {
          url: `/${data.id}`,
          method: "PUT",
          body: data.fields,
        };
      },
    }),
  }),
});

export const {
  useGetDirectoriesQuery,
  useLazyGetDirectoryInfoQuery,
  useUpdateDirectoryFieldsMutation,
} = directoriesApi;
