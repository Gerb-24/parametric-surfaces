import numpy as np

def fixed_looper(lijst1, lijst2):
    value = looper(lijst1,lijst2)
    if not value  == None:
        return value
    else:
        return -1

def looper(lijst1,lijst2):
    for i in range(len(lijst1)):
        if inrange(lijst1[i], lijst2):
            return i
            break

def inrange(lijst1, lijst2):
    vec = np.array(lijst1) - np.array(lijst2)
    dist = np.linalg.norm(vec)
    if dist < 10:
        #print("In Range")
        return True
    else:
        #print("Out of Range")
        return False
