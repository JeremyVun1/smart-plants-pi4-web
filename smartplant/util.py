import json
from select import select


def parse_full_state_update(response):
    print(f"parsing full state update: {response}")
    obj = json.loads(response)
    print(json)


def load_plant_model(response):
    print(f"parsing full state update: {response}")
    obj = json.loads(response)
    print(json)


def readLine(socket):
    print("reading line from socket serial")
    # socket.setblocking(0)
    ready = select([socket], [], [], 1)
    if ready[0]:
        print("serial buffer is ready")
        response = b""
        while True:
            # print(response)
            buffer = socket.recv(1)
            response += buffer
            if (buffer == b"\n"):
                break

        print(response)
        response = response.decode("utf-8")
        response = response.replace('\r', '').replace('\n', '').replace('?', '')
        print(response)
        return response
    else:
        print("serial buffer is not ready")
        return ""
