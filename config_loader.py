import configparser


def get_configurations():
    config = configparser.ConfigParser()
    config.read('config.ini')

    configurations = {
        'fx': float(config['CameraParameters']['fx']),
        'fy': float(config['CameraParameters']['fy']),
        'k1': float(config['CameraParameters']['k1']),
        'k2': float(config['CameraParameters']['k2']),
        'e2e_height_rr': int(config['RingProperties']['e2e_height_rr']),
        'e2e_height_yl': int(config['RingProperties']['e2e_height_yr']),
        'diameter_red_cms': int(config['RingProperties']['diameter_red_cms']),
        'diameter_yellow_cms': int(config['RingProperties']['diameter_yellow_cms']),
        'yellow_optimum_hover_ht': int(config['RingProperties']['yellow_optimum_hover_ht']),
        'red_optimum_hover_ht': int(config['RingProperties']['red_optimum_hover_ht']),
        'speed': int(config['DroneProperties']['speed']),

    }
    return configurations
