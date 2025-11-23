---
title: SHL Assessment Recommender
emoji: 🎯
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
---

# SHL Assessment Recommendation System

An intelligent recommendation system that helps hiring managers find relevant SHL assessments based on natural language queries or job descriptions.

## Features

- **Hybrid RAG Engine**: Combines Neural Embeddings (Sentence Transformers) with TF-IDF
- **Cross-Encoder Re-ranking**: High-precision results
- **Smart Balancing**: Intelligently balances Technical and Soft Skills assessments
- **Mean Recall@10**: 24.1% on training set

## Local Setup

1. **Clone the repository**
   ```bash
   git clone https://huggingface.co/spaces/shravyagautam24/SHL_Assignment
   cd SHL_Assignment
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```
   The API will be available at `http://0.0.0.0:7860`.

## API Endpoints

### 1. Health Check
- **URL**: `/health`
- **Method**: `GET`
- **Description**: Verifies the API is running.

**Response**:
```json
{
  "status": "healthy"
}
```

### 2. Get Recommendations
- **URL**: `/recommend`
- **Method**: `POST`
- **Description**: Returns relevant assessments based on a query.

**Request**:
```json
{
  "query": "Java developer with communication skills"
}
```

**Response**:
```json
{
  "recommended_assessments": [
    {
      "url": "https://www.shl.com/...",
      "name": "Java Platform Enterprise Edition 7",
      "adaptive_support": "No",
      "description": "The Java Platform Enterprise Edition 7...",
      "duration": 30,
      "remote_support": "Yes",
      "test_type": ["K"]
    }
  ]
}
```

### 3. Frontend
- **URL**: `/`
- **Method**: `GET`
- **Description**: Serves the web interface.

## Performance

- **Mean Recall@10**: 24.1%
- **Assessments Indexed**: 389
- **Architecture**: Hybrid Search (Neural + Keyword) + Cross-Encoder Re-ranking
