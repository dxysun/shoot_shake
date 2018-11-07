from watchdog.observers import Observer
from watchdog.events import *
import time
import sys
import os
import datetime
import django

# sys.path.append('../shoot_shake')
# os.chdir('../shoot_shake')
sys.path.append('./shoot_shake')
sys.path.append('../shoot_shake')
os.chdir('./shoot_shake')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shoot_shake.settings")
django.setup()
from shootweb.models import *


# 把datetime转成字符串
def time_to_string(dt):
    return dt.strftime("%H-%M-%S")


# 把字符串转成datetime
def string_to_time(string):
    return datetime.datetime.strptime(string, "%H-%M-%S")


class HeartEventHandler(FileSystemEventHandler):
    def __init__(self):
        FileSystemEventHandler.__init__(self)

    def on_moved(self, event):
        if event.is_directory:
            pass
            # print("directory moved from {0} to {1}".format(event.src_path, event.dest_path))
        else:
            # print("file moved from {0} to {1}".format(event.src_path, event.dest_path))
            pass

    def on_created(self, event):
        if event.is_directory:
            # print("directory created:{0}".format(event.src_path))
            pass
        else:
            print("file created:{0}".format(event.src_path))
            time.sleep(1)
            with open(event.src_path, 'r', encoding='gbk') as file:
                print("heart_file")
                heart_file = event.src_path
                i = heart_file.find("Heart")
                heart_date = heart_file[i + 5:i + 15]
                heart_time = heart_file[i + 16:i + 25]
                heart_time = heart_time.replace("-", ":")
                print(heart_date)
                print(heart_time)
                data = file.readlines()  # 读取全部内容 ，并以列表方式返回
                records = {}
                for line in data:
                    line = line.strip()
                    line = line.split("：")
                    if records.get(line[0]) is None:
                        records[line[0]] = []
                    records[line[0]].append(line[1])
                # print(records)
                context = ""
                record_heart = record_heart_time(record_date=heart_date, record_time=heart_time, start_time=heart_time,
                                                 end_time="")
                record_heart.save()
                print(record_heart.id)
                end_time = ""
                for key, value in records.items():
                    t1 = string_to_time(key)
                    # new_time = time_to_string(t1 - datetime.timedelta(minutes=1, seconds=27))
                    context += time_to_string(t1) + " : "
                    rates = ""
                    total = 0
                    for rate in value:
                        context += rate + " "
                        rates += rate + " "
                        total += int(rate)
                    t = key.replace("-", ":")
                    data = heart_data(record_id=record_heart.id, heart_time=t, heart_date=heart_date,
                                      heart_rate=rates, average_rate=int(total / len(value)))
                    data.save()
                    end_time = t
                    context += "\n"
                record_heart.end_time = end_time
                record_heart.save()
                print(context)

    def on_deleted(self, event):
        if event.is_directory:
            # print("directory deleted:{0}".format(event.src_path))
            pass
        else:
            # print("file deleted:{0}".format(event.src_path))
            pass

    def on_modified(self, event):
        if event.is_directory:
            # print("directory modified:{0}".format(event.src_path))
            pass
        else:
            # print("file modified:{0}".format(event.src_path))
            pass


class ShakeXEventHandler(FileSystemEventHandler):
    def __init__(self):
        FileSystemEventHandler.__init__(self)

    def on_moved(self, event):
        if event.is_directory:
            # print("directory moved from {0} to {1}".format(event.src_path, event.dest_path))
            pass
        else:
            # print("file moved from {0} to {1}".format(event.src_path, event.dest_path))
            pass

    def on_created(self, event):
        if event.is_directory:
            # print("directory created:{0}".format(event.src_path))
            pass
        else:
            print("file created:{0}".format(event.src_path))
            time.sleep(1)
            with open(event.src_path, 'r', encoding='gbk') as file:
                print("shake_x")
                shake_file = event.src_path
                i = shake_file.find("BesideX")
                shake_date = shake_file[i + 7:i + 17]
                shake_time = shake_file[i + 18:i + 27]
                shake_time = shake_time.replace("-", ":")
                print(shake_date)
                print(shake_time)
                data = file.readlines()  # 读取全部内容 ，并以列表方式返回
                records = {}
                for line in data:
                    line = line.strip()
                    line = line.split("：")
                    if records.get(line[0]) is None:
                        records[line[0]] = []
                    records[line[0]].append(line[1])
                # print(records)
                context = ""
                context_all = ""
                end_time = ""
                for key, value in records.items():
                    # t1 = string_to_time(key)
                    # new_time = time_to_string(t1 - datetime.timedelta(minutes=1, seconds=27))
                    context_all += key + ":"
                    end_time = key
                    for shake in value:
                        shake = shake.split('.')
                        data = float(shake[0]) / 1000
                        data = '%.03f' % data
                        context_all += str(data) + ","
                        context += str(data) + ","
                    context_all += "\n"
                record_shakes = record_shake_time.objects.filter(record_date=shake_date).filter(record_time=shake_time)
                if len(record_shakes) == 0:
                    end_time = end_time.replace("-", ":")
                    record_shake = record_shake_time(record_date=shake_date, record_time=shake_time,
                                                     start_time=shake_time, end_time=end_time, shake_x_data=context,
                                                     shake_x_detail_data=context_all)
                    record_shake.save()
                else:
                    record_shake = record_shakes[0]
                    record_shake.shake_x_data = context
                    record_shake.shake_x_detail_data = context_all
                    record_shake.save()
                print(context_all)

    def on_deleted(self, event):
        if event.is_directory:
            # print("directory deleted:{0}".format(event.src_path))
            pass
        else:
            # print("file deleted:{0}".format(event.src_path))
            pass

    def on_modified(self, event):
        if event.is_directory:
            # print("directory modified:{0}".format(event.src_path))
            pass
        else:
            # print("file modified:{0}".format(event.src_path))
            pass


