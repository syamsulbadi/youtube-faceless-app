"""
YouTube Faceless Automation App (Streamlit)
Author: ChatGPT
Date: 2025-11-10

Apa yang dilakukan aplikasi ini:
1) Membuat ide video, judul, deskripsi, tag, dan thumbnail otomatis.
2) Membuat video playlist dari musik yang kamu punya (berlisensi).
3) (Opsional) Upload ke YouTube otomatis lewat YouTube Data API v3.

⚠️ Catatan penting:
- Gunakan hanya audio yang kamu miliki haknya (misal: YouTube Audio Library, Pixabay, CC0).
- Jangan gunakan musik berhak cipta dari artis populer tanpa izin — bisa diblokir atau tidak dimonetisasi.
"""

import os, io, uuid, textwrap, re
import numpy as np
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from slugify import slugify
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, vfx
from pydub import AudioSegment
import streamlit as st

# ==========================================
# Konfigurasi Awal
# ==========================================
def ensure_dirs():
    os.makedirs("output/videos", exist_ok=True)
    os.makedirs("output/thumbnails", exist_ok=True)
    os.makedirs("output/logs", exist_ok=True)
    os.makedirs("assets/backgrounds", exist_ok=True)
    os.makedirs("assets/fonts", exist_ok=True)

# ==========================================
# Fungsi Bantu
# ==========================================
def sec_to_hms(s):
    s = int(s)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    if h: return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"

def pick_contrasty_text_color(bg):
    small = bg.resize((8, 8)).convert("L")
    avg = np.array(small).mean()
    return "white" if avg < 128 else "black"

# ==========================================
# Ide & Metadata Otomatis
# ==========================================
NICHES = {
    "Lo-fi / Ambient": [
        "Lo-fi Beats for Study & Chill",
        "Calm Cafe Beats for Writing",
        "Night Coding Lo-fi Session",
        "Ambient Rain & Soft Piano Mix",
        "Deep Focus: 1-Hour Chill Mix",
    ],
    "Tech & AI Tools": [
        "5 AI Tools to Speed Up Your Day",
        "Hidden Chrome Features You Need",
        "No-Code Apps to Automate Tasks",
        "Top Sites for Learning Coding Fast",
        "Weekly AI News Recap",
    ],
}

def generate_meta(niche, duration_min, keywords=""):
    base_titles = NICHES.get(niche, ["Daily Mix"])
    title = np.random.choice(base_titles)
    if duration_min >= 50:
        title = f"{title} — {duration_min} min"
    else:
        title = f"{title} — {duration_min}m"

    description = (
        f"Relax and enjoy this {niche.lower()} playlist.\n"
        "Perfect for study, work, or sleep.\n\n"
        "Chapters:\n"
        "00:00 Intro\n... (auto-filled after render)\n\n"
        "#lofi #study #focus #relax"
    )

    tags = ["lofi", "study", "focus", "music", "relax", "ambient"]
    if keywords:
        for k in re.split(r"[,\\n]", keywords):
            k = k.strip()
            if k and k not in tags:
                tags.append(k)
    return title, description, tags[:15]

