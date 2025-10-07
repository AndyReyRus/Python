print()
print("Какой язык программирования мы изучаем?")
answer = input()
if answer == "Python":
    print("Верно! Мы ботаем Python =)")
    print("Python - отличный язык!")


print()
answer = input("Какой язык программирования мы изучаем? - ")
if answer == "Python":
    print("Верно! Мы ботаем Python =)")
    print("Python - отличный язык!")


#   if x > 7    если xx больше 77
#   if x < 7    если xx меньше 77
#   if x >= 7   если xx больше либо равен  77
#   if x <= 7   если xx меньше либо равен  77
#   if x == 7   если xx равен  77
#   if x != 7   если xx не равен  77


print()
print("Введи первую цифру")
num1 = int(input())
print("Введи вторую цифру")
num2 = int(input())
if num1 < num2:
    print(num1, "меньше чем", num2)
if num1 > num2:
    print(num1, "больше чем", num2)
if num1 == num2:
    print(num1, "равно", num2)
if num1 != num2:
    print(num1, "не равно", num2)


print()
print("Давай проверим находится твоя цифра между 3 и 6 - или нет?")
age = int(input())
if 3 <= age <= 6:
    print("Вы ребёнок")


print()
print()
num1, num2, num3 = int(input()), int(input()), int(input())
counter = 0  # переменная счётчик
if num1 % 2 == 0:
    counter = counter + 1  # увеличиваем счётчик на 1
if num2 % 2 == 0:
    counter = counter + 1  # увеличиваем счётчик на 1
if num3 % 2 == 0:
    counter = counter + 1  # увеличиваем счётчик на 1
print(counter)


print()
language = "English"
if language == "Русский":
    print("Привет!")
if language == "English":
    print("Hello!")


# цепочки - очень важное равенсво или неравество в Python
print()
language = "Русский"
if language != "English" != "Español":
    print("Язык по умолчанию не является ни английским, ни испанским")
if language != "English" != "Русский":
    print("Язык по умолчанию не является ни английским, ни русским")


print()
print("Давай ты напишешь мне свой возраст, а я опишу твое состояние!")
age = int(input())
if 0 <= age <= 13:
    print("детство")
if 14 <= age <= 24:
    print("молодость")
if 25 <= age <= 59:
    print("зрелость")
if 60 <= age <= 130:
    print("старость")
