#!/bin/bash
echo $1 $2 $3

PYTHON=python3 # ~/Desktop/Python-3.5.1/install/bin/python3

rm -r __pycache__
if [ $1 = 'e' ]; then
  $PYTHON mix_exp.py
elif [ $1 = 'i' ]; then
  $PYTHON intersection_sim.py
elif [ $1 = 'im' ]; then
  $PYTHON intersection_model.py
elif [ $1 = 'ie' ]; then
  $PYTHON intersection_exp.py
elif [ $1 = 'die' ]; then
  $PYTHON -m pdb intersection_exp.py
elif [ $1 = 'r' ]; then
  $PYTHON randmix_model.py
else
  echo "Argument did not match!"
fi
