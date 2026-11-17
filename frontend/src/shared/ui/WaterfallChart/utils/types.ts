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

export interface WaterfallFields {
  total: Total;
  available_resource: AvailableResource;
  distribution: DistributionItem[];
  resource_leftover: ResourceLeftover;
  need: Need;
}

export interface WaterfallData {
  data: WaterfallFields;
}
