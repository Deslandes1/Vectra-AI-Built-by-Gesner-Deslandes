import streamlit as st
import base64
from PIL import Image
import io

st.set_page_config(page_title="Vectra AI – Zero-Collision Engine", layout="wide")

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
    <h1>🚗 Vectra AI – Collision-Proof Simulation</h1>
    <p style="font-size: 1.1rem;">built by <strong>Gesner Deslandes</strong></p>
</div>
""", unsafe_allow_html=True)

# --- Simulation Logic ---
sim_html = f"""
<canvas id="gameCanvas" width="900" height="500" tabindex="0"></canvas>
<div class="info">
    🧠 AI Status: <span id="status">Active</span> &nbsp;|&nbsp; 
    ⏱️ Speed: <span id="currSpeed">0</span> MPH &nbsp;|&nbsp;
    🚗 Traffic Count: <span id="obsActive">0</span>
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
        const SAFE_GAP = 80; // Pixels required between oncoming cars
        
        let car = {{ x: 50, y: 0, speed: 0, alive: true }};
        let obstacles = [];
        const SPEED_LIMIT = {sim_limit}; 

        function getRoadCenterY(x) {{
            return H/2 + 30 + Math.sin(x / 90) * 45 + Math.sin(x / 200) * 25;
        }}

        function update() {{
            if (!car.alive) return;

            // 1. Player Movement (Eastbound)
            car.speed += (SPEED_LIMIT - car.speed) * 0.05;
            car.x += car.speed;
            if (car.x > W + 50) car.x = -50;
            car.y = getRoadCenterY(car.x) + 18 - (CAR_H/2);
            speedSpan.innerText = Math.round(car.speed * 15);

            // 2. Traffic Flow Management (Westbound)
            // Sort by X position so we can evaluate them in order (Westmost car is the leader)
            obstacles.sort((a, b) => a.x - b.x); 

            for (let i = 0; i < obstacles.length; i++) {{
                let o = obstacles[i];
                let targetSpeed = -2.5;

                // Collision Avoidance: Check car ahead in the left lane
                if (i > 0) {{
                    let leader = obstacles[i-1];
                    let gap = o.x - (leader.x + CAR_W);
                    
                    if (gap < SAFE_GAP) {{
                        // Match leader speed to maintain current distance
                        targetSpeed = leader.speed; 
                        // If they get dangerously close, apply brakes
                        if (gap < 20) targetSpeed = -0.1; 
                    }}
                }}

                o.speed = targetSpeed;
                o.x += o.speed;
                o.y = getRoadCenterY(o.x) - 18 - (CAR_H/2);
            }}

            // Cleanup & UI
            obstacles = obstacles.filter(o => o.x > -100);
            obsSpan.innerText = obstacles.length;

            // 3. Global Collision Check (Player vs Traffic)
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

            // Blue Player Car
            ctx.fillStyle = car.alive ? "#00d4ff" : "#f00";
            ctx.fillRect(car.x, car.y, CAR_W, CAR_H);
            
            // Red Oncoming Traffic
            ctx.fillStyle = "#ff4b4b";
            for (let o of obstacles) ctx.fillRect(o.x, o.y, CAR_W, CAR_H);
        }}

        function loop() {{ update(); draw(); requestAnimationFrame(loop); }}

        document.getElementById('spawnBtn').onclick = () => {{
            // PREVENT OVERLAP: Only spawn if the 'entrance' is clear
            let entryBlocked = obstacles.some(o => o.x > W - 60);
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
### 🧠 Logic Overview
* **Virtual Lead-Follow:** Each oncoming car constantly pings the car ahead. If the gap drops below **80px**, the follower synchronizes its speed to the leader instantly.
* **Spawn Sentinel:** The spawn button checks a 60px "safety zone" at the edge of the road. If another car is currently entering, the request is ignored to prevent overlapping.
* **Lane Anchoring:** All vehicles use `getRoadCenterY(x)` with fixed offsets (+18 for you, -18 for them), ensuring no car ever leaves its designated lane.

<div class="footer">
    Vectra AI built by <strong>Gesner Deslandes</strong> – GlobalInternet.py
</div>
""", unsafe_allow_html=True)
