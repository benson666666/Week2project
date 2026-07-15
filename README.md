# AI powered super smart medicine detector 🤑💀
A AI medicine detector, good for old people. This system developed on NVIDIA jetson orin, using the jetson-inference deep learning framework. This project is using high precision image classification net to help visually impaired person, like elder😱😱🥶☠️

key feature: 👽👺

1, High precision image classification: this system identify target medication like fish oil with confidence about 99%-100% 😎🤠

2, 1.5second automatic accessible detect: This system is Specially designed for visually impaired users. The system runs in a continuous loop, automatically capturing and processing camera frames every 1.5 seconds without manual control. 🥳😡🤬

3, Real Safety Guide: Upon successful detection, the system immediately outputs clear directions, safety warnings, and usage guidelines in the terminal to prevent accidental misuse. 😤😰

Project Structure 🥸💥


Week2project/
├── models/

│   └── medicine/

│       ├── resnet18.onnx   # Fine-tuned ResNet-18 classification model in ONNX format 👻

│       └── labels.txt       # Classification labels for target medications 🤩

├── .gitignore               # Use to excludes compilation cache and temporary system files 🤠

├── README.md                # Project documentation this file you are looking 💀

└── smart_medicine.py        # Main Python application script for running the AI powered super smart medicine detector 😍☠️

<img width="183" height="195" alt="image" src="https://github.com/user-attachments/assets/dfd6dbfc-f5a1-4e75-ac78-a29d1ada8c13" />



Make sure your jetson-inference environment is fully configured, then you can launch the AI powered super smart medicine detector program by using the following command: 👺


python3 smart_medicine.py         （will show some system message)


Hardware: NVIDIA Jetson Developer Kit, USB Webcam 👽

Software: Jetson-Inference, PyTorch for model training 🥶

Model: ResNet-18 (ONNX) 💀🤖
