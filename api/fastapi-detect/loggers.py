import logging
import colorlog
import colorlog.formatter


default_formatter = colorlog.ColoredFormatter("%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    },
    secondary_log_colors={},
    style='%')

# creating the utillogger
utillogger = logging.getLogger('utillogger')
utillogger.setLevel('INFO') #handles everything from info up
util_handler =  logging.FileHandler('utils.log')
util_handler.setFormatter(default_formatter)
utillogger.addHandler(util_handler)


#creating the routelogger

routelogger = logging.getLogger('routelogger')
routelogger.setLevel('INFO')
route_handler = logging.FileHandler('routes.log')
route_handler.setFormatter(default_formatter)
routelogger.addHandler(route_handler)

