from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging

app = FastAPI()
logger = logging.getLogger("uvicorn")

# Adjust this to match your frontend's URL
origins = [
    "http://localhost:5173",  # Vite dev server
    # You can add more origins here if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # or ["*"] to allow all origins (not recommended for production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    """Root endpoint that returns a welcome message."""
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
        "file_size_bytes": file_size_in_bytes,
        "contents": dockerfile_contents_as_string
    })