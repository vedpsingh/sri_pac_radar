from datalib import Data
import wradlib as wrl
import os
import pickle
import time

num_files = int(input("How Many Files? "))

raw_path = "D:\IMD\product_raw"
pickle_path = "D:\IMD\product_pickle"
raw_files = os.listdir(raw_path)
pickle_files = os.listdir(pickle_path)

imd_files = []

imd_files_name = f"imd_files.txt"

# Check for previous checkpoints
if os.path.isfile(imd_files_name):
    with open(imd_files_name,'rb') as fp:
        imdb_files = pickle.load(fp)

start = time.time()
count = 0

data = Data()


for file in raw_files:

    raw_file_path = raw_path + '\\' + file

    if file in imd_files:
        continue

    pickle_file_name = file.split('.')[0]+'.txt'

    # Check if file is done
    if pickle_file_name in pickle_files:
        imd_files.append(file)
        continue

    try:
        file_content = wrl.io.read_iris(raw_file_path)
    except:
        print('read problem')
        continue

    rad_type = file_content['product_hdr']['product_configuration']['product_name'].strip()
    if rad_type!='IMD-B':
        continue
    rad_time = file_content['ingest_header']['ingest_configuration']['volume_scan_start_time']

    # Check if file is valid
    data.set_file(file_content)    
    full_pickle_file_name = pickle_path + '\\' + pickle_file_name

    # Print status
    print(file,count)
    count+=1

    data.save_pickle(full_pickle_file_name)

    imd_files.append(file)

    # Check no. of files done
    if count==num_files:
        break

end = time.time()

print(f"Time taken - {end-start} for {count} files")

with open(imd_files_name,'wb') as fp:
    pickle.dump(imd_files,fp)