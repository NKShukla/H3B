import os
import numpy as np

DATA_PATH = 'data/phase2/'
OUTPUT_PATH = 'data/mahimahi/'
BYTES_PER_PKT = 1500.0
MILLISEC_IN_SEC = 1000.0
BITS_IN_BYTE = 8.0


def main():
    files = os.listdir(DATA_PATH)

    for f in files:
        file_path = DATA_PATH + f
        output_path = OUTPUT_PATH + f + '.com-'

        with open(file_path, 'r') as f, open(output_path, 'w') as mf:
            print(file_path)
            time_ms = []
            bytes_recv = []
            recv_time = []
            for line in f:
                parse = line.split(',')
                # trace error, time not monotonically increasing
                if len(time_ms) > 0 and float(parse[0]) < time_ms[-1]:
                    break
                time_ms.append(float(parse[0]))
                bytes_recv.append(float(parse[1]))
                recv_time.append(float(parse[2]))

            time_ms = np.array(time_ms)
            bytes_recv = np.array(bytes_recv)
            recv_time = np.array(recv_time)
            time_ms = time_ms[1:]
            bytes_recv = bytes_recv[1:]
            recv_time = recv_time[1:]
            throughput_all = bytes_recv / recv_time

            millisec_time = 0
            mf.write(str(millisec_time) + '\n')

            print(len(throughput_all))
            for i in range(len(throughput_all)):

                throughput = throughput_all[i]

                pkt_per_millisec = throughput / BYTES_PER_PKT

                millisec_count = 0
                pkt_count = 0

                while True:
                    millisec_count += 1
                    millisec_time += 1
                    to_send = (millisec_count * pkt_per_millisec) - pkt_count
                    to_send = np.floor(to_send)

                    for k in range(int(to_send)):
                        print(millisec_time)
                        mf.write(str(millisec_time) + '\n')

                    pkt_count += to_send

                    if millisec_count >= recv_time[i]:
                        break


if __name__ == '__main__':
    main()
