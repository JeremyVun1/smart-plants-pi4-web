import json
from select import select


def is_query_response(response):
    try:
        obj = json.loads(response)
        return obj['d'] == 'y'
    except Exception:
        return False


def close_sockets(sockets):
    try:
        for mac in sockets:
            sockets[mac].close()
    except Exception:
        print("could not close socket")


def read_line(socket):
    # socket.setblocking(0)
    ready = select([socket], [], [], 1)
    if ready[0]:
        response = b""
        while True:
            # print(response)
            buffer = socket.recv(1)
            response += buffer
            if (buffer == b"\n"):
                break
        try:
            response = response.decode("utf-8")
            response = response.replace('\r', '').replace('\n', '').replace('?', '')
            return response
        except Exception:
            return None
    else:
        return None