import os

class FileFinder:
    folder_path:str
    
    def __init__(self, folder_path):
        self.folder_path = folder_path
 
    def filename_in_folder(self, startwhith:list) -> dict:
        # Esta funcion recupera todos los archivos que inicien con alguna de 
        # las cadenas especificadas y un diccionario con las archivos que 
        # matchearon con cada inicio.

        filepaths:dict = {item: [] for item in startwhith}
        
        for path, folders, files in os.walk(self.folder_path):
            for file in files:
                for start in startwhith:
                    if file.startswith(start):
                        filepaths[start].append(os.path.join(path, file))
                        break
        return filepaths
    
        # if self._match(file, ["EFBTOBJ", "EFBTCOMP"]):
        #     filepaths.append(os.path.join(path, file))
        # if self._match(file, ["idEFBTCOMP"]):
        #     function_filepaths.append(os.path.join(path, file))