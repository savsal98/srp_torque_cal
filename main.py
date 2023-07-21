
from csv import DictReader, reader
import math
#для установки sudo pip3 install pyModbusTCP
from pyModbusTCP.client import ModbusClient

# загрузка параметров станков качалок
with open("param.csv",'r') as data:        
    dict_reader = DictReader(data, delimiter=';')
    list_of_dict = list(dict_reader)
    print(list_of_dict)

# выбор тип станка качалки
equip_type = 1
for i in list_of_dict:
    if i['type'] == str(equip_type):
        d = float(i['D[m]'].replace(',','.'))
        b = float(i['B[m]'].replace(',','.'))
        a = float(i['A[m]'].replace(',','.'))
        c = float(i['C[m]'].replace(',','.'))
        r = float(i['R[m]'].replace(',','.'))
        l1 = float(i['L1[m]'].replace(',','.'))
        l2 = float(i['L2[m]'].replace(',','.'))

dynamo = []
# загрузка динамограммы
with open("dynamogram1.csv",'r') as data:        
    for line in reader(data, delimiter=';'):
            dynamo.append(line)
    dynamo = dynamo[1:]
x_dyn = []
f_dyn = []
for i in range(len(dynamo)):
    f_dyn.append(float(dynamo[i][1]))
    x_dyn.append(float(dynamo[i][0]))

import matplotlib.pyplot as plt
plt.plot(x_dyn, f_dyn)
plt.show()

def closest_idx(lst, K):
    val = lst[min(range(len(lst)), key = lambda i: abs(lst[i]-K))]
    idx = lst.index(val)
    return val, idx

def travel_calc(angle:float, r:float, c:float, 
                a:float, b:float,
                d:float, l1:float, l2:float ) ->float:
    '''
    Функция расчета положение штока по углу на выходе редуктора, 
    который был расчитан на ПЧ

    angle           угол положения противовеса [рад/с]

    r               наибольший радиус кривошипа [м]
    c               длина заднего плеча балансира [м]
    a               длина переднего плеча балансира [м]
    b               длина шатуна [м]
    d               длина хода штока [м]
    l1              расстояние между осью опоры балансира и осью ведомого вала редуктора по горизонтали [м]
    l2              расстояние между осью опоры балансира и осью ведомого вала редуктора по вертикали [м]

    '''

    k = math.sqrt((math.pow(l1, 2) + math.pow(l2, 2)))
    fi = math.pi / 2 - math.atan2(l2, l1)
    psi_max = math.acos((math.pow(k, 2) + math.pow(c, 2) - math.pow((b + r), 2)) / (2 * k * c))
    psi_min = math.acos((math.pow(k, 2) + math.pow(c, 2) - math.pow((b - r), 2)) / (2 * k * c))
    rca = r * a / c
    s_rod_max = (psi_max - psi_min) * a


    j = math.sqrt(math.pow(r, 2) - math.cos(angle - fi) * k * r * 2 + math.pow(k, 2))
    ksi = (math.pow(k, 2) + (math.pow(j, 2) - math.pow(r, 2))) / (2 * j * k)
    if ksi >= 1:
        ksi = 1
    if ksi <= -1:
        ksi = -1
    ksi = math.acos(ksi)

    eps = (math.pow(j, 2) + math.pow(c, 2) - math.pow(b, 2)) / (2 * j * c)
    if eps >= 1:
        eps = 1
    if eps <= -1:
        eps = -1
    eps = math.acos(eps)

    beta = (math.pow(c, 2) + math.pow(b, 2) - math.pow(j, 2)) / (2 * b * c)
    if beta >= 1:
        beta = 1
    if beta <= -1:
        beta = -1
    beta = math.acos(beta)

    psi = math.sin(angle - fi)
    if psi >= 0:
        psi = eps - ksi
    if psi < 0:
        psi = eps + ksi

    alpha = fi - angle + psi + beta

    k_tetta = rca * (math.sin(alpha) / math.sin(beta))

    s_rod = (psi_max - psi) * a

    return s_rod, k_tetta

def torque_calc(angle:float, x_dyn:list, f_dyn: list, s_rod: float,  
                k_tetta: float, f_cu: float, t_count: float, r: float) ->float:
    torque  = 0
    if (angle <= math.pi):
        x_dyn = x_dyn[:int(len(x_dyn)/2)]
        f_dyn = f_dyn[:int(len(f_dyn)/2)]
        v, i = closest_idx(x_dyn,s_rod)
    else:
        x_dyn = x_dyn[int(len(x_dyn)/2):]
        f_dyn = f_dyn[int(len(f_dyn)/2):]
        v, i = closest_idx(x_dyn,s_rod)
    torque  = (9.81*f_dyn[i]- f_cu)*k_tetta  - t_count*math.sin(angle)

    return torque
#пример работы функции расчет момента
angle = 0.0
f_cu = 2350
t_count = 36000
result = []
for i in range(628):
    angle = i/100
    position, k_tetta = travel_calc(angle,r,c,a,b,d,l1,l2)
    torque = torque_calc(angle, x_dyn, f_dyn, position, k_tetta, f_cu, t_count, r)
    result.append([position, k_tetta, torque]) 


import matplotlib.pyplot as plt
plt.plot(result)
plt.show()


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

