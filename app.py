import streamlit as st

st.set_page_config(page_title="Vectra AI – Dust Road Driving", layout="wide")

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
    <h1>🚗 Vectra AI – Road Limits & Scaled Spawning</h1>
    <p style="font-size: 1.1rem;">built by <strong>Gesner Deslandes</strong></p>
    <p>The car adapts to <strong>speed limits</strong> and handles <strong>scaled oncoming traffic</strong> logic.</p>
</div>
""", unsafe_allow_html=True)

# --- The Simulation Canvas ---
sim_html = """
<canvas id="gameCanvas" width="900" height="500" tabindex="0" style="outline: none;"></canvas>
<div class="info">
    🚦 Limit: <span id="limitDisp">45 mph</span> &nbsp;|&nbsp;
    🏎️ Speed: <span id="speedDisp">0.0</span> &nbsp;|&nbsp;
    🎲 Click Count: <span id="spawnIdx">0</span>
</div>
<div style="text-align: center; margin-top: 10px;">
    <button onclick="setLimit(30, 2.2)">30 MPH</button>
    <button onclick="setLimit(45, 3.5)">45 MPH</button>
    <button onclick="setLimit(70, 5.5)">70 MPH</button>
    <button id="spawnBtn" style="background: #2a9d8f;">🚀 Spawn Oncoming</button>
    <button id="resetBtn" style="background: #e63946;">🔄 Reset Drive</button>
</div>

<script>
    (function() {
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const speedDisp = document.getElementById('speedDisp');
        const limitDisp = document.getElementById('limitDisp');
        const spawnIdxDisp = document.getElementById('spawnIdx');

        const W = 900, H = 500;
        const CAR_WIDTH = 30, CAR_HEIGHT = 20;
        let speedLimit = 3.5;
        let spawnClicks = 0;
        let obstacles = [];
        let car = { x: 50, y: 0, angle: 0, speed: 0, alive: true };

        function getRoadCenterY(x) {
            return H/2 + 30 + Math.sin(x / 90) * 45 + Math.sin(x / 200) * 25;
        }

        window.setLimit = (label, val) => {
            speedLimit = val;
            limitDisp.innerText = label + " mph";
        };

        function spawnOncoming() {
            spawnClicks++;
            spawnIdxDisp.innerText = spawnClicks;
            
            let count = 0;
            if (spawnClicks === 1 || spawnClicks === 2) count = 2;
            else if (spawnClicks === 4) count = 4;
            else count = 1; // Default for other click counts

            for(let i=0; i<count; i++) {
                let startX = W + (i * 120) + 100;
                obstacles.push({
                    x: startX,
                    y: getRoadCenterY(startX % W) - 30,
                    w: 28, h: 20,
                    speed: speedLimit * 0.8 // Oncoming traffic moves relative to limit
                });
            }
        }

        function update() {
            if (!car.alive) return;

            // 1. Dynamic Speed Control (Smooth Acceleration/Deceleration)
            car.speed += (speedLimit - car.speed) * 0.05;
            speedDisp.innerText = (car.speed * 12.5).toFixed(1);

            // 2. Movement & Lane Keeping (Stay Right)
            car.x += car.speed;
            if (car.x > W) car.x = -CAR_WIDTH;
            
            let targetY = getRoadCenterY(car.x) + 20;
            car.y += (targetY - car.y) * 0.1;

            // 3. Obstacle Logic
            for (let i = obstacles.length - 1; i >= 0; i--) {
                let obs = obstacles[i];
                obs.x -= obs.speed;
                obs.y = getRoadCenterY(obs.x % W) - 30;

                // Collision Detection
                if (car.x < obs.x + obs.w && car.x + CAR_WIDTH > obs.x &&
                    car.y < obs.y + obs.h && car.y + CAR_HEIGHT > obs.y) {
                    car.alive = false;
                }

                if (obs.x < -100) obstacles.splice(i, 1);
            }
        }

        function draw() {
            // Background
            ctx.fillStyle = "#c9a87b";
            ctx.fillRect(0, 0, W, H);
            
            // Road Path
            ctx.beginPath();
            ctx.moveTo(0, getRoadCenterY(0));
            for (let x = 0; x <= W; x += 10) ctx.lineTo(x, getRoadCenterY(x));
            ctx.lineWidth = 90;
            ctx.strokeStyle = "#a56b3a";
            ctx.stroke();

            // Center Line
            ctx.beginPath();
            ctx.setLineDash([15, 20]);
            for (let x = 0; x <= W; x += 10) ctx.lineTo(x, getRoadCenterY(x));
            ctx.lineWidth = 3;
            ctx.strokeStyle = "#ffffff";
            ctx.stroke();
            ctx.setLineDash([]);

            // Draw Car
            ctx.fillStyle = car.alive ? "#2a9d8f" : "#555";
            ctx.fillRect(car.x, car.y, CAR_WIDTH, CAR_HEIGHT);

            // Draw Obstacles
            ctx.fillStyle = "#e63946";
            for (let obs of obstacles) {
                ctx.fillRect(obs.x, obs.y, obs.w, obs.h);
            }

            update();
            requestAnimationFrame(draw);
        }

        document.getElementById('spawnBtn').addEventListener('click', spawnOncoming);
        document.getElementById('resetBtn').addEventListener('click', () => {
            car.x = 50; car.alive = true; obstacles = []; spawnClicks = 0;
            spawnIdxDisp.innerText = "0";
        });

        draw();
    })();
</script>
"""

st.components.v1.html(sim_html, height=620)

st.markdown("""
---
### 🧠 Logic Breakdown

1.  **Variable Speed Limits**: Clicking a speed button changes the `speedLimit` variable. The AI uses a **linear interpolation** formula to accelerate smoothly rather than jumping instantly to the speed.
2.  **Scaled Spawning**: 
    - **Click 1 & 2**: Spawns **2 cars** each time.
    - **Click 3**: Spawns **1 car** (default).
    - **Click 4**: Spawns **4 cars**.
3.  **Relative Traffic**: Obstacle speed is calculated as `speedLimit * 0.8`, meaning traffic flows faster when the speed limit is higher.
""")
