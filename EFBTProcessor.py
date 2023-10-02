from astropy.io import fits

import matplotlib.pyplot as plt

import os

class EFBTProcessor:
    
    def _legendre(self, coefficients:list, x:float) -> float:
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
        y:float = 0.0
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
    
    def _extract_function_data(self, function_filepath:str) -> (list, str, int):
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
        return coefficients, function_type, function_order
    
    def open_graph_save_With_function_file(self, filepath:str, function_filepath:str, show:bool=True, save:bool=False, saveFolderName:str = 'EFBTOBJCalibrados', plot_comands = True):
        # filepath tipicamente se corresponde con el path de un archivo 'EFBTOBJ...' o 'EFBTCOMP...'
        # funtion_filepath tipicamente se corresponde con el path de un archivo 'idEFBT...'
        hdul = fits.open(filepath)
        if('EFBTOBJ' in filepath):
            headers = hdul[0].header
            data = hdul[0].data[0][0]
        else: # Se trata de un archivo 'EFBTCOMP..' con informacion de 
            # la lampara de comparacion
            headers = hdul[0].header
            data = hdul[0].data
        
        # Extraer informacion de la funcion
        coefficients, function_type, _ = self._extract_function_data(function_filepath=function_filepath)
        
        # Calcula el arreglo de longitudes de onda segun el tipo de funcion
        wav_arr = []
        if function_type == "legendre":
            for i in range(len(data)):
                wav_arr.append(self._legendre(coefficients, i))
        else:
            raise ValueError(f"Ha aparecido un tipo de funcion desconosido: function_type={function_type}")
        
        # Generar grafico
        if (plot_comands):
            plt.figure()
            plt.xlabel('Longitud de Onda (nm)')
            plt.ylabel('Val Pixel')
            plt.title('LongDeOndaXIntensidad')
            plt.grid(True)
        plt.plot(wav_arr, data, marker='', linestyle='-')
        if(save):
            if not os.path.exists(saveFolderName):
                os.makedirs(saveFolderName)
            full_folder_path, filename = os.path.split(filepath)
            _, folder_name = os.path.split(full_folder_path)
            new_path = os.path.join(saveFolderName, f"{folder_name}_{filename}")
            new_path, _ = os.path.splitext(new_path)
            plt.savefig(new_path+'.png')
            plt.close()
            hdul.close()
        if(show):
            plt.show()