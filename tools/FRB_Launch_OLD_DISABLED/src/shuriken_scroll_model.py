"""Qt-free release-to-launch physics for the FRB Remote shuriken scroll.

A deliberate mouse flick only *arms* a flight. Screen movement starts on
release, eases in, peaks, then eases out. Pressing the button again brakes it.
The actual flight is computed from the remaining scroll-bar range so one
flick can reach the end; only duration/velocity respond to gesture strength.
No mouse/keyboard input is synthesized.
"""
from dataclasses import dataclass
import math

TICK_MS = 16
DEADZONE_PX = 18
MOTION_WINDOW_S = 0.18
MIN_SPEED_PX_S = 60.0
MAX_SPEED_PX_S = 2500.0
MIN_TRAVEL_PX = 100
MAX_TRAVEL_PX = 2000
MIN_DURATION_S = 0.68
MAX_DURATION_S = 1.95  # Legacy gesture-analysis compatibility (not the full-range flight cap).

# One throw traverses the remaining scrollbar range. Flight time intentionally
# leaves a few seconds to hit the Remote button again to brake mid-show.
FULL_RANGE_MIN_DURATION_S = 2.8
FULL_RANGE_MAX_DURATION_S = 20.0
FULL_RANGE_BASE_S = 3.6
FULL_RANGE_PER_SQRT_PAGE_S = 1.5

# End-approach show: steady cruising until ~80% of the *distance*, then a
# visibly longer slow-down for the remaining ~20%. Time fractions below are
# intentional: the last 35% of the flight time is the arrival scene.
ARRIVAL_ACCEL_END = 0.18
ARRIVAL_DECEL_START = 0.65
ARRIVAL_BRAKE_POWER = 1.6


def arrival_progress(elapsed_fraction):
    """Monotonic 0..1 position profile with an obvious last-20% arrival.

    Velocity: linear rise -> constant cruise -> (1-s)**1.6 slow-down.
    We integrate the velocity exactly and normalize by total area, so even
    huge QScrollBar ranges land at exactly the requested end value.
    """
    u = _clamp(float(elapsed_fraction), 0.0, 1.0)
    a, b, power = ARRIVAL_ACCEL_END, ARRIVAL_DECEL_START, ARRIVAL_BRAKE_POWER
    total_area = a / 2 + (b - a) + (1 - b) / (power + 1)
    if u <= a:
        traveled = u * u / (2 * a)
    elif u <= b:
        traveled = a / 2 + (u - a)
    else:
        r = (u - b) / (1 - b)
        traveled = (a / 2 + b - a
                    + (1 - b) * (1 - (1 - r)**(power + 1)) / (power + 1))
    return _clamp(traveled / total_area, 0.0, 1.0)


@dataclass(frozen=True)
class ScrollFlight:
    """One bounded kinetic show, independent of widget event timing."""
    distance_px: int  # Signed scrollbar travel; up flick means positive.
    duration_s: float
    input_speed_px_s: float
    full_range: bool = False  # Different endpoint-oriented easing from the legacy trial.


def _clamp(value, low, high):
    return max(low, min(high, value))


def plan_flick(samples):
    """Convert (monotonic_time_s, global_x, global_y) samples into a flight.

    Only vertical gestures with recent movement are valid. This prevents an
    earlier drag followed by a long hold / plain release from launching an
    unexpected scroll. The velocity uses recent actual movement, not the
    distance from the starting cursor position alone.
    """
    if len(samples) < 2:
        return None
    try:
        points = [(float(t), float(x), float(y)) for t, x, y in samples]
    except (ValueError, TypeError):
        return None
    if not all(all(math.isfinite(v) for v in sample) for sample in points):
        return None
    if any(b[0] < a[0] for a, b in zip(points, points[1:])):
        return None

    dx = points[-1][1] - points[0][1]
    dy = points[-1][2] - points[0][2]
    if abs(dy) < DEADZONE_PX or abs(dy) < 1.1 * abs(dx):
        return None

    end_time = points[-1][0]
    recent_moves = [(a, b) for a, b in zip(points, points[1:])
                    if end_time - b[0] <= MOTION_WINDOW_S
                    and abs(b[2] - a[2]) > 0.5]
    if not recent_moves:
        return None
    earliest_start = recent_moves[0][0][0]
    latest_end = recent_moves[-1][1][0]
    # If the last actual pointer movement was long before release, cancel.
    if end_time - latest_end > MOTION_WINDOW_S:
        return None
    recent_dy = sum(b[2] - a[2] for a, b in recent_moves)
    if abs(recent_dy) < 5 or recent_dy * dy <= 0:
        return None
    recent_elapsed = max(0.035, latest_end - earliest_start)
    speed = abs(recent_dy) / recent_elapsed
    if speed < MIN_SPEED_PX_S:
        return None
    speed = _clamp(speed, MIN_SPEED_PX_S, MAX_SPEED_PX_S)

    # Stronger gesture increases BOTH travel and show duration, without
    # making the beginning abruptly fast. These constants are experiment knobs.
    travel = round(_clamp(speed * 0.80, MIN_TRAVEL_PX, MAX_TRAVEL_PX))
    duration = _clamp(MIN_DURATION_S + speed * 0.00050,
                      MIN_DURATION_S, MAX_DURATION_S)
    direction = 1 if dy < 0 else -1
    return ScrollFlight(direction * travel, duration, speed)


def eased_displacement(flight, elapsed_s):
    """Signed travel, landing at exactly the commanded end point.

    Legacy short-distance flights retain symmetric smoothstep easing. Full-
    range flights use the arrival profile with a visibly slower final fifth
    of travel, so approaching the end is apparent without guessing the time.
    """
    if flight is None:
        return 0.0
    duration = max(0.001, flight.duration_s)
    u = _clamp(float(elapsed_s) / duration, 0.0, 1.0)
    progress = (arrival_progress(u) if flight.full_range
                else u * u * (3.0 - 2.0 * u))
    return flight.distance_px * progress


def plan_full_range_flight(gesture, current, minimum, maximum, page_step):
    """Convert a recognized flick into ONE trip to the scroll end.

    Read actual QScrollBar units (which may vary with scroll mode); never
    guess that a scrollbar pixel corresponds to a screen pixel.

    The swipe speed changes HOW LONG the show takes, not whether the last
    item is reachable. A slow throw still gets to the end if not interrupted.
    The user is expected to brake by clicking the scroll pad again.
    """
    if gesture is None:
        return None
    try:
        current, minimum, maximum = int(current), int(minimum), int(maximum)
        page_step = max(1, int(page_step))
    except (TypeError, ValueError, OverflowError):
        return None
    if minimum > maximum or not (minimum <= current <= maximum):
        return None
    direction = 1 if gesture.distance_px > 0 else -1 if gesture.distance_px < 0 else 0
    if direction == 0:
        return None
    remaining = maximum - current if direction > 0 else current - minimum
    if remaining <= 0:
        return None

    # Large lists need a longer show, not a 2,000px cut-off. A sqrt-of-pages
    # scale keeps very large folders from taking minutes to traverse.
    pages = remaining / page_step
    strength = _clamp((gesture.input_speed_px_s - MIN_SPEED_PX_S) / 1400.0,
                      0.0, 1.0)
    duration = _clamp(
        (FULL_RANGE_BASE_S + FULL_RANGE_PER_SQRT_PAGE_S * math.sqrt(pages))
        * (1.20 - 0.50 * strength),
        FULL_RANGE_MIN_DURATION_S, FULL_RANGE_MAX_DURATION_S)
    return ScrollFlight(direction * remaining, duration,
                        gesture.input_speed_px_s, full_range=True)
