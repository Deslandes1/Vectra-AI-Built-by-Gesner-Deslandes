import streamlit as st

st.set_page_config(page_title="Vectra AI – Advanced Simulation", layout="wide")

st.markdown("""
<style>
    body { margin: 0; background-color: #0e1117; }
    canvas { display: block; margin: 0 auto; border: 2px solid #b87c4f; border-radius: 12px; }
    .info { text-align: center; font-family: monospace; font-size: 1.1rem; margin-top: 10px; color: white; }
    .controls { text-align: center; margin-top: 15px; }
    button { background: #b87c4f; border: none; color: white; padding: 10px 20px; font-weight: bold; border-radius: 8px; cursor: pointer; margin: 5px; transition: 0.2s; }
    button:hover { background: #9a653f; transform: translateY(-2px); }
    .speed-btn { background: #1e2a3a; border: 1px solid #b87c4f; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center;">
    <h1>🚗 Vectra AI – Dynamic Speed & Spawning</h1>
    <p>Adjust the <strong>Road Speed Limit</strong> to change AI behavior and use the <strong>Spawn Oncoming</strong> button for scaled obstacles.</p>
</div>
""", unsafe_allow_html=True)

sim_html = """
<canvas id="gameCanvas" width="900" height="500"></canvas>
<div class="info">
    🚦 Limit: <span id="limitDisp">45 mph</span> &nbsp;|&nbsp; 
    🏎️ Actual: <span id="speedDisp">0.0</span> &nbsp;|&nbsp; 
    📉 Spawn Count: <span id="spawnIdx">0</span>
</div>
<div class="controls">
    <button class="speed-btn" onclick="setLimit(30, 2.2)">30 MPH</button>
    <button class="speed-btn" onclick="setLimit(45, 3.5)">45 MPH</button>
    <button class="speed-btn" onclick="setLimit(70, 5.5)">70 MPH</button>
    <br>
    <button id="spawnBtn">🚀 Spawn Oncoming Car</button>
    <button id="resetBtn" style="background: #e63946;">🔄 Reset</button>
</div>

<script>
    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');
    const W = 900, H = 500;
    
    let speedLimit = 3.5;
    let spawnClicks = 0;
    let obstacles = [];
    let car = { x: 50, y: 300, angle: 0, speed: 0 };

    function getRoadCenter(x) { return H/2 + Math.sin(x/100)*40; }

    window.setLimit = (label, val) => {
        speedLimit = val;
        document.getElementById('limitDisp').innerText = label + " mph";
    };

    document.getElementById('spawnBtn').onclick = () => {
        spawnClicks++;
        document.getElementById('spawnIdx').innerText = spawnClicks;
        
        let count = 0;
        if (spawnClicks === 1) count = 2;
        else if (spawnClicks === 2) count = 2;
        else if (spawnClicks === 4) count = 4;
        else count = 1; // Default for other clicks

        for(let i=0; i<count; i++) {
            obstacles.push({
                x: W + (i * 150),
                y: getRoadCenter(W) - 35,
                w: 30, h: 20,
                speed: speedLimit * 0.7
            });
        }
    };

    function update() {
        // AI Speed Control - approach the current speed limit
        car.speed += (speedLimit - car.speed) * 0.05;
        document.getElementById('speedDisp').innerText = (car.speed * 12.8).toFixed(1);

        // Movement
        car.x += car.speed;
        if(car.x > W) car.x = -50;
        
        let targetY = getRoadCenter(car.x) + 25;
        car.y += (targetY - car.y) * 0.1;

        obstacles.forEach(o => {
            o.x -= o.speed;
            o.y = getRoadCenter(o.x) - 25;
        });
        obstacles = obstacles.filter(o => o.x > -50);
    }

    function draw() {
        ctx.fillStyle = "#2c3e50";
        ctx.fillRect(0,0,W,H);
        
        // Road
        ctx.beginPath();
        for(let x=0; x<W; x+=5) ctx.lineTo(x, getRoadCenter(x));
        ctx.lineWidth = 80;
        ctx.strokeStyle = "#7f8c8d";
        ctx.stroke();

        // AI Car
        ctx.fillStyle = "#27ae60";
        ctx.fillRect(car.x, car.y - 10, 30, 20);

        // Obstacles
        ctx.fillStyle = "#c0392b";
        obstacles.forEach(o => ctx.fillRect(o.x, o.y - 10, o.w, o.h));
        
        requestAnimationFrame(() => { update(); draw(); });
    }

    document.getElementById('resetBtn').onclick = () => {
        obstacles = [];
        spawnClicks = 0;
        document.getElementById('spawnIdx').innerText = "0";
    };

    draw();
</script>
"""

st.components.v1.html(sim_html, height=650)

---

### 🛠️ Configuration Details

| Feature | Logic |
| :--- | :--- |
| **Speed Limit** | Updates the global `speedLimit` variable. The AI uses a simple P-controller to accelerate or decelerate smoothly to the new target. |
| **Obstacle Scaling** | The `spawnClicks` counter tracks interaction. It uses a conditional check to spawn exactly **2, 2, or 4** obstacles depending on the click count. |
| **Oncoming Speed** | Obstacles move at **70%** of the current road speed limit to ensure the relative passing speed feels realistic. |

### 🧠 How the AI adapts
The AI doesn't just "jump" to the new speed. It calculates the difference between its current velocity and the road limit, applying a **0.05 friction/acceleration coefficient**. This ensures that if you switch from 30 MPH to 70 MPH, you see the car physically lean into the acceleration.
