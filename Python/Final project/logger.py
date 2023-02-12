import os
import pickle
from datetime import datetime
from pathlib import Path


class Logger(object):
    def __init__(self, file_name: str, wipe_data = True):
        self.path = os.path.dirname(os.path.join(os.path.dirname(__file__), file_name))
        self.file_name = os.path.join(os.path.dirname(__file__), file_name)

        path = Path(self.path)
        path.mkdir(parents=True, exist_ok=True)

        if wipe_data and os.path.exists(self.file_name):
            os.remove(self.file_name)

    def append(self, log: str):
        if self.file_name:
            try:
                with open(self.file_name, 'a', encoding='utf-8') as f:
                    f.write(''.join(('\n', datetime.utcnow().strftime('%m/%d/%Y, %H:%M:%S.%f'), ' ', log)))
                    f.close()
            except:
                pass


class MyCookies:
    def __init__(self, file_name: str, cookies=None):
        self.file_name = file_name
        if cookies:
            try:
                with open(file_name, 'wb') as f:
                    pickle.dump(cookies, f)
                    f.close()
                self.cookies = cookies
            except Exception:
                self.cookies = None
        elif file_name:
            if os.path.exists(file_name):
                try:
                    with open(file_name, 'rb') as f:
                        self.cookies = pickle.load(f)
                        f.close()
                except:
                    self.cookies = None
        else:
            self.cookies = None


    def get_cookies(self):
        try:
            with open(self.file_name, 'rb') as f:
                self.cookies = pickle.load(f)
                f.close()
        except Exception:
            self.cookies = None
        return self.cookies

    def set_cookies(self, cookies: None):
        self.__init__(cookies)