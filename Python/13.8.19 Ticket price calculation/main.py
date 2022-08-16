# Для онлайн-конференции необходимо написать программу, которая будет подсчитывать общую стоимость билетов.
# Программа должна работать следующим образом:
#
# 1. В начале у пользователя запрашивается количество билетов, которые он хочет приобрести на мероприятие.
#
# 2. Далее для каждого билета запрашивается возраст посетителя, в соответствии со значением которого
#    выбирается стоимость:
#
# Если посетителю конференции менее 18 лет, то он проходит на конференцию бесплатно.
# От 18 до 25 лет — 990 руб.
# От 25 лет — полная стоимость 1390 руб.
#
# 3. В результате программы выводится сумма к оплате. При этом, если человек регистрирует больше трёх человек
# на конференцию, то дополнительно получает 10% скидку на полную стоимость заказа.

# price for a guest
def price(guest_age: int):
    '''
    Returns full price for a guest
    :param guest_age: age of the guest
    :return: price applied for the guest of his or her age
    '''
    # declare prices dict as age limit and its price. For example, {0: 0} means a guest must be not younger than 0 years
    prices = {(0, 18): 0, (18, 25): 990, (25, 200): 1390}

    return max([p for a, p in zip(prices.keys(), prices.values()) if a[0] <= guest_age < a[1]])


# order totals
def totals(guests_list: [], discount=False):
    '''
    Returns total price for the order
    :param guests_list: list of guest ages
    :param discount: True if you want to get just discount; False for order totals
    :return: total price for the order or the sum of discount value, if requested
    '''
    return sum((.1 if discount else (.9 if len(guests_list) > 3 else 1)) * p for p in map(price, guests_list))


n = input("Введите количество пользователей: ")

# check whether user typed a number
while(not n.isdigit() or int(n) == 0):
    n = input("Ошибка. Введите число, соответствующее количеству пользователей: ")

# store number of users
n = int(n)
L = []
age = 0

for i in range(1, n + 1):
    age = input("Введите возраст {}-го пользователя: ".format(i))

    # check input to be a number
    while not age.isdigit() or age.isdigit() and int(age) >= 200:
        age = input(("Неверный ввод. " + ("Введите число" if age.isdigit() else "Введите возраст меньше 200 лет")
            + ". Повторите ввод возраста {}-го пользователя: ").format(i))

    print('user\'s price: ', price(int(age)))
    L.append(int(age))

print('')
if len(L) > 3:
    print("Вы делаете заказ со скидкой. Ваша скидка", totals(L, True))

print('Итоговая сумма заказа =', round(totals(L), 2))