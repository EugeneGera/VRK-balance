import { Card, Typography } from "@tinkerbells/xenon-ui";
import { useSearchParams } from "react-router";
import { StackedBarChart } from "@/shared/ui";

import { useGetStockDetalizationQuery } from "@/pages/balance/api/stock";
import { createHighchartsBarOptions } from "./utils/barChartStockMarketCard";
import { EmptyDataPlaceholder } from "@/shared/ui/EmptyDataPlaceholder/EmptyDataPlaceholder";
import { FC } from "react";
import Loader from "@/shared/ui/Loader/Loader";

const legendData = [
  { color: "#108E9C", name: "Реализация на бирже" },
  { color: "#24AFBE", name: "Внебиржевая реализация" },
  { color: "#c5c5c5", name: "Биржа обязательства" },
  { color: "#646CDF", name: "Биржа доп. объемы" },
];

interface StockMarketCardProps {
  unit: string;
}
export const StockMarketCard: FC<StockMarketCardProps> = ({ unit }) => {
  const [searchParams] = useSearchParams();

  const {
    data: marketData,
    isLoading: marketLoading,
    isFetching: marketFetching,
  } = useGetStockDetalizationQuery(searchParams.toString());

  const stockTypes = [
    { id: "percent", value: "В процентах" },
    { id: "absolute", value: "В " + unit },
  ];
  const loading = marketLoading || marketFetching;
  return (
    <Card title="Реализация на бирже" className="card">
      {loading ? (
        <Loader width={85} />
      ) : (
        <div className="stock-market-card-body">
          <div className="legend-stock-card">
            {legendData.map((elm) => (
              <div key={elm.name}>
                <span
                  className="legend-stock-card__color"
                  style={{
                    backgroundColor: elm.color,
                  }}
                />
                <span className="legend-stock-card__name">{elm.name}</span>
              </div>
            ))}
          </div>
          {stockTypes.map((type) => (
            <div key={type.id}>
              <div className="structure-realization">
                {marketData &&
                  marketData[type.id as "percent" | "absolute"].map((data) => {
                    let isEmpty = true;
                    data.data.forEach((item) => {
                      if (item.value) {
                        isEmpty = false;
                      }
                    });
                    return (
                      <div
                        className="factory-card"
                        style={{ padding: "6px" }}
                        key={data.month}
                      >
                        <div className="structure-realization__title">
                          <Typography
                            className="factory-card__title"
                            level="body"
                            weight={500}
                          >
                            {data.month}
                          </Typography>

                          <Typography
                            color="secondary"
                            className="stock-market__title"
                            as={"p"}
                            style={{ placeSelf: "end", paddingRight: "10px" }}
                          >
                            {type.value}
                          </Typography>
                        </div>

                        {isEmpty ? (
                          <EmptyDataPlaceholder width={140} height={80} />
                        ) : (
                          <StackedBarChart
                            options={createHighchartsBarOptions(
                              data.data,
                              type.id as "percent" | "absolute"
                            )}
                          />
                        )}
                      </div>
                    );
                  })}
              </div>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
};
