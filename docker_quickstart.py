from instapy import InstaPy

# Write your automation here
# Stuck ? Look at the github page or the examples in the examples folder

from include import Settings

# If you want to enter your Instagram Credentials directly just enter
# username=<your-username-here> and password=<your-password> into InstaPy
# e.g like so InstaPy(username="instagram", password="test1234")

bot = InstaPy(selenium_local_session=False)
bot.set_selenium_remote_session(selenium_url='http://selenium:4444/wd/hub')
bot.login()

Settings.set(bot)

bot.like_by_tags(['#cat', 'dog'], interact=True)
bot.end()
