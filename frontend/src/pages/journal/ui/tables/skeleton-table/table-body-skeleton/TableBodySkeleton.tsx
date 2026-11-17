import "./table-body-skeleton.styles.scss";
import {
  Skeleton,
  TableBody,
  TableCell,
  TableRow,
} from "@tinkerbells/xenon-ui";

interface TableBodySkeletonProps {
  columns: number;
  rowCount?: number;
}

export function TableBodySkeleton({
  columns,
  rowCount = 20,
}: TableBodySkeletonProps) {
  return (
    <TableBody className={"table-body-skeleton"}>
      {Array.from({ length: rowCount }).map((_, rowIndex) => (
        <TableRow
          key={`row-skeleton-${rowIndex}`}
          className={"body-skeleton-row"}
        >
          {Array.from({ length: columns }).map((_, colIndex) => (
            <TableCell key={`cell-skeleton-${rowIndex}-${colIndex}`}>
              <Skeleton
                paragraph={{
                  rows: 1,
                  width: "80%",
                }}
                title={false}
                className={"item"}
              />
            </TableCell>
          ))}
        </TableRow>
      ))}
    </TableBody>
  );
}
