import { ReactElement } from "react";
import "./style.scss";

export function Spinner ({width, color}: {width?: string, color?: string}): ReactElement {

    return (
        <div className="spinner" style={{width: width, height: width, borderTopColor: color, borderRightColor: color}}>
        </div>
    )
}