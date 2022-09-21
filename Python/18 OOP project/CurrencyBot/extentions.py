import requests, json
from config import keys


class APIException(Exception):
    pass


class CryptoConverter:
    @classmethod
    def currency_code(cls, currency: str) -> str:
        """
            reads the <currency> argument from the keys dictionary and returns currency code
        """
        if currency.lower() in keys.keys():
            return keys[currency.lower()]
        elif currency.upper() in keys.values():
            return list(keys.values())[list(keys.values()).index(currency.upper())]
        else:
            raise KeyError


    @staticmethod
    def get_price(quote: str, base: str, amount: str):
        try:
            quote_ticker = CryptoConverter.currency_code(quote)
        except KeyError:
            raise APIException(f'Не удалось обработать валюту: {quote}')

        try:
            base_ticker = CryptoConverter.currency_code(base)
        except KeyError:
            raise APIException(f'Не удалось обработать валюту: {base}')

        if quote_ticker == base_ticker:
            raise APIException(f'Нельзя конвертировать в себя: {base}.')

        try:
            amount = float(amount)
        except ValueError:
            raise APIException(f'Не удалось обработать количество: {amount}')
        r = requests.get(f'https://min-api.cryptocompare.com/data/price?fsym={quote_ticker}&tsyms={base_ticker}')
        return round(amount * json.loads(r.content)[base_ticker], 5)
