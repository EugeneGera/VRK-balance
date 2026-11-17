--01. Очистка DATASET

delete from tab_dataset_bk
where year = :year;

--02. Загрузка DATASET

insert into tab_dataset_bk
(select
	t.tab_owner_bk_ids as tab_owner_bk_ids,
	t.year as year,
	t.month as month,
	t.tab_bazis_bk_ids as tab_bazis_bk_ids,
	t.tab_product_bk_ids as tab_product_bk_ids,
	t.tab_ei_bk_ids as tab_ei_bk_ids,
	t.tab_napr_real_bk_ids as tab_napr_real_bk_ids,
	t.tab_proizv_bk_ids as tab_proizv_bk_ids,
	t.tab_sobstv_bk_ids as tab_sobstv_bk_ids,
	t.tab_type_otgruz_bk_ids as type_otgruz_bk_ids,
	t.tab_category_sd_bk_ids as tab_category_sd_bk_ids,
	t.tab_point_to_bk_ids as tab_point_to_bk_ids,
	t.tab_pokup_bk_ids as tab_pokup_bk_ids,
	t.tab_status_sd_bk_ids as tab_status_sd_bk_ids,
	sum(t.value) as value,
	sum(t.cost) as cost,
	tp. tab_category_product_bk_ids as tab_category_product_bk_ids,
	cs.tab_type_sd_bk_ids as tab_type_sd_bk_ids,
	cs.tab_kanal_sb_bk_ids as tab_kanal_sb_bk_ids,
	0 as all_resourse,
	0 as resource_before_zayav,
	0 as accept_zayav,
	0 as ost_resource_after_zayav,
	0 as ost_zayav, 
	0 as cos_x_value,
	0 as num_zayav,
	t.id as id_zayav_real
	
	from tab_zayav_real_bk as t
		left join tab_product_bk as tp on tp.id = t.tab_product_bk_ids
		left join tab_category_sd_bk as cs on cs.id = t.tab_category_sd_bk_ids
	
    where t.year = :year
	group by
		t.tab_owner_bk_ids,
		t.year,
		t.month,
		t.tab_bazis_bk_ids,
		t.tab_product_bk_ids,
		t.tab_ei_bk_ids,
		t.tab_napr_real_bk_ids,
		t.tab_proizv_bk_ids,
		t.tab_sobstv_bk_ids,
		t.tab_type_otgruz_bk_ids,
		t.tab_category_sd_bk_ids,
		t.tab_point_to_bk_ids,
		t.tab_pokup_bk_ids,
		t.tab_status_sd_bk_ids,
		tp.tab_category_product_bk_ids,
		cs.tab_type_sd_bk_ids,
		cs.tab_kanal_sb_bk_ids,
		t.id
    )
	
	union all
	
	(select
		null as tab_owner_bk_ids,
		plan.year as year,
		plan.month as month,
		plan.tab_bazis_bk_ids as tab_bazis_bk_ids,
		plan.tab_product_bk_ids as tab_product_bk_ids,
		plan.tab_ei_bk_ids as tab_ei_bk_ids,
		null as tab_napr_real_bk_ids,
		plan.tab_proizv_bk_ids as tab_proizv_bk_ids,
		plan.tab_sobstv_bk_ids as tab_sobstv_bk_ids,
		null as type_otgruz_bk_ids,
		null as tab_category_sd_bk_ids,
		null as tab_point_to_bk_ids,
		null as tab_pokup_bk_ids,
		null as tab_status_sd_bk_ids,
		0 as value,
		0 as cost,
		tp. tab_category_product_bk_ids as tab_category_product_bk_ids,
		0 as tab_type_sd_bk_ids,
		0 as tab_kanal_sb_bk_ids,
		0 as all_resourse,
		0 as resource_before_zayav,
		0 as accept_zayav,
		0 as ost_resource_after_zayav,
		0 as ost_zayav, 
		0 as cos_x_value,
		0 as NUM_zayav,
		0 as ID_ZAYAV_REAL
	
from tab_zayav_proizv_bk as plan
left join tab_product_bk as tp on tp.id = plan.tab_product_bk_ids
where not  exists (select year, 
	month, 
	tab_bazis_bk_ids, 
	tab_product_bk_ids, tab_sobstv_bk_ids,
	tab_proizv_bk_ids from tab_zayav_real_bk as z 
	where
			plan.year = z.year and
			plan.month = z.month and
			plan.tab_bazis_bk_ids = z.tab_bazis_bk_ids and
			plan.tab_product_bk_ids = z.tab_product_bk_ids and
			plan.tab_sobstv_bk_ids = z.tab_sobstv_bk_ids and
			plan.tab_proizv_bk_ids = z.tab_proizv_bk_ids) and
			plan.year = :year
group by 
	plan.year, 
	plan.month, 
	plan.tab_bazis_bk_ids, 
	plan.tab_product_bk_ids, tab_sobstv_bk_ids,
	plan.tab_proizv_bk_ids,
	tp. tab_category_product_bk_ids,
	plan.tab_ei_bk_ids
	having sum(plan.plan) > 0);

