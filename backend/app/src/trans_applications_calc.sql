-- 01. Загрузка в таблицу TAB_SH_ZAYAV_REAL_BK zip-архива или отдельноо файла excel
-- 02. Очистка даты загрузки Заявки на реализацию в историю

delete from tab_upload_history_zayav_real_bk;

-- 03. Добавить дату загрузки Заявки на реализацию в историю
insert into tab_upload_history_zayav_real_bk
(select 
				(:year)::int as year, 
				case when t.month = 'январь' or t.month = 'Январь' then 1
				   when t.month = 'февраль' or t.month = 'Февраль' then 2
				   when t.month = 'март' or t.month = 'Март'  then 3
				   when t.month = 'апрель' or t.month = 'Апрель'  then 4
				   when t.month = 'май' or t.month = 'Май'  then 5
				   when t.month = 'июнь' or t.month = 'Июнь'  then 6
				   when t.month = 'июль' or t.month = 'Июль'  then 7
				   when t.month = 'август' or t.month = 'Август' then 8
				   when t.month = 'сентябрь' or t.month = 'Сентябрь'  then 9
				   when t.month = 'октябрь' or t.month = 'Октябрь'  then 10
				   when t.month = 'ноябрь' or t.month = 'Ноябрь'  then 11
				   when t.month = 'декабрь' or t.month = 'Декабрь'  then 12
		end as month,
		t.tab_product_bk_ids as product,
		pr.id as tab_product_bk_ids
		
	from tab_sh_zayav_real_bk as t
	inner join tab_product_bk as pr on t.tab_product_bk_ids = pr.name
	where concat(month, '.', :year) not in (select concat(month, '.', year) from tab_upload_history_zayav_real_bk group by month, year) and
					month is not null and
					tab_bazis_bk_ids is not null
	group by month, year, t.tab_product_bk_ids, pr.id
);
-- 04. Добавление новых записей в справочник Владелец
insert into tab_owner_bk
(select row_number() over (order by t.tab_owner_bk_ids) + (select id as id from tab_owner_bk order by id desc limit 1)  as id,
			t.tab_owner_bk_ids as name,
			0 as tab_org_bk_ids
				
	from tab_sh_zayav_real_bk as t
	where not exists (select name from tab_owner_bk where name = t.tab_owner_bk_ids) and t.tab_bazis_bk_ids is not null and t.tab_bazis_bk_ids <> '0' and t.tab_bazis_bk_ids <> ''
	group by t.tab_owner_bk_ids
	order by t.tab_owner_bk_ids);

-- 05. Добавление новых записей в справочник Продукт
/*Добавление в справочник Категория продукта*/
insert into tab_category_product_bk
(select  	row_number() over (order by t.tab_category_product_bk_ids) + (select ID as id from tab_product_bk order by id desc limit 1)  as id,
			t.tab_category_product_bk_ids as name		
	from tab_sh_zayav_real_bk as t
	where not exists (select name from tab_category_product_bk where name = t.tab_category_product_bk_ids) and 
					t.tab_bazis_bk_ids is not null and 
					t.tab_bazis_bk_ids <> '0' and 
					t.tab_bazis_bk_ids <> '' and
					t.tab_category_product_bk_ids is not null and
					t.tab_category_product_bk_ids <> ''
	group by t.tab_category_product_bk_ids
	order by t.tab_category_product_bk_ids);
	
/*Добавление в справочник Продукт*/
insert into tab_product_bk
(select  	row_number() over (order by t.tab_product_bk_ids) + (select ID as id from tab_product_bk order by id desc limit 1)  as id,
			t.tab_product_bk_ids as name,
			cp.id as tab_category_product_bk_ids,
			ei.id as tab_ei_bk_ids
				
	from tab_sh_zayav_real_bk as t
	inner join tab_category_product_bk as cp on cp.name = t.tab_category_product_bk_ids
	inner join tab_ei_bk as ei on ei.name = t.tab_ei_bk_ids
	where not exists (select name from tab_product_bk where name = t.tab_product_bk_ids) and t.tab_bazis_bk_ids is not null and t.tab_bazis_bk_ids <> '0' and t.tab_bazis_bk_ids <> ''
	group by t.tab_product_bk_ids, cp.id, ei.id
	order by t.tab_product_bk_ids);

