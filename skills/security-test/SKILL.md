---
name: security-test
description: >-
  Runs Athena2 security firewall batch tests by sending bmtest CLI commands over
  UART (_secure suites plus primitive commands rm/wm/switch_el1/current_el for
  flexible auxiliary verification). Resets after each case. Infers PASS/FAIL
  from register reads. Use for security test, firewall batch testing, or
  flexible memory/EL verification on bmtest.
---

# Athena2 Security 测试

| 对象 | 说明 |
|------|------|
| 测试环境 | 裸机环境，只能使用 bmtest 中的命令 |
| bmtest | 封装 `peri_secure` / `hsperi_secure` 等命令，内部完成寄存器配置 + EL 切换 |
| 辅助测试 | `rm`/`wm`/`switch_el1`/`current_el`/`reset`；配置规律见 [references/testcase_security.c](references/testcase_security.c) |

## 关联文档

| 文档 | 用途 |
|------|------|
| [uart_skill.md](uart_skill.md) | 串口连接 |
| [reference.md](references/reference.md) | **判定规则**、log 字段、寄存器位语义 |
| [security_reg.md](references/security_reg.md) | 寄存器绝对地址、index→bit 映射 |
| [security_testcase.md](references/security_testcase.md) | 官方验证表格用例总结 |
| [test_cases.md](test_cases.md) | 批量测试命令清单 |
| [report_template.md](templates/report_template.md) | 报告模板 |

## 测试套件（bmtest）

| 套件 | 命令 | 数量 | 判定类型 |
|------|------|------|----------|
| peri | `peri_secure <i>` | 28 | **写探针** |
| hsperi | `hsperi_secure <g> <i>` | 42 可测 | **读对比** |
| dram_region | `dram_secure_region <0-7>` | 8 | 读对比 |
| dram_obf | `dram_obfuscation 0` | 1 | 混淆验证 |
| rom_region | `rom_secure_region <0-23>` | 24 | 读对比 |
| rom_lock | `rom_read_lock <0-23>` | 24 | 读对比 |
| rom_define | `rom_define_region 0` | 1 | 读对比 |

**为保证测试稳定，须逐条手动执行，不要用脚本批量刷命令。**

## Agent 执行步骤

Agent 通过串口向 bmtest **直接发送 CLI 命令**，通信方式见 [uart_skill.md](uart_skill.md)。

**固件 log 不会输出 PASS/FAIL**，判定规则见 [reference.md](references/reference.md)。

### 1. 连接串口

等待 `$ ` prompt。开机 log 结束后 **等待 2s** 再发命令。

### 2. 测试循环

```
发送 bmtest 命令 → 收集 log → 判定 → reset → 下一条
```

**每条用例后必须 `reset`**，否则 EL 切换后可能挂死且无法恢复。不要用 Ctrl+C。

### 3. 结果判定（摘要）

完整规则见 [reference.md](references/reference.md)。

#### 写探针类：`peri_secure`

```
EL3 写探针 0x87654321 → switch_el1 → EL1 读回
EL1读值 ≠ 0x87654321  →  PASS（写未穿透）
EL1读值 == 0x87654321  →  FAIL
挂死 / INT: recv interrupt  →  PASS(BLOCKED) / PASS
```

#### 读对比类：`hsperi_secure` / `rom_*` / `dram_secure_region`

```
EL3读值 ≠ EL1读值  →  PASS
EL3读值 == EL1读值  →  触发辅助测试（勿直接 FAIL）→ 见 reference.md「辅助测试流程」
挂死  →  PASS(BLOCKED) 或记录完整 log
INT: recv interrupt  →  PASS
```

#### 辅助测试（EL3==EL1 时）

正式用例 `reset` 后，按 [reference.md](references/reference.md) 辅助测试流程：

1. 从 log 或 [security_reg.md](references/security_reg.md) §4 取探测基址
2. `wm 0x33030004 0x7FD` + 置位 `tz_s` → `rm` 主地址 → `switch_el1` → `rm` 对比
3. 仍相同则换 `+4` / `+8` / `+0x10` 重测（每次 `switch_el1` 后须 `reset`）
4. 查 `0x3303004C/50` 非法访问日志；配置正确且全部相同 → **FAIL**

辅助结论记入报告「辅助验证记录」。

#### 混淆验证：`dram_obfuscation`

混淆 OFF 读值 == `0x76543210`，ON 时 ≠ 明文 → PASS。

### 4. 生成报告

填入 [report_template.md](templates/report_template.md)。

## 挂死恢复

1. 尝试 `reset` → 继续下一条
2. 无效则记 PENDING，提示用户硬件复位 → 从下一条未测用例继续

## 特例（SKIP）

- `hsperi_secure 1 9`：UART0（与调试串口冲突）
- `peri_secure 4`：OTP
- `rom_secure_region 15`：ROM 阶段已使能该防火墙
