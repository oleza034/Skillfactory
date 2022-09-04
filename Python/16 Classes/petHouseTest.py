from petHouse import Animal, Cat, Client

cat = Cat('сибирская кошка', 'мальчик', 'Сэм', 2)
dog = Animal('собака', 'питбуль', 'мальчик', 'Феликс', 3)

print('Животные:')
print(*cat.getCard(), sep = ', ')
print(*dog.getCard(), sep = ', ')
print('=' * 30)

clients = []
clients.append(Client('Иван', 'Иванов', 'Вологда', 410))
clients.append(Client('Василий', 'Бук', 'Иркутск', 860))
clients.append(Client('Мария', 'Петрова', 'Казань', 760))
clients.append(Client('Екатерина', 'Давыдова', 'Москва', 550))
clients.append(Client('Юрий', 'Юров', 'Мурманск', 280))
clients.append(Client('Нина', 'Мартынова', 'Новгород', 170))
clients.append(Client('Виктор', 'Цой', 'Новосибирск', 230))
print('Клиенты (полный список):')
print(*clients, sep='\n')
print('=' * 30)

print('Клиенты (кратко):')
for client in clients:
    print(client.getName())