import { forwardRef, useEffect, useImperativeHandle, useRef } from "react";
import "highcharts/highcharts-more";
import HighchartsReact from "highcharts-react-official";
import Highcharts from "highcharts";
import { debounce } from "@/shared/lib/debounce";
import { customHighchartsTranslation } from "@/shared/lib/translation/translation";

Highcharts.setOptions({
  lang: customHighchartsTranslation,
  accessibility: {
    enabled: false,
  },
});

interface AdaptiveGraphProps {
  className?: string;
  onInit?: (chart: Highcharts.Chart) => void;
  options: Highcharts.Options;
  adjustHeight?: number;
  adjustWidth?: number;
  customHighcharts?: typeof Highcharts;
  useAdaptive?: boolean;
  adaptiveHeight?: boolean;
}

export interface AdaptiveGraphRef {
  chartRef: React.RefObject<HighchartsReact.RefObject | null>;
}

export const AdaptiveGraph = forwardRef<AdaptiveGraphRef, AdaptiveGraphProps>(
  (
    {
      className,
      onInit,
      options,
      customHighcharts,
      adjustHeight,
      adjustWidth,
      useAdaptive = true,
      adaptiveHeight = false,
    },
    ref
  ) => {
    const chartRef = useRef<HighchartsReact.RefObject>(null);
    const containerRef = useRef<HTMLDivElement>(null);

    useImperativeHandle(ref, () => ({
      chartRef,
    }));
    useEffect(() => {
      if (useAdaptive) {
        const container = containerRef.current;

        if (chartRef.current) {
          const { chart } = chartRef.current;
          onInit?.(chart);

          if (container) {
            chart.setSize(
              container.clientWidth + (adjustWidth ?? 0),
              adaptiveHeight
                ? container.clientHeight + (adjustHeight ?? -20)
                : null
            );

            const handleResize = debounce((entries: ResizeObserverEntry[]) => {
              const { contentRect } = entries[0];
              chart.setSize(contentRect.width + (adjustWidth ?? 0), null);
            }, 50);

            const resizeObserver = new ResizeObserver((entries) => {
              handleResize(entries);
            });

            resizeObserver.observe(container);

            return () => {
              handleResize.cancel();
              resizeObserver.disconnect();
            };
          }
        }
      }
    }, [useAdaptive, adaptiveHeight, adjustHeight, onInit, adjustWidth]);

    return (
      <div className={className} ref={containerRef}>
        <HighchartsReact
          highcharts={customHighcharts || Highcharts}
          options={options}
          ref={chartRef}
        />
      </div>
    );
  }
);
