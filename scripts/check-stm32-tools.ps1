[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$tools = @(
    @{
        Name = "ARM GCC"
        Command = "arm-none-eabi-gcc"
        Args = @("--version")
    },
    @{
        Name = "CMake"
        Command = "cmake"
        Args = @("--version")
    },
    @{
        Name = "Ninja"
        Command = "ninja"
        Args = @("--version")
    },
    @{
        Name = "OpenOCD"
        Command = "openocd"
        Args = @("--version")
    }
)

$failed = $false

foreach ($tool in $tools) {
    Write-Host ""
    Write-Host "检查 $($tool.Name)" -ForegroundColor Cyan

    $command = Get-Command $tool.Command -ErrorAction SilentlyContinue
    if ($null -eq $command) {
        Write-Host "找不到命令: $($tool.Command)" -ForegroundColor Red
        $failed = $true
        continue
    }

    Write-Host "路径: $($command.Source)"
    & $command.Source @($tool.Args)
    if ($LASTEXITCODE -ne 0) {
        Write-Host "$($tool.Name) 运行失败。" -ForegroundColor Red
        $failed = $true
    }
}

Write-Host ""
if ($failed) {
    Write-Host "有工具没有通过检查。请把上面的完整错误告诉 Codex。" -ForegroundColor Red
    exit 1
}

Write-Host "四个工具全部检查通过。" -ForegroundColor Green
Write-Host "如果 VS Code 和 STM32CubeMX 也已经安装，就可以开始新建工程了。"
