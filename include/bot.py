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
            # actions
            self.like_by_tags(['#cat', 'dog'], interact=True)

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
