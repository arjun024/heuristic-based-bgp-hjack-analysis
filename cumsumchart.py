# assuming tmp provides data as a list, as outputted by main.py
# e.g. data = [(197155, {'gullible': 2, 'appeared': 2, 'reliability_score': 0.0}), ...
from data import data

import numpy as np
import math
#from pylab import plot, show
import matplotlib.pyplot as plt

dx = 20

buckets = [0] * dx
for el in data:
	score = el[1]['reliability_score']
	buckets[int(math.ceil(score * float(dx)) - 1)] += 1

y = np.cumsum(buckets)
x = np.arange(1.0/dx, 1.0 + 1.0/dx, 1.0/dx)

#plot(x, y)
#show()
plt.title('Cumulative distribution of reliability score')
plt.xlabel('Reliability score')
plt.ylabel('Number of ASes')
plt.semilogy(x, y, color='g')
#plt.fill('b')
plt.savefig('scores_log')
