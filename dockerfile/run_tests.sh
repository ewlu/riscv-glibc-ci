#!/bin/bash

cd $1
pwd
ls
mkdir -p result/sum_files
mkdir -p result/out_files
mkdir -p result/test_result_files
cd build
pwd

if make check -j $(nproc) -k -O > logs/check.log 2>&1
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

cd ..
tar czvf result.tar.gz result/
tar czvf log.tar.gz build/logs

