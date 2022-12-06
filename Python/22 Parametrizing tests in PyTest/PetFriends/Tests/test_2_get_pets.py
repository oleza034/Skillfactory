import pytest
from api import *

class TestGetPets:
    path = 'api/key'
    params = {'filter': 'my_pets'}

    @pytest.mark.parametrize('filter', ['my_pets', '', None])
    def test_positive(self, get_key, filter:str | None):
        if filter == None:
            params = None
        else:
            params = {'filter': str(filter)}
        status_code, headers, body, exec_time = request('GET', self.path, headers=headers)
        assert status_code == 200
        assert 'Content-Type' in headers.keys() and headers['Content-Type'] == 'application/json'
        assert datetime.utcnow() - datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %Z') < timedelta(minutes=1)
        chk_pets(body) # check response structure pets
        assert exec_time <= 1
