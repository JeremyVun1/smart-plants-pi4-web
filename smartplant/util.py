import json
from select import select


def readLine(socket):
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

        response = response.decode("utf-8")
        response = response.replace('\r', '').replace('\n', '').replace('?', '')
        return response
    else:
        print("serial buffer is not ready")
        return None
