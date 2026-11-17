import { createSlice, PayloadAction } from "@reduxjs/toolkit";

export interface PlanItem {
  id: number;
  plan?: number;
  remark?: string;
}

interface PlanState {
  plan: PlanItem[];
}

const initialState: PlanState = {
  plan: [],
};

const planSlice = createSlice({
  name: "plan",
  initialState,
  reducers: {
    addPlanItem: (state, action: PayloadAction<PlanItem>) => {
      const existingItemIndex = state.plan.findIndex(
        (item) => item.id === action.payload.id
      );

      if (existingItemIndex !== -1) {
        state.plan[existingItemIndex] = {
          ...state.plan[existingItemIndex],
          ...action.payload,
        };
      } else {
        state.plan.push(action.payload);
      }
    },
    deletePlanItem: (
      state,
      action: PayloadAction<{ id: number; fieldsToDelete: (keyof PlanItem)[] }>
    ) => {
      const { id, fieldsToDelete } = action.payload;
      const itemIndex = state.plan.findIndex((item) => item.id === Number(id));

      if (itemIndex !== -1) {
        const updatedItem = { ...state.plan[itemIndex] };
        fieldsToDelete.forEach((field) => {
          if (field !== "id") {
            delete updatedItem[field];
          }
        });

        const hasOtherFields = Object.keys(updatedItem).some(
          (key) => key !== "id"
        );

        if (hasOtherFields) {
          state.plan[itemIndex] = updatedItem;
        } else {
          state.plan.splice(itemIndex, 1);
        }
      }
    },
    deleteAllPlanItems: (state) => {
      state.plan = [];
    },
  },
});

export const { addPlanItem, deleteAllPlanItems, deletePlanItem } =
  planSlice.actions;
export default planSlice.reducer;
