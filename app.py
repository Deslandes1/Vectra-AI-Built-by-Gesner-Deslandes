import streamlit as st
import base64
from PIL import Image
import io

st.set_page_config(page_title="Vectra AI – Speed Limit Control", layout="wide")

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
    
    # 1. Speed Limit Selection
    speed_limit = st.select_slider(
        "Set Road Speed Limit (MPH)",
        options=[20, 30, 40, 50, 60, 70, 80],
        value=40
    )
    # Convert MPH to simulation pixels-per-frame (approximate scaling)
    sim_limit = speed_limit / 15 
    
    st.divider()
    
    # 2. Roadmap Upload
    st.header("🗺️ Roadmap Integration")
    uploaded_file = st.file_uploader("Upload top-down roadmap...", type=["jpg", "png", "jpeg"])
    
    roadmap_b64 = ""
    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        roadmap_b64 = base64.b64encode(buffered.getvalue()).decode()
        st.success("Roadmap Loaded")

st.markdown("""
<div style="text-align: center;">
    <h1>🚗 Vectra AI – Speed Governance</h1>
    <p style="font-size: 1.1rem;">built by <strong>Gesner Deslandes</strong></p>
</div>
""", unsafe_allow_html=True)

# --- Video Section ---
video_url = "https://raw.githubusercontent.com/Deslandes1/Vectra-AI-Built-by-Gesner-Deslandes/main/AI%20Selfdriving.mp4"
st.video(video_url)

# --- Simulation Logic ---
# We pass the 'sim_limit' directly into the JS via f-string
sim_html = f"""
<canvas id="gameCanvas" width="900" height="500" tabindex="0"></canvas>
<div class="info">
    🧠 AI Status: <span id="status">Active</span> &nbsp;|&nbsp; 
    ⏱️ Current Speed: <span id="currSpeed">0</span> MPH &nbsp;|&nbsp;
    🛑 Limit: {speed_limit} MPH
</div>
<div style="text-align: center; margin-top: 10px;">
    <button id="resetBtn">🔄 Reset Drive</button>
    <button id="spawnBtn">🎲 Spawn Oncoming</button>
</div>

<script>
    (function() {{
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const statusSpan = document.getElementById('status');
        const speedSpan = document.getElementById('currSpeed');

        const W = 900, H = 500;
        const CAR_W = 34, CAR_H = 20;
        
        // Physics variables
        let car = {{ x: 50, y: 0, speed: 0, alive: true }};
        let obstacles = [];
        const SPEED_LIMIT = {sim_limit}; 
        const ACCEL = 0.05; // The friction/acceleration coefficient

        function getRoadCenterY(x) {{
            return H/2 + 30 + Math.sin(x / 90) * 45 + Math.sin(x / 200) * 25;
        }}

        function update() {{
            if (!car.alive) return;

            // Apply Speed Logic: Smoothly accelerate toward the limit
            if (car.speed < SPEED_LIMIT) {{
                car.speed += (SPEED_LIMIT - car.speed) * ACCEL;
            }} else if (car.speed > SPEED_LIMIT) {{
                car.speed -= (car.speed - SPEED_LIMIT) * ACCEL;
            }}

            car.x += car.speed;
            if (car.x > W + 50) car.x = -50;
            car.y = getRoadCenterY(car.x) + 18 - (CAR_H/2);

            // Update UI Speed Display
            speedSpan.innerText = Math.round(car.speed * 15);

            // Oncoming traffic
            for (let i = obstacles.length - 1; i >= 0; i--) {{
                obstacles[i].x -= 2.5;
                obstacles[i].y = getRoadCenterY(obstacles[i].x) - 18 - (CAR_H/2);
                if (obstacles[i].x < -100) obstacles.splice(i, 1);
            }}

            // Collision check
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
            ctx.beginPath();
            ctx.moveTo(-50, getRoadCenterY(-50));
            for (let x = 0; x <= W + 50; x += 10) ctx.lineTo(x, getRoadCenterY(x));
            ctx.lineWidth = 100;
            ctx.strokeStyle = "#444";
            ctx.stroke();

            // Center Line
            ctx.beginPath();
            ctx.setLineDash([15, 15]);
            for (let x = 0; x <= W; x += 5) ctx.lineTo(x, getRoadCenterY(x));
            ctx.lineWidth = 3;
            ctx.strokeStyle = "#ffd700";
            ctx.stroke();
            ctx.setLineDash([]);

            // Draw Car
            ctx.fillStyle = car.alive ? "#00d4ff" : "#f00";
            ctx.fillRect(car.x, car.y, CAR_W, CAR_H);
            
            // Draw Oncoming
            ctx.fillStyle = "#ff4b4b";
            for (let o of obstacles) ctx.fillRect(o.x, o.y, CAR_W, CAR_H);
        }}

        function loop() {{
            update();
            draw();
            requestAnimationFrame(loop);
        }}

        document.getElementById('spawnBtn').onclick = () => obstacles.push({{ x: W + 50, y: 0 }});
        document.getElementById('resetBtn').onclick = () => {{ 
            car.x = 50; car.speed = 0; car.alive = true; obstacles = []; 
            statusSpan.innerText = "Active";
        }};

        loop();
    }})();
</script>
"""

st.components.v1.html(sim_html, height=600)

# --- Speed and Friction Description ---
st.markdown(f"""
---
### 🧠 Speed Governance System
The AI is currently governed by a **{speed_limit} MPH** limit. 

Unlike basic simulations that jump instantly between velocities, this AI uses a differential equation to calculate acceleration:
* **Friction/Accel Coefficient:** `0.05`
* **Behavior:** When you increase the limit via the sidebar, the car physically leans into the acceleration, mimicking real-world inertia.

<div class="footer">
    Vectra AI built by <strong>Gesner Deslandes</strong> – GlobalInternet.py
</div>
""", unsafe_allow_html=True)
