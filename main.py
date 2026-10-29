import os
import re
import json
import math
import wave
import struct
import random
import asyncio
import subprocess
import urllib.parse
import textwrap
import requests
import edge_tts
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

# =====================================================================
# ENVIRONMENT SECRETS & CONFIGURATION
# =====================================================================
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
PIXABAY_API_KEY = os.environ.get("PIXABAY_API_KEY", "").strip()
GIPHY_API_KEY = (
    os.environ.get("GIPHY_API_KEY", "").strip()
    or os.environ.get("GIPHY_KEY", "").strip()
    or os.environ.get("GIPHY_SECRET", "").strip()
)
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
FB_ACCESS_TOKEN = os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN", "").strip()
FB_PAGE_ID = os.environ.get("FACEBOOK_PAGE_ID", "").strip()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "application/json, text/html, application/xhtml+xml, image/webp, */*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9"
}

USED_TOPICS_FILE = "used_topics.json"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
USED_MEDIA_URLS = set()

# =====================================================================
# INFINITE SEED MATRIX (FIRST-PERSON YESU MASIH LIFE PSYCHOLOGY ENGINE)
# =====================================================================
SPIRITUAL_DOMAINS = [
    {
        "domain": "Anxiety, Kal ki Fikar aur Pahari Waaz (Matthew 6)",
        "nasa_tie": "Asman ke sitaron aur kainat ka nizam",
        "nasa_query": "galaxy stars nebula universe",
        "modern_struggle": "Mustaqbil ka khauf, berozgari ki tension aur raaton ki be-chaini",
        "scripture_ref": "Matta 6:25-34 (Pahari Waaz)",
        "core_truth": "Asman ke parindon aur jungli soosanon ko dekho",
        "pixabay_vid": "birds flying sunrise",
        "giphy_query": "peaceful sunrise light"
    },
    {
        "domain": "Depression, Bojh aur Roohani Aaram (Matthew 11:28)",
        "nasa_tie": "Zameen ka madar aur roshni ka tawazun",
        "nasa_query": "earth sunrise from space",
        "modern_struggle": "Zehni thakawat, mayoosi aur zindagi ke bhari bojh",
        "scripture_ref": "Matta 11:28-30 (Aye Bojh Uthane Walo)",
        "core_truth": "Aye mehnat karne walo aur bojh se dabe hue logo mere paas aao",
        "pixabay_vid": "man walking alone sunset",
        "giphy_query": "glowing light hope"
    },
    {
        "domain": "Zindagi ke Toofan aur Kashti mein Sukoon (Mark 4)",
        "nasa_tie": "Zameen ke samandar aur badalon ka tufani nizam",
        "nasa_query": "hurricane storm earth from space",
        "modern_struggle": "Gharailu pareshaniyan, achanak musibat aur dil ka ڈوبنا",
        "scripture_ref": "Marqus 4:39 (Thum Ja, Sakin Ho Ja)",
        "core_truth": "Jab main teri kashti mein sawaar hoon to toofan tujhe dabo nahi sakta",
        "pixabay_vid": "ocean storm waves",
        "giphy_query": "stormy sea waves"
    },
    {
        "domain": "Dhoka, Bewafai aur Muaafi ki Psychology (Luke 23)",
        "nasa_tie": "Sooraj girhan aur tareeki ke baad naya noor",
        "nasa_query": "solar eclipse sun corona",
        "modern_struggle": "Apno ka dhoka, dil tootna aur nafrat ka zehar",
        "scripture_ref": "Luqa 23:34 (Ae Baap Inhein Muaaf Kar)",
        "core_truth": "Muaaf karna dushman par ehsaan nahi balkay teri apni rooh ki azaadi hai",
        "pixabay_vid": "broken chains freedom",
        "giphy_query": "dove flying peace"
    },
    {
        "domain": "Tanhai ki Raat aur Gethsemane ka Sabق (Matthew 26)",
        "nasa_tie": "Raat ke aasman mein chamakte sitaray aur gehra khala",
        "nasa_query": "night sky milky way stars",
        "modern_struggle": "Akelepan ka dard, jab apne dost bhi saath chhor jayein",
        "scripture_ref": "Matta 26:36-42 (Bagh-e-Gethsemane)",
        "core_truth": "Tanhai teri kamzori nahi balkay Baap se judne ki sab se badi jagah hai",
        "pixabay_vid": "olive trees night moon",
        "giphy_query": "night sky stars pray"
    },
    {
        "domain": "Riya-kaari, Dikhawa aur Asli Sachai (Matthew 23)",
        "nasa_tie": "Sooraj ki khalis roshni jo har cheez zahir karti hai",
        "nasa_query": "sun flare light space",
        "modern_struggle": "Social media ka dikhawa, jhooti shohrat aur andar ka khalipan",
        "scripture_ref": "Matta 6:6 (Band Kothri ki Dua)",
        "core_truth": "Log zahir ko dekhte hain magar main tere dil ki gehrai ko dekhta hoon",
        "pixabay_vid": "candle flame dark room",
        "giphy_query": "candle light peace"
    },
    {
        "domain": "Maali Tangdasti, Barkat aur Paanch Rotiyan (John 6)",
        "nasa_tie": "Zameen par barish, fasal aur zindagi ka chakar",
        "nasa_query": "earth green continents clouds",
        "modern_struggle": "Mehangai ka khauf, karz ka bojh aur rizq ki pareshani",
        "scripture_ref": "Yuhanna 6:35 (Zindagi ki Roti Main Hoon)",
        "core_truth": "Jab tu apna thora sa mere haath mein deta hai to main usay hazaroon ke liye barha deta hoon",
        "pixabay_vid": "wheat field golden sunlight",
        "giphy_query": "golden wheat harvest"
    },
    {
        "domain": "Sharmindagi, Gunah ka Bojh aur Naya Aaghaz (John 8)",
        "nasa_tie": "Naye sitaron ki paidaish aur roshni ka phailao",
        "nasa_query": "hubble nebula star birth",
        "modern_struggle": "Maazi ki galtiyan, logon ke taanay aur khud se nafrat",
        "scripture_ref": "Yuhanna 8:11 (Main Bhi Tujhe Mujrim Nahi Thehrata)",
        "core_truth": "Duniya tere hath mein pathar uthati hai magar mera fazal tujhe nayi zindagi deta hai",
        "pixabay_vid": "sunrise over desert mountains",
        "giphy_query": "sunrise light clouds"
    },
    {
        "domain": "Khauf se Azaadi aur Haqeeqi Salamti (John 14:27)",
        "nasa_tie": "Gehre khala ki khamoshi aur kamil tawazun",
        "nasa_query": "deep space quiet galaxy",
        "modern_struggle": "Bimari ka darr, buri khabron ka khauf aur dil ki ghabrahat",
        "scripture_ref": "Yuhanna 14:27 (Main Tumhein Apni Salamti Deta Hoon)",
        "core_truth": "Meri salamti duniya ke halat par nahi balkay meri maujoodgi par qaim hai",
        "pixabay_vid": "calm lake reflection mountains",
        "giphy_query": "calm water reflection"
    },
    {
        "domain": "Alpha aur Omega: Khudawand ka Din aur Aakhri Umeed (Revelation 22)",
        "nasa_tie": "Kainat ki wusat aur asmani jalal",
        "nasa_query": "james webb telescope cosmic cliffs",
        "modern_struggle": "Na-insafi, zulm aur yeh sawal ke sachai kab jeetegi",
        "scripture_ref": "Mukashfa 22:12-13 (Dekho Main Jald Aane Wala Hoon)",
        "core_truth": "Main Awwal aur Aakhir hoon, tere har aansu ka hisaab mere paas mehfooz hai",
        "pixabay_vid": "golden clouds heaven light",
        "giphy_query": "heavenly clouds sunbeams"
    }
]

