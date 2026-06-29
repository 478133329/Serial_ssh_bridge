# Security 寄存器参考（Athena2）

> 来源：`reg_sec_fab_Athena2.xls`、`reg_sec_fab_firewall.h`、`Athena2_memory_map.xlsx`、`testcase_security.c`
> 供 bmtest 正式测试与 Agent 辅助验证（`rm`/`wm`）使用。

## 1. 模块基地址

| 模块 | 基地址 | 来源 | 用途 |
|------|--------|------|------|
| `sec_fab_firewall` | `0x33030000` | memory map `SE_FAB_FW` | 总线防火墙主控：master/slave TZ、PERI/HSPERI/ROM/TOP |
| `sec_ddr_firewall` | `0x33040000` | memory map `SE_DDR_FW` | DDR secure region / obfuscation |
| PERI 子系统 | `0x03000000` | `peri_fw(1835)` | PERI 外设寄存器窗口 |
| HSPERI 子系统 | `0x04000000` | `HSPERI` sheet | HSPERI 外设寄存器窗口 |
| HSPERI ROM | `0x29400000` | memory map | ROM 分区测试基址 |
| DRAM 测试区 | `0x108000000` | bmtest `dram_secure_region` | DDR secure region 默认探测地址 |

> **注意**：`testcase_security.c` 参考代码中 DDR 寄存器使用 `0x020A0000` 偏移写法，Athena2 memory map 显示 DDR 防火墙在 `0x33040000`。辅助验证时以 **当前固件 bmtest 打印的 `ddr_fab [...]` 地址** 为准。

## 2. 通用测试配置流程

绝大多数防火墙用例遵循相同寄存器操作序列（与官方表格 Initial/Test steps 一致）：

1. **Master 读通道（`fabFW_hsperi_m_ar_ns`）**：清除 CA53（**bit1**）的强制 secure 读，写入 `0x7FD`（见 `testcase_security.c`）
2. **Slave secure 位（`tz_s`）**：将目标外设/区域的对应 bit 置 **1**
3. **EL3** 写探针或读真值
4. **`switch_el1`** 切至非安全 EL1
5. **EL1** 再次访问：预期被阻断（读值变化、挂死或中断）

### 2.1 testcase_security.c 关键写法

```c
// 1) 清除 CA53(master1) 强制 secure 读 — fabFW_hsperi_m_ar_ns bit1 写 0
mmio_write_32(FAB_FIREWALL_BASE + 0x04, 0x000007FD);

// 2) SRAM 设为 secure
mmio_write_32(FAB_FIREWALL_BASE + 0x28, 0xFFFFFFFF);  // reg_sram_s_tz_s

// 3) DDR region0: start/end 4KB 对齐，enable
mmio_write_32(DDR_FW_BASE + 0x08, dram_start >> 12);
mmio_write_32(DDR_FW_BASE + 0x28, dram_end >> 12);
mmio_write_32(DDR_FW_BASE + 0x00, 1UL | (1 << 16));
```

**`fabFW_hsperi_m_ar_ns` 位语义（以 `testcase_security.c` 为准）**：

| bit | 值 | 含义 |
|-----|-----|------|
| bit1（CA53 / master1） | **0** | 允许非安全读（`0x7FD` 清除 bit1） |
| bit1 | **1** | 强制 secure 读（复位默认 `h1`） |

> 字段名带 `_ns`，但本实现中 **bit=1 表示强制 secure**，与字面相反。

### 2.2 辅助验证常用 bmtest 命令

| 场景 | 命令示例 | 说明 |
|------|----------|------|
| 读防火墙配置 | `rm 0x33030004` | 查看 hsperi master ar_ns |
| 读 PERI secure 位图 | `rm 0x3303003C` | `reg_peri_fw_s_tz_s` |
| 读 HSPERI0 位图 | `rm 0x33030040` | `reg_hsperi0_fw_tz_s` |
| 读非法访问日志 | `rm 0x3303004C` / `rm 0x33030050` | `illegal_slave_space_access_info_l/h` |
| 写后回读 | `wm <addr> <val>` 再 `rm <addr>` | 确认配置是否生效 |
| 切 EL | `current_el` / `switch_el1` | 辅助复现 EL3/EL1 读值差异 |

## 3. sec_fab_firewall 寄存器详表

基址：`0x33030000`

### 3.1 控制与 Master 防火墙

#### `reg_fab_fw_ctrl`

- **偏移**：`+0x00` → `0x33030000`
- **说明**：reg_fab_fw_ctrl
- **备注**：全局控制

| 字段 | 位 | 复位 | 读写 | 含义 |
|------|----|------|------|------|
| `reg_fab_fw_ctrl` | [31:0] | h0 | rw | - |

#### `fabFW_hsperi_m_ar_ns`

- **偏移**：`+0x04` → `0x33030004`
- **说明**：master firewall control signal for HSPERI fabric read access
(HSPERI secure master)
- **备注**：HSPERI master 读通道 ns 位，bit1 常对应 CA53

| 字段 | 位 | 复位 | 读写 | 含义 |
|------|----|------|------|------|
| `fabFW_hsperi_m0_ar_ns` | [0:0] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_hsperi_m1_ar_ns` | [1:1] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_hsperi_m2_ar_ns` | [2:2] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_hsperi_m3_ar_ns` | [3:3] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_hsperi_m4_ar_ns` | [4:4] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_hsperi_m5_ar_ns` | [5:5] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_hsperi_m6_ar_ns` | [6:6] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_hsperi_m7_ar_ns` | [7:7] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_hsperi_m8_ar_ns` | [8:8] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_hsperi_m9_ar_ns` | [9:9] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_hsperi_m10_ar_ns` | [10:10] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |

