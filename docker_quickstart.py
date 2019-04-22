import json
import os
import traceback

from selenium import webdriver
from selenium.common.exceptions import WebDriverException

from include import Bot
from include.proxy import get_proxy

# Write your automation here
# Stuck ? Look at the github page or the examples in the examples folder


# If you want to enter your Instagram Credentials directly just enter
# username=<your-username-here> and password=<your-password> into InstaPy
# e.g like so InstaPy(username="instagram", password="test1234")


def selenium_driver(selenium_url):
    mobile_emulation = {"deviceName": "iPhone 6/7/8"}
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
    selenium_driver = webdriver.Remote(command_executor=selenium_url,
                                       desired_capabilities=chrome_options.to_capabilities())
    return selenium_driver


def run():
    global bot
    try:
        bot = Bot(multi_logs=True, selenium_local_session=False,
                  proxy_address_port=get_proxy(os.environ.get('INSTA_USER')))
        selenium_url = "http://%s:%d/wd/hub" % (os.environ.get('SELENIUM', 'selenium'), 4444)
        bot.set_selenium_remote_session(selenium_url=selenium_url, selenium_driver=selenium_driver())
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