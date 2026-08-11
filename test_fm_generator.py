import os
import json
import urllib.parse
import urllib.request

def main():
    print("===================================================")
    print("       FM AI Newgen Face Generation Tester")
    print("===================================================\n")

    # 1. Load config
    config_path = "config.json"
    if not os.path.exists(config_path):
        print(f"[Error] config.json not found! Make sure you are running from the root project folder.")
        return

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    api_key = config.get("api_key", "").strip()
    face_style_template = config.get("face_style", "")

    print(f"[Config] API Key loaded: {api_key[:6]}...{api_key[-6:] if len(api_key) > 12 else ''}" if api_key else "[Config] No API Key found. Defaulting to keyless Sana model.")

    # 2. Setup mock player attributes
    mock_uid = "2002178350"
    mock_age = "17"
    mock_nationality = "Japanese"
    mock_personality_details = "fair skin, short dark brown hair, dark brown eyes, clean-shaven, tidy appearance, focused smiling expression"

    # Build prompt dynamically from config.json template
    prompt = face_style_template
    prompt = prompt.replace("[AGE]", mock_age)
    prompt = prompt.replace("[NATIONALITY]", mock_nationality)
    prompt = prompt.replace("[PERSONALITY]", mock_personality_details)

    print(f"[Player] Seed UID: {mock_uid}")
    print(f"[Prompt] Dynamic Prompt from config.json:\n  {prompt}\n")

    # 3. Build request URL
    encoded_prompt = urllib.parse.quote(prompt)
    if api_key:
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?seed={mock_uid}&model=flux&nologo=true&private=true&key={api_key}"
        print("[API] Model selected: FLUX (photorealistic)")
    else:
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?seed={mock_uid}&nologo=true&private=true"
        print("[API] Model selected: SANA (keyless default)")

    # 4. Fetch and Save
    output_filename = "test_flux_face.png" if api_key else "test_sana_face.png"
    print(f"[Download] Connecting to Pollinations.ai...")
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
            "Referer": "https://pollinations.ai/"
        }
        
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            if response.status == 200:
                image_data = response.read()
                with open(output_filename, "wb") as img_file:
                    img_file.write(image_data)
                print(f"\n[Success] Face generated successfully! Saved as '{output_filename}' in the project directory.")
                print(f"[Info] File size: {len(image_data)} bytes.")
            else:
                print(f"\n[Error] API returned status code: {response.status}")
    except Exception as e:
        print(f"\n[Error] Download failed: {e}")

if __name__ == "__main__":
    main()
