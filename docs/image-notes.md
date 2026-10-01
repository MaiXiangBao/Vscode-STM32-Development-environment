# 配图说明

[返回主教程](../README.md)

原创配图采用统一颜色：蓝色表示配置和编辑，橙色表示构建或需要核对的选项，绿色表示目标硬件与验收，紫色表示调试和辅助配置。

| 配图 | 内容 | 类型 |
|---|---|---|
| 01-workflow | CubeMX 到烧录、调试的完整协作关系 | 原创结构图 |
| 02-files | .ioc、源码、构建文件、ELF、BIN/HEX 的关系 | 原创结构图 |
| 03-path | 可执行程序和 PATH 的关系 | 原创目录图 |
| 04-extensions | 核心扩展的标识和作用 | 原创操作示意 |
| 05-cubemx | SYS、GPIO、HSI 最小配置 | 原创操作示意 |
| 06-project | Project Manager 生成选项 | 原创操作示意 |
| 07-build | Configure、Compile、Link 的区别 | 原创流程图 |
| 08-swd | F103C8T6 与外置 ST-LINK 的 SWD 连接 | 原创接线图 |
| 09-debug-chain | Cortex-Debug、GDB、OpenOCD、探针和芯片 | 原创流程图 |
| 10-debug-ui | 断点、执行位置、Watch、调用栈 | 原创位置示意 |
| 11-porting | 换芯片后需要核对的内容 | 原创核对图 |
| 12-cubemx-clock | CubeMX 6.15.0 的 F103C8T6 HSI 8 MHz 时钟树 | 本地真实截图 |
| 13-cubemx-generator | F103C8T6 工程的库复制与用户代码保留选项 | 本地真实截图 |
| 14-cubemx-pinout | F103C8Tx / LQFP48 引脚图，PC13 LED 与 PA13/PA14 SWD | 本地真实截图 |
| 15-cubemx-sys | F103 的 SYS，Debug = Serial Wire，时基 SysTick | 本地真实截图 |
| 16-cubemx-gpio | PC13 的 High、推挽、无上下拉、Low、LED 标签 | 本地真实截图 |
| 17-cubemx-project | F103 的 CMake / GCC 工程与 F1 固件包 | 本地真实截图 |

操作示意明确标注“非软件截图”，帮助读者定位概念和关键字段；菜单与布局应以安装版本为准。真实截图展示教程验证工程，不表示该工程已经完成硬件验证。截图保留原始软件界面，软件标识归相应权利人所有。

共 17 张配图：11 张原创图各有 PNG 和 SVG，6 张真实截图保留工具输出的 JPG 格式。README 引用 PNG 与 JPG，GitHub 与普通 Markdown 阅读器可直接显示；SVG 保留可编辑图形和文字。`assets/create_images.py` 可重新生成原创图，需 Pillow 和中文字体。脚本默认使用 Windows 微软雅黑字体路径，换系统时修改路径即可。

全部图片放在仓库内，无需外部图床。发布或移动 README 后，注意相对路径关系。
