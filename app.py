import streamlit as st
import base64
from PIL import Image
import io

st.set_page_config(page_title="Vectra AI – Perfect Flow", layout="wide")

# --- 1. INITIALIZATION ---
speed_limit = 40  
sim_limit = 2.6   

# --- 2. SIDEBAR CONTROLS & ROADMAP ---
with st.sidebar:
    st.header("🚦 Traffic Control")
    speed_limit = st.select_slider("AI Speed Limit (MPH)", options=[20, 30, 40, 50, 60, 70, 80], value=40)
    sim_limit = speed_limit / 15 
    
    st.divider()
    
    # --- ADDED ROADMAP SECTION ---
    st.header("🗺️ Project Roadmap")
    # Using the RAW github link so Streamlit can render the image directly
    roadmap_url = "https://raw.githubusercontent.com/Deslandes1/Vectra-AI-Built-by-Gesner-Deslandes/main/Gemini_Generated_Image_mcrtf8mcrtf8mcrt.png"
    st.image(roadmap_url, caption="Vectra AI Development Phases", use_container_width=True)
    
    st.divider()
    uploaded_file = st.file_uploader("Upload custom roadmap overlay", type=["jpg", "png", "jpeg"])

# --- 3. UI HEADER ---
st.markdown(f"""
<div style="text-align: center;">
    <h1>🚗 Vectra AI – Zero-Collision Autopilot</h1>
    <p style="font-size: 1.1rem;">built by <strong>Gesner Deslandes</strong></p>
</div>
""", unsafe_allow_html=True)

# Main Demo Video
st.video("https://raw.githubusercontent.com/Deslandes1/Vectra-AI-Built-by-Gesner-Deslandes/main/AI%20Selfdriving.mp4")

# --- 4. SIMULATION ENGINE ---
# (Logic remains exactly the same as our previous fixed version)
sim_html = f"""
<canvas id="gameCanvas" width="900" height="500" style="display: block; margin: 0 auto; border: 2px solid #b87c4f; border-radius: 12px;"></canvas>
<div style="text-align: center; font-family: monospace; font-size: 1.2rem; margin-top: 10px; color: white;">
    🧠 AI Status: <span id="status" style="color: #00ff00;">ONLINE</span> &nbsp;|&nbsp; 
    ⏱️ Speed: <span id="currSpeed">0</span> MPH
</div>

<script>
    (function() {{
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const W = 900, H = 500, CAR_W = 34, CAR_H = 20;
        const SAFE_BUBBLE = 85; 
        
        let car = {{ x: 50, y: 0, speed: 0, alive: true }};
        let obstacles = [];
        const SPEED_LIMIT = {sim_limit}; 

        function getRoadY(x) {{
            return H/2 + 30 + Math.sin(x / 90) * 45 + Math.sin(x / 200) * 25;
        }}

        function update() {{
            car.speed += (SPEED_LIMIT - car.speed) * 0.05;
            car.x += car.speed;

            if (car.x > W + 50) {{
                let resetZoneClear = obstacles.every(o => o.x > 150 || o.x < -20);
                if (resetZoneClear) {{
                    car.x = -50;
                }} else {{
                    car.x = W + 49; 
                }}
            }}
            car.y = getRoadY(car.x) + 18 - (CAR_H/2);
            document.getElementById('currSpeed').innerText = Math.round(car.speed * 15);

            obstacles.sort((a, b) => a.x - b.x); 
            for (let i = 0; i < obstacles.length; i++) {{
                let o = obstacles[i];
                let targetVel = -2.5;

                if (i > 0) {{
                    let leader = obstacles[i-1];
                    let gap = o.x - (leader.x + CAR_W);
                    if (gap < SAFE_BUBBLE) {{
                        targetVel = leader.speed;
                        if (gap < 25) targetVel = -0.1; 
                    }}
                }}
                o.speed = targetVel;
                o.x += o.speed;
                o.y = getRoadY(o.x) - 18 - (CAR_H/2);
            }}
            obstacles = obstacles.filter(o => o.x > -100);
        }}

        function draw() {{
            ctx.fillStyle = "#0e1117";
            ctx.fillRect(0, 0, W, H);
            ctx.beginPath(); ctx.moveTo(-50, getRoadY(-50));
            for (let x = 0; x <= W + 50; x += 10) ctx.lineTo(x, getRoadY(x));
            ctx.lineWidth = 100; ctx.strokeStyle = "#444"; ctx.stroke();
            ctx.beginPath(); ctx.setLineDash([15, 15]);
            for (let x = 0; x <= W; x += 5) ctx.lineTo(x, getRoadY(x));
            ctx.lineWidth = 3; ctx.strokeStyle = "#ffd700"; ctx.stroke(); ctx.setLineDash([]);
            ctx.fillStyle = "#00d4ff";
            ctx.fillRect(car.x, car.y, CAR_W, CAR_H);
            ctx.fillStyle = "#ff4b4b";
            for (let o of obstacles) ctx.fillRect(o.x, o.y, CAR_W, CAR_H);
        }}

        function loop() {{ update(); draw(); requestAnimationFrame(loop); }}
        
        setInterval(() => {{
            if (obstacles.length < 4) {{
                let entryClear = obstacles.every(o => o.x < W - 100);
                if (entryClear) obstacles.push({{ x: W + 50, y: 0, speed: -2.5 }});
            }}
        }}, 3000);

        loop();
    }})();
</script>
"""

st.components.v1.html(sim_html, height=600)