-- 03. Очистка Ресурс

delete from tab_resource_bk
where year = :year;

-- 04. Загрузка Ресурса

insert into tab_resource_bk	
(select
		tab_bazis_bk_ids as tab_bazis_bk_ids,
		tab_product_bk_ids as tab_product_bk_ids,
		year as year,
		month as month,
		sum(plan) as plan,
		sum(min_ost) as min_ost,
		sum(max_otgr) as max_otgr,
		sum(ost) as_ost,
		0 as summ_res
			
	from tab_zayav_proizv_bk
	where year = :year
	group by
		tab_bazis_bk_ids, 
		tab_product_bk_ids, 
		year, 
		month
    );

-- 05. Расчет Ресурса

update tab_resource_bk	
set summ_res = 
		case 
			when max_otgr = 0 then plan + ost - min_ost
			when max_otgr <> 0 and plan + ost - min_ost <= max_otgr  then plan + ost - min_ost
			when max_otgr <> 0 and plan + ost - min_ost > max_otgr then max_otgr
		end
	where year = :year;

-- 06. Расчет ограничений

update tab_resource_bk	
set ogr = plan + ost - summ_res
	where year = :year;

-- 07_1 Обновление id в dataset для заявок на реализацию
WITH numbered_datasets as (
	select
ds.id_zayav_real,
    CONCAT(ds.year, '-', 
           ds.month, '-',
           ds.tab_category_product_bk_ids, '-',
           ds.tab_bazis_bk_ids, '-',
           ds.tab_sobstv_bk_ids, '-',
           ds.tab_kanal_sb_bk_ids, '-',
           ds.tab_status_sd_bk_ids, '-',
           ds.tab_napr_real_bk_ids, '-',
           ROW_NUMBER() OVER (PARTITION BY ds.year, 
                                             ds.month,
                                             ds.tab_category_product_bk_ids,
                                             ds.tab_bazis_bk_ids,
                                             ds.tab_sobstv_bk_ids,
                                             ds.tab_kanal_sb_bk_ids,
                                             ds.tab_status_sd_bk_ids,
                                             ds.tab_napr_real_bk_ids
                              ORDER BY ds.year, 
                                       ds.month,
                                       ds.tab_category_product_bk_ids,
                                       ds.tab_bazis_bk_ids,
                                       ds.tab_sobstv_bk_ids,
                                       ds.tab_kanal_sb_bk_ids,
                                       ds.tab_status_sd_bk_ids,
                                       ds.tab_napr_real_bk_ids)
    ) as new_id
FROM tab_dataset_bk ds
JOIN tab_zayav_real_bk zr ON ds.ID_ZAYAV_REAL = zr.id
	
)

update tab_dataset_bk
set id = numbered_datasets.new_id
from numbered_datasets
where tab_dataset_bk.id_zayav_real = numbered_datasets.id_zayav_real;

-- 07_2 Проставить нумерацию заявок

