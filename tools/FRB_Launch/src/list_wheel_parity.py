"""FRB Launch: Files List 上のぐりぐりを Remote ボタン基準に合わせる試作設定。

変更する場所はこのファイルの冒頭だけ。

・True : List 上のホイールも Remote ぐりぐりボタンと同じ
         『ホイール 1 ノッチ -> カレント 1 行移動』処理に切り替える。
・False: 従来どおり『Qt 標準スクロール -> 端で追従』に戻る。

Remote ボタンの動作は一切変更しない。加速・行飛ばしもまだ導入しない。
"""

# ===== 調整箇所（まずはこのスイッチだけで A/B 比較） =====
LIST_WHEEL_MATCH_REMOTE = True

# 以下は Remote の WheelPad.wheelEvent と同じ値。初回比較では変更しない。
LIST_WHEEL_ANGLE_PER_NOTCH = 120
LIST_WHEEL_PIXEL_PER_NOTCH = 36
LIST_WHEEL_MAX_STEPS_PER_EVENT = 5
# ==========================================================


def consume_remote_like_wheel(angle_remainder, pixel_remainder, angle_delta, pixel_delta):
    """Remote ぐりぐりボタンと同じ整数化・イベント単位の最大処理数。

    Return: (angle_remainder, pixel_remainder, signed_steps)
    正 = 上回転（カレントを上へ）、負 = 下回転（カレントを下へ）。
    Qt の高精度ホイールの余りは保持する。停止後の遅延・慣性移動はしない。
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
