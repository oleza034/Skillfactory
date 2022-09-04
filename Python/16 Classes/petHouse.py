class Animal:
    def __init__(self, species, breed, gender, name, age):
        self.species = species
        self.breed = breed
        self.gender = gender
        self.name = name
        self.age = age

    def getCard(self):
        return [self.species, self.breed, self.gender, self.name, self.age]


class Cat(Animal):
    def __init__(self, breed, gender, name, age):
        self.species = 'кошка'
        self.breed = breed
        self.gender = gender
        self.name = name
        self.age = age


class Client:
    def __init__(self, name, family, town, money):
        self.name = name
        self.family = family
        self.town = town
        self.money = money

    def __str__(self):
        return f'{self.name} {self.family}. {self.town}. Баланс: {self.money}'

    def getName(self):
        return f'{self.name} {self.family}, {self.town}'