#### `fabFW_hsperi_m_aw_ns`

- **偏移**：`+0x08` → `0x33030008`
- **说明**：master firewall control signal for HSPERI fabric write access
(HSPERI secure master)
- **备注**：HSPERI master 写通道 ns 位

| 字段 | 位 | 复位 | 读写 | 含义 |
|------|----|------|------|------|
| `fabFW_hsperi_m0_aw_ns` | [0:0] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_hsperi_m1_aw_ns` | [1:1] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_hsperi_m2_aw_ns` | [2:2] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_hsperi_m3_aw_ns` | [3:3] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_hsperi_m4_aw_ns` | [4:4] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_hsperi_m5_aw_ns` | [5:5] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_hsperi_m6_aw_ns` | [6:6] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_hsperi_m7_aw_ns` | [7:7] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_hsperi_m8_aw_ns` | [8:8] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_hsperi_m9_aw_ns` | [9:9] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_hsperi_m10_aw_ns` | [10:10] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |

#### `fabFW_ddr_m_ar_ns`

- **偏移**：`+0x14` → `0x33030014`
- **说明**：master firewall control signal for DDR fabric read access 
(from AXI  master can read DDR fabric)
- **备注**：DDR fabric master 读 ns，16 路

| 字段 | 位 | 复位 | 读写 | 含义 |
|------|----|------|------|------|
| `fabFW_ddr_m0_ar_ns` | [0:0] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_ddr_m1_ar_ns` | [1:1] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_ddr_m2_ar_ns` | [2:2] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_ddr_m3_ar_ns` | [3:3] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_ddr_m4_ar_ns` | [4:4] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_ddr_m5_ar_ns` | [5:5] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_ddr_m6_ar_ns` | [6:6] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_ddr_m7_ar_ns` | [7:7] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_ddr_m8_ar_ns` | [8:8] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_ddr_m9_ar_ns` | [9:9] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_ddr_m10_ar_ns` | [10:10] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_ddr_m11_ar_ns` | [11:11] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_ddr_m12_ar_ns` | [12:12] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_ddr_m13_ar_ns` | [13:13] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_ddr_m14_ar_ns` | [14:14] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_ddr_m15_ar_ns` | [15:15] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |

#### `fabFW_ddr_m_aw_ns`

- **偏移**：`+0x18` → `0x33030018`
- **说明**：master firewall control signal for DDR fabric write access 
(from AXI  master can write DDR fabric)
- **备注**：DDR fabric master 写 ns

| 字段 | 位 | 复位 | 读写 | 含义 |
|------|----|------|------|------|
| `fabFW_ddr_m0_aw_ns` | [0:0] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_ddr_m1_aw_ns` | [1:1] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_ddr_m2_aw_ns` | [2:2] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_ddr_m3_aw_ns` | [3:3] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_ddr_m4_aw_ns` | [4:4] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_ddr_m5_aw_ns` | [5:5] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_ddr_m6_aw_ns` | [6:6] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_ddr_m7_aw_ns` | [7:7] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_ddr_m8_aw_ns` | [8:8] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_ddr_m9_aw_ns` | [9:9] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_ddr_m10_aw_ns` | [10:10] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_ddr_m11_aw_ns` | [11:11] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_ddr_m12_aw_ns` | [12:12] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_ddr_m13_aw_ns` | [13:13] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_ddr_m14_aw_ns` | [14:14] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_ddr_m15_aw_ns` | [15:15] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |

#### `fabFW_tpu0_m_ar_ns`

- **偏移**：`+0x30` → `0x33030030`
- **说明**：master firewall control signal for TPU fabric read access
- **备注**：TPU master 读 ns

| 字段 | 位 | 复位 | 读写 | 含义 |
|------|----|------|------|------|
| `fabFW_tpu0_m0_ar_ns` | [0:0] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_tpu0_m1_ar_ns` | [1:1] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_tpu0_m2_ar_ns` | [2:2] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_tpu0_m3_ar_ns` | [3:3] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |

#### `fabFW_tpu0_m_aw_ns`

- **偏移**：`+0x34` → `0x33030034`
- **说明**：master firewall control signal for TPU fabric write access
- **备注**：TPU master 写 ns

| 字段 | 位 | 复位 | 读写 | 含义 |
|------|----|------|------|------|
| `fabFW_tpu0_m0_aw_ns` | [0:0] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_tpu0_m1_aw_ns` | [1:1] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_tpu0_m2_aw_ns` | [2:2] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_tpu0_m3_aw_ns` | [3:3] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |

#### `fabFW_RTC_ar_ns`

- **偏移**：`+0x20` → `0x33030020`
- **说明**：fabFW_RTC_ar_ns
- **备注**：RTC master 读 ns

| 字段 | 位 | 复位 | 读写 | 含义 |
|------|----|------|------|------|
| `fabFW_RTC_ar_ns` | [0:0] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |

#### `fabFW_RTC_aw_ns`

- **偏移**：`+0x24` → `0x33030024`
- **说明**：fabFW_RTC_aw_ns
- **备注**：RTC master 写 ns

| 字段 | 位 | 复位 | 读写 | 含义 |
|------|----|------|------|------|
| `fabFW_RTC_aw_ns` | [0:0] | h1 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |

#### `fabFW_C906B_ns`

- **偏移**：`+0x68` → `0x33030068`
- **说明**：fabFW_C906B_ns
- **备注**：C906B/C906L ar/aw ns

