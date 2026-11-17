import { configureStore } from "@reduxjs/toolkit";
import { setupListeners } from "@reduxjs/toolkit/query";
import {
  TypedUseSelectorHook,
  useDispatch,
  useSelector,
  useStore,
} from "react-redux";

import { journalApi } from "@/pages/journal/api/journal";
import { sankeyAPI } from "@/pages/balance/api/sankey";
import { factoriesAPI } from "@/entities/factories/api";
import { productsAPI } from "@/entities/products/api";
import { stockAPI } from "@/pages/balance/api/stock";
import { mainTableAPI } from "@/pages/balance/api/table";
import leftoversReducer from "@/pages/journal/ui/tables/leftovers/models/leftoversSlice";
import limitReducer from "@/pages/journal/ui/tables/limit/models/limitSlice";
import planReducer from "@/pages/journal/ui/tables/plan/models/planSlice";
import realizationReducer from "@/pages/journal/ui/tables/realization/models/realizationSlice";
import currentTabReducer from "@/widgets/filters/models/currentTabSlice";
import currentSankeyReducer from "@/pages/balance/model/currentSankeySlice";
import succsessUploadReducer from "@/widgets/filters/models/successUploadSlice";
import { uploadApi } from "@/features/upload/api";
import { directoriesApi } from "@/pages/DirectoryPage/api";
import { categoryAPI } from "@/entities/categories/api";
import mainTableExpandStateReducer from "@/pages/balance/model/mainTableSlice";
import { waterfallAPI } from "@/pages/balance/api/waterfall";

const store = configureStore({
  reducer: {
    [journalApi.reducerPath]: journalApi.reducer,
    [sankeyAPI.reducerPath]: sankeyAPI.reducer,
    [factoriesAPI.reducerPath]: factoriesAPI.reducer,
    [productsAPI.reducerPath]: productsAPI.reducer,
    [stockAPI.reducerPath]: stockAPI.reducer,
    [mainTableAPI.reducerPath]: mainTableAPI.reducer,
    [uploadApi.reducerPath]: uploadApi.reducer,
    [directoriesApi.reducerPath]: directoriesApi.reducer,
    [categoryAPI.reducerPath]: categoryAPI.reducer,
    [waterfallAPI.reducerPath]: waterfallAPI.reducer,
    leftovers: leftoversReducer,
    limit: limitReducer,
    plan: planReducer,
    realization: realizationReducer,
    currentTab: currentTabReducer,
    mainTableExpand: mainTableExpandStateReducer,
    succsessUpload: succsessUploadReducer,
    currentSankey: currentSankeyReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false,
    }).concat(
      uploadApi.middleware,
      journalApi.middleware,
      sankeyAPI.middleware,
      factoriesAPI.middleware,
      productsAPI.middleware,
      stockAPI.middleware,
      mainTableAPI.middleware,
      directoriesApi.middleware,
      categoryAPI.middleware,
      waterfallAPI.middleware
    ),
});

setupListeners(store.dispatch);

export default store;

export type AppStore = typeof store;
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

export const useAppDispatch: () => AppDispatch = useDispatch;
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;
export const useAppStore: () => AppStore = useStore;
