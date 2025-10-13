from utils import ocr
import image_modification
import data_transformation
import base64
import numpy as np
import os
import cv2
import json as jsonlib
import re
import pandas as pd
from difflib import SequenceMatcher

def parse_data(data_str,type_toparse):
  match type_toparse:
    case 'name':
      name = data_str.split()
      if len(name) >= 3:
        apellidoM = name[-2]
        apellidoP = name[-3]
        nombre = name[-1]
      else: return '', '', ''
      return nombre, apellidoP, apellidoM
    case 'addre':
      addre = data_str.split()
      addre = addre[1:]
      addre = ''.join(addre)
      addre = re.sub(r'[^A-Za-z0-9,.]', '', addre)
      pattern = r'(\b([a-zA-Z0-9,.]+?\d{1,4})([a-zA-Z0-9,.]+?\d{5})(.+)$)'
      matched = re.match(pattern, addre)
      if matched:
        calle = matched.group(2)
        colonia = matched.group(3)
        ciudad = matched.group(4)
      else:
        calle = ''
        colonia = ''
        ciudad = ''
      return calle, colonia, ciudad
    case 'key':
      if len(data_str) == 0:
        return ''
      key = data_str.split()
      key = ' '.join(key)
      pattern = r'([a-zA-Z]{6}\d{8}[a-zA-Z]\d{3})'
      key = re.search(pattern, key)
      if key:
        key = key.group()
        #print(key)
        return key
      else:
        #SEGUNDO INTENTO EN CASO DE QUE CLAVE DE ELECTOR VAYA JUNTO AL DATO DE LA CLAVE
        second_try = re.compile(r"[A-Z]+\s*([a-zA-Z]{6}\d{8}[a-zA-Z]\d{3})")
        key = re.search(second_try, data_str)
        if key:
          key = key.group(1)
          return key
        else:
          third_try = re.compile(r"(?:[A-Z]+\s*)+([a-zA-Z]{6}\d{8}[a-zA-Z]\d{3})")
          key = re.search(third_try, data_str)
          if key:
            key = key.group(2)
            return key
          else:
            return ''
    case 'sex':
      pattern = r'SEXO\s*([HM])'
      sex = re.search(pattern, data_str)
      if sex:
        sex = sex.group(1)
        return sex
      else: return ''
    case 'back_code':
      back_code = data_str.split()
      back_code = ''.join(back_code)
      back_code = re.sub(r'[^A-Za-z0-9<]', '', back_code)
      #pattern = re.compile(r'[A-Za-z0-9]{5}+(\d{9})\d<<?(\d{13})')
      pattern = re.compile(r'[A-Za-z0-9]{5}(\d{9})\d<<?(\d{13})')
      matched = re.search(pattern, back_code)
      if matched:
        cic = matched.group(1)
        ocr = matched.group(2)
        id_ciudadano = ocr[4:13]
        return cic, ocr, id_ciudadano
      else: return '','',''
    case 'roi1':
      revisit_section = True
      roi1 = data_str.split()
      if len(roi1) < 22:
        curp, fecha, seccion = '', '', ''
        print("El texto recibido es muy corto")
      #Busca la seccion entre los últimos 22 elementos de la lista
      #Esto ya que hay veces en las que se pueden hacer detecciones muy largas
      #que pueden hacer que se pierda la visibilidad del apartado de seccion
      #(Ejemplo: Se lee la parte de quien se encuentra en el cargo de secretario ejecutivo
      #del INE, aumentando la longitud de todo el texto leído de la credencial)
      section_split = roi1[-22:]
      for string in section_split:
        if string.isdigit() and len(string) == 4:
          seccion = string
          revisit_section = False
      roi1 = ' '.join(roi1)
      pattern_curp = re.compile(r'\b[A-Z]{4}'r'(?:\d{2}(?:0[1-9]|1[0-2])'r'(?:0[1-9]|[12]\d|3[01]))'r'[HM]'r'(?:AS|BC|BS|CC|CL|CM|CS|CH|DF|DG|GT|GR|HG|JC|MC|MN|MS|NT|NL|OC|PL|QT|QR|SP|SL|SR|TC|TS|TL|VZ|YN|ZS|NE)'r'[A-Z]{3}'r'[A-Z0-9]{2}\b')
      pattern_fecha = r"(\d{2})/(\d{2})/(\d{4})"
      pattern_seccion = r"\b\d{4}\b"
      curp = re.search(pattern_curp, roi1)
      if curp:
        curp = curp.group()
      else:
        curp = ''
      fecha = re.search(pattern_fecha, roi1)
      if fecha:
        fecha = fecha.group(3) + '-' + fecha.group(2) + '-' + fecha.group(1)
      else:
        fecha = ''
      if revisit_section:
        print("Buscando por RegEx la seccion")
        seccion = re.search(pattern_seccion, roi1)
        if seccion:
          print("Seccion no encontrada")
          seccion = ''
      return curp, fecha, seccion
    case 'roi2':
      roi2 = data_str.split()
      roi2 = ' '.join(roi2)
      pattern_vigencia = r"\b\d{4}-(\d{4})\b"
      pattern_registro = r"\b(\d{4})(\d{2})\b"

      año_vigencia = re.search(pattern_vigencia, roi2)
      if año_vigencia:
        ano_vigencia = año_vigencia.group(1)
      else:
        ano_vigencia = ''
      año_registro = re.search(pattern_registro, roi2)
      if año_registro:
        ano_registro = año_registro.group(1)
        mes_registro = año_registro.group(2)
      else:
        ano_registro = ''
        mes_registro = ''
      return ano_vigencia, ano_registro, mes_registro
    case 'curp':
      curp = data_str.split()
      curp = ' '.join(curp)
      pattern_curp = re.compile(r'\b[A-Z]{4}'r'(?:\d{2}(?:0[1-9]|1[0-2])'r'(?:0[1-9]|[12]\d|3[01]))'r'[HM]'r'(?:AS|BC|BS|CC|CL|CM|CS|CH|DF|DG|GT|GR|HG|JC|MC|MN|MS|NT|NL|OC|PL|QT|QR|SP|SL|SR|TC|TS|TL|VZ|YN|ZS|NE)'r'[A-Z]{3}'r'[A-Z0-9]{2}\b')
      curp = re.search(pattern_curp, curp)
      if curp:
        curp = curp.group()
      else:
        #SEGUNDO INTENTO POR SI LA PALABRA CURP VA PEGADA AL PROPIO DATO DEL CURP
        pattern = re.compile(r"[A-Z]+\s*([A-Z]{4}\d{6}[HM][A-Z]{5}[0-9A-Z]\d)")
        texto_good = pattern.search(pattern,data_str)
        if texto_good:
          curp = texto_good.group(1)
        else:
          curp = ''
      return curp
    case 'birthdate':
      birthdate = data_str.split()
      birthdate = ' '.join(birthdate)
      pattern_fecha = r"(\d{2})/(\d{2})/(\d{4})"
      fecha = re.search(pattern_fecha, birthdate)
      if fecha:
        fecha = fecha.group(3) + '-' + fecha.group(2) + '-' + fecha.group(1)
      else:
        fecha = ''
      return fecha
    case 'seccion':
      idx = 0
      seccion = data_str.split()
      for string in seccion:
        s = SequenceMatcher(None, "SECCION", string).ratio()
        if s > 0.80:
          idx = seccion.index(string)
          #print(f"{string} : {s} :  {idx}")
          break
      if seccion[idx+1].isdigit() and len(seccion[idx+1]) == 4 and idx != 0:
          section = seccion[idx+1]
          #print(section)
      else:
        section = ''
      return section
    case 'registro':
      registro = data_str.split()
      registro = ' '.join(registro)
      pattern_registro_e = r"\b(\d{4})\s*(\d{2})\b"
      register_date = re.search(pattern_registro_e, registro)
      if register_date:
        ano_registro = register_date.group(1)
        mes_registro = register_date.group(2)
      else:
        ano_registro = ''
        mes_registro = ''
      return ano_registro, mes_registro
    case 'vigencia':
      idx = 0
      vigencia = data_str.split()
      for string in vigencia:
        s = SequenceMatcher(None, "VIGENCIA", string.upper()).ratio()
        if s > 0.80:
          idx = vigencia.index(string)
          #print(f"{string} : {s} :  {idx}")
          break
      if vigencia[idx+1].isdigit() and len(vigencia[idx+1]) == 4 and idx != 0:
        ano_vigencia = vigencia[idx+1]
        #print(ano_vigencia)
      else:
        ano_vigencia = ''
      return ano_vigencia
    case 'estado':
      idx = 0
      estado = data_str.split()
      #estado = ' '.join(estado)
      for string in estado:
        s = SequenceMatcher(None, "ESTADO", string.upper()).ratio()
        if s > 0.80:
          idx = estado.index(string)
          #print(f"{string} : {s} :  {idx}")
          break
      if estado[idx+1].isdigit() and len(estado[idx+1]) == 2 and idx != 0:
        estado = estado[idx+1]
        #print(estado)
      else:
        estado = ''
      return estado
    case 'municipio':
      idx = 0
      municipio = data_str.split()
      #municipio = ' '.join(municipio)
      for string in municipio:
        s = SequenceMatcher(None, "MUNICIPIO", string.upper()).ratio()
        if s > 0.80:
          idx = municipio.index(string)
          #print(f"{string} : {s} :  {idx}")
          break
      if municipio[idx+1].isdigit() and len(municipio[idx+1]) == 3 and idx != 0:
        municipio = municipio[idx+1]
        #print(municipio)
      else:
        municipio = ''
      return municipio
    case 'localidad':
      idx = 0
      localidad = data_str.split()
      #localidad = ' '.join(localidad)
      for string in localidad:
        s = SequenceMatcher(None, "LOCALIDAD", string.upper()).ratio()
        if s > 0.80:
          idx = localidad.index(string)
          #print(f"{string} : {s} :  {idx}")
      if localidad[idx+1].isdigit() and len(localidad[idx+1]) == 4 and idx != 0:
        localidad = localidad[idx+1]
        #print(localidad)
      else:
        localidad = ''
      return localidad
    case 'emision':
      idx = 0
      emision = data_str.split()
      #emision = ' '.join(emision)
      for string in emision:
        s = SequenceMatcher(None, "EMISION", string.upper()).ratio()
        if s > 0.80:
          idx = emision.index(string)
          #print(f"{string} : {s} :  {idx}")
          break
      if emision[idx+1].isdigit() and len(emision[idx+1]) == 4 and idx != 0:
        emission_e = emision[idx+1]
        #print(emission_e)
      else:
        emission_e = ''
      return emission_e
    
