"""FastAPI server for AgentCore Runtime."""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from main import agent
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI()


@app.post("/invocations")
async def invocations(request: Request):
    """Handle agent invocations from AgentCore Runtime."""
    try:
        body = await request.json()
        logger.info(f"Received request: {body}")

        # Extract input from request
        user_input = body.get("input", "")
        user_id = body.get("userId", "anonymous")
        session_id = body.get("sessionId")

        # Invoke the Strands agent (agent is callable via __call__)
        result = agent(user_input)

        # Extract text from AgentResult object
        response_text = str(result.content) if hasattr(result, 'content') else str(result)

        # Return response in AgentCore Runtime format
        return JSONResponse({
            "output": {
                "message": {
                    "role": "assistant",
                    "content": [{"text": response_text}]
                }
            },
            "sessionId": session_id or "new-session"
        })

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.get("/ping")
async def ping():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
