import { createSlice, PayloadAction } from "@reduxjs/toolkit";

export interface CurrentTab {
  tab: "realization" | "plan" | "leftovers" | "limit";
  endEdit: boolean;
  savedData: boolean;
}

const initialState: CurrentTab = {
  tab: "realization",
  endEdit: true,
  savedData: false
};

const currentTabSlice = createSlice({
  name: "isEdited",
  initialState,
  reducers: {
    setTab: (state, action: PayloadAction<CurrentTab["tab"]>) => {
      state.tab = action.payload;
    },

    setEndEdit: (state, action: PayloadAction<CurrentTab["endEdit"]>) => {
      state.endEdit = action.payload;
    },

    setSavedData: (state, action: PayloadAction<CurrentTab["savedData"]>) => {
      state.savedData = action.payload
    }
  },
});

export const { setTab, setEndEdit, setSavedData } = currentTabSlice.actions;
export default currentTabSlice.reducer;
