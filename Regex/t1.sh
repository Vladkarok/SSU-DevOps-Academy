#!/bin/bash

echo "Введіть форму призвища \"Карпенко\""

read surname

if echo $surname | grep -qP '^Карпенк[оану]м?(ві)?$'

then

echo "Корректна форма"

else

echo "Помилкова форма"

fi