import streamlit as st
import random

st.set_page_config(page_title="Vectra AI – Self-Driving Simulator", layout="wide")

st.markdown("""
<style>
    body { margin: 0; background-color: #0e1117; }
    canvas { display: block; margin: 0 auto; border: 2px solid #00c9a7; border-radius: 12px; box-shadow: 0 0 20px rgba(0,0,0,0.5); }
    .info { text-align: center; font-family: monospace; font-size: 1.2rem; margin-top: 10px; color: white; }
    button { background: #00c9a7; border: none; color: black; padding: 8px 16px; font-weight: bold; border-radius: 8px; cursor: pointer; margin: 5px; }
    button:hover { background: #00a8c5; }
    .footer { text-align: center; margin-top: 20px; color: #888; font-size: 0.8rem; }
    .sensor-diagram { background: #1e2a3a; border-radius: 16px; padding: 1rem; margin: 1rem 0; text-align: center; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center;">
    <h1>🚗 Vectra AI</h1>
    <p style="font-size: 1.1rem;">built by <strong>Gesner Deslandes</strong></p>
    <p>Self‑Driving Car Simulator – rule‑based AI with 5 sensors</p>
    <p><strong>Click on the canvas to add obstacles. Watch the AI navigate.</strong></p>
</div>
""", unsafe_allow_html=True)

# --- Demonstration Video ---
st.markdown("## 🎥 Vectra AI in Action")
st.markdown("Watch the autonomous driving system navigate real roads with a human driver monitoring only (hands-off).")
video_url = "https://raw.githubusercontent.com/Deslandes1/Vectra-AI-Built-by-Gesner-Deslandes/main/AI%20Selfdriving.mp4"
st.video(video_url)
st.caption("Note: If the video does not play, your browser may not support the MP4 format. Try viewing this app in Chrome or Edge.")

