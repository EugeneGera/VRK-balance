import { FC } from "react";
import Highcharts from "highcharts";
import "highcharts/highcharts-more";
import { AdaptiveGraph } from "@/widgets/adaptiveGraph/ui/AdaptiveGraph";

interface WaterfallProps {
  options: Highcharts.Options;
  needsOption?: Highcharts.Options;
  legend?: boolean;
  lowRest?: boolean;
  adaptiveHeight?: boolean;
  adjustHeight?: number;
}

export const WaterfallChart: FC<WaterfallProps> = ({
  options,
  legend,
  lowRest,
  adaptiveHeight = true,
  adjustHeight,
  // needsOption,
}) => {
  const legendOptions = [
    { color: "#0679BB", name: "План" },
    { color: "#6AE0ED", name: "Остатки" },
    { color: "#32B4FF", name: "Доступный ресурс" },
    { color: "#12B47E", name: "Распределённый ресурс" },
    { color: !lowRest ? "#6B8ABC" : "#FFC5C7", name: "Остаток ресурса" },
    { color: "#32B4FF30", name: "Ограничения" },
    { color: "var(--xenon-color-fill-secondary)", name: "Доп. потребность" },
  ];
  return (
    <div
      style={{
        display: "grid",
        gap: "10px",
        maxHeight: "100%",
        alignContent: "space-between",
      }}
    >
      <div style={{ display: "grid", gridAutoFlow: "column" }}>
        {legend &&
          legendOptions.map((item, key) => (
            <div
              key={key}
              style={{
                display: "grid",
                gridAutoFlow: "column",
                placeContent: "center",
                gap: "5px",
              }}
            >
              <div
                style={{
                  backgroundColor: item.color,
                  width: "10px",
                  height: "10px",
                  borderRadius: "100%",
                  alignSelf: "center",
                }}
              />
              <span>{item.name}</span>
            </div>
          ))}
      </div>
      <div style={{ display: "grid", gridAutoFlow: "column" }}>
        <AdaptiveGraph
          customHighcharts={Highcharts}
          options={options}
          adaptiveHeight={adaptiveHeight}
          adjustHeight={adjustHeight}
        />
        {/* {needsOption && <AdaptiveGraph options={needsOption}  adaptiveHeight adjustHeight={-70}/>} */}
      </div>
    </div>
  );
};
