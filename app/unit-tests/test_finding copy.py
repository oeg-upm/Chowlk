import os


dir_name = "E:\\Trabajo\\ChowlkProject\\test_rehacer_2"

contenido = os.listdir(dir_name)
imagenes = []
num = 401
for fichero in contenido:
    file_path_1 = os.path.join(dir_name, fichero)
    file_path_2 = os.path.join(dir_name, f'test_restriction_{num}.xml')
    os.rename(file_path_1, file_path_2)
    num = num + 1