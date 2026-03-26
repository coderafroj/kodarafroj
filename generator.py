import torch
from diffusers import StableDiffusionPipeline, LCMScheduler
import os
import logging
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("KodarafrojGenerator")

load_dotenv()

class HinglishProcessor:
    """Best-effort Hinglish to English translator for prompts."""
    
    MAPPING = {
        # Core replacements
        "ek": "a", "mein": "in", "par": "on", "saath": "with", "ke": "of", "ka": "of",
        "hai": "is", "tha": "was", "hoga": "will be", "aur": "and", "ko": "to",
        "liye": "for", "se": "from", "ki": "of", "wala": "type of", "wali": "type of",
        "sher": "lion", "hathi": "elephant", "cheeta": "tiger", "ghoda": "horse",
        "billi": "cat", "kutta": "dog", "panchi": "bird", "machli": "fish",
        "jungle": "forest", "pahaad": "mountain", "nadi": "river", "samundar": "ocean",
        "aasman": "sky", "suraj": "sun", "chand": "moon", "taare": "stars",
        "shahar": "city", "gaon": "village", "mahal": "palace", "ghar": "house",
        "sadak": "road", "gadi": "car", "lal": "red", "neela": "blue",
        "hara": "green", "peela": "yellow", "safed": "white", "kala": "black",
        "sundar": "beautiful", "shaktishali": "powerful", "bada": "big", "chota": "small",
        "purana": "old", "naya": "new", "tez": "fast", "dheere": "slow",
        "andhera": "dark", "ujala": "bright", "khush": "happy", "rona": "sad",
        "bhag raha hai": "running", "baitha hai": "sitting", "so raha hai": "sleeping",
        "ud raha hai": "flying", "ter raha hai": "swimming",
        
        # Expanded vocabulary & Synonyms
        "raja": "king", "rani": "queen", "sipahi": "soldier", "yoddha": "warrior",
        "ladka": "boy", "ladki": "girl", "baccha": "child", "insan": "human",
        "shaktishali": "powerful", "takatwar": "strong", "ajeeb": "weird",
        "darauna": "scary", "khubsurat": "beautiful", "khoobsurat": "beautiful",
        "chamkila": "bright", "dhundhla": "misty", "jaadu": "magic",
        "asli": "realistic", "sapno": "dreamy", "bachpan": "childhood",
        "pyaar": "love", "jang": "war", "paisa": "money/wealth",
        "chaudi": "wide", "lambbi": "tall/portrait", "badi": "large", "ghata": "cloudy/moody",
        
        # Actions & State
        "baitha": "sitting", "khada": "standing", "let": "lying", "daud": "running",
        "khel": "playing", "nach": "dancing", "ga": "singing", "padh": "reading",
        "likh": "writing", "so": "sleeping", "ud": "flying", "ter": "swimming",
        "raha": "performing", "rahi": "performing", "kar": "doing", "pahan": "wearing",
        
        # Action & Context
        "poster": "poster", "banner": "banner", "thumbnail": "thumbnail",
        "likho": "write", "dikhao": "show", "banao": "create", "karo": "do", "kijiye": "do",
        "mere": "my", "tumhare": "your", "dikhao": "show", "le": "take", "lo": "take"
    }

    @classmethod
    def translate(cls, prompt: str) -> str:
        translated = prompt.lower()
        for hi, en in cls.MAPPING.items():
            translated = re.sub(rf'\b{hi}\b', en, translated)
        return translated

