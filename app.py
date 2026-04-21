# --- Updated JavaScript Logic within app.py ---

# 1. Update the Loop Reset
if (car.x > W + 50) {
    // Check if the starting area (x=0 to x=100) is clear of oncoming traffic
    let startAreaClear = obstacles.every(o => o.x > 150); 
    
    if (startAreaClear) {
        car.x = -50; 
        // Briefly reduce speed to simulate the car entering a new stretch of road
        car.speed *= 0.8; 
    } else {
        // If an oncoming car is right there, the car "waits" off-screen 
        // for a split second to avoid an instant reset-crash.
        car.x = W + 49; 
    }
}

# 2. Update the Spawn Sentinel
document.getElementById('spawnBtn').onclick = () => {
    // Only spawn if BOTH the entrance (Right) and the loop-reset point (Left) are safe
    let entranceClear = obstacles.every(o => o.x < W - 60);
    let resetPointClear = car.x > 100 || car.x < -10; // Don't spawn if car just reset
    
    if (entranceClear && resetPointClear) {
        obstacles.push({ x: W + 50, y: 0, speed: -2.5 });
    }
};
