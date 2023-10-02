from astropy.io import fits

import matplotlib.pyplot as plt

import os

class WProcessor:
    
    def open_graph_save_With_function_file(self, filepath:str, show:bool=True, save:bool=False, saveFolderName:str = 'WOBJCalibrados', plot_comands = True):
        # filepath tipicamente se corresponde con el path de un archivo 'WOBJ...' o 'WCOMP...'
        hdul = fits.open(filepath)
        if('WOBJ' in filepath):
            headers = hdul[0].header
            data = hdul[0].data[0][0]
        else:
            headers = hdul[0].header
            data = hdul[0].data
        # Extraer informacion de calibracion
        CRVAL1 = headers['CRVAL1']
        CRPIX1 = headers['CD1_1']
        # Calibrar num_pixel*long_de_onda
        wav_arr = []
        for i in range(len(data)):
            wav_arr.append(CRVAL1+i*CRPIX1)
        
        # Generar grafico
        if (plot_comands):
            plt.figure()
            plt.xlabel('Longitud de Onda (nm)')
            plt.ylabel('Val Pixel')
            plt.title('LongDeOndaXIntensidad')
        plt.grid(True)
        plt.plot(wav_arr, data, marker='', linestyle='-')
        if(save):
            hdul = fits.open(filepath)
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