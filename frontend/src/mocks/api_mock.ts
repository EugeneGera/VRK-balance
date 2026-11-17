export const mockTransport = {
  transport: {
    months: [
      {
        month: "Март",
        value: "190,6",
        detalization: {
          total: [
            {
              type: "ЖД",
              value: 165.8,
            },
            {
              type: "Авто",
              value: 24.8,
            },
          ],
          factories: [
            {
              factory_name: "Сургутский ЗСК",
              transports: [
                { type: "ЖД", value: 82.1, category: "Сургутский ЗСК" },
                { type: "Авто", value: 1.6, category: "Сургутский ЗСК" },
              ],
            },
            {
              factory_name: "Уренгойский ЗПКТ",
              transports: [
                { type: "ЖД", value: 0, category: "Уренгойский ЗПКТ" },
                { type: "Авто", value: 0.7, category: "Уренгойский ЗПКТ" },
              ],
            },
          ],
        },
      },
      {
        month: "Апрель",
        value: "168,3",
        detalization: {
          total: [
            {
              type: "ЖД",
              value: 165.8,
            },
            {
              type: "Авто",
              value: 24.8,
            },
          ],
          factories: [
            {
              factory_name: "Сургутский ЗСК",
              transports: [
                { type: "ЖД", value: 82.1, category: "Сургутский ЗСК" },
                { type: "Авто", value: 1.6, category: "Сургутский ЗСК" },
              ],
            },
            {
              factory_name: "Уренгойский ЗПКТ",
              transports: [
                { type: "ЖД", value: 0, category: "Уренгойский ЗПКТ" },
                { type: "Авто", value: 0.7, category: "Уренгойский ЗПКТ" },
              ],
            },
          ],
        },
      },
      {
        month: "Май",
        value: "175,5",
        detalization: {
          total: [
            {
              type: "ЖД",
              value: 165.8,
            },
            {
              type: "Авто",
              value: 24.8,
            },
          ],
          factories: [
            {
              factory_name: "Сургутский ЗСК",
              transports: [
                { type: "ЖД", value: 82.1, category: "Сургутский ЗСК" },
                { type: "Авто", value: 1.6, category: "Сургутский ЗСК" },
              ],
            },
            {
              factory_name: "Уренгойский ЗПКТ",
              transports: [
                { type: "ЖД", value: 0, category: "Уренгойский ЗПКТ" },
                { type: "Авто", value: 0.7, category: "Уренгойский ЗПКТ" },
              ],
            },
          ],
        },
      },
    ],
  },
};

