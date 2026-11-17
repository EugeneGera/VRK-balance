import { createSlice, PayloadAction } from "@reduxjs/toolkit";

export interface RealizationItem {
  id: number;
  realization?: string;
  remark?: string;
}

interface RealizationState {
  realization: RealizationItem[];
}

const initialState: RealizationState = {
  realization: [],
};

const realizationSlice = createSlice({
  name: "realization",
  initialState,
  reducers: {
    addRealizationItem: (state, action: PayloadAction<RealizationItem>) => {
      const existingItemIndex = state.realization.findIndex(
        (item) => item.id === action.payload.id
      );

      if (existingItemIndex !== -1) {
        state.realization[existingItemIndex] = {
          ...state.realization[existingItemIndex],
          ...action.payload,
        };
      } else {
        state.realization.push(action.payload);
      }
    },
    deleteRealizationItem: (
      state,
      action: PayloadAction<{ id: number; fieldsToDelete: (keyof RealizationItem)[] }>
    ) => {
      const { id, fieldsToDelete } = action.payload;
      const itemIndex = state.realization.findIndex((item) => item.id === Number(id));

      if (itemIndex !== -1) {
        const updatedItem = { ...state.realization[itemIndex] };
        fieldsToDelete.forEach((field) => {
          if (field !== "id") {
            delete updatedItem[field];
          }
        });

        const hasOtherFields = Object.keys(updatedItem).some(
          (key) => key !== "id"
        );

        if (hasOtherFields) {
          state.realization[itemIndex] = updatedItem;
        } else {
          state.realization.splice(itemIndex, 1);
        }
      }
    },
    deleteAllRealizationItems: (state) => {
      state.realization = [];
    },
  },
});

export const { addRealizationItem, deleteAllRealizationItems, deleteRealizationItem } = realizationSlice.actions;
export default realizationSlice.reducer;
