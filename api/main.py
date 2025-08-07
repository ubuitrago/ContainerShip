from fastapi import FastAPI, File, UploadFile, Request, HTTPException, Form
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
    create_client,
    ask_docker_docs
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
async def analyze_dockerfile(file: UploadFile = File(...)):
    """
    Analyze a Dockerfile via file upload (non-streaming version for compatibility).
    
    Returns:
    - original_dockerfile: The original Dockerfile content
    - clauses: List of analyzed clauses with recommendations  
    - optimized_dockerfile: An optimized version incorporating recommendations
    """
    try:
        # File upload method
        dockerfile_content_bytes = await file.read()
        dockerfile_content = dockerfile_content_bytes.decode('utf-8')
        logger.info(f"Received file: {file.filename}, size: {len(dockerfile_content_bytes)} bytes")
        
        # Process the Dockerfile
        analysis = DockerfileAnalysis(dockerfile_content)
        await analysis.process(client)
        
        return analysis.as_dict()
    
    except Exception as e:
        logger.error(f"Error analyzing Dockerfile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing Dockerfile: {str(e)}")


@app.post("/analyze/stream/")
async def analyze_dockerfile_stream(file: UploadFile = File(...)):
    """
    Analyze a Dockerfile via file upload with progressive streaming.
    
    Returns streaming JSON objects with:
    - original_dockerfile: The original Dockerfile content (immediate)
    - clauses: List of analyzed clauses with recommendations (progressive)
    - optimized_dockerfile: An optimized version (final)
    """
    try:
        # File upload method
        dockerfile_content_bytes = await file.read()
        dockerfile_content = dockerfile_content_bytes.decode('utf-8')
        logger.info(f"Received file: {file.filename}, size: {len(dockerfile_content_bytes)} bytes")
        
        # Process the Dockerfile with streaming
        analysis = DockerfileAnalysis(dockerfile_content)
        
        async def generate_analysis_stream():
            import json
            
            # 1. Immediately return the original Dockerfile
            yield f"data: {json.dumps({'type': 'original_dockerfile', 'data': dockerfile_content})}\n\n"
            
            # 2. Send clause structure immediately with placeholder recommendations
            clause_structure = []
            for i, clause in enumerate(analysis.clauses):
                clause_dict = clause.as_dict()
                clause_dict['recommendations'] = "⏳ Waiting for recommendation..."
                clause_structure.append(clause_dict)
            
            yield f"data: {json.dumps({'type': 'clause_structure', 'data': clause_structure})}\n\n"
            
            # 3. Stream clause analysis as it happens
            client = await create_client()
            async with client:
                # Analyze each clause progressively
                for i, clause in enumerate(analysis.clauses):
                    clause.technology = analysis.technology
                    
                    # Get recommendations for this clause
                    try:
                        doc_question = f"Best practices for this {analysis.technology} Dockerfile clause:\n{clause.content}"
                        clause.recommendations = await ask_docker_docs(client, doc_question)
                    except Exception as e:
                        clause.recommendations = f"Could not get recommendations: {e}"
                    
                    # Stream this clause update
                    clause_data = {
                        'type': 'clause_update',
                        'data': {
                            'index': i,
                            'clause': clause.as_dict(),
                            'total_clauses': len(analysis.clauses)
                        }
                    }
                    yield f"data: {json.dumps(clause_data)}\n\n"
                
                # 4. Generate and stream the optimized Dockerfile
                try:
                    await analysis._generate_optimized_dockerfile(client)
                    optimized_data = {
                        'type': 'optimized_dockerfile',
                        'data': analysis.optimized_file_contents
                    }
                    yield f"data: {json.dumps(optimized_data)}\n\n"
                except Exception as e:
                    error_data = {
                        'type': 'error',
                        'data': f"Could not generate optimized Dockerfile: {e}"
                    }
                    yield f"data: {json.dumps(error_data)}\n\n"
                
                # 5. Final completion signal
                completion_data = {
                    'type': 'complete',
                    'data': 'Analysis complete'
                }
                yield f"data: {json.dumps(completion_data)}\n\n"
        
        return StreamingResponse(
            generate_analysis_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
            }
        )
    
    except Exception as e:
        logger.error(f"Error analyzing Dockerfile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing Dockerfile: {str(e)}")


# Optional: Keep streaming analysis as a separate endpoint for real-time feedback
@app.post("/analyze/stream/")
async def stream_dockerfile_analysis(request: DockerfileAnalysisRequest):
    """Stream analysis results in real-time for progressive feedback."""
    try:
        logger.info("Starting Dockerfile analysis streaming...")
        logger.info(f"Received Dockerfile contents: {request.content[:100]}...")
        
        # Create the analysis object
        analysis = DockerfileAnalysis(request.content)
        
        # Create an async generator for streaming
        async def generate_analysis():
            async for chunk in analysis.annotate():
                if chunk:
                    yield chunk
        
        return StreamingResponse(
            generate_analysis(), 
            media_type="text/plain",
            headers={"Cache-Control": "no-cache"}
        )
    except Exception as e:
        logger.error(f"Error in streaming analysis: {e}")
        async def error_stream():
            yield f"Error analyzing Dockerfile: {str(e)}"
        return StreamingResponse(error_stream(), media_type="text/plain")


# Additional models for legacy endpoints
class DockerfileRequest(BaseModel):
    content: str
    technology: str = ""


class WebSearchRequest(BaseModel):
    query: str
    max_results: int = 5


# Legacy endpoints - deprecated but kept for backward compatibility
@app.post("/analyze/comprehensive/")
async def comprehensive_dockerfile_analysis(request: DockerfileRequest):
    """
    DEPRECATED: Use /analyze/ instead.
    Get comprehensive Dockerfile analysis using all MCP tools.
    """
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