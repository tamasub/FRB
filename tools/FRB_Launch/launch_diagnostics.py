"""Diagnostics without logging text-send payloads or arbitrary command arguments."""
import base64
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime
from uuid import uuid4


def make_logger(folder):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    logger=logging.getLogger('frb.launch.diagnostics');logger.setLevel(logging.INFO)
    logger.propagate=False
    target=str(folder/'launch.log')
    if not any(getattr(h,'baseFilename',None)==target for h in logger.handlers):
        handler=RotatingFileHandler(target,maxBytes=1024*1024,backupCount=3,encoding='utf-8')
        handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
        logger.addHandler(handler)
    return logger


def ps_literal(value):
    return "'"+str(value).replace("'","''")+"'"


def wifi_transcript_arguments(program, arguments, folder):
    """Wrap only the Wi-Fi script, including parse/binding/early startup errors."""
    args=list(arguments)
    if Path(program.replace('\\','/')).name.lower() not in {'powershell.exe','powershell','pwsh.exe','pwsh'}:
        return args,None
    lowered=[str(a).lower() for a in args]
    if '-file' not in lowered:return args,None
    index=lowered.index('-file')
    if index+1>=len(args):return args,None
    script=args[index+1]
    script_name=Path(str(script).replace('\\','/')).name.lower()
    if script_name not in {'connect-wifi.ps1','set-audiooutput.ps1'}:return args,None
    kind='wifi' if script_name=='connect-wifi.ps1' else 'audio'
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    log=folder/(kind+'_process_'+datetime.now().strftime('%Y%m%d_%H%M%S')+'_'+uuid4().hex[:8]+'.log')
    # Array splatting treats '-ProfileName' as a positional string; use named splatting.
    tail=args[index+2:];params=[];i=0
    while i<len(tail):
        key=tail[i]
        if kind=='audio' and key in ('-List','-Choose'):
            params.append(ps_literal(key[1:])+'=$true');i+=1;continue
        allowed=('-ProfileName','-ProbeUrl','-InterfaceName','-TimeoutSeconds') if kind=='wifi' else ('-DeviceId','-ConfigPath','-VariableId')
        if key not in allowed:
            raise ValueError('Unsupported device script argument: '+str(key))
        if i+1>=len(tail):raise ValueError('Missing device argument value: '+str(key))
        params.append(ps_literal(key[1:])+'='+ps_literal(tail[i+1]));i+=2
    values=';'.join(params)
    command="""$ErrorActionPreference='Stop'
$transcriptStarted=$false
try {
    Start-Transcript -LiteralPath %s -Force -ErrorAction Stop | Out-Null
    $transcriptStarted=$true
    Write-Host 'FRB Launch: starting device script'
    $scriptArgs = @{%s}
    & %s @scriptArgs
    if (-not $?) { exit 1 }
} catch {
    Write-Host ('FRB Launch ERROR: ' + $_.Exception.ToString())
    Write-Host ($_ | Out-String)
    exit 1
} finally {
    if ($transcriptStarted) { Stop-Transcript -ErrorAction SilentlyContinue | Out-Null }
}
""" % (ps_literal(log),values,ps_literal(script))
    encoded=base64.b64encode(command.encode('utf-16le')).decode('ascii')
    return args[:index]+['-EncodedCommand',encoded],log
