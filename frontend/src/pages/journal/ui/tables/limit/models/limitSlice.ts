import { createSlice, PayloadAction } from "@reduxjs/toolkit";

export interface LimitItem {
  id: number;
  min_left?: string;
  min_remark?: string;
  max_shipment?: string;
  max_remark?: string;
}

interface LimitState {
  limit: LimitItem[];
}

const initialState: LimitState = {
  limit: [],
};

const limitSlice = createSlice({
  name: "limit",
  initialState,
  reducers: {
    addLimitItem: (state, action: PayloadAction<LimitItem>) => {
      const existingItemIndex = state.limit.findIndex(
        (item) => item.id === action.payload.id
      );

      if (existingItemIndex !== -1) {
        state.limit[existingItemIndex] = {
          ...state.limit[existingItemIndex],
          ...action.payload,
        };
      } else {
        state.limit.push(action.payload);
      }
    },
    deleteLimitItem: (
      state,
      action: PayloadAction<{ id: number; fieldsToDelete: (keyof LimitItem)[] }>
    ) => {
      const { id, fieldsToDelete } = action.payload;
      const itemIndex = state.limit.findIndex((item) => item.id === id);

      if (itemIndex !== -1) {
        const updatedItem = { ...state.limit[itemIndex] };
        fieldsToDelete.forEach((field) => {
          if (field !== "id") {
            delete updatedItem[field];
          }
        });

        const hasOtherFields = Object.keys(updatedItem).some(
          (key) => key !== "id"
        );

        if (hasOtherFields) {
          state.limit[itemIndex] = updatedItem;
        } else {
          state.limit.splice(itemIndex, 1);
        }
      }
    },
    deleteAllLimitItems: (state) => {
      state.limit = [];
    },
  },
});

export const { addLimitItem, deleteAllLimitItems, deleteLimitItem } = limitSlice.actions;
export default limitSlice.reducer;
