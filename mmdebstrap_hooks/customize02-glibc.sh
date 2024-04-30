#!/bin/bash
# SPDX-FileCopyrightText: 2024 Rivos Inc.
#
# SPDX-License-Identifier: Apache-2.0

set -eo pipefail

d=$(dirname "${BASH_SOURCE[0]}")

mkdir -p $1/src
git clone https://sourceware.org/git/glibc.git $1/home/tester/tests/glibc
cp $d/../run_glibc.sh "$1/home/tester/tests/"
mkdir -p $1/home/tester/tests/build
cp $d/../print_test_results.sh "$1/home/tester/tests/build"

if [[ -n $PATCH_DIR && "$PATCH_DIR" != "" ]];
then
  echo "======================================="
  echo "applying patches"
  cd $1/home/tester/tests/glibc
  git checkout $BASELINE_HASH
  git config user.name "Bot"
  git config user.email "<>"
  git am $PATCH_DIR/*.patch --whitespace=fix -q --3way --empty=drop &> $HASH_DIR/apply.log || true
fi

cd $1/home/tester/tests/glibc
echo "-----------------------------------------"
pwd
git rev-parse HEAD > $HASH_DIR/applied_hash.txt

echo "customize MARCH=$MARCH MABI=$MABI"

echo "export MARCH=$MARCH MABI=$MABI" >>"$1/root/.profile"
cat >> "$1/root/.profile" <<"EOF"
echo "MARCH=$MARCH MABI=$MABI"
cp ~/.bashrc /home/tester/
chown -R tester /home/tester/
gosu tester bash /home/tester/tests/run_glibc.sh $MARCH $MABI
poweroff
EOF

