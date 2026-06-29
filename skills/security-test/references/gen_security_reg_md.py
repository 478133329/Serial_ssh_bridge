#!/usr/bin/env python3
"""Generate security_reg.md from register sources."""

from pathlib import Path
import re
import xlrd
import openpyxl

REF = Path(__file__).resolve().parent
OUT = REF / "security_reg.md"

FAB_BASE = 0x33030000
DDR_FW_BASE = 0x33040000  # SE_DDR_FW in memory map
PERI_SUBSYS = 0x03000000
HSPERI_SUBSYS = 0x04000000


def parse_reg_table():
    sh = xlrd.open_workbook(str(REF / "reg_sec_fab_Athena2.xls")).sheet_by_name("Reg_Table")
    regs = {}
    cur = None
    for r in range(17, sh.nrows):
        row = sh.row_values(r)
        lo, hi, name, desc = row[0], row[1], row[2], row[4] or row[3]
        field, msb, lsb, init, rw = row[6], row[7], row[8], row[10], row[11]
        if name:
            cur = name
            off = int(str(hi).replace("h", ""), 16)
            regs[cur] = {"offset": off, "desc": desc or "", "fields": []}
        if cur and field:
            regs[cur]["fields"].append(
                {
                    "field": field,
                    "bits": f"[{int(msb)}:{int(lsb)}]",
                    "init": init,
                    "rw": rw,
                }
            )
    return regs


def parse_hsperi_fw():
    sh = xlrd.open_workbook(str(REF / "reg_sec_fab_Athena2.xls")).sheet_by_name("hsperi_fw(1835)")
    items = []
    for r in range(sh.nrows):
        row = sh.row_values(r)
        if isinstance(row[2], (int, float)) and row[2] != "":
            items.append((int(row[2]), str(row[3])))
    return sorted(items, reverse=True)


def parse_peri_fw():
    sh = xlrd.open_workbook(str(REF / "reg_sec_fab_Athena2.xls")).sheet_by_name("peri_fw(1835)")
    items = []
    for r in range(4, sh.nrows):
        row = sh.row_values(r)
        if isinstance(row[1], (int, float)):
            items.append(
                {
                    "bit": int(row[1]),
                    "start": str(row[3]).replace("_", ""),
                    "end": str(row[4]).replace("_", ""),
                    "ip": str(row[5]),
                }
            )
    return items


def fmt_addr(off):
    return f"0x{FAB_BASE + off:08X}"


def reg_section(regs, name, extra=""):
    r = regs[name]
    lines = [
        f"#### `{name}`",
        "",
        f"- **偏移**：`+0x{r['offset']:02X}` → `{fmt_addr(r['offset'])}`",
    ]
    if r["desc"]:
        lines.append(f"- **说明**：{r['desc']}")
    if extra:
        lines.append(f"- **备注**：{extra}")
    lines.extend(["", "| 字段 | 位 | 复位 | 读写 | 含义 |", "|------|----|------|------|------|"])
    for f in r["fields"]:
        meaning = ""
        if "_ar_ns" in f["field"] or "_aw_ns" in f["field"]:
            meaning = "1=允许非安全 master 读/写；测试时通常清 0 强制 secure"
        elif "_tz_s" in f["field"]:
            meaning = "1=该 slave 区域设为 secure"
        elif f["field"] == "reg_peri_fw_s_tz_s":
            meaning = "每位对应一个 PERI slave，1=secure"
        elif f["field"] == "reg_hsperi0_fw_tz_s":
            meaning = "HSPERI0 各 slave secure 位图"
        elif f["field"] == "reg_hsperi1_fw_tz_s":
            meaning = "HSPERI1 各 slave secure 位图"
        elif f["field"] == "reg_rom_fw_s_tz_s":
            meaning = "ROM 分区 secure 位图（24 区）"
        elif f["field"] == "fabFW_ROM_psmsk":
            meaning = "ROM 读锁定 post-mask"
        elif "illegal" in f["field"]:
            meaning = "非法从空间访问日志（RO）"
        lines.append(
            f"| `{f['field']}` | {f['bits']} | {f['init']} | {f['rw']} | {meaning or '-'} |"
        )
    lines.append("")
    return lines


