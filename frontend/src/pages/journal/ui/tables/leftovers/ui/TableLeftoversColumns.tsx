import { createColumnHelper } from "@tanstack/react-table";
import { InputCellLeftovers } from "./InputCellLeftovers";
import { LeftoversItem } from "../models/leftoversSlice";
type TabeleColumns = {
  id: number;
  year: number;
  month: string;
  shipmentBasis: string;
  product: string;
  unit: string;
  productOwner: string;
  agentManufacturer: string;
  left: string;
  remark: string;
};

export const getColumns = () => {
  const columnHelper = createColumnHelper<TabeleColumns>();
  const columns = [
    columnHelper.accessor("id", {
      header: "№",
      id: "id",
      size: 100,
    }),

    columnHelper.accessor("year", {
      header: "Год",
      id: "year",
      size: 150,
    }),
    columnHelper.accessor("month", {
      header: "Месяц",
      id: "month",
      size: 200,
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
      size: 150,
      id: "unit",
    }),
    columnHelper.accessor("productOwner", {
      header: "Собственник продукта",
      size: 200,
      id: "productOwner",
    }),
    columnHelper.accessor("agentManufacturer", {
      header: "Агент Производитель",
      size: 200,
      id: "agentManufacturer",
    }),
    columnHelper.accessor("left", {
      header: "Остатки",
      size: 250,
      id: "left",
      cell: ({ cell }) => (
        <InputCellLeftovers
          data={cell.getValue()}
          rowId={cell.row.original.id}
          fieldName={cell.column.id as keyof LeftoversItem}
        />
      ),
    }),
    columnHelper.accessor("remark", {
      header: "Комментарий",
      size: 250,
      cell: ({ cell }) => (
        <InputCellLeftovers
          data={cell.getValue()}
          rowId={cell.row.original.id}
          fieldName={cell.column.id as keyof LeftoversItem}
        />
      ),
      id: "remark",
    }),
  ];
  return columns;
};
