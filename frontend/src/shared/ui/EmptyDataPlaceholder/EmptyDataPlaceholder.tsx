import { EmptyData } from "@/shared/assets/icons";
import { Typography } from "@tinkerbells/xenon-ui";
import { FC } from "react";
import "./style.scss";

interface EmptyDataPlaceholderProps {
    width?: string | number;
    height?: string | number;
    aspectRatio?: number;
}
export const EmptyDataPlaceholder: FC<EmptyDataPlaceholderProps> = ({width, height, aspectRatio}) => {
  return (
    <div className="empty">
      <EmptyData width={width} height={height} aspectRatio={aspectRatio} />
      <Typography level="body">Нет данных</Typography>
    </div>
  );
};
