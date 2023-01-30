from automate import run_model
import os, shutil
import numpy as np
from datetime import date


num = 2
seed = 45
folder_name = f'{date.today()}_num_{num}_seed_{seed}_5_vars'
os.makedirs(folder_name, exist_ok=True)

np.random.seed(seed)
r_out = 0.03 * np.random.rand(num) + 0.2  # range: [0.2, 0.23]
r_in = r_out - (0.02 * np.random.rand(num) + 0.03)  # range: r_out - [0.03, 0.05]
width = 0.1 + 0.05 * np.random.rand(num)  # # range: [0.1, 0.15]
spoke_width = 0.03 * np.random.rand(num) + 0.02  # range: [0.03, 0.05]
num_spokes = np.random.randint(low=2, high=5, size=num)
# E = 1e9 + (1e11 - 1e9) * np.random.rand(num)  # range: [1e9, 1e11]
# load = 1000 + (100000 - 1000) * np.random.rand(num)  # range: [1e3, 1e5]
# init_angle = 90 * np.random.rand(num)  # range: [0, 90]

for i in range(num):
    run_model(r_out=r_out[i], r_in=r_in[i], width=width[i],
              spoke_width=spoke_width[i], num_spokes=num_spokes[i], init_angle=0,
              E=1e10, load=1e4, meshsize=0.02, vis=False)

# move csv files to folder
files = os.listdir('./')
for file in files:
    if file.endswith('.csv'):
        shutil.move(file, f'{folder_name}/{file}')
