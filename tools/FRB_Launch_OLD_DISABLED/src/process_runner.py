"""Launch a process with an optional independent Windows console."""
import os
import subprocess
import ntpath
from pathlib import Path



_BATCH_SUFFIXES = frozenset(('.bat', '.cmd'))


def batch_script_working_directory(program, arguments=()):
    """Use the script's folder when a Run action actually starts a BAT/CMD.

    Only an existing script path (directly or immediately after cmd /c or /k)
    qualifies. Do not guess a directory from arbitrary shell command text.
    This prevents unrelated Run actions from losing their configured cwd.
    """
    def script_folder(raw):
        if not isinstance(raw, str):
            return None
        raw = raw.strip().strip('"')
        path = Path(raw)
        if path.suffix.casefold() not in _BATCH_SUFFIXES or not path.is_file():
            return None
        return str(path.resolve().parent)

    direct = script_folder(program)
    if direct:
        return direct
    if ntpath.basename(str(program)).casefold() not in ('cmd.exe', 'cmd'):
        return None
    args = list(arguments or ())
    for idx, arg in enumerate(args):
        if isinstance(arg, str) and arg.casefold() in ('/c', '/k'):
            if idx + 1 < len(args):
                return script_folder(args[idx + 1])
            break
    return None


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
