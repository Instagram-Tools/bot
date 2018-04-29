from instapy import InstaPy

import os
import time
from tempfile import gettempdir

from selenium.common.exceptions import NoSuchElementException


class Bot(InstaPy):
    def settings(self):
        self.set_upper_follower_count(limit=500)

        """Comment util"""
        # default enabled=False, ~ every 4th image will be commented on
        self.set_do_comment(enabled=True, percentage=25)
        self.set_comments(['Awesome', 'Really Cool', 'I like your stuff'])
        # you can also set comments for specific media types (Photo / Video)
        self.set_comments(['Nice shot!'], media='Photo')
        self.set_comments(['Great Video!'], media='Video')

        """Follow util"""
        # default enabled=False, follows ~ every 10th user from the images
        self.set_do_follow(enabled=True, percentage=10)

        """Like util"""
        # completely ignore liking images from certain users
        self.set_ignore_users(['random_user', 'another_username'])
        # searches the description and owner comments for the given words
        # and won't like the image if one of the words are in there
        self.set_dont_like(['food', 'eat', 'meal'])
        # will ignore the don't like if the description contains
        # one of the given words
        self.set_ignore_if_contains(['glutenfree', 'french', 'tasty'])

        """Unfollow util"""
        # will prevent commenting and unfollowing your good friends
        self.set_dont_include(['friend1', 'friend2', 'friend3'])

        """Extras"""
        # Reduces the amount of time under sleep to a given percentage
        # It might be useful to test the tool or to increase the time for slower connections (percentage > 100)
        self.set_sleep_reduce(20)

        # randomly choose 5 pictures to be liked.
        # take into account the other set options like the comment rate
        # and the filtering for inappropriate words or users
        self.set_user_interact(amount=5, random=True, percentage=50)

    def act(self):
        try:
            """Different tasks"""
            # you can put in as much tags as you want, likes 100 of each tag
            session.like_by_tags(['cat'], amount=100, interact=True)

            # follows the followers of a given user
            # The usernames can be either a list or a string
            # The amount is for each account, in this case 30 users will be followed
            # If random is false it will pick in a top-down fashion
            # default sleep_delay=600 (10min) for every 10 user following, in this case sleep for 60 seconds
            session.follow_user_followers(['friend1', 'friend2', 'friend3'], amount=10, random=False, sleep_delay=60)
            # For 50% of the 30 newly followed, move to their profile
            # and randomly choose 5 pictures to be liked.
            # Take into account the other set options like the comment rate
            # and the filtering for inappropriate words or users

            # default sleep_delay=600 (10min) for every 10 user following, in this case sleep for 60 seconds
            session.follow_user_followers(['cats_of_instagram'], amount=10, random=False, interact=True,
                                          sleep_delay=60)

            session.unfollow_users(onlyInstapyFollowed=True, unfollow_after=48*60*60,
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
            raise

        act()
