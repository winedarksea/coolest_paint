# -*- coding: utf-8 -*-
"""
Created on Thu Jan 25 21:40:21 2024

@author: Colin
"""

import time
import csv
import os
import glob

# calibration = all probes at same temperature for fixed period
calibration_duration = None  # specify calibration time in seconds to calibrate
data_collection_duration = 21600  # runtime for data collection, set to None for no recording
data_collection_interval = 60    # Data collection every N seconds (+ device read time)

# found by placing each labeled probe one at a time in a hot water bath and seeing which probe id read as hot
real_world_ids = {  # strings preferred
    "/sys/bus/w1/devices/28-0317256cbcff": "1",
    "/sys/bus/w1/devices/28-0417302846ff": "2",
    "/sys/bus/w1/devices/28-04173060c6ff": "3",
    "/sys/bus/w1/devices/28-5102d443b7e0": "4",
    "/sys/bus/w1/devices/28-3ce1e3804bad": "5",
    "/sys/bus/w1/devices/28-3ce104578fdd": "6",
    "/sys/bus/w1/devices/28-476fd4431e28": "7",
    "/sys/bus/w1/devices/28-3c2df6490106": "8",
    "/sys/bus/w1/devices/28-3c01f096d69d": "9",
    "/sys/bus/w1/devices/28-3ce10457c1da": "10",
    "/sys/bus/w1/devices/28-506ad443fb8d": "11",
}

# Load kernel modules
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folders = glob.glob(base_dir + '28*')
# device_files = [folder + '/w1_slave' for folder in device_folders]
print(f"{len(device_folders)} devices detected")

"""
# test example
device_folders = ["/sys/bus/w1/devices/28-0317256cbcff", "/sys/bus/w1/devices/28-3ce10457c1da", "/sys/bus/w1/devices/28-3ce104578fdd", "/sys/bus/w1/devices/28-476fd4431e28", "/sys/bus/w1/devices/28-5102d443b7e0", "/sys/bus/w1/devices/28-0417302846ff", "/sys/bus/w1/devices/28-3ce1e3804bad", "/sys/bus/w1/devices/28-3c01f096d69d", "/sys/bus/w1/devices/28-04173060c6ff", "/sys/bus/w1/devices/28-3c2df6490106", "/sys/bus/w1/devices/28-506ad443fb8d"]
"""

def read_temp_raw(device_file):
    with open(device_file, 'r') as file:
        lines = file.readlines()
    return lines

def read_temp(device_file, value_on_failure=99999):
    try:
        lines = read_temp_raw(device_file + '/w1_slave')
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = read_temp_raw(device_file)
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            # temp_f = temp_c * 9.0 / 5.0 + 32.0
            return temp_c
    except Exception as e:
        if value_on_failure is not None:
            # the default 99999 is meant to clearly be an integer the probe couldn't read
            print(f"probe {device_file} failed on read")
            return value_on_failure
        else:
            raise ValueError('probe error') from e

def calibrate_sensors(device_folders, calibration_duration=300, calibration_interval=10):
    print("Starting calibration...")
    start_time = time.time()
    temp_sum = {device_file: 0 for device_file in device_folders}
    readings_count = 0

    while time.time() - start_time < calibration_duration:
        for device_file in device_folders:
            temp_sum[device_file] += read_temp(device_file)
        readings_count += 1
        time.sleep(calibration_interval)

    avg_temp = sum(temp_sum.values()) / readings_count / len(device_folders)
    offsets = {device_file: (avg_temp - (temp / readings_count)) for device_file, temp in temp_sum.items()}
    print("Calibration complete.")
    return offsets


# Calibration
if calibration_duration is not None:
    offsets = calibrate_sensors(device_folders, calibration_duration=calibration_duration, calibration_interval=10)