| 字段 | 位 | 复位 | 读写 | 含义 |
|------|----|------|------|------|
| `fabFW_C906B_ar_ns` | [0:0] | h0 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_C906B_aw_ns` | [1:1] | h0 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_C906L_ar_ns` | [2:2] | h0 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |
| `fabFW_C906L_aw_ns` | [3:3] | h0 | rw | bit=1 强制 secure；bit=0 允许非安全（测试时清 CA53 bit1） |

### 3.2 Slave TrustZone（tz_s）

#### `fabFW_hsperi_s_tz_s`

- **偏移**：`+0x0C` → `0x3303000C`
- **说明**：slave protection control singal for HSPERI fabric
(HSPERI fabric secure region for AXI modules)
- **备注**：HSPERI fabric 内部 slave

| 字段 | 位 | 复位 | 读写 | 含义 |
|------|----|------|------|------|
| `fabFW_hsperi_s0_tz_s` | [0:0] | h0 | rw | 1=该 slave 区域设为 secure |
| `fabFW_hsperi_s1_tz_s` | [1:1] | h0 | rw | 1=该 slave 区域设为 secure |
| `fabFW_hsperi_s2_tz_s` | [2:2] | h0 | rw | 1=该 slave 区域设为 secure |
| `fabFW_hsperi_s3_tz_s` | [3:3] | h0 | rw | 1=该 slave 区域设为 secure |
| `fabFW_hsperi_s4_tz_s` | [4:4] | h0 | rw | 1=该 slave 区域设为 secure |
| `fabFW_hsperi_s5_tz_s` | [5:5] | h0 | rw | 1=该 slave 区域设为 secure |
| `fabFW_hsperi_s6_tz_s` | [6:6] | h0 | rw | 1=该 slave 区域设为 secure |
| `fabFW_hsperi_s7_tz_s` | [7:7] | h0 | rw | 1=该 slave 区域设为 secure |
| `fabFW_hsperi_s8_tz_s` | [8:8] | h0 | rw | 1=该 slave 区域设为 secure |
| `fabFW_hsperi_s9_tz_s` | [9:9] | h0 | rw | 1=该 slave 区域设为 secure |
| `fabFW_hsperi_s10_tz_s` | [10:10] | h0 | rw | 1=该 slave 区域设为 secure |
| `fabFW_hsperi_s11_tz_s` | [11:11] | h0 | rw | 1=该 slave 区域设为 secure |
| `fabFW_hsperi_s12_tz_s` | [12:12] | h0 | rw | 1=该 slave 区域设为 secure |
| `fabFW_hsperi_s13_tz_s` | [13:13] | h0 | rw | 1=该 slave 区域设为 secure |
| `fabFW_hsperi_s14_tz_s` | [14:14] | h0 | rw | 1=该 slave 区域设为 secure |

#### `fabFW_ddr_ctrl_s_tz_s`

- **偏移**：`+0x1C` → `0x3303001C`
- **说明**：slave protection control singal for DDR_ctrl fabric
(DDR_CTRL secure region)
- **备注**：DDR controller slave

| 字段 | 位 | 复位 | 读写 | 含义 |
|------|----|------|------|------|
| `fabFW_ddr_ctrl_s0_tz_s` | [0:0] | h0 | rw | 1=该 slave 区域设为 secure |
| `fabFW_ddr_ctrl_s1_tz_s` | [1:1] | h0 | rw | 1=该 slave 区域设为 secure |
| `fabFW_ddr_ctrl_s2_tz_s` | [2:2] | h0 | rw | 1=该 slave 区域设为 secure |
| `fabFW_ddr_ctrl_s3_tz_s` | [3:3] | h0 | rw | 1=该 slave 区域设为 secure |

#### `reg_sram_s_tz_s`

- **偏移**：`+0x28` → `0x33030028`
- **说明**：RTC TZ_s
to ROM_firewall
- **备注**：on-chip SRAM secure 控制

| 字段 | 位 | 复位 | 读写 | 含义 |
|------|----|------|------|------|
| `reg_sram_s_tz_s` | [31:0] | h0 | rw | 1=该 slave 区域设为 secure |

#### `fabFW_ap_s4_tz_s`

- **偏移**：`+0x2C` → `0x3303002C`
- **说明**：slave protection control singal for AP fabric
(AP secure range)
- **备注**：APB slave s4

| 字段 | 位 | 复位 | 读写 | 含义 |
|------|----|------|------|------|
| `fabFW_ap_s4_tz_s` | [4:4] | h0 | rw | 1=该 slave 区域设为 secure |

#### `fabFW_tpu0_s_tz_s`

- **偏移**：`+0x38` → `0x33030038`
- **说明**：slave protection control singal for TPU fabric
- **备注**：TPU SRAM/ctrl 分区

| 字段 | 位 | 复位 | 读写 | 含义 |
|------|----|------|------|------|
| `fabFW_tpu0_s0_tz_s` | [0:0] | h0 | rw | 1=该 slave 区域设为 secure |
| `fabFW_tpu0_s1_tz_s` | [1:1] | h0 | rw | 1=该 slave 区域设为 secure |
| `fabFW_tpu0_s2_tz_s` | [2:2] | h0 | rw | 1=该 slave 区域设为 secure |
| `fabFW_tpu0_s3_tz_s` | [3:3] | h0 | rw | 1=该 slave 区域设为 secure |
| `fabFW_tpu0_s4_tz_s` | [4:4] | h0 | rw | 1=该 slave 区域设为 secure |
| `fabFW_tpu0_s5_tz_s` | [5:5] | h0 | rw | 1=该 slave 区域设为 secure |

