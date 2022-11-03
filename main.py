from automate import run_model
import os, shutil
import numpy as np

os.makedirs('data', exist_ok=True)
num = 5
np.random.seed(100)
r_out = 0.1 * np.random.rand(num) + 0.2  # range: [0.2, 0.3]
r_in = r_out - (0.05 * np.random.rand(num) + 0.05)  # range: r_out - [0.05, 0.1]
width = 0.1 + 0.1 * np.random.rand(num)  # # range: [0.1, 0.2]
spoke_width = 0.02 * np.random.rand(num) + 0.02  # range: [0.02, 0.04]
num_spokes = np.random.randint(low=2, high=7, size=num)

for i in range(num):
    run_model(r_out=r_out[i], r_in=r_in[i], width=width[i],
              spoke_width=spoke_width[i], num_spokes=num_spokes[i], vis=True)

# move csv files to folder
files = os.listdir('./')
for file in files:
    if file.endswith('.csv'):
        shutil.move(file, 'data/' + file)
