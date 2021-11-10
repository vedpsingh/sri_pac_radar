from data import Data
from calcXY import calcxy
import os
import wradlib
import pickle
import time

nfiles = int(input("How Many Files? "))

path = "D:\Data\product_raw\Raw_Data"
files = os.listdir(path)

parameters_final = []
imdb_files = []
# x,y = 0,0
x,y = -12.532711942024456,154.88571004634898
# x,y = calcxy()

imdb_files_name = f"imdb_files({x},{y}).txt"
parameters_final_name = f"parameters({x},{y}).txt"

# Check for previous checkpoints
if os.path.isfile(imdb_files_name):
    with open(imdb_files_name,'rb') as fp:
        imdb_files = pickle.load(fp)

if os.path.isfile(parameters_final_name):
    with open(parameters_final_name,'rb') as fp:
        parameters_final = pickle.load(fp)

print(f"X - {x}\nY - {y}")

start = time.time()
count = 0

for file in files:
    # Check if file is done
    if file in imdb_files:
        continue
    # Check if file is valid
    if(os.path.isdir(file)):
        continue
    if file.endswith(".py") or file.endswith(".txt") or file.endswith(".ipynb"):
        continue
    filep = path+'\\'+file
    if os.path.getsize(filep) not in range(1000000,1500001):
        continue
    try:
        file_cont = wradlib.io.read_iris(filep)
    except:
        continue
    rad_type = file_cont['product_hdr']['product_configuration']['product_name'].strip()
    rad_time = file_cont['ingest_header']['ingest_configuration']['volume_scan_start_time']
    if rad_type != 'IMD-B':
        continue

    print(file)
    count+=1
    
    # Process file
    process = Data(file_cont)
    parameters = process.parameters(x,y)
    fin_dict = {"name":file,"type":rad_type,"time":rad_time,"parameters":parameters,"co-ord":(x,y)}
    parameters_final.append(fin_dict)
    imdb_files.append(file)
    if count==nfiles:
        break

end = time.time()

print(f"Time taken - {end-start} for {count} files")

with open(imdb_files_name,'wb') as fp:
    pickle.dump(imdb_files,fp)

with open(parameters_final_name,'wb') as fp:
    pickle.dump(parameters_final,fp)