import { WaterfallData } from "@/shared/ui/WaterfallChart/utils/types";

function drawCustomXAxis(this: Highcharts.Chart) {
  const chart = this as Highcharts.Chart & {
    customZeroLine?: Highcharts.SVGElement;
    customZeroLabel?: Highcharts.SVGElement;
  };

  if (chart.customZeroLine) {
    chart.customZeroLine.destroy();
    chart.customZeroLine = undefined;
  }

  if (chart.customZeroLabel) {
    chart.customZeroLabel.destroy();
    chart.customZeroLabel = undefined;
  }

  const xAxis = chart.xAxis[0] as Highcharts.Axis & {
    left: number;
    width: number;
  };
  const yAxis = chart.yAxis[0] as Highcharts.Axis;

  if (!xAxis || !yAxis) return;

  const yZero = yAxis.toPixels(0);
  const xStart = xAxis.left;
  const xEnd = xStart + xAxis.width;

  // Рисуем линию
  chart.customZeroLine = chart.renderer
    .path(["M", xStart + 15, yZero, "L", xEnd, yZero] as const)
    .attr({
      "stroke-width": 1,
      stroke: "#cccccc",
      zIndex: 5,
    })
    .add();

  // Рисуем 0
  chart.customZeroLabel = chart.renderer
    .text("0", xStart - 8, yZero + 4)
    .css({
      color: "var(--xenon-color-text-description)",
      fontSize: "12px",
      fontWeight: "bold",
      fill: "var(--xenon-color-text-description)",
    })
    .add();
}

function drawTotalValue(
  this: Highcharts.Chart & { customTotalValues?: Highcharts.SVGElement[] },
  data: WaterfallData
) {
  if (this.customTotalValues) {
    this.customTotalValues.forEach((el) => el.destroy());
    this.customTotalValues = [];
  } else {
    this.customTotalValues = [];
  }

  const seriesList = this.series;
  const categories = this.xAxis[0]?.categories || [];
  const totalCategories = categories.length;

  for (
    let categoryIndex = 0;
    categoryIndex <= totalCategories - 1;
    categoryIndex++
  ) {
    let totalValue: number | null = null;
    let x: number | undefined;
    let width: number | undefined;
    let plotY: number | undefined;
    let margin: number | undefined;

    if (categoryIndex === 0) {
      totalValue = +(data.data.total.plan + data.data.total.leftovers).toFixed(
        2
      );
      const planSeries = seriesList.find((s) => s.name === "План");
      const point = planSeries?.points?.[0];
      if (point?.shapeArgs) {
        x = point.shapeArgs.x;
        width = point.shapeArgs.width;
        plotY = point.plotY;
      }
      margin = -4;
    } else if (categoryIndex === 1) {
      totalValue = +(
        data.data.available_resource.restrictions +
        data.data.available_resource.available
      ).toFixed(2);
      const restrictionSeries = seriesList.find(
        (s) => s.name === "Ограничения"
      );
      const point = restrictionSeries?.points?.[1];
      if (point?.shapeArgs) {
        x = point.shapeArgs.x;
        width = point.shapeArgs.width;
        plotY = point.plotY;
      }
      margin = -4;
    } else if (categoryIndex === 5) {
      totalValue = data.data.resource_leftover.leftovers;
      const leftoversSeries = seriesList.find(
        (s) => s.name === "Остаток ресурса"
      );

      const point = leftoversSeries?.points?.[5];

      if (point?.shapeArgs) {
        x = point.shapeArgs.x;
        width = point.shapeArgs.width;
        plotY = point.plotY;
      }
      margin = totalValue > 0 ? -4 : 4;
    } else {
      const distIndex = categoryIndex - 2;
      const item = data.data.distribution[distIndex];

      if (!item) continue;

      totalValue = +Math.abs(item.value).toFixed(2);

      const waterfallSeries = seriesList.find((s) => s.type === "waterfall");
      if (!waterfallSeries) continue;
      const columnRangeSeries = seriesList.find(
        (s) => s.type === "columnrange"
      );
      const columnRangePoint = columnRangeSeries?.points?.[categoryIndex];
      const point = waterfallSeries?.points?.[
        categoryIndex
      ] as Highcharts.Point & { box: { y: number } };
      const claimHeight = columnRangePoint?.shapeArgs?.height || 0;

      if (point?.shapeArgs) {
        x = point.shapeArgs.x;
        width = point.shapeArgs.width;
        plotY = point.box.y;
      }
      margin = item.claim ? claimHeight - 4 : -4;
    }
    if (
      totalValue === null ||
      x === undefined ||
      width === undefined ||
      plotY === undefined
    )
      continue;

    const centerX = x + width / 2;
    const textY = plotY - (margin ?? 0);

    const totalLabel = this.renderer
      .text(String(totalValue == 0 ? totalValue : totalValue.toFixed(2)), centerX + 8, textY + (totalValue >= 0 ? 4 : 0))
      .attr({
        align: "center",
      })
      .css({
        color: totalValue >= 0 ? "var(--xenon-color-text-base)" : "#ff6368ff",
        fontSize: "10px",
        fontWeight: "bold",
        fill: "var(--xenon-color-text-base)",
      })
      .add();

    this.customTotalValues.push(totalLabel);
  }
}