ANGLES = [
    "Main Khudawand Yesu Masih Aaj Tum Se Hamkalam Hota Hoon",
    "Dekho Khudawand Ka Din Aata Hai: Aaj Ke Insaan Ke Naam Paigham",
    "Modern Duniya Ki Be-Chaini Aur Meri Zindagi Ki Psychology",
    "Tumhara Dil Kyun Ghabrata Hai? Khudawand Yesu Masih Ki Aawaz",
    "Jab Duniya Tumhein Thukra De: Khudawand Yesu Masih Ka Zinda Kalam",
    "Tanhai, Dard Aur Shifa: Khudawand Yesu Masih Ka Roohani Raaz"
]


def load_used_topics():
    if os.path.exists(USED_TOPICS_FILE):
        try:
            with open(USED_TOPICS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_used_topic(topic_id):
    used = load_used_topics()
    if topic_id not in used:
        used.append(topic_id)
    used = used[-500:]
    with open(USED_TOPICS_FILE, "w", encoding="utf-8") as f:
        json.dump(used, f, indent=2, ensure_ascii=False)


# =====================================================================
# INFINITE 2-MINUTE FIRST-PERSON SCRIPT GENERATOR (12 SCENES = ~120s)
# =====================================================================
def generate_infinite_documentary_script():
    used = load_used_topics()

    candidates = []
    for dom in SPIRITUAL_DOMAINS:
        for ang in ANGLES:
            seed_id = f"{dom['domain']} | {ang}"
            if seed_id not in used:
                candidates.append((seed_id, dom, ang))

    if not candidates:
        dom = random.choice(SPIRITUAL_DOMAINS)
        ang = random.choice(ANGLES)
        seed_id = f"{dom['domain']} | {ang} | Ep-{len(used)+1}"
    else:
        seed_id, dom, ang = random.choice(candidates)

    save_used_topic(seed_id)
    print(f"🕊️ Selected Unique 2-Minute Spiritual Seed: {seed_id}")

    if GEMINI_API_KEY:
        try:
            script = fetch_gemini_2min_script(dom, ang, used[-15:])
            if script and len(script.get("scenes", [])) >= 10:
                print(f"✨ Gemini Generated {len(script['scenes'])} First-Person Scenes (~2 Mins)!")
                return script
        except Exception as e:
            print(f"⚠️ Gemini generation fallback triggered: {e}")

    print("🎬 Building 12-Scene (2-Minute) First-Person Script via Built-in Spiritual Engine...")
    return build_procedural_2min_documentary(dom, ang)


def fetch_gemini_2min_script(dom, ang, recent_topics):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

    prompt = f"""
You are writing a deeply moving, philosophical, cinematic 2-MINUTE Urdu spiritual & psychological documentary script tailored for Pakistani Christians.

CRITICAL NARRATION RULE (FIRST-PERSON POV):
The entire voiceover MUST be in the FIRST PERSON spoken directly by Khudawand Yesu Masih (Lord Jesus Christ) addressing today's struggling human being.
Start Scene 1 with phrases like: "میں خداوند یسوع مسیح آج تم سے ہم کلام ہوتا ہوں۔ دیکھو خداوند کا دن آتا ہے..."
Use authentic Pakistani Christian Urdu terminology (خداوند یسوع مسیح، کلامِ مقدس، فضل، روح القدس، صلیب، شفا، سلامتی، آسمانی باپ).

THEME DOMAIN: {dom['domain']}
MODERN PSYCHOLOGICAL STRUGGLE: {dom['modern_struggle']}
SCRIPTURE REFERENCE: {dom['scripture_ref']}
CORE TEACHING: {dom['core_truth']}
COSMIC / CREATION VISUAL TIE: {dom['nasa_tie']}
NARRATIVE ANGLE: {ang}
RECENTLY COVERED TOPICS TO AVOID REPEATING: {json.dumps(recent_topics)}

REQUIREMENTS FOR 2-MINUTE LENGTH & QUALITY:
1. Write exactly 12 scenes structured across 4 Acts:
   - Scenes 1-2: ACT I - KHUDAWAND KI AAWAZ (Majestic First-Person Call to Modern Man)
   - Scenes 3-5: ACT II - ZAMEENI ZINDAGI AUR NAFSIYAT (How Jesus faced this exact pain on Earth & psychological wisdom)
   - Scenes 6-8: ACT III - KAINAT KA KHALIQ AUR ROOHANI QANOON (Connecting cosmic creation to the listener's heart)
   - Scenes 9-12: ACT IV - SHIFA, SALAMTI AUR AAKHRI PAIGHAM (Healing, practical life transformation & blessing)
2. Each scene's "tts_urdu" MUST be written in pure, majestic Urdu script (اردو) in FIRST-PERSON POV ("میں...", "میری آواز سنو...") and MUST be 24 to 30 words long (~10 seconds per scene = ~120 seconds total).
3. For each scene provide:
   - "act": Short English/Roman-Urdu act badge (e.g. "ACT I: KHUDAWAND KI AAWAZ", "ACT II: ROOHANI PSYCHOLOGY")
   - "tts_urdu": 24-30 words of deep, philosophical, first-person Urdu narration.
   - "caption_part1": Impactful Roman-Urdu headline for first half (max 24 chars).
   - "caption_part2": Impactful Roman-Urdu headline for second half (max 24 chars).
   - "media_source_pref": Choose "nasa" (for creation/heavens/stars), "pixabay" (for nature/life/prayer), or "giphy" (for light/peace loops).
   - "search_query_1": 2-4 English keywords for visual cut 1.
   - "search_query_2": 2-4 English keywords for visual cut 2.
   - "video_query": 1-3 English keywords for stock video or NASA cosmic video.
   - "sfx_type": Choose one of ["boom", "whoosh", "riser", "pulse"].

Return ONLY valid JSON matching this structure:
{{
  "title": "🕊️ [Deep Roman Urdu Title] | Khudawand Yesu Masih Ka Paigham",
  "tagline": "[Touching 1-line hook in Roman Urdu with emojis]",
  "description": "[3-sentence summary explaining how Khudawand Yesu Masih's life psychology heals modern struggles]",
  "hashtags": "#KhudawandYesuMasih #PakistaniChristians #UrduBible #MasihiGeet #YesuMasih #RoohaniSukoon #KalamEMuqaddas #ChristianReels",
  "category_badge": "[SHORT CAPS BADGE]",
  "scenes": [ ... 12 scene objects ... ]
}}
"""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.85,
            "responseMimeType": "application/json"
        }
    }

    resp = requests.post(url, headers={"Content-Type": "application/json"}, json=payload, timeout=75)
    if resp.status_code != 200:
        url_fallback = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        resp = requests.post(url_fallback, headers={"Content-Type": "application/json"}, json=payload, timeout=75)

    if resp.status_code == 200:
        raw_text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
        raw_text = re.sub(r"^```json\s*|\s*```$", "", raw_text.strip())
        return json.loads(raw_text)
    raise RuntimeError(f"Gemini API HTTP {resp.status_code}: {resp.text[:160]}")


