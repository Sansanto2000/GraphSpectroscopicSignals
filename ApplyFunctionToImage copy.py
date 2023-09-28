from ImageToGraph import graficarImagen
import matplotlib.pyplot as plt
from astropy.io import fits
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import re
from tqdm import tqdm

def match (name, match_names):
    for match in match_names:
        if name.startswith(match):
            return True
    return False
    
 
def filename_in_folder(main_folder_name:str):
    filenames = []
    function_filenames = []
    for path, folders, files in os.walk(main_folder_name):
        for file in files:
            if match(file, ["EFBTOBJ", "EFBTCOMP"]):
                filenames.append(os.path.join(path, file))
            if match(file, ["idEFBTCOMP"]):
                function_filenames.append(os.path.join(path, file))
    return filenames, function_filenames

def open_file_and_graph(filepath, function_filepath):
    def legendre(coefficients, x):
        # coefficients:
        #   0 <- Cantidad de numeros a continuacion
        #   1 <- Tipo de funcion (1:?, 2:Legendre, 3:?)
        #   2 <- Cantidad de terminos del polinomio, Orden del polinomio
        #   3, 4 <- xmin, xmax: Valores que se utilizan para normalizar los polinomios al rango [-1,1]
        #           n = (2 * x - (xmax + xmin)) / (xmax - xmin).
        #   5,... <- El resto de los coeficientes son los que corresponden a las funciones propiamente dichas.
        #            - Caso legendre:
        #               y = sum from i=1 to order {c_i * z_i}
        #               donde c_i son los coeficientes y los z_i se definen iterativamente como:
        #               z_1 = 1
        #               z_2 = n
        #               z_i = ((2*i-3) * n * z_{i-1} - (i-2) * z_{i-2}) / (i-1)
        order = int(coefficients[2])
        xmin = coefficients[3]
        xmax = coefficients[4]
        real_coefficients = coefficients[5:]
        n = (2 * x - (xmax + xmin)) / (xmax - xmin)
        y = 0
        z = [None for _ in range(order)]
        for i in range(1, order):
            if (i==1):
                z[i-1] = 1
            elif (i==2):
                z[i-1] = n
            else:
                z[i-1] = ((2*i-3) * n * z[i-2] - z[i-3] * z[i-3]) / (i-1)
            y += real_coefficients[i-1] * z[i-1]
        return y
    
    hdul = fits.open(filepath) #open file
    
    if('EFBTOBJ' in filepath):
        headers = hdul[0].header
        data = hdul[0].data[0][0]
    else:
        headers = hdul[0].header
        data = hdul[0].data
    
    # Extraer informacion de funcion a aplicar
    function_type:str
    function_order:int
    coefficients = []
    reading_coefficients=False
    with open(function_filepath, mode="r") as file:
        for line in file.readlines():
            words=line.split()
            if words:
                if (words[0]=='function'):
                    function_type = words[1]
                elif (words[0]=='order'):
                    function_order = int(words[1])
                elif(words[0]=='coefficients'):
                    reading_coefficients=True
                    coefficients.append(words[1])
                elif(reading_coefficients):
                    coefficients.append(float(words[0]))    
            elif(reading_coefficients):
                reading_coefficients=False             
    # Segun el tipo de funcion calcula el arreglo de longitudes de onda de una hu otra forma
    wav_arr = []
    if function_type == "legendre":
        for i in range(len(data)):
            wav_arr.append(legendre(coefficients, i))
    else:
        raise ValueError(f"Ha aparecido un tipo de funcion desconosido: function_type={function_type}")
    # Grafica
    plt.figure()
    plt.plot(wav_arr, data, marker='', linestyle='-')
    plt.xlabel('Longitud de Onda (nm)')
    plt.ylabel('Val Pixel')
    plt.title('LongDeOndaXIntensidad')
    plt.grid(True)
    #plt.show()
    
    # Guarda los resultados
    destiny_folder = 'Conjunto 2'
    if not os.path.exists(destiny_folder):
        os.makedirs(destiny_folder)
    full_folder_path, filename = os.path.split(filepath)
    _, folder_name = os.path.split(full_folder_path)
    new_path = os.path.join(destiny_folder, f"{folder_name}_{filename}")
    new_path, _ = os.path.splitext(new_path)
    plt.savefig(new_path+'.png')
    plt.close()
    hdul.close()

def extract_path_info(path):
    num = None
    folderpath = None
    patron = r"^(.+)\\EFBT(OBJ|COMP)(\d+)(?:_?\w*)?\.fits$"
    match = re.search(patron, path)
    if match:
        folderpath = match.group(1)
        num = match.group(3)
    return num, folderpath

def encontrar_elemento_con_substring(arr, substring):
    for elemento in arr:
        if substring in elemento:
            return elemento  # Devuelve el primer elemento que contiene el substring
    return None

folder_name = "C:\\Users\\santi\\OneDrive\\Documentos\\Doctorado\\Datos Crudos"
files, comparation_files = filename_in_folder(main_folder_name=folder_name)

for file in tqdm(files, desc="Generando graficos"):
    file_num, file_folderpath = extract_path_info(file)
    comparation_file = f"{file_folderpath}\\database\\idEFBTCOMP{file_num}"
    elem = encontrar_elemento_con_substring(comparation_files, comparation_file)
    if elem:
        comparation_file = elem
    open_file_and_graph(file, comparation_file)
print('Listo')