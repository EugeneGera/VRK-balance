import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@tinkerbells/xenon-ui";
import { useGetMainTableDataQuery } from "../../api/table";
import { useSearchParams } from "react-router";
import { useCallback, useEffect, useMemo, useState } from "react";
import dayjs from "dayjs";
import {
  useReactTable,
  getCoreRowModel,
  getExpandedRowModel,
  flexRender,
} from "@tanstack/react-table";
import {
  columns,
  headerRows,
  transformDataWithSubRows,
} from "./MainTableColumns";
import { useAppSelector } from "@/app/store";

export const MainTable = () => {
  const [searchParams] = useSearchParams();
  const { data: tabledata } = useGetMainTableDataQuery(searchParams.toString());
  const { isExpanded } = useAppSelector((state) => state.mainTableExpand);
  const [expanded, setLocalExpanded] = useState<Record<string, boolean>>({});

  const transformedData = useMemo(() => {
    if (tabledata) {
      return transformDataWithSubRows(tabledata);
    }
    return [];
  }, [tabledata]);

  const activeRowIndex = useMemo(() => {
    const months = [
      "январь",
      "февраль",
      "март",
      "апрель",
      "май",
      "июнь",
      "июль",
      "август",
      "сентябрь",
      "октябрь",
      "ноябрь",
      "декабрь",
    ];
    if (tabledata) {
      return tabledata.findIndex(
        (i) => i[0] === "Итого " + months[dayjs().month()]
      );
    }
    return -1;
  }, [tabledata]);

  const table = useReactTable({
    data: transformedData,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getExpandedRowModel: getExpandedRowModel(),
    getSubRows: (row) => row.subRows,
    state: {
      expanded,
    },
    onExpandedChange: (updater) => {
      setLocalExpanded((prev) => {
        if (typeof updater === "function") {
          const newState = updater(prev);
          return newState === true ? {} : newState; 
        }
        return updater === true ? {} : updater; // true означает "все свернуто"
      });
    },
  });

  const toggleAllRows = useCallback(() => {
    const newExpanded: Record<string, boolean> = {};
    table.getRowModel().rows.forEach((row) => {
      if (row.getCanExpand()) {
        newExpanded[row.id] = true;
      }
    });
    setLocalExpanded(newExpanded);
  }, [table]);

  useEffect(() => {
    if (isExpanded) {
      toggleAllRows();
    } else {
      setLocalExpanded({});
    }
  }, [isExpanded, toggleAllRows]);

  return (
    <div className="table-container" style={{ zoom: 0.8, height: "calc(50vh - 50px)",overflowY: "auto" }}>
     {tabledata &&  <Table view="bordered" size="md">
        <TableHeader className="table-header">
          <TableRow>
            {headerRows[0].map((header, index) => (
              <TableHead
                key={index}
                colSpan={header.colSpan}
                rowSpan={header.rowSpan}
                style={{
                  backgroundColor: [3, 4].includes(index)
                    ? "var(--xenon-blue-1)"
                    : "",
                  width: [0].includes(index) ? "250px" : "unset",
                }}
              >
                {header.name}
              </TableHead>
            ))}
          </TableRow>
          <TableRow>
            {headerRows[1].map((header, index) => (
              <TableHead
                key={index}
                colSpan={header.colSpan}
                rowSpan={header.rowSpan}
                style={{
                  backgroundColor: [0, 8, 12].includes(index)
                    ? "var(--xenon-blue-1)"
                    : "",
                }}
              >
                {header.name}
              </TableHead>
            ))}
          </TableRow>
          <TableRow>
            {headerRows[2].map((header, index) => (
              <TableHead
                key={index}
                colSpan={header.colSpan}
                rowSpan={header.rowSpan}
              >
                {header.name}
              </TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {table.getRowModel().rows.map((row) => (
            <TableRow key={row.id}>
              {row.getVisibleCells().map((cell) => {
                const jindex = cell.column.getIndex();
                return (
                  <TableCell
                    key={cell.id}
                    align={"center"}
                    style={{
                      fontSize: "16px",
                      paddingLeft:
                        jindex === 0 && row.depth > 0
                          ? `${row.depth * 20}px`
                          : undefined,
                      backgroundColor: [3, 4, 5, 15, 19, 21].includes(jindex)
                        ? "var(--xenon-blue-1)"
                        : [7, 16].includes(jindex)
                          ? "var(--xenon-green-1)"
                          : activeRowIndex === row.index
                            ? "var(--xenon-color-bg-text-hover)"
                            : "",
                      whiteSpace: row.index === 0 ? "nowrap" : "",
                    }}
                  >
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </TableCell>
                );
              })}
            </TableRow>
          ))}
        </TableBody>
      </Table>}
    </div>
  );
};
