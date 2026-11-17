import { Card, Radio, Select } from "@tinkerbells/xenon-ui";
import { FC, useState } from "react";
import { useGetChartDataQuery } from "../api/sankey";
import { useNavigate, useSearchParams } from "react-router";
import Loader from "@/shared/ui/Loader/Loader";
import { Sankey, WaterfallChart } from "@/shared/ui";
import { waterfallOptions } from "@/shared/ui/WaterfallChart/utils/waterfallOptions";
import { WaterfallChartFields } from "../api/waterfall";
import { EmptyDataPlaceholder } from "@/shared/ui/EmptyDataPlaceholder/EmptyDataPlaceholder";

interface RecourceCardProps {
  waterfallData: WaterfallChartFields;
  unit: string;
  waterfallLoading: boolean;
}

const sankeySwitchers: { key: string; value: string }[] = [
  {
    value: "Заводы",
    key: "factories",
  },
  {
    value: "Продукты",
    key: "products",
  },
];

const radioButtons = [
  { id: "waterfall", value: "Водопадная диаграмма" },
  { id: "sankey", value: "Баланс потоков" },
];

const ADJUST_HEIGHT_SMALL = 70;
const ADJUST_HEIGHT_LARGE = -120;
export const ResourceCard: FC<RecourceCardProps> = ({
  waterfallData,
  unit,
  waterfallLoading,
}) => {
  const [activeState, setActiveState] = useState<"waterfall" | "sankey">(
    "waterfall"
  );

  const [searchParams] = useSearchParams();
  const sankeyMode =
    sankeySwitchers.find(
      (item) => item.key === searchParams.get("grouping_mode")
    ) ?? sankeySwitchers[0];

  const [activeStateSankey, setActiveStateSankey] = useState(sankeyMode);

  const navigate = useNavigate();

  const {
    data: sankeyData,
    isFetching: sankeyFetching,
    isLoading: sankeyLoading,
  } = useGetChartDataQuery(searchParams.toString());
  const isLoading = sankeyLoading || sankeyFetching || waterfallLoading;

  const switcherClick = (key: string) => {
    const newSearchParams = new URLSearchParams(location.search);
    const selectedSankeyMode = sankeySwitchers.find(
      (item) => item.value === key
    )!;

    setActiveStateSankey(selectedSankeyMode);

    newSearchParams.set("grouping_mode", selectedSankeyMode.key);
    navigate(`?${newSearchParams.toString()}`);
  };

  return (
    <Card
      title={`Общий баланс распределения${unit ? ", " + unit : ""}`}
      className="card"
      extra={
        <div className="card__switchers">
          {activeState === "sankey" && (
            <Select
              value={activeStateSankey.value}
              onChange={(value) => switcherClick(value)}
              options={sankeySwitchers}
              style={{ placeSelf: "end", minWidth: "150px" }}
            />
          )}

          <div
            style={{
              display: "grid",
              gridAutoFlow: "column",
              gridColumn: "2/-1",
              justifyContent: "end",
            }}
          >
            <Radio.Group
              onChange={(e) => setActiveState(e.target.value)}
              value={activeState}
            >
              {radioButtons.map((radioButton) => (
                <Radio.Button key={radioButton.id} value={radioButton.id}>
                  {radioButton.value}
                </Radio.Button>
              ))}
            </Radio.Group>
          </div>
        </div>
      }
    >
      <div
        style={{
          display: "flex",
          paddingInline: "10px",
          placeContent: "center",
          height: "100%",
        }}
      >
        {isLoading ? (
          <div style={{ placeSelf: "center" }}>
            <Loader width={85} />
          </div>
        ) : (
          <div style={{ width: "100%"}}>
            {activeState === "sankey" ? (
              sankeyData && Object.keys(sankeyData).length !== 0 ? (
                <Sankey
                  data={sankeyData}
                  adjustHeight={window.innerHeight > 1100 ? ADJUST_HEIGHT_SMALL : ADJUST_HEIGHT_LARGE}
                  sankeyMode={activeStateSankey.value}
                />
              ) : (
                <EmptyDataPlaceholder width={"50%"} height={"50%"} />
              )
            ) : waterfallData && waterfallData.data ? (
              <WaterfallChart
                options={waterfallOptions(waterfallData)}
                legend
                adaptiveHeight
                adjustHeight={window.innerHeight > 1100 ? ADJUST_HEIGHT_SMALL : ADJUST_HEIGHT_LARGE}
                lowRest={waterfallData.data.resource_leftover.leftovers < 0}
              />
            ) : (
              <EmptyDataPlaceholder width={"50%"} height={"50%"} />
            )}
          </div>
        )}
      </div>
    </Card>
  );
};
