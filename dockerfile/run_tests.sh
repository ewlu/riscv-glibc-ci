#!/bin/bash

echo $1
echo $2
cd $1
pwd
mkdir -p result/sum_files
mkdir -p result/out_files
mkdir -p result/test_result_files
GLIBC_BIN_PATH=$(pwd)/bin
PATH=$GLIBC_BIN_PATH:$PATH
echo $PATH
ls
ls $GLIBC_BIN_PATH
cd build-glibc-linux-$2
pwd
which riscv64-unknown-linux-gnu-gcc
make check -j $(nproc) -k 2>&1 || true | tee log

for file in $(find . -name "*.sum"); do
  cp -r --parents $file ../result/sum_files
done

for file in $(find . -name "*.out"); do
  cp -r --parents $file ../result/out_files
done

for file in $(find . -name "*.test_result"); do
  cp -r --parents $file ../result/test_result_files
done

cp log ../result

cd ..
tar czvf result.tar.gz result/
