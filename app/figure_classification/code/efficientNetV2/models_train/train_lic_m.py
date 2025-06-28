import os
import random
import copy
import math
import argparse

import torch
import torch.optim as optim
from torch.utils.tensorboard import SummaryWriter
from torchvision import transforms
import torch.optim.lr_scheduler as lr_scheduler

from model import efficientnetv2_m as create_model
from my_dataset import MyDataSet
from utils import read_split_data, train_one_epoch, evaluate


def main(args):
    device = torch.device(args.device if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")
    print(args)
    print('Start Tensorboard with "tensorboard --logdir=runs"')

    tb_writer = SummaryWriter()
    os.makedirs("weights", exist_ok=True)

    # Split dataset into training and validation sets
    train_images_path, train_images_label, val_images_path, val_images_label = read_split_data(args.data_path)

    # Class balancing - undersampling
    class_counts = {}
    for label in train_images_label:
        class_counts[label] = class_counts.get(label, 0) + 1

    min_count = min(class_counts.values())
    print(f"Minimum class samples: {min_count}")

    # Undersampled training data
    undersampled_train_images_path = []
    undersampled_train_images_label = []

    for path, label in zip(train_images_path, train_images_label):
        if class_counts[label] > min_count and random.random() >= (min_count / class_counts[label]):
            continue  # Skip to balance classes
        undersampled_train_images_path.append(path)
        undersampled_train_images_label.append(label)

    # Model configuration
    img_size = {"s": [300, 384], "m": [384, 480], "l": [384, 480]}
    model_type = "m"

    # Data transformations
    data_transform = {
        "train": transforms.Compose([
            transforms.Resize(img_size[model_type][0]),
            transforms.CenterCrop(img_size[model_type][0]),
            transforms.RandomHorizontalFlip(p=0.3),
            transforms.RandomVerticalFlip(p=0.3),
            transforms.ToTensor(),
            transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
        ]),
        "val": transforms.Compose([
            transforms.Resize(img_size[model_type][1]),
            transforms.CenterCrop(img_size[model_type][1]),
            transforms.ToTensor(),
            transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
        ])
    }

    # Create datasets
    train_dataset = MyDataSet(
        images_path=undersampled_train_images_path,
        images_class=undersampled_train_images_label,
        transform=data_transform["train"]
    )

    val_dataset = MyDataSet(
        images_path=val_images_path,
        images_class=val_images_label,
        transform=data_transform["val"]
    )

    # Create data loaders
    batch_size = args.batch_size
    num_workers = min([os.cpu_count(), batch_size if batch_size > 1 else 0, 8])
    print(f'Using {num_workers} dataloader workers per process')

    train_loader = torch.utils.data.DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        pin_memory=True,
        num_workers=num_workers,
        collate_fn=train_dataset.collate_fn
    )

    val_loader = torch.utils.data.DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        pin_memory=True,
        num_workers=num_workers,
        collate_fn=val_dataset.collate_fn
    )

    # Initialize model and load pretrained weights
    model = create_model(num_classes=args.num_classes).to(device)

    if args.weights and os.path.exists(args.weights):
        weights_dict = torch.load(args.weights, map_location=device)
        load_weights_dict = {k: v for k, v in weights_dict.items()
                             if model.state_dict()[k].numel() == v.numel()}
        print(model.load_state_dict(load_weights_dict, strict=False))
    elif args.weights:
        raise FileNotFoundError(f"Pretrained weights not found: {args.weights}")

    # Freeze layers if specified
    if args.freeze_layers:
        for name, param in model.named_parameters():
            if "head" not in name:
                param.requires_grad = False
            else:
                print(f"Training layer: {name}")

    # Optimizer and learning rate scheduler
    trainable_params = [p for p in model.parameters() if p.requires_grad]
    optimizer = optim.SGD(trainable_params, lr=args.lr, momentum=0.9, weight_decay=1E-4)

    # Cosine annealing learning rate schedule
    lr_lambda = lambda x: ((1 + math.cos(x * math.pi / args.epochs)) / 2) * (1 - args.lrf) + args.lrf
    scheduler = lr_scheduler.LambdaLR(optimizer, lr_lambda=lr_lambda)

    # Training loop
    best_acc = 0.0
    for epoch in range(args.epochs):
        # Train for one epoch
        train_loss, train_acc = train_one_epoch(
            model=model,
            optimizer=optimizer,
            data_loader=train_loader,
            device=device,
            epoch=epoch
        )

        scheduler.step()

        # Validate
        val_loss, val_acc = evaluate(
            model=model,
            data_loader=val_loader,
            device=device,
            epoch=epoch
        )

        # Log metrics
        tb_writer.add_scalar("train_loss", train_loss, epoch)
        tb_writer.add_scalar("train_acc", train_acc, epoch)
        tb_writer.add_scalar("val_loss", val_loss, epoch)
        tb_writer.add_scalar("val_acc", val_acc, epoch)
        tb_writer.add_scalar("learning_rate", optimizer.param_groups[0]["lr"], epoch)

        # Save model checkpoint
        torch.save(model.state_dict(), f"./weights/model-{epoch}.pth")
        # if val_acc > best_acc:
        #     torch.save(model.state_dict(), "./weights/best_model.pth")
        #     best_acc = val_acc


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='EfficientNetV2 Training')
    parser.add_argument('--num_classes', type=int, default=2, help='Number of classes')
    parser.add_argument('--epochs', type=int, default=100, help='Training epochs')
    parser.add_argument('--batch-size', type=int, default=32, help='Batch size')
    parser.add_argument('--lr', type=float, default=0.01, help='Initial learning rate')
    parser.add_argument('--lrf', type=float, default=0.01, help='Final learning rate factor')
    parser.add_argument('--data-path', type=str,
                        default=r"",
                        help='Path to dataset')
    parser.add_argument('--weights', type=str,
                        default=r'',
                        help='Path to pretrained weights')
    parser.add_argument('--freeze-layers', type=bool, default=False, help='Freeze non-head layers')
    parser.add_argument('--device', default='cuda:0', help='Device ID (e.g., 0 or 0,1 or cpu)')

    opt = parser.parse_args()
    main(opt)