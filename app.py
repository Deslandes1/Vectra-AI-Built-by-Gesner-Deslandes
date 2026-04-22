import streamlit as st

# 1. SYSTEM CONFIG & PRESERVATION
st.set_page_config(page_title="Vectra AI – Autopilot OS", layout="wide")

# --- SIDEBAR: Informants & Mode Toggle ---
with st.sidebar:
    st.header("🛠️ System Status & Informants")
    st.success("Core Model: Gemini 3 Flash")
    st.info("Vectra AI System: Active")
    st.write("Developer: **Gesner Deslandes**")
    
    st.markdown("---")
    
    st.header("🕹️ Operation Mode")
    # This allows the user to switch between the original sim and the "Autopilot" diagnostic view
    app_mode = st.radio("Select Drive Mode:", ["Standard Simulation", "Autopilot OS Mode"])
    
    if app_mode == "Autopilot OS Mode":
        st.subheader("🧠 Software Stack Active")
        with st.expander("👁️ Perception Layer"):
            st.checkbox("Object Detection (YOLO)", value=True)
            st.checkbox("Lane Segmentation", value=True)
        with st.expander("🧠 Planning & Control"):
            st.slider("Safety Buffer (Meters)", 1, 10, 5)
            st.checkbox("Emergency Braking (AEB)", value=True)
    
    st.markdown("---")
    st.caption("v2.6.0 - Video Integration Build")

# --- MAIN UI: Header & Playable Video ---
st.markdown("<h1 style='text-align: center;'>🚗 Vectra AI – Autopilot Simulation</h1>", unsafe_allow_html=True)

# PRESERVING THE ORIGINAL VIDEO & MAKING IT PLAYABLE
with st.container():
    st.subheader("📹 AI Self-Driving Core Demonstration")
    
    # Using the raw link so Streamlit can play the MP4 directly
    video_url = "https://github.com/Deslandes1/Vectra-AI-Built-by-Gesner-Deslandes/raw/main/AI%20Selfdriving.mp4"
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.video(video_url)
    with col2:
        st.write("**Video Specifications:**")
        st.write("- **Project Name:** AI Self-Driving Logic")
        st.write("- **Primary Logic:** Neural Network Pathfinding")
        st.write("- **Status:** Original Core Implementation")
        st.write("[View on GitHub](https://github.com/Deslandes1/Vectra-AI-Built-by-Gesner-Deslandes/)")

st.markdown("---")

