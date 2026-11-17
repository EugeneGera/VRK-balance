import { createColumnHelper } from "@tanstack/react-table";
import { InputCellRealization } from "./InputCellRealization";
import { RealizationItem } from "../models/realizationSlice";

type TabeleColumns = {
  id: number;
  owner: string;
  year: number;
  month: string;
  shipmentBasis: string;
  product: string;
  unit: string;
  direction: string;
  agentManufacturer: string;
  productOwner: string;
  shipmentMethod: string;
  dealCategory: string;
  destinationStation: string;
  buyer: string;
  dealStatus: string;
  applicationSize: string;
  price: string;
  remark: string;
};

export const getColumns = () => {
  const columnHelper = createColumnHelper<TabeleColumns>();

  const columns = [
    columnHelper.accessor("id", {
      header: "№",
      id: "id",
      size: 50,
    }),
    columnHelper.accessor("owner", {
      header: "Владелец записи",
      id: "owner",
      size: 150,
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
      header: "Ед изм",
      size: 80,
      id: "unit",
    }),
    columnHelper.accessor("direction", {
      header: "Направление реализации",
      size: 150,
      id: "direction",
    }),
    columnHelper.accessor("agentManufacturer", {
      header: "Агент Производитель",
      size: 150,
      id: "agentManufacturer",
    }),
    columnHelper.accessor("productOwner", {
      header: "Собственник продукта",
      size: 150,
      id: "productOwner",
    }),
    columnHelper.accessor("shipmentMethod", {
      header: "Способ отгрузки",
      size: 120,
      id: "shipmentMethod",
    }),
    columnHelper.accessor("dealCategory", {
      header: "Категория сделки",
      size: 120,
      id: "dealCategory",
    }),
    columnHelper.accessor("destinationStation", {
      header: "Станция назначение",
      size: 150,
      id: "destinationStation",
    }),
    columnHelper.accessor("buyer", {
      header: "Покупатель",
      size: 150,
      id: "buyer",
    }),
    columnHelper.accessor("dealStatus", {
      header: "Статус заключения сделки",
      size: 150,
      id: "dealStatus",
    }),
    columnHelper.accessor("applicationSize", {
      header: "Объем по заявке, т",
      size: 150,
      cell: ({ cell }) => {
        return (
           <InputCellRealization
          data={cell.getValue()}
          rowId={cell.row.original.id}
          fieldName={cell.column.id as keyof RealizationItem}
        />
        )
      },
      id: "applicationSize",
    }),
    columnHelper.accessor("price", {
      header: "Цена руб./т",
      size: 150,
      cell: ({ cell }) => {
        return (
          <InputCellRealization
            data={cell.getValue()}
            rowId={cell.row.original.id}
            fieldName={cell.column.id as keyof RealizationItem}
          />
        );
      },
      id: "price",
    }),
    columnHelper.accessor("remark", {
      header: "Примечание",
      size: 150,
      cell: ({ cell }) => (
        <InputCellRealization
          data={cell.getValue()}
          rowId={cell.row.original.id}
          fieldName={cell.column.id as keyof RealizationItem}
        />
      ),
      id: "remark",
    }),
  ];
  return columns;
};
