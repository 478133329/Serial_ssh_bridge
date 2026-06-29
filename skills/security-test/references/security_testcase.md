# Security 测试用例

> 来源：`security_testcase.xlsx`（工作表 **28.Security**）
> 本文档为官方验证表格的结构化总结；bmtest 可直接执行的命令见 [test_cases.md](../test_cases.md)。

## 1. 概览

- **用例总数**：145 项（官方 Security 验证表格）
- **来源文件**：`references/security_testcase.xlsx`

## 2. 测试范围说明

官方 Security 验证覆盖以下能力域：

- **总线防火墙**：TOP AXI、HSPERI、Fabric、Master、Debug、RTC、DDR、ROM
- **外设访问控制**：APB/PERI 从设备非安全访问阻断
- **安全加速器**：CryptoDMA 加解密/摘要/Base64、PKA、TRNG
- **存储保护**：DDR secure region / obfuscation、ROM secure region / read lock
- **其他**：OTP、SPACC、非法从地址空间访问等

典型测试方法（表格统一模板）：

1. 复位后配置 master 为安全态
2. 将目标外设/区域配置为 secure
3. 切换 CPU 至非安全态后发起读/写访问
4. 预期：非安全访问失败（hang up / bus error / 中断），且不产生 exception 穿透

## 3. 分类统计

| 分类 | 数量 | 与 bmtest 关系 |
|------|------|----------------|
| TOP AXI Fabric (fabFW_top_s_tz_s) | 9 | 部分覆盖 `top_axi_fab_secure` |
| HSPERI Slave Protection | 26 | 部分覆盖 `axi_hsperi_secure` |
| APB Slave / PERI | 72 | 部分覆盖 `peri_secure` |
| DDR Firewall | 3 | 覆盖 `dram_secure_region` / `dram_obfuscation` |
| ROM Firewall | 3 | 覆盖 `rom_secure_region` / `rom_read_lock` / `rom_define_region` |
| RTC Firewall | 3 | 需辅助验证（rm/wm） |
| Debug Protection Firewall | 8 | 需辅助验证 |
| Master Firewall | 5 | 需辅助验证 |
| Fabric Firewall | 2 | 需辅助验证 |
| SEC_TOP | 7 | 需辅助验证 |
| C906 Firewall | 2 | 需辅助验证 |
| TPU / SRAM Region | 4 | 需辅助验证 |
| Illegal Slave Space | 1 | 需辅助验证 |


## 4. 用例明细

### TOP AXI Fabric (fabFW_top_s_tz_s)（9 项）

| No | 测试目的 | 预期结果 | 标签 | CA55 | 备注 |
|----|----------|----------|------|------|------|
| 1 | fabFW_top_s_tz_s - TOP_AXI_FAB - TOP_AXI_X2P | Non-secure CPU failed to read secure peripheral 并且产生exception | Firewall | - | - |
| 2 | fabFW_top_s_tz_s - TOP_AXI_FAB - VIP_CTRL(vO) | Non-secure CPU failed to read secure peripheral 并且产生exception | - | - | - |
| 3 | fabFW_top_s_tz_s - TOP_AXI_FAB - VIDEO_CTRL(VD3) | Non-secure CPU failed to read secure peripheral 并且产生中断 | - | - | - |
| 4 | fabFW_top_s_tz_s - TOP_AXI_FAB - VIDEO_CTRL(VD2) | Non-secure CPU failed to read secure peripheral 并且产生中断 | - | - | - |
| 5 | fabFW_top_s_tz_s - TOP_AXI_FAB - VIDEO_CTRL(VD1) | Non-secure CPU failed to read secure peripheral 并且产生中断 | - | - | - |
| 6 | fabFW_top_s_tz_s - TOP_AXI_FAB - VIDEO_CTRL(VD0) | Non-secure CPU failed to read secure peripheral 并且产生中断 | - | - | - |
| 7 | fabFW_top_s_tz_s - TOP_AXI_FAB - VIDEO_CTRL(VE) | Non-secure CPU failed to read secure peripheral 并且产生exception | - | - | - |
| 8 | fabFW_top_s_tz_s - TOP_AXI_FAB - top_north_cfg_0 | Non-secure CPU failed to read secure peripheral 并且产生exception | - | - | - |
| 9 | fabFW_top_s_tz_s - TOP_AXI_FAB - DDR_CTRL(256M 7000000) | Non-secure CPU failed to read secure peripheral 并且产生exception | - | - | - |

