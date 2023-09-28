from astropy.io import fits

import os

class EFBTProcessor:
    
    files:list = []
    
    def __init__(self):
        self.files = []
    
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
    
    def open_graph_save_With_function_file(filepath, function_filepath):
        hdul = fits.open(filepath) #open file
        
        if('EFBTOBJ' in filepath):
            headers = hdul[0].header
            data = hdul[0].data[0][0]
        else: # Se trata de un archivo 'EFBTCOMP..' con informacion de 
            # la lampara de comparacion
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