-- 06. Добавление новых записей в справочник Агент/Производитель
insert into tab_proizv_bk
(select  row_number() over (order by t.tab_proizv_bk_ids) + (select id as id from tab_proizv_bk order by id desc limit 1)  as id,
			t.tab_proizv_bk_ids as name		
	from tab_sh_zayav_real_bk as t
	where not exists (select name from tab_proizv_bk where name = t.tab_proizv_bk_ids) and t.tab_bazis_bk_ids is not null and t.tab_bazis_bk_ids <> '0' and t.tab_bazis_bk_ids <> ''
	group by t.tab_proizv_bk_ids
	order by t.tab_proizv_bk_ids);

-- 07. Добавление новых записей в справочник Собственник продукта
insert into tab_sobstv_bk
(select row_number() over (order by t.tab_sobstv_bk_ids) + (select id as id from tab_sobstv_bk order by id desc limit 1)  as id,
			t.tab_sobstv_bk_ids as name		
	from tab_sh_zayav_real_bk as t
	where not exists (select name from tab_sobstv_bk where name = t.tab_sobstv_bk_ids) and t.tab_bazis_bk_ids is not null and t.tab_bazis_bk_ids <> '0' and t.tab_bazis_bk_ids <> ''
	group by t.tab_sobstv_bk_ids
	order by t.tab_sobstv_bk_ids);

-- 08. Добавление новых записей в справочник Станция (пункт назначения)
insert into tab_point_to_bk
(select  	row_number() over (order by t.tab_point_to_bk_ids) + (select id as id from tab_point_to_bk order by id desc limit 1)  as id,
			t.tab_point_to_bk_ids as name		
	from tab_sh_zayav_real_bk as t
	where not exists (select name from tab_point_to_bk where name = t.tab_point_to_bk_ids) and t.tab_bazis_bk_ids IS not null and t.tab_bazis_bk_ids <> '0' and t.tab_bazis_bk_ids <> ''
	group by t.tab_point_to_bk_ids
	order by t.tab_point_to_bk_ids);

-- 09. Добавление новых записей в справочник Покупатель
insert into tab_pokup_bk
(select  	row_number() over (order by t.tab_pokup_bk_ids) + (select id as id from tab_pokup_bk order by id desc limit 1)  as id,
			t.tab_pokup_bk_ids as name		
	from tab_sh_zayav_real_bk as t
	where not exists (select name from tab_pokup_bk where name = t.tab_pokup_bk_ids) and t.tab_bazis_bk_ids IS not null and t.tab_bazis_bk_ids <> '0' and t.tab_bazis_bk_ids <> ''
	group by t.tab_pokup_bk_ids
	order by t.tab_pokup_bk_ids);

-- 10. Добавление новых записей в справочник Базис отгрузки
insert into tab_bazis_bk
(select  	row_number() over (order by t.tab_bazis_bk_ids) + (select id as id from tab_bazis_bk order by id desc limit 1)  as id,
			t.tab_bazis_bk_ids as name,
			pr.id	
	from tab_sh_zayav_real_bk as t
	inner join tab_proizv_bk as pr on pr.name = t.tab_proizv_bk_ids
	where not exists (select name from tab_bazis_bk where name = t.tab_bazis_bk_ids) and t.tab_bazis_bk_ids IS not null and t.tab_bazis_bk_ids <> '0' and t.tab_bazis_bk_ids <> ''
	group by t.tab_bazis_bk_ids, pr.id
	order by t.tab_bazis_bk_ids);

-- 11. Очистка dataset Заявки на реализацию 
delete from tab_zayav_real_bk as d 
using tab_upload_history_zayav_real_bk as history
WHERE d.month = history.month AND d.year = history.year and d.tab_product_bk_ids = history.tab_product_bk_ids;

