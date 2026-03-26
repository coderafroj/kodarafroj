import requests
import base64
import os
import json

def test_health():
    url = "http://localhost:8000/health"
    try:
        response = requests.get(url)
        response.raise_for_status()
        print("Health Check:", response.json())
        return True
    except Exception as e:
        print(f"Health Check Failed: {e}")
        return False

def generate_image(prompt, output_file="kodarafroj_hinglish.png", enhance=True, text=""):
    url = "http://localhost:8000/generate"
    payload = {
        "prompt": prompt,
        "steps": 4,
        "width": 512,
        "height": 512,
        "enhance": enhance,
        "text_overlay": text
    }
    
    print(f"\n--- Kodarafroj Generation ---")
    print(f"Input Prompt: '{prompt}'")
    print(f"Text Overlay: '{text if text else 'None'}'")
    print("Generating... Please wait...")
    
    try:
        response = requests.post(url, json=payload, timeout=300)
        response.raise_for_status()
        
        data = response.json()
        if data["status"] == "success":
            image_b64 = data["data"]["image_b64"]
            processed_prompt = data["data"]["processed_prompt"]
            meta = data["data"]["meta"]
            
            # Decode base64 to image file
            with open(output_file, "wb") as f:
                f.write(base64.b64decode(image_b64))
                
            print(f"✅ Success! Image saved as: {output_file}")
            print(f"🚀 Model-ready Prompt: {processed_prompt}")
            print(f"⏱ Duration: {meta['duration']}")
        else:
            print(f"❌ Failed: {data.get('detail', 'Unknown error')}")
            
    except Exception as e:
        print(f"🚨 Error: {e}")

if __name__ == "__main__":
    if test_health():
        print("\nOptions:")
        print("1. Try Hinglish Prompt (e.g. 'Ek sher pahaad par')")
        print("2. Try Text Overlay (e.g. 'नमस्ते' / 'HINDI TEXT')")
        
        choice = input("\nChoose (1/2) or just enter prompt: ")
        
        if choice == "1":
            p = "Ek sher jungle mein baitha hai"
            generate_image(p, "hinglish_test.png")
        elif choice == "2":
            p = "A beautiful sunset over mountain"
            t = "सुंदर सूर्यास्त" # Hindi for Beautiful Sunset
            generate_image(p, "text_overlay_test.png", text=t)
        else:
            p = choice if len(choice) > 1 else input("Enter prompt: ")
            t = input("Enter overlay text (optional): ")
            generate_image(p, "custom_test.png", text=t)
    else:
        print("Server is not running. Start it with 'python main.py' first.")
