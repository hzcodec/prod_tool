#!/usr/bin/env python

# Auther      : Heinz Samuelsson
# Date        : 2017-06-02
# File        : matplot.py
# Reference   : -
# Description : Used in production test tool for ActSafe
#
# Python ver  : 2.7.3 (gcc 4.6.3)

import sys
import matplotlib.pyplot as plt

t = []

# read in data file
def read_indata():

    with open('logdata/speed_data1.txt') as f:
        content = f.readlines()

    content = [x.strip() for x in content]

    # convert to float
    result = map(float, content)

    # number of lines
    n = sum(1 for line in open('logdata/speed_data1.txt'))

    return content, n

def read_indata2():

    with open('logdata/speed_data2.txt') as f:
        content = f.readlines()

    content = [x.strip() for x in content]

    # convert to float
    result = map(float, content)

    # number of lines
    n = sum(1 for line in open('logdata/speed_data2.txt'))

    return content, n


def main():

    data1, numberOfLines1 = read_indata()
    data2, numberOfLines2 = read_indata2()
    
    t = range(numberOfLines1)
    
    # set window title
    plt.gcf().canvas.set_window_title('Performance test')
    
    plt.plot(t, data1, color="blue", linewidth=1, linestyle='-')
    plt.plot(t, data2, color="red", linewidth=1, linestyle='-')
    
    plt.xlabel('[samples]')
    
    plt.grid(True)
    plt.show()


if __name__ == '__main__':
    main()