# 2. THE SIMULATION ENGINE
# Note: Spawning logic is preserved: 1st=2, 2nd=2, 4th=4.
sim_html = f"""
<style>
    body {{ margin: 0; background-color: #0e1117; color: white; font-family: sans-serif; }}
    canvas {{ display: block; margin: 0 auto; border: 3px solid #b87c4f; border-radius: 12px; }}
    .status-bar {{ display: flex; justify-content: center; gap: 20px; margin-top: 15px; font-family: monospace; }}
    .status-item {{ padding: 5px 15px; border-radius: 5px; background: #1e2a3a; border-left: 4px solid #b87c4f; }}
    button {{ background: #b87c4f; border: none; color: white; padding: 10px 20px; font-weight: bold; border-radius: 8px; cursor: pointer; margin: 5px; }}
    button:hover {{ background: #9a653f; }}
</style>

<canvas id="gameCanvas" width="900" height="450"></canvas>

<div class="status-bar">
    <div class="status-item">🛰️ GPS: <span id="gpsDisp">CONNECTED</span></div>
    <div class="status-item">🏎️ SPEED: <span id="speedDisp">0.0</span></div>
    <div class="status-item">🎲 CLICK INDEX: <span id="clickDisp">0</span></div>
</div>

<div style="text-align: center; margin-top: 20px;">
    <button onclick="setLimit(30, 2.0)">30 MPH</button>
    <button onclick="setLimit(45, 3.5)">45 MPH</button>
    <button onclick="setLimit(70, 5.5)">70 MPH</button>
    <button id="spawnBtn" style="background:#2ecc71;">🚀 SPAWN ONCOMING</button>
    <button id="resetBtn" style="background:#e63946;">🔄 FULL SYSTEM REBOOT</button>
</div>

<script>
    (function() {{
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const W = 900, H = 450;
        const MODE = "{app_mode}"; 
        
        let speedLimit = 3.5;
        let car = {{ x: 50, y: 250, w: 34, h: 18, speed: 0 }};
        let obstacles = [];
        let spawnClicks = 0;

        function getRoadCenter(x) {{ return H/2 + Math.sin(x/150)*40; }}

        window.setLimit = (label, val) => {{ speedLimit = val; }};

        document.getElementById('spawnBtn').onclick = () => {{
            spawnClicks++;
            document.getElementById('clickDisp').innerText = spawnClicks;
            
            // PRECISE SPAWNING LOGIC: 1st=2, 2nd=2, 4th=4
            let qty = 1;
            if (spawnClicks === 1 || spawnClicks === 2) qty = 2;
            else if (spawnClicks === 4) qty = 4;

            for(let i=0; i<qty; i++) {{
                let spawnX = W + (i * 160) + 50;
                obstacles.push({{
                    x: spawnX,
                    y: getRoadCenter(spawnX % W) - 30,
                    w: 30, h: 18,
                    speed: speedLimit * 0.85
                }});
            }}
        }};

        function update() {{
            let roadMid = getRoadCenter(car.x + car.w/2);
            let targetY = roadMid + 20;
            car.y += (targetY - car.y) * 0.1;

            // Boundary Lane-Lock Logic
            if (car.y < roadMid + 2) car.y = roadMid + 2;
            if (car.y + car.h > roadMid + 48) car.y = roadMid + 48 - car.h;

            car.speed += (speedLimit - car.speed) * 0.05;
            car.x += car.speed;
            if (car.x > W) car.x = -50;

            obstacles.forEach(o => {{
                o.x -= o.speed;
                o.y = getRoadCenter(o.x % W) - 30;
                
                // Safety Collision Logic
                if (car.x < o.x + o.w && car.x + car.w > o.x &&
                    car.y < o.y + o.h && car.y + car.h > o.y) {{
                    car.speed = 0;
                }}
            }});
            obstacles = obstacles.filter(o => o.x > -150);
            document.getElementById('speedDisp').innerText = (car.speed * 12.5).toFixed(1);
        }}

        function draw() {{
            ctx.fillStyle = "#111";
            ctx.fillRect(0,0,W,H);

            // Draw Road Base
            ctx.beginPath();
            for(let x=0; x<=W; x+=10) ctx.lineTo(x, getRoadCenter(x));
            ctx.lineWidth = 100; ctx.strokeStyle = "#333"; ctx.stroke();

            // Draw Center Line (Lane separation)
            ctx.beginPath();
            ctx.setLineDash([15, 15]);
            for(let x=0; x<=W; x+=10) ctx.lineTo(x, getRoadCenter(x));
            ctx.lineWidth = 2; ctx.strokeStyle = "#ffffff55"; ctx.stroke();
            ctx.setLineDash([]);

            // SOFTWARE MODE OVERLAYS
            if (MODE === "Autopilot OS Mode") {{
                ctx.strokeStyle = "#00ffcc88";
                ctx.setLineDash([5, 5]);
                ctx.strokeRect(car.x - 5, car.y - 5, car.w + 10, car.h + 10);
                obstacles.forEach(o => ctx.strokeRect(o.x - 2, o.y - 2, o.w + 4, o.h + 4));
                ctx.setLineDash([]);
            }}

            // Draw AI Car (Green)
            ctx.fillStyle = "#2ecc71";
            ctx.fillRect(car.x, car.y, car.w, car.h);

            // Draw Obstacles (Red)
            ctx.fillStyle = "#e63946";
            obstacles.forEach(o => ctx.fillRect(o.x, o.y, o.w, o.h));

            update();
            requestAnimationFrame(draw);
        }}

        document.getElementById('resetBtn').onclick = () => {{
            car.x = 50; obstacles = []; spawnClicks = 0;
            document.getElementById('clickDisp').innerText = 0;
        }};
        draw();
    }})();
</script>
"""

st.components.v1.html(sim_html, height=600)
