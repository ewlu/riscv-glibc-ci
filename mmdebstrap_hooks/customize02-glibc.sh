#!/bin/bash
# SPDX-FileCopyrightText: 2024 Rivos Inc.
#
# SPDX-License-Identifier: Apache-2.0

set -eo pipefail

d=$(dirname "${BASH_SOURCE[0]}")

mkdir -p $1/src
git clone https://github.com/bminor/glibc.git $1/src/glibc
cp $d/../run_glibc.sh "$1/usr/local/bin"

if [[ "$PATCH_DIR" != "" ]];
then
  cd $1/src/glibc
  mkdir -p build
  git config user.name "Bot"
  git config user.email "<>"
  git am $PATCH_DIR/*.patch --whitespace=fix -q --3way --empty=drop &> build/apply.log || true
fi

cat >>"$1/root/.profile" <<"EOF"
run_glibc.sh $MARCH $MABI
# poweroff
EOF