export const mockSankeyData: {
  source: string;
  target?: string;
  value: number;
  kind: string;
  price?: string;
  volume_left?: number;
  unit?: string;
}[] = [
  {
    source: "Нераспределённый ресурс",
    target: "не используется",
    value: 250,
    kind: "Заводы",
  },
  {
    source: "Сургутский ЗСК",
    target: "Нужды ДО",
    kind: "Заводы",
    value: Math.floor(Math.random() * (250 - 15 + 1)) + 15,
    price: "11 532,9 руб/т.",
    volume_left: 0.7,
    unit: "т",
  },
  {
    source: "Сургутский ЗСК",
    target: "Гособязательства",
    kind: "Заводы",
    value: Math.floor(Math.random() * (250 - 15 + 1)) + 15,
    price: "18 333,3 руб/т.",
  },
  {
    source: "Сургутский ЗСК",
    target: "Мелкий опт",
    kind: "Заводы",
    value: Math.floor(Math.random() * (250 - 15 + 1)) + 15,
    price: "18 333,3 руб/т.",
  },
  {
    source: "Сургутский ЗСК",
    target: "Розница",
    kind: "Заводы",
    value: Math.floor(Math.random() * (250 - 15 + 1)) + 15,
    price: "Вн. рынок: 11 532,9 руб/т.",
  },
  {
    source: "Сургутский ЗСК",
    target: "Контрактные объемы",
    kind: "Заводы",
    value: Math.floor(Math.random() * (250 - 15 + 1)) + 15,
    price: "Экспорт:17 797,7 руб/т.",
  },
  {
    source: "Сургутский ЗСК",
    target: "Прочая реализация",
    kind: "Заводы",
    value: Math.floor(Math.random() * (250 - 15 + 1)) + 15,
    price: "16 362,9 руб/т.",
  },
  {
    source: "Уренгойский ЗПКТ",
    target: "Нужды ДО",
    kind: "Заводы",
    value: Math.floor(Math.random() * (250 - 15 + 1)) + 15,
    price: "16 362,9 руб/т.",
  },
  {
    source: "Уренгойский ЗПКТ",
    target: "Гособязательства",
    kind: "Заводы",
    value: Math.floor(Math.random() * (250 - 15 + 1)) + 15,
    price: "14 162,9 руб/т.",
  },
  {
    source: "Уренгойский ЗПКТ",
    target: "Мелкий опт",
    kind: "Заводы",
    value: Math.floor(Math.random() * (250 - 15 + 1)) + 15,
    price: "14 162,9 руб/т.",
  },
  {
    source: "Уренгойский ЗПКТ",
    target: "Розница",
    kind: "Заводы",
    value: Math.floor(Math.random() * (250 - 15 + 1)) + 15,
    price: "14 162,9 руб/т.",
  },
  {
    source: "Уренгойский ЗПКТ",
    target: "Контрактные объемы",
    kind: "Заводы",
    value: Math.floor(Math.random() * (250 - 15 + 1)) + 15,
    price: "14 162,9 руб/т.",
  },
  {
    source: "Уренгойский ЗПКТ",
    target: "Прочая реализация",
    kind: "Заводы",
    value: Math.floor(Math.random() * (250 - 15 + 1)) + 15,
    price: "14 162,9 руб/т.",
  },
  {
    source: "Нужды ДО",
    target: "Внутренний рынок",
    kind: "Каналы сбыта",
    value: Math.floor(Math.random() * (250 - 15 + 1)) + 15,
  },
  {
    source: "Гособязательства",
    target: "Внутренний рынок",
    kind: "Каналы сбыта",
    value: Math.floor(Math.random() * (250 - 15 + 1)) + 15,
  },
  {
    source: "Мелкий опт",
    target: "Внутренний рынок",
    kind: "Каналы сбыта",
    value: Math.floor(Math.random() * (250 - 15 + 1)) + 15,
  },
  {
    source: "Розница",
    target: "Внутренний рынок",
    kind: "Каналы сбыта",
    value: Math.floor(Math.random() * (250 - 15 + 1)) + 15,
  },
  {
    source: "Контрактные объемы",
    target: "Внутренний рынок",
    kind: "Контрактные объемы",
    value: Math.floor(Math.random() * (250 - 15 + 1)) + 15,
  },
  {
    source: "Прочая реализация",
    target: "Внутренний рынок",
    kind: "Прочая реализация",
    value: Math.floor(Math.random() * (250 - 15 + 1)) + 15,
  },
  {
    source: "Нужды ДО",
    target: "Экспорт",
    kind: "Каналы сбыта",
    value: Math.floor(Math.random() * (250 - 15 + 1)) + 15,
  },
  {
    source: "Гособязательства",
    target: "Экспорт",
    kind: "Каналы сбыта",
    value: Math.floor(Math.random() * (250 - 15 + 1)) + 15,
  },
  {
    source: "Мелкий опт",
    target: "Экспорт",
    kind: "Каналы сбыта",
    value: Math.floor(Math.random() * (250 - 15 + 1)) + 15,
  },
  {
    source: "Розница",
    target: "Экспорт",
    kind: "Каналы сбыта",
    value: Math.floor(Math.random() * (250 - 15 + 1)) + 15,
  },
  {
    source: "Контрактные объемы",
    target: "Экспорт",
    kind: "Каналы сбыта",
    value: Math.floor(Math.random() * (250 - 15 + 1)) + 15,
  },
  {
    source: "Прочая реализация",
    target: "Экспорт",
    kind: "Каналы сбыта",
    value: Math.floor(Math.random() * (250 - 15 + 1)) + 15,
  },
];

