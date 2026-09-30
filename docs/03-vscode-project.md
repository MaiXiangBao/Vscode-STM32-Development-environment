# 03 配置 VS Code 工程

[上一章：新建 CubeMX 工程](./02-create-cubemx-project.md) | [返回主页](../README.md) | [下一章：构建、烧录与调试](./04-build-flash-debug.md)

这一章把 CubeMX 生成的代码接入 VS Code：

- 识别头文件和宏定义。
- 使用 CMake Presets 配置和构建。
- 用任务执行常用命令。
- 用 Cortex-Debug 启动 OpenOCD。

## 1. 用 VS Code 打开正确的目录

在 PowerShell 中：

```powershell
code C:\STM32\Projects\stm32f103c8t6-blink
```

或者：

1. 打开 VS Code。
2. 选择 `File` -> `Open Folder`。
3. 选择包含 `.ioc`、`Core/`、`Drivers/` 和 `CMakeLists.txt` 的工程根目录。

不要只打开 `Core/Src/main.c`。C/C++ 扩展、CMake Tools 和 Cortex-Debug 都需要完整的 workspace。

首次打开时，VS Code 可能提示：

```text
Do you trust the authors of the files in this folder?
```

确认这是你的工程后选择信任。工作区不受信任时，部分扩展功能会被限制。

## 2. 安装工作区推荐扩展

工程根目录中创建：

```text
.vscode/extensions.json
```

内容参考：

```json
{
  "recommendations": [
    "ms-vscode.cpptools",
    "twxs.cmake",
    "ms-vscode.cmake-tools",
    "marus25.cortex-debug",
    "dan-c-underwood.arm",
    "EditorConfig.EditorConfig"
  ]
}
```

下一次打开工程时，VS Code 会提示安装推荐扩展。

## 3. 复制本仓库模板

假设本教程仓库位于：

```text
C:\Users\<用户名>\Desktop\Vscode-STM32-Development-environment
```

在工程根目录运行：

```powershell
$Tutorial = "C:\Users\<用户名>\Desktop\Vscode-STM32-Development-environment"
$Project = "C:\STM32\Projects\stm32f103c8t6-blink"

Copy-Item "$Tutorial\templates\.vscode" "$Project\.vscode" -Recurse -Force
Copy-Item "$Tutorial\templates\CMakePresets.json" "$Project\CMakePresets.json" -Force
Copy-Item "$Tutorial\templates\cmake\gcc-arm-none-eabi.cmake" "$Project\cmake\gcc-arm-none-eabi.cmake" -Force
Copy-Item "$Tutorial\templates\openocd" "$Project\openocd" -Recurse -Force
```

如果你的 CubeMX 已经生成了 `cmake/gcc-arm-none-eabi.cmake`：

1. 先备份原文件。
2. 对比 CPU、工具链前缀和编译选项。
3. 不要直接覆盖 CubeMX 更新过的内容。

如果你使用 Makefile 生成器并采用手工 CMake，复制：

```powershell
Copy-Item "$Tutorial\templates\CMakeLists.txt" "$Project\CMakeLists.txt" -Force
```

复制完成后，用 VS Code 的搜索功能全局替换占位符：

| 搜索 | 替换 |
| --- | --- |
| `<工程名>` | `stm32f103c8t6-blink` |
| `<OpenOCD scripts 目录>` | `C:/Tools/xpack-openocd/openocd/scripts` |
| `<ARM GNU Toolchain 目录>` | `C:/Tools/arm-gnu-toolchain` |

路径统一使用 `/` 或双反斜杠 `\\`。JSON 中不能直接写单个反斜杠，例如：

```json
"path": "C:/Tools/ninja/ninja.exe"
```

## 4. 配置 C/C++ IntelliSense

打开：

```text
.vscode/settings.json
```

推荐配置：

```json
{
  "cmake.useCMakePresets": "always",
  "cmake.configureOnOpen": false,
  "cmake.buildDirectory": "${workspaceFolder}/build/${buildType}",
  "C_Cpp.default.configurationProvider": "ms-vscode.cmake-tools",
  "C_Cpp.default.compileCommands": "${workspaceFolder}/build/Debug/compile_commands.json",
  "C_Cpp.default.cStandard": "c11",
  "C_Cpp.default.intelliSenseMode": "gcc-arm",
  "files.associations": {
    "*.ld": "c",
    "*.s": "asm",
    "*.S": "asm"
  },
  "terminal.integrated.defaultProfile.windows": "PowerShell"
}
```

关键说明：

| 设置 | 作用 |
| --- | --- |
| `cmake.useCMakePresets` | 强制使用 `CMakePresets.json`，避免 GUI 缓存和命令行不一致 |
| `cmake.configureOnOpen` | 打开工程时不自动配置，减少意外错误 |
| `C_Cpp.default.configurationProvider` | 让 CMake Tools 提供头文件和宏定义 |
| `C_Cpp.default.compileCommands` | 让 C/C++ 扩展读取真实编译命令 |
| `files.associations` | 让链接脚本和汇编文件更容易阅读 |