class StyleEngine:
    """Advanced detection and application of visual styles/moods."""
    
    STYLES = {
        "cyberpunk": {"p": "cyberpunk style, neon lights, futuristic city, heavy atmosphere", "n": "vintage, medieval"},
        "anime": {"p": "anime style, vibrant cel shading, studio ghibli inspired", "n": "photorealistic, 3d"},
        "sketch": {"p": "pencil sketch, hand-drawn, graphite texture, charcoal", "n": "colors, photography"},
        "3d": {"p": "3d render, octane render, unreal engine 5, soft lighting", "n": "2d, flat"},
        "retro": {"p": "vhs aesthetic, 80s style, grainy film, retro wave", "n": "modern, high def"},
        "royal": {"p": "royal majestic style, elegant gold ornaments, luxury feel", "n": "cheap, messy"}
    }

    MOODS = {
        "dark": "low key lighting, moody atmosphere, deep shadows, dark aesthetics",
        "happy": "bright sunny day, cheerful colors, high key lighting",
        "scary": "horror aesthetic, eerie lighting, misty fog, terrifying",
        "magical": "fantasy glow, magical particles, ethereal lighting, dreamlike"
    }

    @classmethod
    def analyze(cls, prompt: str):
        p_low = prompt.lower()
        pos_mods = []
        neg_mods = []
        
        for style, mods in cls.STYLES.items():
            if style in p_low:
                pos_mods.append(mods["p"])
                neg_mods.append(mods["n"])
        
        for mood, mod in cls.MOODS.items():
            if mood in p_low:
                pos_mods.append(mod)
                
        return ", ".join(pos_mods), ", ".join(neg_mods)

class AspectEngine:
    """Intelligently detects requested aspect ratios from prompt."""
    @classmethod
    def detect(cls, prompt: str, w, h):
        p_low = prompt.lower()
        # Wide / Landscape
        if any(x in p_low for x in ["wide", "chaudi", "landscape"]):
            if w == h: return 768, 512
            return (max(w, h), min(w, h)) if w < h else (w, h)
        # Tall / Portrait
        if any(x in p_low for x in ["tall", "lambbi", "portrait", "mobile"]):
            if w == h: return 512, 768
            return (min(w, h), max(w, h)) if w > h else (w, h)
        return w, h

class TextOverlay:
    """Tool to add Hindi/English text on generated images with premium styling."""
    
    @classmethod
    def apply(cls, image: Image.Image, text: str, position="bottom") -> Image.Image:
        if not text:
            return image
        
        # Create a copy to avoid mutating the original
        img = image.copy().convert("RGBA")
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        width, height = img.size
        
        # Font paths for Windows and Linux (Hugging Face)
        font_paths = [
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", # Linux (HF default)
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",        # Linux fallback
            "C:\\Windows\\Fonts\\Nirmala.ttf",                             # Windows Hindi
            "C:\\Windows\\Fonts\\arialbd.ttf",                            # Windows Arial Bold
            "C:\\Windows\\Fonts\\arial.ttf",                              # Windows Arial
        ]
        
        font = None
        font_size = int(height * 0.07) 
        
        for path in font_paths:
            if os.path.exists(path):
                try:
                    font = ImageFont.truetype(path, font_size)
                    logger.info(f"Loaded font from: {path}")
                    break
                except Exception as e:
                    logger.warning(f"Failed to load font {path}: {e}")
                    continue
        
        if font is None:
            font = ImageFont.load_default()

        # Calculate text position
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        
        x = (width - text_w) / 2
        if position == "bottom":
            y = height - text_h - 60
        elif position == "top":
            y = 60
        else:
            y = (height - text_h) / 2
            
        # Draw soft shadow
        shadow_offset = 3
        for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1), (0, shadow_offset)]:
            draw.text((x+dx, y+dy), text, font=font, fill=(0, 0, 0, 150))
        
        # Final text
        final_draw = ImageDraw.Draw(img)
        final_draw.text((x, y), text, font=font, fill=(255, 255, 255))
        
        return img.convert("RGB")