### HSPERI Slave Protection（26 项）

| No | 测试目的 | 预期结果 | 标签 | CA55 | 备注 |
|----|----------|----------|------|------|------|
| 10 | Slave protection - HSPERI fabric - APSYS_ctrl | Non-secure CPU failed to read secure peripheral 并且产生exception | - | - | - |
| 11 | Slave protection - HSPERI fabric -PCIE_ctrl | Non-secure CPU failed to read secure peripheral. 非安全状态下cpu访问安全ip（spacc ...）失败 | 需pcie db | - | - |
| 12 | Slave protection - HSPERI fabric - USBSYS_ctrl | Non-secure CPU failed to read secure peripheral. 非安全状态下cpu访问安全ip（spacc ...）失败 | 需usb db | - | - |
| 13 | Slave protection - HSPERI fabric - RTC_SYS_ctrl | Non-secure CPU failed to read secure peripheral. 非安全状态下cpu访问安全ip（spacc ...）失败 | - | - | - |
| 14 | Slave protection - HSPERI fabric - HSPERI_ctrl | Non-secure CPU failed to read secure peripheral. 非安全状态下cpu访问安全ip（spacc ...）失败 | 切换成ns 后，串口无法再输出 看PC值，卡在了和其他case相同的地方 | - | - |
| 15 | Slave protection - HSPERI fabric - DBG_SYS | Non-secure CPU failed to read secure peripheral. 非安全状态下cpu访问安全ip（spacc ...）失败 | - | - | - |
| 16 | Slave protection - HSPERI fabric - SYS_ctrl | Non-secure CPU failed to read secure peripheral. 非安全状态下cpu访问安全ip（spacc ...）失败 | - | - | - |
| 17 | Slave protection - HSPERI fabric - PERI | Non-secure CPU failed to read secure peripheral. 非安全状态下cpu访问安全ip（spacc ...）失败 | - | - | - |
| 18 | Slave protection - HSPERI fabric - VE_ctrl | Non-secure CPU failed to read secure peripheral. 非安全状态下cpu访问安全ip（spacc ...）失败 | 需ve db | - | - |
| 19 | Slave protection - HSPERI fabric - VD3_ctrl | Non-secure CPU failed to read secure peripheral. 非安全状态下cpu访问安全ip（spacc ...）失败 | 需vd db | - | - |
| 20 | Slave protection - HSPERI fabric - VD2_ctrl | Non-secure CPU failed to read secure peripheral. 非安全状态下cpu访问安全ip（spacc ...）失败 | 需vd db | - | - |
| 21 | Slave protection - HSPERI fabric - VD1_ctrl | Non-secure CPU failed to read secure peripheral. 非安全状态下cpu访问安全ip（spacc ...）失败 | 需vd db | - | - |
| 22 | Slave protection - HSPERI fabric - VD0_ctrl | Non-secure CPU failed to read secure peripheral. 非安全状态下cpu访问安全ip（spacc ...）失败 | 需vd db | - | - |
| 23 | Slave protection - HSPERI fabric - SE_ctrl | Non-secure CPU failed to read secure peripheral. 非安全状态下cpu访问安全ip（spacc ...）失败 | - | - | - |
| 24 | Slave protection - HSPERI fabric - VO_ctrl | Non-secure CPU failed to read secure peripheral. 非安全状态下cpu访问安全ip（spacc ...）失败 | 需vo db | - | - |
| 25 | Slave protection - HSPERI fabric - DDR_ctrl | Non-secure CPU failed to read secure peripheral. 非安全状态下cpu访问安全ip（spacc ...）失败 | - | - | - |
| 26 | Slave protection - HSPERI fabric - top_north_cfg | Non-secure CPU failed to read secure peripheral. 非安全状态下cpu访问安全ip（spacc ...）失败 | - | - | - |
| 27 | Slave protection - HSPERI fabric - TPU_ctrl | Non-secure CPU failed to read secure peripheral. 非安全状态下cpu访问安全ip（spacc ...）失败 | 需tpu db | - | - |
| 28 | Slave protection - TPU fabric - tpu0 mem | 访问不了，卡住 | - | - | - |
| 29 | Slave protection - TPU fabric - tpu1 mem | 访问不了，卡住 | - | - | - |
| 30 | Slave protection - TPU fabric - tpu2 mem | 访问不了，卡住 | - | - | - |
| 31 | Slave protection - TPU fabric - tpu3 mem | 访问不了，卡住 | - | - | - |
| 32 | Slave protection - TPU fabric - gdma0_cfg | 访问不了，卡住 | - | - | - |
| 33 | Slave protection - TPU fabric - gdma1_cfg | 访问不了，卡住 | - | - | - |
| 34 | Slave protection - TPU fabric - gdma2_cfg | 访问不了，卡住 | - | - | - |
| 35 | Slave protection - TPU fabric - gdma3_cfg | 访问不了，卡住 | - | - | - |

