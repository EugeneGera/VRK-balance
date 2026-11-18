import { Container } from "@/shared/ui/Container/Container";
import { Header } from "@/shared/ui";
import { Filters } from "@/widgets/filters";

import { StockMarketCard } from "./StockMarketCard";

import "./style.scss";
import { useRef, useState } from "react";
import { BalanceReport } from "@/features/balance-report/BalanceReport";
import { ResourceCard } from "./ResourceCard";
import { MainTable } from "./Table/MainTable";
import { DetailsCard } from "./DetailsCard/DetailsCard";
import { useGetWaterfallDataQuery } from "../api/waterfall";
import { useLocation, useSearchParams } from "react-router";
import { Card } from "@tinkerbells/xenon-ui";

export const Balance = () => {
  const location = useLocation();
  const [reportOpen, setReportOpen] = useState(!!location.state?.openReport);
  const channelsRef = useRef<HTMLDivElement | null>(null);

  const [searchParams] = useSearchParams();
  const {
    data: waterfallData,
    isFetching: waterfallFetching,
    isLoading: waterfallLoading,
  } = useGetWaterfallDataQuery(searchParams.toString());
  const mainWaterfallData = waterfallData?.data.data.filter(
    (item) => item.name === "Total"
  );

  const detalizationWaterfallData = waterfallData?.data.data.filter(
    (item) => item.name !== "Total"
  );
  return (
    <div className="balance">
      <Header />
      <Container
        style={{
          height: "calc(100vh - 75px)",
          display: "grid",
          gridTemplateRows: "auto 1fr",
        }}
      >
        <Filters onOpenReport={() => setReportOpen(true)} />
        <div className="channels">
          <div className="channels__resource" ref={channelsRef}>
            {waterfallData && mainWaterfallData && (
              <ResourceCard
                waterfallData={mainWaterfallData[0]}
                unit={waterfallData.unit}
                waterfallLoading={waterfallLoading || waterfallFetching}
              />
            )}
          </div>

          <div className="channels__details">
            {waterfallData && detalizationWaterfallData && (
              <DetailsCard waterfallData={detalizationWaterfallData} loading ={waterfallLoading || waterfallFetching} />
            )}
          </div>

          <div className="channels__stock">
            <StockMarketCard unit={waterfallData?.unit ?? ""} />
          </div>

          <Card className="channels__table">
            <MainTable />
          </Card>
        </div>
      </Container>
      <BalanceReport open={reportOpen} onClose={() => setReportOpen(false)} search={searchParams.toString()} />
    </div>
  );
};
