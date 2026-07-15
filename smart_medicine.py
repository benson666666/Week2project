import os
import sys

# 【核心修复】：强行掐死 GStreamer 的嘴碎系统日志，还终端绝对清净
os.environ["GST_DEBUG"] = "0"
os.environ["DISPLAY"] = "" # 禁用 X11 窗口

import jetson_inference
import jetson_utils
import argparse
import time
import select

# 1. Full English Usage Guidelines
MEDICINE_TIPS = {
    "Alaxan": "【Usage】Take 1 tablet every 4-6 hours after meals. Used for pain relief and reducing fever. Do not exceed 4 tablets in 24 hours.",
    "Bactidol": "【Usage】For sore throat. Gargle 15 ml for 30 seconds and spit out. Use 2-3 times a day. DO NOT swallow.",
    "Bioflu": "【Usage】Take 1 tablet every 6 hours. Used for cold, runny nose, and fever. Note: May cause drowsiness.",
    "Biogesic": "【Usage】Take 1-2 tablets every 4-6 hours for headache and fever. Safe on empty stomach. Do not exceed 8 tablets in 24 hours.",
    "DayZinc": "【Usage】Take 1 capsule daily, preferably with a meal. Used as a Vitamin C + Zinc supplement to boost immunity.",
    "Decolgen": "【Usage】Take 1 tablet every 6-8 hours. Relief for clogged nose, headache, and fever from common colds. Max 4 tablets in 24 hours.",
    "Fish Oil": "【Usage】Take 1-2 softgels daily with meals. Rich in Omega-3 to support cardiovascular, brain, and joint health.",
    "Kremil S": "【Usage】Take 1-2 tablets 1 hour after meals or at bedtime for hyperacidity, stomach ache, or indigestion. Can be chewed.",
    "Medicol": "【Usage】Take 1 tablet every 4-6 hours strictly with or after meals. Used for fast relief of severe headache, toothache, or period pain.",
    "Neozep": "【Usage】Take 1 tablet every 6 hours for relief of clogged nose, runny nose, and sneezing. Drink plenty of warm water."
}

# 2. Setup Arguments
parser = argparse.ArgumentParser()
parser.add_argument("--model", type=str, default="models/medicine/resnet18.onnx")
parser.add_argument("--labels", type=str, default="models/medicine/labels.txt")
args = parser.parse_known_args()[0]

# 3. Load Model and Streams
net = jetson_inference.imageNet(model=args.model, labels=args.labels, input_blob="input_0", output_blob="output_0")
camera = jetson_utils.videoSource("/dev/video0")
display = jetson_utils.videoOutput("webrtc://@:8554/mystream", argv=["--headless"])
font = jetson_utils.cudaFont(size=32)

print("\n=======================================================")
print("ELDERLY/BLIND PEOPLE FRIENDLY MEDICINE DETECTOR ACTIVED")
print("http://192.168.137.181:8554")
print("1, AUTOMATIC MODE: Make sure your medicine is in the screen and hold steady for 1.5 seconds.")
print("2, MANUAL: Press ENTER in this terminal to detect anytime.")
print("=======================================================\n")

# State tracking variables for stability filter
current_focus_medicine = None
focus_start_time = 0
last_printed_medicine = None

# A function to check if Enter was pressed without blocking the whole program
def check_keyboard_input():
    rlist, _, _ = select.select([sys.stdin], [], [], 0.001)
    if rlist:
        sys.stdin.readline() # Clear the buffer
        return True
    return False

# A helper function to print the nice output
def trigger_detection_report(mode_label, name, conf):
    print(f"\n[{mode_label} SNAPSHOT DEPLOYED] ({conf*100:.2f}%)")
    print(f"RESULT: MATCHED {name}")
    if name in MEDICINE_TIPS:
        print(f"Guidelines: {MEDICINE_TIPS[name]}")
    else:
        print("Guidelines: No specific instructions found for this medicine.")
    print("-" * 60 + "\n")

# 4. Main Loop
while True:
    img = camera.Capture()
    if img is None:
        continue

    # Classify the frame in real time
    class_id, confidence = net.Classify(img)
    class_desc = net.GetClassDesc(class_id)
    
    now = time.time()

    # 手动敲回车触发（随时可以强行检测第二遍，无视任何限制）
    if check_keyboard_input():
        trigger_detection_report("MANUAL ENTER KEY", class_desc, confidence)
        font.OverlayText(img, img.width, img.height, f"MANUAL SHOT: {class_desc}", 10, 30, (0, 255, 0, 255), (0, 0, 0, 150))
        # 手动拍照后，重置自动计时器，防止瞬间又触发自动识别
        last_printed_medicine = class_desc
        current_focus_medicine = None

    # 1.5秒自动稳健触发模式（卡在 > 95% 置信度）
    elif confidence >= 0.95 and class_desc in MEDICINE_TIPS:
        # 如果是新放到镜头前的药，或者重新拿起来的药
        if class_desc != current_focus_medicine:
            current_focus_medicine = class_desc
            focus_start_time = now
        
        # 如果稳定在镜头前停留满了 1.5 秒
        elif now - focus_start_time >= 1.5:
            # 如果这个药不是刚才自动触发过的，或者中间拿开过，就自动打一张
            if class_desc != last_printed_medicine:
                trigger_detection_report("1.5S AUTOMATIC", class_desc, confidence)
                last_printed_medicine = class_desc
            
        font.OverlayText(img, img.width, img.height, f"LOCKING: {class_desc} ({confidence*100:.1f}%)", 10, 30, (255, 255, 0, 255), (0, 0, 0, 150))
    
    else:
        # 当镜头移开或者置信度变低（说明老年人把药拿走了）
        # 只要拿开超过 1.0 秒，就彻底清除记忆，允许他们立刻拿回来检测第二遍！
        if current_focus_medicine is not None and (now - focus_start_time > 1.0):
            current_focus_medicine = None
            last_printed_medicine = None

    # video go to website
    display.Render(img)

    if not display.IsStreaming():
        break