def data_comparison(joined_text, compiled_data, doc_type):
  for index, row in compiled_data.iterrows():
    for col, val in row.items():
      if val == "":
        match col:
          case 'nombre' | 'apellidoPaterno' | 'apellidoMaterno':
            nombre = ""
            apellidoP = ""
            apellidoM = ""
            if doc_type == 'G':
              split_copy = data_transformation.keyword_extract(joined_text, 'NOMBRE', doc_type)
              if len(split_copy) == 0 or len(split_copy) < 3 or split_copy == []:
                compiled_data['nombre'] = ""
                compiled_data['apellidoPaterno'] = ""
                compiled_data['apellidoMaterno'] = ""
              else:
                nombre = split_copy[2]
                apellidoP = split_copy[0]
                apellidoM = split_copy[1]
                nombre = nombre.upper()
                apellidoP = apellidoP.upper()
                apellidoM = apellidoM.upper()
            elif doc_type == 'E':
              #print(joined_text)
              text_name = []
              idx = 0
              for element in joined_text:
                element_upper = element.upper()
                s_text = SequenceMatcher(None, "FECHA DE NACIMIENTO", element_upper)
                if s_text.ratio() > 0.70:
                  idx = joined_text.index(element)
                  #print(f"{idx}: {element} {s_text.ratio()} ")
                  small_list = joined_text[idx:idx+8]
                  #print(small_list)
                  break
              if idx != 0:
                for new_element in small_list:
                  if (small_list.index(new_element) + 1) % 2 == 0 and len(text_name) <= 3:
                    if len(new_element) > 1:
                      new_element_up = new_element.upper()
                      if (SequenceMatcher(None, "DOMICILIO", new_element_up).ratio()) > 0.65:
                        text_name.append(small_list[small_list.index(new_element) - 1])
                      else:
                        text_name.append(new_element)
                    else:
                      index_small = small_list.index(new_element)
                      text_name.append(small_list[index_small + 1])
              for element in text_name:
                if (SequenceMatcher(None, "NOMBRE", element.upper()).ratio()) > 0.65:
                  text_name.remove(element)
              if len(text_name) > 2:
                nombre = text_name[2]
                apellidoP = text_name[0]
                apellidoM = text_name[1]
                nombre = nombre.upper()
                apellidoP = apellidoP.upper()
                apellidoM = apellidoM.upper()
                #final_name = text_name[2] + ' ' + text_name[1] + ' ' + text_name[0]
              #print(final_name)
            compiled_data['nombre'] = nombre
            compiled_data['apellidoPaterno'] = apellidoP
            compiled_data['apellidoMaterno'] = apellidoM
          case 'calle' | 'colonia' | 'ciudad':
            calle = ""
            colonia = ""
            ciudad = ""
            split_copy = data_transformation.keyword_extract(joined_text, 'DOMICILIO', doc_type)
            if len(split_copy) == 0 or len(split_copy) < 3 or split_copy == []:
              compiled_data['calle'] = ""
              compiled_data['colonia'] = ""
              compiled_data['ciudad'] = ""
            else:
              calle = split_copy[0] #
              colonia = split_copy[1]
              ciudad = split_copy[2]
              calle = calle.upper()
              colonia = colonia.upper()
              ciudad = ciudad.upper()
              compiled_data['calle'] = calle
              compiled_data['colonia'] = colonia
              compiled_data['ciudad'] = ciudad
          case 'claveElector':
            joined_copy = ' '.join(joined_text)
            compiled_data['claveElector'] = parse_data(joined_copy, 'key')
          case 'curp' | 'fechaNacimiento' | 'seccion':
            curp = ""
            fecha_nacimiento = ""
            seccion = ""
            if doc_type == 'G':
              joined_copy = ' '.join(joined_text)
              curp, fecha_nacimiento, seccion = parse_data(joined_copy, 'roi1')
              compiled_data['curp'] = curp
              compiled_data['fechaNacimiento'] = fecha_nacimiento
              compiled_data['seccion'] = seccion
            elif doc_type == 'E':
              joined_copy = ' '.join(joined_text)
              curp = parse_data(joined_copy, 'curp')
              fecha_nacimiento = parse_data(joined_copy, 'birthdate')
              seccion = parse_data(joined_copy, 'seccion')
              compiled_data['curp'] = curp
              compiled_data['fechaNacimiento'] = fecha_nacimiento
              compiled_data['seccion'] = seccion
          case 'registro' | 'vigencia':
            ano_registro = ""
            mes_registro = ""
            ano_vigencia = ""
            if doc_type == 'G':
              joined_copy = ' '.join(joined_text)
              ano_vigencia, ano_registro, mes_registro = parse_data(joined_copy, 'roi2')
              ano_registro = ano_registro + '-' + mes_registro
              compiled_data['registro'] = ano_registro
              compiled_data['vigencia'] = ano_vigencia
            elif doc_type == 'E':
              joined_copy = ' '.join(joined_text)
              ano_registro, mes_registro = parse_data(joined_copy, 'registro')
              ano_registro = ano_registro + '-' + mes_registro
              compiled_data['registro'] = ano_registro
              ano_vigencia = parse_data(joined_copy, 'vigencia')
              compiled_data['vigencia'] = ano_vigencia
          case 'sexo':
            sexo = ""
            joined_copy = ' '.join(joined_text)
            sexo = parse_data(joined_copy, 'sex')
            compiled_data['sexo'] = sexo
          case 'estado' :
            estado = ""
            joined_copy = ' '.join(joined_text)
            estado = parse_data(joined_copy, 'estado')
            #print(f"Estado: {estado}")
            compiled_data['estado'] = estado
          case 'municipio':
            municipio = ""
            joined_copy = ' '.join(joined_text)
            municipio = parse_data(joined_copy, 'municipio')
            #print(f"Municipio: {municipio}")
            compiled_data['municipio'] = municipio
          case 'localidad':
            localidad = ""
            joined_copy = ' '.join(joined_text)
            localidad = parse_data(joined_copy, 'localidad')
            #print(f"Localidad: {localidad}")
            compiled_data['localidad'] = localidad
          case 'emision':
            emision = ""
            joined_copy = ' '.join(joined_text)
            emision = parse_data(joined_copy, 'emision')
            #print(f"Emision: {emision}")
            compiled_data['emision'] = emision
          case 'cic' | 'ocr' | 'idCiudadano':
            cic = ""
            ocr = ""
            id_ciudadano = ""
            joined_copy = ' '.join(joined_text)
            cic, ocr, id_ciudadano = parse_data(joined_copy, 'back_code')
            compiled_data['cic'] = cic
            compiled_data['ocr'] = ocr
            compiled_data['idCiudadano'] = id_ciudadano
  return compiled_data

