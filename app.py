import streamlit as st

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
    <p>Self‑Driving Car Simulator – two‑lane road, right‑lane driving, obstacle avoidance</p>
    <p><strong>Click on the canvas to add other cars (obstacles) on the left lane. Watch your car avoid them.</strong></p>
</div>
""", unsafe_allow_html=True)

# --- Demonstration Video ---
st.markdown("## 🎥 Vectra AI in Action")
st.markdown("Watch the autonomous driving system navigate real roads with a human driver monitoring only (hands-off).")
video_url = "https://raw.githubusercontent.com/Deslandes1/Vectra-AI-Built-by-Gesner-Deslandes/main/AI%20Selfdriving.mp4"
st.video(video_url)
st.caption("Note: If the video does not play, your browser may not support the MP4 format. Try viewing this app in Chrome or Edge.")

# --- The Simulation Canvas (two‑lane road, right‑lane car, left‑lane obstacles) ---
sim_html = """
<canvas id="gameCanvas" width="900" height="500" tabindex="0" style="outline: none; cursor: crosshair;"></canvas>
<div class="info">
    🧠 AI Status: <span id="status">Driving</span> &nbsp;|&nbsp;
    🚗 Other cars: <span id="obstacleCount">0</span> &nbsp;|&nbsp;
    💥 Collisions: <span id="collisionCount">0</span>
</div>
<div style="text-align: center; margin-top: 10px;">
    <button id="resetBtn">🔄 Reset Simulator</button>
    <button id="clearObstaclesBtn">🗑️ Clear All Other Cars</button>
    <button id="randomObstaclesBtn">🎲 Random Other Cars (left lane)</button>
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
        const OBSTACLE_SIZE = 30;   // other cars are same size
        const SENSOR_LENGTH = 130;
        const SENSOR_COUNT = 5;
        const MAX_SPEED = 3.8;
        const TURN_SPEED = 0.12;
        const LANE_KEEP_STRENGTH = 0.7;

        // Car starts in the right lane (y ~ 80% of height)
        let car = {
            x: 60,
            y: H - 100,
            angle: 0,
            speed: 0,
            alive: true,
            collisions: 0
        };
        // Obstacles (other cars) should be placed in the left lane (y roughly between 100 and 250)
        let obstacles = [];

        function updateUI() {
            obstacleCountSpan.innerText = obstacles.length;
            collisionCountSpan.innerText = car.collisions;
        }

        function resetSimulation() {
            car = {
                x: 60,
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
            // Place obstacles only in the left lane (y between 80 and 250)
            for (let i = 0; i < 10; i++) {
                let x, y;
                let valid = false;
                let attempts = 0;
                while (!valid && attempts < 30) {
                    x = Math.random() * (W - OBSTACLE_SIZE - 100) + 100;
                    y = Math.random() * (H - OBSTACLE_SIZE - 250) + 80;
                    // Ensure y is within left lane (upper half)
                    if (y < 250 && y > 60) {
                        // Also avoid placing obstacles too close to the car's starting area
                        let distToCarStart = Math.hypot(x - 60, y - (H-100));
                        if (distToCarStart > 100) {
                            valid = true;
                        }
                    }
                    attempts++;
                }
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
            let avoidSteer = (rightThreat - leftThreat) * 0.9;
            let laneSteer = -car.angle * LANE_KEEP_STRENGTH;
            let totalSteer = avoidSteer + laneSteer;
            totalSteer = Math.min(Math.max(totalSteer, -0.5), 0.5);
            
            let frontThreat = threats[2];
            let speedTarget = MAX_SPEED * (1 - frontThreat * 0.9);
            car.speed += (speedTarget - car.speed) * 0.1;
            car.angle += totalSteer * TURN_SPEED;
            car.angle = Math.min(Math.max(car.angle, -Math.PI/2.5), Math.PI/2.5);
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
                    statusSpan.innerText = "Collision with other car!";
                    updateUI();
                    return;
                }
            }
        }

        function draw() {
            ctx.clearRect(0, 0, W, H);
            // Road background
            ctx.fillStyle = "#2c3e50";
            ctx.fillRect(0, 0, W, H);
            
            // Draw lane separator (yellow dashed line)
            let laneSeparatorY = H / 2 + 20;
            ctx.beginPath();
            ctx.strokeStyle = "#ffcc00";
            ctx.lineWidth = 4;
            ctx.setLineDash([20, 30]);
            ctx.moveTo(0, laneSeparatorY);
            ctx.lineTo(W, laneSeparatorY);
            ctx.stroke();
            ctx.setLineDash([]);
            
            // Road edge lines
            ctx.beginPath();
            ctx.strokeStyle = "#ffffff";
            ctx.lineWidth = 2;
            ctx.setLineDash([]);
            ctx.moveTo(0, 30);
            ctx.lineTo(W, 30);
            ctx.stroke();
            ctx.moveTo(0, H-30);
            ctx.lineTo(W, H-30);
            ctx.stroke();
            
            // Draw other cars (obstacles) as red cars
            for (let obs of obstacles) {
                ctx.fillStyle = "#e74c3c";
                ctx.fillRect(obs.x, obs.y, obs.w, obs.h);
                ctx.fillStyle = "#c0392b";
                ctx.fillRect(obs.x+5, obs.y+5, obs.w-10, obs.h-10);
                // headlights
                ctx.fillStyle = "#f1c40f";
                ctx.fillRect(obs.x+obs.w-5, obs.y+5, 5, 5);
                ctx.fillRect(obs.x+obs.w-5, obs.y+obs.h-10, 5, 5);
            }
            
            // Draw sensors (rays)
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
            
            // Draw our car (green)
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
            // Only allow placing obstacles in the left lane (y between 60 and 250)
            if (mouseY > 60 && mouseY < 250) {
                let distToCar = Math.hypot(mouseX - (car.x + CAR_WIDTH/2), mouseY - (car.y + CAR_HEIGHT/2));
                if (distToCar > 60) {
                    obstacles.push({ x: mouseX - OBSTACLE_SIZE/2, y: mouseY - OBSTACLE_SIZE/2, w: OBSTACLE_SIZE, h: OBSTACLE_SIZE });
                    updateUI();
                }
            }
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
### 🧠 How Vectra AI works (two‑lane version)

- The road has two lanes: **left lane (top)** for other cars, **right lane (bottom)** for your car.
- Your car is green, other cars are red.
- The car uses **5 sensors** to detect obstacles (other cars or road edges).
- The AI **combines obstacle avoidance** (steer away from the closest red car) with **lane keeping** (stay straight and centered in the right lane).
- Speed is reduced when the front sensor is very close to an obstacle.
- The car will steer around other cars and then return to its lane.

### 🎮 Controls

- **Click** on the left lane (upper half) to add another car (obstacle).
- Use the buttons to reset, clear all other cars, or add random other cars.
- Your car will automatically avoid them while staying on the right side of the road.

### 🚀 Future neural network integration

**No extra software is needed to run Vectra AI.** It works immediately.

However, if you later want to replace the rule‑based AI with a **neural network** that learns from data, you would need a separate training environment (like TensorFlow, PyTorch, or a reinforcement learning framework). You could then replace the `aiControl()` function with a model that predicts steering and throttle based on sensor inputs.

Vectra AI is fully standalone – enjoy driving!

---
<div class="footer">
    Vectra AI built by <strong>Gesner Deslandes</strong> – GlobalInternet.py
</div>
""")
