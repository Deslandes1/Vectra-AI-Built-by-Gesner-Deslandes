import streamlit as st

st.set_page_config(page_title="Vectra AI – Autopilot", layout="wide")

# --- 1. INITIALIZATION ---
# Variables must be defined before the HTML block to avoid NameErrors.
speed_limit = 40  
sim_limit = 2.6   

with st.sidebar:
    st.header("🚦 System Settings")
    speed_limit = st.select_slider("AI Speed Limit (MPH)", options=[20, 30, 40, 50, 60, 70, 80], value=40)
    sim_limit = speed_limit / 15 

st.markdown(f"""
<div style="text-align: center;">
    <h1>🚗 Vectra AI – Zero-Collision Autopilot</h1>
    <p style="font-size: 1.1rem;">built by <strong>Gesner Deslandes</strong></p>
</div>
""", unsafe_allow_html=True)

# --- 2. THE SIMULATION ENGINE ---
# We use f-string with {{ }} to protect Javascript curly braces.
sim_html = f"""
<canvas id="gameCanvas" width="900" height="500" style="display: block; margin: 0 auto; border: 2px solid #b87c4f; border-radius: 12px;"></canvas>
<div style="text-align: center; font-family: monospace; font-size: 1.2rem; margin-top: 10px; color: white;">
    🤖 Autopilot: <span id="status" style="color: #00ff00;">ONLINE</span> &nbsp;|&nbsp; 
    ⏱️ Speed: <span id="currSpeed">0</span> MPH
</div>

<script>
    (function() {{
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const W = 900, H = 500, CAR_W = 34, CAR_H = 20;
        const BUFFER = 90; // Safety distance in pixels
        
        let car = {{ x: 50, y: 0, speed: 0, targetSpeed: {sim_limit} }};
        let obstacles = [];

        function getRoadY(x) {{
            return H/2 + 30 + Math.sin(x / 90) * 45 + Math.sin(x / 200) * 25;
        }}

        function update() {{
            // 1. AUTO-PILOT FOR PLAYER CAR
            let playerTarget = {sim_limit};
            
            // Look ahead for oncoming traffic in the same lane
            obstacles.forEach(o => {{
                let dist = o.x - car.x;
                // If a car is ahead within the safety buffer, match its speed or brake
                if (dist > 0 && dist < BUFFER) {{
                    playerTarget = Math.min(playerTarget, 0); 
                }}
            }});

            car.speed += (playerTarget - car.speed) * 0.1;
            car.x += car.speed;

            // Safe Boundary Reset
            if (car.x > W + 50) {{
                let startClear = obstacles.every(o => o.x > 150 || o.x < -20);
                if (startClear) car.x = -50;
                else car.x = W + 49; // Wait for gap
            }}
            car.y = getRoadY(car.x) + 18 - (CAR_H/2);
            document.getElementById('currSpeed').innerText = Math.round(car.speed * 15);

            // 2. AUTO-PILOT FOR TRAFFIC (Left Lane)
            obstacles.sort((a, b) => a.x - b.x); 
            for (let i = 0; i < obstacles.length; i++) {{
                let o = obstacles[i];
                let oTarget = -2.5;

                // Collision Avoidance between AI cars
                if (i > 0) {{
                    let leader = obstacles[i-1];
                    let gap = o.x - (leader.x + CAR_W);
                    if (gap < BUFFER) oTarget = leader.speed;
                }}
                
                // Avoid collision with Player car
                let distToPlayer = Math.abs(o.x - car.x);
                if (distToPlayer < BUFFER && Math.abs(o.y - car.y) < 15) {{
                    oTarget = 0;
                }

                o.speed += (oTarget - o.speed) * 0.1;
                o.x += o.speed;
                o.y = getRoadY(o.x) - 18 - (CAR_H/2);
            }}
            obstacles = obstacles.filter(o => o.x > -100);
        }}

        function draw() {{
            ctx.fillStyle = "#0e1117";
            ctx.fillRect(0, 0, W, H);
            
            // Draw Road Path
            ctx.beginPath(); ctx.moveTo(-50, getRoadY(-50));
            for (let x = 0; x <= W + 50; x += 10) ctx.lineTo(x, getRoadY(x));
            ctx.lineWidth = 100; ctx.strokeStyle = "#444"; ctx.stroke();

            // Center Markings
            ctx.beginPath(); ctx.setLineDash([15, 15]);
            for (let x = 0; x <= W; x += 5) ctx.lineTo(x, getRoadY(x));
            ctx.lineWidth = 3; ctx.strokeStyle = "#ffd700"; ctx.stroke(); ctx.setLineDash([]);

            // Blue Player / Red Traffic
            ctx.fillStyle = "#00d4ff";
            ctx.fillRect(car.x, car.y, CAR_W, CAR_H);
            ctx.fillStyle = "#ff4b4b";
            for (let o of obstacles) ctx.fillRect(o.x, o.y, CAR_W, CAR_H);
        }}

        function loop() {{ update(); draw(); requestAnimationFrame(loop); }}

        // Safe Auto-Spawning
        setInterval(() => {{
            if (obstacles.length < 4) {{
                let entryClear = obstacles.every(o => o.x < W - 100);
                if (entryClear) obstacles.push({{ x: W + 50, y: 0, speed: -2.5 }});
            }}
        }}, 3000);

        loop();
    }})();
</script>
"""

st.components.v1.html(sim_html, height=600)
