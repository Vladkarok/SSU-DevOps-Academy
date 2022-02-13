#!/bin/bash

echo "Введіть форму імені \"Владислав\""

read name

if echo $name | grep -qP '^Владислав(а|у|ом|ами|ові)?$|чик[a(ом)]?$'

then

echo "Корректна форма"

else

echo "Помилкова форма"

fi