# Security Test Reference

## 常用命令

| 命令 | 参数 | 说明 | 示例 |
|------|------|------|------|
| `peri_secure` | `<index>` | PERI 防火墙：EL3 写探针，EL1 读回 | `peri_secure 0` |
| `hsperi_secure` | `<is_hsperi0> <index>` | HSPERI 防火墙：EL3/EL1 读对比 | `hsperi_secure 1 0` |
| `dram_secure_region` | `<0-7>` | DDR secure region | `dram_secure_region 0` |
| `dram_obfuscation` | `0` | DDR 混淆（仅 EL3） | `dram_obfuscation 0` |
| `rom_secure_region` | `<0-23>` | ROM secure region | `rom_secure_region 0` |
| `rom_read_lock` | `<0-23>` | ROM 读锁定 | `rom_read_lock 0` |
| `rom_define_region` | `0` | 用户自定义 ROM 区 | `rom_define_region 0` |
| `reset` | 无 | 系统复位 | `reset` |
| `current_el` | 无 | 查看当前异常级别 | `current_el` |
| `switch_el1` | 无 | EL3 跳入非安全 EL1 | `switch_el1` |
| `help` | 无 | 命令列表 | `help` |
| `wm` | `<addr> <data>` | 写内存/寄存器 | `wm 0x33030004 0x7FD` |
| `rm` | `<addr>` | 读内存/寄存器 | `rm 0x3303003C` |

### EL3 → EL1 约束

- `switch_el1` 跳入非安全 EL1 后，部分 IP 访问会导致系统挂死
- **每个用例独立一轮**：测试 → 解析 log → `reset` → 等待重启 → 重新进入 CLI
- 挂死后不要用 Ctrl+C，只能 `reset` 或硬件复位

---

## 防火墙通用配置（源自 `testcase_security.c`）

典型顺序（`peri_secure` / `hsperi_secure` / `dram_secure_region` 等 bmtest 命令内部亦遵循）：

1. 配置 **Master** `fabFW_hsperi_m_ar_ns`（偏移 `+0x04`，CA53 为 **bit1**）
2. 配置 **Slave secure** 位图（`reg_peri_fw_s_tz_s` / `reg_hsperi0_fw_tz_s` 等）
3. EL3 访问目标地址（写探针或读真值）
4. `switch_el1`
5. EL1 再次访问，检查是否被阻断

### Master `fabFW_hsperi_m_ar_ns` 位语义（以源码为准）

头文件 `reg_sec_fab_firewall.h` 中该字段复位值为 `h1`（各 bit 默认为 1）。

`testcase_security.c` 注释为 **Remove CA53 forced secure read**，写入：

```c
mmio_write_32(FAB_FIREWALL_BASE + SEC_FAB_FIREWALL_FABFW_HSPERI_M1_AR_NS, 0x000007FD);
```

即 **清除 bit1**（`0x7FF & ~0x2`），使 CA53（master1）读通道不再被强制为 secure。

| bit 值 | 含义（本芯片实现） |
|--------|-------------------|
| **1** | 强制 secure 读（master 以 secure 身份发起读） |
| **0** | 允许非安全读（配合 `switch_el1` 后由非安全 CPU 访问） |

> 注意：字段名虽带 `_ns`，实现上 **bit=1 表示强制 secure**，与字面相反；**以 `testcase_security.c` 注释和写值为准**。

### Slave `*_tz_s` 位语义

| bit 值 | 含义 |
|--------|------|
| **0** | 非 secure（默认） |
| **1** | secure 区域/外设 |

---

## 结果判定

固件 **不打印 PASS/FAIL**，Agent 根据 log 自行推断。

### 共同 log 字段

```
Before switch, CurrentEL=3
  peri_fw [0x........]=0x........    ← EL3 阶段外设/防火墙读值
After switch, CurrentEL=1
  peri_fw [0x........]=0x........    ← EL1 阶段读值
```

SRAM/DDR 测试还会打印：

```
  sec_fab [0x........]=0x........    ← 防火墙寄存器
  sram/dram [0x........]=0x........   ← 探测地址读值
```

---

### 写探针类：`peri_secure`