# --- The Simulation Canvas ---
sim_html = """
<canvas id="gameCanvas" width="900" height="500" tabindex="0" style="outline: none; cursor: crosshair;"></canvas>
<div class="info">
    🧠 AI Status: <span id="status">Driving</span> &nbsp;|&nbsp;
    🚧 Obstacles: <span id="obstacleCount">0</span> &nbsp;|&nbsp;
    💥 Collisions: <span id="collisionCount">0</span>
</div>
<div style="text-align: center; margin-top: 10px;">
    <button id="resetBtn">🔄 Reset Simulator</button>
    <button id="clearObstaclesBtn">🗑️ Clear Obstacles</button>
    <button id="randomObstaclesBtn">🎲 Random Obstacles</button>
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
        const OBSTACLE_SIZE = 30;
        const SENSOR_LENGTH = 120;
        const SENSOR_COUNT = 5;
        const MAX_SPEED = 4;
        const TURN_SPEED = 0.1;

        let car = {
            x: W/2,
            y: H - 100,
            angle: 0,
            speed: 0,
            alive: true,
            collisions: 0
        };
        let obstacles = [];

        function updateUI() {
            obstacleCountSpan.innerText = obstacles.length;
            collisionCountSpan.innerText = car.collisions;
        }

        function resetSimulation() {
            car = {
                x: W/2,
                y: H - 100,
                angle: 0,
                speed: 0,
                alive: true,
                collisions: 0
            };
            obstacles = [];
            updateUI();
            statusSpan.innerText = "Driving";
        }

        function clearObstacles() {
            obstacles = [];
            updateUI();
        }

        function randomObstacles() {
            obstacles = [];
            for (let i = 0; i < 8; i++) {
                let x = Math.random() * (W - OBSTACLE_SIZE);
                let y = Math.random() * (H - OBSTACLE_SIZE - 50) + 50;
                obstacles.push({ x: x, y: y, w: OBSTACLE_SIZE, h: OBSTACLE_SIZE });
            }
            updateUI();
        }

        function castSensor(angleOffset) {
            let rad = car.angle + angleOffset;
            let dx = Math.cos(rad);
            let dy = Math.sin(rad);
            let x = car.x + CAR_WIDTH/2;
            let y = car.y + CAR_HEIGHT/2;
            let distance = SENSOR_LENGTH;
            for (let obs of obstacles) {
                let steps = 20;
                for (let i = 1; i <= steps; i++) {
                    let px = x + dx * (distance * i / steps);
                    let py = y + dy * (distance * i / steps);
                    if (px > obs.x && px < obs.x + obs.w && py > obs.y && py < obs.y + obs.h) {
                        distance = (distance * i / steps);
                        break;
                    }
                }
            }
            let edgeDistance = SENSOR_LENGTH;
            if (dx > 0) edgeDistance = Math.min(edgeDistance, (W - x) / dx);
            if (dx < 0) edgeDistance = Math.min(edgeDistance, -x / dx);
            if (dy > 0) edgeDistance = Math.min(edgeDistance, (H - y) / dy);
            if (dy < 0) edgeDistance = Math.min(edgeDistance, -y / dy);
            distance = Math.min(distance, edgeDistance);
            return distance;
        }

        function aiControl() {
            if (!car.alive) return;
            let sensors = [];
            let angles = [-0.8, -0.4, 0, 0.4, 0.8];
            for (let i = 0; i < SENSOR_COUNT; i++) {
                let dist = castSensor(angles[i]);
                sensors.push(dist);
            }
            let threats = sensors.map(d => Math.max(0, (SENSOR_LENGTH - d) / SENSOR_LENGTH));
            let leftThreat = threats[0] + threats[1];
            let rightThreat = threats[3] + threats[4];
            let steer = (rightThreat - leftThreat) * 0.8;
            let frontThreat = threats[2];
            let speedTarget = MAX_SPEED * (1 - frontThreat * 0.8);
            car.speed += (speedTarget - car.speed) * 0.1;
            car.angle += steer * TURN_SPEED;
            car.angle = Math.min(Math.max(car.angle, -Math.PI/3), Math.PI/3);
        }

        function updateCar() {
            if (!car.alive) return;
            let dx = Math.cos(car.angle) * car.speed;
            let dy = Math.sin(car.angle) * car.speed;
            car.x += dx;
            car.y += dy;
            if (car.x < 0 || car.x + CAR_WIDTH > W || car.y < 0 || car.y + CAR_HEIGHT > H) {
                car.alive = false;
                statusSpan.innerText = "Crashed (out of bounds)";
                return;
            }
            for (let i = 0; i < obstacles.length; i++) {
                let obs = obstacles[i];
                if (car.x < obs.x + obs.w && car.x + CAR_WIDTH > obs.x &&
                    car.y < obs.y + obs.h && car.y + CAR_HEIGHT > obs.y) {
                    car.alive = false;
                    car.collisions++;
                    statusSpan.innerText = "Crashed into obstacle!";
                    updateUI();
                    return;
                }
            }
        }

        function draw() {
            ctx.clearRect(0, 0, W, H);
            ctx.fillStyle = "#2c3e50";
            ctx.fillRect(0, 0, W, H);
            ctx.strokeStyle = "#ffcc00";
            ctx.lineWidth = 4;
            ctx.setLineDash([20, 30]);
            for (let y = 0; y < H; y += 50) {
                ctx.beginPath();
                ctx.moveTo(0, y);
                ctx.lineTo(W, y);
                ctx.stroke();
            }
            ctx.setLineDash([]);
            for (let obs of obstacles) {
                ctx.fillStyle = "#e74c3c";
                ctx.fillRect(obs.x, obs.y, obs.w, obs.h);
                ctx.fillStyle = "#c0392b";
                ctx.fillRect(obs.x+5, obs.y+5, obs.w-10, obs.h-10);
            }
            ctx.beginPath();
            ctx.strokeStyle = "#00ffcc";
            ctx.lineWidth = 1;
            let angles = [-0.8, -0.4, 0, 0.4, 0.8];
            for (let i = 0; i < SENSOR_COUNT; i++) {
                let rad = car.angle + angles[i];
                let dist = castSensor(angles[i]);
                let endX = car.x + CAR_WIDTH/2 + Math.cos(rad) * dist;
                let endY = car.y + CAR_HEIGHT/2 + Math.sin(rad) * dist;
                ctx.beginPath();
                ctx.moveTo(car.x + CAR_WIDTH/2, car.y + CAR_HEIGHT/2);
                ctx.lineTo(endX, endY);
                ctx.stroke();
            }
            ctx.fillStyle = "#2ecc71";
            ctx.fillRect(car.x, car.y, CAR_WIDTH, CAR_HEIGHT);
            ctx.fillStyle = "#ecf0f1";
            ctx.fillRect(car.x+5, car.y+2, 8, 8);
            ctx.fillRect(car.x+CAR_WIDTH-13, car.y+2, 8, 8);
            ctx.fillStyle = "#f1c40f";
            ctx.fillRect(car.x+CAR_WIDTH-5, car.y+5, 5, 5);
            ctx.fillRect(car.x+CAR_WIDTH-5, car.y+CAR_HEIGHT-10, 5, 5);
        }

        function gameLoop() {
            if (!car.alive) {
                draw();
                requestAnimationFrame(gameLoop);
                return;
            }
            aiControl();
            updateCar();
            draw();
            requestAnimationFrame(gameLoop);
        }

        canvas.addEventListener('click', (e) => {
            if (!car.alive) return;
            const rect = canvas.getBoundingClientRect();
            const scaleX = canvas.width / rect.width;
            const scaleY = canvas.height / rect.height;
            let mouseX = (e.clientX - rect.left) * scaleX;
            let mouseY = (e.clientY - rect.top) * scaleY;
            obstacles.push({ x: mouseX - OBSTACLE_SIZE/2, y: mouseY - OBSTACLE_SIZE/2, w: OBSTACLE_SIZE, h: OBSTACLE_SIZE });
            updateUI();
        });

        document.getElementById('resetBtn').addEventListener('click', () => { resetSimulation(); });
        document.getElementById('clearObstaclesBtn').addEventListener('click', () => { clearObstacles(); });
        document.getElementById('randomObstaclesBtn').addEventListener('click', () => { randomObstacles(); });

        resetSimulation();
        gameLoop();
    })();
</script>
"""

