dont_like = ['food', 'girl', 'hot']
ignore_words = ['pizza']
friend_list = ['friend1', 'friend2', 'friend3']


class Settings:

    def set(bot):
        bot.set_upper_follower_count(limit=2500)
        bot.set_do_comment(True, percentage=10)
        bot.set_comments(['Cool!', 'Awesome!', 'Nice!'])
        bot.set_dont_include(friend_list)
        bot.set_dont_like(dont_like)
        bot.set_ignore_if_contains(ignore_words)
