from watchdog.observers import Observer
from watchdog.events import *
import sys
import os
import datetime
import django
import logging

dirname, filename = os.path.split(os.path.abspath(__file__))

sys.path.append(dirname + '/shoot_shake')
sys.path.append(dirname)
os.chdir(dirname)
logging.basicConfig(filename='log.txt', filemode="w", level=logging.ERROR)
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


class AllShakeEventHandler(FileSystemEventHandler):
    def __init__(self):
        FileSystemEventHandler.__init__(self)
        self.shake_file = None
        self.record_heart = None
        self.heart_datas = None
        self.record_all_shake = None
        self.x_beside_data = None
        self.x_beside_pos = None
        self.y_beside_data = None
        self.y_beside_pos = None
        self.x_up_data = None
        self.x_up_pos = None
        self.y_up_data = None
        self.y_up_pos = None
        self.end_time = None
        self.all_info = None

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
            i = file_path.find("-")
            user_name = file_path[:i]
            shake_date = file_path[i + 1:i + 11]
            shake_time = file_path[i + 12:i + 20].replace("-", ":")
            if self.shake_file is not None:
                self.shake_file.close()
            self.shake_file = open(event.src_path, "r")
            self.record_all_shake = shake_all_info(record_date=shake_date, record_time=shake_time,
                                                   start_time=shake_time, end_time="", user_name=user_name)
            self.record_heart = record_heart_time(record_date=shake_date, record_time=shake_time,
                                                  start_time=shake_time, end_time="", user_name=user_name)
            self.record_heart.save()
            self.heart_datas = {}
            self.record_all_shake.save()
            self.x_beside_data = ""
            self.x_beside_pos = ""
            self.y_beside_data = ""
            self.y_beside_pos = ""
            self.x_up_data = ""
            self.x_up_pos = ""
            self.y_up_data = ""
            self.y_up_pos = ""
            self.all_info = ""

    def on_deleted(self, event):
        if event.is_directory:
            print("directory deleted:{0}".format(event.src_path))
        else:
            print("file deleted:{0}".format(event.src_path))

    def save_to_mysql(self):
        self.record_all_shake.beside_x_data = self.x_beside_data[:-1]
        self.record_all_shake.beside_y_data = self.y_beside_data[:-1]
        self.record_all_shake.beside_x_pos = self.x_beside_pos[:-1]
        self.record_all_shake.beside_y_pos = self.y_beside_pos[:-1]
        self.record_all_shake.up_x_data = self.x_up_data[:-1]
        self.record_all_shake.up_y_data = self.y_up_data[:-1]
        self.record_all_shake.up_x_pos = self.x_up_pos[:-1]
        self.record_all_shake.up_y_pos = self.y_up_pos[:-1]
        self.record_all_shake.end_time = self.end_time
        self.record_all_shake.save()
        end_time = ""
        for key, value in self.heart_datas.items():
            total = 0
            rates = ""
            heart_value = set(value)
            for rate in heart_value:
                rates += rate + " "
                total += int(rate)
            heart_time = key
            data = heart_data(record_id=self.record_heart.id, heart_time=heart_time,
                              heart_date=self.record_heart.record_date,
                              heart_rate=rates, average_rate=int(total / len(heart_value)),
                              user_name=self.record_heart.user_name)
            data.save()
            end_time = heart_time
        self.record_heart.end_time = end_time
        self.record_heart.save()
        # self.shake_file.close()
        # self.shake_file = None
        # self.record_heart = None
        # self.heart_datas = None
        # self.record_all_shake = None
        # self.x_beside_data = None
        # self.x_beside_pos = None
        # self.y_beside_data = None
        # self.y_beside_pos = None
        # self.x_up_data = None
        # self.x_up_pos = None
        # self.y_up_data = None
        # self.y_up_pos = None
        # self.end_time = None
        # self.all_info = None
        print("update data success")

    def on_modified(self, event):
        if event.is_directory:
            print("directory modified:{0}".format(event.src_path))
        else:
            # print("file modified:{0}".format(event.src_path))
            if self.shake_file is None:
                self.shake_file = open(event.src_path, "r")
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
                    # logging.info(line)
                    i = find_n_sub_str(line, "-", 2, 0)
                    line2 = line[i + 1:]
                    d2 = line2
                    d3 = d2.split(":")
                    h_time = get_normal_str(d3[0]) + ":" + get_normal_str(d3[1]) + ":" + get_normal_str(d3[2])
                    self.end_time = h_time
                    d4 = d3[3]
                    d5 = d4.split("\t")
                    self.x_up_pos += d5[1] + ","
                    self.y_up_pos += d5[2] + ","
                    self.x_up_data += d5[3] + ","
                    self.y_up_data += d5[4] + ","
                    self.x_beside_pos += d5[5] + ","
                    self.y_beside_pos += d5[6] + ","
                    self.x_beside_data += d5[7] + ","
                    self.y_beside_data += d5[8] + ","
                    if self.heart_datas.get(h_time) is None:
                        self.heart_datas[h_time] = []
                    self.heart_datas[h_time].append(d5[9])
                    self.all_info += h_time + ":" + d5[0] + "#" + d5[1] + "#" + d5[2] + "#" + d5[3] + "#" + d5[
                        4] + "#" + d5[5] + "#" + d5[6] + "#" + d5[7] + "#" + d5[8] + "#" + d5[9] + "\n"


if __name__ == "__main__":
    observer = Observer()
    all_shake_event_handler = AllShakeEventHandler()
    observer.schedule(all_shake_event_handler, "D:/code/shoot/simulation_data/Heart", True)
    observer.start()
    observer.join()
