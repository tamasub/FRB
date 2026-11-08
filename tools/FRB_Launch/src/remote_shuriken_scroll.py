"""Release-to-launch shuriken inertia scroll for the compact FRB Remote.

Press, flick vertically, RELEASE: the Files List begins a smooth acceleration
and deceleration show. During flight, the physical ぐりぐり mouse wheel
accelerates in the travel direction and decelerates against it. A short click
slows the flight, a hold stops it; either real landing hands off the visible
current row. No fake wheel, keyboard or cursor warp.
"""
import time

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
try:
    from PySide6.QtGui import QPixmap
except Exception:  # Qt-free tests may not provide QtGui.
    QPixmap = None

from shuriken_assets import resource_root
from shuriken_scroll_model import (TICK_MS, ARRIVAL_DECEL_START, ScrollFlight, plan_flick,
                                   plan_full_range_flight, eased_displacement)
from guriguri_shuriken_auto import (AUTO_SHURIKEN_INITIAL_SPEED,
                                    AUTO_SHURIKEN_REVERSE_STOP_NOTCHES,
                                    WHEEL_ACCEL_FACTOR, WHEEL_DECEL_FACTOR,
                                    MIN_CRUISE_RATE, MAX_CRUISE_RATE)

ICON_PATH = resource_root(__file__) / 'assets' / 'remote_shuriken_scroll.png'
ICON_MAX_WIDTH = 42
ICON_MAX_HEIGHT = 26

# A button press becomes a brake pedal. Quick tap: a persistent slowdown;
# long hold: full stop. Braking uses a virtual flight clock, never changes the
# preplanned end point or moves the selected file item.
HOLD_TO_STOP_S = 0.52
TAP_SLOW_FACTOR = 0.43
HELD_SLOW_FACTOR = 0.22
# Each physical mouse-wheel notch changes the virtual flight clock only.
# 'DOWN' increases scrollbar value (same direction as an upward flick).


