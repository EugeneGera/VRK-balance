import "./style.scss";

interface LegendProps {
  data: { type: string; value: number }[];
  color?: string[];
  showTotal?: boolean;
}

export const Legend: React.FC<LegendProps> = ({ data, color, showTotal }) => {
  const addTotal = (
    data: { type: string; value: number }[]
  ): { type: string; value: number }[] => {
    const totalValue = data.reduce((sum, item) => sum + item.value, 0);
    return [{ type: "Итого", value: totalValue }];
  };

  if (!data) return <div>Нет данных</div>;

  return (
    <div className="legend">
      {(showTotal ? [...data, ...addTotal(data)] : data).map((elm, key) => (
        <div key={key}>
          <div className="legend__item">
            <div
              className="legend__color"
              style={{ backgroundColor: color?.[key] || "#000" }}
            />
            <span className="legend__name">{elm.type}</span>
            <div className="legend__line" />
            <span className="legend__value">{elm.value}</span>
          </div>
          {key === 3 && <div className="legend__separator" />}
        </div>
      ))}
    </div>
  );
};
