import cv2
import mediapipe as mp
import numpy as np
import time
import keyboard
import tkinter as tk
from pynput.mouse import Button, Controller
from mediapipe.framework.formats import landmark_pb2

mouse = Controller()
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
hotkey = 'Shift'
screenRes = (0, 0)

def tk_arg():
    global screenRes
    root = tk.Tk()
    root.title("Control Panel")

    background_color = '#2D2D2D' 
    foreground_color = '#E0E0E0'  
    button_color = '#4F4F4F' 
    highlight_color = '#606060' 

    root.configure(background=background_color)
    root.geometry("370x320")
    screenRes = (root.winfo_screenwidth(), root.winfo_screenheight())

    Val1 = tk.IntVar()
    Val2 = tk.IntVar()
    Val4 = tk.IntVar()
    Val4.set(30)

    place = ['Normal', 'Above', 'Behind']

    tk.Label(root, text='Camera', bg=background_color, fg=foreground_color).grid(row=1)
    for i in range(4):
        tk.Radiobutton(root, value=i, variable=Val1, text=f'Device{i}', bg=background_color, fg=foreground_color, selectcolor=highlight_color).grid(row=2, column=i*2)

    tk.Label(root, text=' ', bg=background_color).grid(row=3)
    tk.Label(root, text='How to place', bg=background_color, fg=foreground_color).grid(row=4)
    for i in range(3):
        tk.Radiobutton(root, value=i, variable=Val2, text=f'{place[i]}', bg=background_color, fg=foreground_color, selectcolor=highlight_color).grid(row=5, column=i*2)

    tk.Label(root, text=' ', bg=background_color).grid(row=6)
    tk.Label(root, text='Sensitivity', bg=background_color, fg=foreground_color).grid(row=7)
    tk.Scale(root, orient='h', from_=1, to=100, variable=Val4, bg=background_color, fg=foreground_color, troughcolor=highlight_color).grid(row=8, column=2)

    tk.Label(root, text=' ', bg=background_color).grid(row=9)
    tk.Button(root, text="Continue", command=root.destroy, bg=button_color, fg=foreground_color).grid(row=10, column=2)

    tk.Label(root, text='Made by Yair, David and Anton', bg=background_color, fg=foreground_color).grid(row=11, columnspan=4)

    root.mainloop()
    cap_device = Val1.get()
    mode = Val2.get()
    kando = Val4.get() / 10
    return cap_device, mode, kando



def draw_circle(image, x, y, roudness, color):
    cv2.circle(image, (int(x), int(y)), roudness, color,
               thickness=5, lineType=cv2.LINE_8, shift=0)

def calculate_distance(l1, l2):
    v = np.array([l1[0], l1[1]])-np.array([l2[0], l2[1]])
    distance = np.linalg.norm(v)
    return distance

def calculate_moving_average(landmark, ran, LiT):   
    while len(LiT) < ran:               
        LiT.append(landmark)
    LiT.append(landmark)                
    if len(LiT) > ran:                  
        LiT.pop(0)
    return sum(LiT)/ran

