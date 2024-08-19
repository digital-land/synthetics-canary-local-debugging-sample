from http.cookies import SimpleCookie
import logging

logger = logging.getLogger(__name__)

def parse(header: str, divider: str):
    split_list = header.split(divider)
    cookies = []
    for item in split_list:
        if item == "":
            continue

        cookie = SimpleCookie()
        try:
            cookie.load(item)
            cookies.append(cookie)
        except:
            logger.warning("Unable to load cookie %s, potentially malformed cookie with divider %s.", header, repr(divider))
    return cookies


def parse_request_cookies(cookie_header):
    cookies = filter(None, parse(cookie_header, ";"))
    formatted_cookies = []
    for cookie in cookies:
        # get cookie name, there will be only one name
        name = list(cookie).pop()
        if name is not None:
            value = dict(dict(cookie).get(name))
            value["name"] = name
            value["value"] = cookie.get(name).value
            formatted_cookies.append(value)

    return formatted_cookies


def parse_response_cookies(cookie_header):
    return parse(cookie_header, "\n")
