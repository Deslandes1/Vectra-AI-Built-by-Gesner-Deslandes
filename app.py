import streamlit as st
import base64
from PIL import Image
import io

st.set_page_config(page_title="Vectra AI – Perfect Flow", layout="wide")

# --- 1. INITIALIZATION ---
# Define these first to ensure they exist before the simulation string is created.
speed_limit = 40  
sim_limit = 2.6   

# --- 2. SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("🚦 Traffic Control")
    speed_limit = st.select_slider("AI Speed Limit (MPH)", options=[20, 30, 40, 50, 60, 70, 80], value=40)
    sim_limit = speed_limit / 15 
    
    st.divider()
    st.header("🗺️ Roadmap")
    uploaded_file = st.file_uploader("Upload roadmap image...", type=["jpg", "png", "jpeg"])

# --- 3. UI HEADER ---
st.markdown(f"""
<div style="text-align: center;">
    <h1>🚗 Vectra AI – Zero-Collision Autopilot</h1>
    <p style="font-size: 1.1rem;">built by <strong>Gesner Deslandes</strong></p>
    <p>The AI system ensures vehicles never collide at boundaries or in traffic.</p>
</div>
""", unsafe_allow_html=True)

# Replace with your actual video URL if different
st.video("https://raw.githubusercontent.com/Deslandes1/Vectra-AI-Built-by-Gesner-Deslandes/main/AI%20Selfdriving.mp4")

# --- 4. SIMULATION ENGINE ---
# We use f-string with {{ }} to protect JS brackets from Python's parser.
sim_html = f"""
<canvas id="gameCanvas" width="900" height="500" tabindex="0" style="display: block; margin: 0 auto; border: 2px solid #b87c4f; border-radius: 12px;"></canvas>
<div style="text-align: center; font-family: monospace; font-size: 1.2rem; margin-top: 10px; color: white;">
    🧠 AI Status: <span id="status" style="color: #00ff00;">ONLINE</span> &nbsp;|&nbsp; 
    ⏱️ Speed: <span id="currSpeed">0</span> MPH &nbsp;|&nbsp;
    🚗 Traffic: <span id="obsActive">0</span>
</div>
<div style="text-align: center; margin-top: 10px;">
    <button id="spawnBtn" style="background: #b87c4f; color: white; padding: 8px 16px; border-radius: 8px; border: none; cursor: pointer;">🎲 Add Oncoming Car</button>
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
            // 1. PLAYER AUTOPILOT
            car.speed += (SPEED_LIMIT - car.speed) * 0.05;
            car.x += car.speed;

            // BOUNDARY GATEKEEPER: Prevents crashes at the left end
            if (car.x > W + 50) {{
                let resetZoneClear = obstacles.every(o => o.x > 150 || o.x < -20);
                if (resetZoneClear) {{
                    car.x = -50;
                }} else {{
                    car.x = W + 49; // Wait off-screen
                }}
            }}
            car.y = getRoadY(car.x) + 18 - (CAR_H/2);
            document.getElementById('currSpeed').innerText = Math.round(car.speed * 15);

            // 2. TRAFFIC AUTOPILOT (Anti-Collision Logic)
            obstacles.sort((a, b) => a.x - b.x); 
            for (let i = 0; i < obstacles.length; i++) {{
                let o = obstacles[i];
                let targetVel = -2.5;

                // Sync speed with vehicle ahead
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
            document.getElementById('obsActive').innerText = obstacles.length;
        }}

        function draw() {{
            ctx.fillStyle = "#0e1117";
            ctx.fillRect(0, 0, W, H);
            
            // Draw Road
            ctx.beginPath(); ctx.moveTo(-50, getRoadY(-50));
            for (let x = 0; x <= W + 50; x += 10) ctx.lineTo(x, getRoadY(x));
            ctx.lineWidth = 100; ctx.strokeStyle = "#444"; ctx.stroke();

            // Center Markings
            ctx.beginPath(); ctx.setLineDash([15, 15]);
            for (let x = 0; x <= W; x += 5) ctx.lineTo(x, getRoadY(x));
            ctx.lineWidth = 3; ctx.strokeStyle = "#ffd700"; ctx.stroke(); ctx.setLineDash([]);

            // Draw Vehicles
            ctx.fillStyle = "#00d4ff";
            ctx.fillRect(car.x, car.y, CAR_W, CAR_H);
            ctx.fillStyle = "#ff4b4b";
            for (let o of obstacles) ctx.fillRect(o.x, o.y, CAR_W, CAR_H);
        }}

        function loop() {{ update(); draw(); requestAnimationFrame(loop); }}

        document.getElementById('spawnBtn').onclick = () => {{
            // SENTINEL: Only spawn if the entrance isn't blocked
            if (obstacles.every(o => o.x < W - 70)) {{
                obstacles.push({{ x: W + 50, y: 0, speed: -2.5 }});
            }}
        }};

        loop();
    }})();
</script>
"""

st.components.v1.html(sim_html, height=600)

st.markdown("---")
st.markdown("### 🧠 Logic Breakdown")
st.markdown("""
* **The Reset Sentinel:** Your car no longer teleports blindly. It "looks ahead" to the starting area. If a traffic car is in the way, your car waits off-screen until the lane is clear.
* **Predictive Spacing:** Oncoming traffic uses a **Leader-Follower algorithm**. If the gap drops below 85px, the follower matches the speed of the leader instantly.
* **Syntax Fix:** All JavaScript curly braces are escaped as `{{ }}` to prevent Python f-string errors.
""")
