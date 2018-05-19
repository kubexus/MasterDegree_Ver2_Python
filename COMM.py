import serial
from multiprocessing import Process, Pipe
import time


START = bytes([0xf0])
END = bytes([0xff])
ACCK = bytes([0xf1])
ERR = bytes([0xee])
FAIL = bytes([0xf2])
CAN_REC = bytes([0xf4])
SIG_FOUND = bytes([0xf3])

global_bool = True


def test_nlfsr(state, x):
    period = 2**len(state) - 1
    initial = state[:]
    i = 0
    print(state)
    while True:
        i += 1
        feedback = int(state[0]) ^ (int(state[x[0]]) & int(state[x[1]])) ^ int(state[x[2]]) ^ int(state[x[3]]) ^ int(state[x[4]]) ^ int(state[x[5]])
        state = state[1:] + str(feedback)
        #print(state)
        if state == initial:
            break
        if i > period:
            break
    if i == period:
        return True
    else:
        return False


def change(x):
    for i in range(0, 35):
        if x == bytes([i]):
            return i


def take_poly(poly_file):
    poly1 = poly_file.readline()
    if poly1 == '':
        return -1
    poly1 = poly1[:len(poly1) - 1]
    poly1 = poly1.split(' ')
    poly = []
    for i in poly1:
        poly.append(int(i))
    print(poly)
    return poly


def server(ser1):
    poly_file = open('polyFile', 'r')
    give_poly = True
    res_file = open('results', 'w')
    while True:
        t = ser1.read()
        if give_poly:
            poly = take_poly(poly_file)
            if poly == -1:
                print('koniec')
                return
            give_poly = False
        if t == SIG_FOUND:
            ser1.write(ACCK) # moge odebrac
            out = ''
            while True:
                x = ser1.read(size=1)
                if x == SIG_FOUND:
                    continue
                if x == END:
                    out = out[:len(out)-1] + '\n'
                    break
                temp = str(change(x))
                if temp is not None:
                    out += temp
                    out += ' '
            out += '\n'
            res_file.writelines(out)
            x = ser1.read(size=1)
            continue
        if not t:
            ser1.write(START)
            t = ser1.read()
            if t == CAN_REC:       # fpga can receive
                for i in range(len(poly)):
                    ser1.write(bytes([poly[i]]))
                ser1.write(END)
                t = ser1.read(size=1)
                if t == ACCK:   # ACCK
                    give_poly = True
                    continue
                else:
                    continue
            elif t == ERR:    #error
                continue
            elif t == SIG_FOUND:
                ser1.write(ACCK)  # moge odebrac
                out = ''
                while True:
                    x = ser1.read(size=1)
                    if x == SIG_FOUND:
                        continue
                    if x == END:
                        out = out[:len(out) - 1] + '\n'
                        break
                    temp = str(change(x))
                    if temp is not None:
                        out += temp
                        out += ' '
                out += '\n'
                res_file.write(out)
                x = ser1.read(size=1)
                continue
            elif t == FAIL:
                continue
        if t == FAIL:
            continue


if __name__ == '__main__':
    try:
        ser1 = serial.Serial('/dev/ttyUSB0', 115200, timeout=0.1)
        ser1.close()
        ser1.open()
        Server = Process(target=server, args=(ser1,))
        Server.start()
        Server.join()
    except KeyboardInterrupt:
        print('Przerwano z klawiatury')
        ser1.close()

