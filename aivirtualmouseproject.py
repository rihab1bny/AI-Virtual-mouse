import cv2
import numpy as np
import HandTrackingModule as htm
import time
import pyautogui
import os
import absl.logging
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Suppress unnecessary logging
absl.logging.set_verbosity(absl.logging.ERROR)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

class VirtualMouse:
    def __init__(self):
        self.wCam, self.hCam = 1280, 720
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, self.wCam)
        self.cap.set(4, self.hCam)
        self.cap.set(cv2.CAP_PROP_FPS, 60)
        
        self.smoothening = 7
        self.frameR = 150
        self.plocX, self.plocY = 0, 0
        self.points_buffer = []
        self.buffer_length = 8
        
        self.pTime = 0
        self.zoom_cd = time.time()
        self.scroll_cd = time.time()
        self.click_cd = time.time()
        self.screenshot_cd = time.time()  # Cooldown for screenshot
        
        self.detector = htm.handDetector(maxHands=1, detectionCon=0.9, trackCon=0.7)
        self.wScr, self.hScr = pyautogui.size()
        
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(interface, POINTER(IAudioEndpointVolume))
        self.volRange = self.volume.GetVolumeRange()
    
    def process_gestures(self, img, lmList):
        if len(lmList) == 0:
            return
        
        fingers = self.detector.fingersUp()
        x1, y1 = lmList[8][1], lmList[8][2]
        current_time = time.time()

        # Cursor Movement
        if fingers == [0, 1, 0, 0, 0]:  # Only index finger up
            x3 = np.interp(x1, (self.frameR, self.wCam - self.frameR), (0, self.wScr))
            y3 = np.interp(y1, (self.frameR, self.hCam - self.frameR), (0, self.hScr))
            self.plocX += (x3 - self.plocX) / self.smoothening
            self.plocY += (y3 - self.plocY) / self.smoothening
            pyautogui.moveTo(self.plocX, self.plocY)
            return  # Stop processing further gestures
        
        # Left Click
        if fingers == [0, 1, 1, 0, 0] and current_time - self.click_cd > 0.3:  # Index + Middle Up
            length, img, _ = self.detector.findDistance(8, 12, img)
            if length < 30:
                pyautogui.click()
                self.click_cd = current_time
            return

        # Right Click
        if fingers == [0, 1, 1, 1, 0] and current_time - self.click_cd > 0.5:  # Index + Middle + Ring Up
            pyautogui.rightClick()
            self.click_cd = current_time
            return

        # Volume Control (Only Thumb + Index Finger)
        if fingers == [1, 1, 0, 0, 0]:  # Prevents conflict with zoom
            length, img, _ = self.detector.findDistance(4, 8, img)
            vol = np.interp(length, [30, 150], self.volRange[0:2])
            self.volume.SetMasterVolumeLevel(vol, None)
            return



        # Zoom In (Thumb + Pinky Finger up)
        if fingers == [1, 0, 0, 0, 1]:
            print("Zoom In Gesture")
            length, img, _ = self.detector.findDistance(4, 20, img)  # Measure the distance between thumb and pinky
            if length > 100:  # Adjust threshold to make sure it's a zoom-in gesture
                pyautogui.hotkey('ctrl', '+')

    # Zoom Out (Thumb Only Up)
        if fingers == [1, 0, 0, 0, 0]:
            print("Zoom Out Gesture")
            pyautogui.hotkey('ctrl', '-')




        # Scroll Up (All fingers up)
        if fingers == [1, 1, 1, 1, 1] and current_time - self.scroll_cd > 0.5:
            pyautogui.scroll(40)
            self.scroll_cd = current_time
            return

        # Scroll Down (Fist)
        if fingers == [0, 0, 0, 0, 0] and current_time - self.scroll_cd > 0.5:
            pyautogui.scroll(-40)
            self.scroll_cd = current_time
            return
        
        # Screenshot Gesture (Fist - All fingers curled)
        if fingers == [0, 0, 0, 0, 0] and current_time - self.scroll_cd > 0.5:  # Only fist gesture
            pyautogui.screenshot('screenshot.png')  # Take screenshot
            print("Screenshot taken")  # Debugging line to confirm gesture
            self.scroll_cd = current_time  # Reset cooldown to avoid continuous screenshot
            return

    
    def is_fingers_bent(self, lmList):
        # Check for a relaxed fist-like gesture where fingers are slightly bent
        bent = True
        for tip, base in zip([4, 8, 12, 16, 20], [3, 7, 11, 15, 19]):
            if lmList[tip][2] > lmList[base][2] + 10:  # Tip should be significantly below base joint for a bent finger
                bent = False
                break
        return bent
    
    def run(self):
        while True:
            success, img = self.cap.read()
            if not success:
                continue
            
            img = cv2.flip(img, 1)
            img = self.detector.findHands(img, draw=False)  # Set draw=False to avoid drawing landmarks
            lmList = self.detector.findPosition(img)
            
            self.process_gestures(img, lmList)
            
            cTime = time.time()
            fps = 1 / (cTime - self.pTime)
            self.pTime = cTime
            
            cv2.putText(img, f'FPS: {int(fps)}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow("AI Virtual Mouse v3", img)
            if cv2.waitKey(1) == 27:
                break
                
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    vm = VirtualMouse()
    vm.run()
