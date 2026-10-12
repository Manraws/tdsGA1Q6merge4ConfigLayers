# Effective Configuration API

## Deploy on Render
1. Create a new Git repository and add these files.
2. Push the repository to GitHub.
3. In Render, choose **New → Web Service**, connect the repository, and deploy using the included `Dockerfile` (or use the included `render.yaml` blueprint).
4. Once deployed, copy the public service URL and append `/effective-config`.

## Test
- `GET /effective-config`
- `GET /effective-config?set=port=9000&set=debug=true`
- `GET /effective-config?set=workers=5&set=log_level=warning`

The endpoint rereads the YAML, `.env`, and process environment for each request. Only `APP_*` process variables are considered for the OS environment layer. The `api_key` value is always masked in the response.

## Run locally
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload
```
