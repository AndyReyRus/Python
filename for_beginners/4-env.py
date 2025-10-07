print()  # рассматривается - переменная env - именованная область памяти
print()
sity = "Moscow"
print(sity, "- it's my sity!")


print()
print()
name = "Алеша"
city = "Тула"
print("Меня зовут", name, ".", city, "- мой город!")


print()
print()
name1 = "Тимур"
name2 = name1
name1 = "Гвидо"
print(name1)
print(name2)


print()  # В языке Python за одну инструкцию присваивания можно задавать значения сразу нескольким переменным
print()
name, surname = "Timur", "Gusev"
print("Имя:", name, "Фамилия:", surname)


print()  # Тоже самое - можно записать и так
print()
name = "Timur"
surname = "Gusev"
print("Имя:", name, "Фамилия:", surname)


print()  # Если требуется считать текст с клавиатуры и присвоить его в качестве значения переменным
print()
name, surname = input(), input()
print("Имя:", name, "Фамилия:", surname)
