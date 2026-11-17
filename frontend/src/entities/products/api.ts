// Need to use the React-specific entry point to import createApi
import { BASE_URL } from "@/shared/config/consts";
import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

interface Products {
    products: {value: string}[]
}

// Define a service using a base URL and expected endpoints
export const productsAPI = createApi({
  reducerPath: "products",
  baseQuery: fetchBaseQuery({ baseUrl: `${BASE_URL}/info` }),
  endpoints: (builder) => ({
    getAllProducts: builder.query< Products, string | null>({
      query(category) {
        return {
          url: `/products${category ? `?category_product=${category}` : ''}`,
        };
      },
      transformResponse: (res: { products: string[] }): Products=>  {
        const transfomedData = {products: res.products.map(i => ({value: i}))}
        return transfomedData
      },
    }),
  }),
});

export const { useGetAllProductsQuery } = productsAPI;