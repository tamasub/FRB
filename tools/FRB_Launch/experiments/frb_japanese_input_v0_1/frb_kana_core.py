"""FRB 日本語入力 v0.1: UI に依存しない、かな・ジェスチャー定義。

FRB Remote WheelPad の 18px 判定から発展させた単体実験用モデル。
現段階では IME / Windows への入力送信 / 漢字変換を扱わない。
"""

from __future__ import annotations

from dataclasses import dataclass

# 方向の並び: 中央、左、上、右、下（スマホの一般的なフリック配置）。
DIRECTIONS = ("center", "left", "up", "right", "down")

# すべて平仮名。実験上の余白は None にして無理に割り当てない。
KANA_ROWS: tuple[tuple[str, tuple[str | None, ...]], ...] = (
    ("あ", ("あ", "い", "う", "え", "お")),
    ("か", ("か", "き", "く", "け", "こ")),
    ("さ", ("さ", "し", "す", "せ", "そ")),
    ("た", ("た", "ち", "つ", "て", "と")),
    ("な", ("な", "に", "ぬ", "ね", "の")),
    ("は", ("は", "ひ", "ふ", "へ", "ほ")),
    ("ま", ("ま", "み", "む", "め", "も")),
    ("や", ("や", None, "ゆ", None, "よ")),
    ("ら", ("ら", "り", "る", "れ", "ろ")),
    ("わ", ("わ", "を", "ん", "ー", None)),
)
ROW_LABELS: tuple[str, ...] = tuple(row[0] for row in KANA_ROWS)

# Smartphone-style keyboard positions (not a scrollable list).
# Side characters are literal punctuation buttons, not kana rows.
KEY_LAYOUT: tuple[tuple[str, ...], ...] = (
    ("あ", "か", "さ"),
    ("た", "な", "は"),
    ("ま", "や", "ら"),
    ("、", "わ", "。"),
)
DRAG_THRESHOLD_PX = 18


def get_kana(row_index: int, direction: str) -> str | None:
    """行と方向に対応する一文字。未割り当ての方向は None。"""
    if not 0 <= row_index < len(KANA_ROWS):
        raise IndexError(row_index)
    try:
        direction_index = DIRECTIONS.index(direction)
    except ValueError as exc:
        raise ValueError(f"Unknown direction: {direction}") from exc
    return KANA_ROWS[row_index][1][direction_index]


def row_after_wheel(current: int, wheel_steps: int) -> int:
    """ホイール下方向で次の行へ。端から端へ循環する。"""
    return (current - wheel_steps) % len(KANA_ROWS)


def classify_flick(dx: float, dy: float, threshold: int = DRAG_THRESHOLD_PX) -> str | None:
    """始点からの変位でフリック方向を判定。

    Qt の座標は下向きが正。小移動は center、ほぼ45°の曖昧な
    ドラッグは None（入力せずキャンセル）。
    """
    ax, ay = abs(dx), abs(dy)
    if max(ax, ay) < threshold:
        return "center"
    # 斜め45°付近（主軸が 20% 未満の差しかない）は誤入力防止で無効。
    if abs(ax - ay) < 0.2 * max(ax, ay):
        return None
    if ax > ay:
        return "left" if dx < 0 else "right"
    return "up" if dy < 0 else "down"


@dataclass
class WheelStepper:
    """120角度単位または36pixelで1行。微小ホイール量を蓄積する。"""

    angle_remainder: int = 0
    pixel_remainder: int = 0

    def feed(self, *, angle: int = 0, pixel: int = 0) -> int:
        if angle:
            self.angle_remainder += angle
            steps = int(self.angle_remainder / 120)
            self.angle_remainder -= steps * 120
        elif pixel:
            self.pixel_remainder += pixel
            steps = int(self.pixel_remainder / 36)
            self.pixel_remainder -= steps * 36
        else:
            return 0
        return max(-5, min(5, steps))


@dataclass
class KanaInputModel:
    """ウィンドウを使わず検証可能な編集状態。"""

    row_index: int = 0
    text: str = ""

    def scroll(self, steps: int) -> None:
        self.row_index = row_after_wheel(self.row_index, steps)

    def select(self, row_index: int) -> None:
        if not 0 <= row_index < len(KANA_ROWS):
            raise IndexError(row_index)
        self.row_index = row_index

    def input(self, direction: str) -> str | None:
        kana = get_kana(self.row_index, direction)
        if kana is not None:
            self.text += kana
        return kana

    def backspace(self) -> None:
        self.text = self.text[:-1]

    def clear(self) -> None:
        self.text = ""