class ShurikenScrollPad(QFrame):
    scroll_requested = Signal(int)  # Signed scrollbar delta, not row selection.
    flight_settled = Signal(object)  # Exact Files List tree at natural/manual stop.

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('remoteShurikenScrollPad')
        self.setFixedSize(68, 46)  # Exactly the compact ぐりぐり button size.
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setToolTip('手裏剣スクロール：シュッ→滑走／ぐりぐり順方向=加速・逆方向=減速／短押し=減速・長押し=停止（Files List）')

        self.target_provider = None  # Wired by Remote, returns active list tree or None.
        self.auto_target_provider = None  # Wheel-only Files List target, even without visible Remote.
        self.auto_end_callback = None  # Re-arm guard when wheel flight ends.
        self._pressed = False
        self._braking_press = False
        self._samples = []
        self._flight = None
        self._flight_target = None
        self._flight_bounds = None
        self._auto_wheel_flight = False
        self._auto_wheel_source = None
        self._reverse_notches = 0
        self._flight_start_time = 0.0
        self._last_tick_time = 0.0
        self._flight_elapsed_s = 0.0
        self._cruise_rate = 1.0
        self._brake_press_time = 0.0
        self._last_displacement = 0
        self._display_status = 'idle'
        self._timer = QTimer(self)
        self._timer.setInterval(TICK_MS)
        self._timer.timeout.connect(self._scroll_tick)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(1, 1, 1, 1)
        layout.setSpacing(0)

        icon = QLabel('', self)
        icon.setObjectName('remoteShurikenScrollIcon')
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        caption = QLabel('手裏剣↕', self)
        caption.setObjectName('remoteShurikenScrollLabel')
        caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
        caption.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        # Keep the old glyph label as an internal state carrier so the
        # existing Qt-free regression tests and status logic remain intact.
        glyph = QLabel('⇅', self)
        glyph.setObjectName('remoteShurikenScrollGlyph')
        glyph.setAlignment(Qt.AlignmentFlag.AlignCenter)
        glyph.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        layout.addWidget(icon)
        layout.addWidget(caption)

        self._icon_label = icon
        self._caption = caption
        self._glyph = glyph
        self._icon_pixmap = None
        if QPixmap is not None:
            self._icon_pixmap = QPixmap(str(ICON_PATH))
        self._apply_icon_pixmap()

    def wheelEvent(self, event):
        pad = getattr(self.parentWidget(), 'pad', None)
        if pad is not None:
            pad.wheelEvent(event)
        else:
            event.ignore()

    @staticmethod
    def _sample(event):
        point = event.globalPosition()
        return (time.monotonic(), point.x(), point.y())

    def _target(self):
        provider = self.target_provider
        if self._auto_wheel_flight and self._auto_wheel_source == 'list':
            provider = self.auto_target_provider
        return provider() if callable(provider) else None

    def _apply_icon_pixmap(self):
        label = getattr(self, '_icon_label', None)
        if label is None:
            return
        pixmap = getattr(self, '_icon_pixmap', None)
        if pixmap is None or getattr(pixmap, 'isNull', lambda: True)():
            if hasattr(label, 'setText'):
                label.setText('⇅')
            return
        if hasattr(pixmap, 'scaled'):
            pixmap = pixmap.scaled(ICON_MAX_WIDTH, ICON_MAX_HEIGHT,
                                   Qt.AspectRatioMode.KeepAspectRatio,
                                   Qt.TransformationMode.SmoothTransformation)
        if hasattr(label, 'setPixmap'):
            label.setPixmap(pixmap)
        elif hasattr(label, 'setText'):
            label.setText('手裏剣')

    def _update_feedback(self):
        """Expose which wheel direction controls speed, without moving current.

        Upward flick: scrollbar travels DOWN, so wheel DOWN accelerates.
        Downward flick: scrollbar travels UP, so wheel UP accelerates.
        The small Remote pad displays this mapping throughout the flight.
        """
        if self._flight is None:
            status, title, glyph = 'idle', '手裏剣↕', '⇅'
            tip = ('手裏剣スクロール：シュッ→滑走／短押し=減速・'
                   '長押し=停止（Files List）')
        else:
            accel = '↓' if self._flight.distance_px > 0 else '↑'
            decel = '↑' if self._flight.distance_px > 0 else '↓'
            glyph = f'{accel}＋ {decel}－'
            tip = (f'滑走中：ホイール{accel}=加速／{decel}=減速'
                   f'（現在 {self._cruise_rate:.2f}倍）／短押し=減速・長押し=停止')
            # A manual wheel/tap change must remain visible even near the
            # endpoint. The arrival label wins only at neutral cruise speed.
            if self._braking_press or self._cruise_rate < .999:
                status, title = 'slow', '減速中'
            elif self._cruise_rate > 1.001:
                status, title = 'faster', '加速中'
            elif (self._flight.full_range
                  and self._flight_elapsed_s / max(.001, self._flight.duration_s)
                  >= ARRIVAL_DECEL_START):
                status, title = 'approaching', '終点間近'
            else:
                status, title = 'moving', '滑走中'
        # Both direction AND current speed can change without status change.
        # Avoid the old status-only refresh that concealed successive turns.
        if status != self._display_status:
            self._display_status = status
            self._caption.setText(title)
        if self._glyph.text() != glyph:
            self._glyph.setText(glyph)
        self.setToolTip(tip)

    def wheel_while_flying(self, command):
        """Consume a REAL ぐりぐり wheel notch only during a valid flight.

        The normal remote UP/DOWN commands are intentionally left alone.
        The wheel's direction is compared with *scrollbar* movement, not the
        direction of content moving past the screen. This avoids a confusing
        inversion when the shuriken is thrown upward.
        """
        if self._flight is None or command not in ('UP', 'DOWN'):
            return False
        if self._target() is not self._flight_target:
            self._stop()  # A workspace/modal/target change is NOT a landing.
            return False
        direction = 1 if command == 'DOWN' else -1
        flight_direction = 1 if self._flight.distance_px > 0 else -1
        if direction == flight_direction:
            self._reverse_notches = 0
            self._cruise_rate = min(MAX_CRUISE_RATE,
                                    max(MIN_CRUISE_RATE, self._cruise_rate * WHEEL_ACCEL_FACTOR))
        else:
            self._cruise_rate = max(MIN_CRUISE_RATE,
                                    self._cruise_rate * WHEEL_DECEL_FACTOR)
            if self._auto_wheel_flight:
                self._reverse_notches += 1
                if self._reverse_notches >= AUTO_SHURIKEN_REVERSE_STOP_NOTCHES:
                    self._settle()
                    return True
        self._update_feedback()
        return True

    def start_from_wheel(self, signed_direction, *, source='list'):
        """Start the EXISTING full-range shuriken from sustained fast wheel.

        +1 = wheel UP = scrollbar UP, -1 = wheel DOWN = scrollbar DOWN.
        Does not fake a pointer flick or change selected files. The original
        physical button remains a manual fallback for this experiment.
        """
        if self._flight is not None or signed_direction not in (-1, 1):
            return False
        self._auto_wheel_flight = True
        self._auto_wheel_source = source
        target = self._target()
        if target is None:
            self._auto_wheel_flight = False
            self._auto_wheel_source = None
            return False
        bar = target.verticalScrollBar()
        if bar is None:
            self._auto_wheel_flight = False
            self._auto_wheel_source = None
            return False
        # Existing gesture planner uses positive delta for scrollbar DOWN.
        gesture = ScrollFlight(-signed_direction * 200, 0.9,
                               AUTO_SHURIKEN_INITIAL_SPEED)
        flight = plan_full_range_flight(
            gesture, bar.value(), bar.minimum(), bar.maximum(), bar.pageStep())
        if flight is None:
            self._auto_wheel_flight = False
            self._auto_wheel_source = None
            return False
        self._begin_flight(target, bar, flight)
        return True

    def _begin_flight(self, target, bar, flight):
        self._flight = flight
        self._flight_target = target
        self._flight_bounds = (bar.minimum(), bar.maximum())
        self._flight_start_time = time.monotonic()
        self._last_tick_time = self._flight_start_time
        self._flight_elapsed_s = 0.0
        self._cruise_rate = 1.0
        self._reverse_notches = 0
        self._last_displacement = 0
        self._timer.start()
        self._update_feedback()

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            event.ignore()
            return
        if self._flight is not None:
            # Begin slow braking as soon as pressed. A short release commits
            # that slowdown; holding for 0.52 s stops without a new throw.
            self._braking_press = True
            self._brake_press_time = time.monotonic()
            self._pressed = False
            self._update_feedback()
        else:
            self._pressed = True
            self._braking_press = False
            self._samples = [self._sample(event)]
        event.accept()

    def mouseMoveEvent(self, event):
        if self._pressed and (event.buttons() & Qt.MouseButton.LeftButton):
            sample = self._sample(event)
            self._samples.append(sample)
            # Limit memory while preserving the original press location.
            if len(self._samples) > 72:
                self._samples = self._samples[:1] + self._samples[-70:]
            event.accept()
            return
        event.ignore()

    def mouseReleaseEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            event.ignore()
            return
        if self._braking_press:
            if self._flight is not None:
                # Consume the actual hold interval at reduced speed before
                # committing another tap, so progress does not jump on release.
                self._scroll_tick()
                if self._flight is not None:
                    held_s = time.monotonic() - self._brake_press_time
                    if held_s >= HOLD_TO_STOP_S:
                        self._stop()
                    else:
                        self._cruise_rate = max(
                            MIN_CRUISE_RATE, self._cruise_rate * TAP_SLOW_FACTOR)
            self._braking_press = False
            self._brake_press_time = 0.0
            self._update_feedback()
            event.accept()
            return
        if self._pressed:
            self._samples.append(self._sample(event))
            gesture = plan_flick(self._samples)
            self._pressed = False
            self._samples = []
            if gesture is not None:
                target = self._target()
                if target is not None:
                    bar = target.verticalScrollBar()
                    if bar is not None:
                        lower, upper = bar.minimum(), bar.maximum()
                        # A swipe is planned against the *remaining* range,
                        # not a universal 2,000px travel cap.
                        flight = plan_full_range_flight(
                            gesture, bar.value(), lower, upper, bar.pageStep())
                        if flight is not None:
                            self._auto_wheel_flight = False
                            self._auto_wheel_source = None
                            self._begin_flight(target, bar, flight)
        event.accept()

    def _scroll_tick(self):
        flight = self._flight
        if flight is None:
            self._stop()
            return
        # Never scroll a different list if the user changes workspace,
        # current Remote target, closes a dialog, or hides the list mid-flight.
        if self._target() is not self._flight_target:
            self._stop()
            return
        # If Files List contents were replaced during a flight, stop rather
        # than continuing toward a stale scrollbar endpoint.
        bar = self._flight_target.verticalScrollBar()
        if (bar is None or self._flight_bounds is None
                or (bar.minimum(), bar.maximum()) != self._flight_bounds):
            self._stop()
            return
        now = time.monotonic()
        if self._braking_press and now - self._brake_press_time >= HOLD_TO_STOP_S:
            self._settle()
            return
        # Virtual time controls rate, while the physics profile always aims
        # for the ORIGINAL scroll end. Tapping changes rate, not destination.
        dt = max(0.0, now - self._last_tick_time)
        self._last_tick_time = now
        rate = (self._cruise_rate * HELD_SLOW_FACTOR
                if self._braking_press else self._cruise_rate)
        self._flight_elapsed_s += dt * rate
        elapsed = self._flight_elapsed_s
        position = round(eased_displacement(flight, elapsed))
        delta = position - self._last_displacement
        self._last_displacement = position
        if delta:
            self.scroll_requested.emit(delta)
        # Reaching the edge is a legitimate end; a short click slows the
        # journey, while a held click is the deliberate full stop.
        edge = self._flight_bounds[1] if flight.distance_px > 0 else self._flight_bounds[0]
        if elapsed >= flight.duration_s or bar.value() == edge:
            self._settle()
        else:
            self._update_feedback()

    def _stop(self):
        self._finish(settle=False)

    def _settle(self):
        self._finish(settle=True)

    def _finish(self, *, settle):
        # A genuine landing/long brake transfers the logical current. Hiding
        # the Remote or losing the Files List target MUST NOT touch selection.
        settled_target = (self._flight_target if settle and self._flight is not None
                          and self._target() is self._flight_target else None)
        was_auto = self._auto_wheel_flight
        self._timer.stop()
        self._flight = None
        self._flight_target = None
        self._flight_bounds = None
        self._auto_wheel_flight = False
        self._auto_wheel_source = None
        self._reverse_notches = 0
        self._flight_start_time = 0.0
        self._last_tick_time = 0.0
        self._flight_elapsed_s = 0.0
        self._cruise_rate = 1.0
        self._brake_press_time = 0.0
        self._last_displacement = 0
        self._pressed = False
        self._samples = []
        self._update_feedback()
        if was_auto and callable(self.auto_end_callback):
            self.auto_end_callback()
        if settled_target is not None:
            self.flight_settled.emit(settled_target)

    def hideEvent(self, event):
        self._stop()
        self._braking_press = False
        super().hideEvent(event)
