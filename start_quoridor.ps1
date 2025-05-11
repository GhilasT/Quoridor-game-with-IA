# start_quoridor.ps1

<#
.SYNOPSIS
  Lance le menu Quoridor sous Tkinter (et Pygame) via PowerShell.

.DESCRIPTION
  Place le répertoire de travail dans celui du script, 
  puis exécute le script Python.
#>

# 1. Se placer dans le dossier du script PowerShell
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $ScriptDir


# 2. Vérifier la présence de Python
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python n'est pas trouvé dans le PATH. Veuillez l'installer ou ajuster votre PATH."
    exit 1
}

# 3. Lancer le script Python
$MainScript = Join-Path $ScriptDir 'quoridor_menus.py'  # Modifiez 'votre_script.py' par le nom réel
if (Test-Path $MainScript) {
    Write-Host "Lancement de Quoridor…"
    & python $MainScript
} else {
    Write-Error "Script Python introuvable : $MainScript"
    exit 1
}
