# Script-to-Animation Backend

This backend uses Flask to expose endpoints for parsing user scripts and generating an animation plan.

## Setup

1. Create a virtual environment:

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

2. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

3. Create a `.env` file to store your keys locally. Use the example file as a template:

   ```powershell
   copy .env.example .env
   ```

4. Edit `.env` and add your keys:

   ```text
   OPENAI_API_KEY=your_openai_api_key_here
   GOOGLE_AI_STUDIO_API_KEY=your_google_ai_studio_api_key_here
   ```

5. Run the backend:

   ```powershell
   python app.py
   ```

Generated animation videos are saved locally in `backend/videos` and served from `/videos/<filename>`.

> Recommended Python version: 3.9.13

## Endpoints

- `GET /health`
- `POST /api/parse-script`
- `POST /api/generate-plan`
- `POST /api/create-animation`

`/api/create-animation` expects JSON with:

```json
{
  "script": "...",
  "options": [
    {
      "sceneNumber": 1,
      "animationStyle": "Cinematic",
      "transition": "fade",
      "imagePrompt": "..."
    }
  ]
}
```

`/api/parse-script` and `/api/generate-plan` expect JSON with a `script` field.
