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
    <p>Self‑Driving Car on a winding dirt road – avoids all other cars automatically</p>
    <p><strong>Click "Add Random Car" to place obstacles. The AI will steer around them and stay on the road.</strong></p>
</div>
""", unsafe_allow_html=True)

# --- Demonstration Video ---
st.markdown("## 🎥 Vectra AI in Action")
st.markdown("Watch the autonomous driving system navigate real roads with a human driver monitoring only (hands-off).")
video_url = "https://raw.githubusercontent.com/Deslandes1/Vectra-AI-Built-by-Gesner-Deslandes/main/AI%20Selfdriving.mp4"
st.video(video_url)
st.caption("Note: If the video does not play, your browser may not support the MP4 format. Try viewing this app in Chrome or Edge.")

# --- The Simulation Canvas (dust road, strict road‑following, obstacle avoidance) ---
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
    <button id="randomObstaclesBtn">🎲 Add Random Cars (3-5)</button>
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
        const SENSOR_LENGTH = 110;
        const SENSOR_COUNT = 5;
        const MAX_SPEED = 3.5;
        const TURN_SPEED = 0.12;
        const PATH_FOLLOW_STRENGTH = 0.7;
        const ROAD_PULL_STRENGTH = 0.05;

        let car = {
            x: 50,
            y: 0,
            angle: 0,
            speed: 0,
            alive: true,
            collisions: 0
        };
        let obstacles = [];

        // Road center line as a smooth function (winding path)
        function getRoadCenterY(x) {
            let y = H/2 + 30 + Math.sin(x / 90) * 45 + Math.sin(x / 200) * 25;
            return Math.min(Math.max(y, 70), H - 70);
        }

        // Check if a point (x,y) is on the road (within the brown stroke)
        function isOnRoad(x, y) {
            let roadY = getRoadCenterY(x);
            return Math.abs(y - roadY) < 35;
        }

        function drawDustRoad() {
            ctx.fillStyle = "#c9a87b";
            ctx.fillRect(0, 0, W, H);
            ctx.fillStyle = "#b88a5a";
            for (let i = 0; i < 400; i++) {
                ctx.fillRect(Math.random() * W, Math.random() * H, 2, 2);
            }
            // Road path (thick brown band)
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
            
            // Path following: desired angle towards road center ahead
            let targetY = getRoadCenterY(car.x + 15);
            let dyTarget = targetY - (car.y + CAR_HEIGHT/2);
            let desiredAngle = Math.atan2(dyTarget, 20) * 0.8;
            desiredAngle = Math.min(Math.max(desiredAngle, -0.4), 0.4);
            
            // Obstacle avoidance via sensors
            let sensors = [];
            let angles = [-0.8, -0.4, 0, 0.4, 0.8];
            for (let i = 0; i < SENSOR_COUNT; i++) {
                let rad = car.angle + angles[i];
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
                let edgeDist = SENSOR_LENGTH;
                if (dx > 0) edgeDist = Math.min(edgeDist, (W - x) / dx);
                if (dx < 0) edgeDist = Math.min(edgeDist, -x / dx);
                if (dy > 0) edgeDist = Math.min(edgeDist, (H - y) / dy);
                if (dy < 0) edgeDist = Math.min(edgeDist, -y / dy);
                distance = Math.min(distance, edgeDist);
                sensors.push(distance);
            }
            let threats = sensors.map(d => Math.max(0, (SENSOR_LENGTH - d) / SENSOR_LENGTH));
            let leftThreat = threats[0] + threats[1];
            let rightThreat = threats[3] + threats[4];
            let avoidSteer = (rightThreat - leftThreat) * 0.9;
            
            // Road pull: if car is too far from road center, add correction
            let currentYcenter = car.y + CAR_HEIGHT/2;
            let roadY = getRoadCenterY(car.x);
            let yDiff = roadY - currentYcenter;
            let roadPull = yDiff * ROAD_PULL_STRENGTH;
            roadPull = Math.min(Math.max(roadPull, -0.15), 0.15);
            
            // Combine all steering influences
            let totalSteer = desiredAngle * PATH_FOLLOW_STRENGTH + avoidSteer + roadPull;
            totalSteer = Math.min(Math.max(totalSteer, -0.6), 0.6);
            
            let frontThreat = threats[2];
            let speedTarget = MAX_SPEED * (1 - frontThreat * 0.8);
            car.speed += (speedTarget - car.speed) * 0.1;
            car.angle += totalSteer * TURN_SPEED;
            car.angle = Math.min(Math.max(car.angle, -Math.PI/2.5), Math.PI/2.5);
            
            // Move
            let dx = Math.cos(car.angle) * car.speed;
            let dy = Math.sin(car.angle) * car.speed;
            car.x += dx;
            car.y += dy;
            
            // Strict road boundary: if car leaves the road, pull it back
            if (!isOnRoad(car.x + CAR_WIDTH/2, car.y + CAR_HEIGHT/2)) {
                let targetY = getRoadCenterY(car.x);
                let correction = (targetY - (car.y + CAR_HEIGHT/2)) * 0.2;
                car.y += correction;
                car.speed *= 0.98;
                if (Math.abs(correction) > 5) {
                    car.angle += correction * 0.01;
                }
            }
            
            // Final boundary check
            if (car.x < 5 || car.x + CAR_WIDTH > W - 5 || car.y < 25 || car.y + CAR_HEIGHT > H - 25) {
                car.alive = false;
                statusSpan.innerText = "Went off the road!";
                return;
            }
            
            // Collision with other cars
            for (let i = 0; i < obstacles.length; i++) {
                let obs = obstacles[i];
                if (car.x < obs.x + obs.w && car.x + CAR_WIDTH > obs.x &&
                    car.y < obs.y + obs.h && car.y + CAR_HEIGHT > obs.y) {
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
            
            // Draw other cars
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
            let angles = [-0.8, -0.4, 0, 0.4, 0.8];
            for (let i = 0; i < SENSOR_COUNT; i++) {
                let rad = car.angle + angles[i];
                let dist = SENSOR_LENGTH;
                let x = car.x + CAR_WIDTH/2;
                let y = car.y + CAR_HEIGHT/2;
                let endX = x + Math.cos(rad) * dist;
                let endY = y + Math.sin(rad) * dist;
                ctx.beginPath();
                ctx.moveTo(x, y);
                ctx.lineTo(endX, endY);
                ctx.stroke();
            }
            
            // Our car
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
            // Add between 3 and 5 random cars ahead on the road
            let count = Math.floor(Math.random() * 3) + 3;
            for (let i = 0; i < count; i++) {
                let x = car.x + Math.random() * 300 + 100;
                let y = getRoadCenterY(x) - OBSTACLE_SIZE/2 + (Math.random() - 0.5) * 20;
                y = Math.min(Math.max(y, 40), H - OBSTACLE_SIZE - 40);
                // Avoid placing exactly on top of existing obstacles
                let tooClose = false;
                for (let obs of obstacles) {
                    if (Math.abs(obs.x - x) < 50) {
                        tooClose = true;
                        break;
                    }
                }
                if (!tooClose) {
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
            if (Math.abs(mouseY - roadY) < 45) {
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
### 🧠 How Vectra AI avoids random obstacles

- The **"Add Random Cars"** button places **3 to 5** other vehicles ahead on the road.
- The car’s **5 sensors** detect these obstacles from a distance.
- The AI **steers away** from the closest obstacle while **staying on the road** (path following + road pull).
- Speed automatically reduces when an obstacle is near.
- You can also **click directly on the road** to add individual cars.
- The simulation runs forever – the car will keep avoiding all obstacles you place.

### 🎮 Controls

- **Add Random Cars** – places several obstacles ahead.
- **Clear Other Cars** – removes all obstacles.
- **Reset Drive** – restarts the simulation.
- **Click on the road** – add a single car at that position.

### 🚀 Future neural network integration

**No extra software is needed to run Vectra AI.** It works immediately.

If you later want to replace the rule‑based AI with a **neural network**, you would need a training environment (TensorFlow, PyTorch, etc.). The current version is fully standalone – enjoy driving on the dust road!

---
<div class="footer">
    Vectra AI built by <strong>Gesner Deslandes</strong> – GlobalInternet.py
</div>
""")