def build_procedural_2min_documentary(dom, ang):
    """12-Scene (~2 Minute / 120s) First-Person Khudawand Yesu Masih Documentary Fallback."""
    d_name = dom["domain"]
    nasa_q = dom["nasa_query"]
    struggle = dom["modern_struggle"]
    ref = dom["scripture_ref"]
    p_vid = dom["pixabay_vid"]
    g_q = dom["giphy_query"]

    scenes = [
        # ACT I: KHUDAWAND KI AAWAZ (Scenes 1-2)
        {
            "act": "ACT I: KHUDAWAND KI AAWAZ",
            "tts_urdu": "میں خداوند یسوع مسیح آج تم سے ہم کلام ہوتا ہوں۔ دیکھو خداوند کا دن آتا ہے، ذرا اپنے دل کے شور کو روک کر میری آواز غور سے سنو!",
            "caption_part1": "MAIN YESU MASIH",
            "caption_part2": "TUM SE HAMKALAM HOON!",
            "media_source_pref": "pixabay",
            "search_query_1": "sunbeams through clouds",
            "search_query_2": "man praying silhouette sunset",
            "video_query": p_vid,
            "sfx_type": "boom"
        },
        {
            "act": "ACT I: KHUDAWAND KI AAWAZ",
            "tts_urdu": "میں جانتا ہوں کہ آج کی اس تیز رفتار دنیا میں تمہارا ذہن تھک چکا ہے، اور تم اپنے سینے میں ایسی بے چینی چھپائے پھرتے ہو جسے کوئی انسان نہیں سمجھتا۔",
            "caption_part1": "DUNIYA KI BE-CHAINI",
            "caption_part2": "MAIN TERA DARD JANTA HOON!",
            "media_source_pref": "pixabay",
            "search_query_1": "sad lonely person night",
            "search_query_2": "city traffic rain window",
            "video_query": "rain window night",
            "sfx_type": "whoosh"
        },
        # ACT II: ZAMEENI ZINDAGI AUR NAFSIYAT (Scenes 3-5)
        {
            "act": "ACT II: ZINDAGI KI PSYCHOLOGY",
            "tts_urdu": "یاد رکھو، جب میں اس زمین پر انسانی جسم میں چلا پھرا، تو میں نے بھی بھوک، تنہائی، اپنوں کی بے وفائی اور گتسمنی کی رات کا شدید ذہنی دباؤ خود محسوس کیا تھا۔",
            "caption_part1": "GETHSEMANE KI TANHAI",
            "caption_part2": "MAIN NE BHI DARD SAHA!",
            "media_source_pref": "pixabay",
            "search_query_1": "ancient olive trees night",
            "search_query_2": "wooden cross sunset hill",
            "video_query": "olive trees",
            "sfx_type": "riser"
        },
        {
            "act": "ACT II: ZINDAGI KI PSYCHOLOGY",
            "tts_urdu": "آج کی نفسیات تمہیں بتاتی ہے کہ خوف اور فکرمندی انسان کو اندر سے کھوکھلا کر دیتی ہے، اور یہی بات میں نے دو ہزار سال پہلے پہاڑی وعظ میں تمہیں سمجھائی تھی۔",
            "caption_part1": "PAHARI WAAZ KA RAAZ",
            "caption_part2": "KAL KI FIKAR NA KARO!",
            "media_source_pref": "giphy",
            "search_query_1": g_q,
            "search_query_2": "birds flying sky",
            "video_query": "mountains sunrise",
            "sfx_type": "pulse"
        },
        {
            "act": "ACT II: ZINDAGI KI PSYCHOLOGY",
            "tts_urdu": "میں نے تم سے کہا تھا کہ آسمان کے پرندوں کو دیکھو، وہ نہ بوتے ہیں اور نہ کاٹتے ہیں، پھر بھی تمہارا آسمانی باپ انہیں روزانہ رزق دیتا ہے، تو تم کیوں گھبراتے ہو؟",
            "caption_part1": "ASMAN KE PARINDON KO DEKHO",
            "caption_part2": "KHUDA TUMHARA KAFIL HAI!",
            "media_source_pref": "pixabay",
            "search_query_1": "eagle flying high clouds",
            "search_query_2": "wildflowers meadow sunlight",
            "video_query": "birds flying",
            "sfx_type": "whoosh"
        },
        # ACT III: KAINAT KA KHALIQ AUR ROOHANI QANOON (Scenes 6-8)
        {
            "act": "ACT III: KAINAT KA MALIK",
            "tts_urdu": "ذرا اپنی آنکھیں اٹھا کر اس لامحدود کائنات اور آسمان کے کروڑوں ستاروں کو دیکھو! جس کلام سے یہ سارے کہکشاں اپنے مدار میں قائم ہیں، وہی کلام آج تمہارے ساتھ ہے۔",
            "caption_part1": "KAINAT KE SITARAY DEKHO",
            "caption_part2": "MERA KALAM QUDRAT WALA HAI!",
            "media_source_pref": "nasa",
            "search_query_1": nasa_q,
            "search_query_2": "spiral galaxy deep space",
            "video_query": nasa_q,
            "sfx_type": "boom"
        },
        {
            "act": "ACT III: KAINAT KA MALIK",
            "tts_urdu": "جب تمہاری زندگی کی کشتی کے گرد مسائل کا طوفان اٹھتا ہے، تو تم लहरوں کو دیکھ کر ڈر جاتے ہو، حالانکہ میں تمہاری کشتی کے اندر موجود ہوں اور طوفان میرے حکم کا پابند ہے۔",
            "caption_part1": "ZINDAGI KA TOOFAN",
            "caption_part2": "MERI AAWAZ SE THAM JATA HAI!",
            "media_source_pref": "pixabay",
            "search_query_1": "stormy ocean waves boat",
            "search_query_2": "light breaking dark clouds",
            "video_query": "ocean waves storm",
            "sfx_type": "riser"
        },
        {
            "act": "ACT III: KAINAT KA MALIK",
            "tts_urdu": "تمہاری روحانی بے چینی کی سب سے بڑی وجہ یہ ہے کہ تم نے لوگوں کی تلخ باتوں، حسد اور ناانصافی کا بوجھ اپنے دل پر اٹھا رکھا ہے، جس نے تمہاری نیند چھین لی ہے۔",
            "caption_part1": "DIL KA BHAARI BOJH",
            "caption_part2": "NAFRAT SE AZAAD HO JAO!",
            "media_source_pref": "nasa",
            "search_query_1": "earth horizon from space",
            "search_query_2": "broken chains light",
            "video_query": "earth from space",
            "sfx_type": "pulse"
        },
        # ACT IV: SHIFA, SALAMTI AUR AAKHRI PAIGHAM (Scenes 9-12)
        {
            "act": "ACT IV: SHIFA AUR SALAMTI",
            "tts_urdu": "صلیب پر جب میرے ہاتھوں میں کیل ٹھونکے گئے، تب بھی میں نے کہا تھا کہ اے باپ انہیں معاف کر! کیونکہ معاف کرنا کمزوری نہیں بلکہ تمہارے اپنے ذہن اور روح کی سب سے بڑی شفا ہے۔",
            "caption_part1": "SALEEB PAR MUAAFI KA RAAZ",
            "caption_part2": "ROOH KI ASLI SHIFA!",
            "media_source_pref": "pixabay",
            "search_query_1": "cross silhouette dramatic sky",
            "search_query_2": "open hands praying light",
            "video_query": "sunset clouds cross",
            "sfx_type": "boom"
        },
        {
            "act": "ACT IV: SHIFA AUR SALAMTI",
            "tts_urdu": "اے محنت کرنے والو اور بوجھ سے دبے ہوئے لوگو، میرے پاس آؤ، میں تمہیں آرام دوں گا! اپنی ساری فکریں میرے قدموں میں رکھ دو کیونکہ مجھے تمہاری فکر ہے۔",
            "caption_part1": "AYE BOJH UTHANE WALO",
            "caption_part2": "MAIN TUMHEIN AARAM DOONGA!",
            "media_source_pref": "giphy",
            "search_query_1": "peaceful river forest",
            "search_query_2": "open bible glowing light",
            "video_query": "calm river nature",
            "sfx_type": "whoosh"
        },
        {
            "act": "ACT IV: SHIFA AUR SALAMTI",
            "tts_urdu": "میں تمہیں وہ سلامتی دیتا ہوں جو دنیا نہیں دے سکتی۔ نہ تمہارا دل گھبرائے اور نہ خوف کھائے، کیونکہ میں الفا اور اومیگا ہوں اور تمہارا مستقبل میرے محفوظ ہاتھوں میں ہے۔",
            "caption_part1": "MAIN ALPHA AUR OMEGA HOON",
            "caption_part2": "TUMHARA DIL NA GHABRAYE!",
            "media_source_pref": "nasa",
            "search_query_1": "james webb nebula stars",
            "search_query_2": "golden sunrise mountain peak",
            "video_query": "galaxy stars",
            "sfx_type": "pulse"
        },
        {
            "act": "ACT IV: SHIFA AUR SALAMTI",
            "tts_urdu": "دیکھو میں جلد آنے والا ہوں اور ہر ایک کو اس کے کام کے مطابق اجر دوں گا! آج ہی اپنے دل کو میرے نور سے بھر لو اور اس زندگی بخش کلام کو دوسروں تک پہنچاؤ۔ آمین!",
            "caption_part1": "DEKHO MAIN JALD AATA HOON",
            "caption_part2": "KALAM KO SHARE KAREIN! AMEN",
            "media_source_pref": "pixabay",
            "search_query_1": "heavenly light clouds sky",
            "search_query_2": "white dove flying sunbeams",
            "video_query": "golden clouds",
            "sfx_type": "riser"
        }
    ]

    return {
        "title": f"🕊️ {d_name} | Khudawand Yesu Masih Ka Zinda Paigham",
        "tagline": f"Main Khudawand Yesu Masih tum se hamkalam hota hoon — {struggle} ka roohani ilaj! ✝️✨",
        "description": f"Kalam-e-Muqaddas ({ref}) ki roshni mein janiye ke Khudawand Yesu Masih ki zindagi aur talimat aaj ke daur mein {struggle} se kaise azaadi aur shifa deti hain.",
        "hashtags": "#KhudawandYesuMasih #PakistaniChristians #UrduBible #YesuMasih #KalamEMuqaddas #MasihiZindagi #RoohaniShifa #ChristianReels",
        "category_badge": "YESU MASIH KA PAIGHAM",
        "scenes": scenes
    }