- EL3 向探测地址写 **`0x87654321`**
- `switch_el1` 后 EL1 读同一地址

| 结果 | 条件 |
|------|------|
| **PASS** | EL1 读值 **≠ `0x87654321`**（写未穿透） |
| **FAIL** | EL1 读值 **== `0x87654321`** |
| **PASS(BLOCKED)** | 命令超时无 prompt（访问挂死） |
| **PASS** | log 含 `INT: recv interrupt` |

辅助验证寄存器：`reg_peri_fw_s_tz_s`（Athena2 偏移见 [security_reg.md](security_reg.md) §4.2）。

---

### 读对比类：`hsperi_secure` / `rom_*` / `dram_secure_region`

- EL3 读取目标寄存器/内存得 **EL3读值**
- `switch_el1` 后 EL1 再读得 **EL1读值**

| 结果 | 条件 |
|------|------|
| **PASS** | EL3读值 **≠** EL1读值 |
| **FAIL** | EL3读值 **==** EL1读值（非安全读穿透） |
| **PASS(BLOCKED)** | 命令超时无 prompt |
| **PASS** | log 含 `INT: recv interrupt` |

存疑时（EL3 == EL1）：**不要立刻判 FAIL**，按下方 [辅助测试流程](#辅助测试流程el3el1-存疑) 复核；任一备用地址 EL3≠EL1、或非法访问日志非零 → 改判 PASS。

辅助验证寄存器：

- HSPERI0：`reg_hsperi0_fw_tz_s`（`0x33030040`）
- HSPERI1：`reg_hsperi1_fw_tz_s`（`0x33030044`）
- 非法访问日志：`illegal_slave_space_access_info_l/h`（`0x3303004C` / `0x33030050`）
- 探测基址：见 [security_reg.md](security_reg.md) §4.3 / §4.4

---

## 辅助测试流程（EL3==EL1 存疑）

正式命令跑完后，若读对比类 **EL3读值 == EL1读值**，或写探针类结果难以解释，Agent **在同一用例内** 追加辅助步骤（仍须 `reset` 后从 EL3 重来）。

### 何时触发

| 套件 | 触发条件 | 说明 |
|------|----------|------|
| `hsperi_secure` / `rom_*` / `dram_secure_region` | 正式 log 中 EL3读值 **==** EL1读值 | 可能是只读寄存器复位值相同（如均为 `0x0`），需换地址或查日志 |
| `peri_secure` | EL1读值 **==** `0x87654321` | 直接 **FAIL**，一般无需辅助 |
| `peri_secure` | EL1读值 ≠ 探针，但与 EL3 读值相同且存疑 | 可手动复现写探针确认 EL3 是否写成功 |

### 地址来源（优先级）

1. **正式 log** 中 `peri_fw [0x........]` / 同类行里的地址（最准）
2. [security_reg.md](security_reg.md) §4.2（peri 探测地址表）
3. [security_reg.md](security_reg.md) §4.3（hsperi0 探测基址，从 memory map 解析）
4. 以上基址的 **备用偏移**（见下表）

### 备用探测偏移

在同一 IP 窗口内，按顺序最多试 **3 个** 备用地址（4 字节对齐）：

| 次序 | 偏移 | 示例（基址 `0x04190000`） |
|------|------|---------------------------|
| 主地址 | `+0x0` | `0x04190000` |
| 备用 1 | `+0x4` | `0x04190004` |
| 备用 2 | `+0x8` | `0x04190008` |
| 备用 3 | `+0x10` | `0x04190010` |

> 禁止跳出该 IP 的 64KB/窗口范围；若全部 EL3==EL1 再查配置与非法访问日志。

### 标准辅助序列（读对比类，以 `hsperi_secure` 为例）

每条辅助尝试前执行 **`reset`**，等待 `$ ` prompt，确认 `current_el` 为 3。

```
# --- 1. 查 index 对应寄存器与位（security_reg.md §4.3）---
# 例：hsperi_secure 1 0 → reg_hsperi0_fw_tz_s bit18，探测基址 0x04190000

# --- 2. 复现防火墙配置（EL3）---
current_el
rm 0x3303004C                    # 读非法日志基线（可选）
wm 0x33030004 0x7FD              # 清除 CA53 强制 secure 读
rm 0x33030040                    # 读当前 hsperi0 tz_s
wm 0x33030040 <old|(1<<bit)>     # 置位目标 slave secure；bit 未知时可写 (1<<bit) 覆盖
rm 0x33030040                    # 确认 tz_s 已置位

# --- 3. EL3 读探测地址 ---
rm <probe_addr>                  # 记录 EL3读值

# --- 4. 切 EL1 再读 ---
switch_el1
current_el                         # 应为 1
rm <probe_addr>                  # 记录 EL1读值

# --- 5. 收尾 ---
reset
```

若主地址 EL3==EL1，**reset 后**对备用地址 `+4`、`+8`、`+0x10` 各重复步骤 2–5（配置可只做一次，但每次 switch_el1 后须 reset 再测下一地址）。

### 写探针类辅助（`peri_secure`）

```
reset
wm 0x33030004 0x7FD
rm 0x3303003C
wm 0x3303003C <old|(1<<bit)>     # bit 见 security_reg.md §4.2
wm <probe_addr> 0x87654321       # EL3 写探针
rm <probe_addr>                  # 确认 EL3 写成功（应读到 0x87654321）
switch_el1
rm <probe_addr>                  # EL1 读回：≠0x87654321 → PASS
reset
```

### 辅助判定（汇总）

| 条件 | 正式结果修正为 |
|------|----------------|
| 任一地址 EL3读值 **≠** EL1读值 | **PASS**（注明辅助地址） |
| `illegal_slave_space_access_info_l/h` 非零 | **PASS**（访问被记录阻断） |
| `fabFW_hsperi_m_ar_ns` bit1 仍为 1（未清） | **待确认** / 配置错误，先 `wm 0x33030004 0x7FD` 重测 |
| `tz_s` 对应 bit 未置 1 | **待确认** / 配置错误，修正后重测 |
| 主地址 + 3 个备用地址均 EL3==EL1，且配置正确 | **FAIL** |
| `switch_el1` 后无 prompt（挂死） | **PASS(BLOCKED)** |
| log 含 `INT: recv interrupt` | **PASS** |

### 报告要求

在 [report_template.md](../templates/report_template.md)「辅助验证记录」中填写：正式命令、尝试地址列表、各地址 EL3/EL1 读值、`tz_s`/`ar_ns`/illegal_slave 读值、最终结论。

---

### 混淆验证：`dram_obfuscation`

- 仅 EL3，不 `switch_el1`
- 混淆 **OFF**：读值 == 明文 `0x76543210`
- 混淆 **ON**：读值 ≠ 明文

---

## 参考文档

| 名称 | 说明 | 路径 |
|------|------|------|
| bmtest 参考源码 | SRAM/DDR 辅助测试范例（非完整 peri/hsperi 实现） | [testcase_security.c](testcase_security.c) |
| 寄存器头文件 | 符号名与 bit 偏移（**偏移以 Athena2 xls 为准**） | [reg_sec_fab_firewall.h](reg_sec_fab_firewall.h) |
| 寄存器映射 | 绝对地址、bmtest index→bit | [security_reg.md](security_reg.md) |
| 测试用例 | 官方表格总结 | [security_testcase.md](security_testcase.md) |
| 批量命令 | Agent 执行清单 | [test_cases.md](../test_cases.md) |

> `references/testcase_security.c` 仅含 `test_ns_access_secure_sram` / `dram` 范例；**`peri_secure` / `hsperi_secure` 的完整实现以固件 bmtest 为准**，寄存器配置规律与范例一致。

---

## 故障排查

| 现象 | 处理 |
|------|------|
| 串口无响应 | 按 uart_skill 检查 SSH 2222 桥接或 COM 口 |
| reset 后未回到 CLI | 等待更长时间，确认固件自动启动 |
| 系统挂死 | 记 PASS(BLOCKED) 或 PENDING，硬件复位后从下一条继续 |
| EL3==EL1 存疑 | 按 [reference.md](reference.md) 辅助测试流程：换 `+4/+8/+0x10` 地址重测，查 illegal_slave 日志 |
| 编译失败 | 确认交叉编译工具链和 BOARD=ASIC 环境 |
