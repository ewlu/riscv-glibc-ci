cd /src/glibc
ls
echo "PUT COMPILATION INSTRUCTIONS IN run_glibc.sh"


cd build

if [[ -f apply.status ]];
then
  cd build
  if [[ -f build.status && $(cat build.status) == 0 ]]
    cp /usr/lib/riscv64-linux-gnu/libgcc_s.so.1 .
    cp /usr/lib/riscv64-linux-gnu/libstdc++.so.6 .
    ls libgcc_s.so.1 > lib.log

    export GLIBC_TEST_ALLOW_TIME_SETTING=1
    if make check -j $(nproc) -k -O 2>&1 | tee check.log
    then
      echo 0 > check.status
    else
      echo 1 > check.status
    fi
  fi
  poweroff
else
  if [[ $(cat apply.log | wc -l) != 0 ]]; then
    echo 1 > apply.status
    poweroff
  fi
  echo 0 > apply.status

  #rm -rf *
  ../configure CC="gcc -march=$1 -mabi=$2 " CXX="g++ -march=$1 -mabi=$2 " --prefix=$(pwd) --build=riscv64-unknown-linux-gnu --with-timeout-factor=8 2>&1 | tee config.log

  if make -k -O -j $(nproc) 2>&1 | tee build.log
  then
    echo 0 > build.status
  else
    echo 1 > build.status
  fi
  poweroff
fi
