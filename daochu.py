#from ultralytics import YOLO

# 加载 YOLO 模型
#model = YOLO("runs/detect/train2/weights/best.pt")

# 导出为 ONNX 格式
#model.export(format='onnx')

#print("Model successfully exported to ONNX format.")


import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

from ultralytics import YOLO

# 加载 YOLO 模型
model = YOLO("yolov8n.pt")

# 导出为 ONNX 格式
#model.export(format='onnx', opset=12)
model.export(format='onnx', opset=12, dynamic=False)


print("Model successfully exported to ONNX format.")
