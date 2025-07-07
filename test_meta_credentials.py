import os
import requests

def test_meta_credentials():
    # Load credentials from environment
    access_token = os.getenv("META_ACCESS_TOKEN")
    fb_page_id = os.getenv("FB_PAGE_ID")
    ig_business_id = os.getenv("IG_BUSINESS_ID")

    if not all([access_token, fb_page_id, ig_business_id]):
        print("Error: Missing required environment variables")
        print("Please set: META_ACCESS_TOKEN, FB_PAGE_ID, IG_BUSINESS_ID")
        return False

    # Test Facebook Page access
    print("Testing Facebook Page access...")
    fb_response = requests.get(
        f"https://graph.facebook.com/{fb_page_id}?fields=name&access_token={access_token}"
    )
    
    if fb_response.status_code == 200:
        print(f"✅ Facebook Page access verified - Name: {fb_response.json().get('name')}")
    else:
        print(f"❌ Facebook Page access failed: {fb_response.text}")
        return False

    # Test Instagram Business Account access
    print("Testing Instagram Business Account access...")
    ig_response = requests.get(
        f"https://graph.facebook.com/{ig_business_id}?fields=username&access_token={access_token}"
    )
    
    if ig_response.status_code == 200:
        print(f"✅ Instagram Business Account verified - Username: {ig_response.json().get('username')}")
        return True
    else:
        print(f"❌ Instagram Business Account access failed: {ig_response.text}")
        return False

if __name__ == "__main__":
    print("Testing Meta Business Suite Credentials...")
    result = test_meta_credentials()
    if result:
        print("\nAll credentials are valid!")
    else:
        print("\nSome credentials are invalid. Please check your .env file.")
