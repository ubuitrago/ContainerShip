from fastapi import FastAPI, File, UploadFile, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from api.process import DockerfileAnalysis
from api.utils import logger
from api.mcp_client import (
    web_search_docker, 
    optimize_dockerfile, 
    check_security_best_practices,
    search_dockerfile_examples,
    create_client
)


class DockerfileAnalysisRequest(BaseModel):
    content: str


# Initialize MCP client at startup
client = None

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


@app.on_event("startup")
async def startup_event():
    """Initialize the MCP client on startup."""
    global client
    client = await create_client()


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up the MCP client on shutdown."""
    global client
    if client:
        await client.close()


@app.get("/")
def read_root():
    """Root endpoint that returns a welcome message."""
    return {"message": "Welcome to ContainerShip!"}

@app.post("/analyze/")
async def analyze_dockerfile(request: DockerfileAnalysisRequest):
    """
    Analyze a Dockerfile and provide clause-by-clause recommendations with optimized version.
    
    Returns:
    - original_dockerfile: The original Dockerfile content
    - clauses: List of analyzed clauses with recommendations
    - optimized_dockerfile: An optimized version incorporating recommendations
    """
    try:
        analysis = DockerfileAnalysis(request.content)
        await analysis.process(client)
        
        return analysis.as_dict()
    
    except Exception as e:
        logger.error(f"Error analyzing Dockerfile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing Dockerfile: {str(e)}")


@app.post("/stream-analysis/")
async def stream_dockerfile_analysis(request: DockerfileAnalysisRequest):
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
    """
    Endpoint to upload a Dockerfile and process its contents.
    Returns the same format as /analyze/ endpoint.
    """
    try:
        dockerfile_contents_bytes = await file.read()
        dockerfile_contents_as_string = dockerfile_contents_bytes.decode('utf-8')

        logger.info(f"Received file: {file.filename}, size: {len(dockerfile_contents_bytes)} bytes")
        
        analysis = DockerfileAnalysis(dockerfile_contents_as_string)
        await analysis.process(client)
        
        return analysis.as_dict()
        
    except Exception as e:
        logger.error(f"Error processing uploaded file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


# Enhanced MCP-powered endpoints
class DockerfileRequest(BaseModel):
    content: str
    technology: str = ""


class WebSearchRequest(BaseModel):
    query: str
    max_results: int = 5


@app.post("/analyze/comprehensive/")
async def comprehensive_dockerfile_analysis(request: DockerfileRequest):
    """Get comprehensive Dockerfile analysis using all MCP tools."""
    try:
        analysis = DockerfileAnalysis(request.content)
        result = await analysis.get_comprehensive_analysis()
        
        logger.info(f"Comprehensive analysis completed for {analysis.technology} Dockerfile")
        return JSONResponse(content=result, status_code=200)
        
    except Exception as e:
        logger.error(f"Error in comprehensive analysis: {e}")
        return JSONResponse(
            content={"error": f"Analysis failed: {str(e)}"}, 
            status_code=500
        )


@app.post("/optimize/")
async def optimize_dockerfile_endpoint(request: DockerfileRequest):
    """Get Dockerfile optimization recommendations using MCP."""
    try:
        client = await create_client()
        async with client:
            result = await optimize_dockerfile(client, request.content, request.technology)
            
        logger.info("Dockerfile optimization completed")
        return JSONResponse(
            content={"optimization_suggestions": result, "technology": request.technology}, 
            status_code=200
        )
        
    except Exception as e:
        logger.error(f"Error in optimization: {e}")
        return JSONResponse(
            content={"error": f"Optimization failed: {str(e)}"}, 
            status_code=500
        )


@app.post("/security/")
async def security_analysis_endpoint(request: DockerfileRequest):
    """Get security analysis for Dockerfile using MCP."""
    try:
        client = await create_client()
        async with client:
            result = await check_security_best_practices(client, request.content, request.technology)
            
        logger.info("Security analysis completed")
        return JSONResponse(
            content={"security_analysis": result, "technology": request.technology}, 
            status_code=200
        )
        
    except Exception as e:
        logger.error(f"Error in security analysis: {e}")
        return JSONResponse(
            content={"error": f"Security analysis failed: {str(e)}"}, 
            status_code=500
        )


@app.post("/examples/")
async def dockerfile_examples_endpoint(technology: str, use_case: str = "production"):
    """Get Dockerfile examples for a specific technology using MCP."""
    try:
        client = await create_client()
        async with client:
            result = await search_dockerfile_examples(client, technology, use_case)
            
        logger.info(f"Examples found for {technology}")
        return JSONResponse(
            content={"examples": result, "technology": technology, "use_case": use_case}, 
            status_code=200
        )
        
    except Exception as e:
        logger.error(f"Error finding examples: {e}")
        return JSONResponse(
            content={"error": f"Example search failed: {str(e)}"}, 
            status_code=500
        )


@app.post("/web-search/")
async def web_search_endpoint(request: WebSearchRequest):
    """Search the web for Docker-related information using MCP."""
    try:
        client = await create_client()
        async with client:
            result = await web_search_docker(client, request.query, request.max_results)
            
        logger.info(f"Web search completed for: {request.query}")
        return JSONResponse(
            content={"search_results": result, "query": request.query}, 
            status_code=200
        )
        
    except Exception as e:
        logger.error(f"Error in web search: {e}")
        return JSONResponse(
            content={"error": f"Web search failed: {str(e)}"}, 
            status_code=500
        )