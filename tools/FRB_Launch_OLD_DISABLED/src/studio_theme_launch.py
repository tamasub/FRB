"""The launcher does not own FRB Studio's persisted color preference."""


def studio_launch_arguments(program, args, theme=None):
    """Pass user-declared arguments through; Studio resolves its own appearance.

    The retired default ``--studio-theme=light`` prevented Studio's saved
    dark/light choice from being restored at startup (including its splash).
    ``theme`` remains optional for API compatibility and is intentionally unused.
    Explicit --studio-theme arguments entered by the user are preserved.
    """
    return list(args or [])
