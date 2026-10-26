"""Best-effort access to providers' native Explorer 'Copy link' action.

This does not synthesize a web URL from a sync path or grant permissions itself.
Windows 11's modern IExplorerCommand actions are not always exposed to the
legacy Shell.Application/FolderItem.Verbs automation collection.  When they
are not, we can only select the item in Explorer for the user to invoke the
provider's actual command.  Never report copying on that fallback.
"""

import base64
import os
from pathlib import Path
import subprocess


# Exact labels: never accidentally invoke Windows' generic Copy/Share commands.
COPY_LINK_NAMES = (
    'リンクのコピー',
    '共有リンクのコピー',
    '共有リンクをコピー',
    'Copy link',
    'Copy shared link',
    'Copy sharing link',
)


def _ps_literal(text):
    return "'" + str(text).replace("'", "''") + "'"


def copy_link_powershell_script(path):
    """Create a data-quoted PowerShell script; never execute path as code."""
    target = Path(path)
    accepted = ', '.join(_ps_literal(s) for s in COPY_LINK_NAMES)
    return (
        "$ErrorActionPreference = 'Stop'\n"
        "try {\n"
        "  $shell = New-Object -ComObject Shell.Application\n"
        f"  $folder = $shell.Namespace({_ps_literal(str(target.parent))})\n"
        "  if ($null -eq $folder) { Write-Output 'NO_COMMAND'; exit 0 }\n"
        f"  $item = $folder.ParseName({_ps_literal(target.name)})\n"
        "  if ($null -eq $item) { Write-Output 'NO_COMMAND'; exit 0 }\n"
        f"  $names = @({accepted})\n"
        "  foreach ($verb in $item.Verbs()) {\n"
        "    $label = ([string]$verb.Name) -replace '&', ''\n"
        "    $label = ($label -replace '\\(&.\\)', '').Trim()\n"
        "    $label = ($label -replace '(?:\\.\\.\\.|…)$', '').Trim()\n"
        "    if ($names -contains $label) {\n"
        "      $verb.DoIt()\n"
        "      Write-Output 'INVOCATION_REQUESTED'\n"
        "      exit 0\n"
        "    }\n"
        "  }\n"
        "  Write-Output 'NO_COMMAND'\n"
        "} catch {\n"
        "  Write-Output 'NO_COMMAND'\n"
        "}\n"
    )


def request_native_copy_link(path, *, runner=None):
    """Return True only if an exact provider verb was invoked (not copied).

    This should be triggered by an explicit user action. A successful native
    invocation may still open a provider-owned permission dialog or fail to
    copy. It must not be reported as verified clipboard success.
    """
    if os.name != 'nt':
        raise RuntimeError('クラウドリンク操作はWindows専用です')
    if not Path(path).exists():
        raise FileNotFoundError(str(path))
    encoded = base64.b64encode(copy_link_powershell_script(path).encode('utf-16-le')).decode('ascii')
    run = runner or subprocess.run
    try:
        result = run(['powershell.exe', '-NoProfile', '-Sta', '-EncodedCommand', encoded],
                     capture_output=True, text=True, encoding='utf-8', errors='replace',
                     timeout=10, check=False,
                     creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    except (OSError, subprocess.TimeoutExpired):
        return False
    return (result.returncode == 0 and
            'INVOCATION_REQUESTED' in (result.stdout or '').splitlines())


def select_in_explorer(path, *, opener=None):
    """Safe fallback: Explorer selects the actual item for manual Copy link.

    A single /select, argument avoids cmd.exe parsing and supports spaces,
    apostrophes and Japanese file/folder names.
    """
    if os.name != 'nt':
        raise RuntimeError('Windows専用です')
    if not Path(path).exists():
        raise FileNotFoundError(str(path))
    (opener or subprocess.Popen)(['explorer.exe', '/select,', str(path)])
