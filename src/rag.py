"""
Enhanced RAG engine with Neural Embeddings (Sentence Transformers).
Expected improvement: Significant boost in semantic understanding and recall.
"""
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import os
import sys
# Mock tensorflow to prevent transformers from trying to import the broken installation
sys.modules['tensorflow'] = None
from sentence_transformers import SentenceTransformer, CrossEncoder

# Calculate absolute path to data file
import pathlib
DATA_FILE = str(pathlib.Path(__file__).parent.parent / "data" / "assessments.json")

class RecommendationEngine:
    def __init__(self):
        self.assessments = []
        self.model = None
        self.cross_encoder = None
        self.embeddings = None
        self.vectorizer = None
        self.tfidf_matrix = None
        self.load_data()

    def load_data(self):
        print(f"DEBUG: Looking for data file at: {DATA_FILE}")
        print(f"DEBUG: File exists: {os.path.exists(DATA_FILE)}")
        if not os.path.exists(DATA_FILE):
            raise FileNotFoundError(f"{DATA_FILE} not found. Run scraper first.")
        
        with open(DATA_FILE, "r") as f:
            self.assessments = json.load(f)
        
        # Prepare text for embedding
        self.texts = []
        for item in self.assessments:
            # Combine fields for a rich semantic representation
            # We don't need to repeat names like in TF-IDF, the model handles importance better
            name = item['name']
            desc = item.get('description', '')
            cats = ", ".join(item.get('categories', []))
            test_types = ", ".join(item.get('test_type', []))
            
            # Structured text for the model
            text = f"Assessment: {name}. Description: {desc}. Categories: {cats}. Types: {test_types}"
            self.texts.append(text)
        
        # Initialize Sentence Transformer (Bi-Encoder)
        # Upgraded to all-mpnet-base-v2 for better semantic understanding
        print("Loading Bi-Encoder model (all-mpnet-base-v2)...")
        self.model = SentenceTransformer('all-mpnet-base-v2')
        
        print("Generating embeddings...")
        self.embeddings = self.model.encode(self.texts, show_progress_bar=True)
        print("Embeddings ready.")

        # Initialize Cross-Encoder for Re-ranking
        print("Loading Cross-Encoder model (ms-marco-MiniLM-L-6-v2)...")
        self.cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

        # Initialize TF-IDF for Hybrid Search
        from sklearn.feature_extraction.text import TfidfVectorizer
        print("Generating TF-IDF matrix for Hybrid Search...")
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            max_features=5000
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(self.texts)
        print("TF-IDF matrix ready.")

    def recommend(self, query, k=10):
        # 1. Neural Score
        query_embedding = self.model.encode([query])
        neural_scores = cosine_similarity(query_embedding, self.embeddings).flatten()
        
        # 2. Keyword Score (TF-IDF)
        query_vec = self.vectorizer.transform([query])
        keyword_scores = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        
        # 3. Hybrid Score (Initial Retrieval)
        # Weighting: 80% Semantic, 20% Keyword
        hybrid_scores = (0.8 * neural_scores) + (0.2 * keyword_scores)
        
        # Get top 50 candidates for re-ranking
        top_n = min(50, len(self.assessments))
        top_indices = hybrid_scores.argsort()[-top_n:][::-1]
        
        # 4. Cross-Encoder Re-ranking
        candidates = []
        for idx in top_indices:
            candidates.append([query, self.texts[idx]])
            
        cross_scores = self.cross_encoder.predict(candidates)
        
        # Normalize cross-encoder scores to 0-100% range for display
        # Cross-encoder returns raw logits which can be negative or very large
        min_score = float(np.min(cross_scores))
        max_score = float(np.max(cross_scores))
        score_range = max_score - min_score
        
        reranked_results = []
        for i, idx in enumerate(top_indices):
            item = self.assessments[idx]
            # Normalize to 0-100 range
            raw_score = float(cross_scores[i])
            if score_range > 0:
                normalized_score = ((raw_score - min_score) / score_range) * 100
            else:
                normalized_score = 50.0  # Default if all scores are the same
            
            reranked_results.append({
                "Assessment name": item['name'],
                "URL": item['url'],
                "Score": normalized_score,  # Normalized 0-100 score for display
                "Raw Score": raw_score,  # Keep raw score for debugging
                "Hybrid Score": float(hybrid_scores[idx]),
                "Description": item.get('description', '')[:200] + "...",
                "Test Type": item.get('test_type', [])
            })
            
        # Sort by Cross-Encoder score
        reranked_results.sort(key=lambda x: x['Score'], reverse=True)
        
        results = reranked_results
        
        # Apply intelligent balancing
        results = self._balance_recommendations(query, results, k)
        
        return results
    
    def _balance_recommendations(self, query, results, k):
        """Balance recommendations when query spans multiple domains"""
        query_lower = query.lower()
        
        # Detect query intent
        technical_keywords = ['developer', 'programmer', 'engineer', 'python', 'java', 'sql', 
                             'coding', 'technical', 'software', 'data', 'analyst', 'architect']
        soft_keywords = ['communication', 'collaboration', 'leadership', 'teamwork', 'management',
                        'interpersonal', 'stakeholder', 'personality', 'behavioral', 'soft skills']
        
        has_technical = any(keyword in query_lower for keyword in technical_keywords)
        has_soft = any(keyword in query_lower for keyword in soft_keywords)
        
        # Filter by Test Type if query is specific
        if has_technical and not has_soft:
            # Prefer K, C, A types for technical queries
            tech_results = [r for r in results if any(t in ['K', 'C', 'A'] for t in r.get('Test Type', []))]
            if len(tech_results) >= k:
                return tech_results[:k]
        
        elif has_soft and not has_technical:
            # Prefer P, B types for soft skill queries
            soft_results = [r for r in results if any(t in ['P', 'B'] for t in r.get('Test Type', []))]
            if len(soft_results) >= k:
                return soft_results[:k]
        
        # If query spans both domains, ensure balanced mix
        elif has_technical and has_soft:
            knowledge_tests = [r for r in results if 'K' in r.get('Test Type', [])]
            personality_tests = [r for r in results if 'P' in r.get('Test Type', [])]
            
            target_k = min(len(knowledge_tests), k // 2)
            target_p = min(len(personality_tests), k // 2)
            
            balanced = []
            balanced.extend(knowledge_tests[:target_k])
            balanced.extend(personality_tests[:target_p])
            
            remaining_slots = k - len(balanced)
            if remaining_slots > 0:
                used_urls = {r['URL'] for r in balanced}
                remaining = [r for r in results if r['URL'] not in used_urls]
                balanced.extend(remaining[:remaining_slots])
            
            return balanced[:k]
        
        return results[:k]

if __name__ == "__main__":
    engine = RecommendationEngine()
    # Test query
    print(json.dumps(engine.recommend("Java developer with good communication skills"), indent=2))
