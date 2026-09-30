# 01 安装工具与配置 PATH

[返回主页](../README.md) | [下一章：新建 CubeMX 工程](./02-create-cubemx-project.md)

这一章只做一件事：让五个核心命令在 PowerShell 中都能正常运行。

```powershell
arm-none-eabi-gcc --version
cmake --version
ninja --version
openocd --version
code --version
```

只要其中任何一条显示“不是内部或外部命令”，就不要急着创建 STM32 工程，先回到本章修复 PATH。

## 1. 安装前准备

### 1.1 推荐系统

- Windows 10 64 位或 Windows 11 64 位。
- 至少 10 GB 可用磁盘空间。
- 能访问 ST、Arm、GitHub、VS Code Marketplace。
- 普通用户即可安装，安装到用户目录也可以。

### 1.2 路径规范

尽量使用：

```text
C:\Tools\arm-gnu-toolchain
C:\Tools\cmake
C:\Tools\ninja
C:\Tools\xpack-openocd
C:\STM32\STM32CubeMX
C:\STM32\Projects
```

尽量避开：

```text
C:\Users\张三\Desktop\单片机 工程\新建文件夹
C:\Program Files\我的工具\带空格 和 中文
OneDrive\同步目录\...
```

原因不是“中文一定不能用”，而是不同工具、脚本、GDB 配置和 CMake 对空格、中文路径、超长路径的处理并不完全一致。初学阶段减少变量，比事后猜路径更容易。

### 1.3 PowerShell 还是 CMD

本教程统一使用 PowerShell。VS Code 默认终端也可以设置为 PowerShell：

```json
{
  "terminal.integrated.defaultProfile.windows": "PowerShell"
}
```

命令中的路径如果包含空格，要用双引号：

```powershell
& "C:\Program Files\CMake\bin\cmake.exe" --version
```

## 2. 安装 VS Code

### 2.1 下载和安装

