import psutil


def cpu_percent():
    return psutil.cpu_percent()


def cpu_freq():
    return psutil.cpu_freq()


def ram_percent():
    return psutil.virtual_memory().percent
