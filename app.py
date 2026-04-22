import streamlit as st

# 1. SYSTEM CONFIGURATION
st.set_page_config(page_title="Vectra AI – Autopilot OS", layout="wide")

# --- SIDEBAR: Company Informants & B2B Pricing ---
with st.sidebar:
    st.header("🏢 GlobalInternet.py")
    st.success("Founder: Gesner Deslandes")
    
    st.markdown("### 📬 Contact Information")
    st.write("📧 **Email:** deslandes78@gmail.com")
    st.write("📞 **Phone:** (509) 4738-5663")
    st.write("📍 **Base:** Port-au-Prince, Haiti")
    
    st.markdown("---")
    
    with st.expander("💎 B2B Licensing (Fair Market)"):
        st.markdown("""
        **Vectra AI Autopilot OS**
        - **Valuation:** $4,500 – $12,000
        - **Tech:** Real-time physics engine, AI lane-discipline, and custom heading algorithms.
        - **Terms:** Per implementation / Full IP transfer.
        """)
    
    with st.expander("💳 Software Business Model"):
        st.write("**Zero Subscriptions:** One-time licensing fees only.")
        st.write("**Full Access:** All purchases include full source code.")
        st.write("**Support:** 1 year of technical setup included.")
    
    with st.expander("💰 Standard Software List"):
        st.markdown("""
        | Product | Price |
        | :--- | :--- |
        | **Drone Commander** | $2,000 |
        | **Voting Software** | $2,000 |
        | **School Management**| $1,500 |
        | **Digital Marketing**| $150 - $1,200 |
        | **Chess Game** | $20 |
        """)
    
    st.markdown("---")
    st.header("🕹️ Operation Mode")
    app_mode = st.radio("Select Drive Mode:", ["Standard Simulation", "Autopilot OS Mode"])
    
    if app_mode == "Autopilot OS Mode":
        st.subheader("🧠 Software Stack Active")
        with st.expander("👁️ Perception Layer"):
            st.checkbox("Object Detection (YOLO)", value=True)
            st.checkbox("Lane Segmentation", value=True)
        with st.expander("🧠 Planning & Control"):
            st.slider("Safety Buffer (Meters)", 1, 10, 5)
            st.checkbox("Emergency Braking (AEB)", value=True)
    
    st.markdown("---")
    st.caption("v3.1.0 - Full Enterprise Build")

# --- MAIN UI: Header & Playable Video ---
st.markdown("<h1 style='text-align: center;'>🚗 Vectra AI – Autopilot Simulation</h1>", unsafe_allow_html=True)

with st.container():
    st.subheader("📹 AI Self-Driving Core Demonstration")
    # Using the raw link for direct playback in the browser
    video_url = "https://github.com/Deslandes1/Vectra-AI-Built-by-Gesner-Deslandes/raw/main/AI%20Selfdriving.mp4"
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.video(video_url)
    with col2:
        st.write("**Project Specs & Source**")
        st.write("This engine simulates high-fidelity lane discipline and autonomous navigation.")
        st.write("---")
        st.write("🔗 [View GitHub Repository](https://github.com/Deslandes1/Vectra-AI-Built-by-Gesner-Deslandes/)")
        st.info("Logic: Neural Network Pathfinding & Heading-Based Rotation.")

st.markdown("---")

