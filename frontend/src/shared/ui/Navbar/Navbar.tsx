import { MenuProps, Menu } from "@tinkerbells/xenon-ui";
import { FC, useState, useTransition } from "react";
import { useLocation, useNavigate, useSearchParams } from "react-router";
import "./style.scss";

type MenuItem = Required<MenuProps>["items"][number];

const items: MenuItem[] = [
  {
    label: "Баланс распределения",
    key: "/balance_comission",
  },
  {
    label: "Журналы",
    key: "/balance_comission/business-journal",
  },
  // {
  //   label: "Редактирование справочников",
  //   key: "/balance_comission/directory",
  // },
];

export const Navbar: FC = () => {
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const [current, setCurrent] = useState(pathname);
  const [isPending, startTransition] = useTransition();
  const [searchParams] = useSearchParams();

  const onClick: MenuProps["onClick"] = (e) => {
    startTransition(() => {
      setCurrent(e.key);
      navigate(`${e.key}?${searchParams.toString()}`);
    });
  };
  return (
    <Menu
      onClick={onClick}
      mode="horizontal"
      selectedKeys={[current ?? "/balance_comission"]}
      items={items}
      style={{ opacity: isPending ? 0.8 : 1, minWidth: "800px" }}
    />
  );
};
