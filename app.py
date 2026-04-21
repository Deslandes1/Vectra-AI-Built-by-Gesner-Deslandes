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
    <h1>🚗 Vectra AI – Strict Lane Discipline</h1>
    <p style="font-size: 1.1rem;">built by <strong>Gesner Deslandes</strong></p>
    <p>The car is now programmed to <strong>never cross the center line</strong>. It avoids obstacles by slowing down or hugging the right shoulder.</p>
</div>
""", unsafe_allow_html=True)

# --- The Simulation Canvas ---
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
    <button id="randomObstaclesBtn">🎲 Add Random Cars (Left Lane)</button>
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
        const SENSOR_LENGTH = 150;
        const SENSOR_ANGLES = [-0.6, -0.3, 0, 0.3, 0.6];
        const MAX_SPEED = 3.5;
        const TURN_SPEED = 0.12;
        const RIGHT_LANE_OFFSET = 22;
        const OBSTACLE_SPEED = 2.0;

        let car = { x: 50, y: 0, angle: 0, speed: 0, alive: true, collisions: 0 };
        let obstacles = [];

        function getRoadCenterY(x) {
            return H/2 + 30 + Math.sin(x / 90) * 45 + Math.sin(x / 200) * 25;
        }

        function getRightLaneY(x) { return getRoadCenterY(x) + RIGHT_LANE_OFFSET; }
        function getLeftLaneY(x) { return getRoadCenterY(x) - RIGHT_LANE_OFFSET; }

        function enforceBoundaries() {
            let centerY = getRoadCenterY(car.x);
            // STRICT RULE: Car center must stay below (greater than) road center
            if (car.y + CAR_HEIGHT/2 < centerY + 5) {
                car.y = centerY + 5 - CAR_HEIGHT/2;
                car.angle = Math.max(car.angle, 0); // Force nose away from center
            }
        }

        function updateCar() {
            if (!car.alive) return;
            
            let targetY = getRightLaneY(car.x + 30);
            let dyTarget = targetY - (car.y + CAR_HEIGHT/2);
            
            // Basic Path Following
            let desiredAngle = Math.atan2(dyTarget, 30);
            
            // Obstacle Avoidance (Only steer RIGHT or BRAKE)
            let threats = [0, 0, 0, 0, 0];
            for (let i = 0; i < SENSOR_ANGLES.length; i++) {
                let rad = car.angle + SENSOR_ANGLES[i];
                let x = car.x + CAR_WIDTH/2;
                let y = car.y + CAR_HEIGHT/2;
                
                for (let obs of obstacles) {
                    for (let dist = 0; dist < SENSOR_LENGTH; dist += 5) {
                        let px = x + Math.cos(rad) * dist;
                        let py = y + Math.sin(rad) * dist;
                        if (px > obs.x && px < obs.x + obs.w && py > obs.y && py < obs.y + obs.h) {
                            threats[i] = (SENSOR_LENGTH - dist) / SENSOR_LENGTH;
                            break;
                        }
                    }
                }
            }

            // AI Logic: If obstacle is ahead, steer right and slow down. Never steer left into oncoming traffic.
            let frontThreat = threats[2] || threats[1] || threats[0];
            let steerAdjustment = (threats[0] + threats[1] + threats[2]) * 0.8; 
            
            let totalSteer = desiredAngle + steerAdjustment;
            car.speed = Math.max(1.0, MAX_SPEED * (1 - frontThreat));
            car.angle += (totalSteer - car.angle) * TURN_SPEED;
            
            car.x += Math.cos(car.angle) * car.speed;
            car.y += Math.sin(car.angle) * car.speed;

            enforceBoundaries();

            // Loop car
            if (car.x > W) car.x = -CAR_WIDTH;

            // Collision check
            for (let obs of obstacles) {
                if (car.x < obs.x + obs.w && car.x + CAR_WIDTH > obs.x &&
                    car.y < obs.y + obs.h && car.y + CAR_HEIGHT > obs.y) {
                    car.alive = false;
                    statusSpan.innerText = "Collision!";
                }
            }
        }

        function draw() {
            ctx.fillStyle = "#c9a87b"; // Dust background
            ctx.fillRect(0, 0, W, H);
            
            // Draw Road
            ctx.beginPath();
            ctx.moveTo(0, getRoadCenterY(0));
            for (let x = 0; x <= W; x += 10) ctx.lineTo(x, getRoadCenterY(x));
            ctx.lineWidth = 100;
            ctx.strokeStyle = "#a56b3a";
            ctx.stroke();

            // Center Line (The "Wall")
            ctx.beginPath();
            ctx.setLineDash([15, 15]);
            for (let x = 0; x <= W; x += 10) ctx.lineTo(x, getRoadCenterY(x));
            ctx.lineWidth = 4;
            ctx.strokeStyle = "#ffffff";
            ctx.stroke();
            ctx.setLineDash([]);

            // Draw Obstacles
            for (let obs of obstacles) {
                ctx.fillStyle = "#e63946";
                ctx.fillRect(obs.x, obs.y, obs.w, obs.h);
                obs.x += obs.speed;
                if (obs.x > W) obs.x = -OBSTACLE_SIZE;
            }

            // Draw Car
            ctx.save();
            ctx.translate(car.x + CAR_WIDTH/2, car.y + CAR_HEIGHT/2);
            ctx.rotate(car.angle);
            ctx.fillStyle = car.alive ? "#2a9d8f" : "#555";
            ctx.fillRect(-CAR_WIDTH/2, -CAR_HEIGHT/2, CAR_WIDTH, CAR_HEIGHT);
            ctx.restore();
        }

        function gameLoop() {
            updateCar();
            draw();
            requestAnimationFrame(gameLoop);
        }

        document.getElementById('randomObstaclesBtn').addEventListener('click', () => {
            let x = car.x + 300 + Math.random() * 200;
            obstacles.push({
                x: x, y: getLeftLaneY(x % W) - 10,
                w: OBSTACLE_SIZE, h: OBSTACLE_SIZE, speed: OBSTACLE_SPEED
            });
            obstacleCountSpan.innerText = obstacles.length;
        });

        document.getElementById('resetBtn').addEventListener('click', () => {
            car.x = 50; car.alive = true; statusSpan.innerText = "Driving";
        });

        document.getElementById('clearObstaclesBtn').addEventListener('click', () => {
            obstacles = []; obstacleCountSpan.innerText = 0;
        });

        gameLoop();
    })();
</script>
"""

st.components.v1.html(sim_html, height=600)

st.info("**AI Logic Update:** The vehicle now treats the center dashed line as a boundary constraint. If an obstacle appears in the opposite lane, the car maintains its path. If a click forces an obstacle into the right lane, the car will prioritize steering toward the right shoulder and braking over crossing the center line.")
