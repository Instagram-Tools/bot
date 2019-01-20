import datetime
import json
import os
import random
import time
import traceback
from tempfile import gettempdir

from selenium.common.exceptions import NoSuchElementException

from instapy import InstaPy
from instapy.time_util import sleep

print(os.environ)


def shuffle3(in_list=[]):
    out_list = in_list[:]
    random.shuffle(out_list)
    index = len(out_list) if len(out_list) < 3 else 3
    return out_list[:index]


def parse_datetime_prefix(line, fmt):
    try:
        t = datetime.datetime.strptime(line, fmt)
    except ValueError as v:
        if len(v.args) > 0 and v.args[0].startswith('unconverted data remains: '):
            line = line[:-(len(v.args[0]) - 26)]
            t = datetime.datetime.strptime(line, fmt)
        else:
            raise
    return t


def load_env():
    env = os.environ.get('ENV')
    if not env:
        return {}
    print("env: %s" % env)
    if env[0] == "'":
        env = env[1:]
        print("cut Start: %s" % env)
    if env[-1] == "'":
        env = env[:-1]
        print("cut End: %s" % env)

    env1 = json.loads(env)
    print("rep: %s" % env1)
    env_join = json.loads(" ".join(env1))
    print("env_json: %s" % env_join)
    env_json_join = json.loads(env_join)
    print("env_json_join: %s" % env_json_join)
    return clean_settings(env_json_join)


