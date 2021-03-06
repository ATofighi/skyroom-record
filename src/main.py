import os
import pyautogui
import time
import math
import cv2
import numpy as np
import ffmpeg
import argparse
import logging

from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import ui
from skimage.metrics import structural_similarity as ssim

pyautogui.FAILSAFE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SKYROOM_ICON = (1272, 43)
START_RECORDING_ICON = (1136, 178)
BETWEEN_PAUSE_AND_STOP_ICON = (1196, 185)
RECORDING_TAB_ICON = (209, 17)
STOP_RECORDING_ICON = (1217, 180)
CENTER_OF_DOWNLOAD_BAR = (825, 861)
CLOSE_NOTIFICATION = (413, 83)

FAILURE_TEST_INTERVAL = timedelta(minutes=5)


def split_to_100bulks(arr):
    result = []
    for i in range(math.ceil(len(arr) / 100)):
        result.append(arr[i * 100:(i + 1) * 100])
    return result


def goto_class(driver):
    driver.find_element_by_id('btn_guest').click()


def is_skyroom_extension_open():
    return pyautogui.pixelMatchesColor(*SKYROOM_ICON, (225, 225, 225))


def is_tab_in_recording():
    return pyautogui.pixelMatchesColor(*RECORDING_TAB_ICON, (26, 115, 232))


def close_chrome_notification():
    pyautogui.click(*CLOSE_NOTIFICATION)


def open_skyroom_popup():
    for repeat_number in range(10):
        try:
            if not is_skyroom_extension_open():
                pyautogui.click(*SKYROOM_ICON)
                time.sleep(1)
            if not is_skyroom_extension_open():
                raise Exception(
                    'I clicked on skyroom icon but popup is not open! :|')

            break
        except Exception as e:
            logger.exception(e)


def close_skyroom_popup():
    for repeat_number in range(10):
        try:
            if is_skyroom_extension_open():
                pyautogui.click(*SKYROOM_ICON)
                time.sleep(1)
            if is_skyroom_extension_open():
                raise Exception(
                    'I clicked on skyroom icon but popup is not closed! :|')

            break
        except Exception as e:
            logger.exception(e)
    pyautogui.click(0, 0)


def force_refresh(driver):
    driver.execute_script('window.onbeforeunload = function() {};')
    time.sleep(0.5)
    driver.refresh()


def is_need_recording():
    return not os.path.exists('./force-stop-recording')


