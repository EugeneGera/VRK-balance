import { createColumnHelper } from "@tanstack/react-table";
import { InputCellLimit } from "./InputCellLimit";
import { LimitItem } from "../models/limitSlice";

type TabeleColumns = {
  id: number;
  year: number;
  month: string;
  shipmentBasis: string;
  product: string;
  unit: string;
  productOwner: string;
  agentManufacturer: string;
  min_left: string;
  min_remark: string;
  max_shipment: string;
  max_remark: string;
};

export const getColumns = () => {
  const columnHelper = createColumnHelper<TabeleColumns>();

  const columns = [
    columnHelper.accessor("id", {
      header: "№",
      id: "id",
      size: 50,
    }),
    columnHelper.accessor("year", {
      header: "Год",
      id: "year",
      size: 80,
    }),
    columnHelper.accessor("month", {
      header: "Месяц",
      id: "month",
      size: 100,
    }),
    columnHelper.accessor("shipmentBasis", {
      header: "Базис отгрузки",
      id: "shipmentBasis",
      size: 120,
    }),
    columnHelper.accessor("product", {
      header: "Продукт",
      size: 120,
      id: "product",
    }),
    columnHelper.accessor("unit", {
      header: "Ед. изм.",
      size: 80,
      id: "unit",
    }),
    columnHelper.accessor("productOwner", {
      header: "Собственник продукта",
      size: 150,
      id: "productOwner",
    }),
    columnHelper.accessor("agentManufacturer", {
      header: "Агент/Производитель",
      size: 150,
      id: "agentManufacturer",
    }),
    columnHelper.accessor("min_left", {
      header: "Мин. остаток",
      size: 150,
      cell: ({ cell }) => (
        <InputCellLimit
          data={cell.getValue()}
          rowId={cell.row.original.id}
          fieldName={cell.column.id as keyof LimitItem}
        />
      ),
      id: "min_left",
    }),
    columnHelper.accessor("min_remark", {
      header: "Комментарий мин. остаток",
      size: 150,
      cell: ({ cell }) => {
        return (
          <InputCellLimit
            data={cell.getValue()}
            rowId={cell.row.original.id}
            fieldName={cell.column.id as keyof LimitItem}
          />
        );
      },
      id: "min_remark",
    }),
    columnHelper.accessor("max_shipment", {
      header: "Макс. отгрузка",
      size: 150,
      cell: ({ cell }) => (
        <InputCellLimit
          data={cell.getValue()}
          rowId={cell.row.original.id}
          fieldName={cell.column.id as keyof LimitItem}
        />
      ),
      id: "max_shipment",
    }),
    columnHelper.accessor("max_remark", {
      header: "Комментарий макс. отгрузка",
      size: 150,
      cell: ({ cell }) => (
        <InputCellLimit
          data={cell.getValue()}
          rowId={cell.row.original.id}
          fieldName={cell.column.id as keyof LimitItem}
        />
      ),
      id: "max_remark",
    }),
  ];
  return columns;
};
