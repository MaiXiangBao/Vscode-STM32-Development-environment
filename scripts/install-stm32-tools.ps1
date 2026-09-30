[CmdletBinding()]
param(
    [switch]$SkipVsCodeExtensions
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Test-CommandAvailable {
    param([string]$Name)
    return $null -ne (Get-Command $Name -ErrorAction SilentlyContinue)
}

function Install-WingetPackage {
    param(
        [string]$Id,
        [string]$Name
    )

    Write-Step "检查和安装 $Name"
    winget list --id $Id --exact --source winget *> $null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "$Name 已经安装，跳过。"
        return
    }

    winget install --id $Id --source winget --accept-source-agreements --accept-package-agreements --silent
    if ($LASTEXITCODE -ne 0) {
        throw "$Name 安装失败。请把上面的完整错误告诉 Codex。"
    }
}

Write-Host "STM32 工具安装助手" -ForegroundColor Green
Write-Host "这个脚本只会安装下面四个命令行工具："
Write-Host "  Arm GNU Toolchain"
Write-Host "  CMake"
Write-Host "  Ninja"
Write-Host "  OpenOCD xPack"
Write-Host ""
Write-Host "它不会安装或修改 VS Code 和 STM32CubeMX。"

if (-not (Test-CommandAvailable "winget")) {
    throw "没有找到 winget。请先安装 Microsoft App Installer，或者让 Codex 改用官方下载页面。"
}

Install-WingetPackage "Arm.ArmGnuToolchain" "Arm GNU Toolchain"
Install-WingetPackage "Kitware.CMake" "CMake"
Install-WingetPackage "Ninja-build.Ninja" "Ninja"
Install-WingetPackage "xpack-dev-tools.openocd-xpack" "OpenOCD xPack"

Write-Step "刷新当前 PowerShell 的 PATH"
$machinePath = [Environment]::GetEnvironmentVariable("Path", "Machine")
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
$env:Path = @($machinePath, $userPath) -join ";"

if (-not $SkipVsCodeExtensions) {
    Write-Step "安装 VS Code 扩展"
    if (-not (Test-CommandAvailable "code")) {
        Write-Warning "没有找到 code 命令。请打开 VS Code，按 Ctrl+Shift+P，运行 Shell Command: Install 'code' command in PATH。"
    } else {
        $extensions = @(
            "ms-vscode.cpptools",
            "twxs.cmake",
            "ms-vscode.cmake-tools",
            "marus25.cortex-debug",
            "dan-c-underwood.arm"
        )

        foreach ($extension in $extensions) {
            Write-Host "安装扩展: $extension"
            code --install-extension $extension
        }
    }
}

Write-Step "检查安装结果"
$checkScript = Join-Path $PSScriptRoot "check-stm32-tools.ps1"
& powershell -ExecutionPolicy Bypass -File $checkScript

Write-Host ""
Write-Host "STM32 命令行工具部署完成。" -ForegroundColor Green
Write-Host "下一步请打开 BEGINNER-GUIDE.md，从第 1 步开始阅读。"