#### `fabFW_top_s_tz_s`

- **偏移**：`+0x54` → `0x33030054`
- **说明**：access control by hperi_firewall
- **备注**：TOP AXI fabric slave，见 §4.1

| 字段 | 位 | 复位 | 读写 | 含义 |
|------|----|------|------|------|
| `fabFW_top_s0_tz_s` | [0:0] | h0 | rw | 1=该 slave 区域设为 secure |
| `fabFW_top_s1_tz_s` | [1:1] | h0 | rw | 1=该 slave 区域设为 secure |
| `fabFW_top_s2_tz_s` | [2:2] | h0 | rw | 1=该 slave 区域设为 secure |
| `fabFW_top_s3_tz_s` | [3:3] | h0 | rw | 1=该 slave 区域设为 secure |
| `fabFW_top_s4_tz_s` | [4:4] | h0 | rw | 1=该 slave 区域设为 secure |
| `fabFW_top_s5_tz_s` | [5:5] | h0 | rw | 1=该 slave 区域设为 secure |
| `fabFW_top_s6_tz_s` | [6:6] | h0 | rw | 1=该 slave 区域设为 secure |
| `fabFW_top_s7_tz_s` | [7:7] | h0 | rw | 1=该 slave 区域设为 secure |

#### `reg_peri_fw_s_tz_s`

- **偏移**：`+0x3C` → `0x3303003C`
- **说明**：APB slave firewall control signal for TOP fabric non-AXI slaves
(TOP fabric secure region for non-AXI modules),access control by peri_firewall
RESERVED_ADDR = 36'hf_0000_0000-> exception
- **备注**：PERI 各 slave secure 位图，见 §4.2

| 字段 | 位 | 复位 | 读写 | 含义 |
|------|----|------|------|------|
| `reg_peri_fw_s_tz_s` | [31:0] | h0 | rw | 1=该 slave 区域设为 secure |

#### `reg_hsperi0_fw_tz_s`

- **偏移**：`+0x40` → `0x33030040`
- **说明**：APB slave firewall control signal for HSPERI fabric non-AXI slaves
(HSPERI fabric secure region for non-AXI modules)
RESERVED_ADDR = 36'hf_0000_0000-> exception
- **备注**：HSPERI0 secure 位图，见 §4.3

| 字段 | 位 | 复位 | 读写 | 含义 |
|------|----|------|------|------|
| `reg_hsperi0_fw_tz_s` | [31:0] | h0 | rw | 1=该 slave 区域设为 secure |

#### `reg_hsperi1_fw_tz_s`

- **偏移**：`+0x44` → `0x33030044`
- **说明**：APB slave firewall control signal for HSPERI fabric non-AXI slaves
(HSPERI fabric secure region for non-AXI modules)
RESERVED_ADDR = 36'hf_0000_0000-> exception
- **备注**：HSPERI1 secure 位图，见 §4.4

| 字段 | 位 | 复位 | 读写 | 含义 |
|------|----|------|------|------|
| `reg_hsperi1_fw_tz_s` | [31:0] | h0 | rw | 1=该 slave 区域设为 secure |

#### `reg_rom_fw_s_tz_s`

- **偏移**：`+0x58` → `0x33030058`
- **说明**：slave firewall control signal for ROM secure regions
24 regions, 8KB per region,access control by rom_firewall
RESERVED_ADDR =36'h0_2940_0000
- **备注**：ROM 24 分区 secure 位图

| 字段 | 位 | 复位 | 读写 | 含义 |
|------|----|------|------|------|
| `reg_rom_fw_s_tz_s` | [31:0] | h0 | rw | 1=该 slave 区域设为 secure |

#### `fabFW_ROM_psmsk`

