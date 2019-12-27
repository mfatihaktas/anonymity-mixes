#!/bin/bash
echo $1 $2 $3

PYTHON=python3 # ~/Desktop/Python-3.5.1/install/bin/python3

rm -r __pycache__
if [ $1 = 'e' ]; then
  $PYTHON randmix_exp.py
elif [ $1 = 'r' ]; then
  # $PYTHON mixed_exp.py
  $PYTHON randmix_model.py
elif [ $1 = 'b' ]; then
  $PYTHON batch_mix_exp.py
else
  echo "Argument did not match!"
fi
