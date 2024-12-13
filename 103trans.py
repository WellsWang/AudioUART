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

uart_data = []


def readSourceCode(filename):   #读取103程序机器码源代码
    with open(filename, encoding='UTF-8') as f:
        lines = [line.strip() for line in f]
    return lines

def source2PaperTape(source):   #机器码转码成为穿孔纸带代码（8bit模拟5bit代码
    data = []
    for line in source:
        line = line.split("//")[0]
        for c in line:
            if ord(c) >= 48 and ord(c) <= 57:   # 0 - 9
                data.append(ord(c) - 32)
            elif c == '|':
                data.append(0x01)
            elif c == '+':
                data.append(0x1E)
            elif c == '-':
                data.append(0x1F)
        data.append(0x06)
    data.append(0x07)
    return data

def genBinData(tape):   #合成串口输出用的字串
    bindata = ''
    for d in tape:
        bindata += chr(d)
    return bindata

def genTextCode(tape):  #合成十六进制表示的串口输出码
    textcode = ''
    for d in tape:
        hex = "0x%02x"%d
        hex = f"{hex}"[2:]
        textcode = "{} {}".format(textcode, hex)
    return textcode[1:]


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
        try:
            source = readSourceCode(sys.argv[1])
        except Exception as e:
            print("读取103机器码源代码文件 {} 时出现严重错误".format(sys.argv[1]))
            print(e)
            exit(128)
        
        filename = sys.argv[1].rsplit(".", 1)[0]
        raw = source2PaperTape(source)
        try:
            print(f"生成串口输出码文件 {filename}.bin ...")
            f = open(f"{filename}.bin", "w", encoding='UTF-8')
            f.write(genBinData(raw))
            f.close()
        except Exception as e:
            print(f"生成串口输出码文件 {filename}.bin 时出现错误.")
            print(e)
        
        try:
            print(f"生成十六进制表示串口码文件 {filename}.ser ...")
            f = open(f"{filename}.ser", "w", encoding='UTF-8')
            f.write(genTextCode(raw))
            f.close()
        except Exception as e:
            print(f"生成十六进制表示串口码文件 {filename}.ser 时出现错误.")
            print(e)

        try:
            print(f"生成串口输出音频文件 {filename}.wav ...")
            data = genBinData(raw)

            buildPreCycle()

            for c in data:
                appendData(c)
            
            for b in uart_data:
                print (b, end="")
            
            build_wave(uart_data, filename)
        except Exception as e:
            print(f"生成串口输出音频文件 {filename}.wav 时出现错误.")
            print(e)

    else:
        print("-= COMPUTER 103 TRANSCODER =- \n 使用方法：\n 103trans.py <103机器码源文件文件名>")