# =====================================================================
# MULTI-SOURCE MEDIA FETCHERS (NASA API + GIPHY API + PIXABAY + BING)
# =====================================================================
def fetch_nasa_media(query, filename, prefer_video=True):
    """Fetches royalty-free HD Cosmic/Creation Videos or Photos from https://images-api.nasa.gov."""
    if not query:
        return None, False

    encoded = urllib.parse.quote(query.strip())
    media_types = "video,image" if prefer_video else "image"
    api_url = f"https://images-api.nasa.gov/search?q={encoded}&media_type={media_types}&page_size=15"

    try:
        r = requests.get(api_url, headers=HEADERS, timeout=20)
        if r.status_code == 200:
            items = r.json().get("collection", {}).get("items", [])
            random.shuffle(items)
            for item in items:
                data_list = item.get("data", [])
                if not data_list:
                    continue
                m_type = data_list[0].get("media_type", "")
                nasa_id = data_list[0].get("nasa_id", "")
                href = item.get("href", "")

                if prefer_video and m_type == "video" and href:
                    try:
                        asset_r = requests.get(href, headers=HEADERS, timeout=15)
                        if asset_r.status_code == 200:
                            asset_urls = asset_r.json()
                            mp4_links = [
                                u for u in asset_urls
                                if isinstance(u, str) and u.endswith(".mp4") and ("~mobile" in u or "~medium" in u or "~preview" in u)
                            ]
                            if not mp4_links:
                                mp4_links = [u for u in asset_urls if isinstance(u, str) and u.endswith(".mp4")]
                            for vid_url in mp4_links:
                                if vid_url not in USED_MEDIA_URLS:
                                    USED_MEDIA_URLS.add(vid_url)
                                    vid_url_clean = vid_url.replace(" ", "%20")
                                    vr = requests.get(vid_url_clean, headers=HEADERS, timeout=30)
                                    if vr.status_code == 200 and len(vr.content) > 50000:
                                        vid_out = filename if filename.endswith(".mp4") else f"{filename}.mp4"
                                        with open(vid_out, "wb") as f:
                                            f.write(vr.content)
                                        print(f"  [🌌 NASA CREATION VIDEO] Downloaded '{nasa_id}' for '{query}'")
                                        return vid_out, True
                    except Exception:
                        pass

                links = item.get("links", [])
                for lnk in links:
                    if lnk.get("render") == "image":
                        img_url = lnk.get("href", "")
                        if img_url and img_url not in USED_MEDIA_URLS:
                            USED_MEDIA_URLS.add(img_url)
                            ir = requests.get(img_url.replace(" ", "%20"), headers=HEADERS, timeout=15)
                            if ir.status_code == 200 and len(ir.content) > 15000:
                                img_out = filename if filename.endswith(".jpg") else f"{filename}.jpg"
                                with open(img_out, "wb") as f:
                                    f.write(ir.content)
                                if verify_and_grade_image(img_out):
                                    print(f"  [✨ NASA CREATION PHOTO] Downloaded '{nasa_id}' for '{query}'")
                                    return img_out, False
    except Exception as e:
        print(f"  [!] NASA API skip ({query}): {e}")

    return None, False


