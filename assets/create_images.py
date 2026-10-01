"""Render the tutorial's original diagrams to PNG and editable SVG."""
from pathlib import Path
from html import escape
import math
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).parent / 'images'
OUT.mkdir(parents=True, exist_ok=True)
FONT = 'C:/Windows/Fonts/msyh.ttc'
BOLD = 'C:/Windows/Fonts/msyhbd.ttc'
NAVY, MUTED, BG = '#122c47', '#4d6478', '#f4f7fb'
BLUE, GREEN, ORANGE, PURPLE = '#176fc1', '#218461', '#b66416', '#7153b5'
PALE = {BLUE: '#eaf3ff', GREEN: '#e9f6ef', ORANGE: '#fff3e7', PURPLE: '#f2edfc'}


class Diagram:
    def __init__(self, name, title, subtitle, height=670, ui=False):
        self.name, self.height = name, height
        self.image = Image.new('RGB', (1200, height), BG)
        self.draw = ImageDraw.Draw(self.image)
        self.xml = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" '
                    f'height="{height}" viewBox="0 0 1200 {height}">',
                    f'<rect width="1200" height="{height}" fill="{BG}"/>']
        self.rect(0, 0, 1200, 106, NAVY, radius=0)
        self.text(42, 24, title, 31, 'white', bold=True)
        self.text(43, 69, subtitle, 19, '#c7d9e9')
        kind = '原创操作示意 · 非软件截图' if ui else '原创结构示意 · 对照正文操作与验收'
        self.text(42, height - 36, kind, 16, MUTED)

    def rect(self, x, y, width, height, fill='white', stroke=None, radius=14):
        self.draw.rounded_rectangle((x, y, x + width, y + height),
                                    radius=radius, fill=fill, outline=stroke,
                                    width=2 if stroke else 1)
        self.xml.append(f'<rect x="{x}" y="{y}" width="{width}" '
                        f'height="{height}" rx="{radius}" fill="{fill}" '
                        f'stroke="{stroke or "none"}" stroke-width="2"/>')

    def text(self, x, y, value, size=22, color=NAVY, bold=False, center=False):
        font = ImageFont.truetype(BOLD if bold else FONT, size)
        anchor = 'mt' if center else 'lt'
        self.draw.text((x, y), value, font=font, fill=color, anchor=anchor)
        self.xml.append(f'<text x="{x}" y="{y}" fill="{color}" '
                        f'font-size="{size}" font-weight="{700 if bold else 400}" '
                        f'font-family="Microsoft YaHei,Noto Sans CJK SC,sans-serif" '
                        f'text-anchor="{"middle" if center else "start"}" '
                        f'dominant-baseline="text-before-edge">{escape(value)}</text>')

    def card(self, x, y, w, h, title, lines, color=BLUE):
        self.rect(x, y, w, h, PALE[color], color)
        title_size = 25
        while self.draw.textlength(title, font=ImageFont.truetype(BOLD, title_size)) > w - 36:
            title_size -= 1
        self.text(x + 18, y + 17, title, title_size, color, bold=True)
        for i, line in enumerate(lines):
            self.text(x + 18, y + 61 + i * 31, line, 20)

    def arrow(self, x1, y1, x2, y2, color=MUTED):
        self.draw.line((x1, y1, x2, y2), fill=color, width=3)
        angle = math.atan2(y2-y1, x2-x1)
        points = [(x2, y2),
                  (x2-12*math.cos(angle-.5), y2-12*math.sin(angle-.5)),
                  (x2-12*math.cos(angle+.5), y2-12*math.sin(angle+.5))]
        self.draw.polygon(points, fill=color)
        self.xml.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                        f'stroke="{color}" stroke-width="3"/>')
        vertices = ' '.join(f'{x:.1f},{y:.1f}' for x,y in points)
        self.xml.append(f'<polygon points="{vertices}" fill="{color}"/>')

    def save(self):
        self.image.save(OUT / f'{self.name}.png', optimize=True)
        (OUT / f'{self.name}.svg').write_text('\n'.join(self.xml + ['</svg>']),
                                           encoding='utf-8')


d = Diagram('01-workflow', '一张图看懂 STM32 开发环境',
            '先生成工程，再构建固件；烧录和调试都通过探针连接目标芯片', 780)
d.card(44, 142, 330, 146, '1  CubeMX：硬件配置',
       ['选芯片 · 配引脚 · 配时钟', '.ioc → 初始化代码 + CMake'])
