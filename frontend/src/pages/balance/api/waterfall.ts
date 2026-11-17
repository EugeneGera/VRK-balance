import { BASE_URL } from "@/shared/config/consts";

import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

interface Total {
  plan: number;
  leftovers: number;
}

interface AvailableResource {
  available: number;
  restrictions: number;
}

export interface DistributionItem {
  name: string;
  value: number;
  claim?: number;
}

interface ResourceLeftover {
  leftovers: number;
}

interface Need {
  need: number;
}

export interface WaterfallChartFields {
  name: string;
  data: {
    total: Total;
    available_resource: AvailableResource;
    distribution: DistributionItem[];
    resource_leftover: ResourceLeftover;
    need: Need;
  };
}

interface WaterfallFields {
  data: WaterfallChartFields[];
}

export interface WaterfallData {
  data: WaterfallFields;
  unit: string;
}

export const waterfallAPI = createApi({
  reducerPath: "waterfall",
  baseQuery: fetchBaseQuery({ baseUrl: `${BASE_URL}/sankey` }),
  endpoints: (builder) => ({
    getWaterfallData: builder.query<WaterfallData, string>({
      query(query: string) {
        return {
          url: `/waterfall?${query}`,
        };
      },
    }),
  }),
});

export const { useGetWaterfallDataQuery } = waterfallAPI;
