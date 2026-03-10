#!/usr/bin/env bash

# PS3 only for now

for x in 0017 2836 2837 2838 2839 2839 2840 2841 2842; do
	java -jar /home/natalie/Downloads/mhtools.jar --reb-enc ${x} 1
done

for x in 40{60,61,62,63,64,65,66,67,71,72,73,74}; do
	java -jar /home/natalie/Downloads/mhtools.jar --reb-enc ${x} 4
done

for x in 4290 4291 4292; do
	java -jar /home/natalie/Downloads/mhtools.jar --reb-enc ${x} 3
done

java -jar /home/natalie/Downloads/mhtools.jar --create-patch *.bin.enc MHP3RD_DATA.BIN
