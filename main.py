from fastapi import FastAPI, Request
from pydantic import BaseModel
import requests
import os
import openai
from dotenv import load_dotenv
from fastapi import Header, HTTPException, Depends


#API Function

def verify_api_key(x_api_key: str = Header(...)):
    expected_key = os.getenv("API_KEY")
    if x_api_key != expected_key:
        raise HTTPException(status_code=403, detail="Forbidden")



load_dotenv()

app = FastAPI()

openai.api_key = os.getenv("OPENAI_API_KEY")

class PostRequest(BaseModel):
    topic: str

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

class ImageRequest(BaseModel):
    prompt: str

@app.post("/generate-image")
async def generate_image(data: ImageRequest, auth=Depends(verify_api_key)):
    headers = {
        "Authorization": f"Bearer {os.getenv('IDEOGRAM_API_KEY')}",
        "Content-Type": "application/json"
    }
    body = {
        "prompt": data.prompt,
        "model": "ideogram-v3"  # adjust based on actual model name
    }

    response = requests.post("https://api.ideogram.ai/generate", headers=headers, json=body)
    return response.json()

class PromptRequest(BaseModel):
    topic: str
    style: str = "clean, bold, legal-themed, white background, centered text"


# Prompt Bulder
@app.post("/build-prompt")
def build_prompt(data: PromptRequest, auth=Depends(verify_api_key)):
    prompt = (
        f"Create a graphic for: '{data.topic}'. "
        f"Style should be {data.style}. Must be readable on Instagram and Facebook."
    )

# Preview

    return {"prompt": prompt}
import json

@app.post("/preview")
async def save_preview(request: Request, auth=Depends(verify_api_key)):
    body = await request.json()
    
    with open("previews.json", "a") as f:
        f.write(json.dumps(body) + "\n")
    
    return {"message": "Preview saved"}

#Publish Route Meta

class PublishRequest(BaseModel):
    caption: str
    image_url: str

@app.post("/publish")
async def publish_post(data: PublishRequest, auth=Depends(verify_api_key)):

    # Replace with Meta Graph API code
	# Meta Posting Helper

    return {
        "message": "Mock publish complete",
        "platforms": ["Instagram", "Facebook"],
        "caption": data.caption,
        "image_url": data.image_url
    }

def publish_to_meta(image_path, caption):
    access_token = os.getenv("META_ACCESS_TOKEN")
    fb_page_id = os.getenv("FB_PAGE_ID")
    ig_business_id = os.getenv("IG_BUSINESS_ID")

    # Upload image to Facebook Page
    with open(image_path, "rb") as f:
        files = {"source": f}
        fb_response = requests.post(
            f"https://graph.facebook.com/{fb_page_id}/photos",
            data={"caption": caption, "access_token": access_token},
            files=files
        )
    
    fb_result = fb_response.json()

    # Step 1: Upload to Instagram Container
    image_url = fb_result.get("post_id")  # You could also reupload the image
    ig_image_upload = requests.post(
        f"https://graph.facebook.com/v19.0/{ig_business_id}/media",
        data={
            "image_url": fb_result.get("image_url", ""),  # fallback if needed
            "caption": caption,
            "access_token": access_token
        }
    )
    container = ig_image_upload.json()
    creation_id = container.get("id")

    # Step 2: Publish Instagram post
    if creation_id:
        ig_publish = requests.post(
            f"https://graph.facebook.com/v19.0/{ig_business_id}/media_publish",
            data={"creation_id": creation_id, "access_token": access_token}
        )
        return {
            "fb": fb_result,
            "ig": ig_publish.json()
        }
    else:
        return {"fb": fb_result, "ig_error": container}

#  Publish Endpoint


class PublishRequest(BaseModel):
    id: str  # This should be the image ID from your cache

@app.post("/publish")
def publish_image(data: PublishRequest):
    # Load preview metadata
    found = False
    with open("preview_log.json", "r") as f:
        previews = [json.loads(line) for line in f]

    for item in previews:
        if item["id"] == data.id and item["approved"]:
            found = True
            result = publish_to_meta(item["path"], item["prompt"])
            return {"status": "posted", "details": result}

    return {"error": "Image not approved or ID not found"}

