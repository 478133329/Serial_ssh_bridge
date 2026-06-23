# Security Test Reference

## CLI 协议

| 项目 | 值 |
|------|-----|
| 进入 CLI | 启动后等待 `Input 'q' or any key`，发送非 `q` 字符（推荐 `\n`） |
| Prompt | `$ ` |
| 退出 CLI | 发送 `exit` 或 Ctrl+C |

### 常用命令

| 命令 | 参数 | 说明 |
|------|------|------|
| `peri_secure` | `<index>` | PERI 防火墙非安全访问测试 |
| `hsperi_secure` | `<is_hsperi0> <index>` | HSPERI 防火墙非安全访问测试 |
| `top_axi_fab_secure` | `<index>` | TOP AXI fabric 防火墙测试 |
| `axi_hsperi_secure` | `<index>` | HSPERI AXI slave 防火墙测试 |
| `reset` | 无 | 系统复位（`cv_system_reset`） |
| `current_el` | 无 | 查看当前异常级别 |
| `switch_el1` | 无 | EL3 跳入非安全 EL1 |
| `rm` | `<hex_addr>` | 读 32 位内存/寄存器 |
| `wm` | `<hex_addr> <hex_val>` | 写 32 位内存/寄存器 |
| `illegal_slave_access_info` | `<任意>` | 查看非法访问日志 |
| `help` | 无 | 命令列表 |

原语命令灵活组合用法见 [flexible_test.md](flexible_test.md)。

## 串口与烧录

串口连接、固件烧录流程见 [se9_uartdl_skill.md](../se9_uartdl_skill.md)。

编译产物路径：`cvi_bmtest/athena2/out/athena2_ASIC_security.bin`

## EL3→EL1 约束

- `switch_el3_to_el1()` 跳入非安全 EL1 后，部分 IP 访问会导致系统挂死
- **每个 IP 必须独立一轮**：测试 → 解析 log → `reset` → 等待重启 → 重新进入 CLI
- 若系统挂死无法送达 `reset`，记录 PASS(BLOCKED)，硬件复位后从下一条继续

## 判定规则

**固件 log 不会输出 PASS/FAIL**。Agent 根据防火墙开启前后读取到的寄存器值推断防火墙是否生效。

### 通用原则

四套测试分两类，**不要混用判定逻辑**：

| 类型 | 套件 | EL3 行为 | 防火墙/保护生效时表现 |
|------|------|----------|----------------------|
| **写探针** | peri_secure、top_axi_fab_secure | 安全态可正常写/读 | 探针值**未穿透**（EL1 读回 ≠ 探针） |
| **读对比** | hsperi_secure、axi_hsperi_secure、rom_secure_region、rom_read_lock、rom_define_region、dram_secure_region | 安全态读到**真实值** | EL1 读值 **≠** EL3 读值，或中断/挂死 |
| **混淆验证** | dram_obfuscation | EL3 写明文后切换混淆开/关 | 混淆开启时读值 ≠ 明文；关闭时读值 == 明文 |

1. 提取 **EL3、切换 EL1 前** 的读值 → `EL3读值`
2. 提取 **EL1 非安全态访问后** 的读值 → `EL1读值`
3. **读对比类**：EL3 ≠ EL1 → PASS（防火墙生效）；EL3 == EL1 → FAIL（非安全读穿透）
4. **写探针类**：EL1 读回 ≠ 探针值 → PASS；EL1 读回 == 探针值 → FAIL
5. 任意套件：超时挂死 → **PASS(BLOCKED)**；出现 `INT: recv interrupt` → **PASS**

### peri_secure

EL1 非安全态向 secure 区域写入探针 `0x87654321`。

| 结果 | 条件 |
|------|------|
| **PASS** | EL1 读回值 `!= 0x87654321` |
| **FAIL** | EL1 读回值 `== 0x87654321`（写穿透） |
| **PASS(BLOCKED)** | 命令超时无 prompt（访问挂死） |

```
Before switch, CurrentEL=3
  peri_fw [0x........]=0x........    ← EL3 读值
After switch, CurrentEL=...
  peri_fw [0x........]=0x........    ← EL1 写后读值
```

