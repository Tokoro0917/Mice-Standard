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

WHEEL_D, WHEEL_W = 50.0, 6.0          # ホイール径（O リング込み）と幅（案）
AXLE_Z = WHEEL_D / 2
MOTOR = 42.0                          # PKP242D23A2: 42 mm 角
MOTOR_L = 17.0                        # 本体長さ（取付面から後端）
GAP = 1.0                             # 左右モータの後端どうしのすき間
PILOT_D, PILOT_H = 22.0, 1.5          # インロー
SHAFT_D, SHAFT_L = 5.0, 15.0
BOARD_Z = AXLE_Z + MOTOR / 2 + 4.0    # メイン基板の下面 = 50（モータ上面との間 4 mm、部品の足のはみ出し用）
PCB_T = 1.6
SOCKET_H = 8.5                        # ピンソケットの高さ
TAB_OUT = 0.9                         # センサ基板の差し込み部がメイン基板の上に出る長さ

# メイン基板の座標 (KiCad の x, y) → 世界座標
def board_xy(x, y):
    return (x - 25.0, 55.0 - y)


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
SLOTS = {'J11_LF': ((16.5, 4), 0), 'J12_RF': ((33.5, 4), 0),
         'J10_LS': ((6.5, 14), 45), 'J13_RS': ((43.5, 14), -45)}
for name, (xy, r) in SLOTS.items():
    asm.add(sensor(xy, r, sens), name='sensor_' + name, color=cq.Color(0.1, 0.45, 0.2))
# 差し込み式モジュールの仮の形（実寸の外形のみ）
top = BOARD_Z + PCB_T + SOCKET_H
asm.add(box(18.5, 50.3, 1.6, *board_xy(25.0, 31 + 17.78), top), name='NUCLEO-L432KC (仮)',
        color=cq.Color(0.95, 0.95, 0.95))
for side, x in (('L', 8.85), ('R', 41.15)):
    asm.add(box(15.24, 20.32, 1.6, *board_xy(x, 71 + 8.89), top), name='MP6500_' + side + ' (仮)',
            color=cq.Color(0.8, 0.1, 0.1))
asm.save(OUT, exportType='STEP')

# 寸法の確認
bb = asm.toCompound().BoundingBox()
print('overall X %.1f..%.1f  Y %.1f..%.1f  Z %.1f..%.1f' % (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax))
for name in ('sensor_J11_LF', 'sensor_J10_LS', 'wheel_L', 'motor_L'):
    o = asm.objects[name].obj
    b = (o.val() if hasattr(o, 'val') else o).BoundingBox()
    print(name, 'X %.1f..%.1f Y %.1f..%.1f Z %.1f..%.1f' % (b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax))
