import os

from include import Bot

# Write your automation here
# Stuck ? Look at the github page or the examples in the examples folder


# If you want to enter your Instagram Credentials directly just enter
# username=<your-username-here> and password=<your-password> into InstaPy
# e.g like so InstaPy(username="instagram", password="test1234")

bot = Bot(multi_logs=True, selenium_local_session=False)
bot.set_selenium_remote_session(
    selenium_url="http://%s:%d/wd/hub" % (os.environ.get('SELENIUM', 'selenium'), 4444))
bot.login()
bot.set_settings()

bot.act()

bot.end()
