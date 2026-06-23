# Security 测试命令清单

Agent 按顺序通过串口发送以下 bmtest CLI 命令。每条命令执行后必须 `reset` 并等待重启。

**原语命令**（`rm`/`wm`/`switch_el1`/`current_el` 等）用于辅助验证，见 [flexible_test.md](flexible_test.md)。

跳过项直接记 SKIP，不发送命令。

## peri_secure（28 项）

| Index | 命令 | 名称 |
|-------|------|------|
| 0 | `peri_secure 0` | PERI_INTC3 |
| 1 | `peri_secure 1` | PERI_INTC2 |
| 2 | `peri_secure 2` | PERI_INTC1 |
| 3 | `peri_secure 3` | PERI_INTC0 |
| 4 | `peri_secure 4` | PERI_OTP |
| 5 | `peri_secure 5` | PERI_MAILBOX |
| 6 | `peri_secure 6` | PERI_SARADC |
| 7 | `peri_secure 7` | PERI_TEMPSEN |
| 8 | `peri_secure 8` | PERI_PMCTL |
| 9 | `peri_secure 9` | PERI_TIMER |
| 10 | `peri_secure 10` | PERI_PWM4 |
| 11 | `peri_secure 11` | PERI_PWM3 |
| 12 | `peri_secure 12` | PERI_PWM2 |
| 13 | `peri_secure 13` | PERI_PWM1 |
| 14 | `peri_secure 14` | PERI_PWM0 |
| 15 | `peri_secure 15` | PERI_EFUSE |
| 16 | `peri_secure 16` | PERI_KEYSCAN |
| 17 | `peri_secure 17` | PERI_WGN1 |
| 18 | `peri_secure 18` | PERI_WGN0 |
| 19 | `peri_secure 19` | PERI_GPIO5 |
| 20 | `peri_secure 20` | PERI_GPIO4 |
| 21 | `peri_secure 21` | PERI_GPIO3 |
| 22 | `peri_secure 22` | PERI_GPIO2 |
| 23 | `peri_secure 23` | PERI_GPIO1 |
| 24 | `peri_secure 24` | PERI_GPIO0 |
| 25 | `peri_secure 25` | PERI_WDT2 |
| 26 | `peri_secure 26` | PERI_WDT1 |
| 27 | `peri_secure 27` | PERI_WDT0 |

## hsperi_secure（43 项，index 9 跳过）

| is_hsperi0 | Index | 命令 | 名称 | 备注 |
|------------|-------|------|------|------|
| 1 | 0-8 | `hsperi_secure 1 <n>` | HSPERI0_n | |
| 1 | 9 | — | HSPERI0_UART0 | **SKIP** |
| 1 | 10-31 | `hsperi_secure 1 <n>` | HSPERI0_n | |
| 0 | 0-10 | `hsperi_secure 0 <n>` | HSPERI1_n | |

## top_axi_fab_secure（8 项）

| Index | 命令 | 名称 |
|-------|------|------|
| 0 | `top_axi_fab_secure 0` | TOP_AXI_X2P |
| 1 | `top_axi_fab_secure 1` | VIP_CTRL_VI |
| 2 | `top_axi_fab_secure 2` | VIP_CTRL_VO |
| 3 | `top_axi_fab_secure 3` | VIDEO_CTRL_VD1 |
| 4 | `top_axi_fab_secure 4` | VIDEO_CTRL_VD0 |
| 5 | `top_axi_fab_secure 5` | VIDEO_CTRL_VE |
| 6 | `top_axi_fab_secure 6` | DDR_CTRL_32K |
| 7 | `top_axi_fab_secure 7` | DDR_CTRL_256M |

## axi_hsperi_secure（15 项，index 0 跳过）

| Index | 命令 | 名称 | 备注 |
|-------|------|------|------|
| 0 | — | RESERVED | **SKIP** |
| 1 | `axi_hsperi_secure 1` | APSYS_ctrl | 允许非安全读，完成即 PASS |
| 2-14 | `axi_hsperi_secure <n>` | 见 reference.md | |

## dram_secure_region（8 项，region 0–7）

测试地址 `0x108000000`，EL3 写入 `0x76543210` / `0xfedcba98` 后切 EL1 只读。

| Index | 命令 | 说明 |
|-------|------|------|
| 0 | `dram_secure_region 0` | secure region 0 |
| 1 | `dram_secure_region 1` | secure region 1 |
| 2 | `dram_secure_region 2` | secure region 2 |
| 3 | `dram_secure_region 3` | secure region 3 |
| 4 | `dram_secure_region 4` | secure region 4 |
| 5 | `dram_secure_region 5` | secure region 5 |
| 6 | `dram_secure_region 6` | secure region 6 |
| 7 | `dram_secure_region 7` | secure region 7 |

## dram_obfuscation（1 项，仅 EL3）

| 命令 | 说明 |
|------|------|
| `dram_obfuscation 0` | 参数被忽略，但建议传 `0`；**不切换 EL1** |

测试地址 `0x110000000`，验证混淆开/关时读值变化。

## rom_secure_region（24 项，index 0–23）

| Index | 命令 | 基地址 |
|-------|------|--------|
| 0 | `rom_secure_region 0` | 0x29400000 |
| 1 | `rom_secure_region 1` | 0x29402000 |
| 2 | `rom_secure_region 2` | 0x29404000 |
| 3 | `rom_secure_region 3` | 0x29406000 |
| 4 | `rom_secure_region 4` | 0x29408000 |
| 5 | `rom_secure_region 5` | 0x2940a000 |
| 6 | `rom_secure_region 6` | 0x2940c000 |
| 7 | `rom_secure_region 7` | 0x2940e000 |
| 8 | `rom_secure_region 8` | 0x29410000 |
| 9 | `rom_secure_region 9` | 0x29412000 |
| 10 | `rom_secure_region 10` | 0x29414000 |
| 11 | `rom_secure_region 11` | 0x29416000 |
| 12 | `rom_secure_region 12` | 0x29418000 |
| 13 | `rom_secure_region 13` | 0x2941a000 |
| 14 | `rom_secure_region 14` | 0x2941c000 |
| 15 | `rom_secure_region 15` | 0x2941e000 |
| 16 | `rom_secure_region 16` | 0x29420000 |
| 17 | `rom_secure_region 17` | 0x29422000 |
| 18 | `rom_secure_region 18` | 0x29424000 |
| 19 | `rom_secure_region 19` | 0x29426000 |
| 20 | `rom_secure_region 20` | 0x29428000 |
| 21 | `rom_secure_region 21` | 0x2942a000 |
| 22 | `rom_secure_region 22` | 0x2942c000 |
| 23 | `rom_secure_region 23` | 0x2942e000 |

## rom_read_lock（24 项，index 0–23）

地址与 `rom_secure_region` 相同，命令为 `rom_read_lock <index>`。

## rom_define_region（1 项）

| 命令 | 说明 |
|------|------|
| `rom_define_region 0` | 用户自定义 ROM 安全区；参数被忽略，建议传 `0` |

关注 log 中 `rom_fab [0x29400400]` 行（实际读地址 `0x29400800`）。

## 每条用例后的复位

```
reset
```

等待设备重启，重新进入 CLI，再执行下一条。