### APB Slave / PERI（72 项）

| No | 测试目的 | 预期结果 | 标签 | CA55 | 备注 |
|----|----------|----------|------|------|------|
| 54 | APB slave - TOP fabric non-AXI slaves - MEM_MASK_4KB, 32'h2711_3000 (PERI_INTC3) | 不能访问 hang up | - | - | - |
| 55 | APB slave - TOP fabric non-AXI slaves - MEM_MASK_4KB, 32'h2711_2000 (PERI_INTC2) | 不能访问 hang up | - | - | - |
| 56 | APB slave - TOP fabric non-AXI slaves - MEM_MASK_4KB, 32'h2711_1000 (PERI_INTC1) | 不能访问 hang up | - | - | - |
| 57 | APB slave - TOP fabric non-AXI slaves - MEM_MASK_4KB, 32'h2711_0000 (PERI_INTC0) | 不能访问 hang up | - | - | - |
| 58 | APB slave - TOP fabric non-AXI slaves - MEM_MASK_4KB, 32'h2710_0000 (PERI_OTP) | 不能访问 hang up | - | - | - |
| 59 | APB slave - TOP fabric non-AXI slaves - MEM_MASK_4KB, 32'h270F_0000 (PERI_MAILBOX) | 不能访问 hang up | - | - | - |
| 60 | APB slave - TOP fabric non-AXI slaves - MEM_MASK_4KB, 32'h270E_0000 (PERI_SARADC) | 不能访问 hang up | - | - | - |
| 61 | APB slave - TOP fabric non-AXI slaves - MEM_MASK_4KB, 32'h270D_0000 (PERI_TEMPSEN) | 不能访问 hang up | - | - | - |
| 62 | APB slave - TOP fabric non-AXI slaves - MEM_MASK_4KB, 32'h2709_0000 (PERI_TIMER) | 不能访问 hang up | - | - | - |
| 63 | APB slave - TOP fabric non-AXI slaves - MEM_MASK_4KB, 32'h2705_5000 (PERI_PWM5) | 不能访问 hang up | 默认安全 | - | - |
| 64 | APB slave - TOP fabric non-AXI slaves - MEM_MASK_4KB, 32'h2705_4000 (PERI_PWM4) | 不能访问 hang up | - | - | - |
| 65 | APB slave - TOP fabric non-AXI slaves - MEM_MASK_4KB, 32'h2705_3000 (PERI_PWM3) | 不能访问 hang up | - | - | - |
| 66 | APB slave - TOP fabric non-AXI slaves - MEM_MASK_4KB, 32'h2705_2000 (PERI_PWM2) | 不能访问 hang up | - | - | - |
| 67 | APB slave - TOP fabric non-AXI slaves - MEM_MASK_4KB, 32'h2705_1000 (PERI_PWM1) | 不能访问 hang up | - | - | - |
| 68 | APB slave - TOP fabric non-AXI slaves - MEM_MASK_4KB, 32'h2705_0000 (PERI_PWM0) | 不能访问 hang up | - | - | - |
| 69 | APB slave - TOP fabric non-AXI slaves - MEM_MASK_4KB, 32'h2701_7000 (PERI_GPIO7) | 不能访问 hang up | - | - | - |
| 70 | APB slave - TOP fabric non-AXI slaves - MEM_MASK_4KB, 32'h2701_6000 (PERI_GPIO6) | 不能访问 hang up | - | - | - |
| 71 | APB slave - TOP fabric non-AXI slaves - MEM_MASK_4KB, 32'h2701_5000 (PERI_GPIO5) | 不能访问 hang up | - | - | - |
| 72 | APB slave - TOP fabric non-AXI slaves - MEM_MASK_4KB, 32'h2701_4000 (PERI_GPIO4) | 不能访问 hang up | - | - | - |
| 73 | APB slave - TOP fabric non-AXI slaves - MEM_MASK_4KB, 32'h2701_3000 (PERI_GPIO3) | 不能访问 hang up | - | - | - |
| 74 | APB slave - TOP fabric non-AXI slaves - MEM_MASK_4KB, 32'h2701_2000 (PERI_GPIO2) | 不能访问 hang up | - | - | - |
| 75 | APB slave - TOP fabric non-AXI slaves - MEM_MASK_4KB, 32'h2701_1000 (PERI_GPIO1) | 不能访问 hang up | - | - | - |
| 76 | APB slave - TOP fabric non-AXI slaves - MEM_MASK_4KB, 32'h2701_0000 (PERI_GPIO0) | 不能访问 hang up | - | - | - |
| 77 | APB slave - TOP fabric non-AXI slaves - MEM_MASK_4KB, 32'h2700_2000 (PERI_WDT2) | 不能访问 hang up | - | - | - |
| 78 | APB slave - TOP fabric non-AXI slaves - MEM_MASK_4KB, 32'h2700_1000 (PERI_WDT1) | 不能访问 hang up | - | - | - |
| 79 | APB slave - TOP fabric non-AXI slaves - MEM_MASK_4KB, 32'h2700_0000 (PERI_WDT0) | 不能访问 hang up | - | - | - |
| 80 | APB slave - HSPERI fabric non-AXI slaves - MEM_MASK_64KB, 32'h2900_0000 （HSPERI_I2C0） | - | - | - | - |
| 81 | APB slave - HSPERI fabric non-AXI slaves - MEM_MASK_64KB, 32'h2901_0000 （HSPERI_I2C1） | - | - | - | - |
| 82 | APB slave - HSPERI fabric non-AXI slaves - MEM_MASK_64KB, 32'h2902_0000 (HSPERI_I2C2) | - | - | - | - |
| 83 | APB slave - HSPERI fabric non-AXI slaves - MEM_MASK_64KB, 32'h2903_0000 | - | - | - | - |
| 84 | APB slave - HSPERI fabric non-AXI slaves - MEM_MASK_64KB, 32'h2904_0000 | - | - | - | - |
| 85 | APB slave - HSPERI fabric non-AXI slaves - MEM_MASK_64KB, 32'h2905_0000 | - | - | - | - |
| 86 | APB slave - HSPERI fabric non-AXI slaves - MEM_MASK_64KB, 32'h2906_0000 | - | - | - | - |
| 87 | APB slave - HSPERI fabric non-AXI slaves - MEM_MASK_64KB, 32'h2907_0000 | - | - | - | - |
| 88 | APB slave - HSPERI fabric non-AXI slaves - MEM_MASK_64KB, 32'h2908_0000 | - | - | - | - |
| 89 | APB slave - HSPERI fabric non-AXI slaves - MEM_MASK_64KB, 32'h2909_0000 （HSPERI_I2C9） | - | - | - | - |
| 90 | APB slave - HSPERI fabric non-AXI slaves - MEM_MASK_64KB, 32'h292C_0000 （HSPERI_SPI_NAND） | - | - | - | - |
| 91 | APB slave - HSPERI fabric non-AXI slaves - MEM_MASK_64KB, 32'h290D_0000 （HSPERI_ETH0_CFG） | - | - | - | - |
| 92 | APB slave - HSPERI fabric non-AXI slaves - MEM_MASK_64KB, 32'h290E_0000 （HSPERI_ETH1_CFG） | - | - | - | - |
| 93 | APB slave - HSPERI fabric non-AXI slaves - MEM_MASK_64KB, 32'h290F_0000 （HSPERI_I2S_HDMI_AUDIO） | - | - | - | - |
| 94 | APB slave - HSPERI fabric non-AXI slaves - MEM_MASK_64KB, 32'h2910_0000 （HSPERI_I2S_GLOBAL） | - | - | - | - |
| 95 | APB slave - HSPERI fabric non-AXI slaves - MEM_MASK_64KB, 32'h2911_0000 （HSPERI_I2S1） | - | - | - | - |
| 96 | APB slave - HSPERI fabric non-AXI slaves - MEM_MASK_64KB, 32'h2912_0000 （HSPERI_I2S2） | - | - | - | - |
| 97 | APB slave - HSPERI fabric non-AXI slaves - MEM_MASK_64KB, 32'h2913_0000 （HSPERI_I2S3） | - | - | - | - |
| 98 | APB slave - HSPERI fabric non-AXI slaves - MEM_MASK_64KB, 32'h2914_0000 （HSPERI_I2S4） | - | - | - | - |
| 99 | APB slave - HSPERI fabric non-AXI slaves - MEM_MASK_64KB, 32'h2915_0000 （HSPERI_I2S5） | - | - | - | - |
| 100 | APB slave - HSPERI fabric non-AXI slaves - MEM_MASK_64KB, 32'h2916_0000 （HSPERI_I2S6） | - | - | - | - |
| 101 | APB slave - HSPERI fabric non-AXI slaves - MEM_MASK_64KB, 32'h2917_0000 （HSPERI_I2S_AUDSRC） | - | - | - | - |
| 102 | APB slave - HSPERI fabric non-AXI slaves - MEM_MASK_64KB, 32'h2917_8000 （HSPERI_I2S_DW_0） | - | - | - | - |
| 103 | APB slave - HSPERI fabric non-AXI slaves - MEM_MASK_64KB, 32'h2918_0000 （HSPERI_UART0） | - | - | - | - |
| 104 | APB slave - HSPERI fabric non-AXI slaves - MEM_MASK_64KB, 32'h2919_0000 （HSPERI_UART1） | - | - | - | - |
| 105 | APB slave - HSPERI fabric non-AXI slaves - MEM_MASK_64KB, 32'h291A_0000 （HSPERI_UART2） | - | - | - | - |
| 106 | APB slave - HSPERI fabric non-AXI slaves - MEM_MASK_64KB, 32'h291B_0000 （HSPERI_UART3） | - | - | - | - |
| 107 | APB slave - HSPERI fabric non-AXI slaves - MEM_MASK_64KB, 32'h291C_0000 （HSPERI_UART4） | - | - | - | - |
| 108 | APB slave - HSPERI fabric non-AXI slaves - MEM_MASK_64KB, 32'h291D_0000 （HSPERI_UART5） | - | - | - | - |
| 109 | APB slave - HSPERI fabric non-AXI slaves - MEM_MASK_64KB, 32'h291E_0000 （HSPERI_UART6） | - | - | - | - |
| 110 | APB slave - HSPERI fabric non-AXI slaves - MEM_MASK_64KB, 32'h291F_0000 （HSPERI_UART7） | - | - | - | - |
| 111 | APB slave - HSPERI fabric non-AXI slaves - MEM_MASK_64KB, 32'h2920_0000 （HSPERI_SPI0） | - | - | - | - |
| 112 | APB slave - HSPERI fabric non-AXI slaves - MEM_MASK_256KB, 32'h2921_0000 (HSPERI_SPI1) | - | - | - | - |
| 113 | APB slave - HSPERI fabric non-AXI slaves - MEM_MASK_64KB, 32'h2922_0000 (HSPERI_SPI2) | - | - | - | - |
| 114 | APB slave - HSPERI fabric non-AXI slaves - MEM_MASK_64KB, 32'h2923_0000 (HSPERI_SPI3) | - | - | - | - |
| 115 | APB slave - HSPERI fabric non-AXI slaves - MEM_MASK_64KB, 32'h2924_0000 (HSPERI_CAN0) | - | - | - | - |
| 116 | APB slave - HSPERI fabric non-AXI slaves - MEM_MASK_64KB, 32'h2925_0000 (HSPERI_CAN1) | - | - | - | - |
| 117 | APB slave - HSPERI fabric non-AXI slaves - MEM_MASK_64KB, 32'h292C_0000 (HSPERI_ROM) | - | - | - | - |
| 118 | APB slave - HSPERI fabric non-AXI slaves - MEM_MASK_64KB, 32'h2930_0000 (HSPERI_EMMC_CFG) | - | - | - | - |
| 119 | APB slave - HSPERI fabric non-AXI slaves - MEM_MASK_64KB, 32'h2931_0000 (HSPERI_SD0_CFG) | - | - | - | - |
| 120 | APB slave - HSPERI fabric non-AXI slaves - MEM_MASK_64KB, 32'h2932_0000 (HSPERI_SD1_CFG) | - | - | - | - |
| 121 | APB slave - HSPERI fabric non-AXI slaves - MEM_MASK_64KB, 32'h2933_0000 (HSPERI_SDMA0_CFG) | - | - | - | - |
| 122 | APB slave - HSPERI fabric non-AXI slaves - MEM_MASK_64KB, 32'h2934_0000 (HSPERI_SDMA1_CFG) | - | - | - | - |
| 123 | APB slave - HSPERI fabric non-AXI slaves - MEM_MASK_64KB, 32'h293A_F000 (HSPERI_SRAM) | - | - | - | - |
| 124 | APB slave - HSPERI fabric non-AXI slaves - MEM_MASK_64KB, 32'h293B_0000 (HSPERI_APB_REG) | - | - | - | - |
| 125 | APB slave - HSPERI fabric non-AXI slaves - MEM_MASK_64KB, 32'h3000_0000 (HSPERI_SPI_NOR) | - | - | - | - |

