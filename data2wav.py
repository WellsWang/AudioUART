# -*- coding: utf-8 -*-

import wave, sys
import numpy as np

BAUD = 300
START_BIT = 0
STOP_BIT = 1
PRE_BIT  = 1
PRE_CYCLE = BAUD * 1

#音频信号段，44100Hz
ONE = np.append(np.tile(np.array([30000]*5+[-30000]*6), 13), np.array([30000]*4)) #1：300bps
ZERO = np.append(np.tile(np.array([0]*11), 13), np.array([0]*4)) #0：300bps

data = "test String, 12345. abcde - VWXYZ!"
uart_data = []

def buildPreCycle():
    global uart_data
    for pos in range(PRE_CYCLE):
        uart_data.append(PRE_BIT)

def byte2Bits(data_byte):
    o = ord(data_byte)
    t = 0
    bits = []
    for b in  range(8):
        o = o - t
        t = o >> (7 - b)
        bits.append(t)
        t = t << (7 - b)
    bits.reverse()
    return bits

def appendData(data_byte):
    global uart_data
    uart_data.append(START_BIT)
    uart_data = uart_data + byte2Bits(data_byte)
    uart_data.append(STOP_BIT)

def build_wave(data_array, output):
    f = wave.open(output+'.wav','wb')
    f.setnchannels(1)	#设置通道数
    f.setsampwidth(2)	#设置采样宽度
    f.setframerate(44100)	#设置采样
    f.setcomptype('NONE','not compressed')	#设置采样格式  无压缩

    #第一部分，字库数据
    print("\n\n生成第音频数据：")
    wav = np.array([])  #空白音频
    for d in data_array:
        if d == 1: 
            wav = np.append(wav, ONE)
        elif d == 0:
            wav = np.append(wav, ZERO)
        print("#", end="")
    wave_data=wav.astype(np.int16).tobytes() #将类型转为字节

    f.writeframes(wave_data)
    f.close()
    print("\n\n完成音频数据生成。")

if __name__ == "__main__":

    if len(sys.argv)>1:
#        try:
        buildPreCycle()

        for c in data:
            appendData(c)
        
        for b in uart_data:
            print (b, end="")
        
        build_wave(uart_data, sys.argv[1])

#        except:
#            print("Error on generating wav file!")
    else:
        print("-= UART Data to WAV =- \n Usage:\n data2wav.py <output wav filename>")
