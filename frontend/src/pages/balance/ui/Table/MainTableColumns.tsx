import { ColumnDef } from "@tanstack/react-table";
import { CaretDownOutlined, CaretUpOutlined } from "@ant-design/icons";
import { MainTableData } from "../../api/table";

// Тип данных для строк таблицы
export type TableRowData = {
  basis: string;
  remains: number | null;
  productionPlan: number | null;
  resourceToDistribute: number | null;
  distributedAll: number | null;
  internalMarketTotal: number | null;
  internalMarketStockExchangeTotal: number | null;
  internalMarketStockExchangeObligations: number | null;
  internalMarketStockExchangeAdditional: number | null;
  internalMarketGOZ: number | null;
  internalMarketSmallWholesale: number | null;
  internalMarketRetailSupply: number | null;
  internalMarketMandatoryContracts: number | null;
  internalMarketOther: number | null;
  internalMarketAdditionalNeeds: number | null;
  exportTotal: number | null;
  exportMandatoryContracts: number | null;
  exportOther: number | null;
  exportAdditionalNeeds: number | null;
  doNeedsTotal: number | null;
  doNeedsAdditionalNeeds: number | null;
  resourceBalance: number | null;
  subRows?: TableRowData[];
};

// Функция преобразования данных в иерархическую структуру
export const transformDataWithSubRows = (
  data: MainTableData
): TableRowData[] => {
  const mainRows: TableRowData[] = [];
  const subRowMap: { [key: string]: TableRowData[] } = {
    Итого: [],
  };

  data.forEach((row) => {
    const basis = row[0];
    const rowData: TableRowData = {
      basis,
      remains: row[1],
      productionPlan: row[2],
      resourceToDistribute: row[3],
      distributedAll: row[4],
      internalMarketTotal: row[5],
      internalMarketStockExchangeTotal: row[6],
      internalMarketStockExchangeObligations: row[7],
      internalMarketStockExchangeAdditional: row[8],
      internalMarketGOZ: row[9],
      internalMarketSmallWholesale: row[10],
      internalMarketRetailSupply: row[11],
      internalMarketMandatoryContracts: row[12],
      internalMarketOther: row[13],
      internalMarketAdditionalNeeds: row[14],
      exportTotal: row[15],
      exportMandatoryContracts: row[16],
      exportOther: row[17],
      exportAdditionalNeeds: row[18],
      doNeedsTotal: row[19],
      doNeedsAdditionalNeeds: row[20],
      resourceBalance: row[21],
      subRows: [],
    };

    if (basis.includes("Итого") && basis.includes(" (")) {
      const parentBasis = basis.split(" (")[1].replace(")", "");
      if (!subRowMap[parentBasis]) {
        subRowMap[parentBasis] = [];
      }
      const modifyedBasis = basis
        .replace("Итого", "")
        .replace(/\s*\([^)]*\)/, "");
      rowData.basis = modifyedBasis;
      subRowMap[parentBasis].push(rowData);
    } else if (basis.includes("Итого ") && !basis.includes(" (")) {
      const modifyedBasis = basis.replace("Итого ", "");
      rowData.basis = modifyedBasis;
      subRowMap["Итого"].push(rowData);
    } else {
      mainRows.push(rowData);
      if (!subRowMap[basis]) {
        subRowMap[basis] = [];
      }
    }
  });

  mainRows.forEach((row) => {
    if (subRowMap[row.basis] && subRowMap[row.basis].length > 0) {
      row.subRows = subRowMap[row.basis];
    }
  });

  return mainRows;
};