### DDR Firewall（3 项）

| No | 测试目的 | 预期结果 | 标签 | CA55 | 备注 |
|----|----------|----------|------|------|------|
| 43 | DDR firewall - secure region | Non-secure CPU failed to read secure dram. 非安全状态下cpu访问安全dram 区域失败 | 使能DDR FW后会卡死，没有配置新添加的0x100寄存器导致。 配置完0x100寄存器后，配置相关secure region配置，测试结果DDR fw未生效。 DDR配置现在是从0x0开始算，不同于A2从DDR基地址开始算。 | - | - |
| 44 | DDR firewall - dirty region | Non-secure CPU failed to read secure dram. 非安全状态下cpu访问安全dram 区域失败,从 dirty region 返回数据 | - | - | - |
| 51 | DDR firewall obfuscation | obfuscation使能后数据读写正常 抓波形观察fw之后的数据是否被打乱 | - | - | - |

### ROM Firewall（3 项）

| No | 测试目的 | 预期结果 | 标签 | CA55 | 备注 |
|----|----------|----------|------|------|------|
| 134 | Rom firewall - rom post mask 预定义区域 | 相应区域在non-secure world 访问返回0, 如果有require irq则会收到中断 | 异常访问会卡死重定向的地址有问题DE0.54已修复，异常访问重定向至rom首地址 | - | - |
| 135 | Rom firewall - rom post mask region read lock | 相应区域访问返回0（non-secure/secure） | - | - | - |
| 136 | Rom firewall - rom post mask - region programable (自定义postmask 区域) | 相应区域在non-secure world 访问返回0，如果有require irq则会收到中断 | - | - | - |

