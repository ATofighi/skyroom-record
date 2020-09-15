import os
import pyautogui
import time
import difflib
import math
import cv2
import numpy as np
import string
import random
import ffmpeg
import argparse

from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import ui
from selenium.webdriver.support import expected_conditions as EC
from skimage.metrics import structural_similarity as ssim

pyautogui.FAILSAFE = False

def click_on_page(icon):
    icon_x, icon_y = pyautogui.locateCenterOnScreen(icon, confidence=0.6)
    pyautogui.click(icon_x, icon_y)

def split_to_100bulks(arr):
    result = []
    for i in range(math.ceil(len(arr)/100)):
        result.append(arr[i*100:(i+1)*100])
    return result

def goto_class(driver):    
    driver.find_element_by_id('btn_guest').click()

def main():
    parser = argparse.ArgumentParser(description='This command will record a VClass page')
    parser.add_argument('-u', '--url', type=str, required=True, help='URL of vclass')
    parser.add_argument('-d', '--duration', type=float, required=True, help='Duration of class in minutes')

    args = parser.parse_args()

    SOURCE_DIR = os.path.abspath(os.path.dirname(__file__))
    BASE_DIR = os.path.dirname(SOURCE_DIR)

    download_path = os.path.join(BASE_DIR, 'downloads', datetime.now().isoformat() + '--' + ''.join(random.choices(string.ascii_lowercase, k=10)))
    os.mkdir(download_path)

    chrome_options = Options()
    chrome_options.add_extension(os.path.join(SOURCE_DIR, 'skyroom.crx'))
    chrome_options.add_experimental_option("prefs", {
    "download.default_directory": download_path,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
    })
    chrome_options.add_argument("--no-sandbox") 
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("disable-infobars") 


    driver = webdriver.Chrome(options=chrome_options)

    driver.implicitly_wait(10)
    time.sleep(5)

    driver.maximize_window()
    time.sleep(1)
    driver.maximize_window()

    # config skyroom
    driver.execute_script("window.open('about:blank', 'tab2');")

    driver.get("chrome-extension://pejdnafppnpfimpnipdkiidjancinenc/options.html")
    ui.Select(driver.find_element_by_id('video_bitrate')).select_by_value('1000')
    ui.Select(driver.find_element_by_id('audio_bitrate')).select_by_value('32')
    # ui.Select(driver.find_element_by_id('record_stop_action')).select_by_value('download')

    driver.find_element_by_id('btnSave').click()

    # go to vclass
    driver.switch_to.window(driver.window_handles[0])
    driver.get(args.url)

    # set name
    goto_class(driver)
    driver.find_element_by_xpath("//input[@class='full-width']")
    driver.execute_script("document.querySelector('.dlg-nickname .full-width').value = 'ضبط کننده‌ی خودکار';")
    driver.execute_script("document.querySelector('.dlg-nickname .btn').click();")

    # start record
    click_on_page('./skyroom-icon.png')
    time.sleep(0.5)
    click_on_page('./start-recording-btn.png')
    click_on_page('./skyroom-icon.png')
    pyautogui.click(0, 0)

    # wait for recording
    end_time = datetime.now() + timedelta(minutes=args.duration)
    old_screenshot = cv2.imdecode(np.frombuffer(driver.get_screenshot_as_png(), np.uint8), -1)
    while datetime.now() < end_time:
        cur_screenshot = cv2.imdecode(np.frombuffer(driver.get_screenshot_as_png(), np.uint8), -1)
        # import pdb; pdb.set_trace()
        similarity = ssim(old_screenshot, cur_screenshot, multichannel=True)
        if similarity > 0.98:
            driver.execute_script('window.onbeforeunload = function() {};')
            driver.refresh()
            goto_class(driver)
        time.sleep(max(0, min(30, (end_time-datetime.now()).total_seconds())))
        old_screenshot = cur_screenshot

    # stop record
    click_on_page('./skyroom-icon.png')
    time.sleep(0.5)
    click_on_page('./stop-recording-btn.png')

    # download file
    time.sleep(5)
    driver.switch_to.window(driver.window_handles[1])
    time.sleep(0.5)
    driver.find_element_by_id('download').click()

    # close windows
    time.sleep(5)
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    driver.close()

    # webm to mp4
    webm_file = os.listdir(download_path)[0]
    os.rename(os.path.join(download_path, webm_file), os.path.join(download_path, 'video.webm'))

    ffmpeg.input(os.path.join(download_path, 'video.webm')).output(os.path.join(download_path, 'video.mp4'), **{
        'vcodec': 'h264',
        'acodec': 'mp3',
    }).run()

if __name__ == "__main__":
    main()