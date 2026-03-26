import os
import sys
# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from generator import HinglishProcessor, PromptMaster, TextOverlay, AspectEngine
from PIL import Image
import re

def test_hinglish():
    prompts = [
        "Ek sher jungle mein baitha hai",
        "Raja mahal mein rani ke saath hai",
        "Ek sundar ladki phool tod rahi hai",
        "Poster banao ek yoddha ka",
    ]
    
    print("--- Hinglish Translation Test ---")
    for p in prompts:
        translated = HinglishProcessor.translate(p)
        print(f"Original: {p}")
        print(f"Translated: {translated}")
        print("-" * 20)

def test_advanced():
    prompts = [
        "Ek shaktishali yoddha cyberpunk city mein hai, dark mood",
        "Anime style ladki phoolon ke saath, happy mood",
        "Lambbi image of a castle in the mountains, magical",
        "Wide image of a ship in samundar, retro style",
        "3D toy model of a cat, bright colors",
    ]
    
    print("\n--- Advanced AI Logic Test ---")
    for p in prompts:
        final_p, final_n = PromptMaster.enhance(p)
        w, h = AspectEngine.detect(p, 512, 512)
        print(f"Original: {p}")
        print(f"Dimensions: {w}x{h}")
        print(f"Final Prompt: {final_p}")
        print(f"Negative: {final_n[:50]}...")
        print("-" * 20)

def test_text_overlay():
    print("\n--- Text Overlay Test ---")
    # Create a dummy image
    img = Image.new("RGB", (512, 512), color=(73, 109, 137))
    
    try:
        # Test Hindi text (if font exists)
        img_with_text = TextOverlay.apply(img, "नमस्ते दुनिया", position="bottom")
        img_with_text.save("test_overlay_hindi.png")
        print("Saved test_overlay_hindi.png")
        
        # Test English text
        img_with_text_en = TextOverlay.apply(img, "Hello World", position="top")
        img_with_text_en.save("test_overlay_english.png")
        print("Saved test_overlay_english.png")
    except Exception as e:
        print(f"Overlay test failed: {e}")

if __name__ == "__main__":
    test_hinglish()
    test_advanced()
    test_text_overlay()
