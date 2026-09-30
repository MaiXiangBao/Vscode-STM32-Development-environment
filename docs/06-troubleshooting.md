# 06 故障排查

[上一章：CMake 模板详解](./05-cmake-template.md) | [返回主页](../README.md) | [下一章：命令速查表](./07-cheatsheet.md)

排错的核心不是“把网上所有配置都试一遍”，而是确认错误发生在哪一层。

## 1. 先做五层判断

```text
第 1 层：命令是否存在
第 2 层：CMake 是否能配置
第 3 层：GCC 是否能编译和链接
第 4 层：OpenOCD 是否能连接
第 5 层：程序运行时逻辑是否正确
```

每一层都有独立的验证命令。

## 2. 命令层：PowerShell 找不到工具

### 2.1 现象

```text
arm-none-eabi-gcc : 无法将“arm-none-eabi-gcc”项识别为 cmdlet...
cmake : 无法将“cmake”项识别为 cmdlet...
ninja : ...
openocd : ...
```

### 2.2 检查

```powershell
where.exe arm-none-eabi-gcc
where.exe cmake
where.exe ninja
where.exe openocd
where.exe code
```

### 2.3 原因和修复

| 原因 | 修复 |
| --- | --- |
| 安装目录没有加入 PATH | 把对应 `bin` 加入 PATH |
| 修改 PATH 后没有重启终端 | 关闭所有终端和 VS Code，重新打开 |
| 多个版本冲突 | 用 `where.exe` 确认第一条路径 |
| 只在当前 PowerShell 临时设置 | 把临时 `$env:Path += ...` 写入用户环境变量 |
| 使用 CMD 设置的旧 PATH | 以实际安装目录为准重新设置 |

验证：

```powershell
$env:Path -split ";" | Select-String -Pattern "arm|cmake|ninja|openocd" -CaseSensitive:$false
```

## 3. CMake 配置失败

### 3.1 Ninja 找不到

错误示例：

```text
CMake Error: CMake was unable to find a build program corresponding to "Ninja".
CMAKE_MAKE_PROGRAM is not set.
```

检查：

```powershell
ninja --version
where.exe ninja
```

解决：

1. 确认 `ninja.exe` 所在目录已在 PATH。
2. 关闭 CMake Tools 后重新打开 VS Code。
3. 如果使用 CMake GUI，清空 CMake 缓存后重新配置。

### 3.2 编译器找不到

错误示例：

```text
No CMAKE_C_COMPILER could be found.
```

或：

```text
The C compiler identification is unknown
```

检查：

```powershell
arm-none-eabi-gcc --version
where.exe arm-none-eabi-gcc
```

如果命令正常，但 CMake 仍找不到，检查工具链文件中的：

```cmake
find_program(CMAKE_C_COMPILER ${TOOLCHAIN_PREFIX}gcc REQUIRED)
```

以及 `TOOLCHAIN_PREFIX` 是否为：

```cmake
set(TOOLCHAIN_PREFIX arm-none-eabi-)
```

### 3.3 CMake 能配置，但配置到了旧版本

现象：

```text
修改了 CMakeLists.txt，但构建行为没有变化
```

检查：

```powershell
Get-Content .\build\Debug\CMakeCache.txt |
  Select-String "CMAKE_C_COMPILER|CMAKE_TOOLCHAIN_FILE|CMAKE_GENERATOR"
```

如果路径或生成器不对：

```powershell
Remove-Item .\build\Debug -Recurse -Force
cmake --preset debug
```

## 4. GCC 编译或链接失败

### 4.1 头文件找不到

错误：

```text
fatal error: stm32f1xx_hal.h: No such file or directory
```

检查实际文件：

```powershell
Get-ChildItem .\Drivers -Recurse -Filter stm32f1xx_hal.h
```

如果文件存在，检查 `CMakeLists.txt` 的：

```cmake
target_include_directories(...)
```

常见错误是把 F103 的 include 路径复制到了 F4 工程，或者路径中多了一层/少了一层目录。

### 4.2 undefined reference

错误：

