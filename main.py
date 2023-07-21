from dynam2torque import DynamTorqueConverter

PARAMS_PATH = 'param.csv'
DYNAMOGRAM_PATH = 'dynamogram1.csv'

def main():
    dyn2torque = DynamTorqueConverter(PARAMS_PATH, DYNAMOGRAM_PATH)
    
    angle = 0.0
    f_cu = 2350
    t_count = 36000

    result = []
    for i in range(628):
        angle = i/100
        position, k_theta = dyn2torque.compute_travel(angle)
        torque = dyn2torque.get_torque(angle, position, k_theta, f_cu, t_count)

if __name__ == '__main__':
    main()
    
#пример работы с modbus
# try:
#     client = ModbusClient(host='192.168.127.10', port=502)
# except ValueError:
#     print("Error with host or port params")
# if client.open():
#     regs_list_1 = client.read_holding_registers(0, 10)
#     regs_list_2 = client.read_holding_registers(55, 10)
#     regs_list_2 = client.write_single_register(55, 0)
#     client.close()

