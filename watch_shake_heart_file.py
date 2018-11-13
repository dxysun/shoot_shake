from watchdog.observers import Observer
from watchdog.events import *
import sys
import os
import datetime
import django
import logging

sys.path.append('D:/workSpace/PythonWorkspace/shoot_shake/shoot_shake')
sys.path.append('D:/workSpace/PythonWorkspace/shoot_shake')
os.chdir('D:/workSpace/PythonWorkspace/shoot_shake')
logging.basicConfig(filename='log.txt', filemode="w", level=logging.INFO)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shoot_shake.settings")
django.setup()
from shootweb.models import *


# 把datetime转成字符串
def time_to_string(dt):
    return dt.strftime("%H-%M-%S")


# 把字符串转成datetime
def string_to_time(string):
    return datetime.datetime.strptime(string, "%H-%M-%S")


def get_normal_str(s):
    s = s.strip()
    if len(s) < 2 and int(s) < 10:
        s = "0" + s
    return s


def find_n_sub_str(src, sub, pos, start):
    index = src.find(sub, start)
    if index != -1 and pos > 0:
        return find_n_sub_str(src, sub, pos - 1, index + 1)
    return index


class HeartEventHandler(FileSystemEventHandler):
    def __init__(self):
        FileSystemEventHandler.__init__(self)
        self.heart_file = None
        self.record_heart = None
        self.heart_data = None

    def on_moved(self, event):
        if event.is_directory:
            print("directory moved from {0} to {1}".format(event.src_path, event.dest_path))
        else:
            print("file moved from {0} to {1}".format(event.src_path, event.dest_path))

    def on_created(self, event):
        if event.is_directory:
            print("directory created:{0}".format(event.src_path))
        else:
            print("file created:{0}".format(event.src_path))
            logging.info("file created:" + event.src_path)
            self.heart_file = open(event.src_path, "r")
            file_path = event.src_path.split("\\")[-1]
            i = file_path.find("-")
            user_name = file_path[:i]
            heart_date = file_path[i + 1:i + 11]
            heart_time = file_path[i + 12:i + 20].replace("-", ":")
            record_time = string_to_time(heart_time)
            heart_time = time_to_string(record_time - datetime.timedelta(minutes=1, seconds=27))
            self.record_heart = record_heart_time(record_date=heart_date, record_time=heart_time,
                                                  start_time=heart_time, end_time="", user_name=user_name)
            self.record_heart.save()
            self.heart_data = {}

    def on_deleted(self, event):
        if event.is_directory:
            print("directory deleted:{0}".format(event.src_path))
        else:
            print("file deleted:{0}".format(event.src_path))

    def save_to_mysql(self):
        print(self.heart_data)
        end_time = ""
        for key, value in self.heart_data.items():
            total = 0
            rates = ""
            for rate in value:
                rates += rate + " "
                total += int(rate)
            record_time = string_to_time(key)
            heart_time = time_to_string(record_time - datetime.timedelta(minutes=1, seconds=27))
            data = heart_data(record_id=self.record_heart.id, heart_time=heart_time, heart_date=self.record_heart.record_date,
                              heart_rate=rates, average_rate=int(total / len(value)),
                              user_name=self.record_heart.user_name)
            data.save()
            end_time = heart_time
        self.record_heart.end_time = end_time
        self.record_heart.save()
        self.heart_file.close()
        self.record_heart = None
        self.heart_file = None
        self.heart_data = None

    def on_modified(self, event):
        if event.is_directory:
            print("directory modified:{0}".format(event.src_path))
        else:
            # print("file modified:{0}".format(event.src_path))
            file_path = event.src_path
            if self.heart_file is None:
                # self.heart_file = open(event.src_path, "r")
                # file_path = file_path.split("\\")[-1]
                # i = file_path.find("-")
                # user_name = file_path[:i]
                # heart_date = file_path[i + 1:i + 11]
                # heart_time = file_path[i + 12:i + 20].replace("-", ":")
                # self.record_heart = record_heart_time(record_date=heart_date, record_time=heart_time,
                #                                       start_time=heart_time, end_time="", user_name=user_name)
                # self.record_heart.save()
                # self.heart_data = {}
                pass
            else:
                while True:
                    line = self.heart_file.readline()
                    if not line:
                        break
                    line = line.strip()
                    # print(line)
                    logging.info(line)
                    if "END" in line:
                        self.save_to_mysql()
                        break
                    d1 = line.split("-")
                    d2 = d1[3]
                    d3 = d2.split(":")
                    h_time = get_normal_str(d3[0]) + ":" + get_normal_str(d3[1]) + ":" + get_normal_str(d3[2])
                    # print(h_time)
                    d4 = d3[3]
                    d5 = d4.split("\t")
                    # print(d5[-1])
                    if self.heart_data.get(h_time) is None:
                        self.heart_data[h_time] = []
                    self.heart_data[h_time].append(d5[-1])


