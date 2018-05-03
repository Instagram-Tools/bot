from instapy import InstaPy

import os
import time
from tempfile import gettempdir

from selenium.common.exceptions import NoSuchElementException

import json

print(os.environ)


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
        super().__init__(username=username,
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
        self.settings = env

    def set_settings(self, settings=None):
        env = settings or self.settings

        self.set_blacklist(env.get("blacklist_enabled", True),
                           env.get("blacklist_campaign", ''))
        self.set_comments(env.get("comments", None))
        self.set_do_comment(env.get("do_comment_enabled", False),
                            env.get("do_comment_percentage", 0))
        self.set_do_follow(env.get("do_follow_enabled", False),
                           env.get("do_follow_percentage", 0),
                           env.get("do_follow_times", 1))
        self.set_do_like(env.get("do_like_enabled", False),
                         env.get("do_like_percentage", 0))
        self.set_dont_include(env.get("dont_include", None))
        self.set_dont_like(env.get("dont_like", []))
        self.set_dont_unfollow_active_users(env.get("dont_unfollow_active_users_enabled", False),
                                            env.get("dont_unfollow_active_users_posts", 4))
        self.set_ignore_if_contains(env.get("ignore_if_contains", None))
        self.set_ignore_users(env.get("ignore_users", None))
        self.set_lower_follower_count(env.get("lower_follower_count", None))
        self.set_sleep_reduce(env.get("sleep_reduce", 100))
        self.set_smart_hashtags(env.get("smart_hashtags_tags", None),
                                env.get("smart_hashtags_limit", 3),
                                env.get("smart_hashtags_top", "top"),
                                env.get("smart_hashtags_log_tags", True))
        self.set_use_clarifai(env.get("use_clarifai_enabled", False),
                              env.get("use_clarifai_api_key", None),
                              env.get("use_clarifai_full_match", False))
        self.set_upper_follower_count(env.get("upper_follower_count", None))
        self.set_user_interact(env.get("user_interact_amount", 0),
                               env.get("user_interact_percentage", 100),
                               env.get("user_interact_randomize", False),
                               env.get("user_interact_media", None))

    def act(self):
        env = self.settings or {}

        while True:
            try:
                self.like_by_tags(tags=env.get("like_by_tags", None),
                                  amount=env.get("like_by_tags_amount", 50),
                                  skip_top_posts=env.get("like_by_tags_skip_top_posts", True),
                                  use_smart_hashtags=env.get("like_by_tags_use_smart_hashtags", False),
                                  interact=env.get("like_by_tags_interact", False))

                self.follow_user_followers(env.get("follow_user_followers", []),
                                           amount=env.get("follow_user_followers_amount", 10),
                                           randomize=env.get("follow_user_followers_randomize", False),
                                           interact=env.get("follow_user_followers_interact", False),
                                           sleep_delay=env.get("follow_user_followers_sleep_delay", 600))

                self.unfollow_users(amount=env.get("unfollow_users_amount", 10),
                                    onlyInstapyFollowed=env.get("unfollow_users_onlyInstapyFollowed", True),
                                    onlyInstapyMethod=env.get("unfollow_users_onlyInstapyMethod", 'FIFO'),
                                    sleep_delay=env.get("unfollow_users_sleep_delay", 600),
                                    onlyNotFollowMe=env.get("unfollow_users_onlyNotFollowMe", False),
                                    unfollow_after=env.get("unfollow_users_unfollow_after", None))

            except Exception as exc:
                # if changes to IG layout, upload the file to help us locate the change
                if isinstance(exc, NoSuchElementException):
                    file_path = os.path.join(gettempdir(), '{}.html'.format(time.strftime('%Y%m%d-%H%M%S')))
                    with open(file_path, 'wb') as fp:
                        fp.write(self.browser.page_source.encode('utf8'))
                    print('{0}\nIf raising an issue, please also upload the file located at:\n{1}\n{0}'.format(
                        '*' * 70, file_path))
                # full stacktrace when raising Github issue
