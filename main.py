import pygame, sys, random, asyncio, os
from types import SimpleNamespace as NS

BASE = os.path.join(os.path.dirname(__file__), "assets")
web = sys.platform == "emscripten"
if web: import js
else: import aiohttp

pygame.init(); pygame.mixer.init()
W, H = 850, 500
scr = pygame.display.set_mode((W, H), pygame.SCALED)
pygame.display.set_caption("The Last Whisper")

P = lambda kind, n: os.path.join(BASE, kind, n)
def img(n, size=None, bg=False):
    i = pygame.image.load(P("images", n))
    i = i.convert() if bg else i
    return pygame.transform.scale(i, size) if size else i

Bush, Screech, Wrong, Right = (pygame.mixer.Sound(P("audio", n + ".ogg")) for n in ("BushMovement", "Screech1", "Wrong", "Correct"))
Wrong.set_volume(0.7); Right.set_volume(0.5)
BLACK, WHITE, GREY, RED, ORANGE, GREEN = (0,0,0), (255,255,255), (192,192,192), (255,0,0), (255,128,0), (0,255,0)
MSG, SUB, BTN, GUESS, BIG = [pygame.font.SysFont(f, s) for f, s in (("times new roman", 21), ("times new roman", 25), ("arial", 20), ("monospace", 24), ("arial", 45))]
Hang = [img(f"hangman{i}_.png") for i in range(1, 8)]
Bg1, Bg2 = img("Background1_.png", (W, H - 50), True), img("Background2.png", (W, H), True)
Mute, Unmute = img("Mute_Icon.png", (32, 32)), img("Unmute_Icon.png", (32,32))
Replay, Replay2 = img("ReplayIcon.png", (42,32)), img("ReplayIcon2.png", (42, 32))
SoundRect = pygame.Rect(W-42,H-42,32,32)

