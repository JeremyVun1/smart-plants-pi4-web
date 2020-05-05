from smartplant.bt import find_new_smartplant_devices, connect_smartplant_devices

find_new_smartplant_devices()
bt_sockets = connect_smartplant_devices()
print(bt_sockets)