如果 `.c` 文件仍然有大量红色波浪线，但 `cmake --build --preset debug` 能构建成功，通常是 IntelliSense 配置问题，不是编译器问题。打开命令面板：

```text
C/C++: Select a Configuration...
```

选择 CMake Tools 提供的配置。

也可以删除缓存并重开：

```powershell
Remove-Item .\.cache -Recurse -Force -ErrorAction SilentlyContinue
```

## 5. 配置 CMake Presets

工程根目录中的：

```text
CMakePresets.json
```

示例：

```json
{
  "version": 3,
  "cmakeMinimumRequired": {
    "major": 3,
    "minor": 21,
    "patch": 0
  },
  "configurePresets": [
    {
      "name": "debug",
      "displayName": "Debug",
      "generator": "Ninja",
      "binaryDir": "${sourceDir}/build/Debug",
      "cacheVariables": {
        "CMAKE_BUILD_TYPE": "Debug",
        "CMAKE_TOOLCHAIN_FILE": "${sourceDir}/cmake/gcc-arm-none-eabi.cmake",
        "CMAKE_EXPORT_COMPILE_COMMANDS": true
      }
    },
    {
      "name": "release",
      "displayName": "Release",
      "generator": "Ninja",
      "binaryDir": "${sourceDir}/build/Release",
      "cacheVariables": {
        "CMAKE_BUILD_TYPE": "Release",
        "CMAKE_TOOLCHAIN_FILE": "${sourceDir}/cmake/gcc-arm-none-eabi.cmake",
        "CMAKE_EXPORT_COMPILE_COMMANDS": true
      }
    }
  ],
  "buildPresets": [
    {
      "name": "debug",
      "configurePreset": "debug"
    },
    {
      "name": "release",
      "configurePreset": "release"
    }
  ]
}
```

命令行验证：

```powershell
cmake --list-presets
cmake --preset debug
cmake --build --preset debug
```

如果 CMake Tools 状态栏看不到 `Debug`，先检查 JSON 是否有语法错误。VS Code 的“问题”面板会显示 JSON 解析错误。

## 6. 配置常用任务

任务文件：

```text
.vscode/tasks.json
```

示例：

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "CMake: configure (Debug)",
      "type": "shell",
      "command": "cmake",
      "args": [
        "--preset",
        "debug"
      ],
      "options": {
        "cwd": "${workspaceFolder}"
      },
      "problemMatcher": []
    },
    {
      "label": "CMake: build (Debug)",
      "type": "shell",
      "command": "cmake",
      "args": [
        "--build",
        "--preset",
        "debug"
      ],
      "options": {
        "cwd": "${workspaceFolder}"
      },
      "problemMatcher": [
        "$gcc"
      ]
    },
    {
      "label": "CMake: rebuild (Debug)",
      "type": "shell",
      "command": "cmake",
      "args": [
        "--build",
        "--preset",
        "debug",
        "--clean-first"
      ],
      "options": {
        "cwd": "${workspaceFolder}"
      },
      "problemMatcher": [
        "$gcc"
      ]
    },
    {
      "label": "OpenOCD: flash",
      "type": "shell",
      "command": "openocd",
      "args": [
        "-f",
        "openocd/stm32f1-stlink.cfg",
        "-c",
        "program build/Debug/<工程名>.elf verify reset exit"
      ],
      "options": {
        "cwd": "${workspaceFolder}"
      },
      "dependsOn": [
        "CMake: build (Debug)"
      ],
      "problemMatcher": []
    },
    {
      "label": "OpenOCD: server",
      "type": "shell",
      "command": "openocd",
      "args": [
        "-f",
        "openocd/stm32f1-stlink.cfg"
      ],
      "options": {
        "cwd": "${workspaceFolder}"
      },
      "isBackground": true,
      "problemMatcher": []
    }
  ]
}
```

打开命令面板：

```text
Tasks: Run Task
```

选择 `CMake: configure (Debug)`，再选择 `CMake: build (Debug)`。

## 7. 重要：程序名必须和 ELF 一致

如果工程叫 `stm32f103c8t6-blink`，任务和调试配置中通常写：

```text
build/Debug/stm32f103c8t6-blink.elf
```

但 CubeMX 不同版本可能生成不同的 target 名称。最可靠的方法是先构建，再查找实际文件：

```powershell
Get-ChildItem .\build -Recurse -Filter *.elf |
  Select-Object FullName,LastWriteTime
