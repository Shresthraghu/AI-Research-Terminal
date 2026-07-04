# Imports
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()           # this step is a must before importing files from services/ folder
from services.search import get_official_url
from services.crawler import crawl_website
from services.ai import analyze_company_data

# Literals
app = FastAPI(title="Relu AI Research Assistant Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ResearchRequest(BaseModel):
    input_value: str                                # Can be "Tesla" or "https://tesla.com"

# Routes
@app.post("/api/research")
async def start_research(request: ResearchRequest):
    input_data = request.input_value.strip()
    
    # 1. Resolve Name/URL to Official URL via Serper
    if input_data.startswith(("http://", "https://")):
        target_url = input_data
    else:
        target_url = get_official_url(input_data)
        if not target_url:
            raise HTTPException(status_code=404, detail="Could not identify an official website for this company.")
            
    # 2. Extract plain text content via Crawler
    crawled_content = crawl_website(target_url)
            
    # 3. Route content context to OpenRouter
    ai_report = analyze_company_data(crawled_content)            
    
    return {
        "status": "success",
        "resolved_url": target_url,
        "report": ai_report
    }
