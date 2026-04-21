import streamlit as st

st.set_page_config(page_title="Vectra AI – Precision Driving", layout="wide")

st.markdown("""
<style>
    body { margin: 0; background-color: #0e1117; }
    canvas { display: block; margin: 0 auto; border: 3px solid #b87c4f; border-radius: 12px; }
    .info { text-align: center; font-family: monospace; font-size: 1.2rem; margin-top: 10px; color: white; }
    .controls { text-align: center; margin-top: 15px; }
    button { background: #b87c4f; border: none; color: white; padding: 10px 20px; font-weight: bold; border-radius: 8px; cursor: pointer; margin: 5px; }
    button:hover { background: #9a653f; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: white;'>🚗 Vectra AI Precision System</h1>", unsafe_allow_html=True)

# --- The Simulation Logic ---
sim_html = """
<canvas id="gameCanvas" width="900" height="500"></canvas>
<div class="info">
    🚦 Limit: <span id="limitDisp">45 mph</span> &nbsp;|&nbsp; 
    🏎️ Speed: <span id="speedDisp">0.0</span> &nbsp;|&nbsp; 
    🎲 Clicks: <span id="spawnIdx">0</span>
</div>
<div class="controls">
    <button onclick="setLimit(30, 2.0)">30 MPH</button>
    <button onclick="setLimit(45, 3.5)">45 MPH</button>
    <button onclick="setLimit(70, 5.5)">70 MPH</button>
    <button id="spawnBtn" style="background:#2ecc71;">🚀 Spawn Oncoming</button>
    <button id="resetBtn" style="background:#e63946;">🔄 Reset</button>
</div>

<script>
    (function() {
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const W = 900, H = 500;
        
        let speedLimit = 3.5;
        let car = { x: 50, y: 250, w: 34, h: 18, speed: 0 };
        let obstacles = [];
        let spawnClicks = 0;

        function getRoadCenter(x) { return H/2 + Math.sin(x/120)*50; }

        window.setLimit = (label, val) => {
            speedLimit = val;
            document.getElementById('limitDisp').innerText = label + " mph";
        };

        document.getElementById('spawnBtn').onclick = () => {
            spawnClicks++;
            document.getElementById('spawnIdx').innerText = spawnClicks;
            
            // Scaled Spawning Logic: 1st=2, 2nd=2, 4th=4
            let qty = 1;
            if (spawnClicks === 1 || spawnClicks === 2) qty = 2;
            else if (spawnClicks === 4) qty = 4;

            for(let i=0; i<qty; i++) {
                obstacles.push({
                    x: W + (i * 150),
                    y: getRoadCenter(W) - 30, // Oncoming Left Lane
                    w: 30, h: 18,
                    speed: speedLimit * 0.8
                });
            }
        };

        function update() {
            // 1. Strict Boundary Constraints
            let roadMid = getRoadCenter(car.x + car.w/2);
            let roadTopLimit = roadMid + 5;      // Center line wall
            let roadBottomLimit = roadMid + 45; // Right edge wall
            
            // Auto-steer to stay in right lane center
            let targetY = roadMid + 22;
            car.y += (targetY - car.y) * 0.1;

            // Physical Blockers: Prevents leaving road or crossing center
            if (car.y < roadTopLimit) car.y = roadTopLimit;
            if (car.y + car.h > roadBottomLimit) car.y = roadBottomLimit - car.h;

            // 2. Speed & Collision
            let braking = 0;
            obstacles.forEach(o => {
                o.x -= o.speed;
                // Collision Detection
                if (car.x < o.x + o.w && car.x + car.w > o.x &&
                    car.y < o.y + o.h && car.y + car.h > o.y) {
                    car.speed = 0; // Emergency Hard Stop
                }
            });

            car.speed += (speedLimit - car.speed) * 0.05;
            car.x += car.speed;
            if (car.x > W) car.x = -50;
            
            document.getElementById('speedDisp').innerText = (car.speed * 12.5).toFixed(1);
            obstacles = obstacles.filter(o => o.x > -100);
        }

        function draw() {
            ctx.fillStyle = "#1a1a1a";
            ctx.fillRect(0,0,W,H);

            // Draw Road
            ctx.beginPath();
            for(let x=0; x<=W; x+=10) ctx.lineTo(x, getRoadCenter(x));
            ctx.lineWidth = 100;
            ctx.strokeStyle = "#333";
            ctx.stroke();

            // Center Line
            ctx.beginPath();
            ctx.setLineDash([20, 20]);
            for(let x=0; x<=W; x+=10) ctx.lineTo(x, getRoadCenter(x));
            ctx.lineWidth = 4;
            ctx.strokeStyle = "#f1c40f";
            ctx.stroke();
            ctx.setLineDash([]);

            // AI Car
            ctx.fillStyle = "#2ecc71";
            ctx.fillRect(car.x, car.y, car.w, car.h);

            // Traffic
            ctx.fillStyle = "#e74c3c";
            obstacles.forEach(o => ctx.fillRect(o.x, o.y, o.w, o.h));

            update();
            requestAnimationFrame(draw);
        }

        document.getElementById('resetBtn').onclick = () => {
            car.x = 50; obstacles = []; spawnClicks = 0;
            document.getElementById('spawnIdx').innerText = "0";
        };

        draw();
    })();
</script>
"""

st.components.v1.html(sim_html, height=650)
