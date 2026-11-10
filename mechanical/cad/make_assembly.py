"""Whole-robot reference assembly (STEP) for Fusion 360.

World frame: X = right, Y = forward, Z = up, origin = floor under the axle centre.
"""
import math
import sys

import os

import cadquery as cq

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_chassis  # noqa: E402

SP = sys.argv[1]
OUT = sys.argv[2]

WHEEL_D, WHEEL_W = 47.0, 6.0          # ホイール径（O リング込み、車高 2.5 mm になる径）と幅（案）
AXLE_Z = WHEEL_D / 2
MOTOR = 42.0                          # PKP242D23A2: 42 mm 角
MOTOR_L = 17.0                        # 本体長さ（取付面から後端）
GAP = 1.0                             # 左右モータの後端どうしのすき間
PILOT_D, PILOT_H = 22.0, 1.5          # インロー
SHAFT_D, SHAFT_L = 5.0, 15.0
BOARD_Z = AXLE_Z + MOTOR / 2 + 4.0    # メイン基板の下面 = 48.5（モータ上面との間 4 mm、部品の足のはみ出し用）
PCB_T = 1.6
SOCKET_H = 8.5                        # ピンソケットの高さ
TAB_OUT = 0.9                         # センサ基板の差し込み部がメイン基板の上に出る長さ

# メイン基板の座標 (KiCad の x, y) → 世界座標
def board_xy(x, y):
    return (x - 40.0, 55.0 - y)   # 基板 v0.3: 幅 80 mm、中心 x = 40


def motor(side):
    s = 1 if side == 'R' else -1
    rear = s * GAP / 2                       # 後端（中央側）
    face = s * (GAP / 2 + MOTOR_L)           # 取付面（外側）
    body = (cq.Workplane('YZ').rect(MOTOR, MOTOR).extrude(MOTOR_L)
            .translate((min(rear, face), 0, AXLE_Z)))
    pilot = cq.Workplane('YZ').circle(PILOT_D / 2).extrude(PILOT_H)
    shaft = cq.Workplane('YZ').circle(SHAFT_D / 2).extrude(SHAFT_L)
    if s > 0:
        pilot = pilot.translate((face, 0, AXLE_Z))
        shaft = shaft.translate((face, 0, AXLE_Z))
    else:
        pilot = pilot.translate((face - PILOT_H, 0, AXLE_Z))
        shaft = shaft.translate((face - SHAFT_L, 0, AXLE_Z))
    return body.union(pilot), shaft, face


def wheel(side, face):
    s = 1 if side == 'R' else -1
    outer = face + s * SHAFT_L               # 軸の先
    x0 = outer - s * WHEEL_W
    w = cq.Workplane('YZ').circle(WHEEL_D / 2).circle(SHAFT_D / 2).extrude(WHEEL_W)
    return w.translate((min(x0, outer), 0, AXLE_Z))


def sensor(slot_xy, rot_deg, shape):
    """センサ基板を差し込み口 (KiCad の x, y, 回転) に立てる。"""
    # 見る向き d（メイン基板のフットプリントの −y を回転したもの）
    a = math.radians(rot_deg)
    dx, dy = -math.sin(a), math.cos(a)       # 世界座標での向き (KiCad の y は下向き)
    # センサ基板の局所座標: X_s 横、Y_s 上（先端が原点）、Z_s 部品面
    # Y_s → 世界 +Z、Z_s → d、X_s → Z × d
    zx, zy = dx, dy
    xx, xy = -dy, dx                          # (0,0,1) × (dx,dy,0)
    th = math.degrees(math.atan2(dx, -dy))
    placed = shape.rotate((0, 0, 0), (1, 0, 0), 90).rotate((0, 0, 0), (0, 0, 1), th).val()
    cx, cy = board_xy(*slot_xy)
    top = BOARD_Z + PCB_T + TAB_OUT
    off = -PCB_T / 2                          # 基板の厚みをスリットの中央へ
    return cq.Workplane().add(placed).translate((cx + off * zx, cy + off * zy, top))


def box(sx, sy, sz, cx, cy, z0):
    return cq.Workplane('XY').box(sx, sy, sz, centered=(True, True, False)).translate((cx, cy, z0))


main_pcb = cq.importers.importStep(SP + '/main.step').translate((0, 0, BOARD_Z))
sens = cq.importers.importStep(SP + '/sensor.step')

