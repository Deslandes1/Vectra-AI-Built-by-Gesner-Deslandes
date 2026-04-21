import streamlit as st
import base64
from PIL import Image
import io

st.set_page_config(page_title="Vectra AI – Safe Traffic Flow", layout="wide")

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
    
    speed_limit = st.select_slider(
        "Set Road Speed Limit (MPH)",
        options=[20, 30, 40, 50, 60, 70, 80],
        value=40
    )
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

st.markdown("""
<div style="text-align: center;">
    <h1>🚗 Vectra AI – Intelligent Traffic</h1>
    <p style="font-size: 1.1rem;">built by <strong>Gesner Deslandes</strong></p>
    <p>Oncoming cars now maintain safe distances and never collide with each other.</p>
</div>
""", unsafe_allow_html=True)

# --- Video Section ---
video_url = "https://raw.githubusercontent.com/Deslandes1/Vectra-AI-Built-by-Gesner-Deslandes/main/AI%20Selfdriving.mp4"
st.video(video_url)

# --- Simulation Logic ---
sim_html = f"""
<canvas id="gameCanvas" width="900" height="500" tabindex="0"></canvas>
<div class="info">
    🧠 AI Status: <span id="status">Active</span> &nbsp;|&nbsp; 
    ⏱️ Your Speed: <span id="currSpeed">0</span> MPH &nbsp;|&nbsp;
    🚗 Oncoming: <span id="obsActive">0</span>
</div>
<div style="text-align: center; margin-top: 10px;">
    <button id="resetBtn">🔄 Reset Drive</button>
    <button id="spawnBtn">🎲 Spawn Oncoming Car</button>
</div>

<script>
    (function() {{
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const statusSpan = document.getElementById('status');
        const speedSpan = document.getElementById('currSpeed');
        const obsSpan = document.getElementById('obsActive');

        const W = 900, H = 500;
        const CAR_W = 34, CAR_H = 20;
        const SAFE_DISTANCE = 50; // Minimum pixels between oncoming cars
        
        let car = {{ x: 50, y: 0, speed: 0, alive: true }};
        let obstacles = [];
        const SPEED_LIMIT = {sim_limit}; 
        const ACCEL = 0.05; 

        function getRoadCenterY(x) {{
            return H/2 + 30 + Math.sin(x / 90) * 45 + Math.sin(x / 200) * 25;
        }}

        function update() {{
            if (!car.alive) return;

            // 1. Player Speed Logic
            car.speed += (SPEED_LIMIT - car.speed) * ACCEL;
            car.x += car.speed;
            if (car.x > W + 50) car.x = -50;
            car.y = getRoadCenterY(car.x) + 18 - (CAR_H/2);
            speedSpan.innerText = Math.round(car.speed * 15);

            // 2. Intelligent Oncoming Traffic Logic
            // Sort obstacles by X so we know who is "ahead" in the left lane (smaller X is ahead)
            obstacles.sort((a, b) => a.x - b.x);

            for (let i = 0; i < obstacles.length; i++) {{
                let o = obstacles[i];
                let targetSpeed = -2.5; // Base speed for oncoming

                // Check car in front (the one with the smaller X since they drive West)
                if (i > 0) {{
                    let leader = obstacles[i-1];
                    let distance = o.x - (leader.x + CAR_W);
                    
                    if (distance < SAFE_DISTANCE) {{
                        // Match leader speed and maintain gap
                        targetSpeed = leader.speed;
                        if (distance < 10) targetSpeed = -0.1; // Emergency brake
                    }}
                }}

                o.speed = targetSpeed;
                o.x += o.speed;
                o.y = getRoadCenterY(o.x) - 18 - (CAR_H/2);
            }}

            // Remove off-screen
            obstacles = obstacles.filter(o => o.x > -100);
            obsSpan.innerText = obstacles.length;

            // 3. Collision Check (Player vs Obstacles)
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
            ctx.beginPath(); ctx.setLineDash([15, 15]);
            for (let x = 0; x <= W; x += 5) ctx.lineTo(x, getRoadCenterY(x));
            ctx.lineWidth = 3; ctx.strokeStyle = "#ffd700"; ctx.stroke();
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

        document.getElementById('spawnBtn').onclick = () => {{
            // Only spawn if the entry point is clear to prevent initial overlap
            let entryClear = obstacles.every(o => o.x < W - 50);
            if (entryClear) obstacles.push({{ x: W + 50, y: 0, speed: -2.5 }});
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
### 🧠 Traffic Intelligence (V2)
The oncoming fleet is now governed by a **Distance-Keeping Algorithm**:
* **Collision Prevention:** Each car monitors the `x` coordinate of the vehicle in front of it.
* **Speed Matching:** If an oncoming car detects a "leader" within **50 pixels**, it automatically matches that leader's speed to maintain a constant gap.
* **Safety Buffer:** Spawning is blocked if the entry point is currently occupied, ensuring no "teleportation" crashes.

<div class="footer">
    Vectra AI built by <strong>Gesner Deslandes</strong> – GlobalInternet.py
</div>
""", unsafe_allow_html=True)
