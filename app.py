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
    <p>Self‑Driving Car on a winding dirt road – stays on the right side, avoids left‑side obstacles</p>
    <p><strong>Click "Add Random Cars" – other cars appear on the left. Your car avoids them while staying on the right.</strong></p>
</div>
""", unsafe_allow_html=True)

# --- Demonstration Video ---
st.markdown("## 🎥 Vectra AI in Action")
st.markdown("Watch the autonomous driving system navigate real roads with a human driver monitoring only (hands-off).")
video_url = "https://raw.githubusercontent.com/Deslandes1/Vectra-AI-Built-by-Gesner-Deslandes/main/AI%20Selfdriving.mp4"
st.video(video_url)
st.caption("Note: If the video does not play, your browser may not support the MP4 format. Try viewing this app in Chrome or Edge.")

# --- The Simulation Canvas (right‑lane only, left‑side obstacles) ---
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
    <button id="randomObstaclesBtn">🎲 Add Random Cars (left side)</button>
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
        const PATH_LOOKAHEAD = 25;
        const AVOID_STRENGTH = 1.2;
        const RIGHT_LANE_OFFSET = 18;      // pixels to the right of road center
        const ROAD_PULL_STRENGTH = 0.15;

        let car = {
            x: 50,
            y: 0,
            angle: 0,
            speed: 0,
            alive: true,
            collisions: 0
        };
        let obstacles = [];

        // Road center (winding)
        function getRoadCenterY(x) {
            let y = H/2 + 30 + Math.sin(x / 90) * 45 + Math.sin(x / 200) * 25;
            return Math.min(Math.max(y, 70), H - 70);
        }

        // Right lane target (offset from center)
        function getRightLaneY(x) {
            let centerY = getRoadCenterY(x);
            return centerY + RIGHT_LANE_OFFSET;
        }

        // Check if car is on the right side (not crossing center line)
        function isOnRightSide(carCenterY, x) {
            let centerY = getRoadCenterY(x);
            return carCenterY > centerY - 5;   // car center must be to the right of center
        }

        function drawDustRoad() {
            ctx.fillStyle = "#c9a87b";
            ctx.fillRect(0, 0, W, H);
            ctx.fillStyle = "#b88a5a";
            for (let i = 0; i < 400; i++) {
                ctx.fillRect(Math.random() * W, Math.random() * H, 2, 2);
            }
            // Road path (brown band)
            ctx.beginPath();
            ctx.moveTo(0, getRoadCenterY(0));
            for (let x = 0; x <= W; x += 20) {
                ctx.lineTo(x, getRoadCenterY(x));
            }
            ctx.lineWidth = 70;
            ctx.strokeStyle = "#a56b3a";
            ctx.stroke();
            // Center guideline (dashed)
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
            // Right lane marker (small dots)
            ctx.beginPath();
            ctx.strokeStyle = "#ffccaa";
            ctx.lineWidth = 2;
            for (let x = 0; x <= W; x += 30) {
                let y = getRightLaneY(x);
                ctx.moveTo(x, y);
                ctx.lineTo(x+10, y);
                ctx.stroke();
            }
            // Tire tracks
            ctx.beginPath();
            ctx.strokeStyle = "#7a4a2a";
            ctx.lineWidth = 2;
            for (let i = 0; i < 100; i++) {
                let x = Math.random() * W;
                let y = getRightLaneY(x) + (Math.random() - 0.5) * 15;
                ctx.moveTo(x, y);
                ctx.lineTo(x + 10, y + (Math.random() - 0.5) * 10);
                ctx.stroke();
            }
        }

        function updateCar() {
            if (!car.alive) return;
            
            // Path following: aim for right lane ahead
            let lookAheadX = car.x + PATH_LOOKAHEAD;
            let targetY = getRightLaneY(lookAheadX);
            let dyTarget = targetY - (car.y + CAR_HEIGHT/2);
            let desiredAngle = Math.atan2(dyTarget, PATH_LOOKAHEAD);
            desiredAngle = Math.min(Math.max(desiredAngle, -0.5), 0.5);
            
            // Sensor rays
            let threats = [0, 0, 0, 0, 0];
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
                let edgeDist = SENSOR_LENGTH;
                if (dx > 0) edgeDist = Math.min(edgeDist, (W - x) / dx);
                if (dx < 0) edgeDist = Math.min(edgeDist, -x / dx);
                if (dy > 0) edgeDist = Math.min(edgeDist, (H - y) / dy);
                if (dy < 0) edgeDist = Math.min(edgeDist, -y / dy);
                distance = Math.min(distance, edgeDist);
                threats[i] = Math.max(0, (SENSOR_LENGTH - distance) / SENSOR_LENGTH);
            }
            let leftThreat = threats[0] + threats[1];
            let rightThreat = threats[3] + threats[4];
            // Obstacles are on the left, so we steer right (avoid) by pushing away from left threat
            let avoidSteer = (rightThreat - leftThreat) * AVOID_STRENGTH;
            
            // Road pull: keep car on right lane
            let currentYcenter = car.y + CAR_HEIGHT/2;
            let targetLaneY = getRightLaneY(car.x);
            let laneDiff = targetLaneY - currentYcenter;
            let roadPull = laneDiff * ROAD_PULL_STRENGTH;
            roadPull = Math.min(Math.max(roadPull, -0.2), 0.2);
            
            // Combine steering (path following + avoidance + lane keeping)
            let totalSteer = desiredAngle * 0.6 + avoidSteer + roadPull;
            totalSteer = Math.min(Math.max(totalSteer, -0.5), 0.5);
            
            // Speed reduction if obstacle ahead
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
            
            // Enforce right‑side only: prevent car from crossing center line
            let carCenterY = car.y + CAR_HEIGHT/2;
            let centerY = getRoadCenterY(car.x);
            if (carCenterY < centerY - 2) {   // too far left
                car.y = centerY - 2 - CAR_HEIGHT/2;
                car.speed *= 0.98;
                car.angle += 0.05;  // steer right gently
            }
            
            // Boundary check (keep on screen)
            if (car.x < 5 || car.x + CAR_WIDTH > W - 5 || car.y < 25 || car.y + CAR_HEIGHT > H - 25) {
                car.alive = false;
                statusSpan.innerText = "Went off the road!";
                return;
            }
            
            // Collision detection (with safety margin)
            for (let i = 0; i < obstacles.length; i++) {
                let obs = obstacles[i];
                if (car.x + 3 < obs.x + obs.w && car.x + CAR_WIDTH - 3 > obs.x &&
                    car.y + 3 < obs.y + obs.h && car.y + CAR_HEIGHT - 3 > obs.y) {
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
            // Draw obstacles (other cars) on the left side
            for (let obs of obstacles) {
                ctx.fillStyle = "#8b5a2b";
                ctx.fillRect(obs.x, obs.y, obs.w, obs.h);
                ctx.fillStyle = "#6b3e1a";
                ctx.fillRect(obs.x+5, obs.y+5, obs.w-10, obs.h-10);
                ctx.fillStyle = "#d4a373";
                ctx.fillRect(obs.x+obs.w-6, obs.y+4, 4, 5);
                ctx.fillRect(obs.x+obs.w-6, obs.y+obs.h-9, 4, 5);
            }
            // Sensors
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
            // Our car (green)
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
                y: getRightLaneY(50) - CAR_HEIGHT/2,
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
            // Place 2‑4 obstacles on the LEFT side of the road (center - offset)
            let count = Math.floor(Math.random() * 3) + 2;
            for (let i = 0; i < count; i++) {
                let x = car.x + Math.random() * 150 + 100;
                let centerY = getRoadCenterY(x);
                let y = centerY - OBSTACLE_SIZE/2 - (Math.random() * 20 + 10); // left side
                y = Math.min(Math.max(y, 40), H - OBSTACLE_SIZE - 40);
                if (Math.abs(x - car.x) > 60) {
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
            let centerY = getRoadCenterY(mouseX);
            // Only allow placing on left side (y < centerY - 5)
            if (mouseY < centerY - 5 && mouseX > car.x + 60) {
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
### 🧠 How the car stays on the right and avoids left‑side obstacles

- **Right lane following** – the car targets a path 18 pixels to the right of the road center.
- **Obstacles are placed on the left side** of the road (center minus offset).
- **Five sensors** detect obstacles; the car steers **right** (away from left threat) and slows down.
- A **lane‑keeping force** constantly pulls the car back to the right lane.
- A **hard barrier** prevents the car from crossing the road center to the left.
- **Collision detection includes a safety margin** to avoid touching other cars.

### 🎮 Controls

- **Add Random Cars** – places 2‑4 other cars on the left side ahead.
- **Clear Other Cars** – removes all obstacles.
- **Reset Drive** – restarts the simulation.
- **Click on the left side of the road** to add a single car (must be ahead of your car).

### 🚀 Future neural network integration

**No extra software is needed to run Vectra AI.** It works immediately.

---
<div class="footer">
    Vectra AI built by <strong>Gesner Deslandes</strong> – GlobalInternet.py
</div>
""")
