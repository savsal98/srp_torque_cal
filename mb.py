from pyModbusTCP.client import ModbusClient
from pyModbusTCP import utils

#пример работы с modbus
while True:
    try:
        client = ModbusClient(host='192.168.0.6', port=502)
    except ValueError:
        print("Error with host or port params")
    if client.open():
        regs_list_1 = client.read_holding_registers(644, 2)
        regs_list_1 = [regs_list_1[1], regs_list_1[0]]
        a = [utils.decode_ieee(f) for f in utils.word_list_to_long(regs_list_1)]
        print(a)
        client.close()

    try:
        client = ModbusClient(host='192.168.0.7', port=502)
    except ValueError:
        print("Error with host or port params")
    if client.open():
        b32_l = [utils.encode_ieee(f) for f in a]
        b16_l = utils.long_list_to_word(b32_l)
        b16_l = [b16_l[1], b16_l[0]]
        client.write_multiple_registers(694, b16_l)
        client.close()