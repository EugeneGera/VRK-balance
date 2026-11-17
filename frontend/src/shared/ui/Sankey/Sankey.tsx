import { createHighchartsOptions } from "./utils/sankey";
import Highcharts from "highcharts";
import HighchartsReact from "highcharts-react-official";
import sankeyModule from "highcharts/modules/sankey";
import { Typography } from "@tinkerbells/xenon-ui";
import { Data } from "@/pages/balance/api/sankey";
import { AdaptiveGraph } from "@/widgets/adaptiveGraph/ui/AdaptiveGraph";

if (typeof sankeyModule === "function") {
  sankeyModule(Highcharts);
} else if (sankeyModule.default && typeof sankeyModule.default === "function") {
  sankeyModule.default(Highcharts);
}

export const Sankey = ({
  data,
  sankeyMode,
  adjustHeight,
}: {
  data: {
    data: Data;
  };
  sankeyMode: string;
  adjustHeight?: number;
}) => {
  return (
    <>
      <div className="sankey-header">
        <Typography level="heading5">{sankeyMode}</Typography>
        <Typography level="heading5" style={{ marginLeft: "65px" }}>
          Направления сбыта
        </Typography>
        <Typography level="heading5">Категории сделки</Typography>
      </div>
      <AdaptiveGraph
        customHighcharts={Highcharts}
        options={createHighchartsOptions(data.data)}
        adaptiveHeight
        adjustHeight={adjustHeight}
      />
    </>
  );
};