### RTC Firewall（3 项）

| No | 测试目的 | 预期结果 | 标签 | CA55 | 备注 |
|----|----------|----------|------|------|------|
| 40 | rtc firewall - RTC_fw_reg | - | RTC_secure 默认为0，是secure 的，mcu 没有ns/s的区分，默认是ns的，默认情况下mcu不能写 只能读fw寄存器，需要cA55 配置该寄存器为 non-secure 后，mcu才能进行配置 | - | - |
| 41 | rtc firewall - FabFW_RTC_tz_s | 写不生效，读正常 | #NAME? | - | - |
| 42 | rtc firewall - FabFW_RTC_lock | 读写卡住 | 测试结果读写均为卡住 | - | - |

### Debug Protection Firewall（8 项）

| No | 测试目的 | 预期结果 | 标签 | CA55 | 备注 |
|----|----------|----------|------|------|------|
| 126 | dbg prot firewall - 状态查询 | OTP设置的DID优先级更高，结果符合预期 | - | - | - |
| 127 | dbg prot firewall - debug mode - protect mode | - | - | - | - |
| 128 | dbg prot firewall - OTP key | 解锁成功 | - | - | - |
| 129 | dbg prot firewall - sha compare | 解锁成功 | - | - | - |
| 130 | dbg prot firewall - REE 解锁 | - | - | - | - |
| 131 | dbg prot firewall - TEE 解锁 | - | - | - | - |
| 132 | dbg prot firewall - SEE 解锁 | - | - | - | - |
| 133 | dbg prot firewall - TST 解锁 | - | - | - | - |

