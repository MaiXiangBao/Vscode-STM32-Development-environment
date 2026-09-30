# 用 Codex 快速部署 STM32 环境

[返回首页](./README.md)

这份说明写给第一次接触 STM32 的同学。目标只有一个：

```text
只手动安装 VS Code 和 STM32CubeMX，
其余工具让 Codex 自动安装。
```

## 1. 你要准备什么

### 必须自己安装

1. [Visual Studio Code](https://code.visualstudio.com/)
2. [STM32CubeMX](https://www.st.com/en/development-tools/stm32cubemx.html)

### Codex 会自动安装

Codex 使用 Windows 自带的 `winget` 安装：

| 工具 | winget ID |
| --- | --- |
| Arm GNU Toolchain | `Arm.ArmGnuToolchain` |
| CMake | `Kitware.CMake` |
| Ninja | `Ninja-build.Ninja` |
| OpenOCD xPack | `xpack-dev-tools.openocd-xpack` |

这样不用到处找下载页面。

## 2. 最简单的使用方式

### 第一步：在 Codex 打开本项目

仓库地址：

```text
https://github.com/MaiXiangBao/Vscode-STM32-Development-environment
```

### 第二步：复制这句话给 Codex

```text
请你读取 CODEX-DEPLOY-PROMPT.txt，并严格按照里面的步骤帮我部署 STM32 环境。
```

### 第三步：让 Codex 自己执行

Codex 会：

1. 检查 VS Code 和 STM32CubeMX。
2. 使用 `winget` 安装 Arm GNU Toolchain。
3. 使用 `winget` 安装 CMake。
4. 使用 `winget` 安装 Ninja。
5. 使用 `winget` 安装 OpenOCD。
6. 安装 VS Code 扩展。
7. 运行版本检查。

如果 Codex 需要你手动安装 STM32CubeMX，它会明确告诉你。

## 3. VS Code 需要安装的插件

只安装 VS Code 本体还不够。必须安装：

| 插件 | 扩展 ID |
| --- | --- |
| C/C++ | `ms-vscode.cpptools` |
| CMake | `twxs.cmake` |
| CMake Tools | `ms-vscode.cmake-tools` |
| Cortex-Debug | `marus25.cortex-debug` |

建议再安装：

| 插件 | 扩展 ID |
| --- | --- |
| ARM Assembly | `dan-c-underwood.arm` |

手动安装方法：

1. 在 VS Code 按 `Ctrl+Shift+X`。
2. 搜索扩展 ID。
3. 点击 `Install`。

自动安装方法：

```powershell
code --install-extension ms-vscode.cpptools
code --install-extension twxs.cmake
code --install-extension ms-vscode.cmake-tools
code --install-extension marus25.cortex-debug
code --install-extension dan-c-underwood.arm
```

## 4. 不想使用 Codex 时

打开 PowerShell，进入本项目目录：

```powershell
cd C:\path\to\VScode-STM32-
```

运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install-stm32-tools.ps1
```

安装完成后检查：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\check-stm32-tools.ps1
```

## 5. 脚本会做什么

`install-stm32-tools.ps1` 会：

| 操作 | 说明 |
| --- | --- |
| 检查 winget | 确认 Windows 包管理器可用 |
| 安装工具 | 使用官方 winget ID |
| 跳过已安装项 | 已经有的工具不会重复安装 |
| 安装扩展 | 如果 VS Code 的 `code` 命令可用 |
| 检查版本 | 运行 GCC、CMake、Ninja、OpenOCD 版本 |

它不会：

- 打包或上传你的本地工具链。
- 修改 STM32CubeMX 安装文件。
- 删除你的工程。
- 自动烧录开发板。

## 6. 检查成功的方法

如果看到下面这些版本信息，就说明工具装好了：

```text
arm-none-eabi-gcc
cmake version 3.x 或更新
ninja 1.x
Open On-Chip Debugger 0.x
```

版本号不要求完全一致。

## 7. 如果 winget 找不到

对 Codex 说：

```text
我的电脑没有 winget。请改用 Arm、CMake、Ninja 和 OpenOCD 官方下载页面，一步一步带我从网页下载并安装。每一步都告诉我完成后应该看到什么。
```

## 8. 接下来做什么

工具装好后，打开：

```text
BEGINNER-GUIDE.md
```

这是给 12 岁也能看懂的新手教程。它会用图片解释：

- 每个工具是干什么的。
- 它们怎样一起工作。
- 怎样用 CubeMX 点击出一个工程。
- 怎样用 VS Code 编译。
- 怎样接四根线。
- 怎样按 `F5` 让程序停在断点。

## 9. 如果失败

把 Codex 或 PowerShell 里的完整错误复制给 Codex，然后说：

```text
请用最简单的语言解释这个错误，并帮我修好。不要让我同时改很多地方。
```

更详细的错误说明见 [06 故障排查](./docs/06-troubleshooting.md)。