### hsperi_secure（读对比类）

EL3 安全态读取真实值，切换 EL1 后非安全态再次读取。防火墙生效时，EL1 应读到**与 EL3 不同的错误值**（如 `0x14000042` 等 bus error 模式）。

| 结果 | 条件 |
|------|------|
| **PASS** | EL1 读值 **≠** EL3 读值，或出现 `INT: recv interrupt` |
| **FAIL** | EL1 读值 **==** EL3 读值且无中断（非安全读穿透，防火墙未生效） |
| **PASS(BLOCKED)** | 命令超时（访问挂死） |
| **SKIP** | hsperi0 index=9（UART0）默认跳过 |

```
Before switch, CurrentEL=3
  peri_fw [0x........]=0x........    ← EL3 读值（真实值）
After switch, CurrentEL=...
  peri_fw [0x........]=0x........    ← EL1 读值（应与 EL3 不同）
```

### top_axi_fab_secure

EL3 写探针 `0x11111111` 后切换 EL1 再读回。

| 结果 | 条件 |
|------|------|
| **PASS** | EL1 `el1 access peri_fw` 读值 `!= 0x11111111` |
| **FAIL** | EL1 读值 `== 0x11111111`（非安全访问穿透） |
| **PASS(BLOCKED)** | 命令超时（访问挂死） |

```
Before switch, CurrentEL=3
  hperi_fw [0x........]=0x........    ← EL3 切换前读值
  peri_fw [0x........]=0x........     ← EL3 写探针后读值
After switch, CurrentEL=...
 el1 access peri_fw [0x........]=0x.. ← EL1 读值
```

### axi_hsperi_secure（读对比类）

与 hsperi_secure 相同逻辑：EL3 读真实值，EL1 非安全读应得到不同值。

| 结果 | 条件 |
|------|------|
| **PASS** | EL1 读值 **≠** EL3 读值，或中断，或访问挂死（BLOCKED） |
| **FAIL** | EL1 读值 **==** EL3 读值且无中断 |
| **PASS** | index=1 APSYS_ctrl 允许非安全读，正常完成即 PASS（例外） |
| **SKIP** | index=0（地址为 0） |

```
Before switch, CurrentEL=3
  slave : 0x........, value : 0x........    ← EL3 读值
After switch, CurrentEL=...
  slave : 0x........, value : 0x........    ← EL1 读值
```

### dram_secure_region（读对比类，DDR 防火墙）

- 测试地址：`0x108000000`（4KB secure region）
- EL3 配置 region 0–7 之一，写入 `0x76543210` / `0xfedcba98`，切换 EL1 后**只读** secure 区
- 另打印 dirty region `0x100010000`（参考用，**判定以 secure 区为准**）
- IRQ 63：`INT: recv interrupt` 表示 DDR 防火墙触发

| 结果 | 条件 |
|------|------|
| **PASS** | EL1 读 `dram [0x108000000]` **≠** EL3 切换前最后读值，或中断，或挂死 |
| **FAIL** | EL1 读值 **==** EL3 读值且无中断（非安全读穿透） |
| **PASS(BLOCKED)** | 命令超时 |

```
Before switch, CurrentEL=3
  dram [0x108000000]=0x76543210    ← EL3 写后读值（基准）
  dram [0x108000000+4]=0xfedcba98
After switch, CurrentEL=...
  dram [0x108000000]=0x........    ← EL1 读值（应与 EL3 不同）
  dram [0x108000000+4]=0x........
```

### dram_obfuscation（混淆验证类，仅 EL3）

- **不切换 EL1**，整条命令在 EL3 完成
- 测试地址：`0x110000000`
- EL3 写明文 `0x76543210` / `0xfedcba98`，然后三次读回（混淆开 → 混淆关 → 混淆开）

| 结果 | 条件 |
|------|------|
| **PASS** | 混淆**关闭**时读值 == 明文；混淆**开启**时读值 ≠ 明文 |
| **FAIL** | 混淆开启时仍读到明文，或混淆关闭时读不到明文 |

