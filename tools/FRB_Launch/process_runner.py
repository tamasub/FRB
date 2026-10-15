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