```text
undefined reference to `HAL_GPIO_TogglePin'
undefined reference to `SystemInit'
undefined reference to `_exit'
```

分别处理：

| 符号 | 可能原因 |
| --- | --- |
| `HAL_xxx` | HAL 源文件没有加入构建，或 `USE_HAL_DRIVER` 漏了 |
| `SystemInit` | `system_stm32xxxx.c` 没有加入源文件 |
| `_exit`、`_sbrk`、`_write` | 缺少 `nosys.specs` 或系统调用实现 |
| `main` | 启动文件、链接脚本或源文件没有正确加入 |

检查源文件是否参与构建：

```powershell
Get-ChildItem .\build\Debug -Recurse -Filter *.ninja |
  Select-String "HAL_GPIO|system_stm32|main.c"
```

### 4.3 未定义的 startup 符号

错误：

```text
undefined reference to `Reset_Handler'
```

通常说明启动文件没有加入构建，或者启动文件被当成普通文本忽略。

检查：

```powershell
Get-ChildItem . -Filter "startup_*.s"
```

然后确认 `CMakeLists.txt` 中：

```cmake
set(STARTUP_SOURCE ...)
```

和 `add_executable(... ${STARTUP_SOURCE})` 都存在。

### 4.4 region overflow

错误：

```text
region `FLASH' overflowed by 1234 bytes
region `RAM' overflowed by 256 bytes
```

原因：

1. 链接脚本选错，Flash/RAM 大小不匹配。
2. 编入了不该编入的 HAL 文件。
3. 全局数组太大。
4. 栈和堆设置过大。
5. 使用了浮点格式输出，nano/newlib 体积增加。

先用 size 和 map 查看：

```powershell
arm-none-eabi-size .\build\Debug\*.elf
Get-Content .\build\Debug\*.map | Select-String "Memory Configuration" -Context 0,12
```

### 4.5 编译警告很多

`-Wall -Wextra` 会暴露很多 HAL 代码中的警告。初学阶段：

1. 先确认没有 `error`。
2. 把自己业务代码中的警告当作问题处理。
3. 不要把 HAL 警告全部通过关闭警告掩盖。

## 5. OpenOCD 连接失败

### 5.1 找不到 interfaces/targets 脚本

错误：

```text
Error: open failed
Error: Could not find interface/stlink.cfg
Error: could not find target/stm32f1x.cfg
```

先找脚本：

```powershell
Get-ChildItem -Recurse C:\Tools -Filter stlink.cfg -ErrorAction SilentlyContinue
Get-ChildItem -Recurse C:\Tools -Filter stm32f1x.cfg -ErrorAction SilentlyContinue
```

然后运行时加上：

```powershell
-s "C:\Tools\xpack-openocd\openocd\scripts"
```

### 5.2 找不到 ST-Link

错误：

```text
Error: open failed
Error: No ST-Link found
```

检查：

1. USB 是否插好。
2. 设备管理器是否出现 ST-Link。
3. 是否安装了 ST-Link USB 驱动。
4. 是否被其他进程占用。

在 PowerShell 中查找 ST-Link 相关 USB 设备：

```powershell
Get-PnpDevice | Where-Object {
  $_.FriendlyName -match "ST-?Link|STM32"
} | Select-Object Status,Class,FriendlyName,InstanceId
```

如果设备有黄色感叹号，先修驱动。

### 5.3 target voltage may be too low

错误：

```text
Error: target voltage may be too low
```

原因：

1. 没有把 ST-Link 的 3.3V 接到目标板。
2. GND 没有共地。
3. 目标板被错误地接了 5V。
4. 目标板电源不稳定。
5. SWDIO/SWCLK 接错。

先用万用表确认目标板 `3V3` 对 `GND` 约为 3.3 V。

### 5.4 no target found

错误：

```text
Error: No STM32 target found
```

检查：

| 检查项 | 正确状态 |
| --- | --- |
| SWDIO | PA13 |
| SWCLK | PA14 |
| GND | 共地 |
| 3.3V | 目标板上电 |
| BOOT0 | 正常运行通常为 0 |
| 复位 | 尝试连接 NRST |
| 芯片型号 | OpenOCD target 文件匹配 |
| 接口 | `transport select swd` |

