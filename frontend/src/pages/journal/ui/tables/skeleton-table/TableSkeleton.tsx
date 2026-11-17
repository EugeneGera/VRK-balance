import { Table } from "@tinkerbells/xenon-ui";

import { TableBodySkeleton } from "./table-body-skeleton";
import { TableHeaderSkeleton } from "./table-header-skeleton";
import { FC } from "react";

interface TableSkeletonProps {
  columns: number;
  widths: number[];
}
export const TableSkeleton: FC<TableSkeletonProps> = ({ columns, widths }) => {
  return (
    <Table>
      <TableHeaderSkeleton columns={columns} widths={widths} />
      <TableBodySkeleton columns={columns} rowCount={18} />
    </Table>
  );
};
