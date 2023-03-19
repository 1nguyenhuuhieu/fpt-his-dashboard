CREATE TABLE `post` (
	`post_id` INTEGER PRIMARY KEY,
	`time_created` DATETIME,
	`title` VARCHAR,
	`body` TEXT,
    `username` VARCHAR
);

CREATE TABLE `user` (
	`user_id` INTEGER PRIMARY KEY,
	`user_name` VARCHAR,
	`password` VARCHAR,
    `email` VARCHAR
);

DROP TABLE `post`



CREATE TABLE report_money 
(
    id	INTEGER PRIMARY KEY,
    ngay	DATE,
    tien_kham_benh	INT,
    vien_phi	INT,
    xet_nghiem	INT,
    dien_tim	INT,
    test_covid_19	INT,
    luu_huyet_nao	INT,
    sieu_am	INT,
    xq	INT,
    noi_soi_da_day_thuc_quan	INT,
    noi_soi_tmh	INT,
    noi_soi_ctc	INT,
    kham_suc_khoe	INT,
    bo_bot_gay_me	INT,
    chup_ct	INT,
    tiem_sat	INT,
    tiem_phong_dai	INT,
    tiem_vgb_1ml	INT,
    tiem_vgb_0_5ml	INT,
    vac_xin_rotamin	INT,
    vac_xin_soi_quai_bi_rubella	INT,
    vac_xin_cum	INT,
    vac_xin_quimihib	INT,
    thuoc	INT
);


-- SQLite
CREATE TABLE tableName 
(
    id	VARCHAR(512),
    time_created	VARCHAR(512),
    soluutru	VARCHAR(512),
    nguoinap	VARCHAR(512),
    department_id	INT
);