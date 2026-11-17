import { createColumnHelper } from "@tanstack/react-table";
import { InputCellPlan } from "./InputCellPlan";
import { PlanItem } from "../models/planSlice";
type TabeleColumns = {
  id: number;
  year: number;
  month: string;
  shipmentBasis: string;
  product: string;
  unit: string;
  productOwner: string;
  agentManufacturer: string;
  plan: string;
  remark: string;
};

export const getColumns = () => {
  const columnHelper = createColumnHelper<TabeleColumns>();
  const columns = [
    columnHelper.accessor("id", {
      header: "№",
      id: "id",
      size: 70,
    }),

    columnHelper.accessor("year", {
      header: "Год",
      id: "year",
      size: 100,
    }),
    columnHelper.accessor("month", {
      header: "Месяц",
      id: "month",
      size: 120,
    }),
    columnHelper.accessor("shipmentBasis", {
      header: "Базис отгрузки",
      id: "shipmentBasis",
      size: 200,
    }),
    columnHelper.accessor("product", {
      header: "Продукт",
      size: 200,
      id: "product",
    }),
    columnHelper.accessor("unit", {
      header: "Ед изм",
      size: 100,
      id: "unit",
    }),
    columnHelper.accessor("productOwner", {
      header: "Собственник продукта",
      size: 200,
      id: "productOwner",
    }),
    columnHelper.accessor("agentManufacturer", {
      header: "Агент/Производитель",
      size: 200,
      id: "agentManufacturer",
    }),
    columnHelper.accessor("plan", {
      header: "План пр-ва",
      size: 200,
      id: "plan",
      cell: ({ cell }) => (
        <InputCellPlan
          data={cell.getValue()}
          rowId={cell.row.original.id}
          fieldName={cell.column.id as keyof PlanItem}
        />
      ),
    }),
    columnHelper.accessor("remark", {
      header: "Комментарий",
      size: 200,
      cell: ({ cell }) => (
        <InputCellPlan
          data={cell.getValue()}
          rowId={cell.row.original.id}
          fieldName={cell.column.id as keyof PlanItem}
        />
      ),
      id: "remark",
    }),
  ];
  return columns;
};
