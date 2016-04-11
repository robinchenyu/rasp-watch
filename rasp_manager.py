#!/usr/bin/python
# Author : ChenYu
# Date   : 09/03/2014


# Import required Python libraries
import time
import threading
import os
import datetime
import fnmatch
import subprocess
import RPi.GPIO as GPIO
import sqlite3
import logging


# Define GPIO to use on Pi
GPIO_IN  = 11
GPIO_OUT = 12


FORMAT = '%(asctime)-15s %(thread)d %(filename)s[line:%(lineno)d] %(levelname)s %(message)s'
logging.basicConfig(format=FORMAT, filename='log/myapp.log')
logger = logging.getLogger('rasp_manager')


class RaspManager(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self.running = True
        self.interval = 5
        self.start_time = '08:00'
        self.end_time = '22:00'
        self.cnt = 0

        self.power_on = False

        logger.info("start up RaspManager thread")

    def _init_gpio(self):
        try:
            GPIO.setmode(GPIO.BOARD)
            # Set pins as output and input
            print("set gpio port")
            GPIO.setup(GPIO_IN,  GPIO.IN)
            GPIO.setup(GPIO_OUT, GPIO.OUT)
            self.take_photo()
        except Exception as e:
            logger.warning("set gpio pin ports failed %s" % str(e))

    def start_power(self):
        # print("set gpio port to open")
        try:
            GPIO.output(GPIO_OUT, GPIO.HIGH)
            self.power_on = True
        except Exception as e:
            logger.warning("start power failed %s" % str(e))
            self._init_gpio()
            self.power_on = False

    def shutdown_power(self):
        try:
            GPIO.output(GPIO_OUT, GPIO.LOW)
            self.power_on = False
        except Exception as e:
            logger.warning("shutdown power failed %s" % str(e))
            self._init_gpio()
            self.power_on = True

    def take_photo(self):
        proc = subprocess.Popen(["raspistill", "-w", "1280", "-h", "800", "-o", "static/photos/auto%d.jpg" % self.cnt])
        self.cnt += 1
        if self.cnt == 1000:
            self.cnt = 0
        try:
            outs, errs = proc.communicate(timeout=15)
            logger.warning("take photo %d" % self.cnt)
        except Exception as e:
            logger.error("take photos failed %s" % str(e))
            proc.kill()

    def update_config(self):
        c = self.db.cursor()
        c.execute('''select * from rasp_sysset''')
        for row in c:
            id1, name, val = row
            self.update_settings(name, val)

    def update_settings(self, k, v):
        if k == 'start_time':
            self.start_time = v
        elif k == 'end_time':
            self.end_time = v
        elif k == 'interval':
            self.interval = v
        else:
            logger.warning("update param: no param %r => %r" % (k, v))

        logger.info("update param: %r => %r" % (k, v))

    def run(self):

        self._init_gpio()
        conn = sqlite3.connect('rasp_db.db')
        self.db = conn
        count = 0
        while self.running:
            count += 1
            now = datetime.datetime.now()
            cur = now.hour*60 + now.minute
            starttime = self.get_minutes(self.start_time)
            endtime = self.get_minutes(self.end_time)
            # logger.warning("time: %r start: %r end:%r" % (now, self.start_time, self.end_time))
            if cur >= starttime and cur < endtime and (not self.power_on):
                self.start_power()
            elif (cur < starttime or cur >= endtime) and self.power_on:
                self.shutdown_power()

            if count % 6 == 0:
                self.update_config()

            inValue = 0
            try:
                inValue = GPIO.input(GPIO_IN)
            except Exception as e:
                logger.warning("get GPIO_IN failed %s " % str(e))
            if inValue != 0:
                self.take_photo()
            
            time.sleep(self.interval)


    def stop(self):
        GPIO.cleanup()
        self.running = False
        self.db.close()
        logger.info("RaspManager: stop")

    def get_minutes(self, timestr):
        h,m = timestr.split(':')
        return int(h)*60 + int(m)




def start():
    rasp = RaspManager()
    logger.warning("start rasp!!!!!")
    rasp.start()
    return rasp

def stop():
    rasp.stop()

    
if __name__ == '__main__':
    try:
        rasp = start()
    except Exception as e:
        app.logger.error("exception %s" % str(e))
    finally:
        GPIO.cleanup()

    rasp.join()

    stop()

