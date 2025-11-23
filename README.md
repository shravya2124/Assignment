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

## API Endpoints

### Health Check
```bash
GET /health
```

### Get Recommendations
```bash
POST /recommend
Content-Type: application/json

{
  "query": "Java developer with communication skills"
}
```

## Performance

- **Mean Recall@10**: 24.1%
- **Assessments Indexed**: 389
- **Architecture**: Hybrid Search (Neural + Keyword) + Cross-Encoder Re-ranking
