"""Mice-Standard シャーシ（3D プリント、PLA 一体成形）を CadQuery で作る。

座標: X = 右、Y = 前、Z = 上。原点は車軸の真下の床（make_assembly.py と同じ）。
使い方: python make_chassis.py <出力フォルダ>
"""
import sys

import cadquery as cq

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'

# ---- 機体の寸法（make_assembly.py と合わせる）
GROUND = 2.5             # 車高: 床からモータの底面まで
AXLE_Z = GROUND + 21.0   # 車軸の高さ 23.5 mm（ホイール直径 47 mm）
MOTOR = 42.0             # モータ 42 mm 角
MOTOR_L = 17.0           # モータ本体の長さ
GAP = 1.0                # 左右のモータの後端のすき間
FACE_X = GAP / 2 + MOTOR_L          # モータ取付面の位置 |X| = 17.5
BOARD_Z = AXLE_Z + MOTOR / 2 + 4.0  # メイン基板の下面 = 48.5（モータ上面との間 4 mm、足のはみ出し用）

# ---- シャーシの寸法
WALL_T = 3.0             # モータ取付壁の厚さ
WALL_Y = (-43.5, 31.0)   # 取付壁の前後の範囲
WALL_Z = (GROUND, AXLE_Z + 19.0)  # 取付壁の高さの範囲（下端は車高にそろえる）
PILOT_HOLE = 22.4        # インロー φ22 の穴（すき間 0.2 mm）
M3_CLEAR = 3.4           # M3 のバカ穴
M3_HEAD = 6.0            # M3 なべ（低頭）ねじの頭の座ぐり径
M3_HEAD_DEPTH = 1.2
MOTOR_HOLES = [(15.5, 15.5), (-15.5, -15.5)]   # モータの M3 穴（ピッチ 31 mm の対角、要確認）
BAR_T = 4.0              # 前後のはりの厚さ
BAR_X = 24.0             # はりの左右の端 |X|
BAR_Z = (GROUND, BOARD_Z - 10.0)  # 上端を基板の 10 mm 下に（部品の足をよける）
FRONT_Y = 29.0           # 前のはり（メイン基板の取付穴 H1/H2 の位置）
REAR_Y = -41.5           # 後ろのはり（H3/H4）
BOARD_HOLES = [(-21.0, FRONT_Y), (21.0, FRONT_Y), (-21.5, REAR_Y), (21.5, REAR_Y)]
BOSS_D = 7.0             # 基板を留めるボスの径
TAP_D = 2.6              # M3 タッピングねじの下穴
TAP_DEPTH = 10.0
KAGU_T = 1.5             # カグスベール（ニチアス）の厚さ 約 1.5 mm（KOGUMA-Mk4 と同じ。実物を測る）
KAGU_GAP = 0.5           # カグスベールと床のすき間（ホイールに重さをかけるため）
KAGU_D = 8.0             # カグスベールを切る直径
PAD_D = 10.0             # カグスベールを貼る台の直径
PAD_Z = KAGU_GAP + KAGU_T  # 台の下面の高さ 2.0 mm
PAD_Y = (45.0, -47.0)    # 前後の接地点（車軸から）
ARM_W = 10.0             # 前後に伸ばす腕の幅
ARM_TOP = 9.0            # 腕の上面の高さ（センサ基板の下端 約 18.5 mm より低く）


def wall(side):
    s = 1 if side == 'R' else -1
    x0 = s * FACE_X if s > 0 else s * FACE_X - WALL_T
    w = (cq.Workplane('XY')
         .box(WALL_T, WALL_Y[1] - WALL_Y[0], WALL_Z[1] - WALL_Z[0], centered=False)
         .translate((x0, WALL_Y[0], WALL_Z[0])))
    # インローと軸の穴
    hole = cq.Workplane('YZ').circle(PILOT_HOLE / 2).extrude(WALL_T + 2).translate((x0 - 1, 0, AXLE_Z))
    w = w.cut(hole)
    # モータを留める M3 の穴と、外側の座ぐり
    for (dy, dz) in MOTOR_HOLES:
        h = cq.Workplane('YZ').circle(M3_CLEAR / 2).extrude(WALL_T + 2).translate((x0 - 1, dy, AXLE_Z + dz))
        w = w.cut(h)
        outer = x0 + WALL_T if s > 0 else x0
        cb = cq.Workplane('YZ').circle(M3_HEAD / 2).extrude(M3_HEAD_DEPTH)
        cb = cb.translate((outer - M3_HEAD_DEPTH, dy, AXLE_Z + dz)) if s > 0 else cb.translate((outer, dy, AXLE_Z + dz))
        w = w.cut(cb)
    return w


def bar(yc):
    b = (cq.Workplane('XY').box(2 * BAR_X, BAR_T, BAR_Z[1] - BAR_Z[0], centered=(True, True, False))
         .translate((0, yc, BAR_Z[0])))
    # 真ん中を肉抜き（軽くする、配線を通す）
    cut = (cq.Workplane('XY').box(2 * FACE_X - 6, BAR_T + 2, 20, centered=(True, True, False))
           .translate((0, yc, BAR_Z[0] + 10)))
    return b.cut(cut)


def boss(x, y):
    h = BOARD_Z - BAR_Z[0]
    b = cq.Workplane('XY').circle(BOSS_D / 2).extrude(h).translate((x, y, BAR_Z[0]))
    hole = cq.Workplane('XY').circle(TAP_D / 2).extrude(TAP_DEPTH + 1).translate((x, y, BOARD_Z - TAP_DEPTH))
    return b.cut(hole)


def pad_arm(y_bar, y_pad):
    """前後のはりから接地点まで腕を伸ばし、先にカグスベールを貼る台を付ける。"""
    y0, y1 = sorted((y_bar, y_pad + (PAD_D / 2 if y_pad > 0 else -PAD_D / 2)))
    arm = (cq.Workplane('XY').box(ARM_W, y1 - y0, ARM_TOP - GROUND, centered=(True, False, False))
           .translate((0, y0, GROUND)))
    pad = cq.Workplane('XY').circle(PAD_D / 2).extrude(ARM_TOP - PAD_Z).translate((0, y_pad, PAD_Z))
    return arm.union(pad)


def chassis():
    c = wall('L').union(wall('R'))
    # はりの中心は、取付壁の前後の端に合わせる
    for yc in (WALL_Y[1] - BAR_T / 2, WALL_Y[0] + BAR_T / 2):
        c = c.union(bar(yc))
    for (x, y) in BOARD_HOLES:
        # ボスがはりに乗るように、はりの範囲に入れる
        c = c.union(boss(x, y))
    c = c.union(pad_arm(WALL_Y[1] - BAR_T / 2, PAD_Y[0])).union(pad_arm(WALL_Y[0] + BAR_T / 2, PAD_Y[1]))
    return c


if __name__ == '__main__':
    c = chassis()
    cq.exporters.export(c, OUT + '/chassis.step')
    cq.exporters.export(c, OUT + '/chassis.stl', tolerance=0.05, angularTolerance=0.1)
    bb = c.val().BoundingBox()
    vol = c.val().Volume() / 1000.0
    print('chassis X %.1f..%.1f Y %.1f..%.1f Z %.1f..%.1f' % (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax))
    print('volume %.1f cm3 -> PLA 100%% fill about %.1f g' % (vol, vol * 1.24))