WITH matching_rows AS (
    SELECT 
        ds.id,
        ds.ctid,
        ds.year,
        ds.month,
        ds.tab_bazis_bk_ids,
        ds.tab_product_bk_ids
    FROM tab_dataset_bk ds
    JOIN tab_zayav_real_bk zr ON 
        ds.ID_ZAYAV_REAL = zr.id
    WHERE ds.year = :year
    ORDER BY ds.year, ds.month, ds.tab_bazis_bk_ids, ds.tab_product_bk_ids, ds.id
),
numbered_rows AS (
    SELECT 
        id,
        ROW_NUMBER() OVER (
            PARTITION BY year, month, tab_bazis_bk_ids, tab_product_bk_ids
            ORDER BY id  -- Сортируем по полю id вместо ctid
        ) AS row_num
    FROM matching_rows
)

UPDATE tab_dataset_bk
SET num_zayav = numbered_rows.row_num
FROM numbered_rows
WHERE tab_dataset_bk.id = numbered_rows.id
AND tab_dataset_bk.year = :year;

-- 08_1 Заполнение ALL_RESOURCE для Dataset08

update tab_dataset_bk as dt
set all_resourse = r.summ_res
from tab_resource_bk as r
where
	dt.year= r.year and
	dt.month = r.month and
	dt.tab_bazis_bk_ids = r.tab_bazis_bk_ids and
	dt.tab_product_bk_ids = r.tab_product_bk_ids and
	dt.year = :year;


-- 08_2. Заполнение Плана Остатков и Ограничений для Dataset
UPDATE TAB_DATASET_BK as dt
SET plan = r.plan,
ost = r.ost,
ogr = r.ogr
from tab_resource_bk as r
WHERE
	dt.year = r.year and
	dt.month = r.month and
	dt.TAB_BAZIS_BK_IDS = r.TAB_BAZIS_BK_IDS and
	dt.TAB_PRODUCT_BK_IDS = r.TAB_PRODUCT_BK_IDS and
	dt.year = :year;

-- 08_3. Заполнение остатка от ресурса Dataset где нет заявок

update tab_dataset_bk as dt
set ost_resource_after_zayav = (dt.all_resourse - dt.accept_zayav),
       resource_before_zayav = dt.all_resourse
where
	dt.num_zayav = 0 and 
	dt.year = :year and
	not exists
			 (select 1
				 from tab_dataset_bk  as t
				 where t.num_zayav <> 0 and 
				 			dt.year= t.year and
							dt.month = t.month and
							dt.tab_bazis_bk_ids = t.tab_bazis_bk_ids and
							dt.tab_product_bk_ids = t.tab_product_bk_ids);

-- 09. Заполнение RESOURCE_BEFORE_ZAYAV для первых заявок для Dataset

update tab_dataset_bk
set resource_before_zayav = all_resourse
where num_zayav = 1 and year = :year;