class PromptMaster:
    """Enhances user prompts with AI-level understanding and premium styling."""
    
    BASE_MODIFIERS = [
        "cinematic lighting", "8k resolution", "photorealistic masterpiece",
        "highly detailed textures", "professional composition", "vibrant color grading"
    ]
    
    POSTER_MODIFIERS = [
        "movie poster style", "professional graphic design", "bold composition",
        "cinematic lighting", "dramatic high contrast", "premium advertisement feel"
    ]
    
    # Updated to be a method for dynamic usage
    @classmethod
    def get_negative(cls, extra_neg=""):
        base = (
            "blurry, low quality, distorted anatomy, extra limbs, poorly drawn face, "
            "poorly drawn hands, missing fingers, cropped, lowres, text, error, "
            "watermark, signature, jpeg artifacts, ugly, duplicate, morbid, mutilated, "
            "out of frame, extra fingers, mutated hands, poorly drawn eyes, cluttered"
        )
        return f"{base}, {extra_neg}" if extra_neg else base

    @classmethod
    def enhance(cls, prompt: str, add_style: bool = True):
        # 1. Analyze for styles and moods
        style_p, style_n = StyleEngine.analyze(prompt)
        
        # 2. Check for poster intent
        is_poster = any(word in prompt.lower() for word in ["poster", "banner", "thumbnail", "advertisement"])
        
        # 3. Translate Hinglish
        translated = HinglishProcessor.translate(prompt)
        
        if not add_style:
            return translated, cls.get_negative(style_n)
        
        # 4. Clean fillers
        fillers = ["mujhe", "banao", "dikhao", "generate", "ai", "high level", "best", "image"]
        cleaned = translated
        for f in fillers:
            cleaned = re.sub(rf'\b{f}\b', '', cleaned, flags=re.IGNORECASE)
        cleaned = cleaned.strip().strip(',')
        
        # 5. Build final prompt
        mods = cls.POSTER_MODIFIERS if is_poster else cls.BASE_MODIFIERS
        final_prompt = f"{cleaned}, {style_p}, {', '.join(mods)}"
        
        return final_prompt.replace(", ,", ",").strip(", "), cls.get_negative(style_n)

class ImageGenerator:
    def __init__(self):
        model_id = os.getenv("MODEL_ID", "runwayml/stable-diffusion-v1-5")
        lcm_lora_id = os.getenv("LCM_LORA_ID", "latent-consistency/lcm-lora-sdv1-5")
        device_env = os.getenv("DEVICE", "auto")
        
        logger.info(f"Initializing Kodarafroj Generator with model: {model_id}")
        
        if device_env == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device_env
            
        logger.info(f"Using device: {self.device}")

        try:
            self.pipe = StableDiffusionPipeline.from_pretrained(
                model_id, 
                torch_dtype=torch.float32 if self.device == "cpu" else torch.float16,
                safety_checker=None
            )
            self.pipe.to(self.device)

            if self.device == "cpu":
                self.pipe.enable_attention_slicing()
            
            self.pipe.load_lora_weights(lcm_lora_id)
            self.pipe.scheduler = LCMScheduler.from_config(self.pipe.scheduler.config)
            
        except Exception as e:
            logger.error(f"Failed to initialize model: {e}")
            raise RuntimeError(f"Model initialization failed: {e}")

    def generate(self, prompt, num_steps=4, guidance_scale=1.0, width=512, height=512, enhance=True, overlay_text=None):
        try:
            # 1. Detect Aspect Ratio from prompt
            width, height = AspectEngine.detect(prompt, width, height)
            
            # 2. Enhance prompt (including Hinglish translation and style/mood)
            final_prompt, negative_prompt = PromptMaster.enhance(prompt, add_style=enhance)
            
            logger.info(f"Generating {width}x{height} image. Original: '{prompt}' | Enhanced: '{final_prompt}'")
            
            image = self.pipe(
                prompt=final_prompt,
                negative_prompt=negative_prompt,
                num_inference_steps=num_steps, 
                guidance_scale=guidance_scale,
                width=width,
                height=height
            ).images[0]
            
            # 3. Apply text overlay if requested
            if overlay_text:
                logger.info(f"Applying text overlay: '{overlay_text}'")
                image = TextOverlay.apply(image, overlay_text)
            
            return image, final_prompt
        except Exception as e:
            logger.error(f"Generation error: {e}")
            raise e
