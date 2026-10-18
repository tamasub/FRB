"""Launch-owned, nonpersistent appearance hint for FRB Studio NativeShell."""

def studio_launch_arguments(program, args, theme='light'):
    """Leave unrelated programs and explicit Studio theme overrides untouched."""
    result = list(args or [])
    executable = str(program or '').strip().strip('"').replace('\\', '/').casefold()
    if executable.rsplit('/', 1)[-1] != 'frbstudio.nativeshell.exe':
        return result
    if any(str(a).casefold().startswith('--studio-theme=') for a in result):
        return result
    return [*result, '--studio-theme=' + theme]
