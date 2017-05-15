

def extract_region_from_image(image, region_bounding_box):
    return image[region_bounding_box[0]:region_bounding_box[2], region_bounding_box[1]:region_bounding_box[3]]
