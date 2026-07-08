"""Dataset loading and preprocessing for the fabric defect dataset.

Handles two possible layouts transparently:
  1. Pre-split:  data_dir/{train,val,test}/<class_name>/*.jpg
  2. Flat:       data_dir/<class_name>/*.jpg   (split randomly into train/val/test)
"""

import os

import torch
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

SPLIT_ALIASES = {
    "train": ["train", "training"],
    "val": ["val", "valid", "validation"],
    "test": ["test", "testing"],
}


def _find_split_dirs(data_dir: str) -> dict:
    """Return {"train": path, "val": path, "test": path} if data_dir is pre-split, else {}."""
    entries = {e.lower(): e for e in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, e))}
    found = {}
    for split, aliases in SPLIT_ALIASES.items():
        for alias in aliases:
            if alias in entries:
                found[split] = os.path.join(data_dir, entries[alias])
                break
    if "train" in found:
        return found
    return {}


def build_transforms(img_size: int = 224):
    train_tf = transforms.Compose([
        transforms.Resize((img_size, img_size)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomVerticalFlip(),
        transforms.RandomRotation(15),
        transforms.ColorJitter(brightness=0.15, contrast=0.15),
        transforms.ToTensor(),
        transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
    ])
    eval_tf = transforms.Compose([
        transforms.Resize((img_size, img_size)),
        transforms.ToTensor(),
        transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
    ])
    return train_tf, eval_tf


def get_datasets(data_dir: str, img_size: int = 224, val_frac: float = 0.15,
                  test_frac: float = 0.15, seed: int = 42):
    """Return (train_ds, val_ds, test_ds, class_names)."""
    train_tf, eval_tf = build_transforms(img_size)
    split_dirs = _find_split_dirs(data_dir)

    if split_dirs:
        train_ds = datasets.ImageFolder(split_dirs["train"], transform=train_tf)
        class_names = train_ds.classes
        val_ds = (datasets.ImageFolder(split_dirs["val"], transform=eval_tf)
                  if "val" in split_dirs else None)
        test_ds = (datasets.ImageFolder(split_dirs["test"], transform=eval_tf)
                   if "test" in split_dirs else None)

        # Data is pre-split into train/test only -> carve a val set out of train.
        if val_ds is None:
            n_val = int(len(train_ds) * val_frac)
            n_train = len(train_ds) - n_val
            generator = torch.Generator().manual_seed(seed)
            train_ds, val_ds = random_split(train_ds, [n_train, n_val], generator=generator)
            val_ds.dataset.transform = eval_tf  # underlying dataset shared with train_ds

        if test_ds is None:
            n_test = int(len(train_ds) * test_frac)
            n_train = len(train_ds) - n_test
            generator = torch.Generator().manual_seed(seed)
            train_ds, test_ds = random_split(train_ds, [n_train, n_test], generator=generator)

        return train_ds, val_ds, test_ds, class_names

    # Flat layout: one ImageFolder, split randomly.
    full_ds = datasets.ImageFolder(data_dir, transform=train_tf)
    class_names = full_ds.classes

    n_total = len(full_ds)
    n_val = int(n_total * val_frac)
    n_test = int(n_total * test_frac)
    n_train = n_total - n_val - n_test

    generator = torch.Generator().manual_seed(seed)
    train_ds, val_ds, test_ds = random_split(full_ds, [n_train, n_val, n_test], generator=generator)

    # val/test subsets must use eval transforms, not the train-time augmentations.
    eval_full_ds = datasets.ImageFolder(data_dir, transform=eval_tf)
    val_ds.dataset = eval_full_ds
    test_ds.dataset = eval_full_ds

    return train_ds, val_ds, test_ds, class_names


def get_dataloaders(data_dir: str, batch_size: int = 32, img_size: int = 224,
                     val_frac: float = 0.15, test_frac: float = 0.15,
                     seed: int = 42, num_workers: int = 2):
    """Return (train_loader, val_loader, test_loader, class_names)."""
    train_ds, val_ds, test_ds, class_names = get_datasets(
        data_dir, img_size=img_size, val_frac=val_frac, test_frac=test_frac, seed=seed
    )

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True,
                               num_workers=num_workers, pin_memory=torch.cuda.is_available())
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False,
                             num_workers=num_workers, pin_memory=torch.cuda.is_available())
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False,
                              num_workers=num_workers, pin_memory=torch.cuda.is_available())

    return train_loader, val_loader, test_loader, class_names
