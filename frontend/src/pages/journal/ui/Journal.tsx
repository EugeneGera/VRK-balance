import { Header } from "@/shared/ui";
import { Container } from "@/shared/ui/Container/Container";
import { Card, Tabs } from "@tinkerbells/xenon-ui";
import { FC } from "react";
import "./style.scss";
import { Filters } from "@/widgets/filters";
import { TableLeftovers } from "./tables/leftovers";
import { TableRealizationRequests } from "./tables/realization";
import { TablePlan } from "./tables/plan";
import { TableLimit } from "./tables/limit";
import { useDispatch } from "react-redux";
import {
  CurrentTab,
  setEndEdit,
  setSavedData,
  setTab,
} from "@/widgets/filters/models/currentTabSlice";
import { deleteAllLeftoversItems } from "./tables/leftovers/models/leftoversSlice";
import { deleteAllLimitItems } from "./tables/limit/models/limitSlice";
import { deleteAllPlanItems } from "./tables/plan/models/planSlice";
import { deleteAllRealizationItems } from "./tables/realization/models/realizationSlice";

const TABLES_TABS = [
  {
    label: "Заявки на реализацию",
    id: "realization",
    key: "1",
    children: <TableRealizationRequests />,
  },
  {
    label: "План производства",
    id: "plan",
    key: "2",
    children: <TablePlan />,
  },
  {
    label: "Остатки товарной продукции на начало месяца",
    id: "leftovers",
    key: "3",
    children: <TableLeftovers />,
  },
  {
    label: "Ограничения",
    id: "limit",
    key: "4",
    children: <TableLimit />,
  },
];

export const Journal: FC = () => {
  const dispatch = useDispatch();

  const handleChange = (activeKey: string) => {
    dispatch(
      setTab(TABLES_TABS[Number(activeKey) - 1].id as CurrentTab["tab"])
    );

    dispatch(deleteAllLeftoversItems());
    dispatch(deleteAllLimitItems());
    dispatch(deleteAllPlanItems());
    dispatch(deleteAllRealizationItems());
    dispatch(setEndEdit(true));
    dispatch(setSavedData(false));
  };

  return (
    <>
      <Header />
      <Container>
        <Filters />
        <Card className="journals-card">
          <Tabs
            destroyOnHidden
            defaultActiveKey="1"
            type="card"
            style={{ marginBottom: 32 }}
            items={TABLES_TABS}
            onChange={handleChange}
          />
        </Card>
      </Container>
    </>
  );
};
