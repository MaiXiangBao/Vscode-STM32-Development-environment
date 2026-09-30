# 05 CMake 模板详解与跨芯片修改

[上一章：构建、烧录与调试](./04-build-flash-debug.md) | [返回主页](../README.md) | [下一章：故障排查](./06-troubleshooting.md)

这一章解释本仓库模板为什么能构建 STM32，以及换芯片时哪些参数必须修改。

## 1. 两种工程来源

### 1.1 CubeMX 直接生成 CMake

新版 CubeMX 可以选择：

```text
Project Manager -> Toolchain / IDE -> CMake
```

生成结果通常包含：

```text
CMakeLists.txt
cmake/gcc-arm-none-eabi.cmake
cmake/stm32cubemx/CMakeLists.txt
```

这是首选方式。CubeMX 官方生成器最了解它自己生成的源文件和启动文件。

### 1.2 CubeMX 生成 Makefile，再手工使用 CMake

如果 CubeMX 没有 CMake 选项：

1. 选择 `Makefile` 生成代码。
2. 把 `templates/CMakeLists.txt` 复制到工程根目录。
3. 根据实际目录和文件名修改参数。
4. 使用本仓库的 `CMakePresets.json` 和 `cmake/gcc-arm-none-eabi.cmake`。

手工模板的目标不是替代 CubeMX，而是把你已经生成的源码正确交给 GCC。

## 2. CMake 的角色

CMake 不直接“烧录”芯片，也不负责调试。它的工作是：

```text
读取配置
  -> 找到交叉编译器
  -> 找出源文件和头文件
  -> 生成 Ninja 构建文件
  -> 调用 GCC
  -> 调用链接器
```

实际编译过程是：

```text
.c / .s
  -> arm-none-eabi-gcc
  -> .o
  -> arm-none-eabi-gcc 链接
  -> .elf
  -> objcopy
  -> .hex / .bin
```

## 3. 工具链文件

文件：

```text
cmake/gcc-arm-none-eabi.cmake
```

关键内容：

```cmake
set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_PROCESSOR arm)

set(TOOLCHAIN_PREFIX arm-none-eabi-)

find_program(CMAKE_C_COMPILER ${TOOLCHAIN_PREFIX}gcc REQUIRED)
find_program(CMAKE_ASM_COMPILER ${TOOLCHAIN_PREFIX}gcc REQUIRED)
find_program(CMAKE_OBJCOPY ${TOOLCHAIN_PREFIX}objcopy REQUIRED)
find_program(CMAKE_SIZE ${TOOLCHAIN_PREFIX}size REQUIRED)

set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)
set(CMAKE_EXECUTABLE_SUFFIX ".elf")
```

### 3.1 为什么 SYSTEM_NAME 是 Generic

STM32 是裸机目标，没有 Windows/Linux 操作系统。设置：

```cmake
set(CMAKE_SYSTEM_NAME Generic)
```

可以避免 CMake 按桌面操作系统的规则生成可执行文件。

### 3.2 为什么 TRY_COMPILE_TARGET_TYPE 是 STATIC_LIBRARY

CMake 配置阶段会先尝试编译一个测试程序。裸机程序没有默认启动文件和系统 `main()`，链接测试程序可能失败，但编译器本身没有问题。

设置：

```cmake
set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)
```

让 CMake 用静态库方式做编译器测试，减少误报。

## 4. 五个最关键的 STM32 参数

换芯片时，要检查：

1. `MCU_FLAGS`
2. `STM32_DEFINES`
3. `LINKER_SCRIPT`
4. `STARTUP_SOURCE`
5. HAL/CMSIS 目录名

### 4.1 MCU_FLAGS

F103：

```cmake
set(MCU_FLAGS
    -mcpu=cortex-m3
    -mthumb
)
```

常见内核参数：

| 内核 | 参数 |
| --- | --- |
| Cortex-M0 | `-mcpu=cortex-m0 -mthumb` |
| Cortex-M0+ | `-mcpu=cortex-m0plus -mthumb` |
| Cortex-M3 | `-mcpu=cortex-m3 -mthumb` |
| Cortex-M4F | `-mcpu=cortex-m4 -mthumb -mfpu=fpv4-sp-d16 -mfloat-abi=hard` |
| Cortex-M7F | `-mcpu=cortex-m7 -mthumb -mfpu=fpv5-d16 -mfloat-abi=hard` |

