import psutil


def cpu_percent():
    return psutil.cpu_percent()