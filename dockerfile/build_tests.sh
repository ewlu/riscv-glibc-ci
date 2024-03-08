#!/bin/bash

cd $1
pwd
mkdir build
mkdir -p result/sum_files
mkdir -p result/out_files
mkdir -p result/test_result_files
cd build
mkdir logs
if [ "$2" == "rv32gcv-ilp32d" ];
then
  if ../configure CC="gcc -m32 " CXX="g++ -m32 " --prefix=$(pwd) --build=riscv64-unknown-linux-gnu > logs/config.log 2>&1
  then
    echo 0 > logs/config.status
  else
    echo 1 > logs/config.status
    exit 1
  fi
else
  if ../configure --prefix=$(pwd) --build=riscv64-unknown-linux-gnu > logs/config.log 2>&1
  then
    echo 0 > logs/config.status
  else
    echo 1 > logs/config.status
    exit 1
  fi
fi

if make -k -O -j $(nproc) >> logs/build.log 2>&1
then
  echo 0 > logs/build.status
else
  echo 1 > logs/build.status
  exit 1
fi

cd ..
tar czvf log.tar.gz build/logs

exit 0