# 2. THE SIMULATION ENGINE (Physics, Rotation, & Staggered Spawning)
sim_html = f"""
<style>
    body {{ margin: 0; background-color: #0e1117; color: white; font-family: sans-serif; overflow: hidden; }}
    canvas {{ display: block; margin: 0 auto; border: 3px solid #b87c4f; border-radius: 12px; }}
    .status-bar {{ display: flex; justify-content: center; gap: 20px; margin-top: 15px; font-family: monospace; }}
    .status-item {{ padding: 5px 15px; border-radius: 5px; background: #1e2a3a; border-left: 4px solid #b87c4f; }}
    button {{ background: #b87c4f; border: none; color: white; padding: 10px 20px; font-weight: bold; border-radius: 8px; cursor: pointer; margin: 5px; }}
    button:hover {{ background: #9a653f; }}
</style>

<canvas id="gameCanvas" width="900" height="450"></canvas>

<div class="status-bar">
    <div class="status-item">🛰️ GPS: <span id="gpsDisp">CONNECTED</span></div>
    <div class="status-item">🏎️ SPEED: <span id="speedDisp">0.0</span></div>
    <div class="status-item">🎲 INDEX: <span id="clickDisp">0</span></div>
</div>

<div style="text-align: center; margin-top: 20px;">
    <button onclick="setLimit(30, 2.0)">30 MPH</button>
    <button onclick="setLimit(45, 3.5)">45 MPH</button>
    <button onclick="setLimit(70, 5.5)">70 MPH</button>
    <button id="spawnBtn" style="background:#2ecc71;">🚀 SPAWN ONCOMING</button>
    <button id="resetBtn" style="background:#e63946;">🔄 FULL SYSTEM REBOOT</button>
</div>

<script>
    (function() {{
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const W = 900, H = 450;
        const MODE = "{app_mode}"; 
        
        let speedLimit = 3.5;
        let car = {{ x: 50, y: 250, w: 34, h: 18, speed: 0, angle: 0 }};
        let obstacles = [];
        let spawnClicks = 0;
        const SAFE_DISTANCE = 180; // Distance maintained between oncoming cars

        function getRoadCenter(x) {{ return H/2 + Math.sin(x/150)*40; }}

        function getRoadAngle(x) {{
            let x1 = x, x2 = x + 2;
            let y1 = getRoadCenter(x1), y2 = getRoadCenter(x2);
            return Math.atan2(y2 - y1, x2 - x1);
        }}

        window.setLimit = (label, val) => {{ speedLimit = val; }};

        document.getElementById('spawnBtn').onclick = () => {{
            spawnClicks++;
            document.getElementById('clickDisp').innerText = spawnClicks;
            
            // Scaled Spawning Logic: 1st=2, 2nd=2, 4th=4
            let qty = (spawnClicks === 1 || spawnClicks === 2) ? 2 : (spawnClicks === 4 ? 4 : 1);

            for(let i=0; i<qty; i++) {{
                let spawnX = W + (i * SAFE_DISTANCE) + 50;
                obstacles.push({{
                    x: spawnX,
                    y: getRoadCenter(spawnX % W) - 30, // Position on the left lane
                    w: 30, h: 18,
                    speed: speedLimit * 0.85
                }});
            }}
        }};

        function update() {{
            // AI Car Core Pathing
            let roadMid = getRoadCenter(car.x + car.w/2);
            let targetY = roadMid + 20; // Maintain right-lane discipline
            car.y += (targetY - car.y) * 0.1;
            car.angle = getRoadAngle(car.x);

            car.speed += (speedLimit - car.speed) * 0.05;
            car.x += car.speed;
            if (car.x > W) car.x = -50;

            // Oncoming Traffic Logic
            obstacles.forEach(o => {{
                o.x -= o.speed;
                o.y = getRoadCenter(o.x % W) - 30; // Lane-lock on left side
                o.angle = getRoadAngle(o.x) + Math.PI; // Face opposite direction

                // AEB Collision Logic
                if (car.x < o.x + o.w && car.x + car.w > o.x &&
                    car.y < o.y + o.h && car.y + car.h > o.y) {{
                    car.speed = 0;
                }}
            }});
            obstacles = obstacles.filter(o => o.x > -1000);
            document.getElementById('speedDisp').innerText = (car.speed * 12.5).toFixed(1);
        }}

        function drawCar(x, y, w, h, angle, color, isAutopilot) {{
            ctx.save();
            ctx.translate(x + w/2, y + h/2);
            ctx.rotate(angle);
            ctx.fillStyle = color;
            ctx.fillRect(-w/2, -h/2, w, h);
            
            // Visual Headlights
            ctx.fillStyle = "white";
            ctx.fillRect(w/2 - 4, -h/2 + 2, 4, 3);
            ctx.fillRect(w/2 - 4, h/2 - 5, 4, 3);

            if (MODE === "Autopilot OS Mode" && isAutopilot) {{
                ctx.strokeStyle = "#00ffcc88";
                ctx.setLineDash([3, 3]);
                ctx.strokeRect(-w/2 - 5, -h/2 - 5, w + 10, h + 10);
            }}
            ctx.restore();
        }}

        function draw() {{
            ctx.fillStyle = "#111";
            ctx.fillRect(0,0,W,H);
            
            // Render High-Fidelity Road
            ctx.beginPath();
            for(let x=0; x<=W; x+=1) ctx.lineTo(x, getRoadCenter(x));
            ctx.lineWidth = 100; ctx.strokeStyle = "#333"; ctx.stroke();
            
            // Render Lane Markings
            ctx.beginPath();
            ctx.setLineDash([15, 15]);
            for(let x=0; x<=W; x+=5) ctx.lineTo(x, getRoadCenter(x));
            ctx.lineWidth = 2; ctx.strokeStyle = "#ffffff44"; ctx.stroke();
            ctx.setLineDash([]);

            // Draw Actors
            drawCar(car.x, car.y, car.w, car.h, car.angle, "#2ecc71", true);
            obstacles.forEach(o => {{
                drawCar(o.x, o.y, o.w, o.h, o.angle, "#e63946", false);
            }});

            update();
            requestAnimationFrame(draw);
        }}

        document.getElementById('resetBtn').onclick = () => {{
            car.x = 50; obstacles = []; spawnClicks = 0;
            document.getElementById('clickDisp').innerText = 0;
        }};
        draw();
    }})();
</script>
"""

st.components.v1.html(sim_html, height=600)
