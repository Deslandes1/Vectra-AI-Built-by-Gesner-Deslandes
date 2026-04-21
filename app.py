import streamlit as st

st.set_page_config(page_title="Vectra AI – Strict Lane Discipline", layout="wide")

st.markdown("""
<style>
    body { margin: 0; background-color: #0e1117; }
    canvas { display: block; margin: 0 auto; border: 2px solid #b87c4f; border-radius: 12px; box-shadow: 0 0 20px rgba(0,0,0,0.5); }
    .info { text-align: center; font-family: monospace; font-size: 1.2rem; margin-top: 10px; color: white; }
    button { background: #b87c4f; border: none; color: white; padding: 8px 16px; font-weight: bold; border-radius: 8px; cursor: pointer; margin: 5px; }
    button:hover { background: #9a653f; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center;">
    <h1>🚗 Vectra AI – Strict Lane Control</h1>
    <p>Oncoming cars drive <strong>West</strong>. Your car drives <strong>East</strong>. Both are physically locked into their respective lanes.</p>
</div>
""", unsafe_allow_html=True)

sim_html = """
<canvas id="gameCanvas" width="900" height="500" tabindex="0"></canvas>
<div class="info">
    🧠 AI Status: <span id="status">Driving</span> &nbsp;|&nbsp;
    🚗 Oncoming Traffic: <span id="obstacleCount">0</span>
</div>
<div style="text-align: center; margin-top: 10px;">
    <button id="resetBtn">🔄 Reset Simulation</button>
    <button id="spawnBtn">🎲 Spawn Oncoming Car</button>
</div>

<script>
    (function() {
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const statusSpan = document.getElementById('status');
        const countSpan = document.getElementById('obstacleCount');

        const W = 900, H = 500;
        const CAR_W = 34, CAR_H = 20;
        const PLAYER_SPEED = 3.2;
        const ONCOMING_SPEED = -2.8;

        let car = { x: 50, y: 0, alive: true };
        let obstacles = [];

        function getRoadCenterY(x) {
            return H/2 + 30 + Math.sin(x / 90) * 45 + Math.sin(x / 200) * 25;
        }

        function update() {
            if (!car.alive) return;

            // 1. Move Player (Locked to Right Lane)
            car.x += PLAYER_SPEED;
            if (car.x > W + 50) car.x = -50;
            // Strict Y-Constraint: Center + Offset
            car.y = getRoadCenterY(car.x) + 18 - (CAR_H/2);

            // 2. Move Obstacles (Locked to Left Lane, Moving West)
            for (let i = obstacles.length - 1; i >= 0; i--) {
                let obs = obstacles[i];
                obs.x += ONCOMING_SPEED;
                // Strict Y-Constraint: Center - Offset
                obs.y = getRoadCenterY(obs.x) - 18 - (CAR_H/2);
                
                if (obs.x < -100) obstacles.splice(i, 1);
            }
            countSpan.innerText = obstacles.length;

            // 3. Precise Collision Detection
            for (let obs of obstacles) {
                if (car.x < obs.x + CAR_W && car.x + CAR_W > obs.x &&
                    car.y < obs.y + CAR_H && car.y + CAR_H > obs.y) {
                    car.alive = false;
                    statusSpan.innerText = "COLLISION DETECTED";
                }
            }
        }

        function draw() {
            ctx.fillStyle = "#1a1c23";
            ctx.fillRect(0, 0, W, H);

            // Draw Road Path
            ctx.beginPath();
            ctx.moveTo(-50, getRoadCenterY(-50));
            for (let x = 0; x <= W + 50; x += 10) ctx.lineTo(x, getRoadCenterY(x));
            ctx.lineWidth = 110;
            ctx.strokeStyle = "#444"; // Asphalt
            ctx.stroke();

            // Center Dashed Line
            ctx.beginPath();
            ctx.setLineDash([20, 20]);
            for (let x = 0; x <= W; x += 5) ctx.lineTo(x, getRoadCenterY(x));
            ctx.lineWidth = 4;
            ctx.strokeStyle = "#ffd700";
            ctx.stroke();
            ctx.setLineDash([]);

            // Draw Oncoming (Red - Driving Left)
            ctx.fillStyle = "#ff4b4b";
            for (let obs of obstacles) {
                ctx.fillRect(obs.x, obs.y, CAR_W, CAR_H);
                // Headlights (pointing left)
                ctx.fillStyle = "#fff";
                ctx.fillRect(obs.x, obs.y + 2, 4, 4);
                ctx.fillRect(obs.x, obs.y + CAR_H - 6, 4, 4);
                ctx.fillStyle = "#ff4b4b";
            }

            // Draw Player (Green - Driving Right)
            ctx.fillStyle = car.alive ? "#00d4ff" : "#888";
            ctx.fillRect(car.x, car.y, CAR_W, CAR_H);
            // Headlights (pointing right)
            ctx.fillStyle = "#fff";
            ctx.fillRect(car.x + CAR_W - 4, car.y + 2, 4, 4);
            ctx.fillRect(car.x + CAR_W - 4, car.y + CAR_H - 6, 4, 4);
        }

        function loop() {
            update();
            draw();
            requestAnimationFrame(loop);
        }

        document.getElementById('spawnBtn').onclick = () => {
            obstacles.push({ x: W + 100, y: 0, speed: ONCOMING_SPEED });
        };

        document.getElementById('resetBtn').onclick = () => {
            car.x = 50; car.alive = true; obstacles = [];
            statusSpan.innerText = "Driving";
        };

        loop();
    })();
</script>
"""

st.components.v1.html(sim_html, height=620)
