# Rayfall - A* Edition

A cleaned-up multi-file version of the original Pygame ray-casting game.

## Features
- Main menu and exactly 3 JSON-defined levels.
- Level data lives in `levels/levels.json`.
- Enemy movement uses real A* pathfinding on an 8-connected grid.
- Projectiles stop at walls before they can hit enemies behind them.
- Explosions use line-of-sight checks, so blast damage does not pass through walls.
- Player, dash, enemy, projectile and ray-casting code are split into modules.
- No external image assets are required; visuals are drawn by Pygame.

## Run
```bash
pip install -r requirements.txt
python main.py
```

Controls: W/S move, A/D turn, Space dash, left mouse/1 small shot, right mouse/2 big explosive shot, R reload.
