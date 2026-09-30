# 07 命令与配置速查表

[上一章：故障排查](./06-troubleshooting.md) | [返回主页](../README.md)

## 1. 环境验证

```powershell
arm-none-eabi-gcc --version
arm-none-eabi-gdb --version
arm-none-eabi-objcopy --version
arm-none-eabi-size --version
cmake --version
ninja --version
openocd --version
code --version
```

## 2. 路径检查

```powershell
where.exe arm-none-eabi-gcc
where.exe arm-none-eabi-gdb
where.exe cmake
where.exe ninja
where.exe openocd
where.exe code
```

查看当前 PATH：

```powershell
$env:Path -split ";"
```

只查找 STM32 相关路径：

```powershell
$env:Path -split ";" |
  Select-String -Pattern "arm|cmake|ninja|openocd|STM32" -CaseSensitive:$false
```

## 3. 常用 VS Code 扩展命令

```powershell
code --install-extension ms-vscode.cpptools
code --install-extension twxs.cmake
code --install-extension ms-vscode.cmake-tools
code --install-extension marus25.cortex-debug
code --install-extension dan-c-underwood.arm
code --install-extension EditorConfig.EditorConfig

code --list-extensions
```

## 4. 打开工程

```powershell
code C:\STM32\Projects\stm32f103c8t6-blink
```

## 5. CMake 配置和构建

```powershell
# 查看 presets
cmake --list-presets

# 配置 Debug
cmake --preset debug

# 构建 Debug
cmake --build --preset debug

# 清理后重建
cmake --build --preset debug --clean-first

# 配置 Release
cmake --preset release

# 构建 Release
cmake --build --preset release
```

删除本工程的 Debug 构建目录：

```powershell
Remove-Item .\build\Debug -Recurse -Force
```

## 6. 查找固件

```powershell
Get-ChildItem .\build -Recurse -Include *.elf,*.hex,*.bin,*.map |
  Sort-Object LastWriteTime -Descending |
  Select-Object Name,FullName,Length,LastWriteTime
```

## 7. 查看固件大小

```powershell
arm-none-eabi-size .\build\Debug\stm32f103c8t6-blink.elf
```

更详细的段信息：

```powershell
arm-none-eabi-size -A .\build\Debug\stm32f103c8t6-blink.elf
```

## 8. 生成 HEX 和 BIN

```powershell
arm-none-eabi-objcopy -O ihex `
  .\build\Debug\stm32f103c8t6-blink.elf `
  .\build\Debug\stm32f103c8t6-blink.hex

arm-none-eabi-objcopy -O binary `
  .\build\Debug\stm32f103c8t6-blink.elf `
  .\build\Debug\stm32f103c8t6-blink.bin
```

## 9. 反汇编

```powershell
arm-none-eabi-objdump -d `
  .\build\Debug\stm32f103c8t6-blink.elf `
  > .\build\Debug\stm32f103c8t6-blink.disassembly.txt
```

查看所有段：

```powershell
arm-none-eabi-objdump -h .\build\Debug\stm32f103c8t6-blink.elf
```

## 10. OpenOCD 单独测试 STM32F1

```powershell
openocd `
  -s "C:\Tools\xpack-openocd\openocd\scripts" `
  -f "openocd\stm32f1-stlink.cfg" `
  -c "init; targets; shutdown"
```

## 11. OpenOCD 烧录 ELF

```powershell
openocd `
  -s "C:\Tools\xpack-openocd\openocd\scripts" `
  -f "openocd\stm32f1-stlink.cfg" `
  -c "program build/Debug/stm32f103c8t6-blink.elf verify reset exit"
```

## 12. OpenOCD 烧录 HEX

```powershell
openocd `
  -s "C:\Tools\xpack-openocd\openocd\scripts" `
  -f "openocd\stm32f1-stlink.cfg" `
  -c "program build/Debug/stm32f103c8t6-blink.hex verify reset exit"
```

## 13. OpenOCD 复位和擦除

只复位并运行：

```powershell
openocd `
  -s "C:\Tools\xpack-openocd\openocd\scripts" `
  -f "openocd\stm32f1-stlink.cfg" `
  -c "init; reset run; shutdown"
```

擦除 F1 主 Flash：

