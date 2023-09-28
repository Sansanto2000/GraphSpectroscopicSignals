from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt
import os
from tqdm import tqdm

def match (name):
    if name.startswith("WOBJ"):
        return True
    elif name.startswith("WCOMP"):
        return True
    else:
        return False
 
def filename_in_folder(main_folder_name:str):
    filenames = []
    for path, folders, files in os.walk(main_folder_name):
        for file in files:
            if match(file):
                filenames.append(os.path.join(path, file))
    return filenames

def open_file_and_graph(filepath):
    
    hdul = fits.open(filepath) #open file
    
    if('WOBJ' in filepath):
        headers = hdul[0].header
        data = hdul[0].data[0][0]
    else:
        headers = hdul[0].header
        data = hdul[0].data

    CRVAL1 = headers['CRVAL1']
    CRPIX1 = headers['CD1_1']

    wav_arr = []
    for i in range(len(data)):
        wav_arr.append(CRVAL1+i*CRPIX1)

    #print(wav_arr)
    plt.figure()
    #print(wav_arr)
    plt.plot(wav_arr, data, marker='', linestyle='-')
    plt.xlabel('Longitud de Onda (nm)')
    plt.ylabel('Val Pixel')
    plt.title('LongDeOndaXIntensidad')
    plt.grid(True)
    #plt.show()
    destiny_folder = 'Conjunto 1'
    if not os.path.exists(destiny_folder):
        os.makedirs(destiny_folder)
    full_folder_path, filename = os.path.split(filepath)
    _, folder_name = os.path.split(full_folder_path)
    new_path = os.path.join(destiny_folder, f"{folder_name}_{filename}")
    new_path, _ = os.path.splitext(new_path)
    plt.savefig(new_path+'.png')
    plt.close()

    hdul.close()

folder_name = "C:/Users/santi/OneDrive/Documentos/Doctorado/Datos Crudos"
files = filename_in_folder(main_folder_name=folder_name)

for file in tqdm(files, desc="Generando graficos"):
    open_file_and_graph(file)
print('Listo')



