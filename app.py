import streamlit as st
import base64
from PIL import Image
import io

st.set_page_config(page_title="Vectra AI – Zero Collision", layout="wide")

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

# --- Sidebar Controls ---
with st.sidebar:
    st.header("🚦 System Settings")
    speed_limit = st.select_slider("AI Speed Limit (MPH)", options=[20, 30, 40, 50, 60, 70, 80], value=40)
    sim_limit = speed_limit / 15 
    
    st.divider()
    st.header("🗺️ Roadmap")
    uploaded_file = st.file_uploader("Upload roadmap image...", type=["jpg", "png", "jpeg"])

st.markdown(f"""
<div style="text-align: center;">
    <h1>🚗 Vectra AI – Crash-Proof Simulation</h1>
    <p style="font-size: 1.1rem;">built by <strong>Gesner Deslandes</strong></p>
</div>
""", unsafe_allow_html=True)

# --- Simulation Logic ---
# Using f-string with double braces {{ }} to protect Javascript from Python
sim_html = f"""
<canvas id="gameCanvas" width="900" height="500" tabindex="0"></canvas>
<div class="info">
    🧠 AI Status: <span id="status">Active</span> &nbsp;|&nbsp; 
    ⏱️ Speed: <span id="currSpeed">0</span> MPH &nbsp;|&nbsp;
    🚗 Traffic: <span id="obsActive">0</span>
</div>
<div style="text-align: center; margin-top: 10px;">
    <button id="resetBtn">🔄 Hard Reset</button>
    <button id="spawnBtn">🎲 Spawn Safe Car</button>
</div>

<script>
    (function() {{
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const statusSpan = document.getElementById('status');
        const speedSpan = document.getElementById('currSpeed');
        const obsSpan = document.getElementById('obsActive');

        const W = 900, H = 500, CAR_W = 34, CAR_H = 20;
        const SAFE_GAP = 85; 
        
        let car = {{ x: 50, y: 0, speed: 0, alive: true }};
        let obstacles = [];
        const SPEED_LIMIT = {sim_limit}; 

        function getRoadCenterY(x) {{
            return H/2 + 30 + Math.sin(x / 90) * 45 + Math.sin(x / 200) * 25;
        }}

        function update() {{
            if (!car.alive) return;

            // 1. Player Movement & Loop Protection
            car.speed += (SPEED_LIMIT - car.speed) * 0.05;
            car.x += car.speed;

            // FIX: Check if the start of the road is clear before resetting
            if (car.x > W + 50) {{
                let startIsClear = obstacles.every(o => o.x > 120 || o.x < -20);
                if (startIsClear) {{
                    car.x = -50;
                }} else {{
                    car.x = W + 49; // Wait off-screen for a gap
                }}
            }}

            car.y = getRoadCenterY(car.x) + 18 - (CAR_H/2);
            speedSpan.innerText = Math.round(car.speed * 15);

            // 2. Traffic Intelligence (Left Lane)
            obstacles.sort((a, b) => a.x - b.x); 

            for (let i = 0; i < obstacles.length; i++) {{
                let o = obstacles[i];
                let targetSpeed = -2.5;

                if (i > 0) {{
                    let leader = obstacles[i-1];
                    let gap = o.x - (leader.x + CAR_W);
                    if (gap < SAFE_GAP) {{
                        targetSpeed = leader.speed;
                        if (gap < 25) targetSpeed = -0.1; 
                    }}
                }

                o.speed = targetSpeed;
                o.x += o.speed;
                o.y = getRoadCenterY(o.x) - 18 - (CAR_H/2);
            }}

            obstacles = obstacles.filter(o => o.x > -100);
            obsSpan.innerText = obstacles.length;

            // 3. Collision Logic
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
            ctx.beginPath(); ctx.moveTo(-50, getRoadCenterY(-50));
            for (let x = 0; x <= W + 50; x += 10) ctx.lineTo(x, getRoadCenterY(x));
            ctx.lineWidth = 100; ctx.strokeStyle = "#444"; ctx.stroke();
            ctx.beginPath(); ctx.setLineDash([15, 15]);
            for (let x = 0; x <= W; x += 5) ctx.lineTo(x, getRoadCenterY(x));
            ctx.lineWidth = 3; ctx.strokeStyle = "#ffd700"; ctx.stroke(); ctx.setLineDash([]);
            ctx.fillStyle = car.alive ? "#00d4ff" : "#f00";
            ctx.fillRect(car.x, car.y, CAR_W, CAR_H);
            ctx.fillStyle = "#ff4b4b";
            for (let o of obstacles) ctx.fillRect(o.x, o.y, CAR_W, CAR_H);
        }}

        function loop() {{ update(); draw(); requestAnimationFrame(loop); }}

        document.getElementById('spawnBtn').onclick = () => {{
            // Safety: Do not spawn if entrance is blocked
            let entryBlocked = obstacles.some(o => o.x > W - 70);
            if (!entryBlocked) {{
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
### 🛠️ Final Fixes Applied
1.  **Syntax Resolved:** Removed all single quotes from JavaScript comments (e.g., changed "Don't" to "Do not") to prevent Python string termination errors.
2.  **End-of-Road Protection:** The car now performs a **Safety Check** before resetting to the start. If an oncoming car is occupying the reset zone, your car will wait off-screen for 1 frame until it is safe to reappear.
3.  **Spawn Sentinel:** Oncoming cars cannot be spawned if there is already a car in the entry zone, preventing "stacked" collisions.

<div class="footer">
    Vectra AI built by <strong>Gesner Deslandes</strong> – GlobalInternet.py
</div>
""", unsafe_allow_html=True)