def fetch_giphy_mp4(query, filename):
    """Fetches dynamic MP4 visual loops using GIPHY_API_KEY."""
    if not GIPHY_API_KEY or not query:
        return None

    try:
        encoded = urllib.parse.quote(query.strip())
        g_url = f"https://api.giphy.com/v1/gifs/search?api_key={GIPHY_API_KEY}&q={encoded}&limit=15&rating=g"
        r = requests.get(g_url, headers=HEADERS, timeout=18)
        if r.status_code == 200:
            data = r.json().get("data", [])
            random.shuffle(data)
            for item in data:
                images = item.get("images", {})
                mp4_url = (
                    images.get("original", {}).get("mp4")
                    or images.get("downsized_small", {}).get("mp4")
                    or images.get("fixed_height", {}).get("mp4")
                )
                if mp4_url and mp4_url not in USED_MEDIA_URLS:
                    USED_MEDIA_URLS.add(mp4_url)
                    vr = requests.get(mp4_url, headers=HEADERS, timeout=25)
                    if vr.status_code == 200 and len(vr.content) > 20000:
                        with open(filename, "wb") as f:
                            f.write(vr.content)
                        print(f"  [🕊️ GIPHY MP4] Downloaded loop for '{query}'")
                        return filename
    except Exception as e:
        print(f"  [!] GIPHY API skip ({query}): {e}")
    return None


