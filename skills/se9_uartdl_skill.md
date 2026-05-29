# 名词定义与系统架构

## 1. BM1688

| 属性 | 说明 |
|------|------|
| **类型** | 算能（SOPHGO）边缘 AI 算力芯片 |
| **CPU** | 八核 ARM Cortex-A53 |
| **TPU 算力** | 16T（INT8） |
| **操作系统** | Ubuntu 22.04 |
| **登录账号** | `linaro` |
| **登录密码** | `linaro` |
| **Root 切换** | `sudo -s`，密码同为 `linaro` |

---

## 2. SE9

| 属性 | 说明 |
|------|------|
| **类型** | 基于 BM1688 芯片的边缘算力盒子/开发板 |
| **SDK 关系** | 与 BM1688 共用同一套 SDK |
| **硬件差异管理** | 通过 OEM 机制选定指定 DTS（设备树）来适配不同产品的硬件差异 |
| **串口连接** | 物理串口接入跳板机，由桥接程序转发 |
| **固件烧录方式** | 通过跳板机的 UART 桥接程序进行 `fip.bin` 烧录 |

---

## 3. 跳板机（Jump Server / Bridge Host）

| 属性 | 说明 |
|------|------|
| **物理连接** | 通过物理串口线与 SE9 相连 |
| **核心程序** | 运行桥接程序（UART-to-SSH Bridge） |
| **SSH 转发** | 将 SE9 的串口数据以 SSH 服务形式转发，端口 `2222` |
| **账号** | `admin@172.25.87.179` |
| **密码** | `123456` |

### 跳板机的能力边界

| 操作 | 是否可行 | 说明 |
|------|----------|------|
| SCP 上传文件到跳板机 | **可行** | `scp -P 2222 fip.bin admin@172.25.87.179:.` 将文件上传到跳板机本地存储 |
| SSH exec 触发 uart-upgrade | **可行** | `ssh -p 2222 admin@172.25.87.179 uart-upgrade` 作为 SSH exec 命令，桥接程序拦截执行 |
| SSH exec 检查依赖 | **可行** | `ssh -p 2222 admin@172.25.87.179 __uart_deps__` |
| SSH 交互式登录后执行跳板机 shell 命令 | **不可行** | SSH 2222 交互式连接直接透传到 SE9 串口，输入的任何内容都发送给 SE9，而非跳板机 |
| 在跳板机上 ls/check 文件 | **不可行** | 无法在跳板机上执行 shell 命令，fip.bin 是否存在只能通过 scp 命令返回状态判断 |

> **关键特性**：SSH 2222 交互式连接 = SE9 串口控制台，不是跳板机的 shell。所有交互式输入直达 SE9 设备。

---

## 4. 服务器（Build Server / Dev Server）

| 属性 | 说明 |
|------|------|
| **职责** | 运行 Claude、编译代码、维护代码仓库、生成固件 |
| **运行环境** | Docker 容器（如 `martin`）用于隔离编译环境 |
| **与跳板机关系** | 完全隔离，无直接物理连接；通过网络 SSH/SCP 与跳板机交互 |
| **fip.bin 位置** | 编译后在 `install/soc_edge_wevb_emmc/fip.bin`（相对于 SDK 工程根目录） |

### 服务器的能力边界

| 操作 | 是否可行 | 说明 |
|------|----------|------|
| 编译 fip.bin | **可行** | 在 Docker 容器内执行 `source build/envsetup_soc.sh` → `defconfig edge_wevb_emmc` → `build_fsbl` |
| 查找/检查 fip.bin | **可行** | `find` 或直接读取 `install/soc_edge_wevb_emmc/fip.bin` |
| SCP 拷贝 fip.bin 到跳板机 | **可行** | `sshpass -p 123456 scp -P 2222 -o StrictHostKeyChecking=no install/soc_edge_wevb_emmc/fip.bin admin@172.25.87.179:.` |
| SSH exec 触发 uart-upgrade | **可行** | `sshpass -p 123456 ssh -o StrictHostKeyChecking=no admin@172.25.87.179 -p 2222 uart-upgrade` |
| SSH 交互式连接 SE9 串口 | **可行** | 通过 sshpass 连接 SSH 2222，获得 SE9 串口控制台 |

