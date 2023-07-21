from csv import DictReader, reader
import matplotlib.pyplot as plt
import numpy as np
dynamo = []
# загрузка динамограммы
with open("new.csv",'r') as data:        
    for line in reader(data, delimiter=','):
            if line != ['0', '0']:
                dynamo.append(line)
    dynamo = dynamo[1:]
print(len(dynamo))
new_dynamo = []
for i in range(58):
    l = []
    for j in range(2):
        l.append(float(dynamo[i*10000][j]))
    new_dynamo.append(l)
l = []
for j in range(2):
    l.append(float(dynamo[len(dynamo)-1][j]))
new_dynamo.append(l)

new_dynamo = np.array(new_dynamo)
print(new_dynamo)
plt.plot(new_dynamo[:,0],new_dynamo[:,1])


np.savetxt('dynamogram1.csv', new_dynamo, delimiter=';', fmt='%f')