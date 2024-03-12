#!/bin/bash

cd $1
pwd
ls
mkdir build
cd build
mkdir logs
set +o pipefail
if [ "$2" == "rv32gcv-ilp32d" ];
then
  ../configure CC="gcc -march=rv32gc " CXX="g++ -march=rv32gc " --prefix=$(pwd) --build=riscv64-unknown-linux-gnu 2>&1 | tee logs/config.log
  if [ $? == 0 ]
  then
    echo 0 > logs/config.status
  else
    echo 1 > logs/config.status
    exit 1
  fi
else
  ../configure --prefix=$(pwd) --build=riscv64-unknown-linux-gnu 2>&1 | tee logs/config.log 
  if [ $? == 0 ]
  then
    echo 0 > logs/config.status
  else
    echo 1 > logs/config.status
    exit 1
  fi
fi

make -k -O -j $(nproc) 2>&1 | tee logs/build.log 
if [ $? == 0 ]
then
  echo 0 > logs/build.status
else
  echo 1 > logs/build.status
  exit 1
fi

set -o pipefail

cd ..
pwd
tar czvf logs.tar.gz build/logs
ls

exit 0
