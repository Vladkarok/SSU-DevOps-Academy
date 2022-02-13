echo "Введіть форму імені \"Владислав\""

read name

if echo $name | grep -qE '^Владислав(а|у|ом|ами)?$'

then

echo "Корректна форма"

else

echo "Помилкова форма"

fi