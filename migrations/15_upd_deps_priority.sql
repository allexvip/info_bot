UPDATE deps
SET priority=110
where "dep" LIKE  '%Останина%'
;

UPDATE deps
SET priority=100
where ("dep" LIKE  '%Глазкова%' or "dep" LIKE  '%Ларионова%' or "dep" LIKE  '%Буцкая%' or "dep" LIKE  '%Вторыгина%' or "dep" LIKE  '%Дробот%' or "dep" LIKE  '%Милонов%' or "dep" LIKE  '%Коробова%')  AND "dep" not LIKE  '%Бастрыкин%'
;

UPDATE deps
SET priority=99
where
("dep" LIKE  '%Крашениннико%'
or "dep" LIKE  '%Бессарабо%'
or "dep" LIKE  '%Напс%'
or "dep" LIKE  '%Панькин%'
or "dep" LIKE  '%Синельщико%'
or "dep" LIKE  '%Белы%'
or "dep" LIKE  '%Лисицы%'
or "dep" LIKE  '%Аршб%'
or "dep" LIKE  '%Брыки%'
or "dep" LIKE  '%Вятки%'
or "dep" LIKE  '%Глазков%'
or "dep" LIKE  '%Мархае%'
or "dep" LIKE  '%Петров Ю%'
or "dep" LIKE  '%Тетердинк%'
or "dep" LIKE  '%Чепико%')
;