class ShakeYEventHandler(FileSystemEventHandler):
    def __init__(self):
        FileSystemEventHandler.__init__(self)

    def on_moved(self, event):
        if event.is_directory:
            # print("directory moved from {0} to {1}".format(event.src_path, event.dest_path))
            pass
        else:
            # print("file moved from {0} to {1}".format(event.src_path, event.dest_path))
            pass

    def on_created(self, event):
        if event.is_directory:
            # print("directory created:{0}".format(event.src_path))
            pass
        else:
            print("file created:{0}".format(event.src_path))
            time.sleep(1)
            with open(event.src_path, 'r', encoding='gbk') as file:
                print("shake_y")
                shake_file = event.src_path
                i = shake_file.find("BesideY")
                shake_date = shake_file[i + 7:i + 17]
                shake_time = shake_file[i + 18:i + 27]
                shake_time = shake_time.replace("-", ":")
                print(shake_date)
                print(shake_time)
                data = file.readlines()  # 读取全部内容 ，并以列表方式返回
                records = {}
                for line in data:
                    line = line.strip()
                    line = line.split("：")
                    if records.get(line[0]) is None:
                        records[line[0]] = []
                    records[line[0]].append(line[1])
                # print(records)
                context = ""
                context_all = ""
                end_time = ""
                for key, value in records.items():
                    # t1 = string_to_time(key)
                    # new_time = time_to_string(t1 - datetime.timedelta(minutes=1, seconds=27))
                    context_all += key + ":"
                    end_time = key
                    for shake in value:
                        shake = shake.split('.')
                        data = float(shake[0]) / 1000
                        data = str('%.03f' % data)
                        context_all += data + ","
                        context += data + ","
                    context_all += "\n"
                record_shakes = record_shake_time.objects.filter(record_date=shake_date).filter(record_time=shake_time)
                if len(record_shakes) == 0:
                    end_time = end_time.replace("-", ":")
                    record_shake = record_shake_time(record_date=shake_date, record_time=shake_time,
                                                     start_time=shake_time, end_time=end_time, shake_y_data=context,
                                                     shake_y_detail_data=context_all)
                    record_shake.save()
                else:
                    record_shake = record_shakes[0]
                    record_shake.shake_y_data = context
                    record_shake.shake_y_detail_data = context_all
                    record_shake.save()
                print(context_all)

    def on_deleted(self, event):
        if event.is_directory:
            # print("directory deleted:{0}".format(event.src_path))
            pass
        else:
            # print("file deleted:{0}".format(event.src_path))
            pass

    def on_modified(self, event):
        if event.is_directory:
            # print("directory modified:{0}".format(event.src_path))
            pass
        else:
            # print("file modified:{0}".format(event.src_path))
            pass


class GradeEventHandler(FileSystemEventHandler):
    def __init__(self):
        FileSystemEventHandler.__init__(self)
        self.heart_file = None
        self.shake_file = None

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
            self.heart_file = open(event.src_path, "r")

    def on_deleted(self, event):
        if event.is_directory:
            print("directory deleted:{0}".format(event.src_path))
        else:
            print("file deleted:{0}".format(event.src_path))

    def on_modified(self, event):
        if event.is_directory:
            print("directory modified:{0}".format(event.src_path))
        else:
            # print("file modified:{0}".format(event.src_path))
            file_path = event.src_path
            if self.heart_file is None:
                self.heart_file = open(event.src_path, "r")
            else:
                while True:
                    line = self.heart_file.readline()
                    if not line:
                        break
                    line = line.strip()
                    print(line)


class ShakeEventHandler(FileSystemEventHandler):
    def __init__(self):
        FileSystemEventHandler.__init__(self)
        self.heart_file = None
        self.shake_file = None

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
            self.shake_file = open(event.src_path, "r")

    def on_deleted(self, event):
        if event.is_directory:
            print("directory deleted:{0}".format(event.src_path))
        else:
            print("file deleted:{0}".format(event.src_path))

    def on_modified(self, event):
        if event.is_directory:
            print("directory modified:{0}".format(event.src_path))
        else:
            # print("file modified:{0}".format(event.src_path))
            file_path = event.src_path
            if self.shake_file is None:
                self.shake_file = open(event.src_path, "r")
            else:
                while True:
                    line = self.shake_file.readline()
                    if not line:
                        break
                    line = line.strip()
                    print(line)


if __name__ == "__main__":
    observer = Observer()
    heart_event_handler = HeartEventHandler()
    shake_event_handler = ShakeEventHandler()
    # shake_x_event_handler = ShakeXEventHandler()
    # shake_y_event_handler = ShakeYEventHandler()
    observer.schedule(heart_event_handler, "D:/code/shoot/simulation_data/heart", True)
    observer.schedule(shake_event_handler, "D:/code/shoot/simulation_data/shake/x", True)
    # observer.schedule(shake_y_event_handler, "D:/code/shoot/simulation_data/shake/y", True)
    observer.start()
    observer.join()
