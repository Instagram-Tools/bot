import datetime
import json
import os
import random
import time
import traceback
from http.client import RemoteDisconnected
from tempfile import gettempdir

from selenium.common.exceptions import NoSuchElementException
from urllib3.exceptions import ProtocolError, MaxRetryError

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
    if env[0] == "'":
        env = env[1:]
    if env[-1] == "'":
        env = env[:-1]

    env1 = json.loads(env)
    if type(env1) is dict:
        return env1
    env_join = json.loads(" ".join(env1))
    if type(env_join) is dict:
        return env_join
    return json.loads(env_join)


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
                 proxy_address_port=None,
                 bypass_suspicious_attempt=False,
                 bypass_with_mobile=False,
                 disable_image_load=True
                 ):

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

        self.settings = clean_settings(env)
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
                         disable_image_load=disable_image_load,
                         bypass_security_challenge_using='sms',
                         multi_logs=multi_logs)
        self.logger.info("Settings: %s" % self.settings)

    def login(self, count=0):
        try:
            super().login()

            if self.aborting:
                self.aborting = False
                self.bypass_suspicious_attempt = True
                self.logger.warning("bypass_suspicious_attempt with Code: %s" % os.environ.get("SEC_CODE"))
                super().login()

            if self.aborting:
                self.send_mail_wrong_login_data()

        except (ConnectionRefusedError, RemoteDisconnected) as exc:
            return self.try_again(count, exc)

    def try_first_login(self, count=0):
        try:
            self.logger.warning("Try first login: \n%s\n%s" % (self.username, self.password))
            super().login()

            if self.aborting:
                self.aborting = False
                self.bypass_suspicious_attempt = True
                self.logger.warning("bypass_suspicious_attempt with Code: %s" % os.environ.get("SEC_CODE"))
                super().login()


            if self.aborting:
                email = os.environ.get("EMAIL", "")
                self.send_mail(mail_subject="Welcome to Pink Parrot!",
                               mail_body="Unfortunately Pink Parrot wasn\'t able to log-in to your account. Please "
                                         "help us to solve this problem. Go to this url: \n"
                                         "https://pinkparrot.co/insta_verify/?email=%s&username=%s"
                                         "\n\nThank you and enjoy our service!" % (email, self.username))
                self.send_stop_bot()

            else:
                self.send_mail(mail_subject="Welcome to Pink Parrot!",
                               mail_body="Congratulations and welcome to Pink Parrot! We successfully connected to "
                                         "your Instagram account and will now start interacting with your target "
                                         "groups! Now lean back and let us do the work! :)\n\nP.S.: Please make "
                                         "sure your Instagram 2-factor-authorization is switched off, as our service "
                                         "might have problems logging in to your account. ")
                self.send_start_bot()


        except (ConnectionRefusedError, RemoteDisconnected) as exc:
            return self.try_again(count, exc)

    def send_stop_bot(self):
        try:
            api = os.environ.get("API")
            if api:
                import requests
                url = "%s/api/bot/stop/%s" % (api, self.username)
                get = requests.get(url)
                self.logger.warning("GET %s" % url)
            else:
                self.logger.warning("API missing, failed: send_stop_bot")
        except Exception as exc:
            print("Exception in send_stop_bot(): %s \n %s" % (exc, traceback.format_exc()))

    def send_start_bot(self):
        try:
            api = os.environ.get("API")
            if api:
                import requests
                url = "%s/api/bot/start/%s" % (api, self.username)
                get = requests.get(url)
                self.logger.warning("GET %s" % url)
            else:
                self.logger.warning("API missing, failed: send_stop_bot")
        except Exception as exc:
            print("Exception in send_start_bot(): %s \n %s" % (exc, traceback.format_exc()))

    def deal_with_block(self, action="like"):
        super().deal_with_block(action=action)

        from instapy.util import dump_record_activity
        activity = dump_record_activity(self.username,
                                        self.logger,
                                        self.logfolder)
        email = os.environ.get("DEV_EMAIL")
        self.send_mail(mail_subject="%s Block: %s" % (action, self.username), mail_body=activity, email=email)

    def send_mail(self, mail_subject, mail_body, email=os.environ.get("EMAIL")):
        try:
            api = os.environ.get("API")
            if email and api:
                import requests
                post = requests.post("%s/api/mail/" % api,
                                     json.dumps({"username": self.username, "password": self.password, "email": email,
                                                 "subject": mail_subject,
                                                 "body": mail_body,
                                                 "once": True
                                                 }))
                self.logger.warning("send_mail(%s, %s, %s)" % (mail_subject, mail_body, email))
            else:
                self.logger.warning("failed: send_mail(%s, %s, %s)" % (mail_subject, mail_body, email))
        except Exception as exc:
            print("Exception in send_mail(): %s \n %s" % (exc, traceback.format_exc()))

    def send_mail_wrong_login_data(self):
        print("Send Mail for %s" % self.username)
        email = os.environ.get("EMAIL", "")
        self.send_mail(
            mail_subject="Action needed! Pink Parrot can NOT operate.",
            mail_body='Hey, this is the team of Pink Parrot.\n'
                      'We had a problem logging in to your Instagram account. Please help us to '
                      'solve this problem by doing one of the following actions:'
                      '\n 1. If you recently changed your Instagram name or password, please visit the Pink Parrot '
                      'settings page, correct them and press save.'
                      '\n 2. If you open Instagram and they require you to enter your phone number, please do so.'
                      '\n 3. If Instagram asks you whether the '
                      'last log-in was you, please confirm that it was you. By doing so, you allow our '
                      'service to interact in the name of your account.'
                      '\n 4. If Instagram e-mailed you a verification code as the result of an untypical login attempt,'
                      'please click the following link and follow its instructions:'
                      '\n https://pinkparrot.co/insta_verify/?email=%s&username=%s'
                      '\n\nThank you and enjoy our service :-)' % (email, self.username))

        self.send_stop_bot()

    def set_settings(self, settings=None):
        if self.aborting:
            return

        env = settings or self.settings

        self.set_simulation(enabled=True, percentage=66)
        self.set_blacklist(env.get("blacklist_enabled", True),
                           env.get("blacklist_campaign", ''))
        self.set_comments(self.encode_comments(env.get("comments", [])))

        delimit_liking_max = env.get('delimit_liking_max')
        delimit_liking_min = env.get('delimit_liking_min')
        self.set_delimit_liking(enabled=delimit_liking_max or delimit_liking_min,
                                max_likes=delimit_liking_max,
                                min_likes=delimit_liking_min)

        delimit_commenting_max = env.get('delimit_commenting_max')
        delimit_commenting_min = env.get('delimit_commenting_min')
        self.set_delimit_commenting(enabled=delimit_commenting_max or delimit_commenting_min,
                                    max_comments=delimit_commenting_max,
                                    min_comments=delimit_commenting_min)
        self.set_do_comment(enabled=env.get("do_comment_enabled", True) and len(env.get("comments", [])),
                            percentage=30)
        self.set_do_follow(enabled=env.get("do_follow_enabled", True),
                           percentage=65,
                           times=env.get("do_follow_times", 1))
        self.set_do_like(enabled=env.get("do_like_enabled", True),
                         percentage=40)
        self.set_dont_include(set(env.get("dont_include", [])))
        self.set_dont_like(env.get("dont_like", []))
        self.set_dont_unfollow_active_users(env.get("dont_unfollow_active_users_enabled", False),
                                            env.get("dont_unfollow_active_users_posts", 4))
        self.set_ignore_if_contains(env.get("ignore_if_contains", []))
        self.set_ignore_users(env.get("ignore_users", []))
        self.set_relationship_bounds(enabled=env.get("relationship_bounds_enabled", True),
                                     potency_ratio=env.get("relationship_bounds_potency_ratio", None),
                                     delimit_by_numbers=env.get("relationship_bounds_delimit_by_numbers", True),
                                     max_followers=env.get("relationship_bounds_max_followers", 90000),
                                     max_following=env.get("relationship_bounds_max_following", 66834),
                                     min_followers=env.get("relationship_bounds_min_followers", 35),
                                     min_following=env.get("relationship_bounds_min_following", 27))
        self.set_sleep_reduce(env.get("speed", 100))
        self.set_smart_hashtags(env.get("smart_hashtags_tags", []),
                                env.get("smart_hashtags_limit", 3),
                                env.get("smart_hashtags_top", "top"),
                                env.get("smart_hashtags_log_tags", True))
        self.set_use_clarifai(env.get("use_clarifai_enabled", False),
                              env.get("use_clarifai_api_key", None),
                              env.get("use_clarifai_full_match", False))
        self.set_user_interact(amount=random.randint(5, 10),
                               percentage=env.get("user_interact_percentage", 80),
                               randomize=env.get("user_interact_randomize", False),
                               media=env.get("user_interact_media", None))
        self.set_quota_supervisor(enabled=True,
                                  sleepyhead=True, stochastic_flow=True, notify_me=True,
                                  peak_likes_hourly=50,
                                  peak_likes_daily=700,
                                  peak_comments_hourly=50,
                                  peak_comments_daily=None,
                                  peak_follows_hourly=40,
                                  peak_follows_daily=500,
                                  peak_unfollows_hourly=50,
                                  peak_server_calls_hourly=None,
                                  peak_server_calls_daily=None)
        self.set_do_story(enabled=True, percentage=70, simulate=True)
        self.logger.warning("SETTINGS: %s" % env)

    def encode_comments(self, comments):
        return list(map(lambda c: u'%s' % c, comments))

    def act(self, count=0):
        if self.aborting:
            return

        actions = self.get_actions(self.settings or {})

        while datetime.datetime.now() < self.end_time:
            try:
                self.shuffle_actions(actions)
                self.logger.warning("shuffled actions: %s" % list(map(lambda a: a["name"], actions)))
                for f in actions:
                    if self.aborting:
                        self.logger.warning("ABORTING")
                        return

                    self.logger.warning("RUN: %s" % f["name"])
                    f["fun"]()
                    count = 0
                    sleep(1 * 60)

                sleep(2 * 60)

            except NoSuchElementException as exc:
                # if changes to IG layout, upload the file to help us locate the change
                file_path = os.path.join(gettempdir(), '{}.html'.format(time.strftime('%Y%m%d-%H%M%S')))
                with open(file_path, 'wb') as fp:
                    fp.write(self.browser.page_source.encode('utf8'))
                print('{0}\nIf raising an issue, please also upload the file located at:\n{1}\n{0}'.format(
                    '*' * 70, file_path))
                # full stacktrace when raising Github issue
                self.logger.exception(exc)
            except (ConnectionRefusedError, RemoteDisconnected, ProtocolError,
                    MaxRetryError, AttributeError) as exc:
                return self.try_again(count, exc)
            except Exception as exc:
                if 'RemoteDisconnected' in str(exc):
                    return self.try_again(count, exc)

                self.logger.error("Excepiton in act(): %s \n %s" % (exc, traceback.format_exc()))
                raise

    def try_again(self, count, exc):
        self.logger.warning("Exception in act: %s; try again: count=%s" % (exc, count))
        if count > 3:
            raise
        else:
            self.act(count=count + 1)

    def shuffle_actions(self, actions):
        if len(actions) <= 1:
            sleep(7 * 60)
            return actions

        old_order = actions[:]
        random.shuffle(actions)

        if actions[0] == old_order[-1]:
            actions = actions[1:] + actions[0:1]
        return actions

    def get_actions(self, env):
        actions = [
            {
                "name": "like_by_tags",
                "enabled": self.do_like and env.get("enable_like_by_tags", True) and len(
                    env.get("like_by_tags", [])) > 0,
                "fun":
                    lambda: self.like_by_tags(
                        tags=shuffle3(env.get("like_by_tags", [])),
                        amount=random.randint(2, 4),
                        skip_top_posts=env.get("like_by_tags_skip_top_posts", True),
                        use_smart_hashtags=env.get("like_by_tags_use_smart_hashtags", False),
                        interact=True),
            },
            {
                "name": "story_by_tags",
                "enabled": env.get("story_by_tags", False) and len(
                    env.get("like_by_tags", [])) > 0,
                "fun":
                    lambda: self.story_by_tags(
                        tags=shuffle3(env.get("like_by_tags", [])),
                    ),
            },
            {
                "name": "join_pods",
                "enabled": env.get("join_pods", False) and len(
                    env.get("like_by_tags", [])) > 0,
                "fun":
                    lambda: self.join_pods(
                        topic=env.get("join_pods_topic", "general"),
                        engagement_mode=env.get("join_pods_engagement_mode", "normal")
                    ),
            },
            {
                "name": "like_by_locations",
                "enabled": self.do_like and env.get("enable_like_by_locations", True) and len(
                    env.get("like_by_locations", [])) > 0,
                "fun": lambda: self.like_by_locations(
                    locations=shuffle3(env.get("like_by_locations", [])),
                    amount=random.randint(2, 4),
                    skip_top_posts=env.get("like_by_locations_skip_top_posts", True))
            },
            {
                "name": "comment_by_locations",
                "enabled": self.do_comment and env.get("enable_like_by_locations", True) and len(
                    env.get("like_by_locations", [])) > 0,
                "fun": lambda: self.like_by_locations(
                    locations=shuffle3(env.get("like_by_locations", [])),
                    amount=random.randint(15, 30),
                    skip_top_posts=env.get("like_by_locations_skip_top_posts", True))
            },
            {
                "name": "follow_user_followers",
                "enabled": env.get("enable_follow_user_followers", True) and len(
                    env.get("follow_user_followers", [])) > 0,
                "fun": lambda: self.follow_user_followers(
                    usernames=shuffle3(env.get("follow_user_followers", []))[0],
                    amount=random.randint(2, 4),
                    randomize=env.get("follow_user_followers_randomize", True),
                    interact=True,
                    sleep_delay=env.get("follow_user_followers_sleep_delay", 0))
            },
            {
                "name": "interact_by_comments",
                "enabled": env.get("enable_interact_by_comments", True) and env.get("enable_follow_user_followers",
                                                                                    True) and len(
                    env.get("follow_user_followers", [])) > 0,
                "fun": lambda: self.interact_by_comments(
                    usernames=shuffle3(env.get("follow_user_followers", []))[0],
                    posts_amount=random.randint(2, 4),
                    comments_per_post=random.randint(2, 4),
                    reply=False, interact=True,
                    randomize=True, media=None)
            },
            {
                "name": "unfollow_users",
                "enabled": env.get("enable_unfollow", True),
                "fun": lambda: self.unfollow_users(
                    amount=random.randint(8, 12),
                    instapy_followed_enabled=True,
                    instapy_followed_param="all",
                    # 'all' or 'nonfollowers'
                    # nonFollowers=False,
                    # allFollowing=False,
                    style=env.get("unfollow_users_style", 'FIFO'),  # or 'LIFO', 'RANDOM'
                    unfollow_after=(env.get("unfollow_users_unfollow_after", 2) if env.get(
                        "unfollow_users_unfollow_after", 2) > 0 else 1) * 24 * 60 * 60,
                    sleep_delay=env.get("unfollow_users_sleep_delay", 0)
                )
            }
        ]
        return list(filter(lambda a: a["enabled"], actions))