```

看到的路径是什么，就把 `tasks.json` 和 `launch.json` 中的占位路径改成什么。

如果项目名不是 `stm32f103c8t6-blink`，把所有出现的 `<工程名>` 替换成真实名字。

## 8. 配置 Cortex-Debug

打开：

```text
.vscode/launch.json
```

示例：

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
      "executable": "${workspaceFolder}/build/Debug/<工程名>.elf",
      "device": "STM32F103C8",
      "configFiles": [
        "${workspaceFolder}/openocd/stm32f1-stlink.cfg"
      ],
      "searchDir": [
        "<OpenOCD scripts 目录>"
      ],
      "runToEntryPoint": "main",
      "preLaunchTask": "CMake: build (Debug)"
    }
  ]
}
```

说明：

| 字段 | 含义 |
| --- | --- |
| `servertype` | 使用 OpenOCD |
| `executable` | 带调试符号的 ELF 文件 |
| `device` | 目标芯片名称，用于扩展显示信息 |
| `configFiles` | 自定义 OpenOCD 配置 |
| `searchDir` | OpenOCD 查找 `interface/`、`target/` 脚本的目录 |
| `runToEntryPoint` | 启动后运行到 `main` |
| `preLaunchTask` | 调试前自动构建 |

如果 `searchDir` 写错，OpenOCD 会在 `source [find interface/stlink.cfg]` 时报告找不到文件。

## 9. 配置 OpenOCD 本地文件

工程目录中创建：

```text
openocd/stm32f1-stlink.cfg
```

内容：

```tcl
source [find interface/stlink.cfg]
transport select swd
source [find target/stm32f1x.cfg]

adapter speed 1000
```

说明：

| 行 | 作用 |
| --- | --- |
| `source [find interface/stlink.cfg]` | 加载 ST-Link 接口驱动 |
| `transport select swd` | 使用 SWD，而不是 JTAG |
| `source [find target/stm32f1x.cfg]` | 加载 STM32F1 目标配置 |
| `adapter speed 1000` | 使用约 1 MHz 的调试速度 |

不同芯片要替换 target：

```text
STM32F4 -> target/stm32f4x.cfg
STM32G0 -> target/stm32g0x.cfg
STM32H7 -> target/stm32h7x.cfg
```

## 10. 第一次在 VS Code 中配置和构建

### 10.1 用 CMake Tools 配置

1. 按 `Ctrl+Shift+P` 打开命令面板。
2. 运行：

   ```text
   CMake: Select Configure Preset
   ```

3. 选择 `debug`。
4. 运行：

   ```text
   CMake: Configure
   ```

5. 等待底部状态栏显示 `CMake: [Debug]`。

### 10.2 用任务构建

1. 按 `Ctrl+Shift+P`。
2. 选择 `Tasks: Run Task`。
3. 选择 `CMake: build (Debug)`。
4. 终端最后应显示构建成功。

### 10.3 用命令行构建

如果 VS Code 任务看起来不稳定，先用终端证明命令行本身没问题：

```powershell
cmake --preset debug
cmake --build --preset debug
```

终端优先原则：

```text
如果命令行能构建，VS Code 不能构建 -> 查 tasks.json / CMake Tools
如果命令行也不能构建 -> 查 CMakeLists / 工具链 / 源码
```

## 11. 识别错误的来源

### 11.1 C/C++ 红色波浪线

可能原因：

- `compile_commands.json` 不存在。
- C/C++ 扩展没有选择 CMake Tools 配置。
- 配置仍指向旧的 build 目录。

处理：

```powershell
cmake --preset debug
Get-ChildItem .\build\Debug -Filter compile_commands.json
```

然后在 VS Code 中执行：

```text
C/C++: Select a Configuration...
```

选择 `Debug`。

### 11.2 CMake 配置失败

先看终端第一条错误，不要把最后一行当成根因。常见原因是：

- Ninja 不在 PATH。
- `arm-none-eabi-gcc` 不在 PATH。
- 工具链文件路径写错。
- build 目录中残留了旧缓存。

如果确认是缓存问题，可以只删除本工程的 `build/Debug`，不要删除源码目录。

### 11.3 Cortex-Debug 启动失败

如果 OpenOCD 单独能连接，但 VS Code 失败：

1. 检查 `executable` 是否真实存在。
2. 检查 `searchDir` 是否指向 OpenOCD scripts。
3. 检查 `configFiles` 中本地 cfg 是否存在。
4. 打开 `Terminal` 和 `Debug Console` 查看完整 OpenOCD 输出。

## 12. 本章完成标准

- [ ] 使用 VS Code 打开了工程根目录。
- [ ] `.vscode/extensions.json` 已存在。
- [ ] `.vscode/settings.json` 已配置。
- [ ] `CMakePresets.json` 能被 `cmake --list-presets` 识别。
- [ ] `cmake --preset debug` 成功。
- [ ] `cmake --build --preset debug` 成功。
- [ ] `build/Debug/compile_commands.json` 存在。
- [ ] `build/Debug/*.elf` 存在。
- [ ] `.vscode/launch.json` 指向正确的 ELF。
- [ ] `openocd/stm32f1-stlink.cfg` 存在。

下一章：[04 构建、烧录与调试](./04-build-flash-debug.md)
