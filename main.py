import argparse
import time

from whisper_mic import WhisperMic

import vision
from vimbot import Vimbot


def main(voice_mode):
    print("Initializing the Vimbot driver...")
    driver = Vimbot()

    print("Navigating to Booking")
    # site = "https://www.google.com"
    site = "https://www.jalan.net/yad313725/plan/?&screenId=UWW1380&roomCrack=200000&distCd=01&rootCd=04&yadNo=313725&callbackHistFlg=1&reSearchFlg=1&smlCd=221502&distCd=01&stayYear=2024&stayMonth=05&stayDay=19&dateUndecided=0&stayCount=1&roomCount=1&adultNum=2&childNum=0&minPrice=0&maxPrice=999999"
    driver.navigate(site)

    if voice_mode:
        print("Voice mode enabled. Listening for your command...")
        mic = WhisperMic()
        try:
            objective = mic.listen()
        except Exception as e:
            print(f"Error in capturing voice input: {e}")
            return  # Exit if voice input fails
        print(f"Objective received: {objective}")
    else:
        objective = input("Please enter your objective: ")

    actions_history = []

    while True:
        time.sleep(3)
        print("Capturing the screen...")
        screenshot = driver.capture()
        # print(f"hint markers: {driver.local_hint_descriptors}")
        print("Getting actions for the given objective...")
        action = vision.get_actions(screenshot, objective, driver.local_hint_descriptors, actions_history)
        actions_history.append(action)
        print(f"Vison model JSON Response: {action}")
        if driver.perform_action(action):  # returns True if done
            break


def main_entry():
    parser = argparse.ArgumentParser(description="Run the Vimbot with optional voice input.")
    parser.add_argument(
        "--voice",
        help="Enable voice input mode",
        action="store_true",
    )
    args = parser.parse_args()
    main(args.voice)


if __name__ == "__main__":
    try:
        main_entry()
    except KeyboardInterrupt:
        print("Exiting...")
