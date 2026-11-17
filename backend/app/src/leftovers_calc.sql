--01. Загрузка в таблицу TAB_SH_OST_BK отдельно файла excel

--02. Очистка даты загрузки Остатки в историю
delete from tab_upload_history_ost_bk;

--03. Добавить дату загрузки Остатки в историю
insert into tab_upload_history_ost_bk
(select
				(:year)::int as year, 
				case when LOWER(month) = 'январь' then 1
				   when LOWER(month) = 'февраль' then 2
				   when LOWER(month) = 'март' then 3
				   when LOWER(month) = 'апрель' then 4
				   when LOWER(month) = 'май' then 5
				   when LOWER(month) = 'июнь' then 6
				   when LOWER(month) = 'июль' then 7
				   when LOWER(month) = 'август' then 8
				   when LOWER(month) = 'сентябрь' then 9
				   when LOWER(month) = 'октябрь' then 10
				   when LOWER(month) = 'ноябрь' then 11
				   when LOWER(month) = 'декабрь' then 12
		end as month
		
	from tab_sh_ost_bk
	where concat(month, '.', :year) not in (select concat(month, '.', year) from tab_upload_history_ost_bk group by month, year) and
					month is not null and
					tab_bazis_bk_ids is not null
	group by month, year
);

--04. Добавление новых записей в справочник Базис отгрузки
insert into tab_bazis_bk
(select row_number() over (order by t.tab_bazis_bk_ids) + (select id as id from tab_bazis_bk order by id desc limit 1)  as id,
			t.tab_bazis_bk_ids as name,
			pr.id	
	from tab_sh_ost_bk as t
	inner join tab_proizv_bk as pr on pr.name = t.tab_proizv_bk_ids
	where not exists (select name from tab_bazis_bk where name = t.tab_bazis_bk_ids) and t.tab_bazis_bk_ids is not null and t.tab_bazis_bk_ids <> '0' and t.tab_bazis_bk_ids <> ''
	group by t.tab_bazis_bk_ids, pr.id
	order by t.tab_bazis_bk_ids);


--05. Добавление новых записей в справочник Агент/Производитель

insert into tab_proizv_bk
(select  	row_number() over (order by t.tab_proizv_bk_ids) + (select id as id from tab_proizv_bk order by id desc limit 1)  as id,
			t.tab_proizv_bk_ids as name		
	from tab_sh_ost_bk as t
	where not exists (select name from tab_proizv_bk where name = t.tab_proizv_bk_ids) and t.tab_bazis_bk_ids is not null and t.tab_bazis_bk_ids <> '0' and t.tab_bazis_bk_ids <> ''
	group by t.tab_proizv_bk_ids
	order by t.tab_proizv_bk_ids);

--06. Добавление новых записей в справочник Продукт
/*Добавление в справочник Категория продукта*/
insert into tab_category_product_bk
(select  	row_number() over (order by t.tab_category_product_bk_ids) + (select ID as id from tab_product_bk order by id desc limit 1)  as id,
			t.tab_category_product_bk_ids as name		
	from tab_sh_ost_bk as t
	where not exists (select name from tab_category_product_bk where name = t.tab_category_product_bk_ids) and 
					t.tab_bazis_bk_ids is not null and 
					t.tab_bazis_bk_ids <> '0' and 
					t.tab_bazis_bk_ids <> '' and
					t.tab_category_product_bk_ids is not null and
					t.tab_category_product_bk_ids <> ''
	group by t.tab_category_product_bk_ids
	order by t.tab_category_product_bk_ids);
	
