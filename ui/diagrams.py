"""Small inline-SVG diagrams for the introduction page.

Angles passed to the helpers are SCREEN angles in degrees (SVG y-axis points down):
0° = right, 90° = down, -90° = up. Increasing angle = clockwise on screen.
Colours: strokes/text use currentColor so the drawings work in light and dark theme.
"""
import math

ACCENT = "#e8590c"   # sun and rays
BLUE = "#1c7ed6"     # angles
LINE = "currentColor"


def _pt(cx, cy, r, a):
    return cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))


def _f(v):
    return f"{v:.1f}"


def _line(p, q, color=LINE, width=2, dash=None, opacity=1.0, marker=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = f' marker-end="url(#{marker})"' if marker else ""
    return (f'<line x1="{_f(p[0])}" y1="{_f(p[1])}" x2="{_f(q[0])}" y2="{_f(q[1])}" '
            f'stroke="{color}" stroke-width="{width}" opacity="{opacity}"{d}{m}/>')


def _arc(cx, cy, r, a0, a1, color=BLUE, width=2.5):
    x0, y0 = _pt(cx, cy, r, a0)
    x1, y1 = _pt(cx, cy, r, a1)
    large = 1 if (a1 - a0) % 360 > 180 else 0
    return (f'<path d="M {_f(x0)} {_f(y0)} A {r} {r} 0 {large} 1 {_f(x1)} {_f(y1)}" '
            f'fill="none" stroke="{color}" stroke-width="{width}"/>')


def _text(x, y, s, color=LINE, size=14, anchor="middle", weight="normal", opacity=1.0):
    return (f'<text x="{_f(x)}" y="{_f(y)}" fill="{color}" font-size="{size}" '
            f'text-anchor="{anchor}" font-weight="{weight}" opacity="{opacity}" '
            f'font-family="sans-serif">{s}</text>')


def _dot(p, r=4, color=LINE):
    return f'<circle cx="{_f(p[0])}" cy="{_f(p[1])}" r="{r}" fill="{color}"/>'


def _sun(p, r=13):
    return (f'<circle cx="{_f(p[0])}" cy="{_f(p[1])}" r="{r}" fill="{ACCENT}" '
            f'stroke="{ACCENT}" stroke-width="2" fill-opacity="0.85"/>')


def _arrow_defs(uid, color=LINE):
    return (f'<defs><marker id="{uid}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
            f'markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" '
            f'fill="{color}"/></marker></defs>')


def _svg(w, h, body, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" '
            f'aria-label="{label}" style="width:100%;max-width:{w}px;height:auto;display:block;'
            f'margin:0 auto;">{body}</svg>')


def zenith_altitude():
    """Side view: zenith angle θz and solar altitude αs."""
    O = (210, 250)
    ray = _pt(*O, 200, -50)
    b = [
        _line((40, 250), (380, 250), width=2),
        _text(340, 270, "Horizon", anchor="middle", size=13),
        _line(O, (210, 40), dash="6 5", opacity=0.7),
        _text(216, 32, "Zenith (vertical)", anchor="start", size=13),
        _line(O, ray, color=ACCENT, width=3),
        _sun(ray),
        _text(ray[0] + 6, ray[1] - 20, "Sun", color=ACCENT, size=13),
        _arc(*O, 70, -50, 0),
        _arc(*O, 98, -90, -50),
        _dot(O),
        _text(210, 272, "Observer", size=13),
    ]
    x, y = _pt(*O, 92, -22)
    b.append(_text(x, y + 5, "αs", color=BLUE, weight="bold", size=16))
    x, y = _pt(*O, 122, -70)
    b.append(_text(x, y + 5, "θz", color=BLUE, weight="bold", size=16))
    b.append(_text(210, 292, "αs + θz = 90°", size=14, weight="bold"))
    return _svg(420, 300, "".join(b), "Zenith angle and solar altitude angle, side view")


def azimuth_topview():
    """Top view: solar azimuth γs measured from south, west positive."""
    C = (210, 165)
    R = 115
    ray_end = _pt(*C, R, 130)   # 40° from south toward west
    b = [
        f'<circle cx="{C[0]}" cy="{C[1]}" r="{R}" fill="none" stroke="{LINE}" stroke-width="1.5" opacity="0.4"/>',
        _line((C[0] - R - 8, C[1]), (C[0] + R + 8, C[1]), opacity=0.25, width=1),
        _line(C, (C[0], C[1] + R), dash="6 5", opacity=0.8),
        _text(C[0], C[1] - R - 10, "N", weight="bold"),
        _text(C[0], C[1] + R + 22, "S (γs = 0°)", weight="bold"),
        _text(C[0] + R + 16, C[1] + 5, "E", weight="bold"),
        _text(C[0] - R - 18, C[1] + 5, "W", weight="bold"),
        _line(C, ray_end, color=ACCENT, width=3),
        _sun(ray_end, r=10),
        _text(ray_end[0] - 16, ray_end[1] + 5, "Sun", color=ACCENT, size=13, anchor="end"),
        _arc(*C, 62, 90, 130),
        _dot(C),
    ]
    x, y = _pt(*C, 82, 112)
    b.append(_text(x - 4, y + 4, "γs", color=BLUE, weight="bold", size=16))
    b.append(_text(210, 322, "Top view: west of south is positive, east of south is negative", size=13))
    return _svg(420, 335, "".join(b), "Solar azimuth angle, top view")


def slope_incidence():
    """Tilted surface: slope β and angle of incidence θ (between ray and normal)."""
    C = (200, 190)
    beta = 35
    normal_a = -90 + beta          # normal tilts toward the sun side
    ray_a = -20
    d = _pt(0, 0, 1, beta)
    p_left = (C[0] - 135 * d[0], C[1] - 135 * d[1])
    p_right = (C[0] + 135 * d[0], C[1] + 135 * d[1])
    n_end = _pt(*C, 125, normal_a)
    ray_end = _pt(*C, 195, ray_a)
    b = [
        _arrow_defs("sa_arrow"),
        _line((40, 190), (390, 190), dash="6 5", opacity=0.7),
        _text(46, 182, "Horizontal", anchor="start", size=13),
        _line(p_left, p_right, width=7),
        _text(p_left[0] - 4, p_left[1] - 12, "Tilted surface", anchor="start", size=13),
        _line(C, n_end, color=LINE, width=2, marker="sa_arrow"),
        _text(n_end[0] - 6, n_end[1] - 8, "Normal", anchor="middle", size=13),
        _line(C, ray_end, color=ACCENT, width=3),
        _sun(ray_end),
        _text(ray_end[0] - 4, ray_end[1] - 20, "Sun ray", color=ACCENT, size=13),
        _arc(*C, 78, 0, beta),
        _arc(*C, 105, normal_a, ray_a),
        _dot(C),
    ]
    x, y = _pt(*C, 98, 17)
    b.append(_text(x + 8, y + 12, "β", color=BLUE, weight="bold", size=16))
    x, y = _pt(*C, 128, (normal_a + ray_a) / 2)
    b.append(_text(x + 8, y + 4, "θ", color=BLUE, weight="bold", size=16))
    b.append(_text(210, 284, "β = slope, θ = angle of incidence (ray to normal)", size=13))
    return _svg(420, 295, "".join(b), "Slope angle and angle of incidence on a tilted surface")


def latitude_declination():
    """Earth cross-section: latitude φ and declination δ."""
    O = (170, 150)
    R = 85
    phi, delta = 60, 23
    P = _pt(*O, R, -phi)
    sun_end = _pt(*O, 235, -delta)
    b = [
        f'<circle cx="{O[0]}" cy="{O[1]}" r="{R}" fill="none" stroke="{LINE}" stroke-width="2" opacity="0.7"/>',
        _line((30, 150), (400, 150), dash="6 5", opacity=0.7),
        _text(34, 168, "Equatorial plane", anchor="start", size=13),
        _line((170, 35), (170, 268), dash="6 5", opacity=0.7),
        _text(176, 30, "Polar axis", anchor="start", size=13),
        _line(O, sun_end, color=ACCENT, width=3),
        _sun(sun_end, r=11),
        _text(sun_end[0] - 4, sun_end[1] - 18, "Sun", color=ACCENT, size=13),
        _line(O, P, color=BLUE, width=2.5),
        _dot(P, r=5, color=BLUE),
        _text(P[0] + 10, P[1] - 6, "P (observer)", anchor="start", size=13),
        _arc(*O, 48, -phi, 0),
        _arc(*O, 122, -delta, 0),
        _dot(O),
    ]
    x, y = _pt(*O, 66, -44)
    b.append(_text(x + 2, y + 4, "φ", color=BLUE, weight="bold", size=16))
    x, y = _pt(*O, 142, -11)
    b.append(_text(x + 4, y + 4, "δ", color=BLUE, weight="bold", size=16))
    b.append(_text(210, 292, "Side view: latitude φ of the observer, declination δ of the sun", size=13))
    return _svg(420, 302, "".join(b), "Latitude and declination, Earth cross-section")


def hour_angle():
    """View from above the north pole: hour angle ω."""
    C = (210, 150)
    R = 95
    P = _pt(*C, R, -90)
    sun_end = _pt(*C, 175, -30)
    b = [
        f'<circle cx="{C[0]}" cy="{C[1]}" r="{R}" fill="none" stroke="{LINE}" stroke-width="2" opacity="0.7"/>',
        _line(C, P, color=BLUE, width=2.5),
        _dot(P, r=5, color=BLUE),
        _text(P[0] - 12, P[1] + 5, "Observer's meridian", anchor="end", size=13),
        _line(C, sun_end, color=ACCENT, width=3),
        _sun(sun_end, r=11),
        _text(sun_end[0] + 14, sun_end[1] - 22, "Direction of the sun", color=ACCENT, size=13, anchor="end"),
        _arc(*C, 62, -90, -30),
        _dot(C),
        _text(C[0], C[1] + 22, "N pole", size=12, opacity=0.8),
    ]
    x, y = _pt(*C, 82, -60)
    b.append(_text(x + 4, y + 4, "ω", color=BLUE, weight="bold", size=16))
    b.append(_text(210, 292, "View from above the north pole (here: afternoon, ω > 0)", size=13))
    return _svg(420, 302, "".join(b), "Hour angle, view from above the north pole")