export const sankeyDataProducts: {
  source: string;
  target?: string;
  value: number;
  kind: string;
  price?: string;
  volume_left?: number;
  unit?: string;
}[] = [
  {
    source: "ТС-1",
    target: "Нужды ДО",
    kind: "Продукты",
    value: Math.floor(Math.random() * (250 - 15 + 1)) + 15,
    price: "11 532,9 руб/т.",
    volume_left: 0.7,
    unit: "т",
  },
  {
    source: "ТС-1",
    target: "Гособязательства",
    kind: "Продукты",
    value: Math.floor(Math.random() * (250 - 15 + 1)) + 15,
    price: "18 333,3 руб/т.",
  },
  {
    source: "ТС-1",
    target: "Мелкий опт",
    kind: "Продукты",
    value: Math.floor(Math.random() * (250 - 15 + 1)) + 15,
    price: "18 333,3 руб/т.",
  },
  {
    source: "ТС-1",
    target: "Розница",
    kind: "Продукты",
    value: Math.floor(Math.random() * (250 - 15 + 1)) + 15,
    price: "Вн. рынок: 11 532,9 руб/т.",
  },
  {
    source: "ТС-1",
    target: "Контрактные объемы",
    kind: "Продукты",
    value: Math.floor(Math.random() * (250 - 15 + 1)) + 15,
    price: "Экспорт:17 797,7 руб/т.",
  },
  {
    source: "ТС-1",
    target: "Прочая реализация",
    kind: "Продукты",
    value: Math.floor(Math.random() * (250 - 15 + 1)) + 15,
    price: "16 362,9 руб/т.",
  },
  {
    source: "ДГКЛ",
    target: "Нужды ДО",
    kind: "Продукты",
    value: Math.floor(Math.random() * (250 - 15 + 1)) + 15,
    price: "16 362,9 руб/т.",
  },
  {
    source: "ДГКЛ",
    target: "Гособязательства",
    kind: "Продукты",
    value: Math.floor(Math.random() * (250 - 15 + 1)) + 15,
    price: "14 162,9 руб/т.",
  },
  {
    source: "ДГКЛ",
    target: "Мелкий опт",
    kind: "Продукты",
    value: Math.floor(Math.random() * (250 - 15 + 1)) + 15,
    price: "14 162,9 руб/т.",
  },
  {
    source: "ДГКЛ",
    target: "Розница",
    kind: "Продукты",
    value: Math.floor(Math.random() * (250 - 15 + 1)) + 15,
    price: "14 162,9 руб/т.",
  },
  {
    source: "ДГКЛ",
    target: "Контрактные объемы",
    kind: "Продукты",
    value: Math.floor(Math.random() * (250 - 15 + 1)) + 15,
    price: "14 162,9 руб/т.",
  },
  {
    source: "ДГКЛ",
    target: "Прочая реализация",
    kind: "Продукты",
    value: Math.floor(Math.random() * (250 - 15 + 1)) + 15,
    price: "14 162,9 руб/т.",
  },
  {
    source: "Нужды ДО",
    target: "Внутренний рынок",
    kind: "Каналы сбыта",
    value: Math.floor(Math.random() * (250 - 15 + 1)) + 15,
  },
  {
    source: "Гособязательства",
    target: "Внутренний рынок",
    kind: "Каналы сбыта",
    value: Math.floor(Math.random() * (250 - 15 + 1)) + 15,
  },
  {
    source: "Мелкий опт",
    target: "Внутренний рынок",
    kind: "Каналы сбыта",
    value: Math.floor(Math.random() * (250 - 15 + 1)) + 15,
  },
  {
    source: "Розница",
    target: "Внутренний рынок",
    kind: "Каналы сбыта",
    value: Math.floor(Math.random() * (250 - 15 + 1)) + 15,
  },
  {
    source: "Контрактные объемы",
    target: "Внутренний рынок",
    kind: "Контрактные объемы",
    value: Math.floor(Math.random() * (250 - 15 + 1)) + 15,
  },
  {
    source: "Прочая реализация",
    target: "Внутренний рынок",
    kind: "Прочая реализация",
    value: Math.floor(Math.random() * (250 - 15 + 1)) + 15,
  },
  {
    source: "Нужды ДО",
    target: "Экспорт",
    kind: "Каналы сбыта",
    value: Math.floor(Math.random() * (250 - 15 + 1)) + 15,
  },
  {
    source: "Гособязательства",
    target: "Экспорт",
    kind: "Каналы сбыта",
    value: Math.floor(Math.random() * (250 - 15 + 1)) + 15,
  },
  {
    source: "Мелкий опт",
    target: "Экспорт",
    kind: "Каналы сбыта",
    value: Math.floor(Math.random() * (250 - 15 + 1)) + 15,
  },
  {
    source: "Розница",
    target: "Экспорт",
    kind: "Каналы сбыта",
    value: Math.floor(Math.random() * (250 - 15 + 1)) + 15,
  },
  {
    source: "Контрактные объемы",
    target: "Экспорт",
    kind: "Каналы сбыта",
    value: Math.floor(Math.random() * (250 - 15 + 1)) + 15,
  },
  {
    source: "Прочая реализация",
    target: "Экспорт",
    kind: "Каналы сбыта",
    value: Math.floor(Math.random() * (250 - 15 + 1)) + 15,
  },
];