可以手动降低速度：

```tcl
adapter speed 500
```

或者：

```tcl
adapter speed 100
```

下降速度不能修复接线错误，但能帮助排除长杜邦线或干扰问题。

### 5.5 ST-Link 被其他程序占用

如果 STM32CubeProgrammer、STM32CubeIDE、另一个 OpenOCD 或 J-Link 进程正在使用同一个调试器：

```text
Error: open failed
Error: device busy
```

关闭占用它的程序，或者换一个 ST-Link。不要同时启动两个 OpenOCD server。

## 6. VS Code 调试失败

### 6.1 找不到 executable

错误：

```text
Cannot find executable ...
```

检查：

```powershell
Get-ChildItem .\build -Recurse -Filter *.elf
```

然后把 `launch.json` 中的路径改成实际路径。常见问题是：

- 工程名不是模板里的名字。
- Debug 构建输出到了 `build/Debug` 之外。
- CubeMX 生成器改变了 target 名称。
- 实际用的是 Release，却指向 Debug 文件。

### 6.2 Cortex-Debug 找不到 GDB

错误：

```text
Unable to find arm-none-eabi-gdb
```

检查：

```powershell
where.exe arm-none-eabi-gdb
arm-none-eabi-gdb --version
```

如果只有 GCC 没有 GDB，重新安装 ARM GNU Toolchain，或在 `launch.json` 中显式设置 GDB 路径。

### 6.3 OpenOCD 能运行，但 VS Code 启动失败

先检查本地配置文件：

```powershell
Test-Path .\openocd\stm32f1-stlink.cfg
Get-Content .\openocd\stm32f1-stlink.cfg
```

再检查：

```json
"searchDir": [
  "C:/Tools/xpack-openocd/openocd/scripts"
]
```

最后打开：

```text
View -> Output -> Cortex-Debug
```

以及：

```text
Debug Console
```

查看完整输出，不要只看 VS Code 弹出的一行提示。

### 6.4 断点不触发

原因可能是：

1. 程序没有下载成功。
2. ELF 和当前 Flash 不一致。
3. 代码被优化掉，断点地址不存在。
4. 程序没有运行到该行。
5. 目标一直在复位。
6. 链接脚本地址错误。

处理：

1. 在 `main()` 第一行打断点。
2. 使用 Fresh Build 重新生成 ELF。
3. 先暂停 CPU，查看 `PC`。
4. 用 `HAL_GetTick()` 或 GPIO 翻转确认程序是否真的运行。
5. 检查启动文件和链接脚本。

## 7. 程序能烧录但运行异常

### 7.1 LED 不亮

检查：

```c
HAL_GPIO_TogglePin(USER_LED_GPIO_Port, USER_LED_Pin);
HAL_Delay(500);
```

确认：

- `PC13` 已配置为输出。
- LED 是低电平点亮还是高电平点亮。
- 时钟树有效，程序没有停在 HardFault。
- `HAL_Delay()` 依赖 SysTick，时钟配置错误时会失效或延时异常。

### 7.2 一上电就 HardFault

可能原因：

1. 向量表或启动文件错误。
2. 链接脚本地址错误。
3. 没有正确初始化系统时钟。
4. 访问了未使能时钟的外设。
5. 空指针或数组越界。
6. 堆栈溢出。

在调试器中暂停后：

```gdb
bt
info registers
x/16wx $sp
```

查看 `LR`、`SP` 和调用栈。

### 7.3 串口或 printf 没输出

常见原因：

1. 没有配置 UART。
2. 波特率不匹配。
3. TX/RX 接反。
4. 没有实现 `_write()` 或 `syscalls.c`。
5. 使用了 `--specs=nosys.specs`，但没有重定向输出。
6. 没有启用 `printf` 浮点支持，却打印了浮点数。

不要一开始就要求 `printf` 能打印浮点。先让最简单的字符输出跑通，再增加格式化功能。