---

## 5. UART Download（UART 烧录/升级）

| 属性 | 说明 |
|------|------|
| **前提条件** | SE9 必须重启进入 ROM 阶段（Ubuntu 下用 `sudo shutdown -r +1`，密码 linaro） |
| **触发方式** | 服务器执行 `sshpass -p 123456 ssh -o StrictHostKeyChecking=no admin@172.25.87.179 -p 2222 uart-upgrade` |
| **校验机制** | SE9 在 ROM 阶段接收桥接程序发送的串口校验数据，校验通过后进入烧录流程 |
| **连接特性** | 扦行 uart-upgrade 后 SSH 会话会**立即断开**，此为正常行为 |
| **烧录产物** | 跳板机上的 `fip.bin` 文件（由 scp 上传，无法在跳板机上验证是否存在） |
| **完成标志** | 串口输出出现 `Program fip.bin done` |
| **失败处理** | 若未收到完成标志，需检查 SE9 是否已重启进入 ROM 阶段、校验是否通过 |

---

## 6. fip.bin 升级操作流程（哪一步在哪台机器）

| 步骤 | 执行位置 | 命令 | 说明 |
|------|----------|------|------|
| 1. 编译 fip.bin | **服务器** Docker 内 | `source build/envsetup_soc.sh && defconfig edge_wevb_emmc && build_fsbl` | 产物生成在 `install/soc_edge_wevb_emmc/fip.bin` |
| 2. 确认 fip.bin 存在 | **服务器** | `find install/soc_edge_wevb_emmc/fip.bin` 或直接读取 | 在服务器本地验证，**不要尝试在跳板机上检查** |
| 3. SCP 上传到跳板机 | **服务器** | `sshpass -p 123456 scp -P 2222 -o StrictHostKeyChecking=no install/soc_edge_wevb_emmc/fip.bin admin@172.25.87.179:.` | 上传到跳板机本地存储，scp 返回状态即传输结果 |
| 4. SE9 重启 | **SE9** 串口控制台 | Ubuntu: `sudo shutdown -r +1`；U-Boot: `sleep 15; reset` | 通过 SSH 2222 交互式连接 SE9 执行 |
| 5. 在步骤4执行完，立马触发 uart-upgrade|无需等待shutdown 延时执行完| **服务器** | `sshpass -p 123456 ssh -o StrictHostKeyChecking=no admin@172.25.87.179 -p 2222 uart-upgrade` | SSH exec 命令，**不是交互式输入** |
| 6. 监控烧录进度 | **SE9** 串口控制台 | 等待 `Program fip.bin done` | 通过 SSH 2222 交互式连接 SE9 观察输出 |
| 7. 进入 U-Boot 命令行 | **SE9** 串口控制台 | 发送 6 次 Ctrl+C 退出 kermit 等待 | 进入 `sophon#` |

---

## 7. 系统数据流总览

```
┌─────────────┐      SSH/SCP      ┌─────────────┐      物理串口      ┌─────────┐
│   服务器     │ ◄──────────────► │   跳板机     │ ◄────────────────► │   SE9   │
│ (编译/维护)  │   网络隔离        │ (桥接程序)   │    UART 线        │ (BM1688) │
│             │                   │             │                   │         │
│  Docker内    │  scp -P 2222    │  SSH:2222   │  uart-upgrade     │  ROM    │
│  编译fip.bin ├────────────────► │  转发串口    ├──────────────────►│  校验   │
│             │                   │  接收串口    │                   │  烧录   │
│             │                   │  输出        │                   │         │
└─────────────┘                   └─────────────┘                   └─────────┘

SSH 2222 交互式连接 = SE9 串口控制台（不是跳板机 shell）
SSH 2222 exec 命令 = 跳板机桥接程序拦截执行（如 uart-upgrade）
SCP 2222 上传文件 = 跳板机本地存储（fip.bin 等）
```