def main(cap_device, mode, kando):
    dis = 0.7                           
    preX, preY = 0, 0
    nowCli, preCli = 0, 0               
    norCli, prrCli = 0, 0               
    douCli = 0                          
    i, k, h = 0, 0, 0
    LiTx, LiTy, list0x, list0y, list1x, list1y, list4x, list4y, list6x, list6y, list8x, list8y, list12x, list12y = [
    ], [], [], [], [], [], [], [], [], [], [], [], [], []   
    nowUgo = 1
    cap_width = 1920
    cap_height = 1080
    start, c_start = float('inf'), float('inf')
    c_text = 0

    window_name = 'HandPilot'
    cv2.namedWindow(window_name)
    cap = cv2.VideoCapture(cap_device)
    cap.set(cv2.CAP_PROP_FPS, 60)
    cfps = int(cap.get(cv2.CAP_PROP_FPS))
    if cfps < 30:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, cap_width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cap_height)
        cfps = int(cap.get(cv2.CAP_PROP_FPS))

    ran = max(int(cfps/10), 1)
    hands = mp_hands.Hands(
        min_detection_confidence=0.8,   
        min_tracking_confidence=0.8,    
        max_num_hands=1                 
    )

    while cap.isOpened():
        p_s = time.perf_counter()
        success, image = cap.read()
        if not success:
            continue
        if mode == 1:                   
            image = cv2.flip(image, 0)  
        elif mode == 2:                 
            image = cv2.flip(image, 1)  

        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        image.flags.writeable = False   
        results = hands.process(image)  
        image.flags.writeable = True    
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        image_height, image_width, _ = image.shape

        if results.multi_hand_landmarks:

            for hand_landmarks in results.multi_hand_landmarks:

                connection_drawing_spec = mp_drawing.DrawingSpec(color=(0, 0, 0), thickness=5)
                mp_drawing.draw_landmarks(
                    image, 
                    hand_landmarks, 
                    mp_hands.HAND_CONNECTIONS,
                    connection_drawing_spec=connection_drawing_spec)

            if keyboard.is_pressed(hotkey):  
                can = 1
                c_text = 0          
            else:                   
                can = 0
                c_text = 1          

            if can == 1:

                if i == 0:
                    preX = hand_landmarks.landmark[8].x
                    preY = hand_landmarks.landmark[8].y
                    i += 1

                landmark0 = [calculate_moving_average(hand_landmarks.landmark[0].x, ran, list0x), calculate_moving_average(
                    hand_landmarks.landmark[0].y, ran, list0y)]
                landmark1 = [calculate_moving_average(hand_landmarks.landmark[1].x, ran, list1x), calculate_moving_average(
                    hand_landmarks.landmark[1].y, ran, list1y)]
                landmark4 = [calculate_moving_average(hand_landmarks.landmark[4].x, ran, list4x), calculate_moving_average(
                    hand_landmarks.landmark[4].y, ran, list4y)]
                landmark6 = [calculate_moving_average(hand_landmarks.landmark[6].x, ran, list6x), calculate_moving_average(
                    hand_landmarks.landmark[6].y, ran, list6y)]
                landmark8 = [calculate_moving_average(hand_landmarks.landmark[8].x, ran, list8x), calculate_moving_average(
                    hand_landmarks.landmark[8].y, ran, list8y)]
                landmark12 = [calculate_moving_average(hand_landmarks.landmark[12].x, ran, list12x), calculate_moving_average(
                    hand_landmarks.landmark[12].y, ran, list12y)]

                absKij = calculate_distance(landmark0, landmark1)

                absUgo = calculate_distance(landmark8, landmark12) / absKij

                absCli = calculate_distance(landmark4, landmark6) / absKij

                posx, posy = mouse.position

                nowX = calculate_moving_average(
                    hand_landmarks.landmark[8].x, ran, LiTx)
                nowY = calculate_moving_average(
                    hand_landmarks.landmark[8].y, ran, LiTy)

                dx = kando * (nowX - preX) * image_width
                dy = kando * (nowY - preY) * image_height

                dx = dx+0.5 
                dy = dy+0.5
                preX = nowX
                preY = nowY

                if posx+dx < 0:  
                    dx = -posx
                elif posx+dx > screenRes[0]:
                    dx = screenRes[0]-posx
                if posy+dy < 0:
                    dy = -posy
                elif posy+dy > screenRes[1]:
                    dy = screenRes[1]-posy

                if absCli < dis:
                    nowCli = 1         
                    draw_circle(image, hand_landmarks.landmark[8].x * image_width,
                                hand_landmarks.landmark[8].y * image_height, 20, (0, 250, 250))
                elif absCli >= dis:
                    nowCli = 0
                if np.abs(dx) > 7 and np.abs(dy) > 7:
                    k = 0                           
                if nowCli == 1 and np.abs(dx) < 7 and np.abs(dy) < 7:
                    if k == 0:          
                        start = time.perf_counter()
                        k += 1
                    end = time.perf_counter()
                    if end-start > 1.5:
                        norCli = 1
                        draw_circle(image, hand_landmarks.landmark[8].x * image_width,
                                    hand_landmarks.landmark[8].y * image_height, 20, (0, 0, 250))
                else:
                    norCli = 0

                if absUgo >= dis and nowUgo == 1:
                    mouse.move(dx, dy)
                    draw_circle(image, hand_landmarks.landmark[8].x * image_width,
                                hand_landmarks.landmark[8].y * image_height, 8, (250, 0, 0))

                if nowCli == 1 and nowCli != preCli:
                    if h == 1:                                  
                        h = 0
                    elif h == 0:                                
                        mouse.press(Button.left)

                if nowCli == 0 and nowCli != preCli:
                    mouse.release(Button.left)
                    k = 0

                    if douCli == 0:                             
                        c_start = time.perf_counter()
                        douCli += 1
                    c_end = time.perf_counter()
                    if 10*(c_end-c_start) > 5 and douCli == 1:  
                        mouse.click(Button.left, 2)             
                        douCli = 0

                if norCli == 1 and norCli != prrCli:

                    mouse.press(Button.right)
                    mouse.release(Button.right)
                    h = 1                                       

                if hand_landmarks.landmark[8].y-hand_landmarks.landmark[5].y > -0.06:
                    mouse.scroll(0, -dy/50)                     
                    draw_circle(image, hand_landmarks.landmark[8].x * image_width,
                                hand_landmarks.landmark[8].y * image_height, 20, (0, 0, 0))
                    nowUgo = 0
                else:
                    nowUgo = 1

                preCli = nowCli
                prrCli = norCli

        if c_text == 1:
            cv2.putText(image, f"Push {hotkey}", (20, 450),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 3)
        cv2.putText(image, "cameraFPS:"+str(cfps), (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)
        p_e = time.perf_counter()
        fps = str(int(1/(float(p_e)-float(p_s))))
        cv2.putText(image, "FPS:"+fps, (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)
        dst = cv2.resize(image, (800, 600))
        cv2.imshow(window_name, dst)
        if (cv2.waitKey(1) & 0xFF == 27) or (cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) == 0):
            break
    cap.release()

if __name__ == "__main__":
    cap_device, mode, kando = tk_arg()
    main(cap_device, mode, kando)
