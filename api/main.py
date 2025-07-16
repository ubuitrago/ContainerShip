from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from process import DockerfileContents
from utils import logger

app = FastAPI()

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
    dockerfile_contents_as_lines = dockerfile_contents_as_string.split("\n")
    guard_line = "-"* max(len(line) for line in dockerfile_contents_as_lines)

    logger.info(f"Received file: {file.filename}, size: {file_size_in_bytes} bytes")
    logger.info(f"File contents are logged line-by-line below.")
    logger.info(guard_line)
    for line in dockerfile_contents_as_lines:
        logger.info(line)
    logger.info(guard_line)

    dockerfile_contents = DockerfileContents(dockerfile_contents_as_string)
    return JSONResponse(content=dockerfile_contents.as_dict(), status_code=200)