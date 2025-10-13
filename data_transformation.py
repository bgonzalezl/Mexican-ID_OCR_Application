import os
import json as jsonlib
import re
import pandas as pd
from difflib import SequenceMatcher

def keyword_extract(text, keyword, doc_type, n=3, skip="SEXO"):
  try:
    idx = text.index(keyword)
  except ValueError:
    idx = 0
    #print(f"Keyword '{keyword}' not found in text.")
    if keyword == 'DOMICILIO':
      for element in text:
        s = SequenceMatcher(None, "DOMICILIO", element).ratio()
        s_2 = SequenceMatcher(None, "DOMCUO", element).ratio()
        if s > 0.80 or s_2 > 0.80:
          idx = text.index(element)
          #print(f"{element} : {s} :  {idx}")
    if keyword == 'NOMBRE':
      for element in text:
        s = SequenceMatcher(None, "NOMBRE", element).ratio()
        if s > 0.80:
          idx = text.index(element)
          #print(f"{element} : {s} :  {idx}")

  if doc_type == 'G':
    results = []
    for i in range(1, n+2):
      if idx+i < len(text) and idx!= 0:
        val = text[idx+i]
        if val.startswith(skip):
          continue
        else:
          results.append(val)
      if len(results) == n:
        break

  elif doc_type == 'E' and keyword == 'DOMICILIO':
    results = []
    for i in range(1, 4):
      if idx+i < len(text) and idx!= 0:
        val = text[idx+i]
        if val.startswith(skip):
          continue
        else:
          results.append(val)
  return results

def to_Json(compiled_data, validation_data):
  OUTPUT_DIR = 'Output'
  if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
  nombre = compiled_data['nombre'].values[0]
  nombre = re.sub('[^A-Za-z0-9]+', '', nombre)
  apellidoP = compiled_data['apellidoPaterno'].values[0]
  apellidoP = re.sub('[^A-Za-z0-9]+', '', apellidoP)
  apellidoM = compiled_data['apellidoMaterno'].values[0]
  apellidoM = re.sub('[^A-Za-z0-9]+', '', apellidoM)
  curp = compiled_data['curp'].values[0]
  curp = re.sub('[^A-Za-z0-9]+', '', curp)
  #if nombre != "DOMICILIO":
    #print(nombre)
    #print(apellidoP)
    #print(apellidoM)
    #print(curp)
    #json_path = os.path.join(OUTPUT_DIR, f'{str(nombre)}_{str(apellidoP)}_{str(apellidoM)}_{str(curp)}_data.json')
  #else:
    #print(apellidoP)
    #print(apellidoM)
    #print(curp)
    #json_path = os.path.join(OUTPUT_DIR, f'{str(apellidoP)}_{str(apellidoM)}_{str(curp)}_data.json')


  compiled_json = compiled_data.to_dict(orient="records")[0]
  validation_json = validation_data.to_dict(orient="records")[0]
  compiled_json["validacionMRZ"] = validation_json

  curpCheck = compiled_json["curp"]
  nombreCheck = compiled_json["nombre"]
  apellidoPaternoCheck = compiled_json["apellidoPaterno"]
  apellidoMaternoCheck = compiled_json["apellidoMaterno"]
  fullnameCheck = nombreCheck + apellidoPaternoCheck + apellidoMaternoCheck
  clave_electorCheck = compiled_json["claveElector"]
  if fullnameCheck == "":
    if curpCheck == "" and clave_electorCheck == "":
      json_data = None
      return json_data

  final_json = [compiled_json]
  #with open(json_path, "w") as outfile:
  #  jsonlib.dump(final_json, outfile, indent=4)
  json_data = jsonlib.dumps(final_json, indent=4, ensure_ascii=False)
  #print(json_data)
  return json_data

def name_similarity_ratio(text_mzr,nombre):
  clean_mzr = re.sub(r'<|>', ' ', text_mzr)
  s1 = SequenceMatcher(None, nombre, text_mzr).ratio()
  s2 = SequenceMatcher(None, nombre, clean_mzr).ratio()
  if s1 > 0.70 or s2 > 0.70:
    return "OK"
  elif s1 < 0.25 or s2 < 0.25:
    return "ERROR"
  else:
    return "WARNING"
  