```
  dram [0x110000000]=0x........    ← 第1次：混淆 ON（应 ≠ 0x76543210）
  dram [0x110000000]=0x........    ← 第2次：混淆 OFF（应 == 0x76543210）
  dram [0x110000000]=0x........    ← 第3次：混淆 ON（应 ≠ 0x76543210）
```

### rom_secure_region（读对比类，ROM TZ 安全区）

- 24 个 ROM 块（index 0–23），每块 8KB，基址从 `0x29400000` 步进 `0x2000`
- 配置 `rom_fw_s_tz_s` 位后切 EL1 再读 `rom_fab [addr]`
- IRQ 139：`INT: recv interrupt`

| 结果 | 条件 |
|------|------|
| **PASS** | EL1 `rom_fab` 读值 **≠** EL3 切换前最后 `rom_fab` 读值，或中断，或挂死 |
| **FAIL** | EL1 读值 **==** EL3 读值且无中断 |

```
Before switch, CurrentEL=3
  rom_fab [0x........]=0x........    ← EL3 配置后最后读值
After switch, CurrentEL=...
  rom_fab [0x........]=0x........    ← EL1 读值
```

### rom_read_lock（读对比类，ROM 读锁）

- 与 rom_secure_region 相同 24 个地址
- 配置 `fabFW_ROM_psmsk` 读锁位后切 EL1 再读
- 使用 `rom_firewall_irq_handler`，中断 log 为 `INT: recv interrupt`

判定逻辑与 `rom_secure_region` 相同。

### rom_define_region（读对比类，用户自定义 ROM 区）

- **单条命令**，参数被忽略，建议 `rom_define_region 0`
- 关注 `rom_fab [0x29400400]` 行（源码实际读地址 `0x29400800`，以 log 数值为准）

| 结果 | 条件 |
|------|------|
| **PASS** | EL1 读值 **≠** EL3 切换前 `rom_fab [0x29400400]` 读值，或中断 |
| **FAIL** | EL1 读值 **==** EL3 读值且无中断 |

```
Before switch, CurrentEL=3
  rom_fab [0x29400400]=0x........    ← EL3（读 0x29400800）
After switch, CurrentEL=...
  rom_fab [0x29400400]=0x........    ← EL1（读 0x29400800）
```

## Log 解析示例

Agent 从串口 log 手工提取读值并判定，示例：

**peri_secure 0 — PASS**：
```
  peri_fw [0x27113000]=0x00000001    ← EL3
After switch, CurrentEL=1
  peri_fw [0x27113000]=0x00000001    ← EL1，!= 0x87654321 → PASS
```

**peri_secure 0 — FAIL**：
```
  peri_fw [0x27113000]=0x87654321    ← EL1 写穿透 → FAIL
```

**hsperi_secure 1 0 — PASS**（EL3 ≠ EL1，防火墙生效）：
```
  peri_fw [0x29210000]=0x7           ← EL3 读值
After switch, CurrentEL=1
  peri_fw [0x29210000]=0x14000042    ← EL1 读值不同 → PASS
```

**hsperi_secure — FAIL**（EL3 == EL1，非安全读穿透）：
```
  peri_fw [0x29400000]=0x14000042    ← EL3
  peri_fw [0x29400000]=0x14000042    ← EL1 相同 → FAIL
```

**top_axi_fab_secure 0 — PASS**：
```
  hperi_fw [0x28000000]=0x........    ← EL3 切换前
  peri_fw [0x28000000]=0x11111111     ← EL3 写探针后
 el1 access peri_fw [0x28000000]=0x0  ← EL1，!= 0x11111111 → PASS
```

**axi_hsperi_secure 2 — PASS(BLOCKED)**：发送命令后无 `$ ` prompt 返回，系统挂死。

**dram_secure_region 0 — PASS**：
```
  dram [0x108000000]=0x76543210    ← EL3
After switch, CurrentEL=1
  dram [0x108000000]=0x00000000    ← EL1 不同 → PASS
```

**dram_obfuscation 0 — PASS**：
```
  dram [0x110000000]=0xa1b2c3d4    ← 混淆 ON，≠ 0x76543210
  dram [0x110000000]=0x76543210    ← 混淆 OFF，== 明文
  dram [0x110000000]=0xe5f6a7b8    ← 混淆 ON，≠ 明文
```

