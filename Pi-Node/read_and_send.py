from ds18b20_reader import Reader
from MQ_handler import MQ_handler
import json

mq = MQ_handler()
r = Reader()

msg = r.read_temp()
mq = MQ_handler()
mq.consume("measurements",json.dumps(msg,ensure_ascii=False))
