export const DIRS: Mapish = {
  tab_bazis_bk: "Базис отгрузки",
  tab_product_bk: "Продукт",
  tab_category_product_bk: "Категория продукта",
};

export const EDITS: Edits = {
  tab_bazis_bk: {
    adfi: "астраханский ГПЗ",
    sdfdj: "Оренбургский ГПЗ",
    sda: "Ленинградский завод презервативов",
    aseqr: "Рязанский стеклодувный завод",
  },
  tab_product_bk: {
    dfxcv: "Газпром добыча",
    dasc: "Дебилы",
    sdf: "Редкие дегеры",
    sdfzx: "Газпром инвест",
  },
  tab_category_product_bk: {
    dfdf: "Какая-то женщина",
    xcvf: "Прикольный опыт",
    cnb: "американские горки",
    cvbkl: "Сумасшедший енот",
  },
};

export type Mapish = { [k: string]: string };
export type Edits = { [k: string]: Mapish };
export type DirsKeys = keyof Mapish;
