import serial
from multiprocessing import Process, Pipe
import time
import sys

#ser1 = serial.Serial('/dev/ttyUSB0', 115200)
#print(ser1.name)
#while True:
#    x = ser1.read(6)
#    print(x)
#ser1.close()
#for i in range(0, 4294967296):
#    a = 1

#print(a)

global_bool = True


def test_nlfsr(state, x):
    period = 2**len(state) - 1
    initial = state[:]
    i = 0
    while True:
        i += 1
        feedback = int(state[0]) ^ (int(state[x[0]]) & int(state[x[1]])) ^ int(state[x[2]]) ^ int(state[x[3]]) ^ int(state[x[4]]) ^ int(state[x[5]])
        state = state[1:] + str(feedback)
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


def reading(conn):
    try:
        res_file = open('results', 'w')
        x = [7, 18, 1, 8, 9, 15]
        ser1 = serial.Serial('/dev/ttyUSB0', 115200, timeout=0.5)
        ser1.close()
        ser1.open()
        print('opened')
        # while True:
        #     out = ''
        #     x = ser1.read(1)
        #     if x == bytes([0xff]):
        #         while True:
        #             x = ser1.read(1)
        #             if x == bytes([0xfe]):
        #                 out += '\n'
        #                 break
        #             out += str(change(x))
        #             out += ' '
        #     res_file.write(out)
        #     res_file.flush()
        #     conn.send(out)
        ser1.write(bytes([0xf0]))
        #print('sent : ', bytes([0xf0]))
        t = ser1.read(size=1)
        #print(t)
        for i in range(6):
            ser1.write(bytes([x[i]]))
        #print('sent : polynomial')
        ser1.write(bytes([0xff]))
        #print('sent : ', bytes([0xff]))
        t = ser1.read(size=1)
        #print(t)
        t = ser1.read(size=1)
        if t == bytes([0xf0]):
            out = ''
            while True:
                x = ser1.read(1)
                #print(x)
                if x == bytes([0xff]):
                    out += '\n'
                    break
                out += str(change(x))
                out += ' '
            print(out)
        ser1.close()
    except (KeyboardInterrupt):
        ser1.close()
        print('Przerwano z klawiatury')
    # print(test_nlfsr('11100000000', [2, 10, 6, 10, 10, 8]))


def worker(conn):
    try:
        while True:
            num = conn.recv()
            print(num)
    except KeyboardInterrupt:
        print('koniec')


if __name__ == '__main__':
    child, parent = Pipe()
    listener = Process(target=reading, args=(child,))
    trololo = Process(target=worker, args=(parent,))
    listener.start()
    #trololo.start()
    listener.join()
    #trololo.join()