def clean_settings(settings={}):
    for key in settings:
        if type(settings[key]) == str:
            try:
                settings[key] = int(settings[key])
            except:
                print("String in: {%s: %s} " % (key, settings[key]))

    return settings


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
                 proxy_port=None,
                 multi_logs=False,
                 env=load_env(),
                 proxy_address_port=None):

        if proxy_address_port:
            p_address = proxy_address_port.split(":")[0]
            p_port = int(proxy_address_port.split(":")[1])
        else:
            p_address = proxy_address
            p_port: int = proxy_port

        if p_address and p_port:
            proxy_login: str = env.get("proxy_login")
            proxy_password: str = env.get("proxy_password")
            if proxy_login and proxy_password:
                from proxy_extension import create_proxy_extension
                proxy = proxy_login + ':' + proxy_password + '@' + p_address + ':' + p_port
                proxy_chrome_extension = create_proxy_extension(proxy)

                proxy_address = None
                proxy_port = None
            else:
                proxy_address = p_address
                proxy_port = p_port

        self.settings = env
        self.end_time = parse_datetime_prefix(
            str(env.get("end_time", datetime.datetime.now() + datetime.timedelta(hours=1))), '%Y-%m-%d %H:%M:%S')
        os.environ["INSTA_USER"] = username or os.environ.get('INSTA_USER')
        os.environ["INSTA_PW"] = password or os.environ.get('INSTA_PW')

        print(
            "super().init(username=%s, password=%s, nogui=%s, selenium_local_session=%s, use_firefox=%s, page_delay=%s, show_logs=%s, headless_browser=%s, proxy_address=%s, proxy_chrome_extension=%s, proxy_port=%s, disable_image_load=%s, multi_logs=%s)"
            % (
                os.environ["INSTA_USER"],
                os.environ["INSTA_PW"],
                nogui,
                selenium_local_session,
                use_firefox,
                page_delay,
                show_logs,
                headless_browser,
                proxy_address,
                proxy_chrome_extension,
                proxy_port,
                True,
                multi_logs))
        super().__init__(username=os.environ["INSTA_USER"],
                         password=os.environ["INSTA_PW"],
                         nogui=nogui,
                         selenium_local_session=selenium_local_session,
                         use_firefox=use_firefox,
                         page_delay=page_delay,
                         show_logs=show_logs,
                         headless_browser=headless_browser,
                         proxy_address=proxy_address,
                         proxy_chrome_extension=proxy_chrome_extension,
                         proxy_port=proxy_port,
                         disable_image_load=True,
                         multi_logs=multi_logs)

    def set_settings(self, settings=None):
        if self.aborting:
            return

        env = settings or self.settings

        self.set_blacklist(env.get("blacklist_enabled", True),
                           env.get("blacklist_campaign", ''))
        self.set_comments(env.get("comments", []))

        delimit_liking_max = env.get('delimit_liking_max')
        delimit_liking_min = env.get('delimit_liking_min')
        self.set_delimit_liking(enabled=delimit_liking_max or delimit_liking_min,
                                max=delimit_liking_max,
                                min=delimit_liking_min)

        delimit_commenting_max = env.get('delimit_commenting_max')
        delimit_commenting_min = env.get('delimit_commenting_min')
        self.set_delimit_commenting(enabled=delimit_commenting_max or delimit_commenting_min,
                                    max=delimit_commenting_max,
                                    min=delimit_commenting_min)
        self.set_do_comment(enabled=env.get("do_comment_enabled", True) and len(env.get("comments", [])),
                            percentage=env.get("do_comment_percentage", 0))
        self.set_do_follow(env.get("do_follow_enabled", True),
                           env.get("do_follow_percentage", 0),
                           env.get("do_follow_times", 1))
        self.set_do_like(env.get("do_like_enabled", True),
                         env.get("do_like_percentage", 100))
        self.set_dont_include(set(env.get("dont_include", [])))
        self.set_dont_like(env.get("dont_like", []))
        self.set_dont_unfollow_active_users(env.get("dont_unfollow_active_users_enabled", False),
                                            env.get("dont_unfollow_active_users_posts", 4))
        self.set_ignore_if_contains(env.get("ignore_if_contains", None))
        self.set_ignore_users(env.get("ignore_users", None))
        self.set_relationship_bounds(enabled=env.get("relationship_bounds_enabled", False),
                                     potency_ratio=env.get("relationship_bounds_potency_ratio", None),
                                     delimit_by_numbers=env.get("relationship_bounds_delimit_by_numbers", True),
                                     max_followers=env.get("relationship_bounds_max_followers", 90000),
                                     max_following=env.get("relationship_bounds_max_following", 66834),
                                     min_followers=env.get("relationship_bounds_min_followers", 35),
                                     min_following=env.get("relationship_bounds_min_following", 27))
        self.set_sleep_reduce(env.get("sleep_reduce", 100))
        self.set_smart_hashtags(env.get("smart_hashtags_tags", []),
                                env.get("smart_hashtags_limit", 3),
                                env.get("smart_hashtags_top", "top"),
                                env.get("smart_hashtags_log_tags", True))
        self.set_use_clarifai(env.get("use_clarifai_enabled", False),
                              env.get("use_clarifai_api_key", None),
                              env.get("use_clarifai_full_match", False))
        self.set_user_interact(env.get("user_interact_amount", 3),
                               env.get("user_interact_percentage", 100),
                               env.get("user_interact_randomize", False),
                               env.get("user_interact_media", None))
        self.logger.warning("SETTINGS: %s" % env)

    def act(self):
        if self.aborting:
            return

        actions = self.get_actions(self.settings or {})

        while datetime.datetime.now() < self.end_time:
            try:
                random.shuffle(actions)
                self.logger.warning("shuffled actions: %s" % list(map(lambda a: a["name"], actions)))
                for f in actions:
                    if self.aborting:
                        self.logger.warning("ABORTING")
                        return

                    self.logger.warning("RUN: %s" % f["name"])
                    f["fun"]()

                sleep(180)

            except NoSuchElementException as exc:
                # if changes to IG layout, upload the file to help us locate the change
                file_path = os.path.join(gettempdir(), '{}.html'.format(time.strftime('%Y%m%d-%H%M%S')))
                with open(file_path, 'wb') as fp:
                    fp.write(self.browser.page_source.encode('utf8'))
                print('{0}\nIf raising an issue, please also upload the file located at:\n{1}\n{0}'.format(
                    '*' * 70, file_path))
                # full stacktrace when raising Github issue
                self.logger.exception(exc)
            except Exception as exc:
                self.logger.error("Excepiton in act(): %s \n %s" % (exc, traceback.format_exc()))
                raise
                # TODO send Mail to Developers

    def get_actions(self, env):
        actions = [
            {
                "name": "like_by_tags",
                "enabled": env.get("enable_like_by_tags", True) and len(env.get("like_by_tags", [])) > 0,
                "fun":
                    lambda: self.like_by_tags(
                        tags=shuffle3(env.get("like_by_tags", [])),
                        amount=env.get("like_by_tags_amount", 3),
                        skip_top_posts=env.get("like_by_tags_skip_top_posts", True),
                        use_smart_hashtags=env.get("like_by_tags_use_smart_hashtags", False),
                        interact=env.get("like_by_tags_interact", False)),
            },
            {
                "name": "like_by_locations",
                "enabled": env.get("enable_like_by_locations", True) and len(env.get("like_by_locations", [])) > 0,
                "fun": lambda: self.like_by_locations(
                    locations=shuffle3(env.get("like_by_locations", [])),
                    amount=env.get("like_by_locations_amount", 3),
                    skip_top_posts=env.get("like_by_locations_skip_top_posts", True))
            },
            {
                "name": "follow_user_followers",
                "enabled": env.get("enable_follow_user_followers", True) and len(env.get("follow_user_followers", [])) > 0,
                "fun": lambda: self.follow_user_followers(
                    usernames=shuffle3(env.get("follow_user_followers", []))[0],
                    amount=random.randint(4, 6),
                    randomize=env.get("follow_user_followers_randomize", True),
                    interact=env.get("follow_user_followers_interact", True),
                    sleep_delay=env.get("follow_user_followers_sleep_delay", 0))
            },
            {
                "name": "like_by_feed",
                "enabled": env.get("enable_like_by_feed", True),
                "fun": lambda: self.like_by_feed(
                    amount=random.randint(8, 12),
                    randomize=env.get("like_by_feed_randomize", True),
                    unfollow=env.get("like_by_feed_unfollow", False),
                    interact=env.get("like_by_feed_interact", False))
            },
            {
                "name": "unfollow_users",
                "enabled": env.get("enable_unfollow", True),
                "fun": lambda: self.unfollow_users(
                    amount=env.get("unfollow_users_amount", random.randint(8, 12)),
                    # customList=(False, [], "all"),
                    InstapyFollowed=(env.get("unfollow_users_InstapyFollowed", True),
                                     "nonfollowers" if env.get("unfollow_users_nonfollowers", False) else "all"),
                    # 'all' or 'nonfollowers'
                    # nonFollowers=False,
                    # allFollowing=False,
                    style=env.get("unfollow_users_style", 'FIFO'),  # or 'LIFO', 'RANDOM'
                    unfollow_after=env.get("unfollow_users_unfollow_after", 2) * 24 * 60 * 60,
                    sleep_delay=env.get("unfollow_users_sleep_delay", 0)
                )
            }
        ]
        return list(filter(lambda a: a["enabled"], actions))