### Master Firewall（5 项）

| No | 测试目的 | 预期结果 | 标签 | CA55 | 备注 |
|----|----------|----------|------|------|------|
| 45 | Master firewall - DDR fabric - access | 收到 ddr firewall 中断 | - | - | - |
| 46 | Master firewall - DDR fabric - access | 收到 ddr firewall 中断 | - | - | - |
| 47 | Master firewall - DDR fabric - access | 收到 ddr firewall 中断 | - | - | - |
| 48 | Master firewall - DDR fabric - access | 收到 ddr firewall 中断 | - | - | - |
| 49 | Master firewall - DDR fabric - access | 收到 ddr firewall 中断 | - | - | - |

### Fabric Firewall（2 项）

| No | 测试目的 | 预期结果 | 标签 | CA55 | 备注 |
|----|----------|----------|------|------|------|
| 38 | fab firewall - fabFW_RTC_ar_ns | mcu 中读取到0 | - | - | - |
| 39 | fab firewall - fabFW_RTC_aw_ns | - | - | - | - |

### SEC_TOP（7 项）

| No | 测试目的 | 预期结果 | 标签 | CA55 | 备注 |
|----|----------|----------|------|------|------|
| 137 | sec_top - sys_ctrl - lock bit | sys_ctrl reg 写不成功 | - | - | - |
| 138 | sec_top - sec_ctrl - secureboot done | rom 所有区域的 post mask 都enable | - | - | - |
| 139 | sec_top - sec_ctrl - AP_c0_boot_adr_sel | ap cA55 core0 reset 后，不会执行bl1 | - | - | - |
| 140 | sec_top - sec_ctrl - embedded root key | 读取和rtl 对比，一致 | - | - | - |
| 141 | sec_top - sec_ctrl - embedded root key - read_lock | 读取到0 | - | - | - |
| 142 | sec_top - sec_ctrl - dis_enclave | 非安全world也能访问spacc等安全ip | - | - | - |
| 143 | sec_top - sec_ctrl - dis_enclave - write lock | dis_enclave 不能被写 | - | - | - |

