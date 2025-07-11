from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import logging

app = FastAPI()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)


logger = logging.getLogger("ContainerShip-API")

@app.get("/")
def read_root():
    return {"message": "Welcome to ContainerShip!"}




@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    dockerfile_contents_bytes = await file.read()
    file_size_in_bytes = len(dockerfile_contents_bytes)
    dockerfile_contents_as_string = dockerfile_contents_bytes.decode('utf-8')


    logger.info(f"Received file: {file.filename}, size: {file_size_in_bytes} bytes")
    logger.info(f"File contents: {dockerfile_contents_as_string}")
    
    return JSONResponse(content={
        "filename": file.filename,
        "content_type": file.content_type,
        "file_size_bytes": file_size_in_bytes
    })