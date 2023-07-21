import math
from csv import DictReader, reader

GRAVITY_CONSTANT = 9.81

class DynamTorqueConverter:
    
    def __init__(self, params_file_name : str, dynamogram_file : str) -> None:
        # Read sucker-rod pump parameters
        with open(params_file_name, 'r') as data:        
            dict_reader = DictReader(data, delimiter=';')
            list_of_dict = list(dict_reader)

        # Sucker-rod pump parameters
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
        # Load dynamogram
        with open(dynamogram_file,'r') as data:        
            for line in reader(data, delimiter=';'):
                    dynamo.append(line)
            dynamo = dynamo[1:]
            
        x_dyn = []
        f_dyn = []
        for i in range(len(dynamo)):
            f_dyn.append(float(dynamo[i][1]))
            x_dyn.append(float(dynamo[i][0]))
        
        self.a = a
        
        self.r = r
        self.r_sq = r**2
        
        self.b = b
        self.b_sq = b**2
        
        self.c = c
        self.c_sq = c**2
        
        self.force_array = f_dyn
        self.coordinate_array = x_dyn
        
        # Compute kinematic parameters
        self.k = math.sqrt(l1**2 + l2**2)
        self.fi = math.pi / 2 - math.atan2(l2, l1)
        
        # Common psi terms
        self.k_sq = self.k**2
        den = 2 * self.k * c
        
        self.psi_max = math.acos((self.k_sq + self.c_sq - (b + r)**2) / den)
        self.psi_min = math.acos((self.k_sq + self.c_sq - (b - r)**2) / den)
        
        self.s_rod_max = (self.psi_max - self.psi_min) * a
        self.rca = r * a / c
    
    def compute_travel(self, angle : float) -> tuple:
        '''
        angle -- угол положения противовеса [рад]
        
        '''
        j = math.sqrt(self.r_sq - math.cos(angle - self.fi) * self.k * self.r * 2 + self.k_sq)
        ksi = (self.k_sq + (j**2 - self.r_sq)) / (2 * j * self.k)
        
        if ksi >= 1:
            ksi = 1
        if ksi <= -1:
            ksi = -1
        ksi = math.acos(ksi)
        
        eps = (j**2 + self.c_sq - self.b_sq) / (2 * j * self.c)
        if eps >= 1:
            eps = 1
        if eps <= -1:
            eps = -1
        eps = math.acos(eps)
        
        beta = (self.c_sq + self.b_sq - j**2) / (2 * self.b * self.c)
        if beta >= 1:
            beta = 1
        if beta <= -1:
            beta = -1
        beta = math.acos(beta)
    
        psi = math.sin(angle - self.fi)
        if psi >= 0:
            psi = eps - ksi
        if psi < 0:
            psi = eps + ksi
        
        alpha = self.fi - angle + psi + beta
        
        k_theta = self.rca * (math.sin(alpha) / math.sin(beta))
        s_rod = (self.psi_max - psi) * self.a
        return s_rod, k_theta
        
    def get_torque(self, angle : float, s_rod: float, k_theta: float,
                   f_cu: float, t_count: float) -> float:
        if (angle <= math.pi):
            x = self.coordinate_array[:int(len(self.coordinate_array)/2)]
            f = self.force_array[:int(len(self.force_array)/2)]
            
            _, i = self.get_closest_idx(x, s_rod)
            
        else:
            x = self.coordinate_array[int(len(self.coordinate_array)/2):]
            f = self.force_array[int(len(self.force_array)/2):]
            
            _, i = self.get_closest_idx(x, s_rod)
            
        torque  = (GRAVITY_CONSTANT * f[i]- f_cu) * k_theta  - t_count * math.sin(angle)
        return torque
    
    def get_closest_idx(self, array, ref_value) -> tuple:
        value = array[min(range(len(array)), key = lambda i: abs(array[i] - ref_value))]
        idx = array.index(value)
        return value, idx