WIN, LOSE = {"Easy":300,"Medium":600,"Hard":1000}, {"Easy":100,"Medium":250,"Hard":500}
WINMSG = ["Sanity Preserved","Soul Fragments Collected","Shadows Repelled","Echoes Silenced"]
LOSEMSG = ["Sanity Drained", "Soul Fragments Lost", "Darkness Increased","Echoes Unleashed"]
POS = [(25 + round(W / 13)*(i % 13), 40 + 45 * (i // 13)) for i in range(26)]
g = NS(word="",guessed=[], limbs=0, score=0, diff="Easy", muted=False, failed=False)

# helpers
def music(n, fade=1000):
    pygame.mixer.music.load(P("audio", n + ".ogg"))
    pygame.mixer.music.set_volume(0 if g.muted else 0.5)
    if not g.muted: pygame.mixer.music.play(-1, fade_ms=fade)

def sfx(s):
    if not g.muted: s.play()

def toggle_mute():
    g.muted = not g.muted
    pygame.mixer.music.set_volume(0 if g.muted else 0.5)
    Bush.set_volume(0 if g.muted else 1); Screech.set_volume(0 if g.muted else 1)
    if not g.muted and not pygame.mixer.music.get_busy(): pygame.mixer.music.play(-1, fade_ms=50)

def put(s, cx, y): scr.blit(s, (cx - s.get_width()/2, y))

def hud(top=False): # sound icon + score
    scr.blit(Mute if g.muted else Unmute, SoundRect)
    s = SUB.render(f"Score: {g.score}", 1, WHITE)
    scr.blit(s, (W- s.get_width() - 10, 10) if top else (10, H -s.get_height() - 10))

def spaced():
    return "".join(" " if c == " " else (c.upper() if c.upper() in g.guessed else "_") + " " for c in g.word)

def quit_game(): pygame.quit(); sys.exit()

async def get_word(level):
    url = f"https://random-word-api.vercel.app/api?words=1&length={5 + 2 * 'EMH'.index(level[0])}"
    try:
        if web: data = await (await js.fetch(url)).json()
        else:
            async with aiohttp.ClientSession() as s, s.get(url, timeout=aiohttp.ClientTimeout(total=5)) as r: data = await r.json()
            if data[0].strip(): return data[0].strip()
    except Exception: pass
    g.failed = True # fallback: local word list
    try:
        with open(P("words", level + ".txt")) as f: return random.choice(f.read().splitlines()).strip()
    except FileNotFoundError: return "Fallback"

# screens
async def start():
    music("BackgroundMusic_Start")
    names = ["Easy (E)","Medium(M)","Hard(H)"]
    rects = [pygame.Rect(W/6.5-50, H/2+20+70*i, 100, 40) for i in range(3)]
    while True:
        scr.fill(BLACK)
        scr.blit(Bg1, (0, 0))
        Bush.fadeout(500)

        for r, n in zip(rects, names):
            pygame.draw.rect(scr, GREY, r)

            if r.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(scr, RED, r, 3)

            l = BTN.render(n, 1, RED)
            scr.blit(l, l.get_rect(center=r.center))

        hud(True)
        pygame.display.update()
        await asyncio.sleep(0)

        for e in pygame.event.get():

            if e.type == pygame.QUIT:
                quit_game()

            if e.type == pygame.KEYDOWN:
                d = {
                    pygame.K_e: "Easy",
                    pygame.K_m: "Medium",
                    pygame.K_h: "Hard"
                }.get(e.key)

                if d:
                    put(
                        SUB.render("Loading...", 1, RED),
                        W/1.3,
                        H/2+170
                    )
                    pygame.display.update()
                    pygame.mixer.music.fadeout(1000)
                    sfx(Bush)
                    await asyncio.sleep(1)
                    return d

            if e.type == pygame.MOUSEBUTTONDOWN:

                if SoundRect.collidepoint(e.pos):
                    toggle_mute()
                    continue

                d = next(
                    (
                        n.split()[0]
                        for r, n in zip(rects, names)
                        if r.collidepoint(e.pos)
                    ),
                    None
                )

                if d:
                    put(
                        SUB.render("Loading...", 1, RED),
                        W/1.3,
                        H/2+170
                    )
                    pygame.display.update()
                    pygame.mixer.music.fadeout(1000)
                    sfx(Bush)
                    await asyncio.sleep(1)
                    return d

def draw():
    scr.blit(Bg2, (0, 0))

    for i, (x, y) in enumerate(POS):
        l = chr(65 + i)

        b, r, c, t = (
            (20, 18, GREY, BLACK)
            if l not in g.guessed
            else (22, 20, GREEN, BLACK)
            if l in g.word.upper()
            else (20, 20, RED, WHITE)
        )

        pygame.draw.circle(scr, BLACK, (x, y), b)
        pygame.draw.circle(scr, c, (x, y), r)

        s = BTN.render(l, 1, t)
        scr.blit(s, s.get_rect(center=(x, y)))

    put(GUESS.render(spaced(), 1, WHITE), W/2, 400)

    scr.blit(
        Hang[g.limbs],
        (W/2 - Hang[g.limbs].get_width()/2 + 20, 150)
    )

    hud()

    if g.failed:
        put(
            MSG.render(
                "The summoning failed... an ancient scroll whispered instead.",
                1,
                ORANGE
            ),
            W/2,
            H-50
        )

    pygame.display.update()

async def end(won):
    pygame.event.set_blocked(
        [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.KEYDOWN]
    )
    pygame.event.clear()

    d = g.diff

    if won:
        lines = [
            "you broke the curse",
            "the darkness retreats",
            "you survive....for now",
            f"+{WIN[d]} {random.choice(WINMSG)}"
        ]
        g.score += WIN[d]
        music("BackgroundMusic_Win")
    else:
        lines = [
            "the whisper fades",
            "and silence falls",
            "as darkness claims another....",
            "the cursed word was:",
            g.word.upper(),
            f"-{LOSE[d]} {random.choice(LOSEMSG)}"
        ]
        g.score -= LOSE[d]
        music("BackgroundMusic_Lose")

    labels = [
        BIG.render(t, 1, WHITE).convert_alpha()
        for t in lines
    ]

    y0 = 80 if won else 50
    y1 = 275 if won else 245

    for n, lab in enumerate(labels):
        for a in range(0, 256, 10):
            lab.set_alpha(a)
            scr.blit(Bg2, (0, 0))
            hud()

            for i in range(n + 1):
                y = y0 + 50 * i if i < 3 else y1 + 50 * (i - 3)
                put(labels[i], W/2, y)

            pygame.display.update()
            await asyncio.sleep(0.03)

        await asyncio.sleep(0.5)

    pygame.event.set_allowed(
        [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.KEYDOWN]
    )

    t = "Try again (R)....if you dare"
    rr = SUB.render(t, 1, WHITE).get_rect(center=(W/2, 470))
    box = rr.inflate(84, 10)

    while True:
        hov = box.collidepoint(pygame.mouse.get_pos())

        pygame.draw.rect(
            scr,
            ORANGE if hov else BLACK,
            rr.inflate(89, 15),
            border_radius=25
        )
        pygame.draw.rect(
            scr,
            BLACK,
            box,
            border_radius=25
        )

        scr.blit(
            Replay2 if hov else Replay,
            (rr.left - 22, rr.centery - 16)
        )

        scr.blit(
            SUB.render(t, 1, ORANGE if hov else WHITE),
            (rr.left + 15, rr.top)
        )

        pygame.display.update()
        await asyncio.sleep(0)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                quit_game()

            if (
                e.type == pygame.KEYDOWN
                and e.key == pygame.K_r
            ) or (
                e.type == pygame.MOUSEBUTTONDOWN
                and box.collidepoint(e.pos)
            ):
                pygame.mixer.music.fadeout(1000)
                sfx(Bush)
                return await reset()

            if (
                e.type == pygame.MOUSEBUTTONDOWN
                and SoundRect.collidepoint(e.pos)
            ):
                toggle_mute()

async def reset():
    g.failed, g.guessed, g.limbs = False, [], 0
    g.diff = await start()
    g.word = await get_word(g.diff)
    Bush.fadeout(500); music("BackgroundMusic_Gameplay", 500)

# game loop 
async def guess(l):
    if l in g.guessed: return
    g.guessed.append(l)
    ok = l.lower() in g.word.lower()
    sfx(Right if ok else Wrong)
    if not ok:
        g.limbs += 1 
    lost, won = g.limbs == 6, ok and "_" not in spaced()
    if lost or won:
        pygame.mixer.music.fadeout(1000)
        if lost: sfx(Screech)
        await end(won)

async def main():
    await reset()
    while True:
        draw(); await asyncio.sleep(0)
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE): pygame.quit(); return
            if e.type == pygame.KEYDOWN and pygame.K_a <= e.key <= pygame.K_z: await guess(chr(e.key).upper())
            if e.type == pygame.MOUSEBUTTONDOWN:
                if SoundRect.collidepoint(e.pos): toggle_mute()
                for i, (x, y) in enumerate(POS):
                    if chr(65 + i) not in g.guessed and pygame.Rect(x - 20, y - 20, 40, 40).collidepoint(e.pos):
                        await guess(chr(65 + i)); break
                    
if __name__ == "__main__":
    if web: asyncio.ensure_future(main())
    else: asyncio.run(main())