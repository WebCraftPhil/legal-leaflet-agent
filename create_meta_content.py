import requests
import json
import os

# Configuration
API_URL = "http://159.203.99.128"
API_KEY = "your_api_key_here"  # Replace with your API key

# 1. Generate a caption for the post
async def generate_caption(topic):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        f"{API_URL}/generate-post",
        headers=headers,
        json={"topic": topic}
    )
    
    if response.status_code == 200:
        return response.json()["caption"]
    else:
        raise Exception(f"Failed to generate caption: {response.text}")

# 2. Generate an image using Ideogram
async def generate_image(prompt):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        f"{API_URL}/generate-image",
        headers=headers,
        json={"prompt": prompt}
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to generate image: {response.text}")

# 3. Approve an image
async def approve_image(image_id):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        f"{API_URL}/approve-image",
        headers=headers,
        json={"id": image_id}
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to approve image: {response.text}")

# Example workflow
async def create_meta_content(topic):
    try:
        # Step 1: Generate caption
        print(f"Generating caption for topic: {topic}")
        caption = await generate_caption(topic)
        print(f"Generated caption: {caption}")
        
        # Step 2: Generate image using the caption as prompt
        print("Generating image...")
        image_data = await generate_image(caption)
        print(f"Image generated with ID: {image_data['id']}")
        
        # Step 3: Approve the image
        print("Approving image...")
        approve_result = await approve_image(image_data['id'])
        print("Image approved successfully!")
        
        return {
            "caption": caption,
            "image_url": image_data['image_url'],
            "image_id": image_data['id']
        }
        
    except Exception as e:
        print(f"Error creating content: {str(e)}")
        return None

if __name__ == "__main__":
    # Example usage
    topic = "Legal Services for Small Businesses"
    result = create_meta_content(topic)
    if result:
        print("\nContent created successfully!")
        print(f"Caption: {result['caption']}")
        print(f"Image URL: {result['image_url']}")
        print(f"Image ID: {result['image_id']}")
    else:
        print("Failed to create content")