else:
    offsets = {
        '/sys/bus/w1/devices/28-0317256cbcff': 0.907198863636367,
         '/sys/bus/w1/devices/28-3ce10457c1da': 0.2434488636363632,
         '/sys/bus/w1/devices/28-3ce104578fdd': 0.28219886363636704,
         '/sys/bus/w1/devices/28-476fd4431e28': 0.6769488636363654,
         '/sys/bus/w1/devices/28-5102d443b7e0': 0.4229488636363641,
         '/sys/bus/w1/devices/28-0417302846ff': 0.782198863636367,
         '/sys/bus/w1/devices/28-3ce1e3804bad': 0.17294886363636408,
         '/sys/bus/w1/devices/28-3c01f096d69d': -0.4559886363636352,
         '/sys/bus/w1/devices/28-04173060c6ff': -2.905301136363633,
         '/sys/bus/w1/devices/28-3c2df6490106': 0.04794886363636408,
         '/sys/bus/w1/devices/28-506ad443fb8d': -0.17455113636363961,
    }
    offsets = {
        '/sys/bus/w1/devices/28-0317256cbcff': 0.5474090909090954,
        '/sys/bus/w1/devices/28-3ce10457c1da': -0.1671534090909077,
        '/sys/bus/w1/devices/28-3ce104578fdd': -0.0969659090909083,
        '/sys/bus/w1/devices/28-476fd4431e28': 0.29365909090909526,
        '/sys/bus/w1/devices/28-5102d443b7e0': 0.0474090909090954,
        '/sys/bus/w1/devices/28-0417302846ff': 0.3681590909090886,
        '/sys/bus/w1/devices/28-3ce1e3804bad': -0.24521590909090918,
        '/sys/bus/w1/devices/28-3c01f096d69d': -0.8275909090909046,
        '/sys/bus/w1/devices/28-04173060c6ff': 0.7354090909090907,
        '/sys/bus/w1/devices/28-3c2df6490106': -0.3275909090909046,
        '/sys/bus/w1/devices/28-506ad443fb8d': -0.3275284090909061,
    }
    offsets = {
        '/sys/bus/w1/devices/28-0317256cbcff': 0.37575,
        '/sys/bus/w1/devices/28-3ce10457c1da': -0.104,  # -304
        '/sys/bus/w1/devices/28-3ce104578fdd': -0.077437,
        '/sys/bus/w1/devices/28-476fd4431e28': 0.026687,
        '/sys/bus/w1/devices/28-5102d443b7e0': 0.0241875,
        '/sys/bus/w1/devices/28-0417302846ff': 0.211625,
        '/sys/bus/w1/devices/28-3ce1e3804bad': -0.189937,  # 389937
        '/sys/bus/w1/devices/28-3c01f096d69d': -0.525062,  # 925062
        '/sys/bus/w1/devices/28-04173060c6ff': 0.516312,  # highest variability probe in testing
        '/sys/bus/w1/devices/28-3c2df6490106': 0.505375,  # 805375, second highest variability
        '/sys/bus/w1/devices/28-506ad443fb8d': -0.21012,
    }
# fill missing offsets with zero
for probe in device_folders:
    if probe not in offsets.keys():
        offsets[probe] = 0

print(f"temperature calibrated offsets are: {offsets}")

# real world ids (labels on probes) fill out if not present fully
for probe in device_folders:
    if probe not in real_world_ids.keys():
        real_world_ids[probe] = str(probe)

# Data Collection
if data_collection_duration is not None:
    with open(f'temperature_data_{time.strftime("%Y%m%d%H%M")}.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Time"] + [f"Sensor {os.path.basename(real_world_ids[folder])}" for folder in device_folders])

        start_time = time.time()
        while time.time() - start_time < data_collection_duration:
            readings = [read_temp(device_file) + offsets[device_file] for device_file in device_folders]
            print(readings)
            writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S")] + readings)
            time.sleep(data_collection_interval)
else:
    while True:
        print("Press ctrl+c to stop script run")
        for device_file in device_folders:
            print(f"{os.path.basename(real_world_ids[device_file])}: {read_temp(device_file) + offsets[device_file]} °C")
        time.sleep(1)

print("Data collection complete.")