st.components.v1.html(sim_html, height=560, scrolling=False)

st.markdown("""
---
### 🧠 How Vectra AI works
""")

# --- Illustrative diagram (SVG) ---
st.markdown("""
<div class="sensor-diagram">
    <svg width="100%" height="200" viewBox="0 0 600 150" xmlns="http://www.w3.org/2000/svg">
        <!-- Car body -->
        <rect x="250" y="100" width="100" height="40" rx="8" fill="#2ecc71" stroke="#1e8449" stroke-width="2"/>
        <!-- Car windows -->
        <rect x="260" y="108" width="20" height="15" fill="#ecf0f1" rx="3"/>
        <rect x="320" y="108" width="20" height="15" fill="#ecf0f1" rx="3"/>
        <!-- Wheels -->
        <circle cx="270" cy="140" r="10" fill="#333"/>
        <circle cx="330" cy="140" r="10" fill="#333"/>
        <!-- Sensors (rays) -->
        <line x1="300" y1="100" x2="300" y2="20" stroke="#00ffcc" stroke-width="2" stroke-dasharray="4,2"/>
        <line x1="280" y1="105" x2="240" y2="30" stroke="#00ffcc" stroke-width="2" stroke-dasharray="4,2"/>
        <line x1="320" y1="105" x2="360" y2="30" stroke="#00ffcc" stroke-width="2" stroke-dasharray="4,2"/>
        <line x1="260" y1="110" x2="210" y2="50" stroke="#00ffcc" stroke-width="2" stroke-dasharray="4,2"/>
        <line x1="340" y1="110" x2="390" y2="50" stroke="#00ffcc" stroke-width="2" stroke-dasharray="4,2"/>
        <!-- Labels -->
        <text x="290" y="15" fill="#00ffcc" font-size="12">Front</text>
        <text x="220" y="35" fill="#00ffcc" font-size="12">Left</text>
        <text x="370" y="35" fill="#00ffcc" font-size="12">Right</text>
        <text x="180" y="60" fill="#00ffcc" font-size="12">Far left</text>
        <text x="410" y="60" fill="#00ffcc" font-size="12">Far right</text>
    </svg>
    <p><em>Diagram: The car uses 5 sensors (rays) to detect obstacles. The AI steers away from the closest one.</em></p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
- The car has **5 sensors** (rays) pointing forward at different angles.
- Each sensor measures the distance to the nearest obstacle or screen edge.
- The AI steers away from the side where the closest obstacle is detected.
- Speed is reduced when the front sensor is very close to an obstacle.
- This is a simplified **rule‑based autonomous driving** system – similar to early self‑driving experiments.

### 🎮 Controls

- **Click** anywhere on the canvas to add an obstacle.
- Use the buttons to reset, clear, or add random obstacles.
- The car will try to avoid them automatically.

### 🚀 Future neural network integration

**No extra software is needed to run Vectra AI.** It works immediately.

However, if you later want to replace the rule‑based AI with a **neural network** that learns from data, you would need a separate training environment (like TensorFlow, PyTorch, or a reinforcement learning framework). You could then replace the `aiControl()` function with a model that predicts steering and throttle based on sensor inputs.

Vectra AI is fully standalone – enjoy driving!

---
<div class="footer">
    Vectra AI built by <strong>Gesner Deslandes</strong> – GlobalInternet.py
</div>
""")
