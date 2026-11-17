function worldState(S, f) { /* static town; clouds drift slowly */ world.children.forEach((o) => { if (o.userData.cloud) o.position.x += 0.0; }); }
