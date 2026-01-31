import streamlit as st
import google.generativeai as pillow
import tempfile
import os
import time
from PIL import Image

st.set_page_config(page_title="Video Prompt Studio", layout="wide")

# UI Sederhana tapi Powerfull
st.title("Video-to-Prompt Cinematic")
st.sidebar.title("Control Center")

gemini_key = st.sidebar.text_input("Gemini API Key", type="password")
face_file = st.sidebar.file_uploader("Upload Foto Wajah", type=['png', 'jpg', 'jpeg'])

col1, col2 = st.columns(2)

with col1:
    st.header("Input Video")
    video_file = st.file_uploader("Upload Video Model", type=['mp4', 'mov', 'avi'])
    if video_file:
        st.video(video_file)

with col2:
    st.header("Settings")
    gender = st.selectbox("Jenis Kelamin", ["Original", "Pria", "Wanita"])
    pose = st.selectbox("Pose", ["Sesuai Video", "Catwalk", "Hypebeast"])
    generate_btn = st.button("GENERATE PROMPT")

if generate_btn:
    if not gemini_key:
        st.error("Isi API Key dulu bro!")
    elif not video_file:
        st.error("Upload videonya dulu!")
    else:
        try:
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            with st.spinner("Menganalisis..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp:
                    tmp.write(video_file.read())
                    video_path = tmp.name
                
                video_part = genai.upload_file(path=video_path)
                while video_part.state.name == "PROCESSING":
                    time.sleep(2)
                    video_part = genai.get_file(video_part.name)
                
                response = model.generate_content([video_part, "Create a high-quality cinematic prompt for this video. Focus on 8k detail and fashion style."])
                st.success("Berhasil!")
                st.code(response.text)
                os.remove(video_path)
        except Exception as e:
            st.error(f"Error: {str(e)}")
