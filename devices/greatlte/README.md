# Samsung Galaxy Note 8 (greatlte)

Status: first-boot skeleton. Nothing here has run on a phone.

S-Boot cannot start a mainline kernel directly (it loads it at an address
that is not 2 MiB aligned, and applies its own device tree overlay), so the
boot image chains it, as the Galaxy S8 port does:

    S-Boot -> barebox (the "kernel" of boot.img) -> FIT in the ramdisk
              -> Linux Image + exynos8895-greatlte.dtb + rescue initramfs

- `barebox/0001-samsung-exynos-add-greatlte.diff` adds the Note 8 to
  barebox's Samsung Exynos board (applied on barebox c58b5150 by the workflow).
- `boot/image.its` and `boot/init` describe the FIT and the rescue initramfs.
- `stock.dtb` is the device tree image of your own stock boot image (not
  committed here until you add it; see the workflow header for the `dd`).
- `.github/workflows/greatlte.yml` builds all of it and uploads
  `boot-greatlte.img` and `boot-greatlte.img.tar.md5` (Odin) as an artifact.

Unverified: the FIT load address 0x80200000, barebox's relocation over it,
the dt image S-Boot accepts, and the DT build against barebox's own dts/src.
