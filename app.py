# --- 1. Update the car's Reset Logic ---
# Add this inside your update() function in the Javascript block

if (car.x > W + 50) {
    // Look ahead: Is the starting area (x = -50 to 150) empty?
    let resetZoneClear = obstacles.every(o => o.x > 150 || o.x < -20);
    
    if (resetZoneClear) {
        car.x = -50; 
    } else {
        // If an oncoming car is in the way, your car "waits" 
        // off-screen for a split second until it is safe to reappear.
        car.x = W + 49; 
    }
}

# --- 2. Update the Spawn Button Logic ---
# This prevents cars from spawning on top of each other

document.getElementById('spawnBtn').onclick = () => {
    // Only spawn if the entrance area (the right side) is clear
    let entryAreaClear = obstacles.every(o => o.x < W - 70);
    
    if (entryAreaClear) {
        obstacles.push({ x: W + 50, y: 0, speed: -2.5 });
    }
};
