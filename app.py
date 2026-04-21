import streamlit as st

st.set_page_config(page_title="Vectra AI – Perfect Flow", layout="wide")

# --- 1. SIDEBAR: SPEED, ROADMAP, & UPLOAD ---
with st.sidebar:
    st.header("🚦 Traffic Control")
    # This slider now controls the physics engine directly
    speed_limit = st.select_slider(
        "AI Speed Limit (MPH)", 
        options=[20, 30, 40, 50, 60, 70, 80], 
        value=40
    )
    # Math: Convert MPH to "pixels per frame" for the JS engine
    sim_limit = speed_limit / 15 
    
    st.divider()
    st.header("🗺️ Project Roadmap")
    roadmap_url = "https://raw.githubusercontent.com/Deslandes1/Vectra-AI-Built-by-Gesner-Deslandes/main/Gemini_Generated_Image_mcrtf8mcrtf8mcrt.png"
    st.image(roadmap_url, caption="Vectra AI Development Phases", use_container_width=True)
    
    st.subheader("Update Roadmap")
    uploaded_file = st.file_uploader("Upload new roadmap image...", type=["jpg", "png", "jpeg"])

# --- 2. UI HEADER & ORIGINAL VIDEO ---
st.markdown(f"""
<div style="text-align: center;">
    <h1>🚗 Vectra AI – Zero-Clipping Lane Logic</h1>
    <p style="font-size: 1.1rem;">built by <strong>Gesner Deslandes</strong></p>
</div>
""", unsafe_allow_html=True)

# Keeping your original video
st.video("https://raw.githubusercontent.com/Deslandes1/Vectra-AI-Built-by-Gesner-Deslandes/main/AI%20Selfdriving.mp4")

# --- 3. SIMULATION ENGINE ---
sim_html = f"""
<canvas id="gameCanvas" width="900" height="500" style="display: block; margin: 0 auto; border: 2px solid #b87c4f; border-radius: 12px;"></canvas>
<div style="text-align: center; margin-top: 15px;">
    <button id="spawnBtn" style="background: #b87c4f; color: white; padding: 12px 24px; border-radius: 8px; border: none; font-weight: bold; cursor: pointer;">
        🎲 Add Oncoming Car
    </button>
</div>
<div style="text-align: center; font-family: monospace; font-size: 1.2rem; margin-top: 10px; color: white;">
    🧠 Target: <span style="color: #00ff00;">{speed_limit} MPH</span> &nbsp;|&nbsp; 
    ⏱️ Real-time: <span id="currSpeedDisplay">0</span> MPH
</div>

<script>
    (function() {{
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const W = 900, H = 500, CAR_W = 34, CAR_H = 20;
        
        // --- PHYSICS LINK ---
        const TARGET_VELOCITY = {sim_limit}; 
        const LANE_OFFSET = 28; // Prevents yellow line clipping
        
        let car = {{ x: 50, y: 0, speed: 0 }};
        let obstacles = [];

        function getRoadCenterY(x) {{
            return H/2 + 30 + Math.sin(x / 90) * 45 + Math.sin(x / 200) * 25;
        }}

        document.getElementById('spawnBtn').onclick = () => {{
            if (obstacles.every(o => o.x < W - 70)) {{
                obstacles.push({{ x: W + 50, y: 0, speed: -2.5 }});
            }}
        }};

        function update() {{
            // 1. DYNAMIC SPEED (Blue Car)
            // car.speed gradually moves toward TARGET_VELOCITY for smooth acceleration
            let speedDiff = TARGET_VELOCITY - car.speed;
            car.speed += speedDiff * 0.05; 
            car.x += car.speed;
            
            // Lock to Right Lane
            car.y = getRoadCenterY(car.x) + LANE_OFFSET - (CAR_H/2);

            if (car.x > W + 50) {{
                let resetClear = obstacles.every(o => o.x > 150 || o.x < -20);
                if (resetClear) car.x = -50;
                else car.x = W + 49;
            }}
            
            // Update MPH display
            document.getElementById('currSpeedDisplay').innerText = Math.round(car.speed * 15);

            // 2. TRAFFIC MOVEMENT (Red Cars)
            obstacles.forEach(o => {{
                // Oncoming cars move at a constant safe speed
                o.x -= 2.5; 
                // Lock to Left Lane (Negative Offset)
                o.y = getRoadCenterY(o.x) - LANE_OFFSET - (CAR_H/2);
            }});
            obstacles = obstacles.filter(o => o.x > -100);
        }}

        function draw() {{
            ctx.fillStyle = "#0e1117";
            ctx.fillRect(0, 0, W, H);
            
            // Draw Road
            ctx.beginPath(); 
            ctx.moveTo(-50, getRoadCenterY(-50));
            for (let x = 0; x <= W + 50; x += 5) ctx.lineTo(x, getRoadCenterY(x));
            ctx.lineWidth = 120; ctx.strokeStyle = "#444"; ctx.stroke();

            // Draw Yellow Center Line
            ctx.beginPath(); ctx.setLineDash([15, 15]);
            for (let x = 0; x <= W; x += 5) ctx.lineTo(x, getRoadCenterY(x));
            ctx.lineWidth = 4; ctx.strokeStyle = "#ffd700"; ctx.stroke(); 
            ctx.setLineDash([]);

            // Draw Vehicles
            ctx.fillStyle = "#00d4ff"; // Player
            ctx.fillRect(car.x, car.y, CAR_W, CAR_H);
            ctx.fillStyle = "#ff4b4b"; // Traffic
            for (let o of obstacles) ctx.fillRect(o.x, o.y, CAR_W, CAR_H);
        }}

        function loop() {{ update(); draw(); requestAnimationFrame(loop); }}
        loop();
    }})();
</script>
"""

st.components.v1.html(sim_html, height=650)
