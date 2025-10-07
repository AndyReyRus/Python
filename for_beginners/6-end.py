print()  # рассмаривается необязательный именованный параметр - end - который настраивает управляющую последовательностью и задаёт перевод строки
print("A great man doesn't seek to lead.")
print("He's called to it. And he answers.")


print()
print(
    "A great man doesn't seek to lead.", end="\n"
)  # обе строки являются эквивалентными
print("He's called to it. And he answers.", end="\n")


print()
print()  # вызов команды `print()` с пустыми скобками делает перевод строки
print("Python")
print()
print("C#")
print("Java")
print()
print("JavaScript")


print()
minus = "-"
print("a", "b", "c", end=minus)
print("second line")


print()
schitalka = " - сидели"
print("а", "и", "б", end=schitalka)
print(" на трубе")


print()
print("Python", "\n", "Rules", "\n", "4ever", sep="", end="!")


print()
print()
arg1 = "Hello"
sep1 = "_-_"
end2 = "+++"
print(arg1, "everyone", sep=sep1, end="! ")
print("How", "are", "you", "in", "2024?", sep=" ", end=end2)


print()
print()
print("a", "b", "c", sep="", end="")
print("d", "e", "f", sep="", end="")


print()
print()
print("Как тебя зовут сучка?")
name = input()
print("Привет,", name, end="!")
