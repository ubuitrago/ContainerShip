from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import JSONResponse
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from api.process import DockerfileAnalysis
from api.utils import logger

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

@app.post("/analyze/")
async def stream_dockerfile_analysis(request: Request):
    """Stream analysis results in real-time."""
    try:
        # Get the raw JSON string from the request body
        contents = await request.json()
        
        logger.info("Starting Dockerfile analysis streaming...")
        # Log the contents for debugging
        logger.info(f"Received Dockerfile contents: {contents[:100]}...")
        
        # Create the analysis object (not async)
        analysis = DockerfileAnalysis(contents)
        
        # Create an async generator for streaming
        async def generate_analysis():
            async for chunk in analysis.annotate():
                # Ensure each chunk is properly formatted for streaming
                if chunk:
                    yield chunk
        
        return StreamingResponse(
            generate_analysis(), 
            media_type="text/plain",
            headers={"Cache-Control": "no-cache"}
        )
    except Exception as e:
        logger.error(f"Error in streaming analysis: {e}")
        # Return error as a stream
        async def error_stream():
            yield f"Error analyzing Dockerfile: {str(e)}"
        return StreamingResponse(error_stream(), media_type="text/plain")

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    """Endpoint to upload a Dockerfile and process its contents."""
    dockerfile_contents_bytes = await file.read()
    dockerfile_contents_as_string = dockerfile_contents_bytes.decode('utf-8')
    dockerfile_contents_as_lines = dockerfile_contents_as_string.split("\n")
    guard_line = "-" * max(len(line) for line in dockerfile_contents_as_lines)

    logger.info(f"Received file: {file.filename}, size: {len(dockerfile_contents_bytes)} bytes")
    logger.info(f"File contents are logged line-by-line below.")
    for line in [guard_line] + dockerfile_contents_as_lines + [guard_line]: logger.info(line)

    dockerfile_analysis = DockerfileAnalysis(dockerfile_contents_as_string)
    return JSONResponse(content=dockerfile_analysis.as_dict(), status_code=200)