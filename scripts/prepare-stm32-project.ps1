[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectPath,

    [string]$ProjectName,
    [string]$Device = "STM32F103C8",
    [string]$OpenOcdScripts,
    [string]$OpenOcdConfigName = "stm32f1-stlink.cfg"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$ProjectPath = [System.IO.Path]::GetFullPath($ProjectPath)

if (-not (Test-Path -LiteralPath $ProjectPath)) {
    throw "找不到工程目录: $ProjectPath"
}

if ([string]::IsNullOrWhiteSpace($ProjectName)) {
    $ProjectName = Split-Path -Leaf $ProjectPath
}

if ([string]::IsNullOrWhiteSpace($OpenOcdScripts)) {
    $openOcdCommand = Get-Command openocd -ErrorAction SilentlyContinue
    if ($null -ne $openOcdCommand) {
        $openOcdRoot = Split-Path -Parent (Split-Path -Parent $openOcdCommand.Source)
        $candidate = Join-Path $openOcdRoot "openocd\scripts"
        if (Test-Path -LiteralPath $candidate) {
            $OpenOcdScripts = $candidate
        }
    }
}

if ([string]::IsNullOrWhiteSpace($OpenOcdScripts)) {
    throw "没有找到 OpenOCD scripts 目录。请先运行 scripts/install-stm32-tools.ps1，或手动传入 -OpenOcdScripts。"
}

$projectFile = Join-Path $ProjectPath "CMakeLists.txt"
if (-not (Test-Path -LiteralPath $projectFile)) {
    throw "这个目录里没有 CMakeLists.txt。请先让 STM32CubeMX 生成 CMake 工程。"
}

function Replace-Placeholders {
    param([string]$FilePath)

    $utf8 = [System.Text.Encoding]::UTF8
    $content = [System.IO.File]::ReadAllText($FilePath, $utf8)
    $content = $content.Replace("<工程名>", $ProjectName)
    $content = $content.Replace("<OpenOCD scripts 目录>", $OpenOcdScripts.Replace("\", "/"))
    $content = $content.Replace("STM32F103C8", $Device)
    $utf8NoBom = [System.Text.UTF8Encoding]::new($false)
    [System.IO.File]::WriteAllText($FilePath, $content, $utf8NoBom)
}

$templateVsCode = Join-Path $ProjectRoot "templates\.vscode"
$targetVsCode = Join-Path $ProjectPath ".vscode"
if (Test-Path -LiteralPath $targetVsCode) {
    Copy-Item -Path (Join-Path $templateVsCode "*") -Destination $targetVsCode -Recurse -Force
} else {
    Copy-Item -LiteralPath $templateVsCode -Destination $targetVsCode -Recurse
}

Copy-Item -LiteralPath (Join-Path $ProjectRoot "templates\CMakePresets.json") -Destination (Join-Path $ProjectPath "CMakePresets.json") -Force

$targetCmakeDirectory = Join-Path $ProjectPath "cmake"
New-Item -ItemType Directory -Path $targetCmakeDirectory -Force | Out-Null
$targetToolchain = Join-Path $targetCmakeDirectory "gcc-arm-none-eabi.cmake"
if (-not (Test-Path -LiteralPath $targetToolchain)) {
    Copy-Item -LiteralPath (Join-Path $ProjectRoot "templates\cmake\gcc-arm-none-eabi.cmake") -Destination $targetToolchain
}

$targetOpenOcdDirectory = Join-Path $ProjectPath "openocd"
New-Item -ItemType Directory -Path $targetOpenOcdDirectory -Force | Out-Null
Copy-Item -LiteralPath (Join-Path $ProjectRoot "templates\openocd\stm32f1-stlink.cfg") -Destination (Join-Path $targetOpenOcdDirectory $OpenOcdConfigName) -Force

Get-ChildItem -LiteralPath $targetVsCode -File | ForEach-Object {
    if ($_.Extension -eq ".json") {
        Replace-Placeholders $_.FullName
    }
}

Replace-Placeholders (Join-Path $ProjectPath "CMakePresets.json")

Write-Host ""
Write-Host "工程已经准备好：" -ForegroundColor Green
Write-Host "  $ProjectPath"
Write-Host ""
Write-Host "下一步："
Write-Host "  1. 用 VS Code 打开这个工程目录。"
Write-Host "  2. 运行任务 CMake: configure (Debug)。"
Write-Host "  3. 运行任务 CMake: build (Debug)。"
Write-Host "  4. 连接 ST-Link 后按 F5。"
