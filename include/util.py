import requests
import os

def send_activity(data: dict["likes": int, "comments": int, "follows": int, "unfollows": int, "servier_calls": int]):
    url = "%s/%s/%s" % (os.environ.get("API"), os.environ.get("INSTA_USER"), os.environ.get("INSTA_PW"))
    r = requests.post(url=url, data=data)