d.card(436, 142, 330, 146, '2  VS Code：编写程序',
       ['编辑 main.c 和应用源码', '扩展提供补全与操作入口'])
d.card(828, 142, 328, 146, '3  CMake → Ninja → GCC',
       ['生成规则 → 执行 → 编译链接', '输出 STM32_Blink.elf'])
d.arrow(379, 212, 427, 212)
d.arrow(774, 212, 819, 212)
d.arrow(990, 300, 990, 380)
d.card(44, 398, 330, 148, '6  STM32：执行程序',
       ['Flash 保存固件，RAM 保存变量', 'PC13 控制用户 LED'], GREEN)
d.card(436, 398, 330, 148, '5  ST-LINK：硬件桥梁',
       ['电脑侧 USB，芯片侧 SWD', '负责传递下载和调试指令'], GREEN)
d.card(828, 398, 328, 148, '4  OpenOCD：控制目标',
       ['写 Flash · 校验 · 复位', '提供 GDB 调试服务'], GREEN)
d.arrow(822, 470, 778, 470)
d.arrow(428, 470, 384, 470)
d.rect(44, 593, 1112, 95, 'white')
d.text(66, 610, '按 F5 时：Cortex-Debug → GDB → OpenOCD → ST-LINK → STM32', 25, PURPLE, True)
d.text(66, 650, '断点、单步和变量信息通过同一条链路返回 VS Code。', 21)
d.save()

d = Diagram('02-files', '你会遇到的文件：谁生成，谁使用',
            'ELF 是本教程烧录与调试的共同产物；BIN 和 HEX 按需转换', 620)
d.card(44, 151, 308, 158, '.ioc：硬件配置', ['CubeMX 保存', '改引脚、时钟时重新打开'])
d.card(447, 151, 308, 158, '.c / .h / .s / .ld', ['源码、启动代码、链接脚本', 'GCC 编译和链接的输入'])
d.card(850, 151, 306, 158, '.elf：完整固件', ['含加载地址和调试符号', 'OpenOCD 下载，GDB 读符号'], GREEN)
d.arrow(365, 227, 434, 227)
d.arrow(768, 227, 837, 227)
d.arrow(1000, 321, 1000, 368)
d.card(44, 391, 712, 132, 'CMakeLists + 预设 + 工具链文件',
       ['描述编译规则；CMake 生成 build.ninja，Ninja 调用 GCC',
        'build/Debug 存构建产物，compile_commands.json 记录编译参数'], PURPLE)
d.card(850, 391, 306, 132, '.bin / .hex：可选',
       ['由 objcopy 从 ELF 转换', 'BIN 下载要指定起始地址'], ORANGE)
d.save()

d = Diagram('03-path', '安装目录与 PATH：添加可执行程序所在目录',
            '保留完整工具包；PATH 只添加目录，原有条目继续保留', 640)
rows = [('Arm GCC', 'C:/STM32Tools/arm-gnu/bin', 'arm-none-eabi-gcc.exe'),
        ('CMake', 'C:/STM32Tools/cmake/bin', 'cmake.exe'),
        ('Ninja', 'C:/STM32Tools/ninja', 'ninja.exe'),
        ('OpenOCD', 'C:/STM32Tools/openocd/bin', 'openocd.exe')]
for i,(label,path,exe) in enumerate(rows):
    y = 144+i*91
    d.rect(44,y,1112,75,'white')
    d.text(66,y+24,label,23,BLUE,True)
    d.text(237,y+25,path,22)
    d.arrow(755,y+38,802,y+38)
    d.text(823,y+25,exe,19)
d.rect(44,528,1112,54,PALE[ORANGE])
d.text(66,541,'保存后：关掉旧终端和 VS Code，重开后用 Get-Command 查看实际路径。',23,ORANGE)
d.save()

d = Diagram('04-extensions', 'VS Code 扩展：先装这三个',
            'Ctrl + Shift + X 打开扩展列表；搜索名称后核对标识', 610, True)
for y,title,ident,detail,color in [
    (143,'C/C++','ms-vscode.cpptools','补全、跳转、源码诊断',BLUE),
    (277,'CMake Tools','ms-vscode.cmake-tools','预设选择、Configure、Build',PURPLE),
    (411,'Cortex-Debug','marus25.cortex-debug','调用 GDB，显示断点与变量',GREEN)]:
    d.rect(44,y,1112,110,PALE[color],color)
    d.text(66,y+18,title,27,color,True)
    d.text(66,y+63,ident,20)
    d.text(665,y+43,detail,23)
