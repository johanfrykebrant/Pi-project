import os
import pandas
import socket
from datetime import datetime

def get_metrics():
    df_output_lines = [s.split() for s in os.popen("df -P").read().splitlines()]
    sum_space = 0.00
    sum_used = 0.00

    for i in df_output_lines[1:]:
        sum_space = sum_space + float(i[1])
        sum_used = sum_used + float(i[2])

    hostname = socket.gethostname()
    total_gig = round(sum_space / 1000000,2)
    used_gig = round(sum_used / 1000000,2)
    time = datetime.now()
    cpu_temp = round(float(os.popen("/opt/vc/bin/vcgencmd measure_temp").read()[5:][:-3]),2)

    result = [time,hostname,cpu_temp,used_gig,total_gig]
    return result

def main():
    metrics = get_metrics()

if __name__ == "__main__":
    main()