### C906 Firewall（2 项）

| No | 测试目的 | 预期结果 | 标签 | CA55 | 备注 |
|----|----------|----------|------|------|------|
| 144 | C906 Firewall - 关闭gate | - | - | - | - |
| 145 | C906 Firewall - 开启gate | - | - | - | - |

### TPU / SRAM Region（4 项）

| No | 测试目的 | 预期结果 | 标签 | CA55 | 备注 |
|----|----------|----------|------|------|------|
| 36 | Master control(TPU-scaler) - TPU fabric - read access | - | - | - | - |
| 37 | Master control (TPU-scaler) - TPU fabric - write access | - | - | - | - |
| 52 | Only secure CPU can access secure TPU sram region | Non-secure CPU failed to read secure sram. 非安全状态下cpu访问安全sram区域失败 | - | - | - |
| 53 | Only secure CPU can access secure RTC sram region | Non-secure CPU failed to read secure sram. 非安全状态下cpu访问安全sram区域失败 | - | - | - |

### Illegal Slave Space（1 项）

| No | 测试目的 | 预期结果 | 标签 | CA55 | 备注 |
|----|----------|----------|------|------|------|
| 50 | Illegal slave space（ddr mem space） access info | 有访问的地址和长度，以及是读还是写 | l 组成：aw_hit_SecRegion_index[7:0],awprot_m[2:0],awid_m[14:0] u_chip_top.chip_core.A_ddr_top_fab_pr_wrap.u_ddr_top_fab_pwr_wrap.u_ddr_top_interconnect.u_sec_ddr_firewall.u_reg_sec_ddr_firewall.selected_itr_log_h[31:0] u_chip_top.chip_core.A_ddr_top_fab_pr_wrap.u_ddr_top_fab_pwr_wrap.u_ddr_top_interconnect.u_sec_ddr_firewall.u_reg_sec_ddr_firewall.selected_itr_log_l[31:0] | - | - |


## 5. 附录：表格后续补充项

| 行号 | No | 测试目的 | 标签 |
|------|----|----------|------|
| 249 | 1 | Check randomize value generated by TRNG | TRNG |
| 250 | 1 | pka test_rsa2k_verify | PKA |
| 251 | 2 | pka test_rsa2k_sign | - |
| 252 | 3 | pka test_sm2_sign | - |
| 253 | 4 | pka test_sm2_verify | - |

## 6. 使用建议

- 批量防火墙回归：优先执行 [test_cases.md](../test_cases.md) 中的 bmtest 命令
- 全量官方对齐：按本文档分类逐项核对，表格中有但 bmtest 未封装的项目需辅助验证
- 每条用例执行后建议 `reset`，避免 EL 切换后系统挂死影响后续项
- 原始步骤、PLD/FPGA 多平台结果以 `security_testcase.xlsx` 为准
