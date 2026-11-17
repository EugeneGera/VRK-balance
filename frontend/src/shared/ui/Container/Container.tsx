import { ReactNode } from "react";
import "./style.scss";

export const Container = ({
  className,
  children,
  style,
}: {
  className?: string;
  children?: ReactNode;
  style?: React.CSSProperties;
}) => {
  return (
    <div style={style} className={`container ${className ? className : ""}`}>
      {children}
    </div>
  );
};
