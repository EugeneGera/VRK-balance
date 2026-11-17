--01. Загрузка в таблицу TAB_SH_PROIZV_BK отдельно файла excel

--02. Очистка даты загрузки План производства в историю
delete from tab_upload_history_zayav_proizv_bk;

--03. Добавить дату загрузки План производства в историю
insert into tab_upload_history_zayav_proizv_bk
(select (:year)::int as year
	from tab_sh_zayav_proizv_bk
	where :year not in (select year from  tab_upload_history_zayav_proizv_bk group by year)
	group by year
);

--04. Добавление новых записей в справочник Базис отгрузки
insert into tab_bazis_bk
(select  	row_number() over (order by t.tab_bazis_bk_ids) + (select id as id from tab_bazis_bk order by id desc limit 1)  as id,
			t.tab_bazis_bk_ids as name,
			pr.id	
	from tab_sh_zayav_proizv_bk as t
	inner join tab_proizv_bk as pr on pr.name = t.tab_proizv_bk_ids
	where not exists (select name from tab_bazis_bk where name = t.tab_bazis_bk_ids) and t.tab_bazis_bk_ids is not null and t.tab_bazis_bk_ids <> '0' and t.tab_bazis_bk_ids <> ''
	group by t.tab_bazis_bk_ids, pr.id
	order by t.tab_bazis_bk_ids);

--05. Добавление новых записей в справочник Агент/ПроизводительINSERT INTO TAB_PROIZV_BK
insert into tab_proizv_bk
(select  	row_number() over (order by t.tab_proizv_bk_ids) + (select id as id from tab_proizv_bk order by id desc limit 1)  as id,
			t.tab_proizv_bk_ids as name		
	from tab_sh_zayav_proizv_bk as t
	where not exists (select name from tab_proizv_bk where name = t.tab_proizv_bk_ids) and t.tab_bazis_bk_ids is not null and t.tab_bazis_bk_ids <> '0' and t.tab_bazis_bk_ids <> ''
	group by t.tab_proizv_bk_ids
	order by t.tab_proizv_bk_ids);

--06. Добавление новых записей в справочник Продукт
/*Добавление в справочник Категория продукта*/
insert into tab_category_product_bk
(select  	row_number() over (order by t.tab_category_product_bk_ids) + (select id as id from tab_product_bk order by id desc limit 1)  as id,
			t.tab_category_product_bk_ids as name		
	from tab_sh_zayav_proizv_bk as t
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
(select  	row_number() over (order by t.tab_product_bk_ids) + (select id as id from tab_product_bk order by id desc limit 1)  as id,
			t.tab_product_bk_ids as name,
			cp.id as tab_category_product_bk_ids,
			ei.id as tab_ei_bk_ids
				
	from tab_sh_zayav_proizv_bk as t
	inner join tab_category_product_bk as cp on cp.name = t.tab_category_product_bk_ids
	inner join tab_ei_bk as ei on ei.name = t.tab_ei_bk_ids
	where not exists (select name from tab_product_bk where name = t.tab_product_bk_ids) and t.tab_bazis_bk_ids is not null and t.tab_bazis_bk_ids <> '0' and t.tab_bazis_bk_ids <> ''
	group by t.tab_product_bk_ids, cp.id, ei.id
	order by t.tab_product_bk_ids);

--07. Добавление новых записей в справочник Собственник продукта
insert into tab_sobstv_bk
(select row_number() over (order by t.tab_sobstv_bk_ids) + (select id as id from tab_sobstv_bk order by id desc limit 1)  as id,
			t.tab_sobstv_bk_ids as name		
	from tab_sh_zayav_proizv_bk as t
	where not exists (select name from tab_sobstv_bk where name = t.tab_sobstv_bk_ids) and t.tab_bazis_bk_ids is not null and t.tab_bazis_bk_ids <> '0' and t.tab_bazis_bk_ids <> ''
	group by t.tab_sobstv_bk_ids
	order by t.tab_sobstv_bk_ids);

--08. Очистка dataset План производства
delete from tab_zayav_proizv_bk as d 
using tab_upload_history_zayav_proizv_bk as history
where d.year::INTEGER = history.year::INTEGER and (plan is not null or plan::INTEGER <> 0);

--09. Загрузка dataset План производства
insert into tab_zayav_proizv_bk
( select
		coalesce ((select max(id) from  tab_zayav_proizv_bk),0) + row_number() over (order by t.id) as id,
		(:year)::int as year,
		 unnest(array[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]) as month,	 
		bo.id as tab_bazis_bk_ids,
		prod.id as tab_product_bk_ids,
		ei.id as tab_ei_bk_ids,
		sob.id as tab_sobstv_bk_ids,
		pr.id as tab_proizv_bk_ids,
		0 as ost,	
		unnest(array[t.jan::numeric, t.feb::numeric, t.mar::numeric, t.apr::numeric, t.may::numeric, t.jun::numeric, t.jul::numeric, t.aug::numeric, t.sep::numeric, t.oct::numeric, t.nov::numeric, t.dec::numeric])::numeric as plan,
		0 as min_ost,
		0 as max_otgr,
		0 as summ_res,
		0 as percent_birga,
		0 as value_birga,
		t.comment as comment
				
	from tab_sh_zayav_proizv_bk as t
	
   left join tab_bazis_bk as bo on bo.name = t.tab_bazis_bk_ids
   left join tab_product_bk as prod on prod.name = t.tab_product_bk_ids
   left join tab_ei_bk as ei on ei.name = t.tab_ei_bk_ids
   left join tab_proizv_bk as pr on pr.name = t.tab_proizv_bk_ids
   left join tab_sobstv_bk as sob on sob.name = t.tab_sobstv_bk_ids
    where t.tab_bazis_bk_ids is not null and t.tab_bazis_bk_ids <> '0'
    );

--10. Пересчет id в таблице План производства
with numbered_rows as (
	select
		ctid,
		row_number() over (
			partition by year
			order by year, month, tab_bazis_bk_ids, tab_product_bk_ids
		) as new_id
	from tab_zayav_proizv_bk
)

update tab_zayav_proizv_bk t
set id = nr.new_id
from numbered_rows as nr
where t.ctid = nr.ctid;

--11. Расчет процента по Бирже
update TAB_ZAYAV_PROIZV_BK as zp
set PERCENT_BIRGA = PERCENT
from TAB_BIRGA_PERCENT_BK b
where zp.tab_product_bk_ids = b.tab_product_bk_ids and
			zp.year = b.year and
			b.year = :year;

--12. Расчет процента по Бирже обязательства12. Расчет процента по Бирже обязательства
update tab_zayav_proizv_bk 
set value_birga = percent_birga*plan
where year = :year;
