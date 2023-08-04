from pyModbusTCP.client import ModbusClient
from pyModbusTCP import utils

#TODO Import delay, make it as a module, torque negative zone saturation 

from dynam2torque import DynamTorqueConverter

PARAMS_PATH = 'param.csv'
DYNAMOGRAM_PATH = 'dynamogram1.csv'

dyn2torque = DynamTorqueConverter(PARAMS_PATH, DYNAMOGRAM_PATH)

f_cu = 2350
t_count = 36000
k_torque = 0.40
try:
    client = ModbusClient(host='192.168.45.12', port=502)
except ValueError:
    print("Error with host or port params")
if client.open():
#пример работы с modbus
    while True:
        gear_k = client.read_holding_registers(670, 2)
        gear_k = [gear_k[1], gear_k[0]]
        gear_k = [utils.decode_ieee(f) for f in utils.word_list_to_long(gear_k)][0]

        gear_angle = client.read_holding_registers(672, 2)
        gear_angle = [gear_angle[1], gear_angle[0]]
        gear_angle = [utils.decode_ieee(f) for f in utils.word_list_to_long(gear_angle)][0]
        gear_angle = -gear_angle

        position, k_theta = dyn2torque.compute_travel(gear_angle)
        torque = dyn2torque.get_torque(gear_angle, position, k_theta, f_cu, t_count)
        torque = k_torque*torque/gear_k
        print(gear_k, gear_angle, torque)

        b32_l = [utils.encode_ieee(f) for f in [torque]]
        b16_l = utils.long_list_to_word(b32_l)
        b16_l = [b16_l[1], b16_l[0]]
        client.write_multiple_registers(666, b16_l)
        # client.close()

    # try:
    #     client = ModbusClient(host='192.168.45.22', port=502)
    # except ValueError:
    #     print("Error with host or port params")
    # if client.open():
    #     b32_l = [utils.encode_ieee(f) for f in a]
    #     b16_l = utils.long_list_to_word(b32_l)
    #     b16_l = [b16_l[1], b16_l[0]]
    #     client.close()