asm = cq.Assembly(name='Mice-Standard')
asm.add(main_pcb, name='main-board', color=cq.Color(0.1, 0.45, 0.2))
asm.add(make_chassis.chassis(), name='chassis (PLA)', color=cq.Color(0.95, 0.6, 0.1))
for side in ('L', 'R'):
    body, shaft, face = motor(side)
    asm.add(body, name='motor_' + side, color=cq.Color(0.25, 0.25, 0.28))
    asm.add(shaft, name='shaft_' + side, color=cq.Color(0.8, 0.8, 0.8))
    asm.add(wheel(side, face), name='wheel_' + side, color=cq.Color(0.9, 0.9, 0.9))
SLOTS = {'J11_LF': ((11.0, 6.0), 7.0), 'J12_RF': ((69.0, 6.0), -7.0),
         'J10_LS': ((9.5, 16.0), 44.7), 'J13_RS': ((70.5, 16.0), -44.7)}
for name, (xy, r) in SLOTS.items():
    asm.add(sensor(xy, r, sens), name='sensor_' + name, color=cq.Color(0.1, 0.45, 0.2))
# 差し込み式モジュールの仮の形（実寸の外形のみ）
top = BOARD_Z + PCB_T + SOCKET_H
asm.add(box(18.5, 50.3, 1.6, *board_xy(40.0, 31 + 17.78), top), name='NUCLEO-L432KC (仮)',
        color=cq.Color(0.95, 0.95, 0.95))
for side, x in (('L', 22.35), ('R', 57.65)):
    asm.add(box(15.24, 20.32, 1.6, *board_xy(x, 71 + 8.89), top), name='MP6500_' + side + ' (仮)',
            color=cq.Color(0.8, 0.1, 0.1))
# 電池（Zeee 3S 850 mAh、67 x 18.5 x 30 mm を立てて載せる）
_yf, _yb, _xi = make_chassis.tray_dims()
_bz = make_chassis.BASE + make_chassis.TRAY_FLOOR
asm.add(box(make_chassis.BATT[0], make_chassis.BATT[1], make_chassis.BATT[2], 0, _yb + make_chassis.BATT[1] / 2, _bz),
        name='battery 3S 850mAh', color=cq.Color(0.15, 0.15, 0.15))
asm.save(OUT, exportType='STEP')

# 重心の見積もり（重さは仮。実物を量って直す）
MASS = {  # 名前: (g, (X, Y, Z))
    'motor x2': (220, (0, 0, AXLE_Z)),
    'wheel x2 (O リング込み)': (12, (0, 0, AXLE_Z)),
    'chassis (PLA 30 %)': (20, (0, -15, 15)),
    'main board + parts': (45, (0, 5, BOARD_Z + 5)),
    'NUCLEO + MP6500 x2': (16, (0, -10, BOARD_Z + 12)),
    'sensor boards x4': (8, (0, 47, BOARD_Z - 15)),
    'battery': (74, (0, _yb + make_chassis.BATT[1] / 2, _bz + make_chassis.BATT[2] / 2)),
}
tot = sum(m for m, _ in MASS.values())
cg = [sum(m * p[i] for m, p in MASS.values()) / tot for i in range(3)]
print('mass about %d g, CG X %.1f Y %.1f Z %.1f (mm, from axle / floor)' % (tot, *cg))
# その場旋回で一番外を回る点（車軸の中心から）
import math as _m
far = 0
for _n, _o in asm.objects.items():
    if _o.obj is None:
        continue
    _sh = _o.obj.val() if hasattr(_o.obj, 'val') else _o.obj
    if _o.loc is not None:
        _sh = _sh.moved(_o.loc)
    _b = _sh.BoundingBox()
    for _x in (_b.xmin, _b.xmax):
        for _y in (_b.ymin, _b.ymax):
            far = max(far, _m.hypot(_x, _y))
print('turning radius (bbox corners) %.1f mm (wall at 84 mm from cell centre)' % far)

# 寸法の確認
bb = asm.toCompound().BoundingBox()
print('overall X %.1f..%.1f  Y %.1f..%.1f  Z %.1f..%.1f' % (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax))
for name in ('sensor_J11_LF', 'sensor_J10_LS', 'wheel_L', 'motor_L'):
    o = asm.objects[name].obj
    b = (o.val() if hasattr(o, 'val') else o).BoundingBox()
    print(name, 'X %.1f..%.1f Y %.1f..%.1f Z %.1f..%.1f' % (b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax))
