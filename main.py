#!/usr/bin/env python3
"""Procedurally draw a deterministic 1024x1024 newspaper front page."""
import math
import os
import struct
import zlib

W = H = 1024
PAPER = (245, 238, 222)
INK = (28, 43, 61)
RED = (174, 48, 43)
GREY = (104, 105, 101)
PALE = (235, 225, 207)
WHITE = (255, 250, 239)
BLUE = (66, 101, 126)
SEA = (114, 153, 164)
SNOW = (239, 239, 229)

FONT = {
    'A': ('01110','10001','10001','11111','10001','10001','10001'),
    'B': ('11110','10001','10001','11110','10001','10001','11110'),
    'C': ('01111','10000','10000','10000','10000','10000','01111'),
    'D': ('11110','10001','10001','10001','10001','10001','11110'),
    'E': ('11111','10000','10000','11110','10000','10000','11111'),
    'F': ('11111','10000','10000','11110','10000','10000','10000'),
    'G': ('01111','10000','10000','10111','10001','10001','01111'),
    'H': ('10001','10001','10001','11111','10001','10001','10001'),
    'I': ('11111','00100','00100','00100','00100','00100','11111'),
    'J': ('00111','00010','00010','00010','10010','10010','01100'),
    'K': ('10001','10010','10100','11000','10100','10010','10001'),
    'L': ('10000','10000','10000','10000','10000','10000','11111'),
    'M': ('10001','11011','10101','10101','10001','10001','10001'),
    'N': ('10001','11001','10101','10011','10001','10001','10001'),
    'O': ('01110','10001','10001','10001','10001','10001','01110'),
    'P': ('11110','10001','10001','11110','10000','10000','10000'),
    'Q': ('01110','10001','10001','10001','10101','10010','01101'),
    'R': ('11110','10001','10001','11110','10100','10010','10001'),
    'S': ('01111','10000','10000','01110','00001','00001','11110'),
    'T': ('11111','00100','00100','00100','00100','00100','00100'),
    'U': ('10001','10001','10001','10001','10001','10001','01110'),
    'V': ('10001','10001','10001','10001','10001','01010','00100'),
    'W': ('10001','10001','10001','10101','10101','10101','01010'),
    'X': ('10001','10001','01010','00100','01010','10001','10001'),
    'Y': ('10001','10001','01010','00100','00100','00100','00100'),
    'Z': ('11111','00001','00010','00100','01000','10000','11111'),
    '0': ('01110','10001','10011','10101','11001','10001','01110'),
    '1': ('00100','01100','00100','00100','00100','00100','01110'),
    '2': ('01110','10001','00001','00010','00100','01000','11111'),
    '3': ('11110','00001','00001','01110','00001','00001','11110'),
    '4': ('00010','00110','01010','10010','11111','00010','00010'),
    '5': ('11111','10000','10000','11110','00001','00001','11110'),
    '6': ('01110','10000','10000','11110','10001','10001','01110'),
    '7': ('11111','00001','00010','00100','01000','01000','01000'),
    '8': ('01110','10001','10001','01110','10001','10001','01110'),
    '9': ('01110','10001','10001','01111','00001','00001','01110'),
    '.': ('00000','00000','00000','00000','00000','00110','00110'),
    ',': ('00000','00000','00000','00000','00110','00110','00100'),
    ':': ('00000','00110','00110','00000','00110','00110','00000'),
    ';': ('00000','00110','00110','00000','00110','00110','00100'),
    '!': ('00100','00100','00100','00100','00100','00000','00100'),
    '?': ('01110','10001','00001','00010','00100','00000','00100'),
    "'": ('00100','00100','00000','00000','00000','00000','00000'),
    '"': ('01010','01010','00000','00000','00000','00000','00000'),
    '-': ('00000','00000','00000','11111','00000','00000','00000'),
    '(': ('00010','00100','01000','01000','01000','00100','00010'),
    ')': ('01000','00100','00010','00010','00010','00100','01000'),
    '/': ('00001','00010','00010','00100','01000','01000','10000'),
    '&': ('01100','10010','10100','01000','10101','10010','01101'),
    '%': ('11001','11010','00010','00100','01000','01011','10011'),
    '+': ('00000','00100','00100','11111','00100','00100','00000'),
    '=': ('00000','11111','00000','11111','00000','00000','00000'),
    '*': ('00000','10101','01110','11111','01110','10101','00000'),
    '$': ('00100','01111','10100','01110','00101','11110','00100'),
    '#': ('01010','11111','01010','01010','11111','01010','00000'),
    '@': ('01110','10001','10111','10101','10111','10000','01111'),
    '_': ('00000','00000','00000','00000','00000','00000','11111'),
    ' ': ('00000',)*7,
}

