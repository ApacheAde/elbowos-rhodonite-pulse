#!/usr/bin/env python3
"""Rhodonite Pulse — neon rising-lane rhythm tap for ElbowOS."""
from __future__ import annotations

import math
import os
import random
import subprocess
import sys

import pygame

W, H = 1080, 1920
FPS = 30
TITLE = "RHODONITE PULSE"
HANDLE = "x.com/ElbowOS"
LANES = 4
HIT_Y = 280
SPAWN_Y = 1860
LANE_XS = [180, 420, 660, 900]
KEYS = (pygame.K_d, pygame.K_f, pygame.K_j, pygame.K_k)

PLUM = (18, 4, 28)
ROSE = (255, 72, 140)
GOLD = (255, 214, 90)
CYAN = (80, 255, 230)
MAG = (210, 40, 255)
CREAM = (255, 236, 220)
INK = (8, 2, 14)


def lerp(a, b, t):
    return a + (b - a) * t


class Pulse:
    def __init__(self, lane: int, speed: float, kind: int):
        self.lane = lane
        self.y = SPAWN_Y
        self.speed = speed
        self.kind = kind  # 0 rose, 1 gold, 2 mag
        self.hit = False
        self.missed = False
        self.alive = True
        self.flash = 0.0

    @property
    def x(self):
        return LANE_XS[self.lane]

    def update(self, dt: float):
        if not self.alive:
            return
        self.y -= self.speed * dt
        if self.flash:
            self.flash = max(0.0, self.flash - dt * 6)
        if self.y < HIT_Y - 90 and not self.hit:
            self.missed = True
            self.alive = False


