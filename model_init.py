def models_init():
    # Create table structure
    cur.executemany('''CREATE TABLE IF NOT EXISTS "logs" (
        "chat_id" BIGINT NULL,
        "username" VARCHAR(50) NULL,
        "upd" DATETIME NULL,
        "message" TEXT NULL
    )
    ;
CREATE TABLE IF NOT EXISTS "deps" (
        "dep_full_name" TEXT NULL,
        "dep" TEXT NULL,
        "party" TEXT NULL,
        "link" TEXT NULL
    )
    ;
CREATE TABLE IF NOT EXISTS "projects" (
        "project_code" VARCHAR(50) NULL,
        "name" TEXT NULL,
        "desc" TEXT NULL
    )
    ;
CREATE TABLE IF NOT EXISTS "votes" (
        "user_answer" VARCHAR(50) NULL,
        "chat_id" BIGINT NULL,
        "upd" DATETIME NULL,
        "project_code" VARCHAR(50) NULL,
        "dep_id" INTEGER NULL
    )
    ;
CREATE TABLE IF NOT EXISTS "users" (
	"chat_id" BIGINT NULL,
	"username" VARCHAR(50) NULL,
	"first_name" VARCHAR(50) NULL,
	"last_name" VARCHAR(50) NULL,
	"region_id" VARCHAR(50) NULL,
	"upd" DATETIME NULL
    )
    ;
create TABLE country(
	"id" BIGINT not null primary key,
	"name" VARCHAR(128) null
	);

	create table region(
	"id"			bigint not null primary key,
	"country_id"	bigint not null REFERENCES country (id),
	"name"		VARCHAR(128) not null
	);

create table city(
	"region_id"	bigint not null REFERENCES region (id),
	"name" VARCHAR(128) not null
	);

    ''')