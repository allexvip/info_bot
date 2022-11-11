#ALTER TABLE "deps" ADD COLUMN "priority" INTEGER NOT NULL DEFAULT 0;
update "deps" set "priority"=10;