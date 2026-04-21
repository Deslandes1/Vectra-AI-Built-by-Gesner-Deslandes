import streamlit as st
import base64
from PIL import Image
import io

st.set_page_config(page_title="Vectra AI – Crash-Proof Edition", layout="wide")

# --- 1. INITIALIZATION ---
# Placing these first ensures sim_limit exists before the simulation loads.
speed_limit = 40  
sim_limit = 2.6   

# --- 2. SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("🚦 System Settings")
    speed_limit = st.select_slider("AI Speed Limit (MPH)", options=[20, 30, 40, 50, 60, 70, 80], value=40)
    sim_limit = speed_limit / 15 
    
    st.divider()
    st.header("🗺️ Roadmap")
    uploaded_file = st.file_uploader("Upload roadmap image...", type=["jpg", "png", "jpeg"])

# --- 3. UI HEADER & VIDEO ---
st.markdown(f"""
<div style="text-align: center;">
    <h1>🚗 Vectra AI – Collision-Proof Engine</h1>
    <p style="font-size: 1.1rem;">built by <strong>Gesner Deslandes</strong></p>
</div>
""", unsafe_allow_html=True)

st.video("https://raw.githubusercontent.com/Deslandes1/Vectra-AI-Built-by-Gesner-Deslandes/main/AI%20Selfdriving.mp4")

# --- 4. SIMULATION ENGINE ---
# We use f-string with {{ }} to protect JS brackets from Python's parser.
sim_html = f"""
<canvas id="gameCanvas" width="900" height="500" tabindex="0" style="display: block; margin: 0 auto; border: 2px solid #b87c4f; border-radius: 12px;"></canvas>
<div style="text-align: center; font-family: monospace; font-size: 1.2rem; margin-top: 10px; color: white;">
    🧠 AI Status: <span id="status">Active</span> &nbsp;|&nbsp; 
    ⏱️ Speed: <span id="currSpeed">0</span> MPH &nbsp;|&nbsp;
    🚗 Traffic: <span id="obsActive">0</span>
</div>
<div style="text-align: center; margin-top: 10px;">
    <button id="resetBtn" style="background: #b87c4f; color: white; padding: 8px 16px; border-radius: 8px; border: none; cursor: pointer; margin-right: 10px;">🔄 Hard Reset</button>
    <button id="spawnBtn" style="background: #b87c4f; color: white; padding: 8px 16px; border-radius: 8px; border: none; cursor: pointer;">🎲 Add Traffic Car</button>
</div>

<script>
    (function() {{
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
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

            // --- PLAYER PHYSICS ---
            car.speed += (SPEED_LIMIT - car.speed) * 0.05;
            car.x += car.speed;

            // FIX: THE RIGHT SIDE RESET GATEKEEPER
            // Instead of instantly resetting, we check if the left entrance is clear.
            if (car.x > W + 40) {{
                let startZoneClear = obstacles.every(o => o.x > 150 || o.x < -20);
                if (startZoneClear) {{
                    car.x = -50; 
                }} else {{
                    // Hold car 'out of bounds' until it is safe to reappear
                    car.x = W + 39; 
                }}
            }}
            
            car.y = getRoadCenterY(car.x) + 18 - (CAR_H/2);
            document.getElementById('currSpeed').innerText = Math.round(car.speed * 15);

            // --- TRAFFIC COORDINATION (Left Lane) ---
            obstacles.sort((a, b) => a.x - b.x); 
            for (let i = 0; i < obstacles.length; i++) {{
                let o = obstacles[i];
                let targetVel = -2.5;

                if (i > 0) {{
                    let leader = obstacles[i-1];
                    let gap = o.x - (leader.x + CAR_W);
                    // Match leader speed if too close
                    if (gap < SAFE_GAP) {{
                        targetVel = leader.speed;
                        if (gap < 25) targetVel = -0.1; 
                    }}
                }}
                o.speed = targetVel;
                o.x += o.speed;
                o.y = getRoadCenterY(o.x) - 18 - (CAR_H/2);
            }}

            obstacles = obstacles.filter(o => o.x > -100);
            document.getElementById('obsActive').innerText = obstacles.length;

            // --- COLLISION SENSOR (With Boundary Protection) ---
            // Only check collisions if car is actually on the visible road
            if (car.x > -40 && car.x < W + 20) {{
                for (let o of obstacles) {{
                    if (car.x < o.x + CAR_W && car.x + CAR_W > o.x && 
                        car.y < o.y + CAR_H && car.y + CAR_H > o.y) {{
                        car.alive = false;
                        document.getElementById('status').innerText = "CRASHED";
                    }}
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

            // Center Dash
            ctx.beginPath(); ctx.setLineDash([15, 15]);
            for (let x = 0; x <= W; x += 5) ctx.lineTo(x, getRoadCenterY(x));
            ctx.lineWidth = 3; ctx.strokeStyle = "#ffd700"; ctx.stroke(); ctx.setLineDash([]);

            // Car / Traffic
            ctx.fillStyle = car.alive ? "#00d4ff" : "#f00";
            ctx.fillRect(car.x, car.y, CAR_W, CAR_H);
            ctx.fillStyle = "#ff4b4b";
            for (let o of obstacles) ctx.fillRect(o.x, o.y, CAR_W, CAR_H);
        }}

        function loop() {{ update(); draw(); requestAnimationFrame(loop); }}

        document.getElementById('spawnBtn').onclick = () => {{
            // SENTINEL: Do not spawn if another car is already in the entry zone
            if (obstacles.every(o => o.x < W - 70)) {{
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

st.markdown(f"""
---
### 🛠️ Final Boundary Fixes
* **The "Holding Zone":** Your car no longer teleports blindly. If an oncoming car is occupying the reset zone (at $x=-50$), your car will wait at $x=939$ (just off-screen) until the lane is clear.
* **Collision Muting:** Collision detection is now wrapped in a boundary check. It only activates when your car is within the safe coordinates of the road $(-40 < x < 920)$, preventing "edge-glitch" crashes.
* **Predictive Spacing:** Oncoming traffic now uses a **Leader-Follower algorithm** to ensure that even if you spam the "Add Traffic" button, the cars maintain a perfect 85px safety gap.

<div style="text-align: center; margin-top: 20px; color: #888; font-size: 0.8rem;">
    Vectra AI built by <strong>Gesner Deslandes</strong> – GlobalInternet.py
</div>
""", unsafe_allow_html=True)