1. 打开 [Visual Studio Code](https://code.visualstudio.com/)。
2. 下载 Windows x64 User Installer。
3. 安装时建议勾选：
   - `Add to PATH`
   - `Open with Code`
   - `Register Code as an editor for supported file types`
4. 安装完成后重新打开 PowerShell。

验证：

```powershell
code --version
```

应看到类似：

```text
1.xx.x
<commit hash>
x64
```

### 2.2 安装扩展

在 VS Code 中按 `Ctrl+Shift+X` 打开扩展面板，搜索并安装：

| 扩展 | 扩展 ID | 用途 |
| --- | --- | --- |
| C/C++ | `ms-vscode.cpptools` | 代码提示、跳转、查看定义 |
| CMake | `twxs.cmake` | CMake 语法高亮 |
| CMake Tools | `ms-vscode.cmake-tools` | 配置、构建、选择 preset |
| Cortex-Debug | `marus25.cortex-debug` | OpenOCD/GDB 调试和嵌入式视图 |
| ARM Assembly | `dan-c-underwood.arm` | 启动文件和汇编语法高亮 |
| EditorConfig | `EditorConfig.EditorConfig` | 统一缩进和换行风格，可选 |

也可以使用命令行安装：

```powershell
code --install-extension ms-vscode.cpptools
code --install-extension twxs.cmake
code --install-extension ms-vscode.cmake-tools
code --install-extension marus25.cortex-debug
code --install-extension dan-c-underwood.arm
```

安装后执行：

```powershell
code --list-extensions
```

检查扩展 ID 是否出现。

### 2.3 VS Code 安装截图建议

如果要给教程补充真实截图，建议截取：

1. 扩展面板中同时看到 C/C++、CMake Tools 和 Cortex-Debug。
2. 打开一个 STM32 工程后的资源管理器。
3. 底部状态栏显示 `CMake: [Debug]`。
4. 调试侧栏显示变量、调用栈、断点和寄存器。

截取后建议把图片裁剪到只保留关键区域，不要包含用户名、公司路径、邮件通知或浏览器标签页。

## 3. 安装 STM32CubeMX

STM32CubeMX 用于选择芯片、配置引脚和时钟、生成初始化代码。

### 3.1 下载

打开 [STM32CubeMX 官方页面](https://www.st.com/en/development-tools/stm32cubemx.html)，下载 Windows 安装包。

ST 网站通常要求登录账号。安装程序会安装它自带的 Java 运行环境，通常不需要单独安装 Java。

### 3.2 安装

1. 运行安装程序。
2. 安装目录建议使用：

   ```text
   C:\STM32\STM32CubeMX
   ```

3. 安装完成后启动一次。
4. 首次启动可能需要下载 MCU 固件包。

### 3.3 安装目标芯片的固件包

在 CubeMX 主界面：

1. 打开 `Help` -> `Manage embedded software packages`。
2. 选择你的芯片系列，例如 `STM32F1`。
3. 安装对应固件包，例如 `STM32Cube MCU Package for STM32F1 Series`。
4. 等待下载完成。

只有安装过固件包，创建工程时才能选择对应的 HAL/CMSIS 版本。

### 3.4 检查 CubeMX 是否支持 CMake

不同版本的 CubeMX 界面文字可能略有差别。通常可以在：

```text
Project Manager
  -> Project
  -> Toolchain / IDE
```

看到：

```text
STM32CubeIDE
Makefile
CMake
MDK-ARM
EWARM
```

如果能看到 `CMake`，优先使用官方 CMake 生成器。

如果看不到 `CMake`，可以：

1. 使用 `Makefile` 生成工程，再参考 [05 CMake 模板详解](./05-cmake-template.md) 添加手工 CMake。
2. 升级到支持 CMake 的 CubeMX 版本。
3. 改用 STM32CubeCLT，见本章最后的备选方案。

## 4. 安装 ARM GNU Toolchain

这里安装的是 `arm-none-eabi-gcc`，它是面向裸机 ARM 芯片的交叉编译器。

### 4.1 下载

打开 [Arm GNU Toolchain Downloads](https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads)，找到 Windows 版本：

```text
arm-gnu-toolchain-<版本>-mingw-w64-i686-arm-none-eabi.exe
```

不要下载 `aarch64-none-elf`，也不要下载 Linux 或 macOS 版本。

### 4.2 安装

1. 运行安装程序。
2. 建议安装到：

   ```text
   C:\Tools\arm-gnu-toolchain
   ```

3. 安装向导询问是否加入 PATH 时，优先选择加入 PATH。
4. 如果没有加入 PATH，安装后手动添加。

### 4.3 找到 bin 目录

ARM GNU Toolchain 的可执行文件通常位于：

```text
<安装目录>\bin
```

例如：

```text
C:\Tools\arm-gnu-toolchain\bin
```

该目录中应包含：

```text
arm-none-eabi-gcc.exe
arm-none-eabi-g++.exe
arm-none-eabi-gdb.exe
arm-none-eabi-objcopy.exe
arm-none-eabi-size.exe
```

### 4.4 验证

关闭所有 PowerShell，重新打开一个：

```powershell
arm-none-eabi-gcc --version
```

应看到类似：

```text
arm-none-eabi-gcc.exe (Arm GNU Toolchain ...)
Copyright (C) ...
```

如果命令找不到，先看下一节的 PATH 配置。

## 5. 安装 CMake

CMake 负责生成构建系统，Ninja 负责执行构建。

### 5.1 下载

打开 [CMake Download](https://cmake.org/download/)，选择 Windows x64 Installer。

### 5.2 安装

1. 运行安装程序。
2. 选择 `Add CMake to the system PATH for all users` 或当前用户 PATH。
3. 建议安装目录：

   ```text
   C:\Tools\cmake
   ```

4. 安装完成后重新打开 PowerShell。

验证：

```powershell
cmake --version
```

应看到：

```text
cmake version 3.21+
```

本项目模板要求 CMake 最低版本为 `3.21`。更新的版本通常也可以。

## 6. 安装 Ninja

Ninja 是一个小型构建执行器，通常比传统 Make 快，并且与 CMake 配合稳定。

### 6.1 方式一：官方 Release

1. 打开 [Ninja Releases](https://github.com/ninja-build/ninja/releases)。
2. 下载 `ninja-win.zip`。
3. 解压到：

   ```text
   C:\Tools\ninja
   ```

4. 确保目录中直接存在：

   ```text
   C:\Tools\ninja\ninja.exe
   ```

### 6.2 方式二：winget

```powershell
winget install --id Ninja-build.Ninja
```

安装后重新打开 PowerShell。

### 6.3 验证

```powershell
ninja --version
```

应显示类似：

```text
1.11.1
```

版本号不必完全一致，但必须能正常输出。

## 7. 安装 OpenOCD

OpenOCD 负责把 GDB 的调试命令转换成 ST-Link 能识别的 SWD/JTAG 操作。

### 7.1 推荐：xPack OpenOCD

1. 打开 [xPack OpenOCD Releases](https://github.com/xpack-dev-tools/openocd-xpack/releases)。
2. 下载类似：

   ```text
   xpack-openocd-<版本>-win32-x64.zip
   ```

3. 解压到：

   ```text
   C:\Tools\xpack-openocd
   ```

4. 目录中通常会看到：

   ```text
   C:\Tools\xpack-openocd\bin\openocd.exe
   C:\Tools\xpack-openocd\openocd\scripts\
   ```

5. 把 `C:\Tools\xpack-openocd\bin` 加入 PATH。

### 7.2 找到 scripts 目录

OpenOCD 的芯片和接口配置都在 `scripts` 目录下。xPack 版本通常是：

```text
C:\Tools\xpack-openocd\openocd\scripts
```

其中至少应有：

```text
interface\stlink.cfg
target\stm32f1x.cfg
target\stm32f4x.cfg
target\stm32g0x.cfg
```

在 VS Code 的 `launch.json` 中，经常需要把这个 scripts 目录填入 `searchDir`。

### 7.3 验证

```powershell
openocd --version
```

应显示类似：

```text
xPack Open On-Chip Debugger 0.12.0...
Licensed under GNU GPL v2
```

如果显示 `openocd` 不是命令，检查 `bin` 是否加入 PATH。

## 8. 安装 ST-Link USB 驱动

### 8.1 下载驱动

打开 [STSW-LINK009](https://www.st.com/en/development-tools/stsw-link009.html)，下载并安装 ST-Link USB 驱动。

### 8.2 连接 ST-Link

1. 把 ST-Link 插入电脑 USB。
2. 打开设备管理器。
3. 检查是否能看到 `STMicroelectronics STLink`、`STM32 STLink` 或类似设备。
4. 如果设备带黄色感叹号，重新安装驱动。

### 8.3 常见兼容版问题

部分低价 ST-Link V2 兼容版使用旧固件。如果 OpenOCD 能显示设备但无法连接，先查看第三部分常见问题：

```text
openocd -f interface/stlink.cfg -f target/stm32f1x.cfg
```

常见错误：

```text
Error: open failed
Error: No STM32 target found
Error: target voltage may be too low
```

这可能是驱动、接线、供电或 ST-Link 固件问题，不一定是教程配置错误。

## 9. 把工具加入 PATH

### 9.1 图形界面方式

1. 按 `Win`，搜索“编辑系统环境变量”。
2. 打开 `环境变量`。
3. 在“用户变量”或“系统变量”中找到 `Path`。
4. 编辑 `Path`，添加以下目录：

   ```text
   C:\Tools\arm-gnu-toolchain\bin
   C:\Tools\cmake\bin
   C:\Tools\ninja
   C:\Tools\xpack-openocd\bin
   ```

5. 连续点击确定。
6. 重要：关闭所有已经打开的 PowerShell、CMD 和 VS Code，再重新打开。

### 9.2 PowerShell 临时方式

只对当前窗口有效，适合测试：

```powershell
$env:Path += ";C:\Tools\arm-gnu-toolchain\bin"
$env:Path += ";C:\Tools\cmake\bin"
$env:Path += ";C:\Tools\ninja"
$env:Path += ";C:\Tools\xpack-openocd\bin"
```

临时 PATH 不会影响系统，重启终端后失效。

### 9.3 检查命令实际来自哪里

在 PowerShell 中运行：

```powershell
where.exe arm-none-eabi-gcc
where.exe cmake
where.exe ninja
where.exe openocd
where.exe code
```

输出第一条通常是当前实际使用的程序。如果出现多个版本，要确认第一条是不是你刚安装的版本。

## 10. 一次性环境检查

重新打开 PowerShell，复制以下命令：

```powershell
$ErrorActionPreference = "Continue"

Write-Host "`n[ARM GCC]" -ForegroundColor Cyan
arm-none-eabi-gcc --version

Write-Host "`n[CMake]" -ForegroundColor Cyan
cmake --version

Write-Host "`n[Ninja]" -ForegroundColor Cyan
ninja --version

Write-Host "`n[OpenOCD]" -ForegroundColor Cyan
openocd --version

Write-Host "`n[VS Code]" -ForegroundColor Cyan
code --version
```

所有命令都应能输出版本。若某一项失败，先只修复那一项，不要继续创建工程。

## 11. 备选方案：STM32CubeCLT

ST 还提供 STM32CubeCLT，它通常包含：

- GNU ARM 工具链
- CMake
- Ninja
- OpenOCD
- ST-Link GDB Server
- 其他命令行工具

如果不想分别安装多个组件，可以从 ST 官方页面搜索 `STM32CubeCLT`。安装后通常需要把：

```text
<STM32CubeCLT>\GNU-tools-for-STM32\bin
<STM32CubeCLT>\CMake\bin
<STM32CubeCLT>\Ninja\bin
<STM32CubeCLT>\OpenOCD\bin
```

加入 PATH。

注意：STM32CubeCLT 的实际目录结构会因版本而异，安装后请用 `where.exe` 确认真实路径，不要盲目复制目录。

## 12. 本章完成标准

满足以下全部条件后再进入下一章：

- [ ] `arm-none-eabi-gcc --version` 正常。
- [ ] `cmake --version` 正常。
- [ ] `ninja --version` 正常。
- [ ] `openocd --version` 正常。
- [ ] `code --version` 正常。
- [ ] 能找到 OpenOCD 的 `scripts` 目录。
- [ ] VS Code 已安装 C/C++、CMake Tools、Cortex-Debug。
- [ ] ST-Link 插入后设备管理器没有黄色感叹号。

下一章：[02 使用 STM32CubeMX 新建工程](./02-create-cubemx-project.md)
