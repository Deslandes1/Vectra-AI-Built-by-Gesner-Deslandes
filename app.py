import streamlit as st

st.set_page_config(page_title="Vectra AI – Autopilot OS", layout="wide")

# --- SIDEBAR: Real-World Software Stack ---
with st.sidebar:
    st.header("🛠️ Autopilot Software Stack")
    st.info("These diagnostic layers represent the software needed to move from a simulation to a real car.")
    
    with st.expander("👁️ Perception Layer"):
        st.write("**Sensor Fusion:** Aggregating data from LiDAR, Radar, and Cameras.")
        st.checkbox("Object Detection (YOLO)", value=True)
        st.checkbox("Lane Segmentation", value=True)
        
    with st.expander("📍 Localization & Maps"):
        st.write("**RTK-GPS:** Centimeter-level positioning.")
        st.write("**HD Maps:** Pre-cached 3D road geometry.")
        st.checkbox("SLAM (Simultaneous Mapping)", value=False)
        
    with st.expander("🧠 Planning & Control"):
        st.write("**MPC Controller:** Predicting trajectories.")
        st.slider("Safety Buffer (Meters)", 1, 10, 5)
        st.checkbox("Emergency Braking (AEB)", value=True)

    st.markdown("---")
    st.write("Current OS: **Vectra Drive 2.4**")

# --- MAIN UI ---
st.markdown("<h1 style='text-align: center;'>🚗 Vectra AI – Autopilot Simulation</h1>", unsafe_allow_html=True)

# The HTML/JavaScript Simulation Engine
sim_html = """
<style>
    body { margin: 0; background-color: #0e1117; color: white; font-family: sans-serif; }
    canvas { display: block; margin: 0 auto; border: 3px solid #b87c4f; border-radius: 12px; }
    .status-bar { display: flex; justify-content: center; gap: 20px; margin-top: 15px; font-family: monospace; }
    .status-item { padding: 5px 15px; border-radius: 5px; background: #1e2a3a; border-left: 4px solid #b87c4f; }
    button { background: #b87c4f; border: none; color: white; padding: 10px 20px; font-weight: bold; border-radius: 8px; cursor: pointer; margin: 5px; }
    button:hover { background: #9a653f; }
</style>

<canvas id="gameCanvas" width="900" height="450"></canvas>

<div class="status-bar">
    <div class="status-item">📡 LATENCY: <span id="latDisp">12ms</span></div>
    <div class="status-item">🛰️ GPS: <span id="gpsDisp">LOCKED</span></div>
    <div class="status-item">🏎️ SPEED: <span id="speedDisp">0.0</span></div>
</div>

<div style="text-align: center; margin-top: 20px;">
    <button onclick="setLimit(30, 2.0)">CITY (30)</button>
    <button onclick="setLimit(45, 3.5)">SUBURB (45)</button>
    <button onclick="setLimit(70, 5.5)">HWY (70)</button>
    <button id="spawnBtn" style="background:#2ecc71;">ADD TRAFFIC</button>
    <button id="resetBtn" style="background:#e63946;">SYSTEM REBOOT</button>
</div>

<script>
    (function() {
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const W = 900, H = 450;
        
        let speedLimit = 3.5;
        let car = { x: 50, y: 250, w: 34, h: 18, speed: 0 };
        let obstacles = [];
        let spawnClicks = 0;

        function getRoadCenter(x) { return H/2 + Math.sin(x/150)*40; }

        window.setLimit = (label, val) => {
            speedLimit = val;
        };

        document.getElementById('spawnBtn').onclick = () => {
            spawnClicks++;
            // Logic: 1st click = 2 cars, 2nd click = 2 cars, 4th click = 4 cars
            let qty = 1;
            if (spawnClicks === 1 || spawnClicks === 2) qty = 2;
            else if (spawnClicks === 4) qty = 4;

            for(let i=0; i<qty; i++) {
                let spawnX = W + (i * 160) + 50;
                obstacles.push({
                    x: spawnX,
                    y: getRoadCenter(spawnX % W) - 30,
                    w: 30, h: 18,
                    speed: speedLimit * 0.85
                });
            }
        };

        function update() {
            // Steering & Lane Boundary Logic
            let roadMid = getRoadCenter(car.x + car.w/2);
            let targetY = roadMid + 20;
            car.y += (targetY - car.y) * 0.1;

            // Physical Constraints
            if (car.y < roadMid + 2) car.y = roadMid + 2;
            if (car.y + car.h > roadMid + 48) car.y = roadMid + 48 - car.h;

            // Speed & Movement
            car.speed += (speedLimit - car.speed) * 0.05;
            car.x += car.speed;
            if (car.x > W) car.x = -50;

            obstacles.forEach(o => {
                o.x -= o.speed;
                o.y = getRoadCenter(o.x % W) - 30;
                // Collision check
                if (car.x < o.x + o.w && car.x + car.w > o.x &&
                    car.y < o.y + o.h && car.y + car.h > o.y) {
                    car.speed = 0;
                }
            });
            obstacles = obstacles.filter(o => o.x > -150);
            
            document.getElementById('speedDisp').innerText = (car.speed * 12.5).toFixed(1) + " mph";
        }

        function draw() {
            ctx.fillStyle = "#111";
            ctx.fillRect(0,0,W,H);

            // Draw Road
            ctx.beginPath();
            for(let x=0; x<=W; x+=10) ctx.lineTo(x, getRoadCenter(x));
            ctx.lineWidth = 100;
            ctx.strokeStyle = "#333";
            ctx.stroke();

            // Software Diagnostic Overlay
            ctx.strokeStyle = "#00ffcc44";
            ctx.setLineDash([5, 5]);
            ctx.strokeRect(car.x - 5, car.y - 5, car.w + 10, car.h + 10);
            ctx.setLineDash([]);

            // Draw Car
            ctx.fillStyle = "#2ecc71";
            ctx.fillRect(car.x, car.y, car.w, car.h);

            // Draw Obstacles
            ctx.fillStyle = "#e63946";
            obstacles.forEach(o => ctx.fillRect(o.x, o.y, o.w, o.h));

            update();
            requestAnimationFrame(draw);
        }

        document.getElementById('resetBtn').onclick = () => {
            car.x = 50; obstacles = []; spawnClicks = 0;
        };

        draw();
    })();
</script>
"""

st.components.v1.html(sim_html, height=600)
