import utils
import services
import schema
#from services import read_root, process_image
from fastapi import FastAPI, HTTPException, UploadFile, File, Response, Security, Depends
from fastapi.security.api_key import APIKeyHeader, APIKey
#from pydantic import BaseModel
from fastapi import FastAPI

#Se inicializa FastAPI
app = FastAPI()
app.include_router(services.router)