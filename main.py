import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import time

def move_cursor(ix, iy, cam_width, cam_height, screen_width, screen_height, prev_pos, smooth_factor):
    # Map index tip to screen and smooth movement
    screen_x = np.interp(ix, (0, cam_width), (0, screen_width))
    screen_y = np.interp(iy, (0, cam_height), (0, screen_height))
    run_x = prev_pos[0] + (screen_x - prev_pos[0]) / smooth_factor
    run_y = prev_pos[1] + (screen_y - prev_pos[1]) / smooth_factor
    pyautogui.moveTo(run_x, run_y, duration=0.01)
    return (run_x, run_y)

def detect_left_double_drag(ix, tx, state):
    # Handle single click, double click, and drag via thumb-index pinch
    current_time = time.time()
    if ix is not None and tx is not None:
        distance = np.hypot(tx - ix, state['ty'] - state['iy'])
        if distance < state['left_thresh']:
            if not state['pinch_active']:
                state['pinch_active'] = True
                state['pinch_start'] = current_time
                if current_time - state['last_click_time'] < state['double_click_interval']:
                    pyautogui.doubleClick()
                    state['last_click_time'] = 0
                else:
                    state['last_click_time'] = current_time
            else:
                held_time = current_time - state['pinch_start']
                if held_time > state['drag_interval'] and not state['dragging']:
                    pyautogui.mouseDown()
                    state['dragging'] = True
        else:
            if state['dragging']:
                pyautogui.mouseUp()
                state['dragging'] = False
            state['pinch_active'] = False
    else:
        if state['dragging']:
            pyautogui.mouseUp()
            state['dragging'] = False
        state['pinch_active'] = False

def detect_right_click(tx, mx, state):
    # Trigger right-click via thumb-middle pinch
    if tx is not None and mx is not None:
        distance = np.hypot(mx - tx, state['my'] - state['ty'])
        if distance < state['right_thresh'] and not state['right_active']:
            pyautogui.rightClick()
            state['right_active'] = True
        if distance > state['right_thresh']:
            state['right_active'] = False

def detect_middle_click(tx, rx, state):
    # Trigger middle-click via thumb-ring pinch
    if tx is not None and rx is not None:
        distance = np.hypot(rx - tx, state['ry'] - state['ty'])
        if distance < state['middle_thresh'] and not state['middle_active']:
            pyautogui.middleClick()
            state['middle_active'] = True
        if distance > state['middle_thresh']:
            state['middle_active'] = False

def detect_scroll(ix, mx, state):
    # Scroll up/down via index-middle pinch + vertical movement
    if ix is not None and mx is not None:
        distance = np.hypot(mx - ix, state['my'] - state['iy'])
        if distance < state['scroll_thresh']:
            if not state['scroll_active']:
                state['scroll_active'] = True
                state['base_y'] = (ix + mx) / 2
            else:
                current_y = (ix + mx) / 2
                delta = int((state['base_y'] - current_y) / state['scroll_divisor'])
                if abs(delta) > 0:
                    pyautogui.scroll(delta)
                    state['base_y'] = current_y
        else:
            state['scroll_active'] = False

def main():
    mp_hands = mp.solutions.hands
    mp_draw = mp.solutions.drawing_utils
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5
    )

    screen_width, screen_height = pyautogui.size()
    cap = cv2.VideoCapture(0)
    cam_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    cam_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

    prev_pos = (0, 0)
    smooth_factor = 5

    left_state = {
        'left_thresh': 40,
        'double_click_interval': 0.3,
        'drag_interval': 0.1,
        'pinch_active': False,
        'dragging': False,
        'last_click_time': 0,
        'pinch_start': 0,
        'iy': 0,
        'ty': 0
    }
    right_state = {
        'right_thresh': 40,
        'right_active': False,
        'ty': 0,
        'my': 0
    }
    middle_state = {
        'middle_thresh': 40,
        'middle_active': False,
        'ty': 0,
        'ry': 0
    }
    scroll_state = {
        'scroll_thresh': 40,
        'scroll_active': False,
        'base_y': 0,
        'scroll_divisor': 10,
        'iy': 0,
        'my': 0
    }

    while True:
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        ix = iy = tx = ty = mx = my = rx = ry = None
        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            landmark_list = [
                (int(lm.x * cam_width), int(lm.y * cam_height), idx)
                for idx, lm in enumerate(hand_landmarks.landmark)
            ]
            for x, y, idx in landmark_list:
                if idx == 8:
                    ix, iy = x, y
                if idx == 4:
                    tx, ty = x, y
                if idx == 12:
                    mx, my = x, y
                if idx == 16:
                    rx, ry = x, y

            left_state['iy'], left_state['ty'] = iy, ty
            right_state['ty'], right_state['my'] = ty, my
            middle_state['ty'], middle_state['ry'] = ty, ry
            scroll_state['iy'], scroll_state['my'] = iy, my

            prev_pos = move_cursor(
                ix, iy, cam_width, cam_height,
                screen_width, screen_height,
                prev_pos, smooth_factor
            )

            detect_left_double_drag(ix, tx, left_state)
            detect_right_click(tx, mx, right_state)
            detect_middle_click(tx, rx, middle_state)
            detect_scroll(ix, mx, scroll_state)

            mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=3),
                mp_draw.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2)
            )

        cv2.imshow("Hand Mouse Complete", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
