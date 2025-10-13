from pydantic import BaseModel

#Clase "ImageContainer" para definir el formato de las imágenes a recibir (base64)
class ImageContainer(BaseModel):
    front: str
    back: str

class TimeoutException(Exception): pass