**rom_secure_region 0 — PASS**：
```
  rom_fab [0x29400000]=0x12345678  ← EL3
After switch, CurrentEL=1
  rom_fab [0x29400000]=0xdeadbeef  ← EL1 不同 → PASS
```

## PERI IP 表（peri_secure index 0–27）

| Index | 名称 | 基地址 |
|-------|------|--------|
| 0 | PERI_INTC3 | 0x27113000 |
| 1 | PERI_INTC2 | 0x27112000 |
| 2 | PERI_INTC1 | 0x27111000 |
| 3 | PERI_INTC0 | 0x27110000 |
| 4 | PERI_OTP | 0x27100000 | 默认 SKIP |
| 5 | PERI_MAILBOX | 0x270F0000 |
| 6 | PERI_SARADC | 0x270E0000 |
| 7 | PERI_TEMPSEN | 0x270D0000 |
| 8 | PERI_PMCTL | 0x270A0000 |
| 9 | PERI_TIMER | 0x27090000 |
| 10 | PERI_PWM4 | 0x27054000 |
| 11 | PERI_PWM3 | 0x27053000 |
| 12 | PERI_PWM2 | 0x27052000 |
| 13 | PERI_PWM1 | 0x27051000 |
| 14 | PERI_PWM0 | 0x27050000 |
| 15 | PERI_EFUSE | 0x27040000 |
| 16 | PERI_KEYSCAN | 0x27030000 |
| 17 | PERI_WGN1 | 0x27021000 |
| 18 | PERI_WGN0 | 0x27020000 |
| 19 | PERI_GPIO5 | 0x27015000 |
| 20 | PERI_GPIO4 | 0x27014000 |
| 21 | PERI_GPIO3 | 0x27013000 |
| 22 | PERI_GPIO2 | 0x27012000 |
| 23 | PERI_GPIO1 | 0x27011000 |
| 24 | PERI_GPIO0 | 0x27010000 |
| 25 | PERI_WDT2 | 0x27002000 |
| 26 | PERI_WDT1 | 0x27001000 |
| 27 | PERI_WDT0 | 0x27000000 |

## HSPERI IP 表

### hsperi0（is_hsperi0=1, index 0–31）

| Index | 名称 | 基地址 | 备注 |
|-------|------|--------|------|
| 0 | HSPERI0_0 | 0x29210000 | |
| 1 | HSPERI0_1 | 0x29200000 | |
| 2 | HSPERI0_2 | 0x291F0000 | |
| 3 | HSPERI0_3 | 0x291E0000 | |
| 4 | HSPERI0_4 | 0x291D0000 | |
| 5 | HSPERI0_5 | 0x291C0000 | |
| 6 | HSPERI0_6 | 0x291B0000 | |
| 7 | HSPERI0_7 | 0x291A0000 | |
| 8 | HSPERI0_8 | 0x29190000 | |
| 9 | HSPERI0_UART0 | 0x29180000 | uart0 no output，默认 SKIP |
| 10 | HSPERI0_10 | 0x29178000 | |
| 11 | HSPERI0_11 | 0x29170000 | |
| 12 | HSPERI0_12 | 0x29160000 | |
| 13 | HSPERI0_13 | 0x29150000 | |
| 14 | HSPERI0_14 | 0x29140000 | |
| 15 | HSPERI0_15 | 0x29130000 | |
| 16 | HSPERI0_16 | 0x29120000 | |
| 17 | HSPERI0_17 | 0x29110000 | |
| 18 | HSPERI0_18 | 0x29100000 | |
| 19 | HSPERI0_19 | 0x290F0000 | |
| 20 | HSPERI0_20 | 0x290E0000 | |
| 21 | HSPERI0_21 | 0x290D0000 | |
| 22 | HSPERI0_22 | 0x29090000 | |
| 23 | HSPERI0_23 | 0x29080000 | |
| 24 | HSPERI0_24 | 0x29070000 | |
| 25 | HSPERI0_25 | 0x29060000 | |
| 26 | HSPERI0_26 | 0x29050000 | |
| 27 | HSPERI0_27 | 0x29040000 | |
| 28 | HSPERI0_28 | 0x29030000 | |
| 29 | HSPERI0_29 | 0x29020000 | |
| 30 | HSPERI0_30 | 0x29010000 | |
| 31 | HSPERI0_31 | 0x29000000 | |

