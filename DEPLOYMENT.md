# Deployment Configuration

## 1. Render (Backend)
- **Root Directory**: `krishiquery-ai`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`
- **Environment Variables**:
  - `PORT`: `5000` (or Render default)
  - `OPENAI_API_KEY`: `<your_openai_api_key>` (Optional: if omitted, system automatically uses built-in rule-based agricultural fallback rewriter)

## 2. Vercel (Frontend)
- **Root Directory**: `frontend`
- **Build Command**: None (Static Site)
- **Output Directory**: None (Static Site)

## 3. Connect Frontend to Render Backend
In `frontend/script.js`, replace the placeholder on line 7:
```javascript
const API_URL = "RENDER_BACKEND_URL";
```
with your deployed Render URL, for example:
```javascript
const API_URL = "https://your-service.onrender.com";
```
Commit and push to trigger an automatic Vercel redeployment.
