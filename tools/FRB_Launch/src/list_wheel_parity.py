"""FRB Launch: Files List のぐりぐり操作パラメータ（ここだけを調整）。

目標: Remote ぐりぐりボタンの入力応答を基準に、
      「相手がこっちへ来る」スクロールと、端でのカレント追従を両立する。

・高速ハイブリッド: スクロールバーが動ける間は表示内容だけを動かす。
    正式カレントは変えない。スクロール端／全件表示では旧WANの
    カレント追従に切り替える（旧WANの切替判定を再利用）。
・Remote一致: スクロールバーを使わずカレントを直接動かす（前回成功版）。
・旧WAN: Qt標準のスクロールを優先（比較・切り戻し用）。

いずれも Files List だけに適用。ぐりぐりボタン本体、Exp、Bookmarks、
コンテキストメニュー等には適用しない。
"""

# ======== 所長の調整エリア（変更後はLaunch再起動） ========
LIST_WHEEL_MATCH_REMOTE = True  # False -> 旧WANそのままに戻す
LIST_WHEEL_HYBRID_ENABLED = True  # True -> 高速ハイブリッド / False -> Remote一致（前回版）

# 0: List既存の1スクロール刻みを使用（行高さに追従、推奨）。
# 例: 20/35/50 等を指定すると 1ノッチで動くスクロール量をピクセル固定できる。
# ※正式カレントの行飛ばし量ではない。端での追従は常に1ノッチ1行。
LIST_WHEEL_SCROLL_PIXELS_PER_NOTCH = 0

# Remote WheelPad.wheelEvent と同じ入力規則。通常は変更不要。
LIST_WHEEL_ANGLE_PER_NOTCH = 120
LIST_WHEEL_PIXEL_PER_NOTCH = 36
LIST_WHEEL_MAX_STEPS_PER_EVENT = 5
# =============================================================


def consume_remote_like_wheel(angle_remainder, pixel_remainder, angle_delta, pixel_delta):
    """Remote ぐりぐりボタンと同じノッチ換算（Qt依存なし）。

    Returns: (angle_remainder, pixel_remainder, signed_steps)
    正は上回転、負は下回転。停止後に動くタイマー・慣性は使わない。
    """
    if angle_delta:
        angle_remainder += angle_delta
        steps = int(angle_remainder / LIST_WHEEL_ANGLE_PER_NOTCH)
        angle_remainder -= steps * LIST_WHEEL_ANGLE_PER_NOTCH
    else:
        pixel_remainder += pixel_delta
        steps = int(pixel_remainder / LIST_WHEEL_PIXEL_PER_NOTCH)
        pixel_remainder -= steps * LIST_WHEEL_PIXEL_PER_NOTCH
    steps = max(-LIST_WHEEL_MAX_STEPS_PER_EVENT,
                min(LIST_WHEEL_MAX_STEPS_PER_EVENT, steps))
    return angle_remainder, pixel_remainder, steps


def plan_hybrid_scroll(current, minimum, maximum, signed_steps, pixels_per_notch):
    """スクロールを先に使い、残ったノッチだけを旧WANの追従へ渡す。

    正のノッチ=上（スクロールバーの値は減少）、負=下（増加）。
    1つのホイールイベントに複数ノッチが含まれ、途中で端に着いた場合も
    未処理ノッチを消さずに追従へ引き継ぐ。

    Returns: (scroll_target, signed_follow_steps)
    """
    if not signed_steps:
        return current, 0
    pixels = max(1, int(pixels_per_notch))
    direction = 1 if signed_steps > 0 else -1
    target = max(minimum, min(maximum, current - signed_steps * pixels))
    travelled = abs(target - current)
    # 端まで残り数ピクセルでも、その1ノッチはスクロールで消費した扱い。
    scroll_notches = min(abs(signed_steps), (travelled + pixels - 1) // pixels)
    remaining = direction * (abs(signed_steps) - scroll_notches)
    return target, remaining
