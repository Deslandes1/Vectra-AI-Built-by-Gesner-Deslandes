import streamlit as st
import base64
from PIL import Image
import io

st.set_page_config(page_title="Vectra AI – Collision-Proof", layout="wide")

# 1. INITIALIZE VARIABLES (Do this first to avoid NameErrors)
speed_limit = 40  # Default value
sim_limit = 2.6   # Default fallback (40 / 15)

# 2. SIDEBAR CONTROLS
with st.sidebar:
    st.header("🚦 System Settings")
    speed_limit = st.select_slider(
        "AI Speed Limit (MPH)", 
        options=[20, 30, 40, 50, 60, 70, 80], 
        value=40
    )
    # Update the limit based on user input
    sim_limit = speed_limit / 15 
    
    st.divider()
    st.header("🗺️ Roadmap")
    uploaded_file = st.file_uploader("Upload roadmap image...", type=["jpg", "png", "jpeg"])

# 3. HEADER UI
st.markdown(f"""
<div style="text-align: center;">
    <h1>🚗 Vectra AI – Zero-Collision Engine</h1>
    <p style="font-size: 1.1rem;">built by <strong>Gesner Deslandes</strong></p>
</div>
""", unsafe_allow_html=True)

# 4. SIMULATION HTML
# We use f""" and then {{ }} for all JavaScript logic
sim_html = f"""
<canvas id="gameCanvas" width="900" height="500" tabindex="0" style="display: block; margin: 0 auto; border: 2px solid #b87c4f; border-radius: 12px;"></canvas>
<div style="text-align: center; font-family: monospace; font-size: 1.2rem; margin-top: 10px; color: white;">
    🧠 AI Status: <span id="status">Active</span> &nbsp;|&nbsp; 
    ⏱️ Speed: <span id="currSpeed">0</span> MPH
</div>

<script>
    (function() {{
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const W = 900, H = 500, CAR_W = 34, CAR_H = 20;
        
        let car = {{ x: 50, y: 0, speed: 0, alive: true }};
        let obstacles = [];
        const SPEED_LIMIT = {sim_limit}; 

        function getRoadCenterY(x) {{
            return H/2 + 30 + Math.sin(x / 90) * 45 + Math.sin(x / 200) * 25;
        }}

        function update() {{
            if (!car.alive) return;

            // Player Movement
            car.speed += (SPEED_LIMIT - car.speed) * 0.05;
            car.x += car.speed;

            // Loop reset with safety check
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

            // Traffic spacing logic
            obstacles.sort((a, b) => a.x - b.x); 
            for (let i = 0; i < obstacles.length; i++) {{
                let o = obstacles[i];
                let tSpeed = -2.5;
                if (i > 0) {{
                    let leader = obstacles[i-1];
                    let gap = o.x - (leader.x + CAR_W);
                    if (gap < 80) {{
                        tSpeed = leader.speed;
                        if (gap < 20) tSpeed = -0.1;
                    }}
                }}
                o.speed = tSpeed;
                o.x += o.speed;
                o.y = getRoadCenterY(o.x) - 18 - (CAR_H/2);
            }}
            obstacles = obstacles.filter(o => o.x > -100);

            // Collision Check
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
            
            // Road
            ctx.beginPath(); ctx.moveTo(-50, getRoadCenterY(-50));
            for (let x = 0; x <= W + 50; x += 10) ctx.lineTo(x, getRoadCenterY(x));
            ctx.lineWidth = 100; ctx.strokeStyle = "#444"; ctx.stroke();

            // Player
            ctx.fillStyle = car.alive ? "#00d4ff" : "#f00";
            ctx.fillRect(car.x, car.y, CAR_W, CAR_H);
            
            // Traffic
            ctx.fillStyle = "#ff4b4b";
            for (let o of obstacles) ctx.fillRect(o.x, o.y, CAR_W, CAR_H);
        }}

        function loop() {{ update(); draw(); requestAnimationFrame(loop); }}
        
        // Simple interval to spawn cars safely
        setInterval(() => {{
            if (obstacles.length < 5) {{
                let entryClear = obstacles.every(o => o.x < W - 100);
                if (entryClear) obstacles.push({{ x: W + 50, y: 0, speed: -2.5 }});
            }}
        }}, 3000);

        loop();
    }})();
</script>
"""

st.components.v1.html(sim_html, height=600)
