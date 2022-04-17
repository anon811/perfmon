import psutil


def cpu_percent():
    return psutil.cpu_percent()


def ram_percent():
    return psutil.virtual_memory().percent
