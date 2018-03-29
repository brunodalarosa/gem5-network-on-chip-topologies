from math import *
n = 16 # number of nodes
k= int(log(n,2))
print(k)

for i in xrange(1, k+1):
    for j in xrange(n):
        print("O node [" +str(i)+ ","+str(j)+"] se conecta em:")
        print("[" + str(i-1) + "," + str(j) + "]")
        m = j ^ (1 << ((k - 1) - (i - 1)))
        print("[" + str(i-1) + "," + str(m) + "]")
