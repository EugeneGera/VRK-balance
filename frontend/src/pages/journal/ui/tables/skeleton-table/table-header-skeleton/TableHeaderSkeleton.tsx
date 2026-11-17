import { Skeleton, TableHead, TableHeader, TableRow } from '@tinkerbells/xenon-ui'

interface TableHeaderSkeletonProps {
  columns: number
  widths?: (string | number)[]
}

export function TableHeaderSkeleton({ columns, widths = [] }: TableHeaderSkeletonProps) {
  return (
    <TableHeader className={"table-header-skeleton"}>
      <TableRow>
        {Array.from({ length: columns }).map((_, index) => {
          const width = widths[index] || 'auto'

          return (
            <TableHead
              key={`header-skeleton-${index}`}
              style={{ width }}
            >
              <Skeleton
                className={'skeleton'}
                title={false}
                paragraph={{
                  rows: 1,
                }}
              />
            </TableHead>
          )
        })}
      </TableRow>
    </TableHeader>
  )
}
