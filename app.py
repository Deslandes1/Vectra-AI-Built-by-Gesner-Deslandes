import streamlit as st
import base64
from PIL import Image
import io

st.set_page_config(page_title="Vectra AI – Master Build", layout="wide")

# --- Custom Styling ---
st.markdown("""
<style>
    body { margin: 0; background-color: #0e1117; }
    canvas { display: block; margin: 0 auto; border: 2px solid #b87c4f; border-radius: 12px; box-shadow: 0 0 20px rgba(0,0,0,0.5); }
    .info { text-align: center; font-family: monospace; font-size: 1.2rem; margin-top: 10px; color: white; }
    button { background: #b87c4f; border: none; color: white; padding: 8px 16px; font-weight: bold; border-radius: 8px; cursor: pointer; margin: 5px; }
    button:hover { background: #9a653f; }
    .footer { text-align: center; margin-top: 20px; color: #888; font-size: 0.8rem; }
</style>
""", unsafe_allow_html=True)

# --- Sidebar: Roadmap & Speed Controls ---
with st.sidebar:
    st.header("🚦 Road Controls")
    speed_limit = st.select_slider("Set Road Speed Limit (MPH)", options=[20, 30, 40, 50, 60, 70, 80], value=40)
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

st.markdown(f"""
<div style="text-align: center;">
    <h1>🚗 Vectra AI – Intelligent Highway</h1>
    <p style="font-size: 1.1rem;">built by <strong>Gesner Deslandes</strong></p>
    <p>Real-time coordination: Oncoming cars never collide with each other.</p>
</div>
""", unsafe_allow_html=True)

# --- Video Section ---
video_url = "https://raw.githubusercontent.com/Deslandes1/Vectra-AI-Built-by-Gesner-Deslandes/main/AI%20Selfdriving.mp4"
st.video(video_url)

# --- Simulation Logic ---
# Note: Using double curly braces {{ }} for JS blocks to escape Python's f-string
sim_html = f"""
<canvas id="gameCanvas" width="900" height="500" tabindex="0"></canvas>
<div class="info">
    🧠 AI Status: <span id="status">Active</span> &nbsp;|&nbsp; 
    ⏱️ Speed: <span id="currSpeed">0</span> MPH &nbsp;|&nbsp;
    🚗 Traffic: <span id="obsActive">0</span>
</div>
<div style="text-align: center; margin-top: 10px;">
    <button id="resetBtn">🔄 Reset Drive</button>
    <button id="spawnBtn">🎲 Add Oncoming Car</button>
</div>

<script>
    (function() {{
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const statusSpan = document.getElementById('status');
        const speedSpan = document.getElementById('currSpeed');
        const obsSpan = document.getElementById('obsActive');

        const W = 900, H = 500, CAR_W = 34, CAR_H = 20;
        const GAP_THRESHOLD = 70; 
        
        let car = {{ x: 50, y: 0, speed: 0, alive: true }};
        let obstacles = [];
        const SPEED_LIMIT = {sim_limit}; 

        function getRoadCenterY(x) {{
            return H/2 + 30 + Math.sin(x / 90) * 45 + Math.sin(x / 200) * 25;
        }}

        function update() {{
            if (!car.alive) return;

            // 1. Player Physics (The "Lean" Acceleration)
            car.speed += (SPEED_LIMIT - car.speed) * 0.05;
            car.x += car.speed;
            if (car.x > W + 50) car.x = -50;
            car.y = getRoadCenterY(car.x) + 18 - (CAR_H/2);
            speedSpan.innerText = Math.round(car.speed * 15);

            // 2. INTELLIGENT TRAFFIC (No-Crash Left Lane)
            obstacles.sort((a, b) => a.x - b.x); 

            for (let i = 0; i < obstacles.length; i++) {{
                let o = obstacles[i];
                let baseTarget = -2.5;

                if (i > 0) {{
                    let leader = obstacles[i-1];
                    let gap = o.x - (leader.x + CAR_W);
                    
                    // Maintain safe distance logic
                    if (gap < GAP_THRESHOLD) {{
                        o.speed = leader.speed; // Match speed to freeze gap
                        if (gap < 20) o.speed = -0.1; // Hard brake
                    }} else {{
                        o.speed = baseTarget;
                    }}
                }} else {{
                    o.speed = baseTarget;
                }}

                o.x += o.speed;
                o.y = getRoadCenterY(o.x) - 18 - (CAR_H/2);
            }}

            obstacles = obstacles.filter(o => o.x > -100);
            obsSpan.innerText = obstacles.length;

            // 3. Collision Logic (Player vs Traffic)
            for (let o of obstacles) {{
                if (car.x < o.x + CAR_W && car.x + CAR_W > o.x && 
                    car.y < o.y + CAR_H && car.y + CAR_H > o.y) {{
                    car.alive = false;
                    statusSpan.innerText = "CRASHED";
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

            // Player (Blue)
            ctx.fillStyle = car.alive ? "#00d4ff" : "#f00";
            ctx.fillRect(car.x, car.y, CAR_W, CAR_H);
            
            // Traffic (Red)
            ctx.fillStyle = "#ff4b4b";
            for (let o of obstacles) ctx.fillRect(o.x, o.y, CAR_W, CAR_H);
        }}

        function loop() {{ update(); draw(); requestAnimationFrame(loop); }}

        document.getElementById('spawnBtn').onclick = () => {{
            let lastCar = obstacles[obstacles.length - 1];
            if (!lastCar || lastCar.x < W - 50) {{
                obstacles.push({{ x: W + 50, y: 0, speed: -2.5 }});
            }}
        }};

        document.getElementById('resetBtn').onclick = () => {{ 
            car.x = 50; car.speed = 0; car.alive = true; obstacles = []; 
            statusSpan.innerText = "Active";
        }};

        loop();
    }})();
</script>
"""

st.components.v1.html(sim_html, height=600)

st.markdown(f"""
---
### 🧠 System Specifications
* **Road Speed Limit:** Governed at **{speed_limit} MPH**.
* **Acceleration Model:** Uses a 0.05 coefficient for realistic inertia.
* **Oncoming Safety:** All traffic in the opposite lane uses a **Leader-Follower Spacing Algorithm** to maintain a minimum {70}px gap.

<div class="footer">
    Vectra AI built by <strong>Gesner Deslandes</strong> – GlobalInternet.py
</div>
""", unsafe_allow_html=True)
