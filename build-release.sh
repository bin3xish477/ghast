#!/bin/bash

WD=$(pwd)
rm $WD/dist/* && hatch build && hatch publish && rm $WD/dist/*