/*Добавление в справочник Продукт*/
INSERT INTO TAB_PRODUCT_BK
(SELECT  	ROW_NUMBER() OVER (ORDER BY T.TAB_PRODUCT_BK_IDS) + (SELECT ID AS ID FROM TAB_PRODUCT_BK ORDER BY ID DESC LIMIT 1)  AS ID,
			T.TAB_PRODUCT_BK_IDS AS NAME,
			cp.id as TAB_CATEGORY_PRODUCT_BK_IDS,
			ei.id as TAB_EI_BK_IDS
				
	FROM TAB_SH_OST_BK AS T
	INNER JOIN TAB_CATEGORY_PRODUCT_BK as cp on cp.name = T.TAB_CATEGORY_PRODUCT_BK_IDS
	INNER JOIN TAB_EI_BK as ei on ei.name = T.TAB_EI_BK_IDS
	WHERE NOT EXISTS (SELECT NAME FROM TAB_PRODUCT_BK WHERE NAME = T.TAB_PRODUCT_BK_IDS) AND T.TAB_BAZIS_BK_IDS IS NOT NULL AND T.TAB_BAZIS_BK_IDS <> '0' AND T.TAB_BAZIS_BK_IDS <> ''
	GROUP BY T.TAB_PRODUCT_BK_IDS, cp.id, ei.id
	ORDER BY T.TAB_PRODUCT_BK_IDS);

--07. Добавление новых записей в справочник Собственник продукта
insert into tab_sobstv_bk
(select row_number() over (order by t.tab_sobstv_bk_ids) + (select id as id from tab_sobstv_bk order by id desc limit 1)  as id,
			t.tab_sobstv_bk_ids as name		
	from tab_sh_ost_bk as t
	where not exists (select name from tab_sobstv_bk where name = t.tab_sobstv_bk_ids) and t.tab_bazis_bk_ids is not null and t.tab_bazis_bk_ids <> '0' and t.tab_bazis_bk_ids <> ''
	group by t.tab_sobstv_bk_ids
	order by t.tab_sobstv_bk_ids);

--08. Очистка dataset Ограничения
delete from tab_zayav_proizv_bk as d 
using tab_upload_history_ost_bk as history
where d.month = history.month and d.year = history.year and (ost <> 0);

--09. Загрузка dataset Ограничения
insert into tab_zayav_proizv_bk
( select
		coalesce ((select max(id) from  tab_zayav_real_bk),0) + row_number() over (order by t.id) as id,
		(:year)::int as year,
		case when LOWER(t.month) = 'январь' then 1
				   when LOWER(t.month) = 'февраль' then 2
				   when LOWER(t.month) = 'март' then 3
				   when LOWER(t.month) = 'апрель' then 4
				   when LOWER(t.month) = 'май' then 5
				   when LOWER(t.month) = 'июнь' then 6
				   when LOWER(t.month) = 'июль' then 7
				   when LOWER(t.month) = 'август' then 8
				   when LOWER(t.month) = 'сентябрь' then 9
				   when LOWER(t.month) = 'октябрь' then 10
				   when LOWER(t.month) = 'ноябрь' then 11
				   when LOWER(t.month) = 'декабрь' then 12
		end as month, 
		bo.id as tab_bazis_bk_ids,
		prod.id as tab_product_bk_ids,
		ei.id as tab_ei_bk_ids,
		sob.id as tab_sobstv_bk_ids,
		pr.id as tab_proizv_bk_ids,
		t.ost::numeric as ost,	
		0 as plan,
		0 as min_ost,
		0 as max_otgr,
		0 as summ_res,
		0 as percent_birga,
		0 as value_birga,
		t.comment as comment
				
	from tab_sh_ost_bk as t
	
   left join tab_bazis_bk as bo on bo.name = t.tab_bazis_bk_ids
   left join tab_product_bk as prod on prod.name = t.tab_product_bk_ids
   left join tab_ei_bk as ei on ei.name = t.tab_ei_bk_ids
   left join tab_proizv_bk as pr on pr.name = t.tab_proizv_bk_ids
   left join tab_sobstv_bk as sob on sob.name = t.tab_sobstv_bk_ids
   
    where t.tab_bazis_bk_ids is not null and t.tab_bazis_bk_ids <> '0'
    );
