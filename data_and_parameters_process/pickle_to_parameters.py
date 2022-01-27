from datalib import Data
from datetime import datetime
import os
import time
import pickle


x,y = -12.532711942024456,154.88571004634898

num_files = int(input("How many files to process?"))

parameters = []
donefiles = []
data = Data()

pickle_path = "D:\IMD\product_pickle"
pickle_files = os.listdir(pickle_path)
parameter_file_name = f"parameters({x},{y}).txt"

if os.path.isfile(parameter_file_name):
    with open(parameter_file_name,'rb') as fp:
        parameters = pickle.load(fp)

donefiles = [item['name'] for item in parameters]

print(len(parameters))

start = time.time()
count = 0

for file in pickle_files:
    file_name = file.split('.')[0]

    if file_name in donefiles:
        continue
    
    print(file_name)

    full_file_path = pickle_path+'/'+file
    
    timepoint = datetime.strptime(file_name[3:-3]+'000',"%y%m%d%H%M%S")

    data.load_pickle(full_file_path)
    file_parameters = data.parameters(x,y)
    parameters.append({"name":file_name,"datetime":timepoint,"parameters":file_parameters})
    count+=1

    if count==num_files:
        break

end = time.time()

print(f"Time taken for {count} files : {end-start}")

with open(parameter_file_name,'wb') as fp:
    pickle.dump(parameters,fp)