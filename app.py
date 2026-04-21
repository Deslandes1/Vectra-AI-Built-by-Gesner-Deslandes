import streamlit as st
import base64
from PIL import Image
import io

st.set_page_config(page_title="Vectra AI – Master Build", layout="wide")

# --- 1. INITIALIZATION (Prevents NameError) ---
# We define these at the start so they exist even before the sidebar logic runs.
speed_limit = 40  
sim_limit = 2.6   # Default calculation (40 / 15)

# --- 2. SIDEBAR & ROADMAP LOGIC ---
with st.sidebar:
    st.header("🚦 Road Controls")
    speed_limit = st.select_slider(
        "Set Road Speed Limit (MPH)", 
        options=[20, 30, 40, 50, 60, 70, 80], 
        value=40
    )
    # Update sim_limit based on user selection
    sim_limit = speed_limit / 15 
    
    st.divider()
    st.header("🗺️ Roadmap Integration")
    uploaded_file = st.file_uploader("Upload top-down roadmap...", type=["jpg", "png", "jpeg"])
    
    roadmap_b64 = ""
    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        roadmap_b64 = base64.b64encode(buffered.getvalue()).decode()
        st.success("Roadmap Loaded")

# --- 3. MAIN UI & VIDEO ---
st.markdown(f"""
<div style="text-align: center;">
    <h1>🚗 Vectra AI – Intelligent Highway</h1>
    <p style="font-size: 1.1rem;">built by <strong>Gesner Deslandes</strong></p>
    <p>Real-time coordination: Oncoming cars never collide with each other.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("## 🎥 Vectra AI in Action")
video_url = "https://raw.githubusercontent.com/Deslandes1/Vectra-AI-Built-by-Gesner-Deslandes/main/AI%20Selfdriving.mp4"
st.video(video_url)

# --- 4. SIMULATION ENGINE ---
# We use f-string with {{ }} to protect JS brackets from Python
sim_html = f"""
<canvas id="gameCanvas" width="900" height="500" tabindex="0" style="display: block; margin: 0 auto; border: 2px solid #b87c4f; border-radius: 12px;"></canvas>
<div style="text-align: center; font-family: monospace; font-size: 1.2rem; margin-top: 10px; color: white;">
    🧠 AI Status: <span id="status">Active</span> &nbsp;|&nbsp; 
    ⏱️ Speed: <span id="currSpeed">0</span> MPH &nbsp;|&nbsp;
    🚗 Traffic: <span id="obsActive">0</span>
</div>
<div style="text-align: center; margin-top: 10px;">
    <button id="resetBtn" style="background: #b87c4f; color: white; padding: 8px 16px; border-radius: 8px; border: none; cursor: pointer;">🔄 Reset Drive</button>
    <button id="spawnBtn" style="background: #b87c4f; color: white; padding: 8px 16px; border-radius: 8px; border: none; cursor: pointer;">🎲 Add Oncoming Car</button>
</div>

<script>
    (function() {{
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const W = 900, H = 500, CAR_W = 34, CAR_H = 20;
        const GAP_THRESHOLD = 80; 
        
        let car = {{ x: 50, y: 0, speed: 0, alive: true }};
        let obstacles = [];
        const SPEED_LIMIT = {sim_limit}; 

        function getRoadCenterY(x) {{
            return H/2 + 30 + Math.sin(x / 90) * 45 + Math.sin(x / 200) * 25;
        }}

        function update() {{
            if (!car.alive) return;

            // Player Physics
            car.speed += (SPEED_LIMIT - car.speed) * 0.05;
            car.x += car.speed;

            // Boundary Protection: Reset with safety check
            if (car.x > W + 50) {{
                let startIsClear = obstacles.every(o => o.x > 150 || o.x < -20);
                if (startIsClear) {{
                    car.x = -50;
                }} else {{
                    car.x = W + 49; 
                }}
            }}
            car.y = getRoadCenterY(car.x) + 18 - (CAR_H/2);
            document.getElementById('currSpeed').innerText = Math.round(car.speed * 15);

            // INTELLIGENT TRAFFIC (No-Crash Left Lane)
            obstacles.sort((a, b) => a.x - b.x); 

            for (let i = 0; i < obstacles.length; i++) {{
                let o = obstacles[i];
                let targetSpeed = -2.5;

                if (i > 0) {{
                    let leader = obstacles[i-1];
                    let gap = o.x - (leader.x + CAR_W);
                    if (gap < GAP_THRESHOLD) {{
                        targetSpeed = leader.speed;
                        if (gap < 25) targetSpeed = -0.1; 
                    }}
                }}
                o.speed = targetSpeed;
                o.x += o.speed;
                o.y = getRoadCenterY(o.x) - 18 - (CAR_H/2);
            }}

            obstacles = obstacles.filter(o => o.x > -100);
            document.getElementById('obsActive').innerText = obstacles.length;

            // Collision Check (Player vs Traffic)
            for (let o of obstacles) {{
                if (car.x < o.x + CAR_W && car.x + CAR_W > o.x && 
                    car.y < o.y + CAR_H && car.y + CAR_H > o.y) {{
                    car.alive = false;
                    document.getElementById('status').innerText = "CRASHED";
                }}
            }}
        }}

        function draw() {{
            ctx.fillStyle = "#0e1117";
            ctx.fillRect(0, 0, W, H);
            
            // Draw Road
            ctx.beginPath(); ctx.moveTo(-50, getRoadCenterY(-50));
            for (let x = 0; x <= W + 50; x += 10) ctx.lineTo(x, getRoadCenterY(x));
            ctx.lineWidth = 100; ctx.strokeStyle = "#444"; ctx.stroke();

            // Center Line
            ctx.beginPath(); ctx.setLineDash([15, 15]);
            for (let x = 0; x <= W; x += 5) ctx.lineTo(x, getRoadCenterY(x));
            ctx.lineWidth = 3; ctx.strokeStyle = "#ffd700"; ctx.stroke(); ctx.setLineDash([]);

            // Draw Car (Blue)
            ctx.fillStyle = car.alive ? "#00d4ff" : "#f00";
            ctx.fillRect(car.x, car.y, CAR_W, CAR_H);
            
            // Draw Traffic (Red)
            ctx.fillStyle = "#ff4b4b";
            for (let o of obstacles) ctx.fillRect(o.x, o.y, CAR_W, CAR_H);
        }}

        function loop() {{ update(); draw(); requestAnimationFrame(loop); }}

        document.getElementById('spawnBtn').onclick = () => {{
            let entryBlocked = obstacles.some(o => o.x > W - 70);
            if (!entryBlocked) {{
                obstacles.push({{ x: W + 50, y: 0, speed: -2.5 }});
            }}
        }};

        document.getElementById('resetBtn').onclick = () => {{ 
            car.x = 50; car.speed = 0; car.alive = true; obstacles = []; 
            document.getElementById('status').innerText = "Active";
        }};

        loop();
    }})();
</script>
"""

st.components.v1.html(sim_html, height=600)

# --- 5. TECHNICAL EXPLANATIONS ---
st.markdown(f"""
---
### 🧠 System Specifications & Logic
* **Road Speed Limit:** Governed at **{speed_limit} MPH**.
* **Acceleration Model:** Uses a 0.05 coefficient for realistic inertia (the "lean").
* **Oncoming Safety:** Opposite traffic uses a **Leader-Follower Spacing Algorithm** to maintain a minimum 80px gap.
* **Teleportation Buffer:** The car checks if the starting area is clear before resetting, preventing "spawn-frag" crashes at the road's edge.

<div style="text-align: center; margin-top: 20px; color: #888; font-size: 0.8rem;">
    Vectra AI built by <strong>Gesner Deslandes</strong> – GlobalInternet.py
</div>
""", unsafe_allow_html=True)
