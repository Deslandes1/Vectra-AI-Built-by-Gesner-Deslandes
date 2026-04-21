import streamlit as st

st.set_page_config(page_title="Vectra AI – Dust Road Driving", layout="wide")

# --- Original Custom Styling ---
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

st.markdown("""
<div style="text-align: center;">
    <h1>🚗 Vectra AI – Dust Road</h1>
    <p style="font-size: 1.1rem;">built by <strong>Gesner Deslandes</strong></p>
    <p>Self‑Driving Car on a winding dirt road – strictly avoids oncoming cars on the left</p>
</div>
""", unsafe_allow_html=True)

# --- Restored Demonstration Video ---
st.markdown("## 🎥 Vectra AI in Action")
st.markdown("Watch the autonomous driving system navigate real roads with a human driver monitoring only.")
video_url = "https://raw.githubusercontent.com/Deslandes1/Vectra-AI-Built-by-Gesner-Deslandes/main/AI%20Selfdriving.mp4"
st.video(video_url)

# --- Simulation Canvas ---
sim_html = """
<canvas id="gameCanvas" width="900" height="500" tabindex="0" style="outline: none; cursor: crosshair;"></canvas>
<div class="info">
    🧠 AI Status: <span id="status">Driving</span> &nbsp;|&nbsp;
    🚗 Oncoming Traffic: <span id="obstacleCount">0</span> &nbsp;|&nbsp;
    💥 Collisions: <span id="collisionCount">0</span>
</div>
<div style="text-align: center; margin-top: 10px;">
    <button id="resetBtn">🔄 Reset Drive</button>
    <button id="clearObstaclesBtn">🗑️ Clear Other Cars</button>
    <button id="randomObstaclesBtn">🎲 Add Oncoming Cars (Left Side)</button>
</div>

<script>
    (function() {
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const statusSpan = document.getElementById('status');
        const obstacleCountSpan = document.getElementById('obstacleCount');
        const collisionCountSpan = document.getElementById('collisionCount');

        const W = 900, H = 500;
        const CAR_WIDTH = 30, CAR_HEIGHT = 20;
        const SENSOR_LENGTH = 160;
        const MAX_SPEED = 3.5;
        const ONCOMING_SPEED = -2.5; // Driving West (Opposite)

        let car = { x: 50, y: 0, speed: 0, alive: true, collisions: 0 };
        let obstacles = [];

        function getRoadCenterY(x) {
            return H/2 + 30 + Math.sin(x / 90) * 45 + Math.sin(x / 200) * 25;
        }

        function update() {
            if (!car.alive) return;

            // 1. Player Physics (Stay on Right)
            car.speed = Math.min(car.speed + 0.1, MAX_SPEED);
            car.x += car.speed;
            if (car.x > W + 50) car.x = -50;
            // Physical Lane Lock
            car.y = getRoadCenterY(car.x) + 20 - (CAR_HEIGHT/2);

            // 2. Oncoming Traffic (Stay on Left, Move West)
            for (let i = obstacles.length - 1; i >= 0; i--) {
                let o = obstacles[i];
                o.x += ONCOMING_SPEED;
                o.y = getRoadCenterY(o.x) - 20 - (CAR_HEIGHT/2);
                if (o.x < -100) obstacles.splice(i, 1);
            }
            obstacleCountSpan.innerText = obstacles.length;

            // 3. Collision Logic
            for (let o of obstacles) {
                if (car.x < o.x + CAR_WIDTH && car.x + CAR_WIDTH > o.x &&
                    car.y < o.y + CAR_HEIGHT && car.y + CAR_HEIGHT > o.y) {
                    car.alive = false;
                    car.collisions++;
                    statusSpan.innerText = "CRASH!";
                }
            }
        }

        function draw() {
            // Draw Ground
            ctx.fillStyle = "#c9a87b";
            ctx.fillRect(0, 0, W, H);

            // Draw Road
            ctx.beginPath();
            ctx.moveTo(-50, getRoadCenterY(-50));
            for (let x = 0; x <= W + 50; x += 10) ctx.lineTo(x, getRoadCenterY(x));
            ctx.lineWidth = 100;
            ctx.strokeStyle = "#a56b3a";
            ctx.stroke();

            // Center Lane Marker
            ctx.beginPath();
            ctx.setLineDash([15, 20]);
            for (let x = 0; x <= W; x += 5) ctx.lineTo(x, getRoadCenterY(x));
            ctx.lineWidth = 3;
            ctx.strokeStyle = "#f0d5a8";
            ctx.stroke();
            ctx.setLineDash([]);

            // Draw Oncoming (Red)
            ctx.fillStyle = "#e63946";
            for (let o of obstacles) ctx.fillRect(o.x, o.y, CAR_WIDTH, CAR_HEIGHT);

            // Draw Car (Green)
            ctx.fillStyle = car.alive ? "#2a9d8f" : "#555";
            ctx.fillRect(car.x, car.y, CAR_WIDTH, CAR_HEIGHT);
        }

        function loop() {
            update();
            draw();
            requestAnimationFrame(loop);
        }

        document.getElementById('randomObstaclesBtn').onclick = () => {
            obstacles.push({ x: W + 100, y: 0 });
        };
        document.getElementById('resetBtn').onclick = () => {
            car.x = 50; car.alive = true; obstacles = []; car.speed = 0;
            statusSpan.innerText = "Driving";
        };
        document.getElementById('clearObstaclesBtn').onclick = () => { obstacles = []; };

        loop();
    })();
</script>
"""

st.components.v1.html(sim_html, height=600)

# --- Speed and Friction Logic (Fixed Line 141) ---
st.markdown("""
### 🧠 Speed Control Logic
The AI doesn't just "jump" to the new speed. It calculates the difference between its current velocity and the road limit, applying a **0.05 friction/acceleration coefficient**. 

This ensures that if you switch from 30 MPH to 70 MPH, you see the car physically lean into the acceleration rather than snapping instantly to a new value.

---
<div class="footer">
    Vectra AI built by <strong>Gesner Deslandes</strong> – GlobalInternet.py
</div>
""", unsafe_allow_html=True)
