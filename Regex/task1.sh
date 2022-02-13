echo "Введіть форму призвища \"Карпенко\""

read surname

if echo $surname | grep -qE '^Карпенк[оуаи]м?$'

then

echo "Корректна форма"

else

echo "Помилкова форма"

fi