// Определение колонок
export const columns: ColumnDef<TableRowData>[] = [
  {
    header: "Базис",
    accessorKey: "basis",
    cell: ({ row, getValue }) => {
      return (
        <div
          style={{
            display: "flex",
            justifyContent: row.getCanExpand() || row.original.basis === "Итого" ? "start" : "center",
            gap: "8px",
          }}
        >
          {row.getCanExpand() && (
            <button
              onClick={row.getToggleExpandedHandler()}
              aria-expanded={row.getIsExpanded()}
              aria-label={
                row.getIsExpanded() ? "Свернуть строку" : "Развернуть строку"
              }
              style={{
                cursor: "pointer",
                background: "none",
                border: "none",
                padding: "0",
                fontSize: "12px",
              }}
              id="value"
            >
              {row.getIsExpanded() ? (
                <CaretUpOutlined />
              ) : (
                <CaretDownOutlined />
              )}
            </button>
          )}
          <span>{getValue<string>()}</span>
        </div>
      );
    },
  },
  { header: "Остатки", accessorKey: "remains" },
  { header: "План произ-ва", accessorKey: "productionPlan" },
  { header: "Ресурс к распределению", accessorKey: "resourceToDistribute" },
  { header: "Распределено, весь объем", accessorKey: "distributedAll" },
  {
    header: "Внутр. рынок",
    id: "internalMarket",
    columns: [
      { header: "Всего выделено БК", accessorKey: "internalMarketTotal" },
      {
        header: "Биржа, в т. ч.",
        id: "internalMarketStockExchange",
        columns: [
          {
            header: "Всего биржа",
            accessorKey: "internalMarketStockExchangeTotal",
          },
          {
            header: "Обязательства",
            accessorKey: "internalMarketStockExchangeObligations",
          },
          {
            header: "Доп. объемы",
            accessorKey: "internalMarketStockExchangeAdditional",
          },
        ],
      },
      { header: "ГОЗ", accessorKey: "internalMarketGOZ" },
      { header: "Мелкий опт", accessorKey: "internalMarketSmallWholesale" },
      {
        header: "Снабжение розничной сети",
        accessorKey: "internalMarketRetailSupply",
      },
      {
        header: "“Обязательные” контракты",
        accessorKey: "internalMarketMandatoryContracts",
      },
      { header: "Прочее", accessorKey: "internalMarketOther" },
      {
        header: "Доп. потребность",
        accessorKey: "internalMarketAdditionalNeeds",
      },
    ],
  },
  {
    header: "Экспорт",
    id: "export",
    columns: [
      { header: "Всего выделено БК", accessorKey: "exportTotal" },
      {
        header: "“Обязательные” контракты",
        accessorKey: "exportMandatoryContracts",
      },
      { header: "Прочее", accessorKey: "exportOther" },
      { header: "Доп. потребность", accessorKey: "exportAdditionalNeeds" },
    ],
  },
  {
    header: "Нужды ДО",
    id: "doNeeds",
    columns: [
      { header: "Всего выделено БК", accessorKey: "doNeedsTotal" },
      { header: "Доп. потребность", accessorKey: "doNeedsAdditionalNeeds" },
    ],
  },
  { header: "Остаток ресурса", accessorKey: "resourceBalance" },
];

export const headerRows = [
  // Первый уровень
  [
    { name: "Базис", colSpan: 1, rowSpan: 3 },
    { name: "Остатки", colSpan: 1, rowSpan: 3 },
    { name: "План произ-ва", colSpan: 1, rowSpan: 3 },
    { name: "Ресурс к распределению", colSpan: 1, rowSpan: 3 },
    { name: "Распределено, весь объем", colSpan: 1, rowSpan: 3 },
    { name: "Внутр. рынок", colSpan: 10, rowSpan: 1 },
    { name: "Экспорт", colSpan: 4, rowSpan: 1 },
    { name: "Нужды ДО", colSpan: 2, rowSpan: 1 },
    { name: "Остаток ресурса", colSpan: 1, rowSpan: 3 },
  ],
  // Второй уровень
  [
    { name: "Всего выделено БК", colSpan: 1, rowSpan: 2 },
    { name: "Биржа, в т. ч.", colSpan: 3, rowSpan: 1 },
    { name: "ГОЗ", colSpan: 1, rowSpan: 2 },
    { name: "Мелкий опт", colSpan: 1, rowSpan: 2 },
    { name: "Снабжение розничной сети", colSpan: 1, rowSpan: 2 },
    { name: "“Обязательные” контракты", colSpan: 1, rowSpan: 2 },
    { name: "Прочее", colSpan: 1, rowSpan: 2 },
    { name: "Доп. потребность", colSpan: 1, rowSpan: 2 },
    { name: "Всего выделено БК", colSpan: 1, rowSpan: 2 },
    { name: "“Обязательные” контракты", colSpan: 1, rowSpan: 2 },
    { name: "Прочее", colSpan: 1, rowSpan: 2 },
    { name: "Доп. потребность", colSpan: 1, rowSpan: 2 },
    { name: "Всего выделено БК", colSpan: 1, rowSpan: 2 },
    { name: "Доп. потребность", colSpan: 1, rowSpan: 2 },
  ],
  // Третий уровень
  [
    { name: "Всего биржа", colSpan: 1, rowSpan: 1 },
    { name: "Обязательства", colSpan: 1, rowSpan: 1 },
    { name: "Доп. объемы", colSpan: 1, rowSpan: 1 },
  ],
];
