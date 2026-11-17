import { WaterfallChart } from "@/shared/ui";
import { Card, Modal, Typography } from "@tinkerbells/xenon-ui";
import { FC, useState } from "react";
import { waterfallDemoOptions } from "./utils/demoWaterfallOptions";
import { WaterfallChartFields } from "../../api/waterfall";
import { waterfallOptions } from "@/shared/ui/WaterfallChart/utils/waterfallOptions";
import { needsWaterfallOptions } from "@/shared/ui/WaterfallChart/utils/needsChartOptions";
import Loader from "@/shared/ui/Loader/Loader";

interface DetailsCardProps {
  waterfallData: WaterfallChartFields[];
  loading?: boolean;
}

export const DetailsCard: FC<DetailsCardProps> = ({
  waterfallData,
  loading,
}) => {
  const [open, setOpen] = useState({ name: "", open: false });
  return (
    <Card title="Баланс по заводам" className="card">
      {loading ? (
        <Loader width={85} />
      ) : (
        <div className="detalization">
          {waterfallData.map((data, key) => {
            return (
              <div
                key={key}
                className="factory-card"
                style={{
                  cursor: "pointer",
                  width: "100%",
                }}
                onClick={() => {
                  setOpen({ name: data.name, open: true });
                }}
              >
                <Typography
                  className="factory-card__title"
                  level="heading5"
                  weight={500}
                  style={{ marginBottom: "0px" }}
                >
                  {data.name}
                </Typography>
                <div>
                  <WaterfallChart options={waterfallDemoOptions(data)} />
                </div>
              </div>
            );
          })}
          <Modal
            open={open.open}
            onCancel={() => setOpen({ name: "", open: false })}
            okButtonProps={{ style: { display: "none" } }}
            cancelButtonProps={{ style: { display: "none" } }}
            centered
            width={"50%"}
            destroyOnHidden
          >
            <div>
              <Typography level="heading3">{open.name} </Typography>
              <WaterfallChart
                options={waterfallOptions(
                  waterfallData.filter((item) => item.name === open.name)[0]
                )}
                needsOption={needsWaterfallOptions(
                  waterfallData.filter((item) => item.name === open.name)[0]
                )}
                adaptiveHeight
              />
            </div>
          </Modal>
        </div>
      )}
    </Card>
  );
};
