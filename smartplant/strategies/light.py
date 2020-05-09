from datetime import datetime, time
from smartplant.models import MoistureModel, PumpModel


def time_between(now, start, end):
    return now >= start and now <= end


def day_night_lighting_strategy(app, mac, socket):
    now = datetime.now().time()

    # time between 9am and 5pm
    if time_between(now, time(9,00), time(17,00)):
        # turn off the led lights
        print("turning off light automatically")
        socket.send(int(6).to_bytes(1, "little"))
    else:
        # turn on the led lights
        print("turning on light automatically")
        socket.send(int(5).to_bytes(1, "little"))
