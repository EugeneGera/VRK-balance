import { createSlice, PayloadAction } from "@reduxjs/toolkit";

export type CurrentSankey = { key: string; }

const initialState: CurrentSankey = 
    {
      key: "factories",
    }
  

const currentSankeySlice = createSlice({
  name: "isEdited",
  initialState,
  reducers: {
    setSankey: (state, action: PayloadAction<string>) => {
        state.key = action.payload
    },

  },
});

export const { setSankey } = currentSankeySlice.actions;
export default currentSankeySlice.reducer;