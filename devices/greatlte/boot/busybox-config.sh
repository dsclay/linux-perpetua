#!/bin/sh
# Minimal busybox for the rescue initramfs. Run inside the busybox source tree.
set -eu
make allnoconfig >/dev/null
for k in STATIC BUSYBOX FEATURE_INSTALLER INSTALL_APPLET_SYMLINKS INSTALL_APPLET_DONT \
         SH_IS_ASH SH_IS_NONE ASH ASH_ECHO ASH_TEST ASH_OPTIMIZE_FOR_SIZE TEST ECHO \
         MOUNT LS CAT DMESG UNAME MKDIR SLEEP TAIL SETSID; do
	sed -i "/^# CONFIG_$k is not set\$/d;/^CONFIG_$k=/d" .config
done
cat >> .config <<'CFG'
CONFIG_BUSYBOX=y
CONFIG_FEATURE_INSTALLER=y
CONFIG_INSTALL_APPLET_SYMLINKS=y
CONFIG_SH_IS_ASH=y
CONFIG_ASH=y
CONFIG_ASH_ECHO=y
CONFIG_ASH_TEST=y
CONFIG_ASH_OPTIMIZE_FOR_SIZE=y
CONFIG_TEST=y
CONFIG_ECHO=y
CONFIG_MOUNT=y
CONFIG_LS=y
CONFIG_CAT=y
CONFIG_DMESG=y
CONFIG_UNAME=y
CONFIG_MKDIR=y
CONFIG_SLEEP=y
CONFIG_TAIL=y
CONFIG_SETSID=y
# CONFIG_INSTALL_APPLET_DONT is not set
# CONFIG_SH_IS_NONE is not set
CFG
if [ "${STATIC:-1}" = 1 ]; then echo CONFIG_STATIC=y >> .config; else echo "# CONFIG_STATIC is not set" >> .config; fi
make oldconfig </dev/null >/tmp/oldconfig.log 2>&1 || { cat /tmp/oldconfig.log; exit 1; }
if grep -E "^\.config:[0-9]+:warning|nonexistent symbol" /tmp/oldconfig.log; then
	echo "busybox-config: kconfig complained about the settings" >&2
	exit 1
fi
