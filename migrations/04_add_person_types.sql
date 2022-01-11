ALTER TABLE "deps" ADD COLUMN "person_type" VARCHAR(15) NULL DEFAULT NULL;
UPDATE deps SET person_type = 'deputat';
ALTER TABLE "deps" ADD COLUMN "region" TEXT NULL;
ALTER TABLE "deps" ADD COLUMN "link_send" TEXT NULL DEFAULT NULL;
UPDATE deps SET `link_send`='https://priemnaya.duma.gov.ru/ru/message/?type=1';
