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
    prices = {
        (0, 18): 0, # 1st age from 0 to 18: for free
        (18, 25): 990, # 2nd age from 18 to 25: discount
        (25, 200): 1390 # 3rd age older than 25: full price
    }
    
    price = None

    for a in prices.keys():
        if a[0] <= guest_age < a[1]:
            price = prices[a]

    return price


# order totals
def totals(guests_list: list, return_discount=False):
    '''
    Returns total price for the order
    :param guests_list: list of guest ages
    :param discount: True if you want to get just discount; False for order totals
    :return: total price for the order or the sum of discount value, if requested
    '''
    total_sum = 0
    discount = len(guests_list) > 3
    
    for a in guests_list: # take all guests ages
        if discount and return_discount:
            total_sum += price(a) * 0.1
        elif discount:
            total_sum += price(a) * 0.9
        elif not return_discount:
            total_sum += price(a)
            
    return total_sum


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
        age = input(("Неверный ввод. " + ("Введите возраст меньше 200 лет" if age.isdigit() else "Введите число")
            + ". Повторите ввод возраста {}-го пользователя: ").format(i))

    # print('user\'s price: ', price(int(age)))
    L.append(int(age))

print('')
if len(L) > 3:
    print("Вы делаете заказ со скидкой. Ваша скидка", totals(L, True))

print('Итоговая сумма заказа =', round(totals(L), 2))