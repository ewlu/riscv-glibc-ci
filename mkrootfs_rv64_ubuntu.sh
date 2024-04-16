#!/bin/bash
# SPDX-FileCopyrightText: 2024 Rivos Inc.
#
# SPDX-License-Identifier: Apache-2.0

# Builds an RV64 Ubuntu rootfs.

set -euo pipefail

d=$(dirname "${BASH_SOURCE[0]}")

name=$1
distro=mantic

packages=(
        build-essential
        systemd-sysv
        time
        udev
        bison
        gawk
        python3
        gdb
        file
        vim
        gosu
        strace
        libidn2-0
        patchelf
        sudo
)
packages=$(IFS=, && echo "${packages[*]}")

echo "MARCH = $MARCH MABI = $MABI"

MARCH=$MARCH MABI=$MABI mmdebstrap --include="$packages" \
           --variant=minbase \
           --architecture=riscv64 \
           --components="main restricted multiverse universe" \
           --customize-hook='chroot "$1" useradd -m -r -s /usr/bin/bash tester'\
           --customize-hook='chroot "$1" passwd -d tester'\
	   --hook-dir=$(realpath --relative-to=$PWD $d/mmdebstrap_hooks) \
           --skip=cleanup/reproducible \
	   --mode=unshare \
           "${distro}" \
           "${name}"

