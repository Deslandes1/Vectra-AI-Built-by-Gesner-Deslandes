import streamlit as st

st.set_page_config(page_title="Vectra AI – Perfect Flow", layout="wide")

# --- 1. SIDEBAR & SPEED LOGIC ---
with st.sidebar:
    st.header("🚦 Traffic Control")
    # This slider now drives the physics engine
    speed_limit = st.select_slider(
        "AI Speed Limit (MPH)", 
        options=[20, 30, 40, 50, 60, 70, 80], 
        value=40
    )
    # Physics math: 15 MPH = ~1.0 pixel per frame in the engine
    sim_limit = speed_limit / 15 
    
    st.divider()
    st.header("🗺️ Project Roadmap")
    roadmap_url = "https://raw.githubusercontent.com/Deslandes1/Vectra-AI-Built-by-Gesner-Deslandes/main/Gemini_Generated_Image_mcrtf8mcrtf8mcrt.png"
    st.image(roadmap_url, caption="Vectra AI Development Phases", use_container_width=True)

# --- 2. UI HEADER & ORIGINAL VIDEO ---
st.markdown(f"""
<div style="text-align: center;">
    <h1>🚗 Vectra AI – Dynamic Speed Autopilot</h1>
    <p style="font-size: 1.1rem;">built by <strong>Gesner Deslandes</strong></p>
</div>
""", unsafe_allow_html=True)

# YOUR FIRST VIDEO (Remains unchanged)
st.video("https://raw.githubusercontent.com/Deslandes1/Vectra-AI-Built-by-Gesner-Deslandes/main/AI%20Selfdriving.mp4")

# --- 3. SIMULATION ENGINE ---
# {sim_limit} and {speed_limit} are injected into the JavaScript below
sim_html = f"""
<canvas id="gameCanvas" width="900" height="500" style="display: block; margin: 0 auto; border: 2px solid #b87c4f; border-radius: 12px;"></canvas>
<div style="text-align: center; font-family: monospace; font-size: 1.2rem; margin-top: 10px; color: white;">
    🧠 Autopilot Target: <span style="color: #00ff00;">{speed_limit} MPH</span> &nbsp;|&nbsp; 
    ⏱️ Real-time: <span id="currSpeed">0</span> MPH
</div>

<script>
    (function() {{
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const W = 900, H = 500, CAR_W = 34, CAR_H = 20;
        
        // SPEED LINK: This value updates whenever you move the slider
        const TARGET_VELOCITY = {sim_limit}; 
        
        let car = {{ x: 50, y: 0, speed: 0 }};
        let obstacles = [];

        function getRoadY(x) {{
            return H/2 + 30 + Math.sin(x / 90) * 45 + Math.sin(x / 200) * 25;
        }}

        function update() {{
            // 1. DYNAMIC SPEED CONTROL
            // The car 'chases' the slider speed using a 0.05 interpolation for smooth movement
            let speedDiff = TARGET_VELOCITY - car.speed;
            car.speed += speedDiff * 0.05; 
            
            car.x += car.speed;

            // 2. CRASH-PROOF BOUNDARY LOGIC
            if (car.x > W + 50) {{
                // Check if the left-side entry is clear of traffic before resetting
                let resetZoneClear = obstacles.every(o => o.x > 150 || o.x < -20);
                if (resetZoneClear) {{
                    car.x = -50;
                }} else {{
                    car.x = W + 49; // Hold off-screen if lane is blocked
                }}
            }}
            
            car.y = getRoadY(car.x) + 18 - (CAR_H/2);
            document.getElementById('currSpeed').innerText = Math.round(car.speed * 15);

            // 3. TRAFFIC AUTO-FLOW
            obstacles.forEach(o => {{
                o.x -= 2.5; // Oncoming traffic speed
                o.y = getRoadY(o.x) - 18 - (CAR_H/2);
            }});
            obstacles = obstacles.filter(o => o.x > -100);
        }}

        function draw() {{
            ctx.fillStyle = "#0e1117";
            ctx.fillRect(0, 0, W, H);
            
            // Draw Road
            ctx.beginPath(); ctx.moveTo(-50, getRoadY(-50));
            for (let x = 0; x <= W + 50; x += 10) ctx.lineTo(x, getRoadY(x));
            ctx.lineWidth = 100; ctx.strokeStyle = "#444"; ctx.stroke();

            // Center Dash
            ctx.beginPath(); ctx.setLineDash([15, 15]);
            for (let x = 0; x <= W; x += 5) ctx.lineTo(x, getRoadY(x));
            ctx.lineWidth = 3; ctx.strokeStyle = "#ffd700"; ctx.stroke(); ctx.setLineDash([]);

            // Vehicles
            ctx.fillStyle = "#00d4ff"; // Player Car
            ctx.fillRect(car.x, car.y, CAR_W, CAR_H);
            ctx.fillStyle = "#ff4b4b"; // Traffic
            for (let o of obstacles) ctx.fillRect(o.x, o.y, CAR_W, CAR_H);
        }}

        function loop() {{ update(); draw(); requestAnimationFrame(loop); }}

        // Safety Spawn (keeps traffic moving)
        setInterval(() => {{
            if (obstacles.length < 3) obstacles.push({{ x: W + 50, y: 0 }});
        }}, 4000);

        loop();
    }})();
</script>
"""

st.components.v1.html(sim_html, height=600)
