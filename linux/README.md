# CCL OS Linux Distribution - Phase 2
# Custom Linux distro with CCL as the shell

# Base: Ubuntu Server (minimal)
# Shell: CCL OS (Tauri/React)
# Package Manager: APT + CCL Package Manager

# ===== Build Instructions =====
# 1. Install prerequisites
#    sudo apt update && sudo apt install -y debootstrap squashfs-tools xorriso

# 2. Build base system
#    sudo bash linux/scripts/build-base.sh

# 3. Configure CCL shell
#    sudo bash linux/scripts/setup-ccl.sh

# 4. Build ISO
#    sudo bash linux/scripts/build-iso.sh

# 5. Test in VM
#    qemu-system-x86_64 -m 4G -cdrom ccl-os-0.2.iso -boot d

# ===== Directory Structure =====
# linux/
# ├── config/           # System configuration
# │   ├── apt-sources.list
# │   ├── ccl-desktop.conf
# │   └── sudoers.d/ccl
# ├── overlay/          # Files to overlay on base system
# │   ├── etc/skel/     # User skeleton directory
# │   ├── usr/local/bin/ # CCL binaries
# │   └── opt/ccl-os/    # CCL OS files
# ├── scripts/          # Build and setup scripts
# │   ├── build-base.sh
# │   ├── setup-ccl.sh
# │   ├── build-iso.sh
# │   └── cleanup.sh
# └── iso/              # Output ISO files