export const mockOptions: { value: string; label: string }[] = [
  {
    value: "Бензин АИ-92",
    label: "Бензин АИ-92",
  },
  {
    value: "Бензин АИ-95",
    label: "Бензин АИ-95",
  },
  { value: "ТС-1", label: "ТС-1" },
  { value: "ДТ", label: "ДТ" },
  { value: "ДГКЛ", label: "ДГКЛ" },
  { value: "Мазут", label: "Мазут" },
  { value: "КГС / нефть", label: "КГС / нефть" },
  { value: "ШФЛУ", label: "ШФЛУ" },
  { value: "СУГ (кроме бутана)", label: "СУГ (кроме бутана)" },
  { value: "СУГ бутан", label: "СУГ бутан" },
  { value: "Метанол", label: "Метанол" },
  { value: "Сера жидкая", label: "Сера жидкая" },
  { value: "Сера гранулированная", label: "Сера гранулированная" },
];

export const mockMonths: { value: string; label: string }[] = [
  { value: "Январь", label: "Январь" },
  { value: "Февраль", label: "Февраль" },
  { value: "Март", label: "Март" },
  { value: "Апрель", label: "Апрель" },
  { value: "Май", label: "Май" },
  { value: "Июнь", label: "Июнь" },
  { value: "Июль", label: "Июль" },
  { value: "Август", label: "Август" },
  { value: "Сентябрь", label: "Сентябрь" },
  { value: "Октябрь", label: "Октябрь" },
  { value: "Ноябрь", label: "Ноябрь" },
  { value: "Декабрь", label: "Декабрь" },
];

export const mockPieData: {
  pieLeftPlanData: { type: string; value: number }[];
  pieProgressApplication: { percent: number; value: number; type: string };
  pieResourceRestriction: { type: string; value: number }[];
  pieProgressDelta: { type: string; value: number; percent: number };
} = {
  pieLeftPlanData: [
    {
      type: "Остатки",
      value: 6.1,
    },
    { type: "План производства", value: 184.5 },
  ],
  pieResourceRestriction: [
    { type: "Ресурс к распределению", value: 174.5 },
    {
      type: "Ограничения",
      value: 21.4,
    },
  ],
  pieProgressApplication: { percent: 0.9, value: 19.5, type: "Заявки" },
  pieProgressDelta: { type: "Дельта", value: 214.5, percent: 0.3 },
};

export const mockFacoryLeftOverData: {
  factory_name: string;
  leftovers: { type: string; value: number; category: string }[];
}[] = [
  {
    factory_name: "Сургутский ЗСК",
    leftovers: [
      { type: "Остатки", value: 10.6, category: "план" },
      { type: "План производства", value: 72.1, category: "план" },
      { type: "Ресурс к распределению", value: 64.4, category: "ресурс" },
      { type: "Ограничения", value: -9.5, category: "ресурс" },
      { type: "Заявки", value: 64.4, category: "заявки" },
      { type: "Дельта", value: 14.3, category: "заявки" },
    ],
  },
  {
    factory_name: "Оренбургский ГПЗ",
    leftovers: [
      { type: "Остатки", value: 10.6, category: "план" },
      { type: "План производства", value: 82.1, category: "план" },
      { type: "Ресурс к распределению", value: 30.6, category: "ресурс" },
      { type: "Ограничения", value: -9.5, category: "ресурс" },
      { type: "Заявки", value: 10.6, category: "заявки" },
      { type: "Дельта", value: 20, category: "заявки" },
    ],
  },
];

