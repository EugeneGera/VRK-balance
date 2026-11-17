import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@tinkerbells/xenon-ui";
import { useEffect, useRef } from "react";
import {
  useReactTable,
  getCoreRowModel,
  getFilteredRowModel,
  flexRender,
} from "@tanstack/react-table";
import { useVirtualizer } from "@tanstack/react-virtual";
import { getColumns } from "./TablePlanColumns";
import "../../table.style.scss";
import { useSearchParams } from "react-router";
import { useGetPlansQuery } from "@/pages/journal/api/journal";
import { TableSkeleton } from "../../skeleton-table";
import { useAppSelector } from "@/app/store";

export const TablePlan = () => {
  const [searchParams] = useSearchParams();

  const {
    data = { plans: [] },
    isLoading,
    isFetching,
    refetch,
  } = useGetPlansQuery(searchParams.toString());

  const savedData = useAppSelector((state) => state.currentTab.savedData);
  const successUpload = useAppSelector((state) => state.succsessUpload);
  

  const columns = getColumns();

  const table = useReactTable({
    data: data.plans,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
  });

  const { rows } = table.getRowModel();
  const parentRef = useRef<HTMLDivElement>(null);

  const rowVirtualizer = useVirtualizer({
    getScrollElement: () => parentRef.current,
    count: rows.length,
    estimateSize: () => 45,
    overscan: 6,
  });

  useEffect(() => {
    if (savedData || successUpload) {
      refetch();
    }
  }, [refetch, savedData, successUpload]);

  if (isLoading || isFetching) {
    return (
      <TableSkeleton
        columns={columns.length}
        widths={columns.map((col) => col.size ?? 30)}
      />
    );
  }

  return (
    <div className="scroll-area">
      <div
        ref={parentRef}
        style={{ height: `${rowVirtualizer.getTotalSize()}px` }}
      >
        <Table style={{ width:"100%" }} size="sm">
          <TableHeader className="table-header">
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <TableHead
                    key={header.id}
                    style={{ width: header.getSize() }}
                  >
                    {flexRender(
                      header.column.columnDef.header,
                      header.getContext()
                    )}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {rowVirtualizer.getVirtualItems().map((virtualRow) => {
              const row = rows[virtualRow.index];
              return (
                <TableRow key={row.id}>
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id} style={{textAlign: "center"}}> 
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext()
                      )}
                    </TableCell>
                  ))}
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </div>
    </div>
  );
};
