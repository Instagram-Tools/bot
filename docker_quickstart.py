import json
import os
import traceback

from selenium.common.exceptions import WebDriverException

from include import Bot
from include.proxy import get_proxy

# Write your automation here
# Stuck ? Look at the github page or the examples in the examples folder


# If you want to enter your Instagram Credentials directly just enter
# username=<your-username-here> and password=<your-password> into InstaPy
# e.g like so InstaPy(username="instagram", password="test1234")


def run():
    global bot
    try:
        bot = Bot(multi_logs=True, selenium_local_session=False,
                  proxy_address_port=get_proxy(os.environ.get('INSTA_USER')))
        bot.set_selenium_remote_session(
            selenium_url="http://%s:%d/wd/hub" % (os.environ.get('SELENIUM', 'selenium'), 4444))
        bot.login()
        bot.set_settings()
        bot.act()
    except WebDriverException as wde:
        print("WebDriverException in run(): %s \n%s" % (wde, wde.stacktrace))
    except Exception as exc:
        print("Exception in run(): %s \n %s" % (exc, traceback.format_exc()))

        email = os.environ.get("DEV_EMAIL")
        email_api = os.environ.get("EMAIL_API")
        if email and email_api:
            import requests
            requests.post("%s/mail/" % email_api,
                          json.dumps({"username": "ERROR", "email": email,
                                      "subject": "Something went wrong with %s " % os.environ.get('INSTA_USER',
                                                                                                  'UnknownUser'),
                                      "body": "Excepiton in act(): %s \n %s" % (exc, traceback.format_exc()),
                                      "once": True
                                      }))
    finally:
        bot.end()

run()