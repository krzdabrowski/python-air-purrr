#!/usr/bin/python3

from subprocess import check_call
import sys

print("zaraz ubije")
check_call(["pkill", "-9", "-f", "example.py"])
print("ubilem")