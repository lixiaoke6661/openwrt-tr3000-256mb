#!/usr/bin/env python3
"""把 MTK HNAT 驱动适配到官方 OpenWrt 6.12 内核。幂等：重复执行安全。

三处修复：
  1. 补 mtk_eth_dbg.h / mtk_eth_reset.h（HNAT 只 include，未用其中符号）
  2. mtk_eth_soc.c: err_deinit_ppe 标签移入 #if !defined(HNAT) 块内
  3. hnat.h: 补 NETSYS_V3 的 FE_INT2 寄存器默认宏（TR3000 是 V2，不会执行该分支）

注意：第 3 条刻意不改 hnat.c 的结构，避免破坏括号/函数体。
"""
import glob
import os
import sys

BASE = os.path.expanduser("~/openq/openwrt/build_dir")
MARK = "OpenQ-HNAT-FIX"

STUB_DBG = """/* SPDX-License-Identifier: GPL-2.0 */
/* OpenQ stub: 官方 6.12 无此头，HNAT 仅 include 未用其符号 */
#ifndef _MTK_ETH_DBG_H
#define _MTK_ETH_DBG_H
#endif
"""
STUB_RST = """/* SPDX-License-Identifier: GPL-2.0 */
/* OpenQ stub: 官方 6.12 无此头，HNAT 仅 include 未用其符号 */
#ifndef _MTK_ETH_RESET_H
#define _MTK_ETH_RESET_H
#endif
"""

MACROS = """
/* %s: 官方 6.12 无 NETSYS_V3 的 FE_INT2 定义，补默认值。
 * TR3000 为 V2 硬件，该分支不会执行，仅需编译期可见。 */
#ifndef MTK_FE_INT_ENABLE2
#define MTK_FE_INT_ENABLE2 0x000
#endif
#ifndef MTK_FE_INT2_PPE0_FLOW_CHK
#define MTK_FE_INT2_PPE0_FLOW_CHK 0
#endif
#ifndef MTK_FE_INT2_PPE1_FLOW_CHK
#define MTK_FE_INT2_PPE1_FLOW_CHK 0
#endif
""" % MARK


def find_kernel():
    for d in glob.glob(os.path.join(BASE, "target-*", "linux-*", "linux-6.12*")):
        if os.path.isdir(os.path.join(d, "drivers/net/ethernet/mediatek/mtk_hnat")):
            return d
    return None


def main():
    k = find_kernel()
    if not k:
        print("!! 找不到内核源码目录（是否还没执行 target/linux/prepare？）")
        return 1
    md = os.path.join(k, "drivers/net/ethernet/mediatek")
    changed = []

    # 1. 兼容头文件
    for name, body in (("mtk_eth_dbg.h", STUB_DBG), ("mtk_eth_reset.h", STUB_RST)):
        p = os.path.join(md, name)
        if not os.path.exists(p):
            open(p, "w").write(body)
            changed.append(name)

    # 2. err_deinit_ppe 标签
    p = os.path.join(md, "mtk_eth_soc.c")
    lines = open(p).read().split("\n")
    for i in range(len(lines) - 1):
        if lines[i].strip() == "err_deinit_ppe:" and lines[i + 1].strip().startswith(
            "#if !defined(CONFIG_NET_MEDIATEK_HNAT)"
        ):
            lines[i], lines[i + 1] = lines[i + 1], lines[i]
            open(p, "w").write("\n".join(lines))
            changed.append("mtk_eth_soc.c(label)")
            break

    # 3. hnat.h 补宏（不改 hnat.c 结构）
    p = os.path.join(md, "mtk_hnat/hnat.h")
    s = open(p).read()
    if "MTK_FE_INT_ENABLE2" not in s:
        open(p, "a").write(MACROS)
        changed.append("hnat.h(macros)")

    print("内核目录:", k)
    print("本次修改:", ", ".join(changed) if changed else "无（已是修复后状态）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