class Game:
    def __init__(self, record: bool):
        self.record = record
        self.surf = pygame.Surface((W, H))
        self.clock = pygame.time.Clock()
        self.font_lg = pygame.font.Font(None, 86)
        self.font_md = pygame.font.Font(None, 54)
        self.font_sm = pygame.font.Font(None, 40)
        self.pulses: list[Pulse] = []
        self.score = 0
        self.combo = 0
        self.best = 0
        self.t = 0.0
        self.spawn_acc = 0.0
        self.judges: list[tuple[str, float, int]] = []
        self.lane_glow = [0.0] * LANES
        self.sparks: list[list[float]] = []
        self.auto_idx = 0
        self.running = True
        self.screen = None
        if not record:
            self.screen = pygame.display.set_mode((W, H))
            pygame.display.set_caption(TITLE)

    def spawn(self):
        n = 1 if random.random() > 0.22 else 2
        used = set()
        speed = 520 + min(280, self.t * 12)
        for _ in range(n):
            lane = random.randrange(LANES)
            if lane in used:
                continue
            used.add(lane)
            self.pulses.append(Pulse(lane, speed, random.choices([0, 1, 2], [5, 3, 2])[0]))

    def try_hit(self, lane: int):
        self.lane_glow[lane] = 1.0
        best = None
        best_d = 999
        for p in self.pulses:
            if p.lane != lane or p.hit or not p.alive:
                continue
            d = abs(p.y - HIT_Y)
            if d < best_d:
                best_d, best = d, p
        if best is None or best_d > 78:
            self.combo = 0
            self.judges.append(("MISS", 0.7, lane))
            return
        best.hit = True
        best.alive = False
        best.flash = 1.0
        if best_d < 18:
            tag, pts = "PERFECT", 300
        elif best_d < 40:
            tag, pts = "GREAT", 180
        else:
            tag, pts = "OK", 80
        self.combo += 1
        self.best = max(self.best, self.combo)
        self.score += pts + self.combo * 8
        self.judges.append((tag, 0.7, lane))
        col = (ROSE, GOLD, MAG)[best.kind]
        for _ in range(10):
            ang = random.uniform(0, 6.28)
            self.sparks.append([best.x, HIT_Y, math.cos(ang) * 220, math.sin(ang) * 220, 0.4, *col])

    def autoplay(self):
        # fire slightly early so the reel shows hits landing
        for p in self.pulses:
            if p.hit or not p.alive:
                continue
            if HIT_Y - 8 <= p.y <= HIT_Y + 36:
                if random.random() < 0.86:
                    self.try_hit(p.lane)

    def update(self, dt: float):
        self.t += dt
        self.spawn_acc += dt
        gap = max(0.28, 0.62 - self.t * 0.012)
        if self.spawn_acc >= gap:
            self.spawn_acc = 0.0
            self.spawn()
        for p in self.pulses:
            p.update(dt)
        self.pulses = [p for p in self.pulses if p.alive or p.flash > 0]
        self.lane_glow = [max(0.0, g - dt * 4) for g in self.lane_glow]
        self.judges = [(s, life - dt, ln) for s, life, ln in self.judges if life - dt > 0]
        nxt = []
        for sp in self.sparks:
            sp[0] += sp[2] * dt
            sp[1] += sp[3] * dt
            sp[4] -= dt
            if sp[4] > 0:
                nxt.append(sp)
        self.sparks = nxt
        if self.record:
            self.autoplay()

    def draw_bg(self, s: pygame.Surface):
        s.fill(INK)
        for i in range(18):
            y = (i * 140 + int(self.t * 70)) % (H + 140) - 70
            pygame.draw.line(s, (40, 8, 48), (0, y), (W, y), 2)
        pygame.draw.rect(s, (42, 8, 36), (0, 0, 70, H))
        pygame.draw.rect(s, (42, 8, 36), (W - 70, 0, 70, H))
        pygame.draw.rect(s, ROSE, (64, 0, 8, H))
        pygame.draw.rect(s, GOLD, (W - 72, 0, 8, H))
        rng = random.Random(7)
        for i in range(40):
            mx = rng.randint(90, W - 90)
            my = (rng.randint(0, H) + int(self.t * (40 + i % 30))) % H
            pygame.draw.circle(s, (90, 20, 70), (mx, my), 2 + i % 3)

    def draw(self, s: pygame.Surface):
        self.draw_bg(s)
        for i, x in enumerate(LANE_XS):
            glow = self.lane_glow[i]
            col = (int(lerp(48, 255, glow)), int(lerp(10, 90, glow)), int(lerp(70, 180, glow)))
            pygame.draw.line(s, col, (x, 220), (x, H - 40), 6)
            pygame.draw.circle(s, (30, 8, 40), (x, HIT_Y), 54)
            pygame.draw.circle(s, GOLD if glow < 0.3 else CREAM, (x, HIT_Y), 54, 5)
            pygame.draw.circle(s, ROSE, (x, HIT_Y), 28, 3)
        for p in self.pulses:
            col = (ROSE, GOLD, MAG)[p.kind]
            r = 34 + int(6 * math.sin(self.t * 10 + p.lane))
            if p.flash:
                r += int(20 * p.flash)
            pygame.draw.circle(s, col, (p.x, int(p.y)), r)
            pygame.draw.circle(s, CREAM, (p.x, int(p.y)), max(8, r - 16))
            pygame.draw.circle(s, col, (p.x, int(p.y)), r, 4)
        for sp in self.sparks:
            pygame.draw.circle(s, (int(sp[5]), int(sp[6]), int(sp[7])), (int(sp[0]), int(sp[1])), 5)
        title = self.font_lg.render(TITLE, True, GOLD)
        s.blit(title, title.get_rect(center=(W // 2, 72)))
        handle = self.font_sm.render(HANDLE, True, CYAN)
        s.blit(handle, handle.get_rect(center=(W // 2, 128)))
        sc = self.font_md.render(f"SCORE  {self.score}", True, CREAM)
        s.blit(sc, (90, 168))
        cb = self.font_md.render(f"COMBO  {self.combo}   BEST {self.best}", True, ROSE)
        s.blit(cb, (90, 214))
        for tag, life, ln in self.judges:
            col = GOLD if tag == "PERFECT" else (CYAN if tag == "GREAT" else (CREAM if tag == "OK" else MAG))
            img = self.font_md.render(tag, True, col)
            s.blit(img, img.get_rect(center=(LANE_XS[ln], HIT_Y - 80 - int((0.7 - life) * 40))))
        hint = self.font_sm.render("D  F  J  K   —  hit the crown rings", True, (180, 140, 190))
        s.blit(hint, hint.get_rect(center=(W // 2, H - 48)))

    def handle(self, ev):
        if ev.type == pygame.QUIT:
            self.running = False
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                self.running = False
            elif ev.key == pygame.K_r:
                self.__init__(self.record)
            else:
                for i, k in enumerate(KEYS):
                    if ev.key == k:
                        self.try_hit(i)

    def play(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            for ev in pygame.event.get():
                self.handle(ev)
            self.update(dt)
            self.draw(self.surf)
            self.screen.blit(self.surf, (0, 0))
            pygame.display.flip()

    def record_mp4(self, path: str):
        cmd = [
            "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
            "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-crf", "20", "-preset", "fast", "-movflags", "+faststart", path,
        ]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        frames = FPS * 15
        for i in range(frames):
            self.update(1.0 / FPS)
            self.draw(self.surf)
            raw = pygame.image.tostring(self.surf, "RGB")
            proc.stdin.write(raw)
            if i % 30 == 0:
                print(f"frame {i}/{frames}", flush=True)
        proc.stdin.close()
        rc = proc.wait()
        if rc != 0:
            raise SystemExit(f"ffmpeg failed: {rc}")
        print("wrote", path)


def main():
    record = "--record" in sys.argv or os.environ.get("ELBOWOS_RECORD") == "1"
    if record:
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    pygame.font.init()
    g = Game(record)
    if record:
        out = "/home/workdir/artifacts/rhodonite_pulse_ElbowOS.mp4"
        g.record_mp4(out)
    else:
        g.play()
    pygame.quit()


if __name__ == "__main__":
    main()
