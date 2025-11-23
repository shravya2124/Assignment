# Hugging Face Spaces Deployment Guide

## Step 1: Create Hugging Face Account
1. Go to https://huggingface.co/join
2. Sign up for a free account
3. Verify your email

## Step 2: Create a New Space
1. Go to https://huggingface.co/new-space
2. Fill in the details:
   - **Space name**: `shl-assessment-recommender` (or your choice)
   - **License**: MIT
   - **SDK**: Docker
   - **Hardware**: CPU basic (free)
3. Click **"Create Space"**

## Step 3: Push Your Code

### Option A: Using Git (Recommended)

```bash
# Navigate to your project
cd /Users/shravyagautam/Desktop/SHL-assignment.

# Add Hugging Face as a remote (replace USERNAME with your HF username)
git remote add hf https://huggingface.co/spaces/USERNAME/shl-assessment-recommender

# Push to Hugging Face
git push hf main
```

### Option B: Using Hugging Face Web Interface

1. Go to your Space page
2. Click **"Files"** tab
3. Click **"Add file"** → **"Upload files"**
4. Upload all files from your project directory
5. Click **"Commit changes to main"**

## Step 4: Wait for Build

- Hugging Face will automatically build your Docker container
- This takes 5-10 minutes
- You can monitor progress in the **"Logs"** tab

## Step 5: Test Your API

Once deployed, your API will be available at:
```
https://USERNAME-shl-assessment-recommender.hf.space
```

Test it:
```bash
# Health check
curl https://USERNAME-shl-assessment-recommender.hf.space/health

# Get recommendations
curl -X POST https://USERNAME-shl-assessment-recommender.hf.space/recommend \
  -H "Content-Type: application/json" \
  -d '{"query": "Java developer with communication skills"}'
```

## Step 6: Update Frontend

Update `frontend/index.html` line 150 to use your Hugging Face Space URL:

```javascript
const response = await fetch('https://USERNAME-shl-assessment-recommender.hf.space/recommend', {
```

## Troubleshooting

### Build Fails
- Check the **"Logs"** tab for errors
- Ensure all files are uploaded correctly
- Verify `requirements.txt` is correct

### Out of Memory
- Upgrade to a paid hardware tier (GPU or larger CPU)
- Or simplify the model (remove neural embeddings)

### Slow First Request
- Hugging Face Spaces may have cold starts
- First request can take 30-60 seconds
- Subsequent requests are fast

## Cost

- **Free tier**: CPU basic (sufficient for this project)
- **Paid tiers**: Start at $0.60/hour for GPU
- **No credit card required** for free tier