def fetch_contextual_stock_video(query, filename, pref="pixabay"):
    """Routes video requests across NASA, GIPHY, Pixabay, and Mixkit."""
    if not query:
        return None

    if pref == "nasa" or any(k in query.lower() for k in ["nasa", "galaxy", "space", "stars", "nebula", "universe", "earth", "eclipse", "cosmos"]):
        nasa_file, is_vid = fetch_nasa_media(query, filename, prefer_video=True)
        if nasa_file and is_vid:
            return nasa_file

    if pref == "giphy" and GIPHY_API_KEY:
        g_file = fetch_giphy_mp4(query, filename)
        if g_file:
            return g_file

    if PIXABAY_API_KEY:
        try:
            encoded = urllib.parse.quote(query.strip())
            p_url = f"https://pixabay.com/api/videos/?key={PIXABAY_API_KEY}&q={encoded}&safesearch=true&per_page=15"
            r = requests.get(p_url, headers=HEADERS, timeout=20)
            if r.status_code == 200:
                hits = r.json().get("hits", [])
                random.shuffle(hits)
                for hit in hits:
                    videos = hit.get("videos", {})
                    vid_url = (
                        videos.get("medium", {}).get("url")
                        or videos.get("small", {}).get("url")
                        or videos.get("large", {}).get("url")
                    )
                    if vid_url and vid_url not in USED_MEDIA_URLS:
                        USED_MEDIA_URLS.add(vid_url)
                        vr = requests.get(vid_url, headers=HEADERS, timeout=30)
                        if vr.status_code == 200 and len(vr.content) > 50000:
                            with open(filename, "wb") as f:
                                f.write(vr.content)
                            print(f"  [🎬 PIXABAY VIDEO] Downloaded for '{query}'")
                            return filename
        except Exception as e:
            print(f"  [!] Pixabay video skip ({query}): {e}")

    if GIPHY_API_KEY:
        g_file = fetch_giphy_mp4(query, filename)
        if g_file:
            return g_file

    slug = urllib.parse.quote(query.lower().strip().split()[0])
    search_url = f"https://mixkit.co/free-stock-video/{slug}/"
    try:
        resp = requests.get(search_url, headers=HEADERS, timeout=15)
        if resp.status_code == 200:
            mp4_urls = re.findall(r'https://assets\.mixkit\.co/videos/[^\s"\'<>]+\.mp4', resp.text)
            fresh_urls = [u for u in mp4_urls if u not in USED_MEDIA_URLS]
            if fresh_urls:
                chosen_url = random.choice(fresh_urls[:5])
                USED_MEDIA_URLS.add(chosen_url)
                vid_resp = requests.get(chosen_url, headers=HEADERS, timeout=25)
                if vid_resp.status_code == 200 and len(vid_resp.content) > 50000:
                    with open(filename, "wb") as f:
                        f.write(vid_resp.content)
                    print(f"  [✓ Mixkit Video] Downloaded for '{query}'")
                    return filename
    except Exception:
        pass
    return None


def fetch_exact_scene_photo(query, filename, pref="pixabay"):
    """Fetches HD Photos from NASA, Pixabay, or Bing HD."""
    if pref == "nasa" or any(k in query.lower() for k in ["nasa", "galaxy", "space", "stars", "nebula", "universe", "earth", "eclipse", "telescope"]):
        nasa_img, is_vid = fetch_nasa_media(query, filename, prefer_video=False)
        if nasa_img and not is_vid:
            return nasa_img

    if PIXABAY_API_KEY:
        try:
            encoded = urllib.parse.quote(query.strip())
            p_url = f"https://pixabay.com/api/?key={PIXABAY_API_KEY}&q={encoded}&image_type=photo&safesearch=true&per_page=15"
            r = requests.get(p_url, headers=HEADERS, timeout=18)
            if r.status_code == 200:
                hits = r.json().get("hits", [])
                random.shuffle(hits)
                for hit in hits:
                    img_url = hit.get("largeImageURL") or hit.get("webformatURL")
                    if img_url and img_url not in USED_MEDIA_URLS:
                        USED_MEDIA_URLS.add(img_url)
                        img_r = requests.get(img_url, headers=HEADERS, timeout=15)
                        if img_r.status_code == 200 and len(img_r.content) > 15000:
                            with open(filename, "wb") as f:
                                f.write(img_r.content)
                            if verify_and_grade_image(filename):
                                print(f"  [📸 PIXABAY PHOTO] Downloaded for '{query}'")
                                return filename
        except Exception as e:
            print(f"  [!] Pixabay photo skip ({query}): {e}")

    nasa_img, is_vid = fetch_nasa_media(query, filename, prefer_video=False)
    if nasa_img and not is_vid:
        return nasa_img

    try:
        encoded = urllib.parse.quote(f"{query} cinematic dramatic photography")
        b_url = f"https://www.bing.com/images/async?q={encoded}&first=1&count=15&adlt=off&qft=+filterui:imagesize-large"
        r = requests.get(b_url, headers=HEADERS, timeout=18)
        if r.status_code == 200:
            urls = re.findall(r'murl&quot;:&quot;(https?://[^&]+?\.(?:jpg|jpeg|png))&quot;', r.text)
            fresh = [u for u in urls if u not in USED_MEDIA_URLS]
            for img_url in fresh[:6]:
                try:
                    USED_MEDIA_URLS.add(img_url)
                    img_r = requests.get(img_url, headers=HEADERS, timeout=12)
                    if img_r.status_code == 200 and len(img_r.content) > 18000:
                        with open(filename, "wb") as f:
                            f.write(img_r.content)
                        if verify_and_grade_image(filename):
                            print(f"  [🌐 BING HD PHOTO] Downloaded for '{query}'")
                            return filename
                except Exception:
                    continue
    except Exception:
        pass

    img = Image.new("RGB", (1080, 1920), (16, 18, 34))
    img.save(filename, "JPEG", quality=92)
    return filename


