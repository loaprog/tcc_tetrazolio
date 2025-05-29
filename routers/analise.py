from fastapi import APIRouter, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
import torch
import torchvision.transforms as T
import numpy as np
from PIL import Image
from io import BytesIO
import cv2
from models.semente import SegmentationModel
import os

analise = APIRouter(prefix="/analise", tags=["analise"])

@analise.post("/create_analise/")
async def create_analise(image: UploadFile):
    model_path_semente = "./models_ia/semente/checkpoints/epoch=49-step=200.ckpt"
    model_path_embriao = "./models_ia/embriao/checkpoints/epoch=199-step=400.ckpt"

    if not os.path.exists(model_path_semente) or not os.path.exists(model_path_embriao):
        raise HTTPException(status_code=404, detail="Model not found")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model_semente = SegmentationModel.load_from_checkpoint(model_path_semente)
    model_embriao = SegmentationModel.load_from_checkpoint(model_path_embriao)
    model_semente.eval().to(device)
    model_embriao.eval().to(device)

    image_bytes = await image.read()
    pil_image = Image.open(BytesIO(image_bytes)).convert("RGB")

    transform = T.Compose([
        T.Resize((256, 256)),
        T.ToTensor(),
    ])
    input_tensor = transform(pil_image).unsqueeze(0).to(device)

    with torch.no_grad():
        output_semente = torch.sigmoid(model_semente(input_tensor))
        mask_semente = (output_semente.squeeze().cpu().numpy() > 0.5).astype(np.uint8)

        output_embriao = torch.sigmoid(model_embriao(input_tensor))
        mask_embriao = (output_embriao.squeeze().cpu().numpy() > 0.5).astype(np.uint8)

    # Detectar sementes como componentes conectados
    num_labels, labels = cv2.connectedComponents(mask_semente)

    result_image = np.zeros((256, 256, 3), dtype=np.uint8)
    result_image[mask_semente == 1] = [19, 69, 139]  # marrom semente
    result_image[mask_embriao == 1] = [255, 255, 255]  # branco embrião

    hsv = cv2.cvtColor(cv2.cvtColor(np.array(pil_image.resize((256, 256))), cv2.COLOR_RGB2BGR), cv2.COLOR_BGR2HSV)
    lower_red1, upper_red1 = np.array([0, 70, 50]), np.array([10, 255, 255])
    lower_red2, upper_red2 = np.array([170, 70, 50]), np.array([180, 255, 255])
    mask_red = cv2.bitwise_or(
        cv2.inRange(hsv, lower_red1, upper_red1),
        cv2.inRange(hsv, lower_red2, upper_red2)
    )

    print("\nPor unidade:\nsemente %vigor")
    for i in range(1, num_labels):  # Ignora o fundo (label 0)
        seed_mask = (labels == i).astype(np.uint8)
        embriao_mask = cv2.bitwise_and(seed_mask, mask_embriao)
        red_in_embriao = cv2.bitwise_and(mask_red, mask_red, mask=embriao_mask)

        area_total = np.sum(embriao_mask)
        area_red = np.sum(red_in_embriao > 0)
        vigor = (area_red / area_total) * 100 if area_total > 0 else None

        # Desenhar número da semente no centro
        moments = cv2.moments(seed_mask)
        if moments["m00"] > 0:
            cX = int(moments["m10"] / moments["m00"])
            cY = int(moments["m01"] / moments["m00"])
            cv2.putText(result_image, str(i), (cX, cY), cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (255, 255, 0), 1, cv2.LINE_AA)

        if vigor is not None:
            print(f"{i} {vigor:.1f}")
            result_image[red_in_embriao > 0] = [0, 0, 255]
        else:
            print(f"{i} -")

    _, buffer = cv2.imencode(".png", result_image)
    bytes_io = BytesIO(buffer.tobytes())
    return StreamingResponse(bytes_io, media_type="image/png") 