#!/bin/bash
echo $1 $2 $3

PYTHON=python3 # ~/Desktop/Python-3.5.1/install/bin/python3

rm -r __pycache__
if [ $1 = 'e' ]; then
  $PYTHON mix_exp.py
elif [ $1 = 'r' ]; then
  $PYTHON randmix_model.py
else
  echo "Argument did not match!"
fi