带 FPU 的芯片是否使用硬件浮点，还取决于芯片型号、HAL 配置和 ABI。不要只因为内核有 FPU 就直接加硬浮点选项，应先确认芯片实际核心和工程 ABI。

### 4.2 STM32_DEFINES

F103C8 示例：

```cmake
set(STM32_DEFINES
    STM32F103xB
    USE_HAL_DRIVER
)
```

常见定义：

| 芯片 | 宏 |
| --- | --- |
| STM32F103C8T6 | `STM32F103xB` |
| STM32F103RCT6 | `STM32F103xE` |
| STM32F407VGT6 | `STM32F407xx` |
| STM32G030C8 | `STM32G030xx` |
| STM32H743VIT6 | `STM32H743xx` |

准确值优先从 CubeMX 生成的 `Makefile`、`CMakeLists.txt` 或 HAL 头文件对应的 device define 中确认。

### 4.3 LINKER_SCRIPT

示例：

```cmake
set(LINKER_SCRIPT
    ${CMAKE_CURRENT_SOURCE_DIR}/STM32F103C8Tx_FLASH.ld
)
```

链接脚本定义：

- Flash 起始地址。
- Flash 大小。
- RAM 起始地址。
- RAM 大小。
- `.text`、`.data`、`.bss`、堆栈等段如何放置。

如果链接脚本选择错误，可能出现：

