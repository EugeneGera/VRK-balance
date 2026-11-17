// useDateFilter.ts
import { useState } from "react";
import { useLocation, useNavigate } from "react-router";
import dayjs, { Dayjs } from "dayjs";

type DateType = Dayjs;

export const useDateFilter = () => {
  const [showYear, setShowYear] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const searchParams = new URLSearchParams(location.search);
  const currentMonth = dayjs().startOf("month");
  const year = Number(searchParams.get("year") || currentMonth.year());
  const month = Number(searchParams.get("month_start") || currentMonth.month() + 1);
  const range = currentMonth
    .year(Number.isInteger(year) && year > 0 ? year : currentMonth.year())
    .month(Number.isInteger(month) && month >= 1 && month <= 12 ? month - 1 : currentMonth.month());

  const onChangeDate = (range: DateType | null) => {
    const searchParams = new URLSearchParams(location.search);

    if (range) {
      searchParams.set("month_start", String(range.month() + 1));
      searchParams.set("year", String(range.year()));
      if (location.pathname.includes("business-journal")) {
        searchParams.set("month_end", String(range.month() + 1));
      }
    }
    if (!range) {
      searchParams.delete("month_start");
    }
    navigate(`?${searchParams.toString()}`);
  };

  const onPanelChange = (_: unknown, mode: [string, string]) => {
    setShowYear(mode[0] === "year" || mode[1] === "year");
  };

  return {
    range,
    showYear,
    selectedYear: range,
    onChangeDate,
    onPanelChange,
  };
};
