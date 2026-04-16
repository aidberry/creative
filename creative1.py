import streamlit as st
import requests
import json
import base64
from PIL import Image
import io

# --- CONFIGURATION ---
OPENROUTER_API_KEY = "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"
DEFAULT_MODEL = "google/gemini-flash-1.5-8b"

st.set_page_config(
    page_title="VokasiUI Creative Analyst",
    page_icon="⚡",
    layout="wide"
)

# --- CUSTOM STYLING ---
st.markdown("""
    <style>
    .main {
        background-color: #f8fafc;
    }
    .stButton>button {
        width: 100%;
        border-radius: 15px;
        height: 3em;
        background-color: #4f46e5;
        color: white;
        font-weight: bold;
        border: none;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #4338ca;
        transform: scale(1.02);
    }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 20px;
        border: 1px solid #e2e8f0;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    }
    .cultural-box {
        background-color: #ffffff;
        border-left: 5px solid #4f46e5;
        padding: 20px;
        border-radius: 10px;
        font-style: italic;
        color: #334155;
        margin-bottom: 25px;
    }
    .mean-card {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        color: white;
        padding: 30px;
        border-radius: 25px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_stdio=True)

# --- HELPER FUNCTIONS ---
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode('utf-8')

def analyze_creative(image_base64, model_name):
    system_prompt = """
    Bertindaklah sebagai anggota dari audiens spesifik ini: Seorang mahasiswa Produksi Media berusia 20 tahun di Vokasi UI. Kamu adalah digital native yang menggunakan AI setidaknya satu jam sehari untuk brainstorming kampanye iklan kreatif. Kamu menghargai ide-ide yang unik, relevan, dan menyentuh emosi. 
    
    Langkah Kerja:
    Tuliskan satu paragraf "Analisis Resonansi Budaya" singkat (identifikasi elemen visual/verbal Indonesia: tongkrongan, ojol, gaya anak Jaksel/Depok, dll). Gunakan istilah Gen Z (relate, cringe, garing, epic).
    
    Task: Evaluasi kreativitas ini skala 1-7.
    1. Novelty (N1: Unik, N2: Plot Twist)
    2. Meaningfulness (M1: Fungsional Lokal, M2: Kejelasan Pesan)
    3. Connectedness (C1: Relatable, C2: Emosi Kolektif)

    Gunakan perspektif High-Context Communication.
    Output HANYA JSON:
    {
        "cultural_analysis": "isi analisis",
        "scores": {"N1": 0, "N2": 0, "M1": 0, "M2": 0, "C1": 0, "C2": 0},
        "mean": 0
    }
    """
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Evaluasi iklan ini sesuai instruksi."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                ]
            }
        ]
    }
    
    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        content = response.json()['choices'][0]['message']['content']
        # Extract JSON if model wraps it in markdown
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        return json.loads(content)
    except Exception as e:
        return {"error": str(e)}

# --- UI LAYOUT ---
st.title("⚡ VokasiUI Creative Analyst")
st.caption("Framework NMC (Novelty, Meaningfulness, Connectedness) untuk Mahasiswa Produksi Media")

with st.sidebar:
    st.header("Settings")
    selected_model = st.selectbox(
        "Pilih AI Model",
        ["google/gemini-flash-1.5-8b", "google/gemini-pro-1.5-exp", "openai/gpt-4o"],
        index=0
    )
    st.info("Persona: Mahasiswa Prodimed UI (Gen Z). AI ini akan menilai seberapa 'relate' konten lo.")
    
col1, col2 = st.columns([1, 1.5], gap="large")

with col1:
    st.subheader("📁 Upload Konten")
    uploaded_file = st.file_uploader("Pilih gambar iklan (JPG/PNG)", type=['png', 'jpg', 'jpeg'])
    
    if uploaded_file:
        st.image(uploaded_file, use_column_width=True, caption="Preview Iklan")
        analyze_btn = st.button("RUN ANALYSIS")
    else:
        st.info("Upload file dulu buat mulai analisis.")

with col2:
    if uploaded_file and 'analyze_btn' in locals() and analyze_btn:
        with st.spinner("Lagi mikir ala anak Vokasi... 🧠"):
            img_b64 = encode_image(uploaded_file)
            result = analyze_creative(img_b64, selected_model)
            
            if "error" in result:
                st.error(f"Error: {result['error']}")
            else:
                st.subheader("📝 Analisis Resonansi Budaya")
                st.markdown(f'<div class="cultural-box">{result["cultural_analysis"]}</div>', unsafe_allow_stdio=True)
                
                # Scores Grid
                s = result['scores']
                m_col1, m_col2, m_col3 = st.columns(3)
                
                with m_col1:
                    st.markdown("**Novelty**")
                    st.metric("N1: Unik", s['N1'])
                    st.metric("N2: Twist", s['N2'])
                    
                with m_col2:
                    st.markdown("**Meaningful**")
                    st.metric("M1: Fungsi", s['M1'])
                    st.metric("M2: Jelas", s['M2'])
                    
                with m_col3:
                    st.markdown("**Connected**")
                    st.metric("C1: Relate", s['C1'])
                    st.metric("C2: Emosi", s['C2'])
                
                st.markdown("---")
                
                # Mean Score
                mean_val = result['mean']
                status = "KONTEN EPIC 🔥" if mean_val >= 5.5 else "RELATE BANGET 👍" if mean_val >= 4 else "AGAK GARING 🧊"
                
                st.markdown(f"""
                    <div class="mean-card">
                        <p style="margin:0; font-size: 0.9em; opacity: 0.8;">OVERALL MEAN SCORE</p>
                        <h1 style="margin:0; font-size: 4em;">{mean_val:.2f} <span style="font-size: 0.4em;">/ 7.0</span></h1>
                        <p style="margin-top:10px; font-weight: bold; letter-spacing: 2px;">{status}</p>
                    </div>
                """, unsafe_allow_stdio=True)
                
    else:
        st.write("### Hasil analisis bakal muncul di sini...")
        st.image("[https://api.dicebear.com/7.x/bottts/svg?seed=waiting](https://api.dicebear.com/7.x/bottts/svg?seed=waiting)", width=100)

st.markdown("---")
st.caption("Dibuat untuk Ekselensi Kreatif Mahasiswa UI © 2024")