```text
region `FLASH' overflowed by ... bytes
```

或者程序能编译但运行时立即 HardFault。

### 4.4 STARTUP_SOURCE

示例：

```cmake
set(STARTUP_SOURCE
    ${CMAKE_CURRENT_SOURCE_DIR}/startup_stm32f103xb.s
)
```

启动文件负责：

1. 建立中断向量表。
2. 初始化 `.data` 和 `.bss`。
3. 调用 `SystemInit()`。
4. 跳转到 `main()`。

启动文件中的向量表、芯片型号和链接脚本必须匹配。

### 4.5 HAL/CMSIS 目录

F1 模板使用：

```text
Drivers/STM32F1xx_HAL_Driver
Drivers/CMSIS/Device/ST/STM32F1xx
Drivers/CMSIS/Include
```

换系列时要替换成：

```text
Drivers/STM32F4xx_HAL_Driver
Drivers/CMSIS/Device/ST/STM32F4xx
```

或对应的 G0、H7、F0 目录。

## 5. 源文件收集

模板使用：

```cmake
file(GLOB_RECURSE CORE_SOURCES CONFIGURE_DEPENDS
    ${CMAKE_CURRENT_SOURCE_DIR}/Core/Src/*.c
)
```

这样做是为了配合 CubeMX 重新生成代码：新增外设初始化文件时，不需要手动更新每一个源文件名。

但是 `GLOB` 也有缺点：

- 容易把不该编译的文件带入工程。
- 文件重命名或删除时 IDE 有时需要重新配置。
- 大型正式工程更适合显式源文件列表。

对于学生学习工程，`GLOB_RECURSE ... CONFIGURE_DEPENDS` 是可接受的折中。

模板会排除：

```cmake
list(FILTER HAL_SOURCES EXCLUDE REGEX ".*_template\\.c$")
```

因为 HAL 包中的 `_template.c` 通常只是示例模板，不应该直接参与构建。

## 6. 头文件目录

```cmake
target_include_directories(${PROJECT_NAME} PRIVATE
    Core/Inc
    User/Inc
    Drivers/STM32F1xx_HAL_Driver/Inc
    Drivers/STM32F1xx_HAL_Driver/Inc/Legacy
    Drivers/CMSIS/Device/ST/STM32F1xx/Include
    Drivers/CMSIS/Include
)
```

作用：

- 让 `#include "main.h"` 能找到。
- 让 `stm32f1xx_hal.h` 能找到。
- 让 CMSIS 内核头文件能找到。

如果编译时报：

```text
fatal error: stm32f1xx_hal.h: No such file or directory
```

先检查这里是否包含真实目录，不要先猜编译器坏了。

## 7. 编译选项

模板中的核心选项：

```cmake
-Wall
-Wextra
-fdata-sections
-ffunction-sections
```

含义：

| 选项 | 作用 |
| --- | --- |
| `-Wall` | 打开常用警告 |
| `-Wextra` | 打开更多警告 |
| `-fdata-sections` | 每个数据符号单独放段 |
| `-ffunction-sections` | 每个函数单独放段 |

Debug：

```cmake
$<$<CONFIG:Debug>:-Og>
$<$<CONFIG:Debug>:-g3>
```

Release：

```cmake
$<$<CONFIG:Release>:-Os>
```

初学调试建议使用 `-Og`，比 `-O2` 更容易观察变量，也比 `-O0` 更接近真实执行速度。

## 8. 链接选项

```cmake
-T${LINKER_SCRIPT}
-Wl,-Map=${PROJECT_NAME}.map,--cref
-Wl,--gc-sections
-Wl,--print-memory-usage
--specs=nano.specs
--specs=nosys.specs
```

说明：

| 选项 | 作用 |
| --- | --- |
| `-T...ld` | 使用指定链接脚本 |
| `-Wl,-Map=...` | 生成 map 文件 |
| `-Wl,--gc-sections` | 删除未使用的代码和数据段 |
| `-Wl,--print-memory-usage` | 输出 Flash/RAM 使用率 |
| `nano.specs` | 使用精简版 C 库 |
| `nosys.specs` | 提供裸机所需的最小系统调用替身 |

裸机工程常见链接错误：

```text
undefined reference to `_exit'
undefined reference to `_sbrk'
undefined reference to `_write'
```

通常与 `nosys.specs`、系统调用文件或 `printf` 重定向有关。先不要手写一堆系统调用，先确认是否真的使用了会触发这些函数的库功能。

## 9. 启动文件预处理

CubeMX 的启动文件虽然扩展名是 `.s`，里面可能包含预处理指令。GCC 默认对 `.s` 使用汇编器，而不一定走 C 预处理器。

模板设置：

```cmake
set_source_files_properties(${STARTUP_SOURCE} PROPERTIES
    COMPILE_OPTIONS "-x;assembler-with-cpp"
)
```

这样可以按“带 C 预处理器的汇编文件”处理启动文件。

如果启动文件报错，先确认：

1. 文件名是否和实际文件一致。
2. 大小写是否正确。
3. 启动文件是否属于当前芯片。
4. 是否被错误地当作 C 文件处理。

## 10. 生成 HEX、BIN 和 SIZE 报告

构建后执行：

```cmake
add_custom_command(TARGET ${PROJECT_NAME} POST_BUILD
    COMMAND ${CMAKE_OBJCOPY} -O ihex $<TARGET_FILE:${PROJECT_NAME}> ${PROJECT_NAME}.hex
    COMMAND ${CMAKE_OBJCOPY} -O binary $<TARGET_FILE:${PROJECT_NAME}> ${PROJECT_NAME}.bin
    COMMAND ${CMAKE_SIZE} $<TARGET_FILE:${PROJECT_NAME}>
)
```

这样每次构建后都会自动得到：

```text
stm32f103c8t6-blink.elf
stm32f103c8t6-blink.hex
stm32f103c8t6-blink.bin
stm32f103c8t6-blink.map
```

## 11. 换芯片的完整检查表

从 F103 换到另一颗芯片时，按顺序修改：

1. `project(...)` 中的工程名。
2. `MCU_FLAGS` 的内核和 FPU 参数。
3. `STM32_DEFINES`。
4. `LINKER_SCRIPT`。
5. `STARTUP_SOURCE`。
6. HAL 和 CMSIS include/source 路径。
7. OpenOCD target 脚本。
8. `launch.json` 的 `device`。
9. 主频、时钟树、GPIO 和板级外设。

## 12. 构建命令

配置：

```powershell
cmake --preset debug
```

构建：

```powershell
cmake --build --preset debug
```

清理并重建：

```powershell
cmake --build --preset debug --clean-first
```

如果是全新工具链或 CMake 版本出现异常：

```powershell
Remove-Item .\build\Debug -Recurse -Force
cmake --preset debug
cmake --build --preset debug
```

只删除 build 目录不会影响 CubeMX 源文件。

## 13. 本章完成标准

- [ ] 知道工具链文件、工程文件和 build 文件的区别。
- [ ] 能说出 `MCU_FLAGS` 的作用。
- [ ] 能找到 `STM32_DEFINES` 对应的芯片宏。
- [ ] 能找到链接脚本和启动文件。
- [ ] 知道换芯片时至少要修改哪些参数。
- [ ] 知道 `.elf`、`.hex`、`.bin`、`.map` 的区别。
- [ ] 能解释 `--specs=nosys.specs` 为什么常用于裸机工程。

下一章：[06 故障排查](./06-troubleshooting.md)
