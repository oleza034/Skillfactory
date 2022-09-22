import requests, json
from config import keys


class APIException(Exception):
    pass


class CryptoConverter:
    @classmethod
    def code_name(cls, currency: str) -> list:
        """
            reads the <currency> argument from the keys dictionary and returns currency code and name
        """
        if currency.lower() in keys.keys(): # do not take keys or values from input: take from dict
            k = list(keys.keys())[list(keys.keys()).index(currency.lower())]
            return [k, keys[k]]
        elif currency.upper() in keys.values():
            k = list(keys.keys())[list(keys.values()).index(currency.upper())]
            return [k, keys[k]]
        else:
            raise KeyError


    @staticmethod
    def read_msgs(msgs: list):
        if type(msgs) != list or len(msgs) != 3:
            raise APIException('Неверное число аргументов')
        quote, base, amount = msgs

        try:
            quote, quote_ticker = CryptoConverter.code_name(quote)
        except KeyError:
            raise APIException(f'Не удалось обработать валюту: {quote}')

        try:
            base, base_ticker = CryptoConverter.code_name(base)
        except KeyError:
            raise APIException(f'Не удалось обработать валюту: {base}')

        if quote == base:
            raise APIException(f'Нельзя конвертировать в себя: {base}.')

        try:
            amount1 = float(amount)
            if amount <= 0:
                raise APIException(f'Количество валюты должно быть больше нуля: {amount}')
        except ValueError:
            raise APIException(f'Не удалось обработать количество: {amount}')

        return quote, base, amount1, quote_ticker, base_ticker


    @staticmethod
    def get_price(quote_ticker: str, base_ticker: str, amount: float) -> float:
        """
        Gets ratio base to quote. Check all parameters with read_msgs
        """
        r = requests.get(f'https://min-api.cryptocompare.com/data/price?fsym={quote_ticker}&tsyms={base_ticker}')
        return round(amount * json.loads(r.content)[base_ticker], 5)
