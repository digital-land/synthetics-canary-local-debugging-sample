def calculate_req_header_size(har_req):
    buffer = "%s %s %s\r\n".format(har_req["method"], har_req["url"], har_req["httpVersion"])
    header_lines = "".join(
        list(map(lambda header: "%s: %s\r\n".format(header["name"], header["value"]), har_req["headers"])))
    buffer = buffer + header_lines
    buffer = buffer + "\r\n"
    return len(buffer)


def calculate_resp_header_size(perflog_resp):
    buffer = "%s %d %s\r\n".format(perflog_resp["protocol"], perflog_resp["status"], perflog_resp["statusText"])
    keys = list(perflog_resp.keys())
    for key in keys:
        buffer = buffer + "%s: %s\r\n".format(key, perflog_resp[key])
    buffer = buffer + "\r\n"
    return len(buffer)


def parse_header(headers):
    if not headers:
        return []

    keys = list(headers.keys())
    entries = []
    for key in keys:
        entries.append({
            "name": key,
            "value": headers[key]
        })
    return entries


def get_header_value(headers, header):
    if not headers:
        return ""

    # http header names are case insensitive
    lowercase_header = header.lower()
    value = None
    for name in headers:
        if name.lower() == lowercase_header:
            value = headers[name]
            break

    return value or ""