class Canvas:
    def __init__(self, w, h, color):
        self.w, self.h = w, h
        self.p = bytearray(color * (w * h))

    def pixel(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.p[i:i+3] = bytes(color)

    def rect(self, x, y, w, h, color, fill=True, outline=None, thickness=1):
        if fill:
            x0, y0, x1, y1 = max(0, x), max(0, y), min(self.w, x+w), min(self.h, y+h)
            row = bytes(color) * max(0, x1-x0)
            for yy in range(y0, y1):
                i = (yy*self.w+x0)*3
                self.p[i:i+len(row)] = row
        if outline:
            for t in range(thickness):
                self.line(x+t, y+t, x+w-1-t, y+t, outline)
                self.line(x+t, y+h-1-t, x+w-1-t, y+h-1-t, outline)
                self.line(x+t, y+t, x+t, y+h-1-t, outline)
                self.line(x+w-1-t, y+t, x+w-1-t, y+h-1-t, outline)

    def line(self, x0, y0, x1, y1, color, width=1):
        x0, y0, x1, y1 = int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1))
        dx, dy = abs(x1-x0), -abs(y1-y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            r = max(0, width//2)
            self.rect(x0-r, y0-r, width, width, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2*err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, color, fill=True, outline=None, thickness=1):
        for yy in range(max(0, cy-r), min(self.h, cy+r+1)):
            for xx in range(max(0, cx-r), min(self.w, cx+r+1)):
                d = (xx-cx)**2 + (yy-cy)**2
                if fill and d <= r*r:
                    self.pixel(xx, yy, color)
                elif outline and (r-thickness)**2 <= d <= r*r:
                    self.pixel(xx, yy, outline)

    def polygon(self, pts, color, fill=True, outline=None, thickness=1):
        if fill:
            ymin = max(0, min(y for _, y in pts))
            ymax = min(self.h-1, max(y for _, y in pts))
            for yy in range(ymin, ymax+1):
                xs = []
                for i, (x1,y1) in enumerate(pts):
                    x2,y2 = pts[(i+1) % len(pts)]
                    if (y1 <= yy < y2) or (y2 <= yy < y1):
                        xs.append(int(x1 + (yy-y1)*(x2-x1)/(y2-y1)))
                xs.sort()
                for i in range(0, len(xs)-1, 2):
                    self.line(xs[i], yy, xs[i+1], yy, color)
        if outline:
            for i, (x1,y1) in enumerate(pts):
                x2,y2 = pts[(i+1) % len(pts)]
                self.line(x1,y1,x2,y2,outline,thickness)

    def starburst(self, cx, cy, outer, inner, color, rays=8):
        pts = []
        for i in range(rays*2):
            angle = -1.5707963267948966 + i*3.141592653589793/rays
            r = outer if i % 2 == 0 else inner
            pts.append((int(cx + r*math.cos(angle)), int(cy + r*math.sin(angle))))
        self.polygon(pts, color)

    def text(self, x, y, value, scale=2, color=INK):
        value = value.upper().replace('–','-').replace('—','-')
        cursor = x
        for ch in value:
            glyph = FONT.get(ch, FONT[' '])
            for gy, row in enumerate(glyph):
                for gx, bit in enumerate(row):
                    if bit == '1':
                        self.rect(cursor + gx*scale, y + gy*scale, scale, scale, color)
            cursor += 6*scale
        return cursor

    def text_width(self, text, scale):
        return len(text) * 6 * scale

    def wrap(self, text, max_width, scale):
        text = text.upper().replace('–','-').replace('—','-')
        cap = max(1, max_width // (6*scale))
        words = text.split()
        lines, line = [], ''
        for word in words:
            if len(word) > cap:
                if line:
                    lines.append(line); line = ''
                while len(word) > cap:
                    lines.append(word[:cap]); word = word[cap:]
            candidate = word if not line else line + ' ' + word
            if len(candidate) <= cap:
                line = candidate
            else:
                if line: lines.append(line)
                line = word
        if line: lines.append(line)
        return lines

    def paragraph(self, x, y, text, max_width, scale=2, color=INK, leading=None):
        step = leading if leading is not None else 8*scale
        lines = self.wrap(text, max_width, scale)
        for line in lines:
            self.text(x, y, line, scale, color)
            y += step
        return y, len(lines)

    def png(self):
        def chunk(kind, data):
            return struct.pack('>I',len(data)) + kind + data + struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
        raw = b''.join(b'\x00' + self.p[y*self.w*3:(y+1)*self.w*3] for y in range(self.h))
        return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB',self.w,self.h,8,2,0,0,0)) + chunk(b'IDAT',zlib.compress(raw,9)) + chunk(b'IEND',b'')


def centered(c, y, text, scale, color, area=(0,W)):
    x = area[0] + (area[1]-area[0]-c.text_width(text,scale))//2
    c.text(x,y,text,scale,color)


def panel(c, x, y, w, h):
    c.rect(x,y,w,h,WHITE,outline=INK,thickness=2)
    c.line(x+8,y+7,x+w-9,y+7,PALE,1)


def draw_lead_art(c, x, y, w, h):
    """Gulf island with a missile site, drones inbound, intercept bursts, sea below."""
    c.rect(x,y,w,h,(228,222,205))
    horizon = y + int(h*.60)
    # Sea fills everything below the horizon, with a lighter band at the shore.
    c.rect(x,horizon,w,h-(horizon-y),(107,148,160))
    for i in range(3):
        c.line(x,horizon+4+i*3,x+w,horizon+4+i*3,(126,165,175),1)
    # Island: one hump rising out of the water, not a coastline strip.
    ix0, ix1 = x+46, x+w-52
    mid = (ix0+ix1)//2
    plateau = horizon-int(h*.30)
    c.polygon([(ix0,horizon+3),(x+78,horizon-int(h*.16)),(x+108,plateau),(ix1-86,plateau),
               (ix1-40,horizon-int(h*.16)),(ix1,horizon+3)],(206,183,134),outline=(124,104,76))
    # Shaded eastern flank.
    c.polygon([(mid+18,plateau),(ix1-86,plateau),(ix1-40,horizon-int(h*.16)),(ix1,horizon+3),(mid+40,horizon+3)],(185,162,116))
    # Beach line and surf.
    c.line(ix0+4,horizon+3,ix1-4,horizon+3,(238,228,205),2)
    c.line(ix0-14,horizon+9,ix1+14,horizon+9,WHITE,2)
    # Missile facility: bunker, radar dish, two launcher rails with ready missiles.
    bx, by = mid-58, plateau-4
    c.rect(bx,by,104,20,(118,108,88),outline=INK)
    c.rect(bx+6,by-10,26,10,(150,140,116),outline=INK)
    c.line(bx+19,by-10,bx+19,by-17,INK,2)
    c.circle(bx+19,by-19,4,(156,152,136),outline=INK)
    c.line(bx+74,by,bx+74,by-13,INK,3)
    c.polygon([(bx+68,by-13),(bx+80,by-13),(bx+74,by-21)],RED)
    for mx in (bx+36,bx+52):
        c.line(mx,by+1,mx+8,by-30,INK,4)
        c.polygon([(mx+4,by-33),(mx+13,by-31),(mx+9,by-20)],WHITE,outline=INK)
        c.circle(mx+11,by-34,3,RED)
    for wx in range(bx+8,bx+98,13):
        c.rect(wx,by+5,5,5,(72,70,60))
    c.text(bx+2,by+9,'QESHM',1,(238,230,210))
    # Three drones inbound from the upper left, each with a dotted track.
    for dx,dy,tx,ty in [(x+30,y+18,x+112,y+52),(x+74,y+8,x+140,y+44),(x+150,y+26,x+186,y+58)]:
        for i in range(1,7):
            px=dx+(tx-dx)*i//7; py=dy+(ty-dy)*i//7
            c.circle(px,py,2,(178,66,56))
        c.line(dx-9,dy,dx+9,dy,INK,3)
        c.polygon([(dx-2,dy),(dx-11,dy-6),(dx-9,dy+5)],INK)
        c.polygon([(dx+2,dy),(dx+11,dy-6),(dx+9,dy+5)],INK)
        c.line(dx,dy-3,dx+1,dy-9,INK,2)
        c.circle(dx+1,dy-9,2,RED)
    # Intercepts detonating in the air above the island.
    for cx,cy,o,i in [(x+286,y+44,21,8),(x+332,y+24,14,6)]:
        c.starburst(cx,cy,o,i,RED,8)
        c.circle(cx,cy,5,(247,214,120))
    c.starburst(x+264,y+70,9,4,(247,214,120),6)
    # Whitecaps on the open water.
    for yy in [horizon+16,horizon+30,horizon+44]:
        c.line(x+12,yy,x+58,yy-2,WHITE,2)
        c.line(x+w-72,yy+2,x+w-14,yy,WHITE,2)


def draw_ukraine_art(c, x, y, w, h):
    """Suspension bridge with a collapsed middle span sinking into the strait."""
    c.rect(x,y,w,h,(222,226,219))
    water_y=y+int(h*.60)
    c.rect(x,water_y,w,h-(water_y-y),(107,148,160))
    left=x+52; right=x+w-52
    deck_y=water_y-15
    gap0=left+30; gap1=right-42
    # Towers, main cable.
    c.line(left,y+5,left,water_y+2,INK,5); c.line(right,y+5,right,water_y+2,INK,5)
    c.line(left,y+6,right,y+6,INK,3)
    c.line(left-16,y+18,left,y+6,INK,2); c.line(right+16,y+18,right,y+6,INK,2)
    # Hangers only on the surviving spans, so the hole is unmistakable.
    for px in list(range(left+8,gap0,15))+list(range(gap1+8,right,15)):
        c.line(px,y+7,px,deck_y,(96,124,134),1)
    # Intact deck slabs, with piers down to the water.
    c.rect(x+2,deck_y,gap0-(x+2),8,INK)
    c.rect(gap1,deck_y,x+w-2-gap1,8,INK)
    for px in range(x+10,gap0-6,24): c.line(px,deck_y+8,px,water_y,(74,80,82),2)
    for px in range(gap1+6,x+w-8,24): c.line(px,deck_y+8,px,water_y,(74,80,82),2)
    # Broken ends: jagged stubs sagging at the gap edges.
    c.polygon([(gap0-16,deck_y),(gap0,deck_y),(gap0-4,deck_y+13),(gap0-14,deck_y+10)],(52,56,56))
    c.polygon([(gap1,deck_y),(gap1+14,deck_y),(gap1+10,deck_y+11),(gap1+2,deck_y+14)],(52,56,56))
    # The fallen span: one slab tilted steeply and half-submerged.
    c.polygon([(gap0-6,deck_y+8),(gap0+16,deck_y+3),(gap0+58,water_y+14),(gap0+30,water_y+20)],(74,80,82),outline=(46,50,50))
    c.line(gap0-8,deck_y+6,gap0+20,deck_y+2,(112,118,116),2)
    # A short piece still hanging by a cable, swinging free.
    c.line(gap1-4,y+8,gap1-16,deck_y+16,(96,124,134),2)
    c.polygon([(gap1-22,deck_y+16),(gap1-6,deck_y+12),(gap1-8,deck_y+22),(gap1-24,deck_y+24)],(74,80,82),outline=(46,50,50))
    # Smoke drifting up out of the gap.
    for cx,cy,r in [(gap0+2,y+22,10),(gap0+16,y+13,13),(gap0+32,y+24,9)]:
        c.circle(cx,cy,r,(150,148,138))
    # Splash and ripples where the span went in.
    c.line(gap0+14,water_y+6,gap0+70,water_y+6,WHITE,2)
    c.line(gap0+22,water_y+12,gap0+62,water_y+12,WHITE,2)
    for yy in [water_y+22,water_y+30]:
        c.line(x+8,yy,x+64,yy-2,WHITE,2)
        c.line(x+w-70,yy+2,x+w-8,yy,WHITE,2)


def draw_flags_art(c, x, y, w, h):
    c.rect(x,y,w,h,(232,226,211))
    skyline_y=y+h-8
    # simple Shenzhen skyline.
    for bx,bw,bh,col in [(x+2,30,28,(169,174,165)),(x+35,25,39,(156,165,161)),(x+63,32,24,(175,174,160)),(x+w-92,26,31,(169,174,165)),(x+w-62,25,42,(156,165,161)),(x+w-33,31,27,(175,174,160))]:
        c.rect(bx,skyline_y-bh,bw,bh,col,outline=INK)
        for wy in range(skyline_y-bh+5,skyline_y-3,8):
            c.line(bx+5,wy,bx+bw-5,wy,(221,213,194),1)
    c.line(x,skyline_y,x+w,skyline_y,INK,2)
    centers=[x+83,x+w//2,x+w-83]
    pole_top=y+4
    for cx in centers:
        c.line(cx,pole_top,cx,skyline_y,INK,2)
    # China flag, red with yellow star.
    c.rect(centers[0]+2,pole_top+4,54,30,(190,39,43))
    c.starburst(centers[0]+12,pole_top+13,6,3,(248,211,82),5)
    # Russia tricolor.
    c.rect(centers[1]+2,pole_top+4,58,10,(247,244,231))
    c.rect(centers[1]+2,pole_top+14,58,10,(61,91,151))
    c.rect(centers[1]+2,pole_top+24,58,10,(184,56,52))
    # US flag, stripes and blue canton.
    fx=centers[2]+2
    c.rect(fx,pole_top+4,58,30,(247,244,231))
    for sy in range(0,30,6): c.rect(fx,pole_top+4+sy,58,3,(188,54,50))
    c.rect(fx,pole_top+4,25,16,(48,70,111))
    for sy in range(pole_top+7,pole_top+18,5):
        for sx in range(fx+4,fx+23,6): c.circle(sx,sy,1,WHITE)


def draw_virus(c, cx, cy, r, col):
    for i in range(12):
        a=i*math.pi/6
        x1=int(cx+(r-2)*math.cos(a)); y1=int(cy+(r-2)*math.sin(a))
        x2=int(cx+(r+9)*math.cos(a)); y2=int(cy+(r+9)*math.sin(a))
        c.line(x1,y1,x2,y2,col,3)
        c.circle(x2,y2,3,col)
    c.circle(cx,cy,r,col)
    c.circle(cx-5,cy-3,3,(232,174,153)); c.circle(cx+6,cy+4,3,(232,174,153))


def draw_plane_art(c, x, y, w, h):
    c.rect(x,y,w,h,(226,230,227))
    ground=y+h-4
    # distant snow ridges.
    c.polygon([(x,ground-9),(x+int(w*.18),ground-24),(x+int(w*.33),ground-11),(x+int(w*.50),ground-28),(x+int(w*.70),ground-10),(x+int(w*.88),ground-22),(x+w,ground-9),(x+w,ground),(x,ground)],SNOW)
    c.line(x,ground-9,x+w,ground-9,(130,145,145),2)
    # descending transport plane silhouette.
    s=min(1.8,(h-10)/34.0)
    px=x+w//2; py=y+int(h*.24)
    def P(dx,dy): return (px+int(dx*s), py+int(dy*s))
    # Descent path, dotted, running down from the upper left to the tail.
    ax, ay = x+16, y+6
    bx2, by2 = px-44*s, py+6*s
    for i in range(1,8):
        c.circle(int(ax+(bx2-ax)*i/8), int(ay+(by2-ay)*i/8), 2, (152,156,154))
    c.polygon([P(-5,3),P(32,10),P(47,9),P(49,13),P(27,17),P(15,23),P(10,21),P(14,15),P(-13,12),P(-31,23),P(-36,21),P(-25,10),P(-43,6),P(-44,3),P(-7,5)],INK)
    # Tail fin highlight so the type reads as a heavy transport.
    c.polygon([P(-43,6),P(-36,21),P(-30,20),P(-34,7)],(66,78,90))
    c.line(px-45*s,py+5*s,px-58*s,py-3*s,RED,2)
    c.circle(int(px-59*s),int(py-4*s),2,RED)


def make_poster():
    c=Canvas(W,H,PAPER)
    # Broadsheet double border.
    c.rect(13,13,998,998,PAPER,fill=False,outline=INK,thickness=3)
    c.rect(21,21,982,982,PAPER,fill=False,outline=RED,thickness=1)
    centered(c,31,'THE WORLD IN ONE DAY',7,INK)
    c.rect(30,101,964,52,RED)
    centered(c,111,'WEDNESDAY, 18 NOVEMBER 2026',5,WHITE)

    # Lead feature.
    lx,ly,lw,lh=30,162,964,250
    panel(c,lx,ly,lw,lh)
    c.text(lx+17,ly+15,'LEAD STORY - MIDDLE EAST',2,RED)
    lead_head="US STRIKES IRAN'S QESHM ISLAND"
    hx,hy,hw=lx+17,ly+39,520
    lines=c.wrap(lead_head,hw,5)
    for i,line in enumerate(lines): c.text(hx,hy+i*41,line,5,INK)
    deck="US jets hit a Revolutionary Guard missile site on Qeshm Island. Iran answers with drones on a US radar in Bahrain - intercepted - and on Patriot batteries in Kuwait."
    deck_y=hy+len(lines)*41+6
    c.paragraph(lx+17,deck_y,deck,hw,2,INK,leading=16)
    # Red tag line, knocked out in white so it reads at thumbnail size.
    tag="BAHRAIN'S 3RD ATTACK IN A WEEK"
    tag_w=c.text_width(tag,2)+22
    c.rect(lx+17,ly+lh-32,tag_w,20,RED)
    c.text(lx+28,ly+lh-28,tag,2,WHITE)
    draw_lead_art(c,lx+555,ly+15,394,lh-30)

    # Two regional reports.
    ry,rh=422,186
    p1x,p1w=30,474; p2x,p2w=512,482
    panel(c,p1x,ry,p1w,rh); panel(c,p2x,ry,p2w,rh)
    c.text(p1x+14,ry+12,'UKRAINE',2,RED)
    c.text(p1x+14,ry+32,'KERCH BRIDGE HIT AGAIN',3,INK)
    ukdeck="Ukraine strikes the Crimea bridge for a second day; part of the road span drops into the Kerch Strait."
    c.paragraph(p1x+14,ry+58,ukdeck,p1w-28,2,INK,leading=16)
    draw_ukraine_art(c,p1x+12,ry+rh-64,p1w-24,56)

    c.text(p2x+14,ry+12,'ASIA - APEC SUMMIT',2,RED)
    asia_head='XI AND PUTIN IN SHENZHEN'
    asia_lines=c.wrap(asia_head,p2w-28,3)
    for i,line in enumerate(asia_lines): c.text(p2x+14,ry+32+i*24,line,3,INK)
    asia_deck="Xi opens the APEC summit denouncing protectionism; Putin arrives for talks. Trump lands Thursday for the first Xi-Trump-Putin meeting."
    asia_y=ry+32+len(asia_lines)*24+4
    c.paragraph(p2x+14,asia_y,asia_deck,p2w-28,2,INK,leading=16)
    draw_flags_art(c,p2x+12,ry+rh-58,p2w-24,52)

    # Three compact columns: two thirds for the single-story panels,
    # a wider third for the brief so its list breathes.
    by,bh=612,338
    cols=[(30,290),(330,290),(630,364)]
    for x,w in cols: panel(c,x,by,w,bh)
    x,w=cols[0]
    c.text(x+12,by+12,'HEALTH - DR CONGO',2,RED)
    for i,line in enumerate(c.wrap('EBOLA CASES DOUBLE',w-24,3)):
        c.text(x+12,by+34+i*24,line,3,INK)
    health="The UN: over 11,000 cases and 5,400 deaths in three months. In Bunia and Beni, three in four infected children under five die."
    c.paragraph(x+12,by+88,health,w-24,2,INK,leading=16)
    c.line(x+12,by+244,x+w-13,by+244,PALE,1)
    draw_virus(c,x+76,by+288,25,RED); draw_virus(c,x+196,by+296,18,(198,83,68))

    x,w=cols[1]
    c.text(x+12,by+12,'DISASTER - SIBERIA',2,RED)
    disaster_head='MILITARY PLANE CRASH KILLS 19'
    dis_lines=c.wrap(disaster_head,w-24,3)
    for i,line in enumerate(dis_lines): c.text(x+12,by+34+i*24,line,3,INK)
    disaster="A Russian military aircraft crashes in the Kemerovo region of Siberia; all 19 aboard are dead."
    dis_y=by+34+len(dis_lines)*24+8
    c.paragraph(x+12,dis_y,disaster,w-24,2,INK,leading=16)
    draw_plane_art(c,x+12,by+232,w-24,90)

    x,w=cols[2]
    c.text(x+12,by+12,'IN BRIEF',2,RED)
    c.text(x+12,by+30,'AROUND THE WORLD',3,INK)
    c.line(x+12,by+58,x+w-13,by+58,RED,2)
    briefs=[
        'US SENATE: Democrat Mary Peltola wins Alaska - Democrats hold 56 seats.',
        'ISRAEL: President Herzog asks ex-army chief Eisenkot to form a government, bypassing Netanyahu.',
        'GAZA: Australia, Canada, Italy and the UK demand Israel open aid routes as cold and floods hit the camps.',
        'PAPUA NEW GUINEA: magnitude 6.0 earthquake strikes.',
        'MARKETS: European shares slide - DAX -2.08%, CAC 40 -1.62% - on Gulf tension.',
    ]
    yy=by+64
    for item in briefs:
        c.circle(x+14,yy+5,3,RED)
        yy,_=c.paragraph(x+25,yy,item,w-37,2,INK,leading=15)
        yy+=3

    centered(c,968,'ALL EVENTS OF WEDNESDAY, 18 NOVEMBER 2026',2,GREY)
    return c.png()


def main():
    outdir=os.environ.get('MAKEFUN_OUTPUT_DIR','/output')
    os.makedirs(outdir,exist_ok=True)
    path=os.path.join(outdir,'entry.png')
    with open(path,'wb') as f: f.write(make_poster())
    print(path)

if __name__=='__main__':
    main()
