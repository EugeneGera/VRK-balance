import { RouterProvider } from "react-router";
import { router } from "./routing/router";
import { Provider } from "react-redux";
import store from "./store";
import '@/shared/styles/reset.scss'
import '@/shared/styles/global.scss';


function App() {
  return (
    <Provider store={store}>
      <RouterProvider router={router} />
    </Provider>
  );
}

export default App;