def data_obtention2(imgF, imgB, doc_type):
    if doc_type == 'E':
      type_id = 'IFE'
    else:
      type_id = 'INE'

    output_folder = "recorte"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    joined_text = image_modification.bruteforce_ocr(imgF, imgB, output_folder)

    if doc_type == 'G':
        compiled_data = pd.DataFrame({
        'tipo':[type_id],
        'subtipo':[doc_type],
        'nombre': [""],
        'apellidoPaterno': [""],
        'apellidoMaterno': [""],
        'calle': [""],
        'colonia': [""],
        'ciudad': [""],
        'claveElector': [""],
        'curp': [""],
        'fechaNacimiento': [""],
        'seccion': [""],
        'registro': [""],
        'vigencia': [""],
        'sexo': [""],
        'cic': [""],
        'ocr': [""],
        'idCiudadano': [""]
        })
    elif doc_type == 'E':
        compiled_data = pd.DataFrame({
        'tipo':[type_id],
        'subtipo':[doc_type],
        'nombre': [""],
        'apellidoPaterno': [""],
        'apellidoMaterno': [""],
        'calle': [""],
        'colonia': [""],
        'ciudad': [""],
        'estado': [""],
        'municipio': [""],
        'localidad': [""],
        'claveElector': [""],
        'curp': [""],
        'fechaNacimiento': [""],
        'seccion': [""],
        'registro': [""],
        'vigencia': [""],
        'emision': [""],
        'sexo': [""],
        'cic': [""],
        'ocr': [""],
        'idCiudadano': [""]
        })

    compiled_data = data_comparison(joined_text, compiled_data, doc_type)
    validation_data = data_transformation.mrz_validation(compiled_data, joined_text, doc_type)
    final_json = data_transformation.to_Json(compiled_data, validation_data)
    return final_json