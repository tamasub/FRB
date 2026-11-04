"""FRB 日本語入力 v0.3: UI に依存しない、かな・ジェスチャー定義。

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
# Side keys are flickable modifier / punctuation keys.
KEY_LAYOUT: tuple[tuple[str, ...], ...] = (
    ("あ", "か", "さ"),
    ("た", "な", "は"),
    ("ま", "や", "ら"),
    ("゛゜小", "わ", "、。?!"),
)
DRAG_THRESHOLD_PX = 18

MODIFIER_KEY = "゛゜小"
PUNCTUATION_KEY = "、。?!"
SPECIAL_KEYS = (MODIFIER_KEY, PUNCTUATION_KEY)

# Center/left/up/right/down. A short press of the modifier cycles a
# compatible last kana (e.g. つ -> っ -> づ -> つ, は -> ば -> ぱ -> は).
PUNCTUATION_FLICK = {
    "center": "、", "left": "。", "up": "？", "right": "！", "down": "…",
}
MODIFIER_HINTS = {
    "center": "変", "left": "゛", "up": "゜", "right": "小", "down": "大",
}

_VOICED = dict(zip(
    "かきくけこさしすせそたちつてとはひふへほう",
    "がぎぐげござじずぜぞだぢづでどばびぶべぼゔ",
))
_SEMIVOICED = dict(zip("はひふへほ", "ぱぴぷぺぽ"))
_SMALL = dict(zip("あいうえおつやゆよわ", "ぁぃぅぇぉっゃゅょゎ"))

# For every kana family, retain an unmodified base and its variants.
_KANA_FAMILIES = {}
for _base in set(_VOICED) | set(_SEMIVOICED) | set(_SMALL):
    _variants = [_base]
    # Prioritize small kana for click: つ -> っ in one press.
    for _mapping in (_SMALL, _VOICED, _SEMIVOICED):
        if _base in _mapping:
            _variants.append(_mapping[_base])
    _family = tuple(_variants)
    for _variant in _family:
        _KANA_FAMILIES[_variant] = _family


def flick_hint(key_name: str, direction: str) -> str | None:
    """Label for an in-place tiny guide; None for unsupported directions."""
    if key_name == MODIFIER_KEY:
        return MODIFIER_HINTS.get(direction)
    if key_name == PUNCTUATION_KEY:
        return PUNCTUATION_FLICK.get(direction)
    for i, (name, _) in enumerate(KANA_ROWS):
        if name == key_name:
            return get_kana(i, direction)
    raise ValueError(f"Unknown key: {key_name}")


def transform_last_kana(text: str, direction: str) -> tuple[str, str | None]:
    """Alter only the final kana. No input means no change/no stray mark."""
    if direction not in DIRECTIONS:
        raise ValueError(f"Unknown direction: {direction}")
    if not text or text[-1] not in _KANA_FAMILIES:
        return text, None
    char = text[-1]
    family = _KANA_FAMILIES[char]
    base = family[0]
    if direction == "center":
        new_char = family[(family.index(char) + 1) % len(family)]
    elif direction == "down":
        new_char = base
    else:
        target_mapping = {"left": _VOICED, "up": _SEMIVOICED, "right": _SMALL}[direction]
        if base not in target_mapping:
            return text, None
        target = target_mapping[base]
        new_char = base if char == target else target
    if new_char == char:
        return text, None
    return text[:-1] + new_char, new_char



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

    def special_input(self, key_name: str, direction: str) -> str | None:
        """Perform a modifier operation or append one punctuation symbol."""
        if key_name == PUNCTUATION_KEY:
            char = PUNCTUATION_FLICK.get(direction)
            if char is not None:
                self.text += char
            return char
        if key_name == MODIFIER_KEY:
            self.text, char = transform_last_kana(self.text, direction)
            return char
        raise ValueError(f"Unknown special key: {key_name}")

    def backspace(self) -> None:
        self.text = self.text[:-1]

    def clear(self) -> None:
        self.text = ""
