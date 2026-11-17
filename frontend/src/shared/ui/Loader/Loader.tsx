import { GazpromLoader } from "@/shared/assets/icons";
import { ReactElement } from "react";
import "./style.scss";
import { Spinner } from "../Spinner/Spinner";

function Loader({ width }: { width?: number }): ReactElement {
  return (
    <div className="loader-container">
      <div
        className="Loader"
        style={{ width: width + "px", height: width + "px" }}
      >
        <Spinner width={width + "px"} />
        <GazpromLoader color="#0079C2" width={"70%"} height={"70%"} />
        <p className="Loader-Text">Загрузка</p>
      </div>
    </div>
  );
}

export default Loader;
