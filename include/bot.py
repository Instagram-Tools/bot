from instapy import InstaPy

import os
import time
from tempfile import gettempdir

from selenium.common.exceptions import NoSuchElementException

import json


class Bot(InstaPy):
    def __init__(self,
                 username=None,
                 password=None,
                 nogui=False,
                 selenium_local_session=True,
                 use_firefox=False,
                 page_delay=25,
                 show_logs=True,
                 headless_browser=False,
                 proxy_address=None,
                 proxy_chrome_extension=None,
                 proxy_port=0,
                 bypass_suspicious_attempt=False,
                 multi_logs=False,
                 env=json.loads(os.environ.get('ENV', '{}'))):
        super().__init__(self,
                         username=username,
                         password=password,
                         nogui=nogui,
                         selenium_local_session=selenium_local_session,
                         use_firefox=use_firefox,
                         page_delay=page_delay,
                         show_logs=show_logs,
                         headless_browser=headless_browser,
                         proxy_address=proxy_address,
                         proxy_chrome_extension=proxy_chrome_extension,
                         proxy_port=proxy_port,
                         bypass_suspicious_attempt=bypass_suspicious_attempt,
                         multi_logs=multi_logs)
        self.env = env

    def settings(self):
        self.set_blacklist(self.env.get("blacklist_enabled", True),
                           self.env.get("blacklist_campaign", ''))
        self.set_comments(self.env.get("comments", None))
        self.set_do_comment(self.env.get("do_comment_enabled", False),
                            self.env.get("do_comment_percentage", 0))
        self.set_do_follow(self.env.get("do_follow_enabled", False),
                           self.env.get("do_follow_percentage", 0),
                           self.env.get("do_follow_times", 1))
        self.set_do_like(self.env.get("do_like_enabled", False),
                         self.env.get("do_like_percentage", 0))
        self.set_dont_include(self.env.get("dont_include", None))
        self.set_dont_like(self.env.get("dont_like", None))
        self.set_dont_unfollow_active_users(self.env.get("dont_unfollow_active_users_enabled", False),
                                            self.env.get("dont_unfollow_active_users_posts", 4))
        self.set_ignore_if_contains(self.env.get("ignore_if_contains", None))
        self.set_ignore_users(self.env.get("ignore_users", None))
        self.set_lower_follower_count(self.env.get("lower_follower_count", None))
        self.set_sleep_reduce(self.env.get("sleep_reduce", 100))
        self.set_smart_hashtags(self.env.get("smart_hashtags_tags", None),
                                self.env.get("smart_hashtags_limit", 3),
                                self.env.get("smart_hashtags_top", "top"),
                                self.env.get("smart_hashtags_log_tags", True))
        self.set_use_clarifai(self.env.get("use_clarifai_enabled", False),
                              self.env.get("use_clarifai_api_key", None),
                              self.env.get("use_clarifai_full_match", False))
        self.set_upper_follower_count(self.env.get("upper_follower_count", None))
        self.set_user_interact(self.env.get("user_interact_amount", 0),
                               self.env.get("user_interact_percentage", 100),
                               self.env.get("user_interact_randomize", False),
                               self.env.get("user_interact_media", None))

    def act(self):
        while True:
            try:
                """Different tasks"""
                # you can put in as much tags as you want, likes 100 of each tag
                self.like_by_tags(['cat', 'funnycat', 'cutecat'], amount=10, interact=True)

                # For 50% of the 30 newly followed, move to their profile
                # and randomly choose 5 pictures to be liked.
                # Take into account the other set options like the comment rate
                # and the filtering for inappropriate words or users

                # default sleep_delay=600 (10min) for every 10 user following, in this case sleep for 60 seconds
                self.follow_user_followers(['cats_of_instagram'], amount=10, randomize=False, interact=True,
                                           sleep_delay=60)

                self.unfollow_users(onlyInstapyFollowed=True, unfollow_after=48 * 60 * 60,
                                    amount=10)  # unfollows 10 of the accounts your following -> instagram will only unfollow 10 before you'll be 'blocked
                #  for 10 minutes' (if you enter a higher number than 10 it will unfollow 10, then wait 10 minutes and will continue then)

            except Exception as exc:
                # if changes to IG layout, upload the file to help us locate the change
                if isinstance(exc, NoSuchElementException):
                    file_path = os.path.join(gettempdir(), '{}.html'.format(time.strftime('%Y%m%d-%H%M%S')))
                    with open(file_path, 'wb') as fp:
                        fp.write(self.browser.page_source.encode('utf8'))
                    print('{0}\nIf raising an issue, please also upload the file located at:\n{1}\n{0}'.format(
                        '*' * 70, file_path))
                # full stacktrace when raising Github issue