### hsperi1（is_hsperi0=0, index 0–10）

| Index | 名称 | 基地址 |
|-------|------|--------|
| 0 | HSPERI1_0 | 0x29400000 |
| 1 | HSPERI1_1 | 0x29350000 |
| 2 | HSPERI1_2 | 0x29340000 |
| 3 | HSPERI1_3 | 0x29330004 |
| 4 | HSPERI1_4 | 0x29320004 |
| 5 | HSPERI1_5 | 0x29310004 |
| 6 | HSPERI1_6 | 0x29300004 |
| 7 | HSPERI1_7 | 0x29250000 |
| 8 | HSPERI1_8 | 0x29240000 |
| 9 | HSPERI1_9 | 0x29230000 |
| 10 | HSPERI1_10 | 0x29220000 |

## TOP AXI IP 表（top_axi_fab_secure index 0–7）

| Index | 名称 | 基地址 | 备注 |
|-------|------|--------|------|
| 0 | TOP_AXI_X2P | 0x28000000 | 安全区访问数据出错 |
| 1 | VIP_CTRL_VI | 0x68000000 | |
| 2 | VIP_CTRL_VO | 0x67000000 | |
| 3 | VIDEO_CTRL_VD1 | 0x24000000 | |
| 4 | VIDEO_CTRL_VD0 | 0x23000000 | |
| 5 | VIDEO_CTRL_VE | 0x21000000 | |
| 6 | DDR_CTRL_32K | 0x6FFF0000 | |
| 7 | DDR_CTRL_256M | 0x70000000 | |

## AXI HSPERI Slave 表（axi_hsperi_secure index 0–14）

| Index | 名称 | 基地址 | 备注 |
|-------|------|--------|------|
| 0 | RESERVED | 0x00000000 | 跳过 |
| 1 | APSYS_ctrl | 0x36000000 | 允许非安全读 |
| 2 | SSPERI_ctrl | 0x20000000 | 非安全访问卡住 |
| 3 | USBSYS_ctrl | 0x39000000 | 非安全访问卡住 |
| 4 | RTC_SYS_ctrl | 0x05020000 | 非安全访问卡住 |
| 5 | HSPERI_ctrl | 0x29000000 | EL3 跳 EL1 会卡住 |
| 6 | DBG_SYS | 0x28000000 | 非安全访问卡住 |
| 7 | SYS_ctrl | 0x28100000 | 非安全访问卡住 |
| 8 | PERI | 0x27000000 | 非安全访问卡住 |
| 9 | VE_ctrl | 0x21000000 | 非安全访问卡住 |
| 10 | VD1_ctrl | 0x24000000 | 非安全访问卡住 |
| 11 | VD0_ctrl | 0x23000000 | 非安全访问卡住 |
| 12 | Vi_ctrl | 0x68000000 | 非安全访问卡住 |
| 13 | Vo_ctrl | 0x67000000 | 非安全访问卡住 |
| 14 | DDR_ctrl | 0x6FFF0000 | 非安全访问卡住 |

## 固件编译

```bash
cd cvi_bmtest/athena2
bash build_scripts/build_security.sh
# 等价: make clean; make TEST_CASE=security RUN_ENV=DDR BOARD=ASIC
```

烧录与串口连接见 [se9_uartdl_skill.md](../se9_uartdl_skill.md)。

## 故障排查

| 现象 | 处理 |
|------|------|
| 串口无响应 | 按 se9_uartdl_skill 检查 SSH 2222 桥接或 COM 口 |
| reset 后未回到 CLI | 等待更长时间，确认固件自动启动 |
| 系统挂死 | 记录结果，提示手动完成硬件复位，从下一条未测用例继续 |
| 编译失败 | 确认交叉编译工具链和 BOARD=ASIC 环境 |
