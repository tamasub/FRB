"""FRB ぐりぐりハイブリッド with 手裏剣: wheel gesture gate (Qt-free).

【所長の調整エリア】まずはここだけ変更して Launch を再起動。
既存のスクロール/追従切替、手裏剣の物理モデルは変更しない。
"""
from collections import deque
import time

# ======= 調整パラメータ（実験中はここだけ） =======
AUTO_SHURIKEN_ENABLED = True          # False で自動起動だけ OFF（手裏剣ボタンは維持）
# Windows/Qt は高速回転の複数ノッチを1イベントにまとめる場合がある。
# イベント4回必須にしない。2回以上かつノッチ量・回転ペースで判定。
AUTO_SHURIKEN_MIN_NOTCHES = 4         # 判定窓内に必要な同方向ノッチ合計
AUTO_SHURIKEN_MIN_EVENTS = 4          # 単一の wheelEvent では起動しない
AUTO_SHURIKEN_WINDOW_MS = 700          # 判定対象の時間窓（100msだと短すぎやすい）
AUTO_SHURIKEN_MAX_GAP_MS = 150        # これ以上イベント間が空くと連続判定をリセット
AUTO_SHURIKEN_MIN_SPAN_MS = 220        # 1瞬間のバーストでは起動しない
AUTO_SHURIKEN_MIN_RATE_NPS = 25.0     # 判定区間の最低回転ペース（ノッチ/秒）
AUTO_SHURIKEN_REARM_MS = 450          # 手裏剣終了直後の再発火防止
AUTO_SHURIKEN_INITIAL_SPEED = 500.0  # 自動起動時の既存手裏剣への入力速度換算 (px/s)
AUTO_SHURIKEN_REVERSE_STOP_NOTCHES = 200  # 自動手裏剣中、連続逆回転で確定停止
# 以下は既存手裏剣ボタンからの起動にも共通する、滑走中の速度調整。
WHEEL_ACCEL_FACTOR = 1.45             # 進行方向へ1ノッチ回した時の速度倍率
WHEEL_DECEL_FACTOR = 0.75             # 逆方向へ1ノッチ回した時の速度倍率
MIN_CRUISE_RATE = 0.01               # 最低滑走倍率
MAX_CRUISE_RATE = 4.0                # 最高滑走倍率
# =================================================


class WheelShurikenGate:
    """Consecutive SAME-direction wheel events arm an explicit scroll mode.

    `steps`: +up / -down in remote-style wheel notches. Caller MUST invoke
    only on the Files List under the existing safety guards, before scrolling.
    """
    def __init__(self):
        self._samples = deque()
        self._direction = 0
        self._source = None
        self._cooldown_until = 0.0

    def reset(self, *, cooldown=False, now=None):
        self._samples.clear()
        self._direction = 0
        self._source = None
        if cooldown:
            t = time.monotonic() if now is None else now
            self._cooldown_until = t + AUTO_SHURIKEN_REARM_MS / 1000.0

    def feed(self, steps, *, source='list', now=None):
        """Return signed flight direction once when the gesture is armed.

        Returns +1 for scrollbar UP, -1 for scrollbar DOWN, or 0. No timer,
        no synthetic events and no transition on idle/zero-step input.
        """
        if not AUTO_SHURIKEN_ENABLED or not steps:
            return 0
        t = time.monotonic() if now is None else float(now)
        if t < self._cooldown_until:
            return 0
        direction = 1 if steps > 0 else -1
        max_gap = AUTO_SHURIKEN_MAX_GAP_MS / 1000.0
        if (self._samples and (t - self._samples[-1][0] > max_gap
                               or t < self._samples[-1][0])) or (direction != self._direction or source != self._source):
            self.reset()
        self._direction, self._source = direction, source
        self._samples.append((t, abs(int(steps))))
        window = AUTO_SHURIKEN_WINDOW_MS / 1000.0
        while self._samples and t - self._samples[0][0] > window:
            self._samples.popleft()
        span = t - self._samples[0][0]
        notches = sum(quantity for _, quantity in self._samples)
        # A trackpad/Qt event may aggregate several physical wheel notches.
        # Count those notches, but require at least two distinct events and
        # sustained speed. Slow scrolling must remain ordinary hybrid input.
        if (len(self._samples) >= AUTO_SHURIKEN_MIN_EVENTS
                and notches >= AUTO_SHURIKEN_MIN_NOTCHES
                and span >= AUTO_SHURIKEN_MIN_SPAN_MS / 1000.0
                and notches / max(span, 0.001) >= AUTO_SHURIKEN_MIN_RATE_NPS):
            self.reset(cooldown=True, now=t)
            return direction
        return 0
