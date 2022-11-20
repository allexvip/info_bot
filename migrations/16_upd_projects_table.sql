ALTER TABLE "projects" 	ADD COLUMN "activity" TINYINT NULL DEFAULT '0';
UPDATE "bot_db"."projects" SET "activity"='1' WHERE  "project_code" in ('vospitanie','alimentover');