- **偏移**：`+0x5C` → `0x3303005C`
- **说明**：slave firewall control signal for ROM post-mask regions (forbidden read access),access control by rom_firewall
24 regions, 8KB per region
(access re-direct to reserved address 36'h0_2940_0000)
- **备注**：ROM read lock post-mask

| 字段 | 位 | 复位 | 读写 | 含义 |
|------|----|------|------|------|
| `fabFW_ROM_psmsk` | [31:0] | h0 | rw | ROM 读锁定 post-mask |

### 3.3 调试与其它

#### `illegal_slave_space_access_info_l`

- **偏移**：`+0x4C` → `0x3303004C`
- **说明**：illegal access info: addr
- **备注**：非法从空间访问日志低/高 32 位

| 字段 | 位 | 复位 | 读写 | 含义 |
|------|----|------|------|------|
| `illegal_slave_space_access_info_l` | [31:0] | h0 | ro | 非法从空间访问日志（RO） |

#### `illegal_slave_space_access_info_h`

- **偏移**：`+0x50` → `0x33030050`
- **说明**：illegal access info: blen,rw（1:w, r:0）
- **备注**：非法从空间访问日志低/高 32 位

| 字段 | 位 | 复位 | 读写 | 含义 |
|------|----|------|------|------|
| `illegal_slave_space_access_info_h` | [31:0] | h0 | ro | 非法从空间访问日志（RO） |

#### `fabFW_dbgbus_lock`

- **偏移**：`+0x60` → `0x33030060`
- **说明**：access lock for debug bus

| 字段 | 位 | 复位 | 读写 | 含义 |
|------|----|------|------|------|
| `fabFW_dbgbus_lock` | [31:0] | h0 | rw | - |

#### `fabFW_postmsk_ctrl`

- **偏移**：`+0x64` → `0x33030064`
- **说明**：fabFW_postmsk_ctrl

| 字段 | 位 | 复位 | 读写 | 含义 |
|------|----|------|------|------|
| `fabFW_postmsk_base` | [8:0] | h0 | rw | - |
| `fabFW_postmsk_size` | [12:9] | h0 | rw | - |
| `fabFW_postmsk_lock` | [13:13] | h0 | rw | - |

#### `C906B_postmsk_ctrl`

- **偏移**：`+0x6C` → `0x3303006C`
- **说明**：C906B_postmsk_ctrl

| 字段 | 位 | 复位 | 读写 | 含义 |
|------|----|------|------|------|
| `C906B_postmsk_base` | [8:0] | h0 | rw | - |
| `C906B_postmsk_size` | [12:9] | h0 | rw | - |
| `C906B_postmsk_lock` | [13:13] | h0 | rw | - |

## 4. bmtest 命令与寄存器位映射

### 4.1 `top_axi_fab_secure <index>` → `fabFW_top_s_tz_s`

- 寄存器：`0x33030054`
- 每位为 1 表示对应 TOP AXI slave 设为 secure

| Index | 位 | 名称 |
|-------|----|------|
| 0 | bit0 | TOP_AXI_X2P |
| 1 | bit1 | VIP_CTRL_VO |
| 2 | bit2 | VIDEO_CTRL_VD3 |
| 3 | bit3 | VIDEO_CTRL_VD2 |
| 4 | bit4 | VIDEO_CTRL_VD1 |
| 5 | bit5 | VIDEO_CTRL_VD0 |
| 6 | bit6 | VIDEO_CTRL_VE |
| 7 | bit7 | DDR_CTRL_256M / top_north_cfg |

### 4.2 `peri_secure <index>` → `reg_peri_fw_s_tz_s`

- 寄存器：`0x3303003C`
- 测试地址 = 下表探测地址；写探针值：`0x87654321`（bmtest 预设）
- 备用偏移：`+0x4`、`+0x8`、`+0x10`（写探针类一般不必换址；读回均为 `0x87654321` 时直接 FAIL）

| Index | 名称 | 探测地址 | reg_peri_fw 位 | 备注 |
|-------|------|----------|----------------|------|
| 0 | PERI_INTC3 | `0x27113000` | bit - |  |
| 1 | PERI_INTC2 | `0x27112000` | bit - |  |
| 2 | PERI_INTC1 | `0x27111000` | bit - |  |
| 3 | PERI_INTC0 | `0x27110000` | bit - |  |
| 4 | PERI_OTP | `0x27100000` | bit - | SKIP |
| 5 | PERI_MAILBOX | `0x270F0000` | bit - |  |
| 6 | PERI_SARADC | `0x270E0000` | bit 28 |  |
| 7 | PERI_TEMPSEN | `0x270D0000` | bit 27 |  |
| 8 | PERI_PMCTL | `0x27090000` | bit - |  |
| 9 | PERI_TIMER | `0x270A0000` | bit 23 |  |
| 10 | PERI_PWM4 | `0x27064000` | bit - |  |
| 11 | PERI_PWM3 | `0x27063000` | bit 19 |  |
| 12 | PERI_PWM2 | `0x27062000` | bit 19 |  |
| 13 | PERI_PWM1 | `0x27061000` | bit 19 |  |
| 14 | PERI_PWM0 | `0x27060000` | bit 19 |  |
| 15 | PERI_EFUSE | `0x27050000` | bit 18 |  |
| 16 | PERI_KEYSCAN | `0x27040000` | bit 17 |  |
| 17 | PERI_WGN1 | `0x27031000` | bit 16 |  |
| 18 | PERI_WGN0 | `0x27030000` | bit 16 |  |
| 19 | PERI_GPIO5 | `0x27025000` | bit - |  |
| 20 | PERI_GPIO4 | `0x27024000` | bit - |  |
| 21 | PERI_GPIO3 | `0x27023000` | bit 15 |  |
| 22 | PERI_GPIO2 | `0x27022000` | bit 15 |  |
| 23 | PERI_GPIO1 | `0x27021000` | bit 15 |  |
| 24 | PERI_GPIO0 | `0x27020000` | bit 15 |  |
| 25 | PERI_WDT2 | `0x27010200` | bit - |  |
| 26 | PERI_WDT1 | `0x27010100` | bit - |  |
| 27 | PERI_WDT0 | `0x27010000` | bit - |  |

### 4.3 `hsperi_secure 1 <index>` → `reg_hsperi0_fw_tz_s`

- 寄存器：`0x33030040`
- 探测基址：下表「探测地址」列（HSPERI 子系统窗口内）；**优先以正式 log 打印地址为准**
- 备用偏移：`+0x4`、`+0x8`、`+0x10`（EL3==EL1 存疑时使用，见 §6.4）

| Index | 名称 | 探测地址 | tz_s 位 | 备注 |
|-------|------|----------|---------|------|
| 0 | HSPERI_SPI1 | `0x04190000` | bit18 |  |
| 1 | HSPERI_SPI0 | `0x04180000` | bit17 |  |
| 2 | HSPERI_UART7 | `0x04170000` | bit16 |  |
| 3 | HSPERI_UART6 | `0x04160000` | bit15 |  |
| 4 | HSPERI_UART5 | `0x04150000` | bit14 |  |
| 5 | HSPERI_UART4 | `0x04140000` | bit13 |  |
| 6 | HSPERI_UART3 | `0x04130000` | bit12 |  |
| 7 | HSPERI_UART2 | `0x04120000` | bit11 |  |
| 8 | HSPERI_UART1 | `0x04110000` | bit10 |  |
| 9 | HSPERI_UART0 | `0x04108000` | bit9 | SKIP |
| 10 | HSPERI_I2S_DW | `0x04100000` | bit8 |  |
| 11 | HSPERI_I2S_AUDSRC | `0x040C0000` | bit7 |  |
| 12 | HSPERI_I2S5 | `0x04080000` | bit6 |  |
| 13 | HSPERI_I2S4 | `0x04060000` | bit5 |  |
| 14 | HSPERI_I2S3 | `0x04040000` | bit4 |  |
| 15 | HSPERI_I2S2 | `0x04030000` | bit3 |  |
| 16 | HSPERI_I2S1 | `0x04020000` | bit2 |  |
| 17 | HSPERI_I2S0 | `0x04010000` | bit1 |  |
| 18 | HSPERI_I2S_GLOBAL | `0x04000000` | bit0 |  |
| 19 | HSPERI_ETH1_CFG | `0x04520000` | bit28 |  |
| 20 | HSPERI_ETH0_CFG | `0x04510000` | bit27 |  |
| 21 | HSPERI_SPI_NAND | `0x041C0000` | bit21 |  |
| 22 | HSPERI_I2C9 | `0x20000000` | bit31 |  |
| 23 | HSPERI_I2C8 | `0x10000000` | bit30 |  |
| 24 | HSPERI_I2C7 | `0x0E000000` | bit29 |  |
| 25 | HSPERI_I2C6 | `0x04400000` | bit26 |  |
| 26 | HSPERI_I2C5 | `0x04330000` | bit25 |  |
| 27 | HSPERI_I2C4 | `0x04320000` | bit24 |  |
| 28 | HSPERI_I2C3 | `0x04310000` | bit23 |  |
| 29 | HSPERI_I2C2 | `0x04300000` | bit22 |  |
| 30 | HSPERI_I2C1 | `0x041B0000` | bit20 |  |
| 31 | HSPERI_I2C0 | `0x041A0000` | bit19 |  |

### 4.4 `hsperi_secure 0 <index>` → `reg_hsperi1_fw_tz_s`

- 寄存器：`0x33030044`
- 探测地址：**以正式 log 中 `peri_fw`/`hsperi_fw` 打印地址为准**（控制类 IP，无统一 memory map 基址表）
- 备用偏移：同上 `+4/+8/+0x10`

| Index | 名称 | tz_s 位 | 说明 |
|-------|------|---------|------|
| 0 | HSPERI_ROM | bit26 | HSPERI1 从设备 |
| 1 | HSPERI_SDMA1_CFG | bit25 | HSPERI1 从设备 |
| 2 | HSPERI_SDMA0_CFG | bit24 | HSPERI1 从设备 |
| 3 | HSPERI_SD2_CFG | bit23 | HSPERI1 从设备 |
| 4 | HSPERI_SD1_CFG | bit22 | HSPERI1 从设备 |
| 5 | HSPERI_SD0_CFG | bit21 | HSPERI1 从设备 |
| 6 | HSPERI_EMMC_CFG | bit22 | HSPERI1 从设备 |
| 7 | HSPERI_CAN1 | bit20 | HSPERI1 从设备 |
| 8 | HSPERI_CAN0 | bit19 | HSPERI1 从设备 |
| 9 | HSPERI_SPI3 | bit20 | HSPERI1 从设备 |
| 10 | HSPERI_SPI2 | bit19 | HSPERI1 从设备 |

### 4.5 `dram_secure_region <0-7>` → DDR 防火墙

- 模块基址：`0x33040000`（`SE_DDR_FW`）
- bmtest 默认探测：`0x108000000`，EL3 写 `0x76543210` / `0xFEDCB A98`

| 寄存器（相对偏移） | 典型绝对地址* | 位/字段 | 用途 |
|-------------------|--------------|---------|------|
| `+0x00` region_ctrl | `0x33040000` | bit0 enable; bit16 lock | 使能 region N |
| `+0x08 + N*0x20` start | region0: `+0x08` | [31:0] addr>>12 | 区域起始（4KB 对齐） |
| `+0x28 + N*0x20` end | region0: `+0x28` | [31:0] addr>>12 | 区域结束 |

*参考 `testcase_security.c` 中 region0 写法：`0x020A0000`=ctrl，`0x020A0008`=start，`0x020A0028`=end；Athena2 请以 bmtest log 打印为准。

| Index | 命令 | 说明 |
|-------|------|------|
| 0 | `dram_secure_region 0` | DDR secure region 0 |
| 1 | `dram_secure_region 1` | DDR secure region 1 |
| 2 | `dram_secure_region 2` | DDR secure region 2 |
| 3 | `dram_secure_region 3` | DDR secure region 3 |
| 4 | `dram_secure_region 4` | DDR secure region 4 |
| 5 | `dram_secure_region 5` | DDR secure region 5 |
| 6 | `dram_secure_region 6` | DDR secure region 6 |
| 7 | `dram_secure_region 7` | DDR secure region 7 |

### 4.6 `dram_obfuscation 0`

- 同一 DDR 防火墙模块内混淆开关寄存器（具体偏移见 bmtest log / SPEC）
- 仅 EL3 测试：混淆 ON 读值 ≠ 明文，OFF 读值 == 明文

### 4.7 ROM 相关命令

- `reg_rom_fw_s_tz_s`：`0x33030058`，bit N = region N secure
- `fabFW_ROM_psmsk`：`0x3303005C`，读锁定掩码

| 命令 | Index | 基地址 | 寄存器位 |
|------|-------|--------|----------|
| `rom_secure_region 0` | 0 | `0x29400000` | `reg_rom_fw_s_tz_s` bit0 |  |
| `rom_secure_region 1` | 1 | `0x29402000` | `reg_rom_fw_s_tz_s` bit1 |  |
| `rom_secure_region 2` | 2 | `0x29404000` | `reg_rom_fw_s_tz_s` bit2 |  |
| `rom_secure_region 3` | 3 | `0x29406000` | `reg_rom_fw_s_tz_s` bit3 |  |
| `rom_secure_region 4` | 4 | `0x29408000` | `reg_rom_fw_s_tz_s` bit4 |  |
| `rom_secure_region 5` | 5 | `0x2940A000` | `reg_rom_fw_s_tz_s` bit5 |  |
| `rom_secure_region 6` | 6 | `0x2940C000` | `reg_rom_fw_s_tz_s` bit6 |  |
| `rom_secure_region 7` | 7 | `0x2940E000` | `reg_rom_fw_s_tz_s` bit7 |  |
| `rom_secure_region 8` | 8 | `0x29410000` | `reg_rom_fw_s_tz_s` bit8 |  |
| `rom_secure_region 9` | 9 | `0x29412000` | `reg_rom_fw_s_tz_s` bit9 |  |
| `rom_secure_region 10` | 10 | `0x29414000` | `reg_rom_fw_s_tz_s` bit10 |  |
| `rom_secure_region 11` | 11 | `0x29416000` | `reg_rom_fw_s_tz_s` bit11 |  |
| `rom_secure_region 12` | 12 | `0x29418000` | `reg_rom_fw_s_tz_s` bit12 |  |
| `rom_secure_region 13` | 13 | `0x2941A000` | `reg_rom_fw_s_tz_s` bit13 |  |
| `rom_secure_region 14` | 14 | `0x2941C000` | `reg_rom_fw_s_tz_s` bit14 |  |
| `rom_secure_region 15` | 15 | `0x2941E000` | `reg_rom_fw_s_tz_s` bit15 | SKIP |
| `rom_secure_region 16` | 16 | `0x29420000` | `reg_rom_fw_s_tz_s` bit16 |  |
| `rom_secure_region 17` | 17 | `0x29422000` | `reg_rom_fw_s_tz_s` bit17 |  |
| `rom_secure_region 18` | 18 | `0x29424000` | `reg_rom_fw_s_tz_s` bit18 |  |
| `rom_secure_region 19` | 19 | `0x29426000` | `reg_rom_fw_s_tz_s` bit19 |  |
| `rom_secure_region 20` | 20 | `0x29428000` | `reg_rom_fw_s_tz_s` bit20 |  |
| `rom_secure_region 21` | 21 | `0x2942A000` | `reg_rom_fw_s_tz_s` bit21 |  |
| `rom_secure_region 22` | 22 | `0x2942C000` | `reg_rom_fw_s_tz_s` bit22 |  |
| `rom_secure_region 23` | 23 | `0x2942E000` | `reg_rom_fw_s_tz_s` bit23 |  |
| `rom_read_lock <i>` | 0-23 | 同上 | `fabFW_ROM_psmsk` bit<i> | |
| `rom_define_region 0` | - | `0x29400400`（读 `0x29400800`） | 用户自定义区 | |

## 5. 位语义速查

| 后缀 | 方向 | bit=0 | bit=1 |
|------|------|-------|-------|
| `_ar_ns` / `_aw_ns`（master） | Master 读/写属性 | 允许非安全访问 | **强制 secure**（复位默认） |
| `_tz_s` / `reg_*_fw_tz_s`（slave） | Slave 区域 | 非 secure | **secure** |
| `fabFW_ROM_psmsk` | ROM 读锁 | - | 读锁定 post-mask |

## 6. 辅助测试建议

### 6.1 判定存疑时

完整流程见 [reference.md](reference.md)「辅助测试流程」。摘要：

**`peri_secure`**：写探针类；EL1 == `0x87654321` → FAIL；否则 PASS。

**`hsperi_secure` / `rom_*` / `dram_secure_region`**：读对比类；EL3 == EL1 时 **勿直接 FAIL**，按下列顺序辅助：

1. `reset` 后 `rm 0x33030004`（期望含 `0x7FD` 模式，bit1=0）
2. `rm 0x3303003C/40/44` 确认 `tz_s` 目标 bit 已置 1
3. 对主探测地址及 `+4/+8/+0x10` 执行：`rm`(EL3) → `switch_el1` → `rm`(EL1)
4. `rm 0x3303004C` / `rm 0x33030050` 查非法访问日志
5. 任一地址 EL3≠EL1 或日志非零 → PASS；全部相同且配置正确 → FAIL

### 6.4 辅助测试命令速查

| 步骤 | 命令 | 期望 |
|------|------|------|
| 确认 EL3 | `current_el` | `3` |
| 放开 CA53 读 | `wm 0x33030004 0x7FD` | `rm` 回读 bit1=0 |
| 置 peri secure | `wm 0x3303003C <mask>` | bit 见 §4.2 |
| 置 hsperi0 secure | `wm 0x33030040 <mask>` | bit 见 §4.3 |
| 置 hsperi1 secure | `wm 0x33030044 <mask>` | bit 见 §4.4 |
| EL3 读 | `rm <probe>` | 记录 |
| 切 EL1 | `switch_el1` | `current_el` 为 1 |
| EL1 读 | `rm <probe>` | 与 EL3 对比 |
| 非法日志 | `rm 0x3303004C` / `rm 0x33030050` | 非零表示有阻断记录 |
| 恢复 | `reset` | 回到 `$ ` prompt |

`tz_s` 写值：`mask = (1 << bit_index)`，或 `rm` 原值后 `wm` 为 `old | mask`。

### 6.2 挂死恢复

- 优先 `reset`（bmtest 命令）
- 无效则硬件复位，从下一条未测用例继续

### 6.3 头文件与 Athena2 寄存器表差异

- `references/reg_sec_fab_firewall.h`：符号名、bit 偏移、**复位值**；bmtest 编译使用
- `reg_sec_fab_Athena2.xls`：**绝对地址布局**（Athena2 为准）
- `references/testcase_security.c`：仅含 SRAM/DDR 辅助范例；`peri_secure`/`hsperi_secure` 完整逻辑在固件 bmtest 内

| 寄存器 | `.h` 偏移 | Athena2 xls 偏移 | 说明 |
|--------|----------|-----------------|------|
| `reg_peri_fw_s_tz_s` | `+0x54` | `+0x3C` | 以 xls / 本文 §1 绝对地址为准 |
| `reg_hsperi_fw_tz_s` | `+0x10`（合并） | `+0x40` / `+0x44`（拆为 hsperi0/1） | bmtest 用拆分后的两个寄存器 |
| `fabFW_top_s_tz_s` | `+0x50` | `+0x54` | 以 xls 为准 |

## 7. 完整 hsperi0 位图（reg_hsperi0_fw_tz_s）

| 位 | 映射 |
|----|------|
| 31 | SIZE_256MB:0x2000_0000,<-31:SPI_NOR2 |
| 30 | SIZE_256MB:0x1000_0000,<-30:SPI_NOR1 |
| 29 | SIZE_16MB :0x0E00_0000,<-29:AXI_RAM |
| 28 | SIZE_64KB :0x0452_0000,<-28:Gigabit Ethernet 1 |
| 27 | SIZE_64KB :0x0451_0000,<-27:Gigabit Ethernet 0 |
| 26 | SIZE_512KB:0x0440_0000,<-26:ROM |
| 25 | SIZE_64KB :0x0433_0000,<-25:System DMA |
| 24 | SIZE_64KB :0x0432_0000,<-24:SD Controller 2 (SDIO) |
| 23 | SIZE_64KB :0x0431_0000,<-23:SD Controller 1 (SDIO) |
| 22 | SIZE_64KB :0x0430_0000,<-22:eMMC Controller |
| 21 | SIZE_64KB :0x041C_0000,<-21:UART4 |
| 20 | SIZE_64KB :0x041B_0000,<-20:SPI3 |
| 19 | SIZE_64KB :0x041A_0000,<-19:SPI2 |
| 18 | SIZE_64KB :0x0419_0000,<-18:SPI1 |
| 17 | SIZE_64KB :0x0418_0000,<-17:SPI0 |
| 16 | SIZE_64KB :0x0417_0000,<-16:UART3 |
| 15 | SIZE_64KB :0x0416_0000,<-15:UART2 |
| 14 | SIZE_64KB :0x0415_0000,<-14:UART1 |
| 13 | SIZE_64KB :0x0414_0000,<-13:UART0 |
| 12 | SIZE_64KB :0x0413_0000,<-12:I2S3 |
| 11 | SIZE_64KB :0x0412_0000,<-11:I2S2 |
| 10 | SIZE_64KB :0x0411_0000,<-10:I2S1 |
| 9 | SIZE_32KB :0x0410_8000,<-9:I2S Subsystem |
| 8 | SIZE_32KB :0x0410_0000,<-8:I2S0 |
| 7 | SIZE_256KB:0x040C_0000,<-7:USB |
| 6 | SIZE_256KB:0x0408_0000,<-6:Reserved |
| 5 | SIZE_128KB:0x0406_0000,<-5:SPI_NAND |
| 4 | SIZE_128KB:0x0404_0000,<-4:I2C Master / Slave 4 |
| 3 | SIZE_64KB :0x0403_0000,<-3:I2C Master / Slave 3 |
| 2 | SIZE_64KB :0x0402_0000,<-2:I2C Master / Slave 2 |
| 1 | SIZE_64KB :0x0401_0000,<-1:I2C Master / Slave 1 |
| 0 | SIZE_64KB :0x0400_0000 <-0:I2C Master / Slave 0 |

## 8. PERI 位图摘录（reg_peri_fw_s_tz_s）

| 位 | 起始地址 | IP |
|----|----------|-----|
| 0 | `0x00000000` | top_misc |
| 1 | `0x00001000` | pinmux |
| 2 | `0x00002000` | clkgen |
| 3 | `0x00003000` | rstgen |
| 4 | `0x00004000` | RTC_FC |
| 5 | `0x00005000` | RTC (REG) |
| 6 | `0x00006000` | comb_usbpcie_phy0 |
| 11 | `0x0000B000` | csi0_wrap |
| 12 | `0x0000C000` | dsi_wrap |
| 13 | `0x0000D000` | csi1_wrap |
| 14 | `0x00010000` | Watch Dog |
| 15 | `0x00020000` | GPIO0 |
| 16 | `0x00030000` | WGN0 |
| 17 | `0x00040000` | KEYSCAN |
| 18 | `0x00050000` | Efuse Controller |
| 19 | `0x00060000` | PWM0 |
| 23 | `0x000A0000` | Timer |
| 26 | `0x000D0000` | process_monitor (7T) |
| 27 | `0x000E0000` | TEMPSEN |
| 28 | `0x000F0000` | SARADC |