```powershell
openocd `
  -s "C:\Tools\xpack-openocd\openocd\scripts" `
  -f "openocd\stm32f1-stlink.cfg" `
  -c "init; reset halt; stm32f1x mass_erase 0; reset run; shutdown"
```

擦除会删除当前程序，执行前确认目标开发板。

## 14. OpenOCD target 对照

| 芯片系列 | target 文件 |
| --- | --- |
| STM32F0 | `target/stm32f0x.cfg` |
| STM32F1 | `target/stm32f1x.cfg` |
| STM32F2 | `target/stm32f2x.cfg` |
| STM32F3 | `target/stm32f3x.cfg` |
| STM32F4 | `target/stm32f4x.cfg` |
| STM32F7 | `target/stm32f7x.cfg` |
| STM32G0 | `target/stm32g0x.cfg` |
| STM32G4 | `target/stm32g4x.cfg` |
| STM32H7 | `target/stm32h7x.cfg` |
| STM32L0 | `target/stm32l0.cfg` |
| STM32L1 | `target/stm32l1.cfg` |
| STM32L4 | `target/stm32l4x.cfg` |
| STM32WB | `target/stm32wbx.cfg` |
| STM32WL | `target/stm32wlx.cfg` |

最终以 OpenOCD 安装目录中的实际文件为准。

## 15. OpenOCD interface 对照

| 调试器 | interface 文件 |
| --- | --- |
| ST-Link | `interface/stlink.cfg` |
| CMSIS-DAP | `interface/cmsis-dap.cfg` |
| J-Link | `interface/jlink.cfg` |
| FTDI | `interface/ftdi/...cfg` |

## 16. 常用 OpenOCD 命令

在 GDB Console 中：

```gdb
monitor init
monitor reset halt
monitor reset run
monitor targets
monitor flash list
monitor adapter speed 1000
```

在 OpenOCD 配置文件或 `-c` 中：

```tcl
adapter speed 1000
init
reset halt
targets
shutdown
```

## 17. Cortex-Debug launch.json 最小模板

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug (OpenOCD + ST-Link)",
      "type": "cortex-debug",
      "request": "launch",
      "servertype": "openocd",
      "cwd": "${workspaceFolder}",
      "executable": "${workspaceFolder}/build/Debug/stm32f103c8t6-blink.elf",
      "device": "STM32F103C8",
      "configFiles": [
        "${workspaceFolder}/openocd/stm32f1-stlink.cfg"
      ],
      "searchDir": [
        "C:/Tools/xpack-openocd/openocd/scripts"
      ],
      "runToEntryPoint": "main",
      "preLaunchTask": "CMake: build (Debug)"
    }
  ]
}
```

## 18. VS Code 常用快捷键

| 快捷键 | 作用 |
| --- | --- |
| `Ctrl+Shift+P` | 命令面板 |
| `Ctrl+P` | 快速打开文件 |
| `Ctrl+Shift+X` | 扩展面板 |
| `Ctrl+Shift+B` | 运行默认构建任务 |
| `F5` | 开始/继续调试 |
| `F9` | 设置或取消断点 |
| `F10` | Step Over |
| `F11` | Step Into |
| `Shift+F11` | Step Out |
| `Ctrl+Shift+F5` | 重启调试 |
| `Shift+F5` | 停止调试 |

## 19. Git 初始化和推送

```powershell
git init -b main
git add .
git commit -m "docs: add STM32 VS Code development tutorial"
git branch -M main
git remote add origin https://github.com/<用户名>/<仓库名>.git
git push -u origin main
```

查看状态：

```powershell
git status
git log --oneline --decorate -5
```

## 20. 发布教程前检查

```text
[ ] README.md 在仓库根目录
[ ] 图片使用相对路径
[ ] 图片文件名是英文、小写、连字符
[ ] 没有提交 build/
[ ] 没有提交 .cache/
[ ] 没有提交个人用户名和绝对本机路径
[ ] 代码块使用正确语言标记
[ ] 每个章节有返回主页链接
[ ] 示例芯片和实际芯片差异已说明
```

## 21. 最短成功路径

```text
安装工具 -> 验证 PATH -> CubeMX 生成 CMake 工程
  -> 复制 .vscode/CMakePresets/openocd
  -> cmake --preset debug -> cmake --build --preset debug
  -> OpenOCD 连接 -> VS Code F5 -> 断点
```

[返回主页](../README.md)
