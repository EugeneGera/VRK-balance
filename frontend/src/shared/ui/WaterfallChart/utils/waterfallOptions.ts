import { WaterfallData } from "./types";

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
    .text("0", xStart, yZero + 4)
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
    categoryIndex <= totalCategories - 2;
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
      margin = 0;
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
      margin = 0;
    } else {
      const distIndex = categoryIndex - 2;
      const item = data.data.distribution[distIndex];

      if (!item) continue;

      totalValue = +(Math.abs(item.value) + (item.claim ?? 0)).toFixed(2);

      const waterfallSeries = seriesList.find((s) => s.type === "waterfall");
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
      margin = item.claim ? claimHeight + (claimHeight > 3 ? 0 : 8) : 0;
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
      .text(String(totalValue === 0 ? totalValue : totalValue.toFixed(2)), centerX + 8, textY + (totalValue >= 0 ? 4 : 0))
      .attr({
        align: "center",
      })
      .css({
        color: "var(--xenon-color-text-base)",
        fontSize: "14px",
        fontWeight: "bold",
        fill: "var(--xenon-color-text-base)",
      })
      .add();

    this.customTotalValues.push(totalLabel);
  }
}

export const waterfallOptions = (data: WaterfallData): Highcharts.Options => {
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
      labels: { style: { color: "var(--xenon-color-text-base)" } },
    },
    yAxis: { visible: false, gridLineWidth: 0 },
    tooltip: {
      shared: true,
      formatter: function () {
        return (
          `<b>${this.category}</b><br/>` +
          (this.points
            ?.map(
              (p) =>
                `${p.series.name}: ${p.color === "var(--xenon-color-fill-secondary)" ? Math.abs((p.high ?? 0) - (p?.low ?? 0)).toFixed(2) : Math.abs(p.y ?? 0)}`
            )
            .join("<br/>") ?? "")
        );
      },
    },
    plotOptions: {
      waterfall: {
        pointWidth: 120,
        pointPadding: 0.1,
        groupPadding: 0.2,
        borderRadius: 2,
        borderWidth: 0,
        pointRange: 1,
        color: "#12B47E",
        pointPlacement: "on",
        lineColor: "var(--xenon-color-text)",
        dataLabels: {
          enabled: true,
          crop: false,
          inside: true,
          formatter: function (this: unknown) {
            const self = this as Highcharts.Point & {
              point: { y: number };
            };
            return self.point.y !== 0
              ? Math.abs(self.point.y as number)
              : undefined;
          },
          style: {
            fontWeight: "400",
            fontSize: "12px",
            color: "#fff",
          },
        },
      },
      columnrange: {
        pointWidth: 120,
        borderWidth: 0,
        borderRadius: 2,
        dataLabels: {
          enabled: true,
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
            const gap = self.shapeArgs?.height < 3 ? -7 : 0;

            return `<div style="transform: translateY(${gap}px); color: var(--xenon-color-text-disabled); z-index: -1; font-size: 12px;">${center.toFixed(2)}</div>`;
          },

          verticalAlign: "middle",
          style: {
            fontWeight: "400",
            fontSize: "12px",
            marginBotton: "20px",
          },
        },
      },
      column: {
        stacking: "normal",
        grouping: false,
        borderRadius: 2,
        pointWidth: 120,
        pointPadding: 0.1,
        groupPadding: 0.2,
        borderWidth: 0,
        pointRange: 1,
        negativeColor: "#FFC5C7",
        dataLabels: {
          enabled: true,
          crop: false,
          inside: true,
          formatter: function (this: unknown) {
            const self = this as Highcharts.Point & {
              y: number;
            };
            let color = "";
            if (self.y !== 0) {
              if (self.y > 0) {
                color = "#fff";
              } else {
                color = "#ff6368ff";
              }
              return (
                '<div style="margin-top: -15.5px; text-align:center"><span style="font-size:12px;color:' +
                color +
                '">' +
                self.y +
                "</span><br/>" +
                "</div>"
              );
            }
          },
          style: { fontWeight: "400", fontSize: "12px", color: "#fff" },
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
        data: [null, null, ...claimArr, null] as Highcharts.PointOptionsObject[],
      },
      {
        type: "column",
        name: "Остаток",
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
