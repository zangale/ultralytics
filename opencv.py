import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

# 加载 YOLO ONNX 模型
onnx_model_path = "runs/detect/train2/weights/best.onnx"
net = cv2.dnn.readNetFromONNX(onnx_model_path)

# 类别信息
names = ['Missing']

# 创建主窗口
root = tk.Tk()
root.title("YOLO 车牌检测")

# 置信度阈值变量
conf_threshold_var = tk.StringVar()
conf_threshold_var.set("0.8")

# 用于存储原始图像和标签
original_image = None
image_label = None


def select_image():
    global original_image, image_label
    """ 选择图片并进行车牌检测 """
    image_path = filedialog.askopenfilename(title="选择要测试的图片", filetypes=[("图像文件", "*.jpg;*.jpeg;*.png")])
    if not image_path:
        return

    try:
        conf_threshold = float(conf_threshold_var.get())
    except ValueError:
        conf_threshold = 0.8  # 默认值

    # 读取图片
    img = cv2.imread(image_path)

    # 预处理图片
    input_shape = (640, 640)
    blob = cv2.dnn.blobFromImage(img, 1 / 255.0, input_shape, swapRB=True, crop=False)
    net.setInput(blob)

    # 模型推理
    output = net.forward()
    output = output.transpose((0, 2, 1))

    # 获取图片尺寸
    height, width, _ = img.shape
    x_factor = width / input_shape[0]
    y_factor = height / input_shape[1]

    nms_threshold = 0.45
    class_ids, confidences, boxes = [], [], []

    # 解析 YOLO 输出
    for i in range(output[0].shape[0]):
        box = output[0][i]
        scores = box[4:]
        class_id = np.argmax(scores)
        confidence = scores[class_id]

        if confidence > conf_threshold:
            center_x, center_y = int(box[0] * x_factor), int(box[1] * y_factor)
            w, h = int(box[2] * x_factor), int(box[3] * y_factor)
            x, y = int(center_x - w / 2), int(center_y - h / 2)

            boxes.append([x, y, w, h])
            confidences.append(float(confidence))
            class_ids.append(class_id)

    # 非极大值抑制
    indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)

    # 绘制检测结果
    for i in indices:
        i = i.item()
        x, y, w, h = boxes[i]
        label = f'{names[class_ids[i]]}: {confidences[i]:.2f}'
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(img, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # 将 OpenCV 图像转换为 PIL 格式
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    original_image = Image.fromarray(img)

    # 显示图像
    if image_label:
        image_label.destroy()
    resized_image = resize_image(original_image)
    photo = ImageTk.PhotoImage(resized_image)
    image_label = tk.Label(root, image=photo)
    image_label.image = photo
    image_label.pack()


def resize_image(image):
    """ 根据窗口大小调整图像大小 """
    window_width = root.winfo_width()
    window_height = root.winfo_height() - 50  # 减去一些空间用于按钮和输入框

    original_width, original_height = image.size
    ratio = min(window_width / original_width, window_height / original_height)
    new_width = int(original_width * ratio)
    new_height = int(original_height * ratio)
    return image.resize((new_width, new_height), Image.Resampling.LANCZOS)


def on_window_resize(event):
    global original_image, image_label
    if original_image and image_label:
        resized_image = resize_image(original_image)
        photo = ImageTk.PhotoImage(resized_image)
        image_label.config(image=photo)
        image_label.image = photo


# 创建 UI 组件
select_button = tk.Button(root, text="选择图片", command=select_image)
select_button.pack(pady=10)

conf_label = tk.Label(root, text="置信度阈值:")
conf_label.pack()
conf_entry = tk.Entry(root, textvariable=conf_threshold_var)
conf_entry.pack()

# 绑定窗口大小改变事件
root.bind("<Configure>", on_window_resize)

# 运行 Tkinter 主循环
root.mainloop()