def mrz_validation(compiled_data, joined_text, doc_type):
  #print(joined_text)
  nombre = compiled_data['nombre'].values[0]
  apellidoP = compiled_data['apellidoPaterno'].values[0]
  apellidoM = compiled_data['apellidoMaterno'].values[0]
  registro = compiled_data['registro'].values[0]
  vigencia = compiled_data['vigencia'].values[0]
  vigencia = vigencia[2:4]
  sexo = compiled_data['sexo'].values[0]
  cic = compiled_data['cic'].values[0]
  fechaNacimiento = compiled_data['fechaNacimiento'].values[0]
  registro_separated = registro.split('-')
  registro_mes = registro_separated[1]
  if doc_type == 'E':
    emision_real = compiled_data['emision'].values[0]

  mrz = joined_text[-4:]
  validation_data = pd.DataFrame({
    'fechaNacimiento': ['ERROR'],
    'sexo': ['ERROR'],
    'vigencia': ['ERROR'],
    'emision': ['ERROR'],
    'nombre': ['ERROR']
  })
  for element in mrz:
    if sexo != "" and vigencia != "" and registro != "":
      patronVal = re.compile(r"\d+([HM])(\d{6})\w+")
      patronReg = re.compile(r"<(\d{2})<")
      sexoVigencia = patronVal.search(element)
      registroObtained = patronReg.search(element)
      if sexoVigencia:
        año_vigencia = sexoVigencia[2]
        if sexoVigencia[1] == sexo:
          validation_data['sexo'] = 'OK'
        if año_vigencia[0:2] == vigencia:
          validation_data['vigencia'] = 'OK'
      if registroObtained:
        if registroObtained[1] == registro_mes:
          validation_data['emision'] = 'OK'
    else:
      if sexo == "" or vigencia == "":
        patronVal = re.compile(r"\d+([HM])(\d{6})\w+")
        sexoVigencia = patronVal.search(element)
        if sexoVigencia:
          sexo = sexoVigencia[1]
          compiled_data['sexo'] = sexo
          validation_data['sexo'] = 'OK'
          vigencia = sexoVigencia[2]
          if vigencia[0:2] > 25:
            vigencia = "19" + vigencia[0:2]
          else:
            compiled_data['vigencia'] = "20" + vigencia[0:2]
          validation_data['vigencia'] = 'OK'
      if registro == "":
        patronReg = re.compile(r"<(\d{2})<")
        registroObtained = patronReg.search(element)
        if registroObtained:
          if registroObtained[1] == registro_mes:
            registro = registroObtained[1]
            compiled_data['registro'] = registro
            validation_data['emision'] = 'OK'

    if fechaNacimiento != "":
      fechaVal = fechaNacimiento.split('-')
      año = fechaVal[0]
      mes = fechaVal[1]
      dia = fechaVal[2]
      new_format = año[2:4] + mes + dia
      if new_format in element:
        validation_data['fechaNacimiento'] = 'OK'
    else:
      patron_birth = re.compile(r"(\d{6})([HM])\d+")
      birth_search = patron_birth.search(element)
      if birth_search:
        fechaNacimiento = birth_search.group(1)
        if fechaNacimiento[0:2] > 25:
          compiled_data['fechaNacimiento'] = '19' + fechaNacimiento[0:2] + '-' + fechaNacimiento[2:4] + '-' + fechaNacimiento[4:6]
        else:
          compiled_data['fechaNacimiento'] = '20' + fechaNacimiento[0:2] + '-' + fechaNacimiento[2:4] + '-' + fechaNacimiento[4:6]
        validation_data['fechaNacimiento'] = 'OK'


    if nombre != "" and apellidoP != "" and apellidoM != "":
      if nombre != "DOMICILIO":
        nombre_ordenado = apellidoP + apellidoM + nombre
      else:
        nombre_ordenado = apellidoP + apellidoM
      nombre_ordenado = nombre_ordenado.split()
      nombre_ordenado = ' '.join(nombre_ordenado)
      estado_val = name_similarity_ratio(element, nombre_ordenado)
      #print(f"Estado de la validación por similaridad: {estado_val}")
      validation_data['nombre'] = estado_val
    else:
      clean_mzr = re.sub(r'<|>', ' ', element)
      clean_mzr = clean_mzr.split()
      if clean_mzr[0].isalpha() and clean_mzr[1].isalpha():
        if len(clean_mzr) > 2:
          nombre = clean_mzr[2]
          nombre = nombre.upper()
          apellidoP = clean_mzr[0]
          apellidoP = apellidoP.upper()
          apellidoM = clean_mzr[1]
          apellidoM = apellidoM.upper()
          compiled_data['nombre'] = nombre
          compiled_data['apellidoPaterno'] = apellidoP
          compiled_data['apellidoMaterno'] = apellidoM
          validation_data['nombre'] = 'OK'
        else:
          if nombre != "":
            apellidoP = clean_mzr[0]
            apellidoP = apellidoP.upper()
            apellidoM = clean_mzr[1]
            apellidoM = apellidoM.upper()
            compiled_data['apellidoPaterno'] = apellidoP
            compiled_data['apellidoMaterno'] = apellidoM
            validation_data['nombre'] = 'OK'
          else:
            apellidoP = clean_mzr[0]
            apellidoP = apellidoP.upper()
            apellidoM = clean_mzr[1]
            apellidoM = apellidoM.upper()
            compiled_data['apellidoPaterno'] = apellidoP
            compiled_data['apellidoMaterno'] = apellidoM
            validation_data['nombre'] = 'WARNING'

    if doc_type == 'E' and emision_real == "":
      if vigencia != "":
        emision_real = int(vigencia) - 10
        compiled_data['emision'] = emision_real
        validation_data['emision'] = 'OK'

  #print(validation_data)

  return validation_data