export const waterfallDemoOptions = (
  data: WaterfallData
): Highcharts.Options => {
  if (!data?.data) {
    return {};
  }

  const {
    distribution,
    available_resource: ar,
    total,
    resource_leftover: rl,
  } = data.data;

  if (!Array.isArray(distribution)) {
    return {};
  }

  const distLength = distribution.length;
  const nullsArr = new Array(distLength).fill(null);

  const waterfallElms = distribution.map(({ name, value }) => ({
    name,
    y: value,
  }));

  let cumulativeSum = ar?.available ?? 0;
  const claimArr = distribution.map((item) => {
    if (item.claim == null) {
      return null;
    }

    const start = Number(cumulativeSum.toFixed(2));
    const end = Number((cumulativeSum + item.claim).toFixed(2));

    cumulativeSum += item.value ?? 0;

    return [start, end];
  });

  const categories = [
    "Общий ресурс",
    "Доступный ресурс",
    ...distribution.map((item) => item.name),
    "Остаток ресурса",
  ];

  return {
    chart: {
      spacingBottom: 0,
      height: 75,
      backgroundColor: "transparent",
      events: {
        load: function () {
          drawCustomXAxis.call(this);
          drawTotalValue.call(this, data);
        },
        redraw: function () {
          drawCustomXAxis.call(this);
          drawTotalValue.call(this, data);
        },
      },
    },
    legend: { enabled: false },
    title: { style: { display: "none" } },
    xAxis: {
      type: "category",
      categories,
      lineWidth: 0,
      tickLength: 0,
      gridLineWidth: 0,
      labels: {
        enabled: true,
        y: 13,
        formatter: function () {
          let shortValue: string = "";
          switch (this.value) {
            case "Общий ресурс":
              shortValue = "ОбщР";
              break;
            case "Доступный ресурс":
              shortValue = "ДР";
              break;
            case "Остаток ресурса":
              shortValue = "ОстР";
              break;
            case "Внутренний рынок":
              shortValue = "ВР";
              break;
            case "Экспорт":
              shortValue = "Э";
              break;
            case "Нужды ДО":
              shortValue = "ДО";
              break;
          }
          return shortValue;
        },
        style: { fontSize: "10px", color: "var(--xenon-color-text-base)" },
      },
    },
    yAxis: { visible: false, gridLineWidth: 0 },
    tooltip: {
      enabled: false,
    },
    plotOptions: {
      waterfall: {
        pointWidth: 50,
        pointPadding: 0.1,
        groupPadding: 0.2,
        borderRadius: 2,
        borderWidth: 0,
        pointRange: 1,
        color: "#12B47E",
        pointPlacement: "on",
        lineColor: "var(--xenon-color-text)",
        dataLabels: {
          enabled: false,
        },
      },
      columnrange: {
        pointWidth: 50,
        borderWidth: 0,
        borderRadius: 2,
        dataLabels: {
          enabled: false,
          useHTML: true,
          crop: false,
          overflow: "justify",
          inside: true,
          allowOverlap: true,
          formatter: function (this: unknown) {
            const self = this as Highcharts.Point & {
              point: { high: number; low: number };
            };
            if (self.point.high === self.point.low) return null;
            const center = self.point.high - self.point.low;
            const gap = center < 5 ? -10 : 0;

            return `<div style="transform: translateY(${gap}px); color: var(--xenon-color-text-disabled); z-index: -1; font-size: 12px;">${center.toFixed(2)}</div>`;
          } as Highcharts.DataLabelsFormatterCallbackFunction,

          verticalAlign: "middle",
          style: {
            fontWeight: "400",
            fontSize: "12px",
          },
        } as Highcharts.SeriesAreaRangeDataLabelsOptionsObject,
      },
      column: {
        stacking: "normal",
        grouping: false,
        borderRadius: 2,
        pointWidth: 50,
        pointPadding: 0.1,
        groupPadding: 0.2,
        borderWidth: 0,
        pointRange: 1,
        negativeColor: "#FFC5C7",
        dataLabels: {
          enabled: false,
        },
      },
    },
    series: [
      {
        type: "column",
        name: "План",
        stack: "Общий ресурс",
        data: [
          { name: "План", y: total.plan, color: "#0679BB" },
          null,
          ...nullsArr,
          null,
        ] as Highcharts.PointOptionsObject[],
      },
      {
        type: "column",
        name: "Остатки",
        stack: "Общий ресурс",
        data: [
          { name: "Остатки", y: total.leftovers, color: "#6AE0ED" },
          null,
          ...nullsArr,
          null,
        ] as Highcharts.PointOptionsObject[],
      },
      {
        type: "column",
        name: "Ограничения",
        stack: "Доступный ресурс",
        data: [
          null,
          { name: "Ограничения", y: ar.restrictions, color: "#32B4FF30" },
          ...nullsArr,
          null,
        ] as Highcharts.PointOptionsObject[],
      },
      {
        type: "column",
        name: "Доступный ресурс",
        stack: "Доступный ресурс",
        data: [
          null,
          { name: "Доступный ресурс", y: ar.available, color: "#32B4FF" },
          ...nullsArr,
          null,
        ] as Highcharts.PointOptionsObject[],
      },
      {
        type: "waterfall",
        name: "Изменения",
        data: [
          null,
          { name: "Доступный ресурс", y: ar.available, color: "transparent" },
          ...waterfallElms,
          null,
          null,
        ],
      },
      {
        type: "columnrange",
        name: "Доп. потребность",
        zIndex: 1,
        color: "var(--xenon-color-fill-secondary)",
        data: [
          null,
          null,
          ...claimArr,
          null,
        ] as Highcharts.PointOptionsObject[],
      },
      {
        type: "column",
        name: "Остаток ресурса",
        stack: "Остаток ресурса",
        data: [
          null,
          null,
          null,
          null,
          null,
          { name: "Остаток ресурса", y: rl.leftovers },
        ] as Highcharts.PointOptionsObject[],
      },
    ],
  };
};
