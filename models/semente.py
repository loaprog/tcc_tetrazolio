import torch
import torch.nn as nn
import segmentation_models_pytorch as smp
import pytorch_lightning as pl
import torch.nn as nn
from torchvision import models
import pytorch_lightning as pl

class SegmentationModel(pl.LightningModule):
    def __init__(self):
        super().__init__()
        self.model = smp.Unet(encoder_name='resnet34', in_channels=3, classes=1)
        self.loss_fn = smp.losses.DiceLoss('binary')

    def forward(self, x):
        return self.model(x)

    def compute_metrics(self, preds, masks):
        preds_bin = (preds > 0.5).float()
        intersection = (preds_bin * masks).sum()
        union = ((preds_bin + masks) >= 1).float().sum()
        iou = intersection / (union + 1e-6)

        correct = (preds_bin == masks).float().sum()
        total = torch.numel(masks)
        accuracy = correct / total

        return iou, accuracy

    def training_step(self, batch, batch_idx):
        images, masks = batch
        preds = self(images)
        loss = self.loss_fn(preds, masks)

        iou, accuracy = self.compute_metrics(preds, masks)

        # Logging
        self.log("train_loss", loss, on_step=True, prog_bar=True)
        self.log("train_iou", iou, on_step=True, prog_bar=True)
        self.log("train_acc", accuracy, on_step=True, prog_bar=False)

        return loss

    def configure_optimizers(self):
        optimizer = torch.optim.Adam(self.parameters(), lr=1e-4)
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, mode='min', factor=0.5, patience=3
        )
        return {
            'optimizer': optimizer,
            'lr_scheduler': scheduler,
            'monitor': 'train_loss'
        }




class SeedClassifier(pl.LightningModule):
    def __init__(self):
        super().__init__()
        self.model = models.resnet34(pretrained=False)
        self.model.fc = nn.Linear(self.model.fc.in_features, 3)  # ou 3 se tiver classe "incerta"

    def forward(self, x):
        return self.model(x)
