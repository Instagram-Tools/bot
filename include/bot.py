from instapy import InstaPy

import os
import time
from tempfile import gettempdir

from selenium.common.exceptions import NoSuchElementException


class Bot(InstaPy):
    def act(self):
        try:
            # actions
            self.like_by_tags(['#cat', 'dog'], interact=True)

        except Exception as exc:
            # if changes to IG layout, upload the file to help us locate the change
            if isinstance(exc, NoSuchElementException):
                file_path = os.path.join(gettempdir(), '{}.html'.format(time.strftime('%Y%m%d-%H%M%S')))
                with open(file_path, 'wb') as fp:
                    fp.write(self.browser.page_source.encode('utf8'))
                print('{0}\nIf raising an issue, please also upload the file located at:\n{1}\n{0}'.format(
                    '*' * 70, file_path))
            # full stacktrace when raising Github issue
            raise

        act()
