#!/usr/bin/env bash
# OpenQ 出包（无 HNAT，软件 flow offloading）
# 用法: bash build-release.sh [jobs]   默认 2
set -uo pipefail
JOBS="${1:-2}"
export PATH="$(printf '%s' "$PATH" | tr ':' '\n' | grep -v '^/mnt/' | paste -sd: -)"
export CCACHE_DIR="$HOME/.ccache" CCACHE_MAXSIZE=20G
export PATH="/usr/lib/ccache:$PATH"
cd "$HOME/openq/openwrt" || exit 1
LOG="$HOME/openq/build-release.log"
: > "$LOG"

say() { echo "$*" | tee -a "$LOG"; }
run() {
    local tag="$1"; shift
    say ""
    say "===== $tag 开始 $(date '+%H:%M:%S') ====="
    make -j"$JOBS" "$@" >> "$LOG" 2>&1
    local rc=$?
    say "===== $tag 结束 rc=$rc  $(date '+%H:%M:%S') ====="
    return $rc
}

say "RELEASE BUILD START $(date '+%H:%M:%S')  jobs=$JOBS"

# mkimage：系统版 2025.10，与 OpenWrt 期望一致
ln -sfn /usr/bin/mkimage staging_dir/host/bin/mkimage
command -v mkimage >/dev/null || { say "!! 缺 mkimage: sudo apt-get install -y u-boot-tools"; exit 20; }

# 1. 配置
say "--- 应用配置"
REPO="${REPO:-/mnt/e/WorkBuddy/projects/openwrt-tr3000-256mb}"
cat "$REPO/configs/cudy_tr3000-256mb-v1.config" > .config
make defconfig >> "$LOG" 2>&1 || { say "!! defconfig 失败"; exit 21; }

# 1b. 复制文件覆盖层（含首启调优 / flow offloading 脚本）
rm -rf files
cp -r "$REPO/files" .
find files/etc/uci-defaults -type f -exec chmod 755 {} \; 2>/dev/null || true
say "files/ 已同步: $(ls files/etc/uci-defaults 2>/dev/null | tr '\n' ' ')"

# 2. 内核 prepare（HNAT 补丁已移除，走纯官方内核）
run "KERNEL-PREPARE" target/linux/prepare || exit 22

# 3. 内核编译
run "KERNEL" target/linux/compile || exit 23

# 4. 完整镜像
run "IMAGE" || exit 24

# 5. 产物
say ""
say "--- 产物 ---"
find bin/targets/mediatek/filogic -maxdepth 1 \( -name '*.bin' -o -name '*.itb' \) 2>/dev/null \
    | while read -r f; do say "$(du -h "$f" | cut -f1)  $(basename "$f")"; done
say "RELEASE BUILD DONE $(date '+%H:%M:%S')"