d.save()

d = Diagram('05-cubemx', 'CubeMX：F103C8T6 LED 示例的最小配置',
            '在 Pinout & Configuration 中设置；PA13 / PA14 保留给 SWD', 680, True)
d.card(44,142,350,150,'System Core → SYS',
       ['Debug = Serial Wire', 'PA13：SWDIO，PA14：SWCLK'])
d.card(44,315,350,155,'System Core → GPIO',
       ['PC13 = GPIO_Output', 'User Label = LED', 'Push Pull · No Pull · Low'])
d.rect(458,142,698,328,'white')
d.rect(610,178,384,233,NAVY)
d.text(802,210,'STM32F103C8T6',30,'white',True,True)
d.text(802,267,'HSI → SYSCLK = 8 MHz',23,'#c7d9e9',False,True)
d.text(802,318,'生成后：LED_GPIO_Port / LED_Pin',18,'#c7d9e9',False,True)
d.arrow(588,360,410,360,GREEN)
d.text(509,433,'PC13 → 用户 LED（低电平亮）',22,GREEN)
d.text(1010,207,'PA13',21,BLUE)
d.text(1010,255,'PA14',21,BLUE)
d.card(44,498,1112,106,'Clock Configuration',
       ['System Clock Mux 选 HSI；AHB / APB 保持 /1；HSE / LSE 不启用。'],ORANGE)
d.save()

d = Diagram('06-project', 'CubeMX：生成工程前检查这些选项',
            'Project Manager 中配置；最终工程根目录要同时有 .ioc 和 CMakeLists.txt', 660, True)
d.rect(44,145,710,432,'white')
rows=[('Project Name','STM32_Blink'),('最终工程目录','C:/STM32Projects/STM32_Blink'),
      ('Toolchain / IDE','CMake'),('Default Compiler / Linker','GCC'),
      ('固件包','STM32Cube FW_F1')]
for i,(label,value) in enumerate(rows):
    y=167+i*74
    d.text(64,y+12,label,20,MUTED)
    d.rect(333,y,394,51,PALE[BLUE])
    d.text(349,y+13,value,18,BLUE,bold=True)
d.card(800,145,356,214,'Code Generator',
       ['Keep User Code：勾选', '所需库：复制进工程', '之后检查 USER CODE 保留'],GREEN)
d.rect(800,398,356,82,BLUE)
d.text(978,422,'GENERATE CODE',25,'white',True,True)
d.text(801,511,'生成完再核对目录与文件。',21)
d.save()

d = Diagram('07-build', '构建分三步：Configure、Compile、Link',
            'Configuring done 只表示规则已生成；生成 ELF 才完成本次构建', 680)
d.card(44,144,333,184,'1  CMake Configure',
       ['读取 CMakeLists 和预设', '识别 arm-none-eabi-gcc', '生成 build.ninja'],BLUE)
d.card(434,144,333,184,'2  Ninja → GCC Compile',
       ['执行每个源文件的编译', '.c / .s → .o', '未改变的文件通常无需重编'],ORANGE)
d.card(824,144,332,184,'3  GCC Link',
       ['按 .ld 链接目标文件', '生成 STM32_Blink.elf', '还可生成 .map'],GREEN)
d.arrow(383,235,425,235)
d.arrow(773,235,815,235)
d.rect(44,373,1112,199,'white')
d.text(65,394,'cmake --preset tutorial-debug',25,BLUE,True)
d.text(65,446,'cmake --build --preset tutorial-debug --parallel',25,ORANGE,True)
d.text(65,505,'验收：build/Debug/STM32_Blink.elf 存在，构建退出码为 0。',23,GREEN)
d.save()

d = Diagram('08-swd', 'F103C8T6：连接外置 ST-LINK',
            '芯片 SWDIO / SWCLK 引脚要保留；USB 线必须支持数据传输', 810)
d.card(44,140,1112,117,'STM32F103C8T6 最小系统板 · BOOT0 = 0',
       ['电脑 USB → 外置 ST-LINK → SWD 信号线 → STM32F103C8T6'],BLUE)
