---
name: security-test
description: >-
  Runs Athena2 security firewall batch tests by sending bmtest CLI commands over
  UART (_secure suites plus primitive commands rm/wm/switch_el1/current_el for
  flexible auxiliary verification). Resets after each case. Infers PASS/FAIL
  from register reads. Use for security test, firewall batch testing, or
  flexible memory/EL verification on bmtest.
---

# Athena2 Security 批量测试

Agent 通过串口向 bmtest **直接发送 CLI 命令**。正式测试用 `_secure` 套件；**辅助验证**用原语命令（`rm`/`wm`/`switch_el1`/`current_el`）提高结果可信度。

**固件 log 不会输出 PASS/FAIL**，Agent 须根据读值自行判定，规则见 [reference.md](reference.md)。

## 关联文档

| 文档 | 用途 |
|------|------|
| [se9_uartdl_skill.md](../se9_uartdl_skill.md) | 烧录、串口连接 |
| [reference.md](reference.md) | 判定规则、log 字段、IP 表 |
| [test_cases.md](test_cases.md) | 批量测试命令清单 |
| [flexible_test.md](flexible_test.md) | **原语命令与灵活辅助测试** |
| [templates/report_template.md](templates/report_template.md) | 报告模板 |

## 两层测试策略

| 层级 | 命令类型 | 目的 |
|------|----------|------|
| **正式** | `*_secure` 套件 | 批量防火墙测试，产出 PASS/FAIL 结论 |
| **辅助** | `rm` `wm` `switch_el1` `current_el` `illegal_slave_access_info` | 复核读值、确认 EL、补充非法访问日志 |

Agent **必须先完成正式测试**；对存疑/FAIL 项，按 [flexible_test.md](flexible_test.md) 执行辅助验证，并在报告备注中标注。

## 原语命令速查

| 命令 | 示例 | 用途 |
|------|------|------|
| `current_el` | `current_el` | 确认 CurrentEL（3=EL3, 1=EL1） |
| `switch_el1` | `switch_el1` | EL3→非安全 EL1 |
| `rm` | `rm 29210000` | 读地址（hex） |
| `wm` | `wm 27113000 87654321` | 写地址（hex） |
| `illegal_slave_access_info` | `illegal_slave_access_info 0` | 非法访问日志 |
| `reset` | `reset` | 复位（每条用例后必做） |

详细工作流见 [flexible_test.md](flexible_test.md)。

## 正式测试套件

| 套件 | 命令 | 数量 | 类型 |
|------|------|------|------|
| peri | `peri_secure <i>` | 28 | 写探针 |
| hsperi | `hsperi_secure <g> <i>` | 42 可测 | 读对比 |
| top_axi | `top_axi_fab_secure <i>` | 8 | 写探针 |
| axi_hsperi | `axi_hsperi_secure <i>` | 14 可测 | 读对比 |
| dram_region | `dram_secure_region <0-7>` | 8 | 读对比 |
| dram_obf | `dram_obfuscation 0` | 1 | 混淆验证 |
| rom_region | `rom_secure_region <0-23>` | 24 | 读对比 |
| rom_lock | `rom_read_lock <0-23>` | 24 | 读对比 |
| rom_define | `rom_define_region 0` | 1 | 读对比 |

**重要**：需要逐一完成每一个测试项，不能使用脚本或其他方式优化测试步骤。

## Agent 执行步骤

### 1. 连接串口

按 [se9_uartdl_skill.md](../se9_uartdl_skill.md)，等待 `$ ` prompt。

### 2. 正式测试循环

```
发送 _secure 命令 → 收集 log → 判定 → （可选）辅助复核 → reset → 下一条
```

**辅助复核**（CLI 仍可用时，任选）：

```
current_el
rm <同测试地址>
illegal_slave_access_info 0   # FAIL/BLOCKED 时推荐
```

### 3. 判定（正式测试）

#### 读对比类（hsperi / axi_hsperi / rom_* / dram_secure_region）

```
EL3读值 ≠ EL1读值  →  PASS
EL3读值 == EL1读值  →  FAIL
超时挂死            →  PASS(BLOCKED)
INT: recv interrupt →  PASS
```

#### 写探针类（peri / top_axi）

```
EL1读值 ≠ 探针值  →  PASS    （探针：peri=87654321, top_axi=11111111）
EL1读值 == 探针值  →  FAIL
```

#### 混淆验证（dram_obfuscation）

混淆 OFF 读值 == 明文 `76543210`，ON 时 ≠ 明文 → PASS。

### 4. 生成报告

填入报告模板，辅助验证结果写入「备注」列（如 `已 rm 复核`）。

## 挂死恢复

`reset` 无法送达 → 记 PASS(BLOCKED) → 硬件复位 → 继续下一条。

## 特例

- `hsperi_secure 1 9`：SKIP（UART0）
- `axi_hsperi_secure 0`：SKIP
- `axi_hsperi_secure 1`：APSYS 允许非安全读，完成即 PASS
- 原语 `rm`/`wm` **不配置防火墙**，不能单独替代 `_secure` 套件
