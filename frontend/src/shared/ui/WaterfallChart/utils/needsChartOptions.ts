import { DistributionItem, WaterfallData } from "./types";

function drawCustomXAxis(this: Highcharts.Chart) {
  if (this.customZeroLine) {
    this.customZeroLine.destroy();
    this.customZeroLine = undefined;
  }
  if (this.customZeroLabel) {
    this.customZeroLabel.destroy();
    this.customZeroLabel = undefined;
  }

  const xAxis = this.xAxis[0];
  const yAxis = this.yAxis[0];

  if (!xAxis || !yAxis) return;

  const yZero = yAxis.toPixels(0);
  const xStart = xAxis.left;
  const xEnd = xStart + xAxis.width;

  // Рисуем линию
  this.customZeroLine = this.renderer
    .path(["M", xStart + 15, yZero, "L", xEnd, yZero])
    .attr({
      "stroke-width": 1,
      stroke: "#cccccc",
      zIndex: 5,
    })
    .add();

  // Рисуем 0
  this.customZeroLabel = this.renderer
    .text("0", xStart, yZero + 4)
    .css({
      color: "var(--xenon-color-text-description)",
      fontSize: "12px",
      fontWeight: "bold",
      fill: "var(--xenon-color-text-description)",
    })
    .add();
}

function drawHighlightRectangles(
  this: Highcharts.Chart,
  waterfallElmsData: DistributionItem[]
) {
  if (this.customHighlights) {
    this.customHighlights.forEach((el) => el.destroy());
    this.customHighlights = [];
  } else {
    this.customHighlights = [];
  }

  const filterData = waterfallElmsData.filter((data) => data.claim);

  const waterfallSeries = this.series.find((s) => s.type === "waterfall");
  const needsSeries = this.series.find((s) => s.name === "Доп. потребность");
  let needsHeight: number | undefined;
  let needsValue: number | undefined;
  if (needsSeries) {
    needsSeries.points.forEach((targetPoint) => {
      if (!targetPoint.name || !targetPoint.shapeArgs) return;
      if (targetPoint.name === "Доп. потребность") {
        const { height } = targetPoint.shapeArgs;
        needsHeight = height;
        needsValue = targetPoint.total;
      }
    });
  }
  if (!waterfallSeries) return;

  waterfallSeries.points.forEach((targetPoint) => {
    if (!targetPoint.name || !targetPoint.shapeArgs) return;

    if (filterData.some((data) => data.name === targetPoint.name)) {
      const data = filterData.find((data) => data.name === targetPoint.name);
      const { x, y, width, height } = targetPoint.shapeArgs;

      const highlightRect = this.renderer
        .rect(
          x + 10,
          y + 10 - (data?.claim * needsHeight) / needsValue,
          width,
          (data?.claim * needsHeight) / needsValue,
          2
        )
        .attr({
          fill: "#AAAFBB",
          "stroke-width": 1,
        })
        .add();

      const labelText = this.renderer
        .text(
          String(data?.claim),
          x + 50 - String(data?.claim).length * 2,
          y + 3
        )
        .css({
          fontSize: "12px",
          fontWeight: "bold",
          fill: "#fff",
          zIndex: 2,
          // stroke: "#000",
          // strokeWidth: 0.5,
          textStroke: "1px 1px 1px #000",
        })
        .add();
      this.customHighlights.push(highlightRect, labelText);
    }
  });
}

function drawTotalValue(this: Highcharts.Chart, data: WaterfallData) {
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
      margin = 5;
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
      const point = waterfallSeries?.points?.[categoryIndex];

      if (point?.shapeArgs) {
        x = point.shapeArgs.x;
        width = point.shapeArgs.width;
        plotY = point.box.y;
      }

      margin = item.claim ? 20 : 5;
    }

    if (
      totalValue === null ||
      x === undefined ||
      width === undefined ||
      plotY === undefined
    )
      continue;

    const centerX = x + width / 2;
    const textY = plotY - margin;

    const totalLabel = this.renderer
      .text(String(totalValue), centerX + 8, textY + (totalValue >= 0 ? 4 : 0))
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

export const needsWaterfallOptions = (
  data: WaterfallData
): Highcharts.Options => {
  if (!data) return {};
  const waterfallFieldsName = data.data.distribution.map((item) => item.name);
  const claimArr = [];

  data.data.distribution.forEach((item) => {
    if (item.claim) {
      claimArr.push(item);
    }
  });

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
    legend: {
      enabled: false,
    },
    title: {
      style: {
        display: "none",
      },
    },
    xAxis: {
      type: "category",
      categories: ["Остаток ресурса", "Доп. потребность"],
      lineWidth: 0,
      tickLength: 0,
      gridLineWidth: 0,
      labels: {
        style: { color: "var(--xenon-color-text-base)" },
      },
    },
    yAxis: {
      visible: false,
      gridLineWidth: 0,
    },
    tooltip: {
      shared: true,
      formatter: function () {
        return (
          `<b>${this.category}</b><br/>` +
          this.points
            ?.map((p) => `${p.series.name}: ${Math.abs(p.y)}`)
            .join("<br/>")
        );
      },
    },
    plotOptions: {
      column: {
        stacking: "normal",
        grouping: false,
        borderRadius: 2,
        pointWidth: 60,
        pointPadding: 0.1,
        groupPadding: 0.2,
        borderWidth: 0,
        pointRange: 1,
        negativeColor: "#FFC5C7",
        dataLabels: {
          enabled: true,
          crop: false,
          inside: true,
          formatter: function () {
            let color = "";
            if (this.y !== 0) {
              if (this.y > 0) {
                color = "#fff";
              } else {
                color = "#ff6368ff";
              }
              return (
                '<div style="margin-top: -15.5px; text-align:center"><span style="font-size:12px;color:' +
                color +
                '">' +
                this.y +
                "</span><br/>" +
                "</div>"
              );
            }
          },
          style: {
            fontWeight: "bold",
            fontSize: "12px",
            color: "#fff",
          },
        },
      },
    },
    series: [
      {
        type: "column",
        name: "Остаток",
        stack: "Остаток ресурса",
        data: [
          {
            name: "Остаток ресурса",
            y: data.data.resource_leftover.leftovers,
            color:
              data.data.resource_leftover.leftovers > 0 ? "#6B8ABC" : "#FFC5C7",
          },
        ] as Highcharts.PointOptionsObject[],
      },
      {
        type: "column",
        name: "Доп. потребность",
        stack: "Доп. потребность",
        data: [
          null,
          { name: "Доп. потребность", y: data.data.need.need },
        ] as Highcharts.PointOptionsObject[],
        color: "#AAAFBB",
      },
    ],
  };
};
