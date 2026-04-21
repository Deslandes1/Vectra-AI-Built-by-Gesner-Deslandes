import streamlit as st

st.set_page_config(page_title="Vectra AI – Manual Flow", layout="wide")

# --- 1. SIDEBAR & SPEED LOGIC ---
with st.sidebar:
    st.header("🚦 Traffic Control")
    speed_limit = st.select_slider(
        "AI Speed Limit (MPH)", 
        options=[20, 30, 40, 50, 60, 70, 80], 
        value=40
    )
    sim_limit = speed_limit / 15 
    
    st.divider()
    st.header("🗺️ Project Roadmap")
    roadmap_url = "https://raw.githubusercontent.com/Deslandes1/Vectra-AI-Built-by-Gesner-Deslandes/main/Gemini_Generated_Image_mcrtf8mcrtf8mcrt.png"
    st.image(roadmap_url, caption="Vectra AI Development Phases", use_container_width=True)

# --- 2. UI HEADER & ORIGINAL VIDEO ---
st.markdown(f"""
<div style="text-align: center;">
    <h1>🚗 Vectra AI – Manual Traffic Control</h1>
    <p style="font-size: 1.1rem;">built by <strong>Gesner Deslandes</strong></p>
</div>
""", unsafe_allow_html=True)

st.video("https://raw.githubusercontent.com/Deslandes1/Vectra-AI-Built-by-Gesner-Deslandes/main/AI%20Selfdriving.mp4")

# --- 3. SIMULATION ENGINE ---
sim_html = f"""
<canvas id="gameCanvas" width="900" height="500" style="display: block; margin: 0 auto; border: 2px solid #b87c4f; border-radius: 12px;"></canvas>
<div style="text-align: center; margin-top: 15px;">
    <button id="spawnBtn" style="background: #b87c4f; color: white; padding: 12px 24px; border-radius: 8px; border: none; font-weight: bold; cursor: pointer; font-size: 1rem;">
        🎲 Add Oncoming Car
    </button>
</div>
<div style="text-align: center; font-family: monospace; font-size: 1.2rem; margin-top: 10px; color: white;">
    🚗 On-Road: <span id="obsActive">0</span> &nbsp;|&nbsp; 
    ⏱️ Speed: <span id="currSpeed">0</span> MPH
</div>

<script>
    (function() {{
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const W = 900, H = 500, CAR_W = 34, CAR_H = 20;
        const SAFE_BUBBLE = 85; 
        
        const TARGET_VELOCITY = {sim_limit}; 
        let car = {{ x: 50, y: 0, speed: 0 }};
        let obstacles = [];

        function getRoadY(x) {{
            return H/2 + 30 + Math.sin(x / 90) * 45 + Math.sin(x / 200) * 25;
        }}

        // --- THE SPAWN FUNCTIONALITY ---
        document.getElementById('spawnBtn').onclick = () => {{
            // SENTINEL: Only add a car if the entrance (right side) isn't occupied
            // This allows you to click as fast as you want, provided there's space.
            let entranceClear = obstacles.every(o => o.x < W - 60);
            if (entranceClear) {{
                obstacles.push({{ x: W + 50, y: 0, speed: -2.5 }});
            }}
        }};

        function update() {{
            // Player Speed Sync
            let speedDiff = TARGET_VELOCITY - car.speed;
            car.speed += speedDiff * 0.05; 
            car.x += car.speed;

            // Boundary Logic (Zero-Crash)
            if (car.x > W + 50) {{
                let resetZoneClear = obstacles.every(o => o.x > 150 || o.x < -20);
                if (resetZoneClear) car.x = -50;
                else car.x = W + 49;
            }}
            car.y = getRoadY(car.x) + 18 - (CAR_H/2);
            document.getElementById('currSpeed').innerText = Math.round(car.speed * 15);

            // Traffic Coordination
            obstacles.sort((a, b) => a.x - b.x); 
            for (let i = 0; i < obstacles.length; i++) {{
                let o = obstacles[i];
                let oTarget = -2.5;

                // Sync with car ahead to prevent rear-ends
                if (i > 0) {{
                    let leader = obstacles[i-1];
                    let gap = o.x - (leader.x + CAR_W);
                    if (gap < SAFE_BUBBLE) oTarget = leader.speed;
                }}
                
                o.speed = oTarget;
                o.x += o.speed;
                o.y = getRoadY(o.x) - 18 - (CAR_H/2);
            }}
            obstacles = obstacles.filter(o => o.x > -100);
            document.getElementById('obsActive').innerText = obstacles.length;
        }}

        function draw() {{
            ctx.fillStyle = "#0e1117";
            ctx.fillRect(0, 0, W, H);
            ctx.beginPath(); ctx.moveTo(-50, getRoadY(-50));
            for (let x = 0; x <= W + 50; x += 10) ctx.lineTo(x, getRoadY(x));
            ctx.lineWidth = 100; ctx.strokeStyle = "#444"; ctx.stroke();
            ctx.beginPath(); ctx.setLineDash([15, 15]);
            for (let x = 0; x <= W; x += 5) ctx.lineTo(x, getRoadY(x));
            ctx.lineWidth = 3; ctx.strokeStyle = "#ffd700"; ctx.stroke(); ctx.setLineDash([]);
            ctx.fillStyle = "#00d4ff";
            ctx.fillRect(car.x, car.y, CAR_W, CAR_H);
            ctx.fillStyle = "#ff4b4b";
            for (let o of obstacles) ctx.fillRect(o.x, o.y, CAR_W, CAR_H);
        }}

        function loop() {{ update(); draw(); requestAnimationFrame(loop); }}
        loop();
    }})();
</script>
"""

st.components.v1.html(sim_html, height=650)