## 8. 路径、编码和文件名问题

### 8.1 中文路径

有些工具能处理中文路径，但某些脚本、GDB、Make、OpenOCD 组合可能失败。最稳妥的方案：

```text
C:\STM32\Projects\stm32f103c8t6-blink
```

不要使用：

```text
桌面\新建 文件夹\张三的单片机工程
```

### 8.2 空格路径

命令行中带空格的路径要加引号：

```powershell
& "C:\Program Files\CMake\bin\cmake.exe" --version
```

CMake 的 JSON 配置建议使用：

```json
"path": "C:/Program Files/CMake/bin/cmake.exe"
```

### 8.3 OneDrive 同步

构建目录包含大量小文件，OneDrive 同步可能导致：

- 文件被锁定。
- 构建时间变长。
- 文件状态异常。
- 调试时 ELF 被同步进程占用。

建议把 STM32 工程放在：

```text
C:\STM32\Projects
```

而不是放在 OneDrive 下。

## 9. CubeMX 重新生成后代码丢失

### 9.1 原因

代码写在了 `USER CODE BEGIN/END` 之外，或者修改了 CubeMX 生成区域。

### 9.2 预防

1. 只改用户代码区。
2. 重新生成前先提交 Git。
3. 重新生成后立即查看 diff。
4. 自己新增的文件放在 `User/`，不要放 `Drivers/`。

### 9.3 恢复

如果代码被覆盖：

```powershell
git diff
git restore --source=HEAD -- Core/Src/main.c
```

但 `git restore` 会覆盖当前文件，只在你明确知道要回到上一个提交时使用。更安全的做法是先复制当前文件，再对比：

```powershell
Copy-Item .\Core\Src\main.c .\Core\Src\main.c.backup
git diff -- .\Core\Src\main.c
```

## 10. OpenOCD 脚本针对不同芯片

### STM32F1

```tcl
source [find interface/stlink.cfg]
transport select swd
source [find target/stm32f1x.cfg]
```

### STM32F4

```tcl
source [find interface/stlink.cfg]
transport select swd
source [find target/stm32f4x.cfg]
```

### STM32G0

```tcl
source [find interface/stlink.cfg]
transport select swd
source [find target/stm32g0x.cfg]
```

### STM32H7

```tcl
source [find interface/stlink.cfg]
transport select swd
source [find target/stm32h7x.cfg]
```

如果 target 文件名不完全相同，直接在 OpenOCD scripts 目录里搜索：

```powershell
Get-ChildItem C:\Tools\xpack-openocd\openocd\scripts\target -Filter "stm32*.cfg" |
  Select-Object Name
```

## 11. 一张最小排查命令表

```powershell
# 工具版本
arm-none-eabi-gcc --version
cmake --version
ninja --version
openocd --version

# 路径
where.exe arm-none-eabi-gcc
where.exe cmake
where.exe ninja
where.exe openocd

# CMake
cmake --list-presets
cmake --preset debug
cmake --build --preset debug

# ELF
Get-ChildItem .\build -Recurse -Filter *.elf
arm-none-eabi-size .\build\Debug\*.elf

# OpenOCD
openocd -s "C:\Tools\xpack-openocd\openocd\scripts" `
  -f "openocd\stm32f1-stlink.cfg" `
  -c "init; targets; shutdown"

# 搜索配置
Get-ChildItem -Recurse C:\Tools -Filter stm32f1x.cfg
```

## 12. 如果仍然无法解决

准备提交给同学或老师的信息：

1. 开发板型号和芯片型号。
2. ST-Link 型号。
3. 操作系统和工具版本。
4. 失败命令的完整文本。
5. `CMakeCache.txt` 中的编译器和工具链路径。
6. `launch.json` 和 `tasks.json`。
7. OpenOCD 完整输出。
8. 接线照片。
9. CubeMX 生成的 `.ioc` 文件。

不要只发一句“VSCode 不能用”。把错误缩小到一个可复现的命令，别人才能快速帮你。

下一章：[07 命令速查表](./07-cheatsheet.md)
