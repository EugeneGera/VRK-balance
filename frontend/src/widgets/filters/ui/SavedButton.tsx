import { useAppSelector } from "@/app/store";
import { deleteAllLeftoversItems } from "@/pages/journal/ui/tables/leftovers/models/leftoversSlice";
import { deleteAllLimitItems } from "@/pages/journal/ui/tables/limit/models/limitSlice";
import { deleteAllPlanItems } from "@/pages/journal/ui/tables/plan/models/planSlice";
import { deleteAllRealizationItems } from "@/pages/journal/ui/tables/realization/models/realizationSlice";
import { Button, notification } from "@tinkerbells/xenon-ui";
import { FC, useCallback } from "react";
import { shallowEqual, useDispatch } from "react-redux";
import { setEndEdit, setSavedData } from "../models/currentTabSlice";
import {
  useUpdateApplicationsValuesMutation,
  useUpdateLeftoversValuesMutation,
  useUpdateLimitsValuesMutation,
  useUpdatePlansValuesMutation,
} from "@/pages/journal/api/journal";

export const SavedButton: FC = () => {
  const { tab } = useAppSelector((state) => state.currentTab, shallowEqual);
  const [updatePlansValues] = useUpdatePlansValuesMutation();
  const [updateApplicationsValues] = useUpdateApplicationsValuesMutation();
  const [updateLefoversValues] = useUpdateLeftoversValuesMutation();
  const [updateLimitsValues] = useUpdateLimitsValuesMutation();

  const currentState = useAppSelector((state) => {
    switch (state.currentTab.tab) {
      case "realization":
        return state.realization.realization;
      case "plan":
        return state.plan.plan;
      case "leftovers":
        return state.leftovers.leftovers;
      case "limit":
        return state.limit.limit;
      default:
        return [];
    }
  }, shallowEqual);

  const dispatch = useDispatch();

  const updatePlan = useCallback(() => {
    if (tab === "plan") {
      updatePlansValues({ plans: currentState });
      dispatch(deleteAllPlanItems());
    }
  }, [currentState, dispatch, tab, updatePlansValues]);

  const updateRealization = useCallback(() => {
    if (tab === "realization") {
      updateApplicationsValues({ applications: currentState });
      dispatch(deleteAllRealizationItems());
    }
  }, [currentState, dispatch, tab, updateApplicationsValues]);

  const updateLimits = useCallback(() => {
    if (tab === "limit") {
      updateLimitsValues({ limits: currentState });
      dispatch(deleteAllLimitItems());
    }
  }, [currentState, dispatch, tab, updateLimitsValues]);

  const updateLeftovers = useCallback(() => {
    if (tab === "leftovers") {
      updateLefoversValues({ leftovers: currentState });
      dispatch(deleteAllLeftoversItems());
    }
  }, [currentState, dispatch, tab, updateLefoversValues]);

  const onClick = useCallback(() => {
    const actions = {
      realization: updateRealization,
      plan: updatePlan,
      leftovers: updateLeftovers,
      limit: updateLimits,
    };

    const actionCreator = actions[tab];
    if (actionCreator) {
      try {
        actionCreator();
        notification({
          title: "Успешное сохранение",
          status: "success",
          position: "bottom-right",
        });
      } catch {
        notification({
          title: "Ошибка при сохранении",
          status: "error",
          position: "bottom-right",
        });
      }
    }

    dispatch(setEndEdit(true));
    dispatch(setSavedData(true))
  }, [
    dispatch,
    tab,
    updateLeftovers,
    updateLimits,
    updatePlan,
    updateRealization,
  ]);

  return (
    <Button disabled={currentState.length === 0} onClick={onClick} style={{width: "190px"}}>
      Сохранить изменения
    </Button>
  );
};
