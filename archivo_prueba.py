def suma(a, b):
    total = a + b
    if total >= 10:
        return "mayor o igual a 10"
    else:
        return 'menor que 10'

x = 3
y = 9
print(suma(x, y))