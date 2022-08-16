import numpy

per_cent = {'ТКБ': 5.6, 'СКБ': 5.9, 'ВТБ': 4.28, 'СБЕР': 4.0}

money = int(input('Введите сумму:'))


deposit = list(per_cent.values())

deposit = deposit * money
#for i in deposit:
#    deposit[i] *= money

print(deposit)