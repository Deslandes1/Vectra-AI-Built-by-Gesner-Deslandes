import streamlit as st

st.set_page_config(page_title="Vectra AI – True Heading", layout="wide")

# --- 1. SIDEBAR ---
with st.sidebar:
    st.header("🚦 Traffic Control")
    speed_limit = st.select_slider("AI Speed Limit (MPH)", options=[20, 30, 40, 50, 60, 70, 80], value=50)
    sim_limit = speed_limit / 15 
    st.divider()
    st.header("🗺️ Project Roadmap")
    roadmap_url = "https://raw.githubusercontent.com/Deslandes1/Vectra-AI-Built-by-Gesner-Deslandes/main/Gemini_Generated_Image_mcrtf8mcrtf8mcrt.png"
    st.image(roadmap_url, caption="Vectra AI Development Phases", use_container_width=True)
    uploaded_file = st.file_uploader("Update Roadmap", type=["jpg", "png", "jpeg"])

# --- 2. HEADER & VIDEO ---
st.markdown(f"""
<div style="text-align: center;">
    <h1>🚗 Vectra AI – Heading & Rotation Logic</h1>
    <p style="font-size: 1.1rem;">built by <strong>Gesner Deslandes</strong></p>
</div>
""", unsafe_allow_html=True)

st.video("https://raw.githubusercontent.com/Deslandes1/Vectra-AI-Built-by-Gesner-Deslandes/main/AI%20Selfdriving.mp4")

# --- 3. SIMULATION ENGINE ---
sim_html = f"""
<canvas id="gameCanvas" width="900" height="500" style="display: block; margin: 0 auto; border: 2px solid #b87c4f; border-radius: 12px;"></canvas>
<div style="text-align: center; margin-top: 15px;">
    <button id="spawnBtn" style="background: #b87c4f; color: white; padding: 12px 24px; border-radius: 8px; border: none; font-weight: bold; cursor: pointer;">🎲 Add Oncoming Car</button>
</div>
<div style="text-align: center; font-family: monospace; font-size: 1.2rem; margin-top: 10px; color: #000; font-weight: bold;">
    🧠 Target: {speed_limit} MPH &nbsp;|&nbsp; ⏱️ Real-time: <span id="currSpeedDisplay">0</span> MPH
</div>

<script>
    (function() {{
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const W = 900, H = 500, CAR_W = 34, CAR_H = 20;
        const TARGET_VELOCITY = {sim_limit};
        const LANE_OFFSET = 28; 
        
        let car = {{ x: 50, y: 0, speed: 0, angle: 0 }};
        let obstacles = [];

        function getRoadCenterY(x) {{
            return H/2 + 30 + Math.sin(x / 90) * 45 + Math.sin(x / 200) * 25;
        }}

        // MATH: Get the angle of the road at any X coordinate
        function getRoadAngle(x, direction = 1) {{
            const lookAhead = 2; // Check 2 pixels ahead
            const y1 = getRoadCenterY(x);
            const y2 = getRoadCenterY(x + (lookAhead * direction));
            return Math.atan2(y2 - y1, lookAhead * direction);
        }}

        document.getElementById('spawnBtn').onclick = () => {{
            if (obstacles.every(o => o.x < W - 70)) {{
                obstacles.push({{ x: W + 50, y: 0, speed: -2.5, angle: 0 }});
            }}
        }};

        function update() {{
            // 1. Blue Car Logic
            car.speed += (TARGET_VELOCITY - car.speed) * 0.05;
            car.x += car.speed;
            car.y = getRoadCenterY(car.x) + LANE_OFFSET;
            car.angle = getRoadAngle(car.x, 1);

            if (car.x > W + 50) {{
                if (obstacles.every(o => o.x > 150 || o.x < -20)) car.x = -50;
                else car.x = W + 49;
            }}
            document.getElementById('currSpeedDisplay').innerText = Math.round(car.speed * 15);

            // 2. Red Car Logic
            obstacles.forEach(o => {{
                o.x -= 2.5;
                o.y = getRoadCenterY(o.x) - LANE_OFFSET;
                o.angle = getRoadAngle(o.x, -1);
            }});
            obstacles = obstacles.filter(o => o.x > -100);
        }}

        function drawCar(x, y, angle, color) {{
            ctx.save();
            ctx.translate(x, y);
            ctx.rotate(angle);
            ctx.fillStyle = color;
            // Draw relative to center so rotation looks natural
            ctx.fillRect(-CAR_W/2, -CAR_H/2, CAR_W, CAR_H);
            ctx.restore();
        }}

        function draw() {{
            ctx.fillStyle = "#0e1117";
            ctx.fillRect(0, 0, W, H);
            
            // Draw Road & Yellow Line
            ctx.beginPath(); ctx.moveTo(-50, getRoadCenterY(-50));
            for (let x = -50; x <= W + 50; x += 5) ctx.lineTo(x, getRoadCenterY(x));
            ctx.lineWidth = 120; ctx.strokeStyle = "#444"; ctx.stroke();

            ctx.beginPath(); ctx.setLineDash([15, 15]);
            for (let x = -50; x <= W + 50; x += 5) ctx.lineTo(x, getRoadCenterY(x));
            ctx.lineWidth = 4; ctx.strokeStyle = "#ffd700"; ctx.stroke(); ctx.setLineDash([]);

            // Draw Blue Car & Red Traffic with specific rotation
            drawCar(car.x, car.y, car.angle, "#00d4ff");
            obstacles.forEach(o => drawCar(o.x, o.y, o.angle, "#ff4b4b"));
        }}

        function loop() {{ update(); draw(); requestAnimationFrame(loop); }}
        loop();
    }})();
</script>
"""

st.components.v1.html(sim_html, height=650)
