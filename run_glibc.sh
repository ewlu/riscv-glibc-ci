cd /home/tester/tests/build
ls
echo "PUT COMPILATION INSTRUCTIONS IN run_glibc.sh"

pwd

if [[ -f apply.status ]];
then
  if [[ -f build.status && $(cat build.status) == 0 ]];
  then
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
  exit
else
  if [[ $(cat apply.log | wc -l) != 0 ]]; then
    echo 1 > apply.status
    exit
  fi
  echo 0 > apply.status

  #rm -rf *
  ../glibc/configure CC="gcc -march=$MARCH -mabi=$MABI " CXX="g++ -march=$MARCH -mabi=$MABI " --prefix=$(pwd) --build=riscv64-unknown-linux-gnu --with-timeout-factor=8 2>&1 | tee config.log

  if make -k -O -j $(nproc) 2>&1 | tee build.log
  then
    echo 0 > build.status
  else
    echo 1 > build.status
  fi
  exit
fi
exit