export const mainTableData = [
  [
    "Сургутский ЗСК",
    0.1,
    0.6,
    0.7,
    0.7,
    0.7,
    0.7,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    0.6,
    null,
    null,
    null,
    null,
    null,
    0.3,
  ],
  [
    "Уренгойский ЗПКТ",
    0.1,
    0.6,
    0.7,
    0.7,
    0.7,
    0.7,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    0.6,
    null,
    null,
    null,
    null,
    null,
    0.3,
  ],
  [
    "Газпром метанол",
    0.1,
    0.6,
    0.7,
    0.7,
    0.7,
    0.7,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    0.6,
    null,
    null,
    null,
    null,
    null,
    0.3,
  ],
  [
    "Итого март",
    0.1,
    0.6,
    0.7,
    0.7,
    0.7,
    0.7,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    0.6,
    null,
    null,
    null,
    null,
    null,
    0.3,
  ],
  [
    "Итого май",
    0.1,
    0.6,
    0.7,
    0.7,
    0.7,
    0.7,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    0.6,
    null,
    null,
    null,
    null,
    null,
    0.3,
  ],
];

export const waterfallMock = {
  data: {
    total: {
      plan: 100,
      leftovers: 10,
    },
    available_resource: {
      available: 70,
      restriction: 40,
    },
    distribution: [
      {
        name: "Внутренний рынок",
        value: -20,
        claim: 10,
      },
      {
        name: "Экспорт",
        value: -11,
      },
      {
        name: "Нужды ДО",
        value: -14,
        claim: 5,
      },
    ],
    resource_leftover: {
      leftover: -25,
    },
    need: {
      need: 15,
    },
  },
};

export const detalizationWaterfallDemoMock = [
  {
    name: "Сургутский ЗСК",
    data: {
      total: {
        plan: 100,
        leftovers: 10,
      },
      available_resource: {
        available: 70,
        restriction: 40,
      },
      distribution: [
        {
          name: "Внутренний рынок",
          value: -0,
          claim: 10,
        },
        {
          name: "Экспорт",
          value: -11,
        },
        {
          name: "Нужды ДО",
          value: -24,
          claim: 5,
        },
      ],
      resource_leftover: {
        leftover: 25,
      },
      need: {
        need: 15,
      },
    },
  },
  {
    name: "Уренгойский ЗПКТ",
    data: {
      total: {
        plan: 100,
        leftovers: 10,
      },
      available_resource: {
        available: 70,
        restriction: 40,
      },
      distribution: [
        {
          name: "Внутренний рынок",
          value: -20,
          claim: 10,
        },
        {
          name: "Экспорт",
          value: -11,
        },
        {
          name: "Нужды ДО",
          value: -24,
          claim: 5,
        },
      ],
      resource_leftover: {
        leftover: -25,
      },
      need: {
        need: 15,
      },
    },
  },
  {
    name: "Астраханский ГПЗ",
    data: {
      total: {
        plan: 100,
        leftovers: 10,
      },
      available_resource: {
        available: 70,
        restriction: 40,
      },
      distribution: [
        {
          name: "Внутренний рынок",
          value: -20,
          claim: 10,
        },
        {
          name: "Экспорт",
          value: -11,
        },
        {
          name: "Нужды ДО",
          value: -24,
          claim: 5,
        },
      ],
      resource_leftover: {
        leftover: -25,
      },
      need: {
        need: 15,
      },
    },
  },
];

export const stockMockData = {
  absolute: [
    {
      month: "Март",
      data: [
        {
          type: "Реализация на бирже",
          value: 10,
          category: "Реализация",
        },
        {
          type: "Биржа обязательства",
          value: 5,
          category: "Реализация на бирже",
        },
        {
          type: "Биржа доп. объёмы",
          value: 5,
          category: "Реализация на бирже",
        },
        {
          type: "Внебиржевая реализация",
          value: 15,
          category: "Реализация",
        },
      ],
    },
  ],
  percent: [
    {
      month: "Март",
      data: [
        {
          type: "Реализация на бирже",
          value: 10,
          category: "Реализация",
        },
        {
          type: "Биржа обязательства",
          value: 5,
          category: "Реализация на бирже",
        },
        {
          type: "Биржа доп. объёмы",
          value: 5,
          category: "Реализация на бирже",
        },
        {
          type: "Внебиржевая реализация",
          value: 15,
          category: "Реализация",
        },
      ],
    },
  ],
};
