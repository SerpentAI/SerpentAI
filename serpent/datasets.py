import random
import uuid
import os
import shutil


def create_training_and_validation_sets(file_paths, validation_set_probability=0.1, seed=None):
    if seed is None:
        seed = generate_seed()

    random.seed(seed)
    
    if isinstance(file_paths, str):
        file_paths = [file_paths]

    clear_current_dataset()
        
    for file_path in file_paths:
        file_names = os.listdir(file_path)
        random.shuffle(file_names)

        os.makedirs(f"datasets/current/training/{file_path.split('/')[-1]}")
        os.makedirs(f"datasets/current/validation/{file_path.split('/')[-1]}")
    
        for file_name in file_names:
            set_label = "training"
    
            if random.random() <= validation_set_probability:
                set_label = "validation"
    
            shutil.copyfile(
                f"{file_path}/{file_name}",
                f"datasets/current/{set_label}/{file_path.split('/')[-1]}/{file_name}"
            )

    return seed


def generate_seed():
    return str(uuid.uuid4())


def clear_current_dataset():
    try:
        shutil.rmtree("datasets/current")
    except FileNotFoundError:
        pass

    os.mkdir("datasets/current")
