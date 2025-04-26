<#
.SYNOPSIS
    Gestion sécurisée des ports réseau pour Node.js
.VERSION
    2.0
#>

param (
    [int[]]$Ports = @(3000),
    [string]$NodeScript = "server.js",
    [switch]$KillExisting = $false
)

# Vérification des privilèges admin
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "Relance avec élévation de privilèges..." -ForegroundColor Yellow
    Start-Process powershell -Verb RunAs -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$($MyInvocation.MyCommand.Path)`" -Ports $($Ports -join ',') -NodeScript `"$NodeScript`""
    exit
}

# Configuration
$FirewallRulePrefix = "NodeJS_Port_"
$LogFile = Join-Path $PSScriptRoot "nodejs_ports.log"

# Initialisation
Start-Transcript -Path $LogFile -Append

# Fonctions
function Manage-FirewallPorts {
    param($Action)
    foreach ($port in $Ports) {
        $ruleName = "$FirewallRulePrefix$port"
        switch ($Action) {
            'Open' {
                if (-not (Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue)) {
                    New-NetFirewallRule -DisplayName $ruleName -Direction Inbound -LocalPort $port -Protocol TCP -Action Allow
                    Write-Host "Port $port ouvert"
                }
            }
            'Close' {
                if (Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue) {
                    Remove-NetFirewallRule -DisplayName $ruleName
                    Write-Host "Port $port fermé"
                }
            }
        }
    }
}

function Start-NodeServer {
    try {
        Write-Host "Démarrage de Node.js..."
        $process = Start-Process node -ArgumentList $NodeScript -PassThru -WindowStyle Hidden
        Start-Sleep -Seconds 2
        return $process
    } catch {
        Write-Host "Erreur démarrage Node: $_" -ForegroundColor Red
        exit 1
    }
}

# Main
try {
    # Nettoyage initial
    if ($KillExisting) {
        Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force
    }

    # Gestion des ports
    Manage-FirewallPorts -Action 'Open'
    $nodeProcess = Start-NodeServer

    # Affichage informations
    Write-Host "`nServeur Node.js en cours d'exécution" -ForegroundColor Green
    Write-Host "PID: $($nodeProcess.Id)"
    Write-Host "Ports: $($Ports -join ', ')"
    Write-Host "Logs: $LogFile`n"

    # Attente
    $nodeProcess.WaitForExit()
}
catch {
    Write-Host "ERREUR: $_" -ForegroundColor Red
}
finally {
    # Nettoyage
    Manage-FirewallPorts -Action 'Close'
    Stop-Transcript
}