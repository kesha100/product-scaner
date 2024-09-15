# main.py

import base64
import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class AnalysisResponse(BaseModel):
    description: str

@app.post("/analyze/", response_model=AnalysisResponse)
async def analyze_product(file: UploadFile = File(...)):
    # Check if the file is an image
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Read and encode the file
    contents = await file.read()
    encoded_image = base64.b64encode(contents).decode("utf-8")
    
    try:
        # Call OpenAI API
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "You are the best skincare product ingredients analyzer. Analyze this skincare product image and describe its ingredients and tell  for what type of skins it suits. What are the results and reviews."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{encoded_image}"
                            }
                        }
                    ],
                }
            ],
            max_tokens=300,
        )
        
        description = response.choices[0].message.content
        return {"description": description}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)