import os
import pickle
import numpy as np
from pprint import pprint
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import pandas as pd

# directory of homebrew database
DATADIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       '..',
                       'data')

# pickle database path
DBPATH = os.path.join(DATADIR, 'bdb.pickle')

with open(DBPATH, 'rb') as fidr:
    data = pickle.load(fidr)

# read the comments
# for d in data:
#     if len(data[d]['comments']) > 1:
#         print(f"{data[d]['name']}")
#         print(f"{data[d]['recipe']['Style']}")
#         pprint(data[d]['comments'][:6])
# exit()

stats = [data[d]['stats'] for d in data]
vals = np.array([[s[k] for k in sorted(s)] for s in stats])

og = [0.0] * len(stats)
fg = [0.0] * len(stats)
abv = [0.0] * len(stats)
abv_names = [''] * len(stats)

for i, s in enumerate(stats):
    og[i] = s['Original Gravity']
    fg[i] = s['Final Gravity']
    abv_name = 'ABV (standard)'
    if abv_name not in s:
        abv_name = 'ABV (alternate)'
    abv[i] = s[abv_name] * 100
    abv_names[i] = abv_name
    print(f'{i+1:5,}', end='\r')

df = pd.DataFrame({'OG': og, 'FG': fg, 'ABV': abv, 'ABV_NAME': abv_names})
print(df.head())
pd.plotting.scatter_matrix(df)

plt.show()

# create scatter plot comparing values
# fig = plt.figure()
# ax = fig.gca(projection='3d')
# ax.scatter(og, fg, abv)
# ax.set_xlabel('OG')
# ax.set_ylabel('FG')
# ax.set_zlabel('ABV (%%)')
# plt.show()
