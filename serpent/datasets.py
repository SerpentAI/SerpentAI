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

        os.makedirs(f"datasets/current/training/{file_path.split(os.sep)[-1]}".replace("/", os.sep))
        os.makedirs(f"datasets/current/validation/{file_path.split(os.sep)[-1]}".replace("/", os.sep))
    
        for file_name in file_names:
            set_label = "training"
    
            if random.random() <= validation_set_probability:
                set_label = "validation"
    
            shutil.copyfile(
                f"{file_path}/{file_name}".replace("/", os.sep),
                f"datasets/current/{set_label}/{file_path.split(os.sep)[-1]}/{file_name}".replace("/", os.sep)
            )

    return seed


def generate_seed():
    return str(uuid.uuid4())


def clear_current_dataset():
    try:
        shutil.rmtree("datasets/current".replace("/", os.sep))
    except FileNotFoundError:
        pass

    os.mkdir("datasets/current".replace("/", os.sep))
