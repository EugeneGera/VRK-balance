import { createSlice, PayloadAction } from "@reduxjs/toolkit";

export interface LeftoversItem {
  id: number;
  left?: string;
  plan?: string;
  min_left?: string;
  max_shipment?: string;
  remark?: string;
}

interface LeftoversState {
  leftovers: LeftoversItem[];
}

const initialState: LeftoversState = {
  leftovers: [],
};

const leftoversSlice = createSlice({
  name: "leftovers",
  initialState,
  reducers: {
    addLeftoversItem: (state, action: PayloadAction<LeftoversItem>) => {
      const existingItemIndex = state.leftovers.findIndex(
        (item) => item.id === action.payload.id
      );

      if (existingItemIndex !== -1) {
        state.leftovers[existingItemIndex] = {
          ...state.leftovers[existingItemIndex],
          ...action.payload,
        };
      } else {
        state.leftovers.push(action.payload);
      }
    },
    deleteLeftoversItem: (
      state,
      action: PayloadAction<{ id: number; fieldsToDelete: (keyof LeftoversItem)[] }>
    ) => {
      const { id, fieldsToDelete } = action.payload;
      const itemIndex = state.leftovers.findIndex((item) => item.id === id);

      if (itemIndex !== -1) {
        const updatedItem = { ...state.leftovers[itemIndex] };
        fieldsToDelete.forEach((field) => {
          if (field !== "id") {
            delete updatedItem[field];
          }
        });

        const hasOtherFields = Object.keys(updatedItem).some(
          (key) => key !== "id"
        );

        if (hasOtherFields) {
          state.leftovers[itemIndex] = updatedItem;
        } else {
          state.leftovers.splice(itemIndex, 1);
        }
      }
    },
    deleteAllLeftoversItems: (state) => {
      state.leftovers = [];
    },
  },
});

export const { addLeftoversItem, deleteAllLeftoversItems, deleteLeftoversItem } = leftoversSlice.actions;
export default leftoversSlice.reducer;
