#!/bin/bash

cd $1
pwd
ls
mkdir build
cd build
mkdir logs
if [ "$2" == "rv32gcv-ilp32d" ];
then
  if ../configure CC="gcc -march=rv32gc " CXX="g++ -march=rv32gc " --prefix=$(pwd) --build=riscv64-unknown-linux-gnu > logs/config.log 2>&1
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
pwd
tar czvf logs.tar.gz build/logs
ls

exit 0