class ShakeEventHandler(FileSystemEventHandler):
    def __init__(self):
        FileSystemEventHandler.__init__(self)
        self.shake_file = None
        self.record_shake = None
        self.x_data = None
        self.x_detail_data = None
        self.y_data = None
        self.y_detail_data = None
        self.end_time = None

    def on_moved(self, event):
        if event.is_directory:
            print("directory moved from {0} to {1}".format(event.src_path, event.dest_path))
        else:
            print("file moved from {0} to {1}".format(event.src_path, event.dest_path))

    def on_created(self, event):
        if event.is_directory:
            print("directory created:{0}".format(event.src_path))
        else:
            print("file created:{0}".format(event.src_path))
            logging.info("file created:" + event.src_path)
            file_path = event.src_path.split("\\")[-1]
            # shake_date = file_path[2:12]
            # shake_time = file_path[13:21].replace("-", ":")
            i = file_path.find("-")
            user_name = file_path[:i]
            shake_date = file_path[i + 1:i + 11]
            shake_time = file_path[i + 12:i + 20].replace("-", ":")
            self.shake_file = open(event.src_path, "r")
            record_time = string_to_time(shake_time)
            shake_time = time_to_string(record_time - datetime.timedelta(minutes=1, seconds=27))
            self.record_shake = record_shake_time(record_date=shake_date, record_time=shake_time,
                                                  start_time=shake_time, end_time="", user_name=user_name)
            self.record_shake.save()
            self.x_data = ""
            self.x_detail_data = {}
            self.y_data = ""
            self.y_detail_data = {}

    def on_deleted(self, event):
        if event.is_directory:
            print("directory deleted:{0}".format(event.src_path))
        else:
            print("file deleted:{0}".format(event.src_path))

    def save_to_mysql(self):
        print(self.x_detail_data)
        print(self.y_detail_data)
        x = ""
        y = ""
        for key, value in self.x_detail_data.items():
            x += key + ":" + value + "\n"
        for key, value in self.y_detail_data.items():
            y += key + ":" + value + "\n"
        self.record_shake.shake_x_data = self.x_data[:-1]
        self.record_shake.shake_y_data = self.y_data[:-1]
        self.record_shake.shake_x_detail_data = x
        self.record_shake.shake_y_detail_data = y
        self.record_shake.end_time = self.end_time
        self.record_shake.save()
        self.shake_file.close()
        self.shake_file = None
        self.record_shake = None
        self.x_data = None
        self.x_detail_data = None
        self.y_data = None
        self.y_detail_data = None
        self.end_time = None

    def on_modified(self, event):
        if event.is_directory:
            print("directory modified:{0}".format(event.src_path))
        else:
            # print("file modified:{0}".format(event.src_path))
            if self.shake_file is None:
                # file_path = event.src_path.split("\\")[-1]
                # i = file_path.find("-")
                # user_name = file_path[:i]
                # shake_date = file_path[i + 1:i + 11]
                # shake_time = file_path[i + 12:i + 20].replace("-", ":")
                # self.shake_file = open(event.src_path, "r")
                # self.record_shake = record_shake_time(record_date=shake_date, record_time=shake_time,
                #                                       start_time=shake_time, end_time="", user_name=user_name)
                # self.record_shake.save()
                # self.x_data = ""
                # self.x_detail_data = {}
                # self.y_data = ""
                # self.y_detail_data = {}
                pass
            else:
                while True:
                    line = self.shake_file.readline()
                    if not line:
                        break
                    line = line.strip()
                    if "END" in line:
                        self.save_to_mysql()
                        break
                    # print(line)
                    logging.info(line)
                    i = find_n_sub_str(line, "-", 2, 0)
                    line2 = line[i + 1:]
                    d2 = line2
                    d3 = d2.split(":")
                    h_time = get_normal_str(d3[0]) + ":" + get_normal_str(d3[1]) + ":" + get_normal_str(d3[2])
                    record_time = string_to_time(h_time)
                    h_time = time_to_string(record_time - datetime.timedelta(minutes=1, seconds=27))
                    # print(h_time)
                    self.end_time = h_time
                    d4 = d3[3]
                    d5 = d4.split("\t")
                    self.x_data += d5[-2] + ","
                    if self.x_detail_data.get(h_time) is None:
                        self.x_detail_data[h_time] = ""
                    self.x_detail_data[h_time] += d5[-2] + ","
                    self.y_data += d5[-1] + ","
                    if self.y_detail_data.get(h_time) is None:
                        self.y_detail_data[h_time] = ""
                    self.y_detail_data[h_time] += d5[-1] + ","
                    # print(d5[-2])
                    # print(d5[-1])


if __name__ == "__main__":
    observer = Observer()
    heart_event_handler = HeartEventHandler()
    shake_event_handler = ShakeEventHandler()
    observer.schedule(heart_event_handler, "D:/code/shoot/simulation_data/Heart", True)
    observer.schedule(shake_event_handler, "D:/code/shoot/simulation_data/Hand", True)
    observer.start()
    observer.join()
