# 串口连接与烧录

| 属性 | 说明 |
|------|------|
| **串口连接方式** | 物理串口接入跳板机，由桥接程序转发至ssh，与agent建立通信 |
| **固件烧录方式** | 通过跳板机的 UART 桥接程序进行 `fip.bin` 烧录 |

---

## 1. 跳板机（Jump Server / Bridge Host）

| 属性 | 说明 |
|------|------|
| **物理连接** | 一般是个人电脑，通过物理串口线与 A2 相连 |
| **核心程序** | 需要运行桥接程序（UART-to-SSH Bridge） |
| **SSH 转发** | 将 A2 的串口数据以 SSH 服务形式转发，端口 `2222` |
| **账号** | `admin@172.25.87.179` |
| **密码** | `123456` |

**重要**: 跳板机的IP(172.25.87.179)为示例，需要先向用户确认跳板机IP

### 跳板机的能力边界

| 操作 | 是否可行 | 说明 |
|------|----------|------|
| SCP 上传文件到跳板机 | **可行** | `scp -P 2222 fip.bin admin@172.25.87.179:.` 将文件上传到跳板机本地存储 |
| SSH exec 触发 uart-upgrade | **可行** | `ssh -p 2222 admin@172.25.87.179 uart-upgrade` 作为 SSH exec 命令，桥接程序拦截执行 |
| SSH exec 检查依赖 | **可行** | `ssh -p 2222 admin@172.25.87.179 __uart_deps__` |
| SSH 交互式登录后执行跳板机 shell 命令 | **不可行** | SSH 2222 交互式连接直接透传到 A2 串口，输入的任何内容都发送给 A2，而非跳板机 |
| 在跳板机上 ls/check 文件 | **不可行** | 无法在跳板机上执行 shell 命令，fip.bin 是否存在只能通过 scp 命令返回状态判断 |

> **关键特性**：SSH 2222 交互式连接 = A2 串口控制台，不是跳板机的 shell。所有交互式输入直达 A2 设备。

---

## 2. 服务器（Build Server / Dev Server）

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
| SSH 交互式连接 A2 串口 | **可行** | 通过 sshpass 连接 SSH 2222，获得 A2 串口控制台 |

---

## 3. UART Download（UART 烧录/升级）

| 属性 | 说明 |
|------|------|
| **前提条件** | A2 必须重启进入 ROM 阶段（bmtest中需要相关的重启命令如reset、reboot等，如果没有只能手动重启） |
| **触发方式** | 服务器执行 `sshpass -p 123456 ssh -o StrictHostKeyChecking=no admin@172.25.87.179 -p 2222 uart-upgrade` |
| **校验机制** | A2 在 ROM 阶段接收桥接程序发送的串口校验数据，校验通过后进入烧录流程 |
| **连接特性** | 扦行 uart-upgrade 后 SSH 会话会**立即断开**，此为正常行为 |
| **烧录产物** | 跳板机上的 `fip.bin` 文件（由 scp 上传，无法在跳板机上验证是否存在） |

---

## 4. fip.bin 升级操作流程（哪一步在哪台机器）

| 步骤 | 执行位置 | 命令 | 说明 |
|------|----------|------|------|
| 1. 编译 fip.bin | **服务器** Docker 内 | `source build/envsetup_soc.sh && defconfig edge_wevb_emmc && build_fsbl` | 产物生成在 `install/soc_edge_wevb_emmc/fip.bin` |
| 2. 确认 fip.bin 存在 | **服务器** | `find install/soc_edge_wevb_emmc/fip.bin` 或直接读取 | 在服务器本地验证，**不要尝试在跳板机上检查** |
| 3. SCP 上传到跳板机 | **服务器** | `sshpass -p 123456 scp -P 2222 -o StrictHostKeyChecking=no install/soc_edge_wevb_emmc/fip.bin admin@172.25.87.179:.` | 上传到跳板机本地存储，scp 返回状态即传输结果 |
| 4. A2 重启 | **A2** 串口控制台 | Ubuntu: `sudo shutdown -r +1`；U-Boot: `sleep 15; reset` Bmtest: `reset`| 通过 SSH 2222 交互式连接 A2 执行 |
| 5. 在步骤4执行完，立马触发 uart-upgrade|无需等待shutdown 延时执行完| **服务器** | `sshpass -p 123456 ssh -o StrictHostKeyChecking=no admin@172.25.87.179 -p 2222 uart-upgrade` | SSH exec 命令，**不是交互式输入** |
| 6. 监控烧录进度 | **A2** 串口控制台 | 等待 `Program fip.bin done` | 通过 SSH 2222 交互式连接 A2 观察输出 |

**注意**： 测试前开发板可能处于linux、uboot、bmtest环境下，但固件烧录后 A2 应当处于bmtest环境。烧录后如果为uboot环境下（sophon#），则烧录失败。

---

## 5. 系统数据流总览

```
┌─────────────┐      SSH/SCP      ┌─────────────┐      物理串口      ┌─────────┐
│   服务器     │ ◄──────────────► │   跳板机     │ ◄────────────────► │    A2   │
│ (编译/维护)  │   网络隔离        │ (桥接程序)   │    UART 线        │ (BM1688) │
│             │                   │             │                   │         │
│  Docker内    │  scp -P 2222    │  SSH:2222   │  uart-upgrade     │  ROM    │
│  编译fip.bin ├────────────────► │  转发串口    ├──────────────────►│  校验   │
│             │                   │  接收串口    │                   │  烧录   │
│             │                   │  输出        │                   │         │
└─────────────┘                   └─────────────┘                   └─────────┘

SSH 2222 交互式连接 = A2 串口控制台（不是跳板机 shell）
SSH 2222 exec 命令 = 跳板机桥接程序拦截执行（如 uart-upgrade）
SCP 2222 上传文件 = 跳板机本地存储（fip.bin 等）
```
