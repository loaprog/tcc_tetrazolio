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
    if not os.path.exists(model_path_semente):
        raise HTTPException(status_code=404, detail="Model not found")

    

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model_semente = SegmentationModel.load_from_checkpoint(model_path_semente)
    model_semente.eval().to(device)

    image_bytes = await image.read()
    pil_image = Image.open(BytesIO(image_bytes)).convert("RGB")

    transform = T.Compose([
        T.Resize((256, 256)),
        T.ToTensor(),
    ])
    input_tensor = transform(pil_image).unsqueeze(0).to(device)

    with torch.no_grad():
        output_semente = model_semente(input_tensor)
        output_semente = torch.sigmoid(output_semente)
        output_np_semente = (output_semente.squeeze().cpu().numpy() > 0.5).astype(np.uint8) * 255

    _, buffer = cv2.imencode(".png", output_np_semente)
    bytes_io = BytesIO(buffer.tobytes())

    return StreamingResponse(bytes_io, media_type="image/png")