def main():
    parser = argparse.ArgumentParser(
        description='This command will record a VClass page')
    parser.add_argument('-u', '--url', type=str,
                        required=True, help='URL of vclass')
    parser.add_argument('-d', '--duration', type=float,
                        required=True, help='Duration of class in minutes')
    parser.add_argument('-n', '--name', type=str,
                        required=True, help='Name of downloads folder')
    parser.add_argument('-a', '--username', type=str,
                        default='ضبط کننده', help='Username of skyroom user')
    parser.add_argument('-e', '--encoding', type=str,
                        default='no-encode',
                        help='Encoding preset, see readme.md')

    args = parser.parse_args()

    SOURCE_DIR = os.path.abspath(os.path.dirname(__file__))
    BASE_DIR = os.path.dirname(SOURCE_DIR)

    try:
        os.mkdir(os.path.join(
            BASE_DIR,
            'downloads',
            args.name))
    except FileExistsError:
        pass
    download_path = os.path.join(
        BASE_DIR,
        'downloads',
        args.name,
        datetime.now().strftime("%Y-%m-%d--%H-%M"))
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

    logger.info('Opening google chrome')
    driver = None
    for retry_number in range(10):
        try:
            if driver:
                logger.info('Driver is not none, close it.')
                driver.close()
        except Exception as e:
            logger.exception(e)
        try:
            driver = webdriver.Chrome(options=chrome_options)

            driver.implicitly_wait(10)
            time.sleep(2)

            driver.maximize_window()
            time.sleep(1)
            driver.maximize_window()

            break
        except Exception as e:
            logger.exception(e)

    logger.info('Create new window for not closing browser')
    for retry_number in range(10):
        try:
            if len(driver.window_handles) < 2:
                driver.execute_script("window.open('about:blank', 'tab2');")
            time.sleep(2 * (retry_number + 1))

            break
        except Exception as e:
            logger.exception(e)

    logger.info('Configure skyroom extension')
    for retry_number in range(10):
        try:
            if len(driver.window_handles) > 1:
                driver.switch_to.window(driver.window_handles[0])
                driver.get(
                    "chrome-extension://"
                    "pejdnafppnpfimpnipdkiidjancinenc/options.html")
                ui.Select(driver.find_element_by_id(
                    'video_bitrate')).select_by_value('1000')
                ui.Select(driver.find_element_by_id(
                    'audio_bitrate')).select_by_value('32')

                driver.find_element_by_id('btnSave').click()
            time.sleep(2 * (retry_number + 1))

            break
        except Exception as e:
            logger.exception(e)

    logger.info('Open vclass')
    for retry_number in range(10):
        try:
            driver.switch_to.window(driver.window_handles[0])
            driver.get(args.url)
            time.sleep(2 * (retry_number + 1))

            break
        except Exception as e:
            logger.exception(e)

    logger.info('Login as guest')
    for retry_number in range(10):
        try:
            force_refresh(driver)
            time.sleep(5 * retry_number)
            goto_class(driver)
            driver.find_element_by_xpath("//input[@class='full-width']")
            driver.execute_script(
                "document.querySelector('.dlg-nickname .full-width').value"
                f" = '{args.username}';")
            driver.execute_script(
                "document.querySelector('.dlg-nickname .btn').click();")

            break
        except Exception as e:
            logger.exception(e)

    logger.info('Start record')
    for retry_number in range(10):
        try:
            open_skyroom_popup()

            if not is_tab_in_recording():
                if not pyautogui.pixelMatchesColor(
                        *START_RECORDING_ICON, (255, 0, 0)):
                    close_skyroom_popup()
                    raise Exception('Recording red color not found :|')

                pyautogui.click(*START_RECORDING_ICON)
                time.sleep(5)

            if not pyautogui.pixelMatchesColor(
                    *BETWEEN_PAUSE_AND_STOP_ICON, (245, 245, 245)):
                raise Exception('I can not see pause and stop icon!')
            if not is_tab_in_recording():
                raise Exception('Tab blue recording icon can not be seen!')

            close_skyroom_popup()

            break
        except Exception as e:
            logger.exception(e)

    close_chrome_notification()

    logger.info('Recording is started, watch for freeze detection!')
    end_time = datetime.now() + timedelta(minutes=args.duration)
    old_screenshot = cv2.imdecode(np.frombuffer(
        driver.get_screenshot_as_png(), np.uint8), -1)
    next_failure_test = datetime.now() + FAILURE_TEST_INTERVAL
    while datetime.now() < end_time and is_need_recording():
        if datetime.now() >= next_failure_test:
            for retry_number in range(10):
                try:
                    cur_screenshot = cv2.imdecode(np.frombuffer(
                        driver.get_screenshot_as_png(), np.uint8), -1)
                    similarity = ssim(
                        old_screenshot, cur_screenshot, multichannel=True)
                    if similarity > 0.98:
                        logger.info('Screenshots are too similar, refresh!')
                        force_refresh(driver)
                        goto_class(driver)
                    old_screenshot = cur_screenshot
                    break
                except Exception as e:
                    logger.exception(e)
            next_failure_test = datetime.now() + FAILURE_TEST_INTERVAL

        time.sleep(max(0, min(
            10,
            (end_time - datetime.now()).total_seconds()
        )))

    logger.info('Time is over, stop recording')
    for retry_number in range(10):
        try:
            time.sleep(5 * retry_number)
            if is_tab_in_recording():
                open_skyroom_popup()

                if not pyautogui.pixelMatchesColor(
                        *STOP_RECORDING_ICON, (0, 0, 0)):
                    raise Exception('I can not see stop recording black icon')
                pyautogui.click(*STOP_RECORDING_ICON)
                time.sleep(5)
                close_skyroom_popup()

            if is_tab_in_recording():
                raise Exception('I stop recording but tab is in recording :|')
            if len(driver.window_handles) < 2:
                raise Exception('Recording window is not open :(')

            break
        except Exception as e:
            logger.exception(e)

    # download file
    for retry_number in range(10):
        try:
            time.sleep(5)

            driver.switch_to.window(driver.window_handles[1])
            time.sleep(0.5)

            driver.find_element_by_id('download').click()
            time.sleep(5 * (1 + retry_number))

            if not pyautogui.pixelMatchesColor(
                    *CENTER_OF_DOWNLOAD_BAR, (255, 255, 255)):
                raise Exception('I can not see download bar')

            break
        except Exception as e:
            logger.exception(e)

    # close windows
    time.sleep(60 + 3 * args.duration)
    for retry_number in range(100):
        try:
            if len(os.listdir(download_path)) == 0 or not os.listdir(
                    download_path)[0].endswith('.webm'):
                raise Exception('Downloaded file can not be found!')
                time.sleep(10 * (1 + retry_number))
            break
        except Exception as e:
            logger.exception(e)

    for retry_number in range(100):
        try:
            driver.switch_to.window(driver.window_handles[0])
            driver.close()
            time.sleep(3)
            driver.switch_to.window(driver.window_handles[0])
            driver.close()
            break
        except Exception as e:
            logger.exception(e)

    # webm to mp4
    webm_file = os.path.join(
        download_path,
        os.listdir(download_path)[0]
    )
    new_webm_file = os.path.join(download_path, 'video.webm')
    os.rename(webm_file, new_webm_file)

    ffmpeg_pipe = ffmpeg.input(new_webm_file)
    if args.encoding == "quality-optimized":
        ffmpeg_pipe.output(
            os.path.join(download_path, 'video.mp4'),
            **{'vcodec': 'libx264', 'acodec': 'aac', },
            crf='36',
            tune='stillimage',
            preset='slow',
            movflags='+faststart'
        ).run()
    elif args.encoding == "speed-optimized":
        ffmpeg_pipe.output(
            os.path.join(download_path, 'video.mp4'),
            **{'vcodec': 'libx264', 'acodec': 'aac', },
            crf='28',
            preset='ultrafast',
            s='852x480',
            movflags='+faststart'
        ).run()
    elif args.encoding == "size-optimized":
        ffmpeg_pipe.output(
                os.path.join(download_path, 'video.mp4'),
                **{'vcodec': 'libx264', 'acodec': 'aac', },
                crf='28',
                tune='stillimage',
                preset='veryfast',
                s='640x360',
                movflags='+faststart'
            ).run()


if __name__ == "__main__":
    main()
