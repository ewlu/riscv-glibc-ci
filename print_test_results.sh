#!/bin/bash
cat tests.sum | grep -E '^[A-Z]+:' | grep -E -v '^(PASS|XFAIL):' || true
echo "         === Summary of results ==="
cat tests.sum | sed -e '/:.*/!d' -e 's/:.*//' | sort | uniq -c
