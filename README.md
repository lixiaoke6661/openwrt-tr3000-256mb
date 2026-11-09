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
- A **random 16-character root password** is generated on first boot and written to
  `/root/.root-initial-password` (mode 600). Log in with it over SSH/console, then
  **change it immediately** and delete that file:

```sh
cat /root/.root-initial-password
passwd
rm -f /root/.root-initial-password
```

  No usable password is baked into the image or this repository.
- Web terminal (ttyd, port 7681) is **disabled by default** — upstream ships it without
  a credential, which combined with an empty-password root is an unauthenticated root shell
  on the LAN. To re-enable it, set a credential first:

```sh
uci set ttyd.@ttyd[0].credential='admin:YourPassword'
uci set ttyd.@ttyd[0].enable='1'
uci commit ttyd
/etc/init.d/ttyd enable && /etc/init.d/ttyd start
```

## Side-router / main-router mode

The image boots in **side-router** mode: `192.168.5.1`, gateway/DNS `192.168.1.1`, DHCP off.
Switch with the bundled helper:

```sh
router-mode status          # show current preset
router-mode main            # 192.168.1.1, no gateway, DHCP on
router-mode side            # back to 192.168.5.1, DHCP off
router-mode main -n         # write config only, apply on next reboot
```

The LAN IP changes immediately, so reconnect on the new address. Then configure WAN
(PPPoE/DHCP) in LuCI -> Network -> Interfaces.

Manual equivalent:

```sh
uci set network.lan.ipaddr='192.168.1.1'
uci delete network.lan.gateway
uci delete network.lan.dns
uci set dhcp.lan.ignore='0'
uci commit
/etc/init.d/network restart && /etc/init.d/dnsmasq restart
```

## What is included

- Official OpenWrt `v25.12.6`, target `mediatek/filogic`, profile `cudy_tr3000-256mb-v1`
- LuCI + Chinese (base/firewall/package-manager/ttyd)
- PPPoE / IPv6 protocol support
- `kmod-tun`, `kmod-nft-tproxy`, `ip-full` (side-router/proxy building blocks)
- `curl`, `openssh-sftp-server`
- `router-mode` helper for side-router / main-router switching

## Security notes

- Built from `github.com/openwrt/openwrt` at the tag you specify.
- No third-party feeds, no `install.sh`, no `--no-check-certificate`.
- Actions are official (`actions/checkout@v4`, `actions/upload-artifact@v4`).
- Artifacts include `SHA256SUMS`, `config.buildinfo`, and `.manifest` for audit.
- Userland is byte-identical to the official `25.12.6` image for this profile (only `wpad` differs, by design).
- First boot (`files/etc/uci-defaults/95-secure-defaults`): disables ttyd, generates a **random**
  root password (stored on-device only, never in the image), and removes
  `/etc/apk/keys/public-key.pem` — the build runner's local package-signing
  key that `base-files` installs on non-buildbot builds. Only the official
  `openwrt-25.12.pem` trust anchor is kept.
- Images are **not** cryptographically signed (same as official OpenWrt sysupgrade images);
  verify `SHA256SUMS` before flashing.
