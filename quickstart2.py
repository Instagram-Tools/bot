import os
import time
from tempfile import gettempdir

from include import Bot
from env import insta_username, insta_password, settings
from selenium.common.exceptions import NoSuchElementException

# set headless_browser=True if you want to run InstaPy on a server

# set these in instapy/settings.py if you're locating the
# library in the /usr/lib/pythonX.X/ directory:
#   Settings.database_location = '/path/to/instapy.db'
#   Settings.chromedriver_location = '/path/to/chromedriver'

bot = Bot(username=insta_username,
          password=insta_password,
          headless_browser=False,
          multi_logs=True,
          disable_image_load=False,
          env=settings)

try:
    bot.login()

    bot.set_settings()

    bot.act()

except Exception as exc:
    # if changes to IG layout, upload the file to help us locate the change
    if isinstance(exc, NoSuchElementException):
        file_path = os.path.join(gettempdir(), '{}.html'.format(time.strftime('%Y%m%d-%H%M%S')))
        with open(file_path, 'wb') as fp:
            fp.write(bot.browser.page_source.encode('utf8'))
        print('{0}\nIf raising an issue, please also upload the file located at:\n{1}\n{0}'.format(
            '*' * 70, file_path))
    # full stacktrace when raising Github issue
    raise

finally:
    # end the bot session
    print("END")
    # bot.end()
