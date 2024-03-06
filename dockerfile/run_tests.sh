#!/bin/bash

cd $1
mkdir -p result/sum_files
mkdir -p result/out_files
mkdir -p result/test_result_files
cd build-glibc-linux-$2
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
