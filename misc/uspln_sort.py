import os 

path1 = 'C:/Users/tetra/data/lightning/lsu/uspln/'
path0 = 'C:/Users/tetra/data/lightning/lsu/uspln/2016/'

files = [f for f in os.listdir(path0) if os.path.isfile(os.path.join(path0,f))]

for file in files:
    folder = file[10:20]
    output_path = path1 + folder
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    output_file = output_path +'/' + file
    full_file = path0 + file
    os.renames(full_file, output_file)