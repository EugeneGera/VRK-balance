import { InitialFilters } from "../../InitialFilters";

type PrivateRouteProps = {
  component: React.FC;
};

export const PrivateRoute: React.FC<PrivateRouteProps> = ({
  component: Component,
}) => {
  return <InitialFilters><Component /></InitialFilters>;
};


