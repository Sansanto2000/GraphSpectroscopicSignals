from FileFinder import FileFinder
from EFBTProcessor import EFBTProcessor
from WProcessor import WProcessor

import re
from tqdm import tqdm

# def _match_EFBT_W(path, Wfiles):
#     for file in Wfiles:
#         num, obj_type, folderpath, ext = _extract_path_info(file)
#         patron = fr"{re.escape(folderpath)}\\W({re.escape(obj_type)})({re.escape(num)})({re.escape(ext)})?.fits$"
        
#         if()
#     for file_path in Wfiles:
#         path =re.search(patron, file_path)
#     return path

def _extract_path_info(path):
    num = None
    obj_type = None
    folderpath = None
    ext:str = None
    patron = r"^(.+)\\EFBT(OBJ|COMP)(\d+)(_?\w*)?\.fits$"
    match = re.search(patron, path)
    if match:
        folderpath = match.group(1)
        obj_type = match.group(2)
        num = match.group(3)
        ext = match.group(4)
    return num, obj_type, folderpath, ext

def _encontrar_elemento_con_substring(arr, substring):
    for elemento in arr:
        if substring in elemento:
            return elemento  # Devuelve el primer elemento que contiene el substring
    return None

folder_path = "C:\\Users\\santi\\OneDrive\\Documentos\\Doctorado\\Datos Crudos"
ff = FileFinder(folder_path=folder_path)
start_array1 = ["WOBJ", "WCOMP"]
start_array2 = ["EFBTOBJ", "EFBTCOMP"]
start_array3 = ["idEFBTCOMP"]
filesW = ff.filename_in_folder(startwhith=start_array1)
filesW = filesW["WOBJ"] + filesW["WCOMP"]
filesEFBT = ff.filename_in_folder(startwhith=start_array2)
filesEFBT = filesEFBT["EFBTOBJ"] + filesEFBT["EFBTCOMP"]
function_files = ff.filename_in_folder(startwhith=start_array3)
function_files = function_files["idEFBTCOMP"]
# Matchea cada EFBT con su archivo de funcion
dictEFBT_function = {}
for file in filesEFBT:
    file_num, _, file_folderpath, _ = _extract_path_info(file)
    function_file = f"{file_folderpath}\\database\\idEFBTCOMP{file_num}"
    elem = _encontrar_elemento_con_substring(function_files, function_file)
    if elem:
        dictEFBT_function[file] = elem
# Matchea cada EFBT con el W que le corresponden
dictEFBT_W = {}
for file in filesEFBT:
    #print(file)
    file_num, obj_type, file_folderpath, ext = _extract_path_info(file)
    w_file = f"{file_folderpath}\\W{obj_type}{file_num}{ext}.fits"
    elem = _encontrar_elemento_con_substring(filesW, w_file)
    #print(w_file)
    if elem:
        dictEFBT_W[file] = elem

#print(filesEFBT)
#print(dictEFBT_function)

# Generar y guardar los graficos
efbtp = EFBTProcessor()
wp = WProcessor()
for file in tqdm(filesEFBT, desc="Generando graficos"):
    file_num, _, file_folderpath, _ = _extract_path_info(file)
    try:
        function_file = dictEFBT_function[file]
        w_file = dictEFBT_W[file]
        efbtp.open_graph_save_With_function_file(file, function_file, show = False, save = False, plot_comands = True)
        wp.open_graph_save_With_function_file(w_file, show = False, save = True, saveFolderName='Conjunto_3_(Calibrados)', plot_comands = False)
    except KeyError as e:
        continue
print('Listo')