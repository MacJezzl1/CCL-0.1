#!/bin/bash
# Build base system for CCL OS Linux Distribution
# Phase 2: Custom Linux with CCL as shell

set -e

echo "=========================================="
echo "  CCL OS Linux - Base System Builder"
echo "=========================================="
echo ""

# Configuration
BASE_DIR=$(pwd)/linux
BUILD_DIR=$BASE_DIR/build
ROOTFS=$BUILD_DIR/rootfs
ISO_DIR=$BASE_DIR/iso

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Error: This script must be run as root (sudo)."
    exit 1
fi

# Install prerequisites
echo "Installing prerequisites..."
apt update
apt install -y debootstrap squashfs-tools xorriso wget curl

# Create build directories
echo "Creating build directories..."
mkdir -p $ROOTFS $ISO_DIR

# Bootstrap base system (Ubuntu Server minimal)
echo "Bootstrapping base system (Ubuntu Server)..."
debootstrap --arch=amd64 jammy $ROOTFS http://archive.ubuntu.com/ubuntu/

# Configure base system
echo "Configuring base system..."

# Set hostname
echo "ccl-os" > $ROOTFS/etc/hostname
echo "127.0.0.1   ccl-os" > $ROOTFS/etc/hosts

# Configure APT sources
cat > $ROOTFS/etc/apt/sources.list <<EOF
deb http://archive.ubuntu.com/ubuntu/ jammy main restricted
deb http://archive.ubuntu.com/ubuntu/ jammy-updates main restricted
deb http://archive.ubuntu.com/ubuntu/ jammy universe
deb http://security.ubuntu.com/ubuntu/ jammy-security main restricted
EOF

# Mount virtual filesystems
mount -t proc /proc $ROOTFS/proc
mount -t sysfs /sys $ROOTFS/sys
mount --bind /dev $ROOTFS/dev
mount --bind /dev/pts $ROOTFS/dev/pts

# Install essential packages
echo "Installing essential packages..."
chroot $ROOTFS /bin/bash <<'EOF'
apt update
apt install -y \
    linux-image-generic \
    grub-pc \
    network-manager \
    openssh-server \
    sudo \
    vim \
    curl \
    wget \
    git \
    build-essential \
    nodejs \
    npm \
    python3 \
    python3-pip \
    rustc \
    cargo \
    xorg \
    lightdm \
    openbox \
    xterm
EOF'

# Install CCL OS shell (Tauri app)
echo "Installing CCL OS shell..."
mkdir -p $ROOTFS/opt/ccl-os
# Copy CCL OS desktop files
if [ -d "$BASE_DIR/../desktop" ]; then
    cp -r $BASE_DIR/../desktop $ROOTFS/opt/ccl-os/
fi

# Create CCL launcher script
cat > $ROOTFS/usr/local/bin/ccl-launcher <<'EOF'
#!/bin/bash
export DISPLAY=:0
cd /opt/ccl-os/desktop
npm start
EOF'
chmod +x $ROOTFS/usr/local/bin/ccl-launcher

# Configure LightDM to use CCL as default session
cat > $ROOTFS/etc/lightdm/lightdm.conf <<EOF'
[Seat:*]
user-session=ccl
EOF'

# Create CCL desktop session
cat > $ROOTFS/usr/share/xsessions/ccl.desktop <<EOF'
[Desktop Entry]
Name=CCL OS
Comment=AI-Native Operating System
Exec=ccl-launcher
Type=Application
EOF'

# Configure auto-login (optional)
mkdir -p $ROOTFS/etc/lightdm/lightdm.conf.d/
cat > $ROOTFS/etc/lightdm/lightdm.conf.d/50-ccl.conf <<EOF'
[Seat:*]
autologin-user=ccluser
autologin-user-timeout=0
EOF'

# Create CCL user
chroot $ROOTFS /bin/bash <<'EOF'
useradd -m -s /bin/bash ccluser
echo "ccluser:ccluser" | chpasswd
echo "ccluser ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
EOF'

# Copy CCL OS configuration
echo "Copying CCL OS files..."
if [ -d "$BASE_DIR/overlay" ]; then
    cp -r $BASE_DIR/overlay/* $ROOTFS/
fi

# Configure sudoers for CCL
cp $BASE_DIR/config/sudoers.d/ccl $ROOTFS/etc/sudoers.d/ 2>/dev/null || true

# Set CCL as default shell (optional)
chroot $ROOTFS /bin/bash -c "chsh -s /usr/local/bin/ccl-launcher ccluser" 2>/dev/null || true

# Unmount virtual filesystems
umount $ROOTFS/dev/pts
umount $ROOTFS/dev
umount $ROOTFS/sys
umount $ROOTFS/proc

# Build squashfs image
echo "Building squashfs image..."
mkdir -p $ISO_DIR/casper
mksquashfs $ROOTFS $ISO_DIR/casper/filesystem.squashfs -e boot

# Copy kernel and initrd
cp $ROOTFS/boot/vmlinuz-* $ISO_DIR/casper/vmlinuz
cp $ROOTFS/boot/initrd.img-* $ISO_DIR/casper/initrd

# Create ISO structure
echo "Creating ISO structure..."
mkdir -p $ISO_DIR/.disk
echo "CCL OS 0.2" > $ISO_DIR/.disk/info

# Copy bootloader files
mkdir -p $ISO_DIR/boot/grub
cat > $ISO_DIR/boot/grub/grub.cfg <<'EOF'
set default=0
set timeout=10

menuentry "Try CCL OS without installing" {
    linux /casper/vmlinuz boot=casper
    initrd /casper/initrd
}

menuentry "Install CCL OS" {
    linux /casper/vmlinuz boot=casper only-ubiquity
    initrd /casper/initrd
}
EOF'

# Build ISO
echo "Building ISO..."
grub-mkrescue -o $BASE_DIR/../ccl-os-0.2.iso $ISO_DIR

# Cleanup
echo "Cleaning up..."
rm -rf $BUILD_DIR

echo ""
echo "=========================================="
echo "  Build Complete!"
echo "=========================================="
echo ""
echo "ISO created: $BASE_DIR/../ccl-os-0.2.iso"
echo ""
echo "Test with: qemu-system-x86_64 -m 4G -cdrom ccl-os-0.2.iso"
echo "=========================================="
