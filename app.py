import streamlit as st

st.set_page_config(page_title="Vectra AI – Perfect Flow", layout="wide")

# --- 1. SIDEBAR & SPEED LOGIC ---
with st.sidebar:
    st.header("🚦 Traffic Control")
    # This slider creates the 'speed_limit' variable
    speed_limit = st.select_slider(
        "AI Speed Limit (MPH)", 
        options=[20, 30, 40, 50, 60, 70, 80], 
        value=40
    )
    # Convert MPH to internal simulation units (pixels per frame)
    sim_limit = speed_limit / 15 
    
    st.divider()
    st.header("🗺️ Project Roadmap")
    roadmap_url = "https://raw.githubusercontent.com/Deslandes1/Vectra-AI-Built-by-Gesner-Deslandes/main/Gemini_Generated_Image_mcrtf8mcrtf8mcrt.png"
    st.image(roadmap_url, caption="Vectra AI Development Phases", use_container_width=True)

# --- 2. UI HEADER ---
st.markdown(f"""
<div style="text-align: center;">
    <h1>🚗 Vectra AI – Dynamic Speed Autopilot</h1>
    <p style="font-size: 1.1rem;">built by <strong>Gesner Deslandes</strong></p>
</div>
""", unsafe_allow_html=True)

# --- 3. SIMULATION ENGINE ---
# We inject {sim_limit} into the JS. Streamlit reruns this block on every slider change.
sim_html = f"""
<canvas id="gameCanvas" width="900" height="500" style="display: block; margin: 0 auto; border: 2px solid #b87c4f; border-radius: 12px;"></canvas>
<div style="text-align: center; font-family: monospace; font-size: 1.2rem; margin-top: 10px; color: white;">
    ⏱️ Target Speed: {speed_limit} MPH &nbsp;|&nbsp; 
    🚗 Current: <span id="currSpeed">0</span> MPH
</div>

<script>
    (function() {{
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const W = 900, H = 500, CAR_W = 34, CAR_H = 20;
        
        // This constant updates whenever you move the slider
        const TARGET_VELOCITY = {sim_limit}; 
        
        let car = {{ x: 50, y: 0, speed: 0 }};
        let obstacles = [];

        function getRoadY(x) {{
            return H/2 + 30 + Math.sin(x / 90) * 45 + Math.sin(x / 200) * 25;
        }}

        function update() {{
            // DYNAMIC SPEED ACCELERATION
            // The car 'chases' the TARGET_VELOCITY set by your slider
            let speedDiff = TARGET_VELOCITY - car.speed;
            car.speed += speedDiff * 0.05; 
            
            car.x += car.speed;

            // Loop logic with safety check
            if (car.x > W + 50) {{
                let resetZoneClear = obstacles.every(o => o.x > 150 || o.x < -20);
                if (resetZoneClear) car.x = -50;
                else car.x = W + 49;
            }}
            
            car.y = getRoadY(car.x) + 18 - (CAR_H/2);
            document.getElementById('currSpeed').innerText = Math.round(car.speed * 15);

            // Traffic Logic (matching player speed or default)
            obstacles.forEach(o => {{
                o.x -= 2.5; // Oncoming traffic speed
                o.y = getRoadY(o.x) - 18 - (CAR_H/2);
            }});
            obstacles = obstacles.filter(o => o.x > -100);
        }}

        function draw() {{
            ctx.fillStyle = "#0e1117";
            ctx.fillRect(0, 0, W, H);
            ctx.beginPath(); ctx.moveTo(-50, getRoadY(-50));
            for (let x = 0; x <= W + 50; x += 10) ctx.lineTo(x, getRoadY(x));
            ctx.lineWidth = 100; ctx.strokeStyle = "#444"; ctx.stroke();
            ctx.fillStyle = "#00d4ff";
            ctx.fillRect(car.x, car.y, CAR_W, CAR_H);
            ctx.fillStyle = "#ff4b4b";
            for (let o of obstacles) ctx.fillRect(o.x, o.y, CAR_W, CAR_H);
        }}

        function loop() {{ update(); draw(); requestAnimationFrame(loop); }}

        setInterval(() => {{
            if (obstacles.length < 3) obstacles.push({{ x: W + 50, y: 0 }});
        }}, 4000);

        loop();
    }})();
</script>
"""

st.components.v1.html(sim_html, height=600)