d.rect(44,295,338,309,PALE[PURPLE],PURPLE)
d.rect(819,295,337,309,PALE[GREEN],GREEN)
d.text(213,310,'外置 ST-LINK',27,PURPLE,True,True)
d.text(987,310,'STM32F103C8T6',27,GREEN,True,True)
signals=[('SWDIO','PA13 / SWDIO',BLUE),('SWCLK','PA14 / SWCLK',ORANGE),
         ('GND','GND',MUTED),('VTref / Vref','目标板 3.3 V 电源域',PURPLE),
         ('NRST','NRST（建议连接）',GREEN)]
for i,(left,right,color) in enumerate(signals):
    y=366+i*44
    d.text(67,y,left,23,color)
    d.text(841,y,right,21,color)
    d.arrow(387,y+15,811,y+15,color)
d.rect(44,641,1112,87,PALE[ORANGE])
d.text(65,657,'VTref 是目标电压参考；是否能供电要看探针说明。',24,ORANGE,True)
d.text(65,696,'目标板须有稳定供电和共地，避免两个电源输出直接相连。',20)
d.save()

d = Diagram('09-debug-chain', '按 F5 后，断点指令怎样到达芯片',
            'ELF 提供源码与符号；硬件运行状态沿调试链路返回界面', 660)
labels=[('VS Code','Cortex-Debug',BLUE),('Arm GDB','读取 ELF 符号',PURPLE),
        ('OpenOCD','本地 GDB 服务',ORANGE),('ST-LINK','USB / SWD',GREEN),
        ('STM32','执行 / 暂停',GREEN)]
for i,(title,detail,color) in enumerate(labels):
    x=44+i*226
    d.card(x,163,207,151,title,[detail],color)
    if i<4: d.arrow(x+210,240,x+222,240)
d.rect(44,365,1112,191,'white')
d.text(67,386,'F5 启动顺序',25,PURPLE,True)
d.text(67,431,'先 Build → 启动 OpenOCD → GDB 连接 → 下载并复位 → 停在 main',24)
d.text(67,484,'不要同时让 CubeProgrammer、手工 OpenOCD 和其他调试器占用探针。',22,ORANGE)
d.save()

d = Diagram('10-debug-ui', '断点调试：三个位置先学会看',
            'Run and Debug 中选本文配置；下面是位置示意，实际布局随版本变化', 710, True)
d.rect(44,142,298,477,'white')
d.text(66,162,'VARIABLES / WATCH',23,PURPLE,True)
d.text(67,218,'now = …',22)
d.text(67,256,'last_tick = …',22)
d.text(67,294,'s_blink_count = 1',22,GREEN,True)
d.text(66,371,'CALL STACK',23,PURPLE,True)
d.text(67,425,'main',23)
d.text(67,464,'当前函数调用链',21,MUTED)
d.rect(372,142,784,320,'white')
d.text(393,162,'main.c  /  主循环',23,BLUE,True)
code=[(218,'uint32_t now = HAL_GetTick();'),
      (264,'if (时间差 >= 500 ms)'),
      (315,'    HAL_GPIO_TogglePin(...);'),
      (363,'    ++s_blink_count;')]
for y,line in code:
    if y==315:
        d.rect(385,y-7,748,42,'#fff0b9',radius=5)
        d.rect(389,y+7,12,12,'#d83f43',radius=6)
    d.text(421,y,line,23)
d.text(395,412,'红点：断点；黄色行：下一条待执行位置',20,MUTED)
d.card(372,492,784,127,'调试工具栏',
       ['F5 继续    F10 单步跳过    F11 进入函数',
        'Shift + F5 停止；暂停会改变 LED 的时间行为。'],GREEN)
d.save()

d = Diagram('11-porting', '换芯片时，检查这三组内容',
            '生成对应型号的新工程，再迁移应用代码与通用编辑器配置', 580)
d.card(44,151,333,281,'硬件与 CubeMX',
       ['真实型号与封装', 'LED 引脚、有效电平', 'HSI / HSE / PLL 配置',
        'SWD 接线、供电和复位'],BLUE)
d.card(434,151,333,281,'编译与内存',
       ['启动文件、中断向量表', '芯片宏、CPU / FPU 参数', 'Flash / RAM 链接脚本',
        'HAL / CMSIS 对应系列'],ORANGE)
d.card(824,151,332,281,'下载与调试',
       ['OpenOCD target 脚本', '实际支持的探针驱动', 'ELF 的名称与构建目录',
        'F5 前的编译任务'],GREEN)
d.text(44,473,'本例：Cortex-M3 · Flash 64 KB · RAM 20 KB · target/stm32f1x.cfg。',22)
d.save()

print(f'Rendered 11 diagrams: {OUT}')
