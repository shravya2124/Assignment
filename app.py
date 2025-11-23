"""
Hugging Face Spaces entry point for SHL Assessment Recommendation System
"""
from src.api import app

# Hugging Face Spaces will automatically run this file
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
