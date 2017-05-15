from redis import StrictRedis

import skimage.io
import numpy as np

import pickle
import itertools

from lib.config import config


class VisualDebugger:

    def __init__(self):
        self.available_buckets = config["visual_debugger"]["available_buckets"]
        self.bucket_generator = itertools.cycle(self.available_buckets)

        self.redis_client = StrictRedis(**config["redis"])

        for bucket in self.available_buckets:
            self.redis_client.delete(f"{config['visual_debugger']['redis_key_prefix']}:{bucket}:SHAPE")
            self.redis_client.delete(f"{config['visual_debugger']['redis_key_prefix']}:{bucket}")

    def store_image_data(self, image_data, image_shape, bucket="debug"):
        self.redis_client.lpush(f"{config['visual_debugger']['redis_key_prefix']}:{bucket}:SHAPE", pickle.dumps(image_shape))
        self.redis_client.lpush(f"{config['visual_debugger']['redis_key_prefix']}:{bucket}", image_data.tobytes())

    def retrieve_image_data(self):
        bucket = next(self.bucket_generator)
        bucket_key = f"{config['visual_debugger']['redis_key_prefix']}:{bucket}"

        response = self.redis_client.rpop(bucket_key)

        if response is not None:
            bucket = bucket_key.split(":")[-1]

            image_shape = self.redis_client.rpop(f"{config['visual_debugger']['redis_key_prefix']}:{bucket}:SHAPE")
            image_shape = pickle.loads(image_shape)

            image_data = np.fromstring(response, dtype="uint8").reshape(image_shape)

            return bucket, image_data

        return None

    def save_image_data(self, bucket, image_data):
        if bucket in self.available_buckets:
            if image_data.dtype == "bool" or (image_data.dtype == "uint8" and 1 in np.unique(image_data)):
                image_data = image_data.astype("uint8") * 255

            skimage.io.imsave(f"{bucket}.png", image_data)

    def get_bucket_queue_length(self, bucket):
        return self.redis_client.llen(f"{config['visual_debugger']['redis_key_prefix']}:{bucket}")
