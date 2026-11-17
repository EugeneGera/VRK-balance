const colors = [
  "#32B4FF",
  "#9CA3FF",
  "#0679BB",
  "#FFBD59",
  "#00724C",
  "#6AE0ED",
  "#417B7E",
  "#FF7479",
  "#12B47E",
];
export const createHighchartsOptions = (data): Highcharts.Options => {
  const allNodeNames = [...new Set(data.flatMap((d) => [d.source, d.target]))];

  const incoming = {};
  const outgoing = {};

  data.forEach((d) => {
    outgoing[d.source] = (outgoing[d.source] || 0) + 1;
    incoming[d.target] = (incoming[d.target] || 0) + 1;
  });

  const getNodePosition = (name) => {
    const hasOut = !!outgoing[name];
    const hasIn = !!incoming[name];

    if (hasOut && !hasIn) return "source";
    if (hasIn && !hasOut) return "sink";
    return "middle";
  };

  const nodes = allNodeNames.map((name, index) => {
    const position = getNodePosition(name);
    const dataLabels = {
      enabled: true,
      style: {
        textOverflow: "ellipsis",
        fontSize: "12px",
        fontWeight: "bold",
        color: "#fff",
      },
      y: -15,
    };

    if (position === "source") {
      dataLabels.align = "left";
      dataLabels.x = -10;
    } else if (position === "sink") {
      dataLabels.align = "right";
      dataLabels.x = 10;
    } else {
      dataLabels.align = "center";
      dataLabels.x = 0;
    }

    return {
      id: `node-${index}`,
      color: colors[index],
      name: name,
      dataLabels: dataLabels,
    };
  });

  const nodeMap = {};
  nodes.forEach((node) => {
    nodeMap[node.name] = node.id;
  });

  // Формируем связи
  const links = data.map((d) => ({
    from: nodeMap[d.source],
    to: nodeMap[d.target],
    weight: d.value,
  }));

  return {
    chart: {
      type: "sankey",
      backgroundColor: "transparent",
    },
    title: {
      style: {
        display: "none",
      },
    },
    tooltip: {
      headerFormat: "",
      pointFormat:
        "<b>{point.fromNode.name}</b> → <b>{point.toNode.name}</b><br/>Значение: <b>{point.weight}</b>",
    },
    plotOptions: {
      sankey: {
        borderColor: "#ccc",
        borderWidth: 1,
        colorByPoint: true,
        nodePadding: 20,
        nodeWidth: 30,
      },
    },
    series: [
      {
        data: links,
        nodes: nodes,
        type: "sankey",
        name: "Потоки",
        dataLabels: {
          enabled: true,
          style: {
            color: "#fff",
          },
          formatter: function (this) {
            return this.point.weight;
          },
        },
      },
    ],
  };
};
