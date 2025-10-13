from utils import ocr
import cv2
import os
import base64
import json as jsonlib
import numpy as np

#Método encargado de la decodificación de las imágenes en base64, se recibe el string base64,
#el directorio en donde se guardará la imagen decodificada y un booleano que indica si la 
#imagen es de la parte delantera o trasera de la credencial para asignarle un nombre.
#Regresa el path de guardado y el nombre de la imagen decodificada.
def decode_base64_image(base64_string, upload_dir, isFront):
    try:
        #Decodificación del string base64 
        image_data = base64.b64decode(base64_string)
        #Conversión de los datos decodificados a un array de numpy
        np_array = np.frombuffer(image_data, np.uint8)
        #Decodificación de la imagen desde el array de numpy por medio de OpenCV
        image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        #Modificación del nombre de la imagen dependiendo de si es delantera o trasera
        if isFront:
            filename = "decoded_front_image.jpg"
        else:
            filename = "decoded_back_image.jpg"
        #Generación del path de guardado de la imagen y guardado de la imagen decodificada
        upload_path = os.path.join(upload_dir, filename)
        cv2.imwrite(upload_path, image)
        return upload_path, filename
    except Exception as e:
        return None, None
    
def bruteforce_ocr(imgF, imgB, output_folder):
  #output_folder es "recorte/"
  texts_extracted = []
  full_front_path = (os.path.join(output_folder, "id_front.jpg"))
  full_back_path = (os.path.join(output_folder, "id_back.jpg"))
  cv2.imwrite(full_front_path, imgF)
  cv2.imwrite(full_back_path, imgB)

  result_front = ocr.predict(input = full_front_path)
  for res_f in result_front:
    res_f.save_to_json(output_folder)
  result_back = ocr.predict(input = full_back_path)
  for res_b in result_back:
    res_b.save_to_json(output_folder)
  os.remove(full_front_path)
  os.remove(full_back_path)
  json_front = os.path.join(output_folder, 'id_front_res.json')
  json_back = os.path.join(output_folder, 'id_back_res.json')
  with open(json_front, 'r') as f:
    data_front = jsonlib.load(f)
    textsf = data_front.get("rec_texts", [])
    texts_extracted += textsf
  with open(json_back, 'r') as f:
    data_back = jsonlib.load(f)
    textsb = data_back.get("rec_texts", [])
    texts_extracted += textsb
  os.remove(json_front)
  os.remove(json_back)
  return texts_extracted