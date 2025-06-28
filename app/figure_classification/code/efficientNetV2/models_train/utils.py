import os
import sys
import json
import pickle
import random

import torch
from tqdm import tqdm

import matplotlib.pyplot as plt


def read_split_data(root: str, val_rate: float = 0.3):
    random.seed(0)  # Ensure reproducible random results
    assert os.path.exists(root), f"Dataset root: {root} does not exist."

    # Traverse folders (each folder represents a class)
    classes = [cla for cla in os.listdir(root) if os.path.isdir(os.path.join(root, cla))]
    classes.sort()  # Sort to ensure consistency across platforms

    # Generate class names and corresponding numeric indices
    class_indices = {k: v for v, k in enumerate(classes)}
    with open('class_indices.json', 'w') as f:
        json.dump({v: k for k, v in class_indices.items()}, f, indent=4)

    train_images_path = []  # Training image paths
    train_images_label = []  # Training image labels
    val_images_path = []  # Validation image paths
    val_images_label = []  # Validation image labels
    class_sample_count = []  # Number of samples per class

    supported_formats = [".jpg", ".JPG", ".png", ".PNG", ".JPEG", ".jpeg"]

    # Process each class folder
    for cla in classes:
        cla_path = os.path.join(root, cla)
        images = [os.path.join(cla_path, i) for i in os.listdir(cla_path)
                  if os.path.splitext(i)[-1] in supported_formats]
        images.sort()
        class_idx = class_indices[cla]
        class_sample_count.append(len(images))

        # Randomly sample validation images
        val_paths = random.sample(images, k=int(len(images) * val_rate))

        for img_path in images:
            if img_path in val_paths:
                val_images_path.append(img_path)
                val_images_label.append(class_idx)
            else:
                train_images_path.append(img_path)
                train_images_label.append(class_idx)

    total_samples = sum(class_sample_count)
    print(f"Found {total_samples} images in the dataset.")
    print(f"{len(train_images_path)} for training, {len(val_images_path)} for validation.")

    assert len(train_images_path) > 0, "Training images cannot be empty."
    assert len(val_images_path) > 0, "Validation images cannot be empty."

    # Visualize class distribution
    if True:  # Modify to plot_image=False to disable
        plt.bar(range(len(classes)), class_sample_count, align='center')
        plt.xticks(range(len(classes)), classes, rotation=45)
        for i, v in enumerate(class_sample_count):
            plt.text(i, v + 5, str(v), ha='center')
        plt.xlabel('Class')
        plt.ylabel('Sample Count')
        plt.title('Class Distribution')
        plt.tight_layout()
        plt.show()

    return train_images_path, train_images_label, val_images_path, val_images_label


def plot_data_loader_image(data_loader):
    batch_size = data_loader.batch_size
    plot_count = min(batch_size, 4)

    assert os.path.exists('./class_indices.json'), "Class indices file not found."
    with open('./class_indices.json', 'r') as f:
        class_indices = json.load(f)

    for data in data_loader:
        images, labels = data
        for i in range(plot_count):
            # Convert [C, H, W] to [H, W, C]
            img = images[i].numpy().transpose(1, 2, 0)
            # Reverse normalization
            img = (img * [0.229, 0.224, 0.225] + [0.485, 0.456, 0.406]) * 255
            label = labels[i].item()

            plt.subplot(1, plot_count, i + 1)
            plt.xlabel(class_indices[str(label)])
            plt.xticks([])
            plt.yticks([])
            plt.imshow(img.astype('uint8'))

        plt.tight_layout()
        plt.show()


def write_pickle(list_info: list, file_name: str):
    with open(file_name, 'wb') as f:
        pickle.dump(list_info, f)


def read_pickle(file_name: str) -> list:
    with open(file_name, 'rb') as f:
        return pickle.load(f)


def train_one_epoch(model, optimizer, data_loader, device, epoch):
    model.train()
    loss_fn = torch.nn.CrossEntropyLoss()
    accu_loss = torch.zeros(1, device=device)  # Cumulative loss
    accu_correct = torch.zeros(1, device=device)  # Cumulative correct predictions
    optimizer.zero_grad()

    sample_count = 0
    data_loader = tqdm(data_loader, file=sys.stdout)

    for step, (images, labels) in enumerate(data_loader):
        sample_count += images.shape[0]
        images, labels = images.to(device), labels.to(device)

        pred = model(images)
        pred_classes = torch.max(pred, dim=1)[1]
        accu_correct += torch.eq(pred_classes, labels).sum()

        loss = loss_fn(pred, labels)
        loss.backward()
        accu_loss += loss.detach()

        # Update progress bar
        data_loader.set_description(
            f"[Train Epoch {epoch}] Loss: {accu_loss.item() / (step + 1):.3f}, "
            f"Acc: {accu_correct.item() / sample_count:.3f}"
        )

        if not torch.isfinite(loss):
            print(f'WARNING: Non-finite loss: {loss}, terminating training')
            sys.exit(1)

        optimizer.step()
        optimizer.zero_grad()

    return accu_loss.item() / (step + 1), accu_correct.item() / sample_count


@torch.no_grad()
def evaluate(model, data_loader, device, epoch):
    loss_fn = torch.nn.CrossEntropyLoss()
    model.eval()

    accu_correct = torch.zeros(1, device=device)  # Cumulative correct predictions
    accu_loss = torch.zeros(1, device=device)  # Cumulative loss
    sample_count = 0

    data_loader = tqdm(data_loader, file=sys.stdout)

    for step, (images, labels) in enumerate(data_loader):
        sample_count += images.shape[0]
        images, labels = images.to(device), labels.to(device)

        pred = model(images)
        pred_classes = torch.max(pred, dim=1)[1]
        accu_correct += torch.eq(pred_classes, labels).sum()

        loss = loss_fn(pred, labels)
        accu_loss += loss

        # Update progress bar
        data_loader.set_description(
            f"[Valid Epoch {epoch}] Loss: {accu_loss.item() / (step + 1):.3f}, "
            f"Acc: {accu_correct.item() / sample_count:.3f}"
        )

    return accu_loss.item() / (step + 1), accu_correct.item() / sample_count