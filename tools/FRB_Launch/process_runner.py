"""Launch a process with an optional independent Windows console."""
import os
import subprocess


def start_process(program, arguments, cwd, show_console=False):
    options = {'cwd': cwd}
    if os.name == 'nt':
        options['creationflags'] = subprocess.CREATE_NEW_CONSOLE if show_console else subprocess.CREATE_NO_WINDOW
    if not show_console:
        options.update(stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return subprocess.Popen([program, *arguments], **options)
