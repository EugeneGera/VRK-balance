-- Apply only to an isolated copy of BK.sql used for both experimental conditions.
-- These two historical periods deliberately distinguish known zero from missing data.
BEGIN;
INSERT INTO public.tab_zayav_proizv_bk
    (id,year,month,tab_bazis_bk_ids,tab_product_bk_ids,tab_ei_bk_ids,tab_sobstv_bk_ids,tab_proizv_bk_ids,ost,plan,min_ost,max_otgr,summ_res,percent_birga,value_birga,comment_plan)
VALUES
    (990001,2024,1,1,1,2,1,1,0,0,0,0,0,0,0,'Контроль: известный ноль'),
    (990002,2024,2,1,1,2,1,1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Контроль: отсутствующие значения');
INSERT INTO public.tab_resource_bk
    (tab_bazis_bk_ids,tab_product_bk_ids,year,month,plan,min_ost,max_otgr,ost,summ_res,ogr)
VALUES (1,1,2024,1,0,0,0,0,0,0), (1,1,2024,2,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO public.tab_zayav_real_bk
    (id,tab_owner_bk_ids,year,month,tab_bazis_bk_ids,tab_product_bk_ids,tab_ei_bk_ids,tab_napr_real_bk_ids,tab_proizv_bk_ids,tab_sobstv_bk_ids,tab_type_otgruz_bk_ids,tab_category_sd_bk_ids,tab_point_to_bk_ids,tab_pokup_bk_ids,tab_status_sd_bk_ids,value,cost,comment)
VALUES
    (990001,1,2024,1,1,1,2,2,1,1,1,3,1,3,2,0,0,'Контроль: известный ноль'),
    (990002,1,2024,2,1,1,2,2,1,1,1,3,1,3,2,NULL,NULL,'Контроль: отсутствующие значения');
INSERT INTO public.tab_dataset_bk
    (id,year,month,tab_bazis_bk_ids,tab_product_bk_ids,tab_ei_bk_ids,tab_category_product_bk_ids,tab_owner_bk_ids,tab_proizv_bk_ids,tab_sobstv_bk_ids,tab_napr_real_bk_ids,tab_type_otgruz_bk_ids,tab_category_sd_bk_ids,tab_type_sd_bk_ids,tab_kanal_sb_bk_ids,tab_status_sd_bk_ids,value,cost,accept_zayav,id_zayav_real,all_resourse,plan,ost,ogr)
VALUES
    ('control-zero',2024,1,1,1,2,101,1,1,1,2,1,3,1,1,2,0,0,0,990001,0,0,0,0),
    ('control-null',2024,2,1,1,2,101,1,1,1,2,1,3,1,1,2,NULL,NULL,NULL,990002,NULL,NULL,NULL,NULL);
COMMIT;
