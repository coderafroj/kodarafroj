from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from generator import ImageGenerator
import base64
from io import BytesIO
import uvicorn
import os
import time
import logging
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("KodarafrojAPI")

app = FastAPI(
    title="Kodarafroj Premium AI Image Generator",
    description="Production-grade AI image generation with Hinglish & Text Overlay support.",
    version="2.2.0"
)

# Enable CORS for website integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with your website URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global generator instance
generator = None

@app.on_event("startup")
async def startup_event():
    global generator
    try:
        generator = ImageGenerator()
        logger.info("Generator initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize generator: {e}")

class GenerateRequest(BaseModel):
    prompt: str = Field(..., example="Ek sher jungle mein baitha hai")
    steps: int = Field(default=4, ge=1, le=50)
    guidance_scale: float = Field(default=1.0, ge=1.0, le=20.0)
    width: int = Field(default=512, multiple_of=8)
    height: int = Field(default=512, multiple_of=8)
    enhance: bool = Field(default=True, description="Enable Kodarafroj premium styling")
    text_overlay: str = Field(default=None, description="Text to overlay on the image (supports Hindi if font exists)")

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "device": generator.device if generator else "warming up",
        "model": os.getenv("MODEL_ID"),
        "features": ["Hinglish-Support", "Text-Overlay"]
    }

@app.post("/generate")
async def generate_image(request: GenerateRequest):
    if not generator:
        raise HTTPException(status_code=503, detail="Generator not ready")
        
    try:
        start_time = time.time()
        
        # Generate the image with optional overlay
        image, final_prompt = generator.generate(
            prompt=request.prompt,
            num_steps=request.steps,
            guidance_scale=request.guidance_scale,
            width=request.width,
            height=request.height,
            enhance=request.enhance,
            overlay_text=request.text_overlay
        )
        
        # Save to memory
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        
        # Convert to base64
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        duration = time.time() - start_time
        logger.info(f"Generated image in {duration:.2f}s for prompt: '{request.prompt[:30]}...'")
        
        return {
            "status": "success",
            "data": {
                "input_prompt": request.prompt,
                "processed_prompt": final_prompt,
                "text_overlay": request.text_overlay,
                "image_b64": img_str,
                "format": "png",
                "meta": {
                    "steps": request.steps,
                    "width": request.width,
                    "height": request.height,
                    "duration": f"{duration:.2f}s"
                }
            }
        }
    except Exception as e:
        logger.error(f"API Error: {e}")
        raise HTTPException(status_code=500, detail="An error occurred during image generation.")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
