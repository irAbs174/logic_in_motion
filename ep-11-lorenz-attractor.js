// Episode 11: Lorenz Attractor
let dx = sigma * (y - x) * dt;
let dy = (x * (rho - z) - y) * dt;
let dz = (x * y - beta * z) * dt;
