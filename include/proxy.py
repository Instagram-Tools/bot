from time import sleep
import os
import requests

PROXY_MANAGER = os.environ.get('PROXY_MANAGER')

def get_proxy(user):
    if not PROXY_MANAGER:
        return None

    proxy = None
    while not proxy:
        try:
            proxy = get_proxy_manager(user)
            proxy = create_proxy(user=user, proxy=proxy)
        except requests.exceptions.ConnectionError:
            print("retry: get Proxy for user: %s" % user)
            sleep(10)
    print("use Proxy: %s for User: %s" % (proxy, user))
    return proxy


def create_proxy(user, proxy):
    for i in range(2):
        if check_proxy(proxy=proxy):
            return proxy
        print("%s: waiting for Proxy of user: %s" % (i, user))
        sleep(10)
        proxy = get_proxy_manager(user)

    return create_proxy(user=user, proxy=restart_proxy_manager(user=user))


def get_proxy_manager(user):
    return requests.get((PROXY_MANAGER + '/%s') % user).text


def restart_proxy_manager(user):
    return requests.get(PROXY_MANAGER + '/restart/%s' % user).text


def check_proxy(proxy):
    try:
        print('check_proxy(%s)' % proxy)
        requests.get('http://example.com', proxies={'http': proxy})
    except IOError:
        return False
    else:
        return True