def verify_and_grade_image(filepath):
    try:
        with Image.open(filepath) as im:
            im = im.convert("RGB")
            w, h = im.size
            if w < 220 or h < 220:
                return False
            im = ImageEnhance.Contrast(im).enhance(1.18)
            im = ImageEnhance.Color(im).enhance(1.12)
            im = ImageEnhance.Brightness(im).enhance(0.94)
            im.save(filepath, "JPEG", quality=92)
        return True
    except Exception:
        return False


# =====================================================================
# PURE-PYTHON SACRED CINEMATIC SFX & BGM SYNTHESIZER
# =====================================================================
def write_synthesized_wav(filename, duration_sec, sample_fn, sample_rate=44100):
    """Writes a 16-bit mono WAV file using pure Python math (100% crash-proof)."""
    num_samples = int(duration_sec * sample_rate)
    with wave.open(filename, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        frames = bytearray()
        for i in range(num_samples):
            t = i / float(sample_rate)
            val = max(-1.0, min(1.0, sample_fn(t, duration_sec)))
            frames.extend(struct.pack("<h", int(val * 32767.0)))
        wf.writeframes(frames)
    return filename


def generate_cinematic_sfx_library():
    """Generates warm, reverent documentary transition SFX in pure Python."""
    sfx_files = {}

    # 1. Deep Prophetic Timpani / Sub Boom
    sfx_files["boom"] = write_synthesized_wav(
        "sfx_boom.wav", 1.4,
        lambda t, d: 0.65 * math.exp(-2.8 * t) * math.sin(2.0 * math.pi * (72.0 * math.exp(-1.2 * t) + 36.0) * t)
    )

    # 2. Gentle Wind / Spirit Breath Swell
    sfx_files["whoosh"] = write_synthesized_wav(
        "sfx_whoosh.wav", 1.0,
        lambda t, d: 0.45 * math.sin(math.pi * (t / d)) * (
            0.6 * math.sin(2.0 * math.pi * 196.0 * t) + 0.4 * math.sin(2.0 * math.pi * 293.66 * t)
        )
    )

    # 3. Orchestral Harmonic Riser
    sfx_files["riser"] = write_synthesized_wav(
        "sfx_riser.wav", 1.2,
        lambda t, d: 0.45 * (t / d) * math.sin(math.pi * (t / d)) * (
            0.5 * math.sin(2.0 * math.pi * 220.0 * t) + 0.5 * math.sin(2.0 * math.pi * 329.63 * t)
        )
    )

    # 4. Warm Celestial Chime / Bell Resonance
    sfx_files["pulse"] = write_synthesized_wav(
        "sfx_pulse.wav", 1.1,
        lambda t, d: 0.40 * math.exp(-3.5 * t) * (
            0.6 * math.sin(2.0 * math.pi * 528.0 * t) + 0.4 * math.sin(2.0 * math.pi * 264.0 * t)
        )
    )

    return sfx_files


async def synthesize_scene_voice(urdu_text, index, sfx_path=None):
    """Synthesizes Deep, Majestic, Philosophical First-Person Urdu Voiceover with Subtle Cathedral Echo."""
    raw_audio = f"raw_voice_{index}.mp3"
    voice_clean = f"voice_clean_{index}.m4a"
    mastered_audio = f"voice_{index}.m4a"

    # Deep, measured, philosophical cadence (-6% speed, -6Hz deep resonant pitch)
    communicate = edge_tts.Communicate(urdu_text, voice="ur-PK-AsadNeural", rate="-6%", pitch="-6Hz")
    await communicate.save(raw_audio)

    # Warm low-end EQ + subtle sacred room echo (aecho) + dramatic 0.40s pause between scenes
    af_chain = (
        "silenceremove=start_periods=1:start_silence=0.05:start_threshold=-45dB,"
        "highpass=f=65,"
        "bass=g=5.5:f=95,"
        "treble=g=2.5:f=4200,"
        "aecho=0.8:0.88:45:0.16,"
        "acompressor=threshold=-16dB:ratio=3.2:attack=8:release=90:makeup=3.5dB,"
        "apad=pad_dur=0.40"
    )
    subprocess.run([
        "ffmpeg", "-y", "-i", raw_audio,
        "-af", af_chain,
        "-ar", "44100", "-ac", "2", "-c:a", "aac", "-b:a", "192k",
        voice_clean
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if sfx_path and os.path.exists(sfx_path):
        try:
            subprocess.run([
                "ffmpeg", "-y",
                "-i", voice_clean,
                "-i", sfx_path,
                "-filter_complex", "[1:a]volume=0.18[sfx];[0:a][sfx]amix=inputs=2:duration=first:dropout_transition=1[a]",
                "-map", "[a]", "-ar", "44100", "-ac", "2", "-c:a", "aac", "-b:a", "192k",
                mastered_audio
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return mastered_audio
        except Exception:
            pass

    return voice_clean


# =====================================================================
# SACRED DOCUMENTARY HUD OVERLAY (GOLD & ROYAL THEME)
# =====================================================================
def create_burned_hud_overlay(caption_text, badge_text, act_text, scene_idx, total_scenes, part_num):
    overlay = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    for y in range(320):
        alpha = int(190 * (1 - y / 320))
        draw.line([(0, y), (1080, y)], fill=(0, 0, 0, alpha))
    for y in range(1140, 1920):
        alpha = int(235 * ((y - 1140) / 780))
        draw.line([(0, y), (1080, y)], fill=(0, 0, 0, alpha))

    try:
        act_font = ImageFont.truetype(FONT_BOLD, 28)
        badge_font = ImageFont.truetype(FONT_BOLD, 36)
        cap_font = ImageFont.truetype(FONT_BOLD, 62)
    except Exception:
        act_font = ImageFont.load_default()
        badge_font = ImageFont.load_default()
        cap_font = ImageFont.load_default()

    # Top Royal Crimson/Gold Pill
    bw, bh = 680, 78
    bx, by = (1080 - bw) // 2, 78
    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=39, fill=(145, 22, 35, 245), outline=(255, 215, 0, 245), width=4)
    b_text = badge_text.upper()[:24]
    b_bbox = draw.textbbox((0, 0), b_text, font=badge_font)
    b_tw, b_th = b_bbox[2] - b_bbox[0], b_bbox[3] - b_bbox[1]
    draw.text((bx + (bw - b_tw) // 2, by + (bh - b_th) // 2 - 4), b_text, font=badge_font, fill=(255, 245, 215, 255))

    # Act Tag
    act_str = f"✝️ {act_text.upper()}  •  HISSA {scene_idx + 1}/{total_scenes}"
    a_bbox = draw.textbbox((0, 0), act_str, font=act_font)
    a_tw = a_bbox[2] - a_bbox[0]
    draw.rounded_rectangle([(1080 - a_tw) // 2 - 24, 172, (1080 + a_tw) // 2 + 24, 218], radius=14, fill=(18, 22, 38, 225), outline=(255, 215, 0, 190), width=2)
    draw.text(((1080 - a_tw) // 2, 180), act_str, font=act_font, fill=(255, 225, 110, 255))

    # Subtitle Card
    lines = textwrap.wrap(caption_text.upper(), width=16)
    if not lines:
        lines = ["KHUDAWAND KA KALAM"]

    line_height = 88
    total_text_h = len(lines) * line_height
    box_y1 = 1365 - (total_text_h // 2)
    box_y2 = box_y1 + total_text_h + 44

    draw.rounded_rectangle([50, box_y1, 1030, box_y2], radius=26, fill=(10, 14, 26, 235), outline=(255, 215, 0, 235), width=4)

    for i, line in enumerate(lines):
        t_bbox = draw.textbbox((0, 0), line, font=cap_font)
        tw = t_bbox[2] - t_bbox[0]
        tx = (1080 - tw) // 2
        ty = box_y1 + 20 + (i * line_height)

        if part_num == 1:
            fill_col = (255, 225, 75, 255) if i == 0 else (255, 255, 255, 255)
        else:
            fill_col = (135, 235, 255, 255) if i == 0 else (255, 225, 75, 255)

        for dx, dy in [(-4, -4), (4, -4), (-4, 4), (4, 4), (0, 5)]:
            draw.text((tx + dx, ty + dy), line, font=cap_font, fill=(0, 0, 0, 255))
        draw.text((tx, ty), line, font=cap_font, fill=fill_col)

    progress_fraction = (scene_idx + (0.5 if part_num == 1 else 1.0)) / total_scenes
    prog_w = int(980 * progress_fraction)
    draw.rounded_rectangle([50, 1835, 1030, 1855], radius=10, fill=(255, 255, 255, 75))
    draw.rounded_rectangle([50, 1835, 50 + max(prog_w, 25), 1855], radius=10, fill=(255, 215, 0, 255))

    out_png = f"hud_{scene_idx}_p{part_num}.png"
    overlay.save(out_png)
    return out_png


def get_audio_duration(audio_path):
    out = subprocess.check_output([
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        audio_path
    ]).decode().strip()
    return max(float(out), 3.5)


def prepare_visual_subclip(media_path, is_video, overlay_path, duration, sub_idx, out_clip):
    if is_video:
        vf = (
            "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
            "crop=1080:1920,setsar=1,eq=contrast=1.08:saturation=1.12[bg];"
            "[bg][1:v]overlay=0:0:shortest=1,format=yuv420p[v]"
        )
        cmd = [
            "ffmpeg", "-y",
            "-stream_loop", "-1", "-t", str(duration), "-i", media_path,
            "-loop", "1", "-t", str(duration), "-i", overlay_path,
            "-filter_complex", vf,
            "-map", "[v]", "-r", "24", "-an",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
            out_clip
        ]
    else:
        direction = 1 if sub_idx % 2 == 0 else -1
        vf = (
            f"[0:v]scale=1240:2200:force_original_aspect_ratio=increase,crop=1240:2200,setsar=1,"
            f"crop=1080:1920:'(in_w-out_w)/2+({direction}*45)*sin(t*0.8)':'(in_h-out_h)/2+55*cos(t*0.65)'[bg];"
            f"[bg][1:v]overlay=0:0:shortest=1,format=yuv420p[v]"
        )
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-t", str(duration), "-i", media_path,
            "-loop", "1", "-t", str(duration), "-i", overlay_path,
            "-filter_complex", vf,
            "-map", "[v]", "-r", "24", "-an",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
            out_clip
        ]

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        safe_vf = (
            "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1[bg];"
            "[bg][1:v]overlay=0:0:shortest=1,format=yuv420p[v]"
        )
        safe_cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-t", str(duration), "-i", media_path,
            "-loop", "1", "-t", str(duration), "-i", overlay_path,
            "-filter_complex", safe_vf,
            "-map", "[v]", "-r", "24", "-an",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
            out_clip
        ]
        subprocess.run(safe_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def render_two_cut_scene(scene, idx, total_scenes, badge, sfx_library):
    sfx_type = scene.get("sfx_type", "whoosh")
    sfx_file = sfx_library.get(sfx_type)

    audio_path = asyncio.run(synthesize_scene_voice(scene["tts_urdu"], idx, sfx_file))
    total_dur = get_audio_duration(audio_path)
    half_dur = round(total_dur / 2.0, 2)
    rem_dur = round(total_dur - half_dur, 2)

    q1 = scene.get("search_query_1", "sunbeams clouds")
    q2 = scene.get("search_query_2", "praying hands light")
    v_q = scene.get("video_query", q1)
    pref = scene.get("media_source_pref", "pixabay")
    act_text = scene.get("act", "KALAM-E-MUQADDAS")

    vid_file = fetch_contextual_stock_video(v_q, f"stock_vid_{idx}.mp4", pref=pref) if v_q else None
    if vid_file:
        media1, is_vid1 = vid_file, True
    else:
        media1 = fetch_exact_scene_photo(
