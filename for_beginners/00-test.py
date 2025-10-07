num = int(input())
if (num // 1000 % 10) - (num // 1 % 10) == (num // 100 % 10) - (num // 10 % 10):
    print("ДА")
else:
    print("НЕТ")
