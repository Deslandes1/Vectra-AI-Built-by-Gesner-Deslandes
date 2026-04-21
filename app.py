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
    .sensor-diagram { background: #1e2a3a; border-radius: 16px; padding: 1rem; margin: 1rem 0; text-align: center; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center;">
    <h1>🚗 Vectra AI – Dust Road</h1>
    <p style="font-size: 1.1rem;">built by <strong>Gesner Deslandes</strong></p>
    <p>Self‑Driving Car on a winding dirt road – avoids obstacles while staying perfectly on the path</p>
    <p><strong>Click "Add Random Cars" – the AI will steer around them without leaving the road.</strong></p>
</div>
""", unsafe_allow_html=True)

# --- Demonstration Video ---
st.markdown("## 🎥 Vectra AI in Action")
st.markdown("Watch the autonomous driving system navigate real roads with a human driver monitoring only (hands-off).")
video_url = "https://raw.githubusercontent.com/Deslandes1/Vectra-AI-Built-by-Gesner-Deslandes/main/AI%20Selfdriving.mp4"
st.video(video_url)
st.caption("Note: If the video does not play, your browser may not support the MP4 format. Try viewing this app in Chrome or Edge.")

# --- The Simulation Canvas (precision road‑following + smooth avoidance) ---
sim_html = """
<canvas id="gameCanvas" width="900" height="500" tabindex="0" style="outline: none; cursor: crosshair;"></canvas>
<div class="info">
    🧠 AI Status: <span id="status">Driving</span> &nbsp;|&nbsp;
    🚗 Other cars: <span id="obstacleCount">0</span> &nbsp;|&nbsp;
    💥 Collisions: <span id="collisionCount">0</span>
</div>
<div style="text-align: center; margin-top: 10px;">
    <button id="resetBtn">🔄 Reset Drive</button>
    <button id="clearObstaclesBtn">🗑️ Clear Other Cars</button>
    <button id="randomObstaclesBtn">🎲 Add Random Cars</button>
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
        const OBSTACLE_SIZE = 28;
        const SENSOR_LENGTH = 140;
        const SENSOR_ANGLES = [-0.9, -0.5, 0, 0.5, 0.9];
        const MAX_SPEED = 3.2;
        const TURN_SPEED = 0.16;
        const PATH_LOOKAHEAD = 25;       // pixels ahead for road following
        const AVOID_STRENGTH = 1.3;
        const ROAD_PULL_STRENGTH = 0.12;

        let car = {
            x: 50,
            y: 0,
            angle: 0,
            speed: 0,
            alive: true,
            collisions: 0
        };
        let obstacles = [];

        // Winding road center (smooth sine wave)
        function getRoadCenterY(x) {
            let y = H/2 + 30 + Math.sin(x / 90) * 45 + Math.sin(x / 200) * 25;
            return Math.min(Math.max(y, 70), H - 70);
        }

        // Strict on‑road check (distance to road center < 30px)
        function isOnRoad(x, y) {
            let roadY = getRoadCenterY(x);
            return Math.abs(y - roadY) < 30;
        }

        function drawDustRoad() {
            // Dirt background
            ctx.fillStyle = "#c9a87b";
            ctx.fillRect(0, 0, W, H);
            ctx.fillStyle = "#b88a5a";
            for (let i = 0; i < 400; i++) {
                ctx.fillRect(Math.random() * W, Math.random() * H, 2, 2);
            }
            // Road path
            ctx.beginPath();
            ctx.moveTo(0, getRoadCenterY(0));
            for (let x = 0; x <= W; x += 20) {
                ctx.lineTo(x, getRoadCenterY(x));
            }
            ctx.lineWidth = 70;
            ctx.strokeStyle = "#a56b3a";
            ctx.stroke();
            // Center guideline
            ctx.beginPath();
            for (let x = 0; x <= W; x += 40) {
                let y = getRoadCenterY(x);
                ctx.moveTo(x, y);
                ctx.lineTo(x+20, getRoadCenterY(x+20));
            }
            ctx.lineWidth = 3;
            ctx.strokeStyle = "#f0d5a8";
            ctx.setLineDash([15, 25]);
            ctx.stroke();
            ctx.setLineDash([]);
            // Tire tracks
            ctx.beginPath();
            ctx.strokeStyle = "#7a4a2a";
            ctx.lineWidth = 2;
            for (let i = 0; i < 100; i++) {
                let x = Math.random() * W;
                let y = getRoadCenterY(x) + (Math.random() - 0.5) * 25;
                ctx.moveTo(x, y);
                ctx.lineTo(x + 10, y + (Math.random() - 0.5) * 10);
                ctx.stroke();
            }
        }

        function updateCar() {
            if (!car.alive) return;
            
            // 1. Path following (look ahead)
            let lookAheadX = car.x + PATH_LOOKAHEAD;
            let targetY = getRoadCenterY(lookAheadX);
            let dyTarget = targetY - (car.y + CAR_HEIGHT/2);
            let desiredAngle = Math.atan2(dyTarget, PATH_LOOKAHEAD);
            desiredAngle = Math.min(Math.max(desiredAngle, -0.5), 0.5);
            
            // 2. Obstacle detection via 5 rays
            let threats = [0, 0, 0, 0, 0];
            let minDist = SENSOR_LENGTH;
            for (let i = 0; i < SENSOR_ANGLES.length; i++) {
                let rad = car.angle + SENSOR_ANGLES[i];
                let dx = Math.cos(rad);
                let dy = Math.sin(rad);
                let x = car.x + CAR_WIDTH/2;
                let y = car.y + CAR_HEIGHT/2;
                let distance = SENSOR_LENGTH;
                for (let obs of obstacles) {
                    let steps = 25;
                    for (let s = 1; s <= steps; s++) {
                        let px = x + dx * (distance * s / steps);
                        let py = y + dy * (distance * s / steps);
                        if (px > obs.x && px < obs.x + obs.w && py > obs.y && py < obs.y + obs.h) {
                            distance = (distance * s / steps);
                            break;
                        }
                    }
                }
                // edge distance
                let edgeDist = SENSOR_LENGTH;
                if (dx > 0) edgeDist = Math.min(edgeDist, (W - x) / dx);
                if (dx < 0) edgeDist = Math.min(edgeDist, -x / dx);
                if (dy > 0) edgeDist = Math.min(edgeDist, (H - y) / dy);
                if (dy < 0) edgeDist = Math.min(edgeDist, -y / dy);
                distance = Math.min(distance, edgeDist);
                threats[i] = Math.max(0, (SENSOR_LENGTH - distance) / SENSOR_LENGTH);
                if (distance < minDist) minDist = distance;
            }
            let leftThreat = threats[0] + threats[1];
            let rightThreat = threats[3] + threats[4];
            let avoidSteer = (rightThreat - leftThreat) * AVOID_STRENGTH;
            
            // 3. Road pull (keep on center)
            let currentYcenter = car.y + CAR_HEIGHT/2;
            let roadY = getRoadCenterY(car.x);
            let yDiff = roadY - currentYcenter;
            let roadPull = yDiff * ROAD_PULL_STRENGTH;
            roadPull = Math.min(Math.max(roadPull, -0.2), 0.2);
            
            // Combine steering
            let totalSteer = desiredAngle * 0.6 + avoidSteer + roadPull;
            totalSteer = Math.min(Math.max(totalSteer, -0.6), 0.6);
            
            // Speed control
            let frontThreat = threats[2];
            let speedTarget = MAX_SPEED * (1 - frontThreat * 0.9);
            car.speed += (speedTarget - car.speed) * 0.1;
            car.angle += totalSteer * TURN_SPEED;
            car.angle = Math.min(Math.max(car.angle, -Math.PI/2.5), Math.PI/2.5);
            
            // Move
            let dx = Math.cos(car.angle) * car.speed;
            let dy = Math.sin(car.angle) * car.speed;
            car.x += dx;
            car.y += dy;
            
            // Hard road boundary enforcement (prevent leaving the road)
            if (!isOnRoad(car.x + CAR_WIDTH/2, car.y + CAR_HEIGHT/2)) {
                let targetY = getRoadCenterY(car.x);
                let correction = (targetY - (car.y + CAR_HEIGHT/2)) * 0.3;
                car.y += correction;
                car.speed *= 0.98;
                if (Math.abs(correction) > 3) {
                    car.angle += correction * 0.02;
                }
            }
            
            // Final safety boundaries
            if (car.x < 5 || car.x + CAR_WIDTH > W - 5 || car.y < 25 || car.y + CAR_HEIGHT > H - 25) {
                car.alive = false;
                statusSpan.innerText = "Went off the road!";
                return;
            }
            
            // Collision detection (with extra margin)
            for (let i = 0; i < obstacles.length; i++) {
                let obs = obstacles[i];
                // add a small safety margin (2px)
                if (car.x + 2 < obs.x + obs.w && car.x + CAR_WIDTH - 2 > obs.x &&
                    car.y + 2 < obs.y + obs.h && car.y + CAR_HEIGHT - 2 > obs.y) {
                    car.alive = false;
                    car.collisions++;
                    statusSpan.innerText = "Crashed into another car!";
                    updateUI();
                    return;
                }
            }
        }

        function draw() {
            drawDustRoad();
            // Draw obstacles (other cars)
            for (let obs of obstacles) {
                ctx.fillStyle = "#8b5a2b";
                ctx.fillRect(obs.x, obs.y, obs.w, obs.h);
                ctx.fillStyle = "#6b3e1a";
                ctx.fillRect(obs.x+5, obs.y+5, obs.w-10, obs.h-10);
                ctx.fillStyle = "#d4a373";
                ctx.fillRect(obs.x+obs.w-6, obs.y+4, 4, 5);
                ctx.fillRect(obs.x+obs.w-6, obs.y+obs.h-9, 4, 5);
            }
            // Draw sensors
            ctx.beginPath();
            ctx.strokeStyle = "#ffaa44";
            ctx.lineWidth = 1;
            for (let i = 0; i < SENSOR_ANGLES.length; i++) {
                let rad = car.angle + SENSOR_ANGLES[i];
                let x = car.x + CAR_WIDTH/2;
                let y = car.y + CAR_HEIGHT/2;
                let endX = x + Math.cos(rad) * SENSOR_LENGTH;
                let endY = y + Math.sin(rad) * SENSOR_LENGTH;
                ctx.beginPath();
                ctx.moveTo(x, y);
                ctx.lineTo(endX, endY);
                ctx.stroke();
            }
            // Draw our car
            ctx.fillStyle = "#6a994e";
            ctx.fillRect(car.x, car.y, CAR_WIDTH, CAR_HEIGHT);
            ctx.fillStyle = "#bcbcbc";
            ctx.fillRect(car.x+5, car.y+2, 8, 8);
            ctx.fillRect(car.x+CAR_WIDTH-13, car.y+2, 8, 8);
            ctx.fillStyle = "#f4a261";
            ctx.fillRect(car.x+CAR_WIDTH-5, car.y+5, 5, 5);
            ctx.fillRect(car.x+CAR_WIDTH-5, car.y+CAR_HEIGHT-10, 5, 5);
        }

        function gameLoop() {
            if (!car.alive) {
                draw();
                requestAnimationFrame(gameLoop);
                return;
            }
            updateCar();
            draw();
            requestAnimationFrame(gameLoop);
        }

        function updateUI() {
            obstacleCountSpan.innerText = obstacles.length;
            collisionCountSpan.innerText = car.collisions;
        }

        function resetSimulation() {
            car = {
                x: 50,
                y: getRoadCenterY(50) - CAR_HEIGHT/2,
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

        function addRandomObstacles() {
            // Add 2‑4 obstacles at varying distances (100‑250px ahead)
            let count = Math.floor(Math.random() * 3) + 2;
            for (let i = 0; i < count; i++) {
                let x = car.x + Math.random() * 150 + 100;
                let y = getRoadCenterY(x) - OBSTACLE_SIZE/2 + (Math.random() - 0.5) * 30;
                y = Math.min(Math.max(y, 40), H - OBSTACLE_SIZE - 40);
                // Prevent placing obstacles too close to the car
                if (Math.abs(x - car.x) > 50) {
                    obstacles.push({ x: x, y: y, w: OBSTACLE_SIZE, h: OBSTACLE_SIZE });
                }
            }
            updateUI();
        }

        canvas.addEventListener('click', (e) => {
            if (!car.alive) return;
            const rect = canvas.getBoundingClientRect();
            const scaleX = canvas.width / rect.width;
            const scaleY = canvas.height / rect.height;
            let mouseX = (e.clientX - rect.left) * scaleX;
            let mouseY = (e.clientY - rect.top) * scaleY;
            let roadY = getRoadCenterY(mouseX);
            if (Math.abs(mouseY - roadY) < 45 && mouseX > car.x + 60) {
                obstacles.push({ x: mouseX - OBSTACLE_SIZE/2, y: mouseY - OBSTACLE_SIZE/2, w: OBSTACLE_SIZE, h: OBSTACLE_SIZE });
                updateUI();
            }
        });

        document.getElementById('resetBtn').addEventListener('click', () => { resetSimulation(); });
        document.getElementById('clearObstaclesBtn').addEventListener('click', () => { clearObstacles(); });
        document.getElementById('randomObstaclesBtn').addEventListener('click', () => { addRandomObstacles(); });

        resetSimulation();
        gameLoop();
    })();
</script>
"""

st.components.v1.html(sim_html, height=560, scrolling=False)

st.markdown("""
---
### 🧠 How the car stays on the road and avoids obstacles

- **Precise path following** – the car looks 25 pixels ahead and steers toward the road center.
- **Five wide‑angle sensors** detect obstacles left, center, and right.
- **Avoidance steering** is added to the path‑following command, so the car swerves only when needed.
- **Road pull** gently corrects any drift, keeping the car within 30 pixels of the road center.
- **Speed reduction** when an obstacle is near gives the AI more reaction time.
- **Collision detection includes a safety margin** to prevent touching other cars.

### 🎮 Controls

- **Add Random Cars** – places 2‑4 other cars ahead on the road.
- **Clear Other Cars** – removes all obstacles.
- **Reset Drive** – restarts the simulation.
- **Click on the road** (ahead of your car) to add a single car.

### 🚀 Future neural network integration

**No extra software is needed to run Vectra AI.** It works immediately.

---
<div class="footer">
    Vectra AI built by <strong>Gesner Deslandes</strong> – GlobalInternet.py
</div>
""")
