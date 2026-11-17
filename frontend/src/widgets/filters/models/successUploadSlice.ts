import { createSlice, PayloadAction } from "@reduxjs/toolkit";

export interface SuccsessUpload {
  succsessUpload: boolean;
}

const initialState: SuccsessUpload = {
  succsessUpload: false,
};

const succsessUploadSlice = createSlice({
  name: "isSuccessUpload",
  initialState,
  reducers: {
    setSuccsessUpload: (
      state,
      action: PayloadAction<SuccsessUpload["succsessUpload"]>
    ) => {
      state.succsessUpload = action.payload;
    },
  },
});

export const { setSuccsessUpload } = succsessUploadSlice.actions;
export default succsessUploadSlice.reducer;
