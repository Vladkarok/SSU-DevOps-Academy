#!/bin/bash

<<RESOURCE
http://www.biblos.org.ua/forLife/ua_zip_phone.php
Чернівці            0372, 03722
Хмельницький        0382, 03822
Рівне               0362, 03622
Луцьк               03322
Львів               0322
Тернопіль           0352
Івано-Франківськ    0342, 03422
Ужгород             0312, 03122
RESOURCE


echo "Введіть телефонний код обласних центрів Західної України"

read name

if echo $name | grep -qP "^\(?(03[78632541]2)\)?([ -]?\d{2}[ -]?\d{2}[ -]?\d{2})?$|^\(?(03[78632541]22)\)?([ -]?[0-9][ -]?\d{2}[ -]?\d{2})?$"

then

echo "Номер наш"

else

echo "Номер не наш"

fi
