---
title: Kodarafroj AI Image Generator
emoji: 🖼️
colorFrom: indigo
colorTo: blue
sdk: docker
pinned: false
---

# AI Image Generator for SaaS

This is an advanced AI Image Generator optimized for **CPU and 8GB RAM**, but ready for high-performance **GPU environments**.

## Setup Instructions

1. **Install Dependencies**:
   Open your terminal in this folder and run:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the API**:
   ```bash
   python main.py
   ```
   *Note: On the first run, it will download about 3-4GB of model weights. This only happens once.*

3. **How to Use**:
   - The API will be running at `http://localhost:8000`
   - You can test it using the `/generate` endpoint.
   - Example JSON Request:
     ```json
     {
       "prompt": "An astronaut riding a horse on mars, cinematic lighting",
       "steps": 4,
       "width": 512,
       "height": 512
     }
     ```

## Key Optimizations for 8GB RAM / CPU
- **LCM-LoRA**: Reduces generation steps from 50 to 4, making CPU generation possible in reasonable time.
- **Attention Slicing**: Reduces memory peaks to fit in 8GB RAM.
- **Auto-Detection**: If you move this code to a server with a GPU, it will automatically use `cuda` for ultra-fast generation.

## SaaS Integration
To use this in your website:
- Send a POST request from your frontend or backend to this API.
- The API returns the image as a `base64` string, which you can show directly in an `<img>` tag or save to your database/S3.
