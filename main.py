from automate import run_model
import os, shutil

os.makedirs('data', exist_ok=True)
run_model(r_out=0.3, r_in=0.2, width=0.1, spoke_width=0.04, num_spokes=4, vis=True)

# move csv files to folder
files = os.listdir('./')
for file in files:
    if file.endswith('.csv'):
        shutil.move(file, 'data/' + file)
