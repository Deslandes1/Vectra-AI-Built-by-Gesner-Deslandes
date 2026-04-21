// 1. Sort the fleet by position (West-most car first)
obstacles.sort((a, b) => a.x - b.x);

// 2. Process each car starting from the leader
for (let i = 0; i < obstacles.length; i++) {
    let o = obstacles[i];
    let baseSpeed = -2.5; // Desired cruising speed

    if (i > 0) {
        // This car has someone in front of it
        let leader = obstacles[i - 1];
        let gap = o.x - (leader.x + CAR_W);

        if (gap < 60) {
            // Match the leader's speed to freeze the gap
            o.speed = leader.speed;
            
            // Emergency brake if they get dangerously close
            if (gap < 20) o.speed = -0.1; 
        } else {
            o.speed = baseSpeed;
        }
    } else {
        // I am the leader, I set the pace
        o.speed = baseSpeed;
    }
    
    o.x += o.speed;
}
