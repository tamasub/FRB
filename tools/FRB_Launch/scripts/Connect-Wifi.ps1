[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$ProfileName,
    [string]$ProbeUrl = '',
    [string]$InterfaceName = '',
    [ValidateRange(5,60)][int]$TimeoutSeconds = 30
)
$ErrorActionPreference = 'Stop'
& "$env:SystemRoot\System32\chcp.com" 65001 | Out-Null
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding = [Console]::OutputEncoding
$logDir = Join-Path $env:LOCALAPPDATA 'FRBLaunch'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$logPath = Join-Path $logDir 'wifi.log'
function Report([string]$Text) {
    Write-Host $Text
    Add-Content -LiteralPath $logPath -Value ((Get-Date -Format 'yyyy/MM/dd HH:mm:ss') + ' ' + $Text) -Encoding UTF8
}
try {
    if ([string]::IsNullOrWhiteSpace($ProfileName) -or $ProfileName.StartsWith('REPLACE_') -or $ProfileName -match '["\r\n]') {
        throw 'Set a saved Wi-Fi profile name in the launcher JSON first.'
    }
    if ($ProbeUrl) {
        $uri = [Uri]$ProbeUrl
        if (-not $uri.IsAbsoluteUri -or $uri.Scheme -notin @('http','https')) { throw 'ProbeUrl must be an http/https URL.' }
    }
    Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
using System.ComponentModel;
public static class FrbWlan {
    [StructLayout(LayoutKind.Sequential, CharSet=CharSet.Unicode)]
    struct Info {
        public Guid Id;
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst=256)] public string Description;
        public int State;
    }
    [DllImport("wlanapi.dll")] static extern uint WlanOpenHandle(uint version, IntPtr reserved, out uint negotiated, out IntPtr handle);
    [DllImport("wlanapi.dll")] static extern uint WlanEnumInterfaces(IntPtr handle, IntPtr reserved, out IntPtr list);
    [DllImport("wlanapi.dll")] static extern uint WlanQueryInterface(IntPtr handle, ref Guid id, int opcode, IntPtr reserved, out uint size, out IntPtr data, out int type);
    [DllImport("wlanapi.dll")] static extern uint WlanCloseHandle(IntPtr handle, IntPtr reserved);
    [DllImport("wlanapi.dll")] static extern void WlanFreeMemory(IntPtr memory);
    static void Check(uint result) { if(result!=0) throw new Win32Exception((int)result); }
    public static bool Connected(string profile, string adapter) {
        IntPtr handle=IntPtr.Zero, list=IntPtr.Zero; uint version;
        Check(WlanOpenHandle(2,IntPtr.Zero,out version,out handle));
        try {
            Check(WlanEnumInterfaces(handle,IntPtr.Zero,out list));
            int count=Marshal.ReadInt32(list), stride=Marshal.SizeOf(typeof(Info));
            for(int i=0;i<count;i++) {
                Info info=(Info)Marshal.PtrToStructure(IntPtr.Add(list,8+i*stride),typeof(Info));
                if(info.State!=1) continue;
                // Native interface descriptions are not netsh aliases. Resolve alias separately.
                if(adapter.Length>0 && info.Id!=Guid.Parse(adapter)) continue;
                uint size; int type; IntPtr data=IntPtr.Zero;
                uint result=WlanQueryInterface(handle,ref info.Id,7,IntPtr.Zero,out size,out data,out type);
                try {
                    if(result==5) Check(result);
                    if(result==0 && size>=520 && Marshal.ReadInt32(data)==1) {
                        string current=Marshal.PtrToStringUni(IntPtr.Add(data,8),256).TrimEnd('\0');
                        if(String.Equals(current,profile,StringComparison.Ordinal)) return true;
                    }
                } finally { if(data!=IntPtr.Zero) WlanFreeMemory(data); }
            }
            return false;
        } finally { if(list!=IntPtr.Zero) WlanFreeMemory(list); WlanCloseHandle(handle,IntPtr.Zero); }
    }
}
'@
    $adapterId = ''
    if ($InterfaceName) {
        $adapter = Get-NetAdapter -Name $InterfaceName -ErrorAction Stop
        $adapterId = [string]$adapter.InterfaceGuid
    }
    Report ('Connecting: ' + $ProfileName)
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    if (-not [FrbWlan]::Connected($ProfileName,$adapterId)) {
        $netshArgs = @('wlan','connect',('name=' + $ProfileName))
        if ($InterfaceName) { $netshArgs += ('interface=' + $InterfaceName) }
        $output = & "$env:SystemRoot\System32\netsh.exe" @netshArgs 2>&1
        $code = $LASTEXITCODE
        foreach ($line in $output) { Report ([string]$line) }
        if ($code -ne 0) { throw ('netsh failed (' + $code + '). Check the saved profile and Wi-Fi adapter.') }
    }
    $ok = $false
    while ((Get-Date) -lt $deadline) {
        if ([FrbWlan]::Connected($ProfileName,$adapterId)) {
            if (-not $ProbeUrl) { $ok=$true;break }
            $response=$null
            try {
                $request = [Net.HttpWebRequest]::Create($ProbeUrl)
                $request.Proxy = $null
                $request.Timeout = 1500; $request.ReadWriteTimeout = 1500
                $request.AllowAutoRedirect = $false
                try { $response=$request.GetResponse() }
                catch [Net.WebException] {
                    # Authentication or other HTTP status still proves that the web server answered.
                    if ($_.Exception.Response) { $response=$_.Exception.Response } else { throw }
                }
                $ok=$true
            } catch { $ok=$false }
            finally { if ($response) { $response.Close() } }
            if ($ok) { break }
        }
        Start-Sleep -Milliseconds 500
    }
    if (-not $ok) { throw 'Timed out waiting for the selected Wi-Fi profile / web server. Check device power, saved profile and URL.' }
    Report ('Connected: ' + $ProfileName)
    if ($ProbeUrl) { Report ('Web server ready: ' + $ProbeUrl) }
    exit 0
} catch {
    Report ('ERROR: ' + $_.Exception.Message)
    Report 'If Windows denies WLAN access, check Settings > Privacy & security > Location (desktop apps).'
    Report ('Log: ' + $logPath)
    Start-Sleep -Seconds 2
    exit 1
}
