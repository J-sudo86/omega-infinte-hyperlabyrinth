import math
import pygame


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def segment_intersection(a, b, c, d):
    ax, ay = a; bx, by = b; cx, cy = c; dx, dy = d
    r = (bx-ax, by-ay); s = (dx-cx, dy-cy)
    den = r[0]*s[1] - r[1]*s[0]
    if abs(den) < 1e-9: return None
    qmp = (cx-ax, cy-ay)
    t = (qmp[0]*s[1] - qmp[1]*s[0]) / den
    u = (qmp[0]*r[1] - qmp[1]*r[0]) / den
    if 0 <= t <= 1 and 0 <= u <= 1:
        return (ax+t*r[0], ay+t*r[1], t)
    return None


def line_of_sight(a, b, walls):
    for w in walls:
        if segment_intersection(a, b, w.a, w.b):
            return False
    return True


def move_circle(pos, delta, radius, walls, is_noclip=False):
    # Sub-step movement prevents tunnelling through thin walls.
    x, y = pos
    dist = math.hypot(*delta)
    steps = max(1, math.ceil(dist / 3.0))
    sx, sy = delta[0]/steps, delta[1]/steps

    for _ in range(steps):
        nx, ny = x+sx, y+sy
        blocked = False
        if is_noclip:
            x, y = nx, ny
            continue
        for w in walls:
            if w.collides_circle((nx, ny), radius):
                blocked = True; break
        if not blocked:
            x, y = nx, ny
    return x, y
