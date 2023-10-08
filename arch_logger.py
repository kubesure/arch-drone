import logging

tello_logger = logging.getLogger("djitellopy")
tello_logger.propagate = True
tello_logger.setLevel(logging.INFO)


logger = logging.getLogger('arch_logger')
logger.setLevel(logging.INFO)
# log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log_format = logging.Formatter('[%(asctime)s] [%(levelname)s] %(filename)s - %(lineno)d - %(message)s')

file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(log_format)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(log_format)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

tello_logger.addHandler(file_handler)
# tello_logger.addHandler(console_handler)