-- 10. Заполнение расределения заявок
WITH RECURSIVE calculation_sequence AS (
    -- Первая заявка (num_zayav = 1)
    SELECT 
        num_zayav,
        year,
        month,
        tab_bazis_bk_ids,
        tab_product_bk_ids,
        value::numeric,
        all_resourse::numeric,
        tab_kanal_sb_bk_ids,
        tab_status_sd_bk_ids,
        all_resourse::numeric AS RESOURCE_BEFORE_ZAYAV,
        CASE 
            WHEN all_resourse = 0 THEN 0
            WHEN  all_resourse > 0 and (tab_kanal_sb_bk_ids = 1 OR tab_status_sd_bk_ids = 1) THEN value
            WHEN all_resourse < value THEN all_resourse
            ELSE value
        END AS accept_zayav,
        (all_resourse - CASE 
            WHEN all_resourse = 0 THEN 0
            WHEN all_resourse > 0 and (tab_kanal_sb_bk_ids = 1 OR tab_status_sd_bk_ids = 1)  THEN value
            WHEN all_resourse < value THEN all_resourse
            ELSE value
        END)::numeric AS ost_resource_after_zayav
    FROM 
        tab_dataset_bk
    WHERE 
        num_zayav = 1
        AND year = :year
    
    UNION ALL
    
    --Последующие заявки
    SELECT 
        ds.num_zayav,
        ds.year,
        ds.month,
        ds.tab_bazis_bk_ids,
        ds.tab_product_bk_ids,
        ds.value,
        ds.all_resourse,
        ds.tab_kanal_sb_bk_ids,
        ds.tab_status_sd_bk_ids,
        CASE 
            WHEN cs.ost_resource_after_zayav > 0 THEN cs.ost_resource_after_zayav 
            ELSE 0 
        END AS resource_before_zayav,
        CASE 
            WHEN cs.ost_resource_after_zayav <= 0 THEN 0
            WHEN ds.value > CASE WHEN cs.ost_resource_after_zayav > 0 THEN cs.ost_resource_after_zayav ELSE 0 END THEN 
                CASE 
                    WHEN (ds.tab_kanal_sb_bk_ids = 1 OR ds.tab_status_sd_bk_ids = 1) then ds.value
                    WHEN cs.ost_resource_after_zayav > 0 and (ds.tab_kanal_sb_bk_ids <> 1 and ds.tab_status_sd_bk_ids <> 1) THEN cs.ost_resource_after_zayav 
                    ELSE 0 
                END
            ELSE ds.value
        END AS accept_zayav,
        CASE 
            WHEN cs.ost_resource_after_zayav <= 0 THEN 0
            ELSE CASE WHEN cs.ost_resource_after_zayav > 0 THEN cs.ost_resource_after_zayav  ELSE 0  END 
                    - CASE WHEN ds.value >  CASE WHEN cs.ost_resource_after_zayav > 0 
                                                                            THEN cs.ost_resource_after_zayav 
                                                                            ELSE 0  
                                                                END 
                                THEN CASE WHEN cs.ost_resource_after_zayav > 0 THEN cs.ost_resource_after_zayav ELSE 0 END                
                                ELSE ds.value
                     END
        END AS ost_resource_after_zayav
   
    FROM 
        tab_dataset_bk ds
    JOIN 
        calculation_sequence cs ON (
            ds.year = cs.year AND
            ds.month = cs.month AND
            ds.tab_bazis_bk_ids = cs.tab_bazis_bk_ids AND
            ds.tab_product_bk_ids = cs.tab_product_bk_ids AND
            ds.num_zayav = cs.num_zayav + 1
        )
    WHERE 
        ds.year = :year
)
UPDATE tab_dataset_bk ds
SET 
    resource_before_zayav = cs.resource_before_zayav,
    ost_resource_after_zayav = cs.ost_resource_after_zayav,
    accept_zayav = cs.accept_zayav
FROM 
    calculation_sequence cs
WHERE 
    ds.num_zayav = cs.num_zayav AND
    ds.year = cs.year AND
    ds.month = cs.month AND
    ds.tab_bazis_bk_ids = cs.tab_bazis_bk_ids AND
    ds.tab_product_bk_ids = cs.tab_product_bk_ids AND
    ds.year = :year;

-- 11. Обновление Остатка от заявки, цена*объем принятый

UPDATE tab_dataset_bk
SET
       	ost_zayav = case when (value - accept_zayav) <= 0 then 0
		   								when (value - accept_zayav) >0 then (value - accept_zayav)
							 end,
		cost_x_value = cost * accept_zayav,
		ost_resource_after_zayav = case when ost_resource_after_zayav <= 0 then 0
		   								when ost_resource_after_zayav > 0 then ost_resource_after_zayav
							 end,
		resource_before_zayav = case when resource_before_zayav <= 0 then 0
		   								when resource_before_zayav > 0 then resource_before_zayav
							 end
where year = :year;

-- 12. Загрузка биржа по заявкам

update tab_dataset_bk
set  value_birga = value 
where year = :year and tab_category_sd_bk_ids in (3, 8);

