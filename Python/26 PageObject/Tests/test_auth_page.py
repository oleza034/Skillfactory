from Pages.auth_page import AuthPage
from settings import valid_email, valid_password


def test_auth_page(selenium):
    page = AuthPage(selenium)
    print(f'\nDEBUG:\nemail: \'{valid_email}\',\npass: \'{valid_password}\'')
    page.enter_email(valid_email)
    page.enter_password(valid_password)
    page.btn_click()

    assert page.get_relative_link() == '/all_pets', 'login error'
