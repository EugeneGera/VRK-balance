import { SeriesOptionsType } from "highcharts";

function drawTotalValue(
  this: Highcharts.Chart,
  data: { realization: number; exchange: number }
) {
  const chart = this as Highcharts.Chart & {
    customTotalLabels: Highcharts.SVGElement[];
  };
  const renderer = chart.renderer;

  if (chart.customTotalLabels) {
    chart.customTotalLabels.forEach((label) => label.destroy());
  }
  chart.customTotalLabels = [];

  const xPosition = chart.plotLeft + chart.plotWidth + 10;

  const categoryHeight = chart.plotHeight / 2;
  const yRealization = chart.plotTop + categoryHeight / 2;
  const yExchange = chart.plotTop + chart.plotHeight - categoryHeight / 2;

  // "Реализация"
  const label1 = renderer
    .text(String(data.realization === 0 ? data.realization : data.realization.toFixed(2)), xPosition, yRealization + 5)
    .css({
      color: "var(--xenon-color-text)",
      fontSize: "14px",
      fontWeight: "bold",
    })
    .add();
  chart.customTotalLabels.push(label1);

  // "Реализация на бирже"
  const label2 = renderer
    .text(String(data.exchange === 0 ? data.exchange : data.exchange.toFixed(2)), xPosition, yExchange + 5)
    .css({
      color: "var(--xenon-color-text)",
      fontSize: "14px",
      fontWeight: "bold",
    })
    .add();
  chart.customTotalLabels.push(label2);
}

function drawVerticalLinesForExchange(this: Highcharts.Chart) {
  const chart = this as Highcharts.Chart & {
    customExchangeLines?: Highcharts.SVGElement[];
  };
  const renderer = chart.renderer;

  if (chart.customExchangeLines) {
    chart.customExchangeLines.forEach(line => line.destroy());
  }
  chart.customExchangeLines = [];

  const categoryIndex = 1; // "Реализация на бирже"
  const yAxis = chart.yAxis[0];

  let total = 0;

  chart.series.forEach(series => {
    const point = series.points[categoryIndex] as Highcharts.Point & {y: number};
    if (point && point.y > 0) {
      total += point.y;
    }
  });

  const leftX = yAxis.toPixels(0);
  const rightX = yAxis.toPixels(total);

  const padding = 6.5;
  const minY = chart.plotTop + padding;
  const maxY = chart.plotTop + chart.plotHeight - padding;

  const strokeColor = 'var(--xenon-color-bg-mask)';

  const leftLine = renderer
    .path(['M', leftX, minY, 'L', leftX, maxY] as const)
    .attr({
      stroke: strokeColor,
      'stroke-width': 2,
      zIndex: 3
    })
    .add();

  const rightLine = renderer
    .path(['M', rightX, minY, 'L', rightX, maxY] as const)
    .attr({
      stroke: strokeColor,
      'stroke-width': 2,
      zIndex: 3
    })
    .add();

  chart.customExchangeLines!.push(leftLine, rightLine);
}

export const createHighchartsBarOptions = (
  data: {
    value: number;
    type: string;
    category?: string;
  }[],
  type: "percent" | "absolute"
): Highcharts.Options => {
  let onExchange = 0;
  let offExchange = 0;
  let obligation = 0;
  let additional = 0;

  data.forEach((item) => {
    switch (item.type) {
      case "Реализация на бирже":
        onExchange = item.value;
        break;
      case "Внебиржевая реализация":
        offExchange = item.value;
        break;
      case "Биржа обязательства":
        obligation = item.value;
        break;
      case "Биржа доп. объёмы":
        additional = item.value;
        break;
      default:
        break;
    }
  });

  const valueSuffix = type === "percent" ? "%" : "";

  return {
    chart: {
      type: "bar",
      height: 100,
      backgroundColor: "transparent",
      spacingRight: type === "absolute" ? 70 : 0,
      events: {
        load: function () {
          if (type === "absolute") {
            drawTotalValue.call(this, {
              realization: (onExchange ?? 0) + (offExchange ?? 0),
              exchange: obligation + additional,
            });
          }
          drawVerticalLinesForExchange.call(this);
        },
        redraw: function () {
          if (type === "absolute") {
            drawTotalValue.call(this, {
              realization: (onExchange ?? 0) + (offExchange ?? 0),
              exchange: obligation + additional,
            });
          }
          drawVerticalLinesForExchange.call(this);
        },
      },
    },

    title: {
      text: undefined,
    },
    xAxis: {
      categories: ["Реализация", "Реализация на бирже"],
      labels: {
        enabled: false,
      },
      lineWidth: 0,
      tickWidth: 0,
      minorTickLength: 0,
      tickLength: 0,
      gridLineWidth: 0,
      maxPadding: 0,
      minPadding: 0,
      startOnTick: false,
      endOnTick: false,
      showLastLabel: true,
    },
    yAxis: {
      min: 0,
      title: {
        text: "",
      },
      labels: {
        enabled: false,
      },
      lineWidth: 0,
      tickWidth: 0,
      tickLength: 0,
      minorTickLength: 0,
      gridLineWidth: 0,
      endOnTick: false,
      startOnTick: false,
      minPadding: 0,
      showLastLabel: true,
    },
    legend: {
      enabled: false,
    },
    tooltip: {
      valueDecimals: 2,
      valueSuffix,
    },
    plotOptions: {
      bar: {
        groupPadding: 0.1,
        borderColor: "transparent",
      },
      series: {
        stacking: "normal",
        dataLabels: {
          enabled: true,
          color: "#fff",
          formatter: function (this) {
            if (this.y == null || this.y === 0) {
              return "";
            }
            return this.y.toFixed(2) + valueSuffix;
          },
        },
      },
    },
    series: [
      {
        name: "Внебиржевая реализация",
        data: [offExchange, 0],
        type: "bar",
        color: "#24AFBE",
      },
      {
        name: "Реализация на бирже",
        data: [onExchange, 0],
        type: "bar",
        color: "#108E9C",
      },

      {
        name: "Биржа обязательства",
        data: [0, obligation],
        type: "bar",
        color: "#c5c5c5",
      },
      {
        name: "Биржа доп. объёмы",
        data: [0, additional],
        type: "bar",
        color: "#646CDF",
      },
    ] as SeriesOptionsType[],
  };
};
