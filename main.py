from fastapi import FastAPI, Request, Header, HTTPException, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel
import requests
import os
import openai
import uuid
import json
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Server is running"}

@app.post("/generate")
def generate_content():
    return {"status": "success", "message": "Generated content here"}



# Environment Variables
openai.api_key = os.getenv("OPENAI_API_KEY")

# Security: API Key Verification
def verify_api_key(x_api_key: str = Header(...)):
    expected_key = os.getenv("API_KEY")
    if x_api_key != expected_key:
        raise HTTPException(status_code=403, detail="Forbidden")

# Request Schemas
class PostRequest(BaseModel):
    topic: str

class ImageRequest(BaseModel):
    prompt: str

class PromptRequest(BaseModel):
    topic: str
    style: str = "clean, bold, legal-themed, white background, centered text"

class PublishRequest(BaseModel):
    id: str

class ApproveRequest(BaseModel):
    id: str

# Generate Caption (GPT-4o)
@app.post("/generate-post")
async def generate_post(data: PostRequest, auth=Depends(verify_api_key)):
    prompt = f"Create an Instagram caption about this topic: {data.topic}. Make it punchy, smart, and with a clear CTA."
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    caption = response["choices"][0]["message"]["content"]
    return {"caption": caption}

# Generate Image (Ideogram)
@app.post("/generate-image")
async def generate_image(data: ImageRequest, auth=Depends(verify_api_key)):
    headers = {
        "Authorization": f"Bearer {os.getenv('IDEOGRAM_API_KEY')}",
        "Content-Type": "application/json"
    }
    body = {
        "prompt": data.prompt,
        "model": "ideogram-v3",
        "generation_speed": "default"
    }

    response = requests.post("https://api.ideogram.ai/generate", headers=headers, json=body)
    result = response.json()
    image_url = result.get("image_url")

    if not image_url:
        return {"error": "No image URL returned from Ideogram"}

    os.makedirs("images", exist_ok=True)
    image_id = str(uuid.uuid4())
    image_path = f"images/{image_id}.png"
    img_data = requests.get(image_url).content

    with open(image_path, "wb") as handler:
        handler.write(img_data)

    preview_meta = {
        "id": image_id,
        "prompt": data.prompt,
        "path": image_path,
        "url": f"/preview-image/{image_id}",
        "approved": False
    }

    with open("preview_log.json", "a") as f:
        f.write(json.dumps(preview_meta) + "\n")

    return {
        "message": "Image generated and cached",
        "image_path": image_path,
        "image_url": f"/preview-image/{image_id}"
    }

# Build Prompt
@app.post("/build-prompt")
def build_prompt(data: PromptRequest, auth=Depends(verify_api_key)):
    prompt = f"Create a graphic for: '{data.topic}'. Style should be {data.style}. Must be readable on Instagram and Facebook."
    return {"prompt": prompt}

# Save Preview (manual store)
@app.post("/preview")
async def save_preview(request: Request, auth=Depends(verify_api_key)):
    body = await request.json()
    with open("previews.json", "a") as f:
        f.write(json.dumps(body) + "\n")
    return {"message": "Preview saved"}

# Serve Cached Image
@app.get("/preview-image/{image_id}")
async def preview_image(image_id: str, auth=Depends(verify_api_key)):
    image_path = f"images/{image_id}.png"
    if os.path.exists(image_path):
        return FileResponse(image_path, media_type="image/png")
    return {"error": "Image not found"}

# List All Previews
@app.get("/preview-images")
def list_previews(auth=Depends(verify_api_key)):
    previews = []
    if os.path.exists("preview_log.json"):
        with open("preview_log.json", "r") as f:
            for line in f:
                previews.append(json.loads(line))
    return previews

# Approve Image
@app.post("/approve-image")
def approve_image(data: ApproveRequest, auth=Depends(verify_api_key)):
    updated_previews = []
    found = False

    with open("preview_log.json", "r") as f:
        for line in f:
            item = json.loads(line)
            if item["id"] == data.id:
                item["approved"] = True
                found = True
            updated_previews.append(item)

    if not found:
        return {"error": "Image ID not found"}

    with open("preview_log.json", "w") as f:
        for item in updated_previews:
            f.write(json.dumps(item) + "\n")

    return {"message": "Image approved", "id": data.id}

# Meta Publishing Logic
def publish_to_meta(image_path, caption):
    access_token = os.getenv("META_ACCESS_TOKEN")
    fb_page_id = os.getenv("FB_PAGE_ID")
    ig_business_id = os.getenv("IG_BUSINESS_ID")

    with open(image_path, "rb") as f:
        files = {"source": f}
        fb_response = requests.post(
            f"https://graph.facebook.com/{fb_page_id}/photos",
            data={"caption": caption, "access_token": access_token},
            files=files
        )

    fb_result = fb_response.json()

    image_url = fb_result.get("post_id")
    ig_image_upload = requests.post(
        f"https://graph.facebook.com/v19.0/{ig_business_id}/media",
        data={
            "image_url": fb_result.get("image_url", ""),
            "caption": caption,
            "access_token": access_token
        }
    )

    container = ig_image_upload.json()
    creation_id = container.get("id")

    if creation_id:
        ig_publish = requests.post(
            f"https://graph.facebook.com/v19.0/{ig_business_id}/media_publish",
            data={"creation_id": creation_id, "access_token": access_token}
        )
        return {"fb": fb_result, "ig": ig_publish.json()}
    else:
        return {"fb": fb_result, "ig_error": container}

# Final Publish Route
@app.post("/publish")
def publish_image(data: PublishRequest, auth=Depends(verify_api_key)):
    found = False
    with open("preview_log.json", "r") as f:
        previews = [json.loads(line) for line in f]

    for item in previews:
        if item["id"] == data.id and item["approved"]:
            found = True
            result = publish_to_meta(item["path"], item["prompt"])
            return {"status": "posted", "details": result}

    return {"error": "Image not approved or ID not found"}



##Open Frontend
from fastapi.responses import HTMLResponse

@app.get("/", response_class=HTMLResponse)
def root():
    with open("frontend.html") as f:
        return f.read()
