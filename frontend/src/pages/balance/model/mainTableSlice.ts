import { createSlice, PayloadAction } from "@reduxjs/toolkit";

export interface MainTableExpandState {
  isExpanded: boolean;
}

const initialState: MainTableExpandState = {
  isExpanded: false,
};

const mainTableExpandStateSlice = createSlice({
  name: "isExpanded",
  initialState,
  reducers: {
    setExpanded: (
      state,
      action: PayloadAction<MainTableExpandState["isExpanded"]>
    ) => {
      state.isExpanded = action.payload;
    },
  },
});

export const { setExpanded } = mainTableExpandStateSlice.actions;
export default mainTableExpandStateSlice.reducer;
