import streamlit as st
import base64
from PIL import Image
import io

# ... [Keep your existing st.set_page_config and styles here] ...

# --- Simulation Logic ---
# Note the 'f' before the triple quotes. 
# Inside, we use {{ }} for JS and { } for Python variables.
sim_html = f"""
<canvas id="gameCanvas" width="900" height="500" tabindex="0"></canvas>
<div class="info">
    🧠 AI Status: <span id="status">Active</span> &nbsp;|&nbsp; 
    ⏱️ Speed: <span id="currSpeed">0</span> MPH
</div>

<script>
    (function() {{
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const W = 900, H = 500, CAR_W = 34, CAR_H = 20;
        
        let car = {{ x: 50, y: 0, speed: 0, alive: true }};
        let obstacles = [];
        const SPEED_LIMIT = {sim_limit}; // Python variable injected here

        function getRoadCenterY(x) {{
            return H/2 + 30 + Math.sin(x / 90) * 45 + Math.sin(x / 200) * 25;
        }}

        function update() {{
            if (!car.alive) return;

            // 1. Player Movement & Loop Protection
            car.speed += (SPEED_LIMIT - car.speed) * 0.05;
            car.x += car.speed;

            if (car.x > W + 50) {{
                // Safety check: only reset if the start is clear
                let startIsClear = obstacles.every(o => o.x > 120 || o.x < -20);
                if (startIsClear) {{
                    car.x = -50;
                }} else {{
                    car.x = W + 49; 
                }}
            }}

            car.y = getRoadCenterY(car.x) + 18 - (CAR_H/2);
            
            // 2. Traffic Intelligence (Left Lane)
            obstacles.sort((a, b) => a.x - b.x); 

            for (let i = 0; i < obstacles.length; i++) {{
                let o = obstacles[i];
                let targetSpeed = -2.5;

                if (i > 0) {{
                    let leader = obstacles[i-1];
                    let gap = o.x - (leader.x + CAR_W);
                    if (gap < 85) {{
                        targetSpeed = leader.speed;
                        if (gap < 25) targetSpeed = -0.1; 
                    }}
                }}

                o.speed = targetSpeed;
                o.x += o.speed;
                o.y = getRoadCenterY(o.x) - 18 - (CAR_H/2);
            }}

            // Collision check
            for (let o of obstacles) {{
                if (car.x < o.x + CAR_W && car.x + CAR_W > o.x && 
                    car.y < o.y + CAR_H && car.y + CAR_H > o.y) {{
                    car.alive = false;
                }}
            }}
        }}

        function draw() {{
            ctx.fillStyle = "#0e1117";
            ctx.fillRect(0, 0, W, H);
            
            // Draw Road
            ctx.beginPath(); ctx.moveTo(-50, getRoadCenterY(-50));
            for (let x = 0; x <= W + 50; x += 10) ctx.lineTo(x, getRoadCenterY(x));
            ctx.lineWidth = 100; ctx.strokeStyle = "#444"; ctx.stroke();

            // Blue Player Car
            ctx.fillStyle = car.alive ? "#00d4ff" : "#f00";
            ctx.fillRect(car.x, car.y, CAR_W, CAR_H);
            
            // Red Traffic
            ctx.fillStyle = "#ff4b4b";
            for (let o of obstacles) ctx.fillRect(o.x, o.y, CAR_W, CAR_H);
        }}

        function loop() {{ update(); draw(); requestAnimationFrame(loop); }}
        loop();
    }})();
</script>
"""

st.components.v1.html(sim_html, height=600)
