#!/bin/bash
# SPDX-FileCopyrightText: 2024 Rivos Inc.
#
# SPDX-License-Identifier: Apache-2.0

set -euo pipefail

d=$(dirname "${BASH_SOURCE[0]}")

echo 44f789c720e545ab8fb376b1526ba6ca > "$1/etc/machine-id"

echo "File $1"

mkdir -p "$1/etc/systemd/system/serial-getty@ttyS0.service.d"
cat > "$1/etc/systemd/system/serial-getty@ttyS0.service.d/autologin.conf" << "EOF"
[Service]
ExecStart=
ExecStart=-/sbin/agetty -o '-p -f -- \u' --keep-baud --autologin root 115200,57600,38400,9600 - $TERM
EOF

cat > "$1/etc/sysctl.d/10-console-messages.conf" << "EOF"
kernel.printk = 7 4 1 7
EOF

cat >"$1/root/.profile" <<"EOF"
# Poor man's SysV init ;-)
set -x
echo "booted"
EOF

