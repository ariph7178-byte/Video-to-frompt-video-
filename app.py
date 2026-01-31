import streamlit as st
import google.generativeai as genai
import tempfile
import os
import time

# --- Konfigurasi Halaman ---
st.set_page_config(page_title="Cinematic Video-to-Prompt Pro", layout="wide")

# Custom CSS untuk tampilan premium
st.markdown("""
    <style>
    .main { background-color: #0f172a; color: #f8fafc; }
    .stSelectbox, .stSlider, .stTextInput { border-radius: 10px; }
    .stButton>button {
        width: 100%;
        background: linear-gradient(45deg, #4f46e5, #9333ea);
        color: white;
        border: none;
        padding: 12px;
        font-weight: bold;
        border-radius: 12px;
        transition: 0.3s;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 4px 20px rgba(79, 70, 229, 0.4); }
    .result-box {
        background-color: #1e293b;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #334155;
        font-family: 'Courier New', Courier, monospace;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Sidebar: API Keys & Identity Lock ---
with st.sidebar:
    st.title(" Control Center")
    gemini_key = st.text_input("Gemini API Key", type="password", help="Dapatkan di Google AI Studio")
    
    st.divider()
    st.header("👤 Identity Lock")
    face_file = st.file_uploader("Upload Foto Wajah (Reference)", type=['png', 'jpg', 'jpeg'])
    if face_file:
        st.image(face_file, caption="Wajah Terkunci", use_container_width=True)

    st.divider()
    st.info("Aplikasi ini menggunakan Gemini 2.5 Flash untuk analisis video & image-to-prompt.")

# --- Main UI ---
st.title("🎬 Video-to-Prompt Cinematic Master")
st.subheader("Ubah video model menjadi Master Technical Prompt 8K")

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.header("📤 Input Video")
    video_file = st.file_uploader("Upload Video Model", type=['mp4', 'mov', 'avi'])
    if video_file:
        st.video(video_file)

    st.header("🎯 Detail Karakter")
    c1, c2 = st.columns(2)
    with c1:
        gender = st.selectbox("Jenis Kelamin", ["Original", "Pria", "Wanita", "Androgynous"])
        expression = st.selectbox("Ekspresi Wajah", ["Sesuai Video", "High-Fashion Pout", "Smirk", "Determined", "Serene"])
        pose = st.selectbox("Pose Model", ["Sesuai Video", "Catwalk Walk", "Hypebeast Squat", "Hand on Hip", "Dynamic Motion"])
    with c2:
        shot_type = st.selectbox("Shot Type", ["Full Body", "Medium Shot", "Close-up", "Wide Angle"])
        angle = st.selectbox("Camera Angle", ["Eye Level", "Low Angle (Heroic)", "High Angle", "Dutch Angle"])
        fidelity = st.slider("Fidelity Level (Kemiripan)", 0.0, 1.0, 0.8, help="Semakin tinggi, semakin mirip dengan video asli.")

with col2:
    st.header("🌍 Atmosfer & Style")
    c3, c4 = st.columns(2)
    with c3:
        bg_loc = st.selectbox("Background/Location", ["Studio Minimalis", "Cyberpunk City", "Parisian Street", "Lush Forest", "Luxury Penthouse"])
        art_style = st.selectbox("Art Style", ["Photorealistic Cinematic", "Anime Style", "Vogue Magazine", "3D Octane Render"])
    with c4:
        lighting = st.selectbox("Lighting", ["Natural Sunlight", "Neon Glow", "Studio Softbox", "Golden Hour", "Dramatic Rim Light"])
        tone = st.selectbox("Color Tone", ["Neutral", "Warm (Golden)", "Cold (Cinematic Blue)", "Moody Teal & Orange"])
    
    st.divider()
    generate_btn = st.button("🚀 GENERATE MASTER PROMPT")

# --- Logika Proses ---
if generate_btn:
    if not gemini_key:
        st.error("Silakan masukkan Gemini API Key di sidebar!")
    elif not video_file:
        st.error("Silakan upload video terlebih dahulu!")
    else:
        try:
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
            
            with st.status("Menganalisis video dan mengunci anatomi...", expanded=True) as status:
                # Simpan video sementara
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp:
                    tmp.write(video_file.read())
                    video_path = tmp.name

                st.write("Memproses video...")
                video_part = genai.upload_file(path=video_path)
                
                # Tunggu upload selesai
                while video_part.state.name == "PROCESSING":
                    time.sleep(2)
                    video_part = genai.get_file(video_part.name)

                # Persiapkan input analisis
                prompt_parts = [
                    video_part,
                    f"""Analyze this video and the uploaded images to create a master image generation prompt.
                    ANATOMY SHIELD: Ensure the prompt describes correct human proportions, 5 fingers per hand, and natural bone structure.
                    TEMPORAL MEMORY: Capture the fluid motion of the clothing textures and body movement.
                    
                    USER CUSTOMIZATIONS:
                    - Gender: {gender}
                    - Expression: {expression}
                    - Pose: {pose}
                    - Shot: {shot_type}
                    - Angle: {angle}
                    - Style: {art_style}
                    - Environment: {bg_loc}
                    - Lighting: {lighting}
                    - Color Tone: {tone}
                    - Fidelity: {fidelity} (If high, stay extremely close to original video details).
                    
                    OUTPUT FORMAT: Provide a structured 'Master Technical Prompt' for 8K cinematic rendering. Focus on camera lens (35mm, f/1.8), ISO, textures, and specific identity traits from the face reference image."""
                ]

                if face_file:
                    from PIL import Image
                    face_img = Image.open(face_file)
                    prompt_parts.append(face_img)

                st.write("Menyusun Master Prompt...")
                response = model.generate_content(prompt_parts)
                
                status.update(label="Analisis Selesai!", state="complete", expanded=False)

            # Menampilkan Hasil
            st.success("Master Technical Prompt Berhasil Dibuat!")
            st.markdown('<div class="result-box">' + response.text + '</div>', unsafe_allow_html=True)
            
            st.button("📋 Copy to Clipboard", on_click=lambda: st.write("Copied! (Gunakan manual copy di atas)"))
            
            # Cleanup
            os.remove(video_path)
            
        except Exception as e:
            st.error(f"Terjadi kesalahan teknis: {str(e)}")
