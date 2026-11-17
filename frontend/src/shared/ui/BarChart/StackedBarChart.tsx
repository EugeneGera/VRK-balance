import Highcharts from "highcharts";
import { AdaptiveGraph } from "@/widgets/adaptiveGraph/ui/AdaptiveGraph";

interface BarChartProps {
  options: Highcharts.Options;
}

Highcharts.setOptions({
  accessibility: {
    enabled: false,
  },
});

export const StackedBarChart: React.FC<BarChartProps> = ({ options }) => {
  return (
    <div>
      <AdaptiveGraph customHighcharts={Highcharts} options={options} adaptiveHeight />
    </div>
  );
};
