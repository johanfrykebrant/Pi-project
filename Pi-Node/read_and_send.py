from ds18b20_reader import reader
from MQ_handler import MQ_handler
import json

mq = MQ_handler()
r = reader()

msq = r.read_temp()
mq = MQ_handler()
mq.produce("measurements",json.dumps(msq,ensure_ascii=False))
