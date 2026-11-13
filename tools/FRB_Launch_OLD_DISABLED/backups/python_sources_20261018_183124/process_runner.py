"""Launch a process with an optional independent Windows console."""
import os
import subprocess


def start_process(program, arguments, cwd, show_console=False, log_path=None):
    options = {'cwd': cwd}
    if os.name == 'nt':
        options['creationflags'] = subprocess.CREATE_NEW_CONSOLE if show_console else subprocess.CREATE_NO_WINDOW
    if not show_console:
        options.update(stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if log_path is not None:
        # Capture errors emitted before the PowerShell script's own catch block,
        # e.g. execution-policy restrictions, parse errors, and startup failures.
        stream = open(log_path, 'ab')
        try:
            options.update(stdout=stream, stderr=subprocess.STDOUT)
            return subprocess.Popen([program, *arguments], **options)
        finally:
            stream.close()
    return subprocess.Popen([program, *arguments], **options)


def should_start_before_dismiss(steps):
    """A detached GUI launch must inherit the launcher's foreground privilege.

    Hiding the launcher first transfers keyboard foreground to another app;
    Windows may then refuse to foreground the new GUI process/splash.
    Waiting/background/console jobs retain the existing deferred execution.
    An action can explicitly opt out with launch_foreground_on_start=False.
    """
    if not steps:
        return False
    first = steps[0]
    return (
        first.get('launch_action_type') == 'Run'
        and bool(first.get('launch_program'))
        and not first.get('launch_wait_for_exit', False)
        and not first.get('launch_show_console', False)
        and first.get('launch_foreground_on_start', True) is not False
    )
