import logging

logger = logging.getLogger('arch_logger')
logger.setLevel(logging.DEBUG)
log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.DEBUG) 
file_handler.setFormatter(log_format)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)  
console_handler.setFormatter(log_format)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

'''
tello_logger = logging.getLogger("djitellopy")
tello_logger.propagate = True
tello_logger.setLevel(logging.DEBUG)
tello_logger.addHandler(file_handler)
tello_logger.addHandler(console_handler)
'''





