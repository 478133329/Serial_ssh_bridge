#include "arch.h"
#include "boot_test.h"
#include "utils_def.h"
#include "uart.h"
#include "mmio.h"
#include "reg_sec_fab_firewall.h"

#define MAP_DEVICE	MAP_REGION_FLAT(0, 0x80000000,		\
					MT_DEVICE | MT_RW | MT_SECURE)
#define MAP_DRAM	MAP_REGION_FLAT(DRAM_BASE, 0x800000000,	\
					MT_MEMORY | MT_RW | MT_NS)

typedef int (*test_func_t)(void);

extern void switch_el3_to_s_el1(uint64_t dummy, uintptr_t func);
extern void switch_el3_to_el1(uint64_t dummy, uintptr_t func);
extern int get_arm_current_el(void);

int el_switch_cnt;

void el1_callback(void)
{
    el_switch_cnt++;
}

void s_el1_callback(void)
{
    el_switch_cnt++;
}

int test_exception_level(void)
{
    uint32_t spsr;

    printf("Before switch, CurrentEL=%d\n", get_arm_current_el());

#if 0
    spsr = SPSR_64(MODE_EL2, MODE_SP_ELX, DISABLE_ALL_EXCEPTIONS);
    switch_el3_to_s_el1(spsr, (uintptr_t)s_el1_callback);
#else
    spsr = SPSR_64(MODE_EL1, MODE_SP_ELX, DISABLE_ALL_EXCEPTIONS);
    switch_el3_to_el1(spsr, (uintptr_t)s_el1_callback);
#endif

    printf("After switch, CurrentEL=%d\n", get_arm_current_el());
    printf("test_exception_level: el_switch_cnt=%d\n", el_switch_cnt);

    return 0;
}

int test_ns_access_secure_sram(void)
{
    int res = 0;
    uint32_t spsr, val;
    uintptr_t test_addr = (uintptr_t)SRAM_BASE;
    uint32_t old_value = 0xfedcba98;

    printf("Before switch, CurrentEL=%d\n", get_arm_current_el());

    // Remove CA53 forced secure read
    mmio_write_32(FAB_FIREWALL_BASE+SEC_FAB_FIREWALL_FABFW_HSPERI_M1_AR_NS, 0x000007FD);

    // Set secure sram access
    mmio_write_32(FAB_FIREWALL_BASE+SEC_FAB_FIREWALL_REG_SRAM_S_TZ_S, 0xFFFFFFFF);

    // write sram
    mmio_write_32(test_addr, 0xdeadbeef/*0x76543210*/);
    mmio_write_32(test_addr+4, old_value);
    
    // Check write succeed
    res = (mmio_read_32(test_addr+4)==old_value) ? res : -1;

    printf("  sec_fab [0x%08x]=0x%08xxn", FAB_FIREWALL_BASE+SEC_FAB_FIREWALL_FABFW_HSPERI_M1_AR_NS, mmio_read_32(FAB_FIREWALL_BASE+SEC_FAB_FIREWALL_FABFW_HSPERI_M1_AR_NS));
    printf("  sec_fab [0x%08x]=0x%08x\n", FAB_FIREWALL_BASE+SEC_FAB_FIREWALL_REG_SRAM_S_TZ_S, mmio_read_32(FAB_FIREWALL_BASE+SEC_FAB_FIREWALL_REG_SRAM_S_TZ_S));
    printf("  sram [%p]=0x%x\n", (void *)test_addr, mmio_read_32(test_addr));
    printf("  sram [%p]=0x%x\n", (void *)(test_addr+4), mmio_read_32(test_addr+4));

    spsr = SPSR_64(MODE_EL1, MODE_SP_ELX, DISABLE_ALL_EXCEPTIONS);
    switch_el3_to_el1(spsr, (uintptr_t)s_el1_callback);

    // Check exception level
    res = (get_arm_current_el()==1) ? res : -1;
    
    // Check illegal read
    val = mmio_read_32(test_addr+4);
    res = (val != old_value) ? res : -1;

    printf("After switch, CurrentEL=%d\n", get_arm_current_el());
    printf("  test_exception_level: el_switch_cnt=%d\n", el_switch_cnt);

    printf("  sram [%p]=0x%x\n", (void *)test_addr, mmio_read_32(test_addr));
    printf("  sram [%p]=0x%x\n", (void *)(test_addr+4), mmio_read_32(test_addr+4));

    return res;
}

int test_ns_access_secure_dram(void)
{
    int res = 0;
    uint32_t spsr;
    uint64_t dram_start = 0x101000000ULL;   // offset 16MB
    uint64_t dram_end = (dram_start + (1<<12));

    printf("Before switch, CurrentEL=%d\n", get_arm_current_el());

    // Remove CA53 forced secure read
    mmio_write_32(FAB_FIREWALL_BASE+SEC_FAB_FIREWALL_FABFW_HSPERI_M1_AR_NS, 0x000007FD);

    // Set secure dram region 0, 4kB aligned
    mmio_write_32(0x020a0008, (uint32_t)(dram_start>>12));
    mmio_write_32(0x020a0028, (uint32_t)(dram_end>>12));
    
    // enable region0
    mmio_write_32(0x020a0000, 1UL | (1<<16));

    // Write dram
    mmio_write_32(dram_start, 0x76543210);
    mmio_write_32(dram_start+4, 0xfedcba98);

    printf("  ddr_fab [0x020a0000]=0x%x\n", mmio_read_32(0x020a0000));
    printf("  ddr_fab [0x020a0008]=0x%x\n", mmio_read_32(0x020a0008));
    printf("  ddr_fab [0x020a0028]=0x%x\n", mmio_read_32(0x020a0028));
    printf("  dram [%p]=0x%x\n", (void *)dram_start, mmio_read_32(dram_start));
    printf("  dram [%p]=0x%x\n", (void *)dram_start+4, mmio_read_32(dram_start+4));

    spsr = SPSR_64(MODE_EL1, MODE_SP_ELX, DISABLE_ALL_EXCEPTIONS);
    switch_el3_to_el1(spsr, (uintptr_t)s_el1_callback);

    printf("After switch, CurrentEL=%d\n", get_arm_current_el());
    printf("  test_exception_level: el_switch_cnt=%d\n", el_switch_cnt);

    printf("  dram [%p]=0x%x\n", (void *)dram_start, mmio_read_32(dram_start));
    printf("  dram [%p]=0x%x\n", (void *)dram_start+4, mmio_read_32(dram_start+4));

    return res;
}

static test_func_t test_func_table[] = {
    test_ns_access_secure_sram,
    /*test_ns_access_secure_dram,*/
};

#ifndef BUILD_TEST_CASE_all
int testcase_main(void)
{
    int i;
    int ret = 0;

    for (i = 0; i < ARRAY_SIZE(test_func_table); i++) {
        ret |= test_func_table[i]();
    }

    printf("\nFINAL TEST RESULT");
    printf("[%s]\n", ret ? "FAIL" : "PASS");

    return ret;
}
#endif /* BUILD_TEST_CASE_all */
