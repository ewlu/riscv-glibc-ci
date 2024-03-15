#!/bin/bash

cd $1
pwd
ls
mkdir -p result/sum_files
mkdir -p result/out_files
mkdir -p result/test_result_files
cd build
pwd


set +o pipefail
find / -name libgcc_s.so.1 
cp /usr/lib/riscv64-linux-gnu/libgcc_s.so.1 .
make check -j $(nproc) -k -O 2>&1 | tee logs/check.log
if [ $? == 0 ]
then
  echo 0 > logs/check.status
else
  cat */subdir-tests.sum > logs/check.sum
  echo 1 > logs/check.status
  exit 1
fi

for file in $(find . -name "*.sum"); do
  cp -r --parents $file ../result/sum_files
done

for file in $(find . -name "*.out"); do
  cp -r --parents $file ../result/out_files
done

for file in $(find . -name "*.test_result"); do
  cp -r --parents $file ../result/test_result_files
done

set -o pipefail

cd ..
tar czvf result.tar.gz result/
tar czvf logs.tar.gz build/logs
pwd
ls

exit 0
