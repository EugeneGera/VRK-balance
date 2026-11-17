//01. Загрузка в таблицу TAB_SH_OGR_BK отдельно файла excel

//02. Очистка даты загрузки Ограничения в историю
delete from tab_upload_history_ogr_bk;

//03. Добавить дату загрузки Ограничения в историю
insert into tab_upload_history_ogr_bk
(select (:year)::int as year
	from tab_sh_ogr_bk
	where :year not in (select year from  tab_upload_history_ogr_bk group by year)
	group by year
);

//04. Добавление новых записей в справочник Базис отгрузки
insert into tab_bazis_bk
(select  	row_number() over (order by t.tab_bazis_bk_ids) + (select id as id from tab_bazis_bk order by id desc limit 1)  as id,
			t.tab_bazis_bk_ids as name,
			pr.id	
	from tab_sh_ogr_bk as t
	inner join tab_proizv_bk as pr on pr.name = t.tab_proizv_bk_ids
	where not exists (select name from tab_bazis_bk where name = t.tab_bazis_bk_ids) and t.tab_bazis_bk_ids IS not null and t.tab_bazis_bk_ids <> '0' and t.tab_bazis_bk_ids <> ''
	group by t.tab_bazis_bk_ids, pr.id
	order by t.tab_bazis_bk_ids);

//05. Добавление новых записей в справочник Агент/Производитель
insert into tab_proizv_bk
(select  	row_number() over (order by t.tab_proizv_bk_ids) + (select id as id from tab_proizv_bk order by id desc limit 1)  as id,
			t.tab_proizv_bk_ids as name		
	from tab_sh_ogr_bk as t
	where not exists (select name from tab_proizv_bk where name = t.tab_proizv_bk_ids) and t.tab_bazis_bk_ids is not null and t.tab_bazis_bk_ids <> '0' and t.tab_bazis_bk_ids <> ''
	group by t.tab_proizv_bk_ids
	order by t.tab_proizv_bk_ids);

//06. Добавление новых записей в справочник Продукт
/*Добавление в справочник Категория продукта*/
insert into tab_category_product_bk
(select  	row_number() over (order by t.tab_category_product_bk_ids) + (select ID as id from tab_product_bk order by id desc limit 1)  as id,
			t.tab_category_product_bk_ids as name		
	from tab_sh_ogr_bk as t
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
				
	from tab_sh_ogr_bk  as t
	inner join tab_category_product_bk as cp on cp.name = t.tab_category_product_bk_ids
	inner join tab_ei_bk as ei on ei.name = t.tab_ei_bk_ids
	where not exists (select name from tab_product_bk where name = t.tab_product_bk_ids) and t.tab_bazis_bk_ids is not null and t.tab_bazis_bk_ids <> '0' and t.tab_bazis_bk_ids <> ''
	group by t.tab_product_bk_ids, cp.id, ei.id
	order by t.tab_product_bk_ids);

//07. Добавление новых записей в справочник Собственник продукта
insert into tab_sobstv_bk
(select row_number() over (order by t.tab_sobstv_bk_ids) + (select id as id from tab_sobstv_bk order by id desc limit 1)  as id,
			t.tab_sobstv_bk_ids as name		
	from tab_sh_ogr_bk as t
	where not exists (select name from tab_sobstv_bk where name = t.tab_sobstv_bk_ids) and t.tab_bazis_bk_ids is not null and t.tab_bazis_bk_ids <> '0' and t.tab_bazis_bk_ids <> ''
	group by t.tab_sobstv_bk_ids
	order by t.tab_sobstv_bk_ids);

//08. Очистка dataset Ограничения
delete from tab_zayav_proizv_bk as d 
using tab_upload_history_ogr_bk as history
where d.year = history.year and (min_ost <> 0 or max_otgr <> 0);

//09. Загрузка dataset Ограничения
insert into tab_zayav_proizv_bk
( select
		coalesce ((select max(id) from tab_zayav_real_bk),0) + row_number() over (order by t.id) as id,
		(:year)::int as year,
		 unnest(array[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]) as month,	 
		bo.id as tab_bazis_bk_ids,
		prod.id as tab_product_bk_ids,
		ei.id as tab_ei_bk_ids,
		sob.id as tab_sobstv_bk_ids,
		pr.id as tab_proizv_bk_ids,
		0 as ost,	
		0 as plan,
		unnest(array[t.min_jan, t.min_feb, t.min_mar, t.min_apr, t.min_may, t.min_jun, t.min_jul, t.min_aug, t.min_sep, t.min_oct, t.min_nov, t.min_dec])::numeric as min_ost,
		unnest(array[t.max_jan, t.max_feb, t.max_mar, t.max_apr, t.max_may, t.max_jun, t.max_jul, t.max_aug, t.max_sep, t.max_oct, t.max_nov, t.max_dec])::numeric as max_otgr,
		0 as summ_res,
		0 as percent_birga,
		0 as value_birga,
		t.comment_max as comment
				
	from tab_sh_ogr_bk as t
	
   left join tab_bazis_bk as bo on bo.name = t.tab_bazis_bk_ids
   left join tab_product_bk as prod on prod.name = t.tab_product_bk_ids
   left join tab_ei_bk as ei on ei.name = t.tab_ei_bk_ids
   left join tab_proizv_bk as pr on pr.name = t.tab_proizv_bk_ids
   left join tab_sobstv_bk as sob on sob.name = t.tab_sobstv_bk_ids
    where t.tab_bazis_bk_ids is not null and t.tab_bazis_bk_ids <> '0'
    );

//10. Очистка нулевых значений строк Ограничения
delete from tab_zayav_proizv_bk where tab_bazis_bk_ids is null or tab_bazis_bk_ids = 0;

