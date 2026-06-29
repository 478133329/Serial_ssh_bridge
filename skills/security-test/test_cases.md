# Security 测试命令清单

备注中有 SKIP 的项直接跳过，不发送命令。

| Index | 模块 | 名称 | 命令 | 备注 |
| 0 | peri | PERI_INTC3 | `peri_secure 0` | |
| 1 | peri | PERI_INTC2 | `peri_secure 1` | |
| 2 | peri | PERI_INTC1 | `peri_secure 2` | |
| 3 | peri | PERI_INTC0 | `peri_secure 3` | |
| 4 | peri | PERI_OTP | `peri_secure 4` | SKIP |
| 5 | peri | PERI_MAILBOX | `peri_secure 5` | |
| 6 | peri | PERI_SARADC | `peri_secure 6` | |
| 7 | peri | PERI_TEMPSEN | `peri_secure 7` | |
| 8 | peri | PERI_PMCTL | `peri_secure 8` | |
| 9 | peri | PERI_TIMER | `peri_secure 9` | |
| 10 | peri | PERI_PWM4 | `peri_secure 10` | |
| 11 | peri | PERI_PWM3 | `peri_secure 11` | |
| 12 | peri | PERI_PWM2 | `peri_secure 12` | |
| 13 | peri | PERI_PWM1 | `peri_secure 13` | |
| 14 | peri | PERI_PWM0 | `peri_secure 14` | |
| 15 | peri | PERI_EFUSE | `peri_secure 15` | |
| 16 | peri | PERI_KEYSCAN | `peri_secure 16` | |
| 17 | peri | PERI_WGN1 | `peri_secure 17` | |
| 18 | peri | PERI_WGN0 | `peri_secure 18` | |
| 19 | peri | PERI_GPIO5 | `peri_secure 19` | |
| 20 | peri | PERI_GPIO4 | `peri_secure 20` | |
| 21 | peri | PERI_GPIO3 | `peri_secure 21` | |
| 22 | peri | PERI_GPIO2 | `peri_secure 22` | |
| 23 | peri | PERI_GPIO1 | `peri_secure 23` | |
| 24 | peri | PERI_GPIO0 | `peri_secure 24` | |
| 25 | peri | PERI_WDT2 | `peri_secure 25` | |
| 26 | peri | PERI_WDT1 | `peri_secure 26` | |
| 27 | peri | PERI_WDT0 | `peri_secure 27` | |
| 28 | hsperi0 | HSPERI_SPI1 | `hsperi_secure 1 0` | |
| 29 | hsperi0 | HSPERI_SPI0 | `hsperi_secure 1 1` | |
| 30 | hsperi0 | HSPERI_UART7 | `hsperi_secure 1 2` | |
| 31 | hsperi0 | HSPERI_UART6 | `hsperi_secure 1 3` | |
| 32 | hsperi0 | HSPERI_UART5 | `hsperi_secure 1 4` | |
| 33 | hsperi0 | HSPERI_UART4 | `hsperi_secure 1 5` | |
| 34 | hsperi0 | HSPERI_UART3 | `hsperi_secure 1 6` | |
| 35 | hsperi0 | HSPERI_UART2 | `hsperi_secure 1 7` | |
| 36 | hsperi0 | HSPERI_UART1 | `hsperi_secure 1 8` | |
| 37 | hsperi0 | HSPERI_UART0 | `hsperi_secure 1 9` | SKIP |
| 38 | hsperi0 | HSPERI_I2S_DW | `hsperi_secure 1 10` | |
| 39 | hsperi0 | HSPERI_I2S_AUDSRC | `hsperi_secure 1 11` | |
| 40 | hsperi0 | HSPERI_I2S5 | `hsperi_secure 1 12` | |
| 41 | hsperi0 | HSPERI_I2S4 | `hsperi_secure 1 13` | |
| 42 | hsperi0 | HSPERI_I2S3 | `hsperi_secure 1 14` | |
| 43 | hsperi0 | HSPERI_I2S2 | `hsperi_secure 1 15` | |
| 44 | hsperi0 | HSPERI_I2S1 | `hsperi_secure 1 16` | |
| 45 | hsperi0 | HSPERI_I2S0 | `hsperi_secure 1 17` | |
| 46 | hsperi0 | HSPERI_I2S_GLOBAL | `hsperi_secure 1 18` | |
| 47 | hsperi0 | HSPERI_ETH1_CFG | `hsperi_secure 1 19` | |
| 48 | hsperi0 | HSPERI_ETH0_CFG | `hsperi_secure 1 20` | |
| 49 | hsperi0 | HSPERI_SPI_NAND | `hsperi_secure 1 21` | |
| 50 | hsperi0 | HSPERI_I2C9 | `hsperi_secure 1 22` | |
| 51 | hsperi0 | HSPERI_I2C8 | `hsperi_secure 1 23` | |
| 52 | hsperi0 | HSPERI_I2C7 | `hsperi_secure 1 24` | |
| 53 | hsperi0 | HSPERI_I2C6 | `hsperi_secure 1 25` | |
| 54 | hsperi0 | HSPERI_I2C5 | `hsperi_secure 1 26` | |
| 55 | hsperi0 | HSPERI_I2C4 | `hsperi_secure 1 27` | |
| 56 | hsperi0 | HSPERI_I2C3 | `hsperi_secure 1 28` | |
| 57 | hsperi0 | HSPERI_I2C2 | `hsperi_secure 1 29` | |
| 58 | hsperi0 | HSPERI_I2C1 | `hsperi_secure 1 30` | |
| 59 | hsperi0 | HSPERI_I2C0 | `hsperi_secure 1 31` | |
| 60 | hsperi1 | HSPERI_ROM | `hsperi_secure 0 0` | |
| 61 | hsperi1 | HSPERI_SDMA1_CFG | `hsperi_secure 0 1` | |
| 62 | hsperi1 | HSPERI_SDMA0_CFG | `hsperi_secure 0 2` | |
| 63 | hsperi1 | HSPERI_SD2_CFG | `hsperi_secure 0 3` | |
| 64 | hsperi1 | HSPERI_SD1_CFG | `hsperi_secure 0 4` | |
| 65 | hsperi1 | HSPERI_SD0_CFG | `hsperi_secure 0 5` | |
| 66 | hsperi1 | HSPERI_EMMC_CFG | `hsperi_secure 0 6` | |
| 67 | hsperi1 | HSPERI_CAN1 | `hsperi_secure 0 7` | |
| 68 | hsperi1 | HSPERI_CAN0 | `hsperi_secure 0 8` | |
| 69 | hsperi1 | HSPERI_SPI3 | `hsperi_secure 0 9` | |
| 70 | hsperi1 | HSPERI_SPI2 | `hsperi_secure 0 10` | |
| 71 | ddr_firewall | DDR_SECURE_REGION1 | `dram_secure_region 0` | |
| 72 | ddr_firewall | DDR_SECURE_REGION2 | `dram_secure_region 1` | |
| 73 | ddr_firewall | DDR_SECURE_REGION3 | `dram_secure_region 2` | |
| 74 | ddr_firewall | DDR_SECURE_REGION4 | `dram_secure_region 3` | |
| 75 | ddr_firewall | DDR_SECURE_REGION5 | `dram_secure_region 4` | |
| 76 | ddr_firewall | DDR_SECURE_REGION6 | `dram_secure_region 5` | |
| 77 | ddr_firewall | DDR_SECURE_REGION7 | `dram_secure_region 6` | |
| 78 | ddr_firewall | DDR_SECURE_REGION8 | `dram_secure_region 7` | |
| 79 | ddr_firewall | DDR_OBFUSCATION | `dram_obfuscation 0` | |
| 80 | rom_firewall | ROM_SECURE_REGION0 | `rom_secure_region 0` | |
| 81 | rom_firewall | ROM_SECURE_REGION1 | `rom_secure_region 1` | |
| 82 | rom_firewall | ROM_SECURE_REGION2 | `rom_secure_region 2` | |
| 83 | rom_firewall | ROM_SECURE_REGION3 | `rom_secure_region 3` | |
| 84 | rom_firewall | ROM_SECURE_REGION4 | `rom_secure_region 4` | |
| 85 | rom_firewall | ROM_SECURE_REGION5 | `rom_secure_region 5` | |
| 86 | rom_firewall | ROM_SECURE_REGION6 | `rom_secure_region 6` | |
| 87 | rom_firewall | ROM_SECURE_REGION7 | `rom_secure_region 7` | |
| 88 | rom_firewall | ROM_SECURE_REGION8 | `rom_secure_region 8` | |
| 89 | rom_firewall | ROM_SECURE_REGION9 | `rom_secure_region 9` | |
| 90 | rom_firewall | ROM_SECURE_REGION10 | `rom_secure_region 10` | |
| 91 | rom_firewall | ROM_SECURE_REGION11 | `rom_secure_region 11` | |
| 92 | rom_firewall | ROM_SECURE_REGION12 | `rom_secure_region 12` | |
| 93 | rom_firewall | ROM_SECURE_REGION13 | `rom_secure_region 13` | |
| 94 | rom_firewall | ROM_SECURE_REGION14 | `rom_secure_region 14` | |
| 95 | rom_firewall | ROM_SECURE_REGION15 | `rom_secure_region 15` | SKIP |
| 96 | rom_firewall | ROM_SECURE_REGION16 | `rom_secure_region 16` | |
| 97 | rom_firewall | ROM_SECURE_REGION17 | `rom_secure_region 17` | |
| 98 | rom_firewall | ROM_SECURE_REGION18 | `rom_secure_region 18` | |
| 99 | rom_firewall | ROM_SECURE_REGION19 | `rom_secure_region 19` | |
| 100 | rom_firewall | ROM_SECURE_REGION20 | `rom_secure_region 20` | |
| 101 | rom_firewall | ROM_SECURE_REGION21 | `rom_secure_region 21` | |
| 102 | rom_firewall | ROM_SECURE_REGION22 | `rom_secure_region 22` | |
| 103 | rom_firewall | ROM_SECURE_REGION23 | `rom_secure_region 23` | |
| 104 | rom_firewall | ROM_READ_LOCK0 | `rom_read_lock 0` | |
| 105 | rom_firewall | ROM_READ_LOCK1 | `rom_read_lock 1` | |
| 106 | rom_firewall | ROM_READ_LOCK2 | `rom_read_lock 2` | |
| 107 | rom_firewall | ROM_READ_LOCK3 | `rom_read_lock 3` | |
| 108 | rom_firewall | ROM_READ_LOCK4 | `rom_read_lock 4` | |
| 109 | rom_firewall | ROM_READ_LOCK5 | `rom_read_lock 5` | |
| 110 | rom_firewall | ROM_READ_LOCK6 | `rom_read_lock 6` | |
| 111 | rom_firewall | ROM_READ_LOCK7 | `rom_read_lock 7` | |
| 112 | rom_firewall | ROM_READ_LOCK8 | `rom_read_lock 8` | |
| 113 | rom_firewall | ROM_READ_LOCK9 | `rom_read_lock 9` | |
| 114 | rom_firewall | ROM_READ_LOCK10 | `rom_read_lock 10` | |
| 115 | rom_firewall | ROM_READ_LOCK11 | `rom_read_lock 11` | |
| 116 | rom_firewall | ROM_READ_LOCK12 | `rom_read_lock 12` | |
| 117 | rom_firewall | ROM_READ_LOCK13 | `rom_read_lock 13` | |
| 118 | rom_firewall | ROM_READ_LOCK14 | `rom_read_lock 14` | |
| 119 | rom_firewall | ROM_READ_LOCK15 | `rom_read_lock 15` | |
| 120 | rom_firewall | ROM_READ_LOCK16 | `rom_read_lock 16` | |
| 121 | rom_firewall | ROM_READ_LOCK17 | `rom_read_lock 17` | |
| 122 | rom_firewall | ROM_READ_LOCK18 | `rom_read_lock 18` | |
| 123 | rom_firewall | ROM_READ_LOCK19 | `rom_read_lock 19` | |
| 124 | rom_firewall | ROM_READ_LOCK20 | `rom_read_lock 20` | |
| 125 | rom_firewall | ROM_READ_LOCK21 | `rom_read_lock 21` | |
| 126 | rom_firewall | ROM_READ_LOCK22 | `rom_read_lock 22` | |
| 127 | rom_firewall | ROM_READ_LOCK23 | `rom_read_lock 23` | |
| 128 | rom_firewall | ROM_DEFINE_REGION | `rom_define_region 0` | |