-- 12. Загрузка dataset Заявки на реализацию
insert into tab_zayav_real_bk as z
( select
		coalesce ((select max(id) from  tab_zayav_real_bk),0) + row_number() over (order by t.id) as id,
		own.id as tab_owner_bk_ids,
		(:year)::int as year,
		case when t.month = 'январь' or t.month = 'Январь' or t.month = 'ЯНВАРЬ' then 1
				   when t.month = 'февраль' or t.month = 'Февраль' or t.month = 'ФЕВРАЛЬ' then 2
				   when t.month = 'март' or t.month = 'Март' or t.month = 'МАРТ' then 3
				   when t.month = 'апрель' or t.month = 'Апрель' or t.month = 'АПРЕЛЬ' then 4
				   when t.month = 'май' or t.month = 'Май' or t.month = 'МАЙ' then 5
				   when t.month = 'июнь' or t.month = 'Июнь' or t.month = 'ИЮНЬ' then 6
				   when t.month = 'июль' or t.month = 'Июль' or t.month = 'ИЮЛЬ' then 7
				   when t.month = 'август' or t.month = 'Август' or t.month = 'АВГУСТ' then 8
				   when t.month = 'сентябрь' or t.month = 'Сентябрь' or t.month = 'СЕНТЯБРЬ' then 9
				   when t.month = 'октябрь' or t.month = 'Октябрь' or t.month = 'ОКТЯБРЬ' then 10
				   when t.month = 'ноябрь' or t.month = 'Ноябрь' or t.month = 'НОЯБРЬ' then 11
				   when t.month = 'декабрь' or t.month = 'Декабрь' or t.month = 'ДЕКАБРЬ' then 12
		end as month,
		bo.id as tab_bazis_bk_ids,
		case when  t.tab_product_bk_ids is null then 0  else prod.id end as tab_product_bk_ids,
		prod.tab_ei_bk_ids as tab_ei_bk_ids,
		ni.id as tab_napr_real_bk_ids,
		pr.id as tab_proizv_bk_ids,
		sob.id as tab_sobstv_bk_ids,
		case when  t.tab_type_otgruz_bk_ids is null then 0  else tot.id end as tab_type_otgruz_bk_ids,
		cat.id as tab_category_sd_bk_ids,
		case when  t.tab_point_to_bk_ids is null then 0  else pt.id end as tab_point_to_bk_ids,	
		case when  t.tab_pokup_bk_ids is null then 0  else pokup.id end as tab_pokup_bk_ids,
		sts.id as tab_status_sd_bk_ids,
		t.value::numeric as value,
		t.cost::numeric as cost,
		t.comment as comment
				
	from tab_sh_zayav_real_bk as t
	
   inner join tab_owner_bk as own on own.name = t.tab_owner_bk_ids
   inner join tab_bazis_bk as bo on bo.name = t.tab_bazis_bk_ids
   inner join tab_napr_real_bk as ni on ni.name = t.tab_napr_real_bk_ids
   inner join tab_proizv_bk as pr on pr.name = t.tab_proizv_bk_ids
   inner join tab_category_sd_bk as cat on cat.name = t.tab_category_sd_bk_ids
   inner join tab_status_sd_bk as sts on sts.name = t.tab_status_sd_bk_ids
   inner join tab_product_bk as prod on prod.name = t.tab_product_bk_ids
   inner join tab_sobstv_bk as sob on sob.name = t.tab_sobstv_bk_ids
   left join tab_point_to_bk as pt on pt.name = t.tab_point_to_bk_ids
   left  join tab_pokup_bk as pokup on pokup.name = t.tab_pokup_bk_ids
   left join tab_type_otgruz_bk as tot on tot.name = t.tab_type_otgruz_bk_ids
   where t.tab_bazis_bk_ids is not null and t.tab_bazis_bk_ids <> '0' and t.month is not null
    );

