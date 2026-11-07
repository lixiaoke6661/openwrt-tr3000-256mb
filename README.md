# OpenWrt 25.12.6 for Cudy TR3000 256MB v1

Minimal, reproducible OpenWrt build for `cudy,tr3000-256mb-v1` (UBI 230 MB layout).
No third-party feeds, no closed-source packages, no prebuilt binaries.

## Build

1. GitHub -> Actions -> **Build OpenWrt for Cudy TR3000 256MB** -> Run workflow.
2. Keep `ref = v25.12.6` (or set another official tag).
3. Wait for the job; download artifact `openwrt-v25.12.6-tr3000-256mb`.
4. Verify:

```sh
sha256sum -c SHA256SUMS
```

## Flash

The device currently runs Kwrt 24.10 on the same UBI layout. Flashing another
distribution does **not** need a U-Boot change.

```sh
# from your PC
scp openwrt-25.12.6-mediatek-filogic-cudy_tr3000-256mb-v1-squashfs-sysupgrade.bin root@192.168.5.1:/tmp/
ssh root@192.168.5.1
sysupgrade -n /tmp/openwrt-25.12.6-mediatek-filogic-cudy_tr3000-256mb-v1-squashfs-sysupgrade.bin
```

- `-n` = do not keep config (recommended when switching from Kwrt).
- If sysupgrade refuses due to image metadata, inspect the message before using `-F`.
- Keep a backup of the current system and the `Factory` partition.

Optional safer path: boot the generated `initramfs-kernel.bin` via TFTP first,
confirm LAN/WiFi works, then run sysupgrade.

## First boot

- LAN: `192.168.5.1` (preset as side-router), DHCP disabled.
- Set a root password immediately (LuCI -> System -> Administration).
- Web terminal: `http://192.168.5.1:7681` (ttyd, login with root).

## Switch to main-router mode

```sh
uci set network.lan.ipaddr='192.168.1.1'
uci set network.lan.gateway=''
uci set network.lan.dns=''
uci set dhcp.lan.ignore='0'
uci commit
/etc/init.d/network restart
/etc/init.d/dnsmasq restart
```

Then configure WAN (PPPoE/DHCP) in LuCI -> Network -> Interfaces.

## What is included

- Official OpenWrt `v25.12.6`, target `mediatek/filogic`, profile `cudy_tr3000-256mb-v1`
- LuCI + Chinese (base/firewall/package-manager/ttyd)
- PPPoE / IPv6 protocol support
- `kmod-tun`, `kmod-nft-tproxy`, `ip-full` (side-router/proxy building blocks)
- `curl`, `openssh-sftp-server`

## Security notes

- Built from `github.com/openwrt/openwrt` at the tag you specify.
- No third-party feeds, no `install.sh`, no `--no-check-certificate`.
- Actions are official (`actions/checkout@v4`, `actions/upload-artifact@v4`).
- Artifacts include `SHA256SUMS`, `config.buildinfo`, and `.manifest` for audit.
