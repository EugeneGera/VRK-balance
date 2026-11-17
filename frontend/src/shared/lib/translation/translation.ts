import { LangOptions } from "highcharts";

const months = [ 'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
  'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь' ];

const shortMonths = [ 'янв', 'фев', 'март', 'апр', 'май', 'июнь',
  'июль', 'авг', 'сен', 'окт', 'ноя', 'дек' ];

const weekdays = [ 'Воскресенье', 'Понедельник', 'Вторник', 'Среда', 'Четверг',
  'Пятница', 'Суббота' ];

const shortWeekdays = [ 'Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб' ];

const decimalPoint = '.';
const thousandsSep = ' ';

export const customHighchartsTranslation: LangOptions = {
  decimalPoint,
  thousandsSep,
  
  months,
  shortMonths,
  weekdays,
  shortWeekdays

};
