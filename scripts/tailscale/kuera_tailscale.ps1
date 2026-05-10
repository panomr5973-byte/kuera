# KUERA Tailscale Network Manager
# Manage and test connectivity across your tailnet
# Usage: .\kuera_tailscale.ps1 -Action <status|test-proxy|test-ollama|ssh|machines>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("status", "test-proxy", "test-ollama", "ssh", "machines", "test-all")]
    [string]$Action
)

$ErrorActionPreference = "Stop"

# Tailnet configuration
$VPS_IP = "100.111.193.44"
$WINDOWS_IP = "192.168.1.100"
$ANDROID_IP = "100.99.229.51"
$NGINX_PORT = 9090
$OLLAMA_PORT = 11434

function Write-Header($text) {
    Write-Host "`n==========================================" -ForegroundColor Cyan
    Write-Host "  $text" -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Cyan
}

function Write-Ok($text) { Write-Host "[OK] $text" -ForegroundColor Green }
function Write-Warn($text) { Write-Host "[WARN] $text" -ForegroundColor Yellow }
function Write-Err($text) { Write-Host "[ERR] $text" -ForegroundColor Red }
function Write-Info($text) { Write-Host "[INFO] $text" -ForegroundColor White }

function Test-TailscaleInstalled {
    try {
        $ver = tailscale version 2>$null | Select-Object -First 1
        if ($ver) { return $ver }
    } catch {}
    return $null
}

function Test-ConnectionQuick($ip, $port, $name) {
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $tcp.Connect($ip, $port)
        $tcp.Close()
        Write-Ok "$name ($ip`:$port) - REACHABLE"
        return $true
    } catch {
        Write-Err "$name ($ip`:$port) - UNREACHABLE"
        return $false
    }
}

function Test-HttpStatus($url, $name) {
    try {
        $resp = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 10 -ErrorAction Stop
        Write-Ok "$name → HTTP $($resp.StatusCode)"
        return $true
    } catch {
        if ($_.Exception.Response) {
            Write-Warn "$name → HTTP $($_.Exception.Response.StatusCode.value__)"
        } else {
            Write-Err "$name → FAILED: $($_.Exception.Message)"
        }
        return $false
    }
}

# ===== ACTIONS =====

switch ($Action) {
    "status" {
        Write-Header "Tailscale Network Status"

        $ver = Test-TailscaleInstalled
        if ($ver) { Write-Ok "Tailscale installed: $ver" }
        else { Write-Err "Tailscale not found"; exit 1 }

        Write-Info "Testing connectivity..."
        Test-ConnectionQuick $VPS_IP 22 "VPS SSH"
        Test-ConnectionQuick $VPS_IP $NGINX_PORT "VPS Nginx"
        Test-ConnectionQuick $VPS_IP $OLLAMA_PORT "VPS Ollama"

        Write-Info "HTTP tests..."
        Test-HttpStatus "http://$VPS_IP`:$NGINX_PORT/nginx-health" "VPS Nginx Health"
        Test-HttpStatus "http://$VPS_IP`:$NGINX_PORT/" "VPS → KUERA Proxy"
    }

    "test-proxy" {
        Write-Header "Testing VPS Reverse Proxy"

        $urls = @(
            @{Url="http://$VPS_IP`:$NGINX_PORT/nginx-health"; Name="Nginx Health"}
            @{Url="http://$VPS_IP`:$NGINX_PORT/"; Name="KUERA Control Panel"}
            @{Url="http://$VPS_IP`:$NGINX_PORT/api/services"; Name="KUERA API /services"}
            @{Url="http://$VPS_IP`:$NGINX_PORT/api/health"; Name="KUERA API /health"}
        )

        foreach ($u in $urls) {
            Test-HttpStatus $u.Url $u.Name
        }
    }

    "test-ollama" {
        Write-Header "Testing Ollama on VPS"

        try {
            $resp = Invoke-WebRequest -Uri "http://$VPS_IP`:$OLLAMA_PORT/api/tags" -UseBasicParsing -TimeoutSec 10
            Write-Ok "Ollama is running!"
            $data = $resp.Content | ConvertFrom-Json
            Write-Info "Models loaded: $($data.models.Count)"
            foreach ($m in $data.models | Select-Object -First 5) {
                Write-Info "  - $($m.name)"
            }
        } catch {
            Write-Err "Ollama not reachable: $($_.Exception.Message)"
        }
    }

    "ssh" {
        Write-Header "SSH to VPS via Tailscale"
        Write-Info "Connecting to root@$VPS_IP ..."
        ssh root@$VPS_IP
    }

    "machines" {
        Write-Header "Tailnet Machines"
        tailscale status
    }

    "test-all" {
        Write-Header "Full Tailnet Health Check"

        . $PSCommandPath -Action status
        . $PSCommandPath -Action test-proxy
        . $PSCommandPath -Action test-ollama

        Write-Header "Summary"
        Write-Info "VPS: $VPS_IP"
        Write-Info "Windows: $WINDOWS_IP"
        Write-Info "Android: $ANDROID_IP (may be offline)"
        Write-Info ""
        Write-Info "To enable public access:"
        Write-Info "  1. Enable Tailscale Funnel: https://login.tailscale.com/f/funnel?node=nuyBxkS1Wk11CNTRL"
        Write-Info "  2. On VPS: tailscale funnel --bg $NGINX_PORT"
    }
}
