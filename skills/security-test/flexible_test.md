# 灵活辅助测试（原语命令）

bmtest 除批量 `_secure` 套件外，还提供颗粒度更小的原语命令。Agent 可用它们**辅助验证**批量测试结果、排查疑点、提高报告可信度。

**定位**：原语命令是**辅助手段**，不替代正式批量套件；正式结论仍以 `_secure` 套件 + [reference.md](reference.md) 判定规则为准。

## 原语命令一览

| 命令 | 格式 | 作用 | log 关键输出 |
|------|------|------|-------------|
| `help` | `help` | 列出所有可用命令 | `Command List:` |
| `current_el` | `current_el` | 查看当前异常级与安全状态 | `CurrentEL=N`, `Current state=N` |
| `switch_el1` | `switch_el1` | EL3 跳入非安全 EL1 | `Before/After switch, CurrentEL=`, `el_switch_cnt=` |
| `rm` | `rm <hex_addr>` | 读 32 位寄存器/内存 | `read addr = 0x..., value = 0x...` |
| `wm` | `wm <hex_addr> <hex_val>` | 写 32 位寄存器/内存 | `write addr = 0x..., value = 0x...` |
| `reset` | `reset` | 系统复位 | `resetting ...` |
| `illegal_slave_access_info` | `illegal_slave_access_info 0` | 读非法访问日志寄存器 | `rom_fab [0x3303004c]=`, `[0x33030050]=` |

地址与数值均为**十六进制**，例如：`rm 29210000`、`wm 27113000 87654321`。

## 重要约束

1. **防火墙配置**由 `_secure` 套件命令内部完成；`rm`/`wm`/`switch_el1` **不会**配置防火墙。
2. EL3→EL1 后若非法访问导致挂死，CLI 不可用，需 `reset` 或硬件复位。
3. `switch_el1` 执行后，后续 `rm`/`wm` 在 **EL1 非安全态**下执行（若 CLI 仍存活）。
4. `reset` 后防火墙配置丢失，每条辅助验证需在新会话中重新建立上下文。
5. 每条独立验证路径结束后应 `reset`，再进入下一条。

## 何时使用辅助测试

| 场景 | 建议辅助操作 |
|------|-------------|
| 批量结果 PASS/FAIL 存疑 | 同会话内 `rm` 同地址复核；或 `reset` 后重跑该条 `_secure` |
| 需确认当前 EL | `current_el` |
| 需确认 EL 切换是否成功 | `switch_el1` + 查看 log 中 `CurrentEL` 与 `el_switch_cnt` |
| FAIL 或 BLOCKED 后需深挖 | 在 `reset` 前（若 CLI 仍可用）执行 `illegal_slave_access_info 0` |
| 需对**指定地址**手动读写 | `rm`/`wm` + `switch_el1` + 再 `rm`/`wm` |
| 写探针穿透怀疑 | `wm <addr> <probe>` 后 `rm <addr>` 确认 |

## 辅助工作流

### 工作流 A：批量测试 + 同会话复核（推荐）

`_secure` 命令若正常返回 `$ ` prompt（未挂死），Agent 可立即复核：

```
hsperi_secure 1 0          ← 正式测试，记录 log 中 EL3/EL1 读值
current_el                 ← 确认当前 EL（多为 EL1）
rm 29210000                ← 对同一地址再读一次
illegal_slave_access_info 0  ← 可选，查非法访问日志
reset
```

**判定增强**：若正式 log 与 `rm` 复核读值一致，在报告中标注「已复核」提高可信度。

### 工作流 B：手动 EL3/EL1 读对比（需先配置防火墙）

对某地址验证防火墙时，**须先**执行对应 `_secure` 命令完成防火墙配置；若该命令已包含完整测试，通常直接以其 log 为准。

若仅需在**已配置防火墙的同一会话**内补充读值：

```
# 前提：已通过某 _secure 命令配置防火墙且 CLI 仍可用
current_el                 → 期望 CurrentEL=1（或 3，视上一步而定）
rm <addr>                  ← 当前 EL 下读值
reset
```

无法在不跑 `_secure` 的情况下单独配置防火墙。

### 工作流 C：纯 EL 行为基线（不配置防火墙）

用于区分「EL 切换本身」与「防火墙生效」的影响：

```
current_el                 → CurrentEL=3
rm <addr>                  → EL3 读值（记为 V3）
switch_el1                 → 切 EL1
current_el                 → 期望 CurrentEL=1
rm <addr>                  → EL1 读值（记为 V1）
reset
```

此时尚未配置防火墙，V3 与 V1 差异仅反映 EL 差异，**不能**作为防火墙 PASS/FAIL 依据。可与正式 `_secure` 结果对照分析。

### 工作流 D：手动写探针（类似 peri_secure 逻辑）

在已通过 `_secure` 配置防火墙的会话中，或用于无防火墙的 EL 写穿透实验：

```
rm <addr>                  → 记录写前读值
wm <addr> 87654321         → 写入探针（peri 常用值）
rm <addr>                  → 确认 EL3 写成功
switch_el1
wm <addr> 87654321         → EL1 写探针
rm <addr>                  → EL1 读回：== 87654321 则写穿透
reset
```

正式 peri_secure 判定：EL1 读回 `== 0x87654321` → FAIL。

### 工作流 E：FAIL 项诊断（reset 前）

```
illegal_slave_access_info 0
reset
```

将 `0x3303004c` / `0x33030050` 读值记入报告「失败项详情」。

## 与批量套件的配合

```
┌─────────────────────────────────────────────────────────┐
│  正式测试（必做）                                        │
│  peri_secure / hsperi_secure / ... 按 test_cases.md     │
│  → 按 reference.md 判定 PASS/FAIL/BLOCKED               │
└───────────────────────┬─────────────────────────────────┘
                        │ 结果存疑 / FAIL / 需增强可信度
                        ▼
┌─────────────────────────────────────────────────────────┐
│  辅助测试（可选）                                        │
│  current_el / rm / wm / switch_el1 / illegal_slave_... │
│  → 复核读值、确认 EL、补充非法访问日志                   │
└───────────────────────┬─────────────────────────────────┘
                        ▼
                   reset → 下一条
```

## 报告中的标注方式

辅助测试通过后，在备注列注明，例如：

- `已 rm 复核，读值一致`
- `illegal_slave_access_info: 0x.../0x...`
- `switch_el1 确认 CurrentEL: 3→1`
- `手动写探针复核：EL1 未穿透`

## 常用地址速查

正式测试地址见 [reference.md](reference.md) IP 表。原语 `rm`/`wm` 使用表中**基地址**（十六进制，不带 `0x` 前缀亦可）。

| 示例 | 地址 | 对应套件 |
|------|------|----------|
| HSPERI0_0 | `29210000` | hsperi_secure 1 0 |
| PERI_INTC3 | `27113000` | peri_secure 0 |
| DRAM secure | `108000000` | dram_secure_region |
| ROM region 0 | `29400000` | rom_secure_region 0 |

防火墙寄存器（高级调试，慎用）：`FAB_FIREWALL_BASE = 0x33030000`
