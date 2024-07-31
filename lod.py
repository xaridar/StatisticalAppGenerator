import pandas as pd
import numpy as np

def lod_calc(n, cv, beta, k):
    if cv == 0:
        return -np.log(beta) / (n * k)
    d = 1 / np.pow(cv,2)
    return ((d / np.pow(beta, 1 / (n * d))) - d) / k

def calc(cv, beta, k, threshold, arr):
    lod = pd.DataFrame(np.linspace(1, 1000, num=1000), columns=['n'])
    lod['LOD'] = lod.n.apply(lod_calc, args=[cv, beta, k])
    lod['LOD2'] = lod.n.apply(lod_calc, args=[0, beta, k])

    table = {}
    below_threshold = lod[lod['LOD'] < threshold]
    if len(below_threshold) == 0:
        table['Minimum n'] = '> 1000'
    else:
        table['Minimum n'] = below_threshold.n.iloc[0].item()
        table['LOD'] = below_threshold.LOD.iloc[0].item()
    return {'Graph': lod[lod['n'] <= 50], 'Table': table, 'Table2': lod[lod['n'] <= 10], 'Text': 'test'}