def main():
    regs = parse_reg_table()
    hsperi_fw = parse_hsperi_fw()
    peri_fw = parse_peri_fw()

    # test_cases peri mapping (from bmtest names + memory map offsets in xlsx)
    peri_test_map = [
        (0, "PERI_INTC3", "0x27113000"),
        (1, "PERI_INTC2", "0x27112000"),
        (2, "PERI_INTC1", "0x27111000"),
        (3, "PERI_INTC0", "0x27110000"),
        (4, "PERI_OTP", "0x27100000", "SKIP"),
        (5, "PERI_MAILBOX", "0x270F0000"),
        (6, "PERI_SARADC", "0x270E0000"),
        (7, "PERI_TEMPSEN", "0x270D0000"),
        (8, "PERI_PMCTL", "0x27090000"),
        (9, "PERI_TIMER", "0x270A0000"),
        (10, "PERI_PWM4", "0x27064000"),
        (11, "PERI_PWM3", "0x27063000"),
        (12, "PERI_PWM2", "0x27062000"),
        (13, "PERI_PWM1", "0x27061000"),
        (14, "PERI_PWM0", "0x27060000"),
        (15, "PERI_EFUSE", "0x27050000"),
        (16, "PERI_KEYSCAN", "0x27040000"),
        (17, "PERI_WGN1", "0x27031000"),
        (18, "PERI_WGN0", "0x27030000"),
        (19, "PERI_GPIO5", "0x27025000"),
        (20, "PERI_GPIO4", "0x27024000"),
        (21, "PERI_GPIO3", "0x27023000"),
        (22, "PERI_GPIO2", "0x27022000"),
        (23, "PERI_GPIO1", "0x27021000"),
        (24, "PERI_GPIO0", "0x27020000"),
        (25, "PERI_WDT2", "0x27010200"),
        (26, "PERI_WDT1", "0x27010100"),
        (27, "PERI_WDT0", "0x27010000"),
    ]

    hsperi0_test = [
        (0, "HSPERI_SPI1", 18),
        (1, "HSPERI_SPI0", 17),
        (2, "HSPERI_UART7", 16),
        (3, "HSPERI_UART6", 15),
        (4, "HSPERI_UART5", 14),
        (5, "HSPERI_UART4", 13),
        (6, "HSPERI_UART3", 12),
        (7, "HSPERI_UART2", 11),
        (8, "HSPERI_UART1", 10),
        (9, "HSPERI_UART0", 9, "SKIP"),
        (10, "HSPERI_I2S_DW", 8),
        (11, "HSPERI_I2S_AUDSRC", 7),
        (12, "HSPERI_I2S5", 6),
        (13, "HSPERI_I2S4", 5),
        (14, "HSPERI_I2S3", 4),
        (15, "HSPERI_I2S2", 3),
        (16, "HSPERI_I2S1", 2),
        (17, "HSPERI_I2S0", 1),
        (18, "HSPERI_I2S_GLOBAL", 0),
        (19, "HSPERI_ETH1_CFG", 28),
        (20, "HSPERI_ETH0_CFG", 27),
        (21, "HSPERI_SPI_NAND", 21),
        (22, "HSPERI_I2C9", 31),
        (23, "HSPERI_I2C8", 30),
        (24, "HSPERI_I2C7", 29),
        (25, "HSPERI_I2C6", 26),
        (26, "HSPERI_I2C5", 25),
        (27, "HSPERI_I2C4", 24),
        (28, "HSPERI_I2C3", 23),
        (29, "HSPERI_I2C2", 22),
        (30, "HSPERI_I2C1", 20),
        (31, "HSPERI_I2C0", 19),
    ]

    hsperi1_test = [
        (0, "HSPERI_ROM", 26),
        (1, "HSPERI_SDMA1_CFG", 25),
        (2, "HSPERI_SDMA0_CFG", 24),
        (3, "HSPERI_SD2_CFG", 23),
        (4, "HSPERI_SD1_CFG", 22),
        (5, "HSPERI_SD0_CFG", 21),
        (6, "HSPERI_EMMC_CFG", 22),
        (7, "HSPERI_CAN1", 20),
        (8, "HSPERI_CAN0", 19),
        (9, "HSPERI_SPI3", 20),
        (10, "HSPERI_SPI2", 19),
    ]

    top_axi_map = [
        (0, "TOP_AXI_X2P"),
        (1, "VIP_CTRL_VO"),
        (2, "VIDEO_CTRL_VD3"),
        (3, "VIDEO_CTRL_VD2"),
        (4, "VIDEO_CTRL_VD1"),
        (5, "VIDEO_CTRL_VD0"),
        (6, "VIDEO_CTRL_VE"),
        (7, "DDR_CTRL_256M / top_north_cfg"),
    ]

    rom_regions = [f"0x{0x29400000 + i * 0x2000:08X}" for i in range(24)]

    lines = [
        "# Security 寄存器参考（Athena2）",
        "",
        "> 来源：`reg_sec_fab_Athena2.xls`、`reg_sec_fab_firewall.h`、`Athena2_memory_map.xlsx`、`testcase_security.c`",
        "> 供 bmtest 正式测试与 Agent 辅助验证（`rm`/`wm`）使用。",
        "",
        "## 1. 模块基地址",
        "",
        "| 模块 | 基地址 | 来源 | 用途 |",
        "|------|--------|------|------|",
        f"| `sec_fab_firewall` | `0x33030000` | memory map `SE_FAB_FW` | 总线防火墙主控：master/slave TZ、PERI/HSPERI/ROM/TOP |",
        f"| `sec_ddr_firewall` | `0x33040000` | memory map `SE_DDR_FW` | DDR secure region / obfuscation |",
        f"| PERI 子系统 | `0x03000000` | `peri_fw(1835)` | PERI 外设寄存器窗口 |",
        f"| HSPERI 子系统 | `0x04000000` | `HSPERI` sheet | HSPERI 外设寄存器窗口 |",
        f"| HSPERI ROM | `0x29400000` | memory map | ROM 分区测试基址 |",
        f"| DRAM 测试区 | `0x108000000` | bmtest `dram_secure_region` | DDR secure region 默认探测地址 |",
        "",
        "> **注意**：`testcase_security.c` 参考代码中 DDR 寄存器使用 `0x020A0000` 偏移写法，Athena2 memory map 显示 DDR 防火墙在 `0x33040000`。辅助验证时以 **当前固件 bmtest 打印的 `ddr_fab [...]` 地址** 为准。",
        "",
        "## 2. 通用测试配置流程",
        "",
        "绝大多数防火墙用例遵循相同寄存器操作序列（与官方表格 Initial/Test steps 一致）：",
        "",
        "1. **Master 非安全放行位（ar_ns / aw_ns）**：将 CPU 对应 master 的 `_ar_ns` / `_aw_ns` 位置 1，允许其在非安全态发起访问",
        "2. **Slave secure 位（tz_s）**：将目标外设/区域的 `_tz_s` 位置 1，标记为 secure",
        "3. **EL3 写入探针或读取真值**",
        "4. **`switch_el1` 切换至非安全 EL1**",
        "5. **EL1 再次访问**：预期读/写被阻断（读值变化、bus error、挂死或中断）",
        "",
        "### 2.1 testcase_security.c 关键写法",
        "",
        "```c",
        "// 1) 放开 CA53(master1) 非安全读（清除 forced secure）",
        "mmio_write_32(FAB_FIREWALL_BASE + 0x04, 0x000007FD);  // fabFW_hsperi_m_ar_ns",
        "",
        "// 2) SRAM 设为 secure",
        "mmio_write_32(FAB_FIREWALL_BASE + 0x28, 0xFFFFFFFF);  // reg_sram_s_tz_s",
        "",
        "// 3) DDR region0: start/end 4KB 对齐，enable",
        "mmio_write_32(DDR_FW_BASE + 0x08, dram_start >> 12);",
        "mmio_write_32(DDR_FW_BASE + 0x28, dram_end >> 12);",
        "mmio_write_32(DDR_FW_BASE + 0x00, 1 | (1 << 16));",
        "```",
        "",
        "**`fabFW_hsperi_m1_ar_ns`**：bit1=0 表示 CA53 读通道不再强制 secure，配合 `switch_el1` 后由非安全 CPU 发起访问。",
        "",
        "### 2.2 辅助验证常用 bmtest 命令",
        "",
        "| 场景 | 命令示例 | 说明 |",
        "|------|----------|------|",
        "| 读防火墙配置 | `rm 0x33030004` | 查看 hsperi master ar_ns |",
        "| 读 PERI secure 位图 | `rm 0x3303003C` | `reg_peri_fw_s_tz_s` |",
        "| 读 HSPERI0 位图 | `rm 0x33030040` | `reg_hsperi0_fw_tz_s` |",
        "| 读非法访问日志 | `rm 0x3303004C` / `rm 0x33030050` | `illegal_slave_space_access_info_l/h` |",
        "| 写后回读 | `wm <addr> <val>` 再 `rm <addr>` | 确认配置是否生效 |",
        "| 切 EL | `current_el` / `switch_el1` | 辅助复现 EL3/EL1 读值差异 |",
        "",
        "## 3. sec_fab_firewall 寄存器详表",
        "",
        f"基址：`0x{FAB_BASE:08X}`",
        "",
        "### 3.1 控制与 Master 防火墙",
        "",
    ]

    for n, extra in [
        ("reg_fab_fw_ctrl", "全局控制"),
        ("fabFW_hsperi_m_ar_ns", "HSPERI master 读通道 ns 位，bit1 常对应 CA53"),
        ("fabFW_hsperi_m_aw_ns", "HSPERI master 写通道 ns 位"),
        ("fabFW_ddr_m_ar_ns", "DDR fabric master 读 ns，16 路"),
        ("fabFW_ddr_m_aw_ns", "DDR fabric master 写 ns"),
        ("fabFW_tpu0_m_ar_ns", "TPU master 读 ns"),
        ("fabFW_tpu0_m_aw_ns", "TPU master 写 ns"),
        ("fabFW_RTC_ar_ns", "RTC master 读 ns"),
        ("fabFW_RTC_aw_ns", "RTC master 写 ns"),
        ("fabFW_C906B_ns", "C906B/C906L ar/aw ns"),
    ]:
        if n in regs:
            lines.extend(reg_section(regs, n, extra))

    lines.extend(["### 3.2 Slave TrustZone（tz_s）", ""])
    for n, extra in [
        ("fabFW_hsperi_s_tz_s", "HSPERI fabric 内部 slave"),
        ("fabFW_ddr_ctrl_s_tz_s", "DDR controller slave"),
        ("reg_sram_s_tz_s", "on-chip SRAM secure 控制"),
        ("fabFW_ap_s4_tz_s", "APB slave s4"),
        ("fabFW_tpu0_s_tz_s", "TPU SRAM/ctrl 分区"),
        ("fabFW_top_s_tz_s", "TOP AXI fabric slave，见 §4.1"),
        ("reg_peri_fw_s_tz_s", "PERI 各 slave secure 位图，见 §4.2"),
        ("reg_hsperi0_fw_tz_s", "HSPERI0 secure 位图，见 §4.3"),
        ("reg_hsperi1_fw_tz_s", "HSPERI1 secure 位图，见 §4.4"),
        ("reg_rom_fw_s_tz_s", "ROM 24 分区 secure 位图"),
        ("fabFW_ROM_psmsk", "ROM read lock post-mask"),
    ]:
        if n in regs:
            lines.extend(reg_section(regs, n, extra))

    lines.extend(["### 3.3 调试与其它", ""])
    for n in ["illegal_slave_space_access_info_l", "illegal_slave_space_access_info_h",
              "fabFW_dbgbus_lock", "fabFW_postmsk_ctrl", "C906B_postmsk_ctrl"]:
        if n in regs:
            extra = "非法从空间访问日志低/高 32 位" if "illegal" in n else ""
            lines.extend(reg_section(regs, n, extra))

    lines.extend([
        "## 4. bmtest 命令与寄存器位映射",
        "",
        "### 4.1 `top_axi_fab_secure <index>` → `fabFW_top_s_tz_s`",
        "",
        f"- 寄存器：`{fmt_addr(regs['fabFW_top_s_tz_s']['offset'])}`",
        "- 每位为 1 表示对应 TOP AXI slave 设为 secure",
        "",
        "| Index | 位 | 名称 |",
        "|-------|----|------|",
    ])
    for idx, name in top_axi_map:
        lines.append(f"| {idx} | bit{idx} | {name} |")

    lines.extend([
        "",
        "### 4.2 `peri_secure <index>` → `reg_peri_fw_s_tz_s`",
        "",
        f"- 寄存器：`{fmt_addr(regs['reg_peri_fw_s_tz_s']['offset'])}`",
        "- 测试地址 = PERI 子系统基址 + offset（下表为官方 xlsx 探测地址）",
        "- 写探针值：`0x87654321`（bmtest 预设）",
        "",
        "| Index | 名称 | 探测地址 | reg_peri_fw 位 | 备注 |",
        "|-------|------|----------|----------------|------|",
    ])
    for item in peri_test_map:
        idx, name, addr = item[0], item[1], item[2]
        note = item[3] if len(item) > 3 else ""
        # find bit from peri_fw by IP name heuristic
        bit = "-"
        for p in peri_fw:
            if name.replace("PERI_", "") in p["ip"].upper().replace(" ", "") or p["ip"].upper() in name:
                bit = str(p["bit"])
                break
        lines.append(f"| {idx} | {name} | `{addr}` | bit {bit} | {note} |")

    lines.extend([
        "",
        "### 4.3 `hsperi_secure 1 <index>` → `reg_hsperi0_fw_tz_s`",
        "",
        f"- 寄存器：`{fmt_addr(regs['reg_hsperi0_fw_tz_s']['offset'])}`",
        "",
        "| Index | 名称 | tz_s 位 | hsperi_fw 描述 | 备注 |",
        "|-------|------|---------|----------------|------|",
    ])
    hsperi_desc = {b: d for b, d in hsperi_fw}
    for item in hsperi0_test:
        idx, name, bit = item[0], item[1], item[2]
        note = item[3] if len(item) > 3 else ""
        desc = hsperi_desc.get(bit, "-")
        lines.append(f"| {idx} | {name} | bit{bit} | {desc} | {note} |")

    lines.extend([
        "",
        "### 4.4 `hsperi_secure 0 <index>` → `reg_hsperi1_fw_tz_s`",
        "",
        f"- 寄存器：`{fmt_addr(regs['reg_hsperi1_fw_tz_s']['offset'])}`",
        "",
        "| Index | 名称 | tz_s 位 | 说明 |",
        "|-------|------|---------|------|",
    ])
    for item in hsperi1_test:
        idx, name, bit = item[0], item[1], item[2]
        lines.append(f"| {idx} | {name} | bit{bit} | HSPERI1 从设备 |")

    lines.extend([
        "",
        "### 4.5 `dram_secure_region <0-7>` → DDR 防火墙",
        "",
        f"- 模块基址：`0x{DDR_FW_BASE:08X}`（`SE_DDR_FW`）",
        "- bmtest 默认探测：`0x108000000`，EL3 写 `0x76543210` / `0xFEDCB A98`",
        "",
        "| 寄存器（相对偏移） | 典型绝对地址* | 位/字段 | 用途 |",
        "|-------------------|--------------|---------|------|",
        "| `+0x00` region_ctrl | `0x33040000` | bit0 enable; bit16 lock | 使能 region N |",
        "| `+0x08 + N*0x20` start | region0: `+0x08` | [31:0] addr>>12 | 区域起始（4KB 对齐） |",
        "| `+0x28 + N*0x20` end | region0: `+0x28` | [31:0] addr>>12 | 区域结束 |",
        "",
        "*参考 `testcase_security.c` 中 region0 写法：`0x020A0000`=ctrl，`0x020A0008`=start，`0x020A0028`=end；Athena2 请以 bmtest log 打印为准。",
        "",
        "| Index | 命令 | 说明 |",
        "|-------|------|------|",
    ])
    for i in range(8):
        lines.append(f"| {i} | `dram_secure_region {i}` | DDR secure region {i} |")

    lines.extend([
        "",
        "### 4.6 `dram_obfuscation 0`",
        "",
        "- 同一 DDR 防火墙模块内混淆开关寄存器（具体偏移见 bmtest log / SPEC）",
        "- 仅 EL3 测试：混淆 ON 读值 ≠ 明文，OFF 读值 == 明文",
        "",
        "### 4.7 ROM 相关命令",
        "",
        f"- `reg_rom_fw_s_tz_s`：`{fmt_addr(regs['reg_rom_fw_s_tz_s']['offset'])}`，bit N = region N secure",
        f"- `fabFW_ROM_psmsk`：`{fmt_addr(regs['fabFW_ROM_psmsk']['offset'])}`，读锁定掩码",
        "",
        "| 命令 | Index | 基地址 | 寄存器位 |",
        "|------|-------|--------|----------|",
    ])
    for i in range(24):
        skip = "SKIP" if i == 15 else ""
        lines.append(f"| `rom_secure_region {i}` | {i} | `{rom_regions[i]}` | `reg_rom_fw_s_tz_s` bit{i} | {skip} |")
    lines.append("| `rom_read_lock <i>` | 0-23 | 同上 | `fabFW_ROM_psmsk` bit<i> | |")
    lines.append("| `rom_define_region 0` | - | `0x29400400`（读 `0x29400800`） | 用户自定义区 | |")

    lines.extend([
        "",
        "## 5. 位语义速查",
        "",
        "| 后缀 | 方向 | 值=0 | 值=1 |",
        "|------|------|------|------|",
        "| `_ar_ns` / `_aw_ns` | Master | 强制 secure 访问 | 允许非安全访问 |",
        "| `_tz_s` | Slave | 非安全可访问（视策略） | Slave 标记为 secure |",
        "| `reg_*_fw_tz_s` 位图 | Slave 组 | 对应 IP 非 secure | 对应 IP secure |",
        "| `fabFW_ROM_psmsk` | ROM | - | 读锁定 post-mask |",
        "",
        "## 6. 辅助测试建议",
        "",
        "### 6.1 判定存疑时",
        "",
        "1. EL3 用 `rm` 读目标寄存器/内存，记录真值",
        "2. `switch_el1` 后再次 `rm` 同一地址",
        "3. 若仍相同，读 `illegal_slave_space_access_info_l/h` 检查是否有非法访问记录",
        "4. 读 `fabFW_hsperi_m_ar_ns` 确认 master 配置是否如预期",
        "",
        "### 6.2 挂死恢复",
        "",
        "- 优先 `reset`（bmtest 命令）",
        "- 无效则硬件复位，从下一条未测用例继续",
        "",
        "### 6.3 与头文件差异",
        "",
        "- `reg_sec_fab_firewall.h` 为较早版本，**PERI/HSPERI 寄存器偏移与 Athena2 xls 不一致**",
        "- 测试与辅助验证 **以 `reg_sec_fab_Athena2.xls` + memory map 为准**",
        "- 例：头文件 `reg_peri_fw_s_tz_s` 在 `+0x54`，Athena2 在 `+0x3C`",
        "",
        "## 7. 完整 hsperi0 位图（reg_hsperi0_fw_tz_s）",
        "",
        "| 位 | 映射 |",
        "|----|------|",
    ])
    for bit, desc in hsperi_fw:
        lines.append(f"| {bit} | {desc} |")

    lines.extend([
        "",
        "## 8. PERI 位图摘录（reg_peri_fw_s_tz_s）",
        "",
        "| 位 | 起始地址 | IP |",
        "|----|----------|-----|",
    ])
    seen = set()
    for p in peri_fw:
        if p["bit"] in seen:
            continue
        seen.add(p["bit"])
        lines.append(f"| {p['bit']} | `0x{p['start']}` | {p['ip']} |")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"written {OUT}")


if __name__ == "__main__":
    main()
