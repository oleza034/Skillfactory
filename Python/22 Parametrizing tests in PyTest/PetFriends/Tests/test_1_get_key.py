from api import *
from datetime import timedelta
import urllib.parse


class TestGetKey:
    path = 'api/key'
    params = {'filter': 'my_pets'}


    @pytest.mark.getkey
    @pytest.mark.positive
    @pytest.mark.parametrize('email', [valid_email], ids=['valid email'])
    @pytest.mark.parametrize('password', [valid_password], ids=['valid password'])
    def test_positive(self, email: str, password: str):
        headers = {'email': email, 'password': password, 'accept': 'application/json'}
        status_code, headers, body, exec_time = request('GET', self.path, headers=headers)
        assert status_code == 200
        assert 'Content-Type' in headers.keys() and headers['Content-Type'] == 'application/json'
        assert datetime.utcnow() - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
        assert type(body) == dict and 'key' in body.keys() and type(body['key']) == str and body['key']
        assert exec_time <= 1


    @pytest.mark.getkey
    @pytest.mark.negative
    @pytest.mark.wrong_headers
    @pytest.mark.parametrize('email', [valid_email, '', rnd_str(1, 'l'), rnd_str(255), rnd_str(1024),
                                       rnd_str(15, 's'), rnd_str(15, 'r'), rnd_str(15, 'rga')],
                             ids=['valid_email', 'empty_email', '1_letter_email', '255_letters_email',
                                  '1024_email', 'symbols_email', 'rus_emal', 'ru_gr_ar_email'])
    @pytest.mark.parametrize('password', [valid_password, '', rnd_str(1, 'l'), rnd_str(255), rnd_str(1024),
                                       rnd_str(15, 's'), rnd_str(15, 'r'), rnd_str(15, 'rga')],
                             ids=['valid_pwd', 'empty_pwd', '1_letter_pwd', '255_letters_pwd', '1024_letters_pwd',
                                  'symbols_pwd', 'rus_pwd', 'ru_gr_ar_pwd'])
    def test_wrong_eml_pwd(self, email: str, password: str):
        if email != valid_email or password != valid_password:
            headers = {'email': urllib.parse.quote_plus(email), 'password': urllib.parse.quote_plus(password),
                       'accept': 'application/json', 'Content-Type': 'application/json; charset=utf-8'}
            status, headers, body, exec_time = request('GET', self.path, headers=headers)
            assert status == 403
            assert 'Content-Type' in headers.keys() and headers['Content-Type'] == 'text/html; charset=utf-8'
            assert datetime.utcnow() - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(
                minutes=1)
            assert type(body) == str
            if exec_time < 1:
                assert True
            else:
                print(f'\nWrong response time: {exec_time} sec.\n')


    @pytest.mark.getkey
    @pytest.mark.negative
    @pytest.mark.wrong_ct_type
    @pytest.mark.parametrize('ct_type', ['text/html; application/json; image/jpeg', rnd_str(255), rnd_str(1024),
                                         rnd_str(15, 's'), rnd_str(15, 'r'), rnd_str(15, 'agr')],
                             ids=['multiple', '255_symbols', '1024_symbols', 'special_symbols',
                                  'cyrillic', 'gr_ar_ru_symbols'])
    def test_wrong_ct_type(self, ct_type: str):
        headers = {'email': valid_email, 'password': valid_password, 'accept': 'application/json',
                   'Content-Type': ct_type}
        status, headers, body, exec_time = request('GET', self.path, headers=headers)
        assert status == 415
        assert 'Content-Type' in headers.keys() and headers['Content-Type'] == 'text/html; charset=utf-8'
        assert datetime.utcnow() - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(
            minutes=1)
        assert type(body) == str
        if exec_time < 1:
            assert True
        else:
            print(f'\nWrong response time: {exec_time} sec.\n')


    @pytest.mark.getkey
    @pytest.mark.negative
    @pytest.mark.wrong_method
    @pytest.mark.parametrize('method', ['PUT', 'POST'], ids=['PUT', 'POST'])
    def test_wrong_method(self, method: str):
        headers = {'email': valid_email, 'password': valid_password, 'accept': 'application/json'}
        status, headers, body, exec_time = request(method, self.path, headers=headers)
        assert status == 405
        assert 'Content-Type' in headers.keys() and headers['Content-Type'] == 'text/html; charset=utf-8'
        assert datetime.utcnow() - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(
            minutes=1)
        assert type(body) == str
        if exec_time < 1:
            assert True
        else:
            print(f'\nWrong response time: {exec_time} sec.\n')
