import pandas as pd
import numpy as np

def lod_calc(n, cv, beta, k):
    if cv == 0:
        return -np.log(beta) / (n * k)
    d = 1 / np.pow(cv,2)
    return ((d / np.pow(beta, 1 / (n * d))) - d) / k

def calc(num, cv, beta, k):
    lod = pd.DataFrame(np.linspace(1, 1000, num=1000), columns=['n'])
    for i in range(num):
        lod[f'Line {i}'] = lod.n.apply(lod_calc, args=[cv[i], beta[i], k[i]])

    return {'Graph': lod[lod['n'] <= 50], 'Table': lod[lod['n'] <= 10]}