import skimage.color
import skimage.segmentation
import skimage.filters
import skimage.morphology
import skimage.util
import skimage.transform
import skimage.measure
import skimage.io

import tesserocr
import editdistance

from PIL import Image


def locate_string(query_string, image, fuzziness=0, ocr_preset=None, offset_x=0, offset_y=0):
    images, text_regions = extract_ocr_candidates(
        image,
        gradient_size=ocr_preset["extract"]["gradient_size"],
        closing_size=ocr_preset["extract"]["closing_size"]
    )

    detected_strings = list()

    for image in images:
        detected_strings.append(
            perform_ocr(
                image,
                scale=ocr_preset["perform"]["scale"],
                order=ocr_preset["perform"]["order"],
                horizontal_closing=ocr_preset["perform"]["horizontal_closing"],
                vertical_closing=ocr_preset["perform"]["vertical_closing"]
            )
        )

    if query_string in detected_strings:
        text_region = list(text_regions[detected_strings.index(query_string)])

        text_region[0] += offset_y
        text_region[1] += offset_x
        text_region[2] += offset_y
        text_region[3] += offset_x

        return text_region

    edit_distances = [editdistance.eval(query_string, string) for string in detected_strings]
    minimum_edit_distance = min(edit_distances)

    if minimum_edit_distance <= fuzziness:
        text_region = list(text_regions[edit_distances.index(minimum_edit_distance)])

        text_region[0] += offset_y
        text_region[1] += offset_x
        text_region[2] += offset_y
        text_region[3] += offset_x

        return text_region

    return None


def extract_ocr_candidates(image, gradient_size=3, closing_size=10, minimum_area=100, minimum_aspect_ratio=2):
    gray_image = skimage.color.rgb2gray(image)
    gradient_image = skimage.filters.rank.gradient(gray_image, skimage.morphology.disk(gradient_size))
    bw_image = gradient_image > skimage.filters.threshold_otsu(gradient_image)
    bw_image = skimage.morphology.closing(bw_image, skimage.morphology.rectangle(1, closing_size))
    label_image = skimage.measure.label(bw_image)

    regions = skimage.measure.regionprops(label_image)

    text_regions = list()

    for region in regions:
        if region.area > minimum_area:
            y0, x0, y1, x1 = region.bbox
            region_image = bw_image[y0:y1, x0:x1]

            aspect_ratio = region_image.shape[1] / region_image.shape[0]

            black_pixel_count = region_image[region_image == 0].size
            white_pixel_count = region_image[region_image == 1].size

            if aspect_ratio >= minimum_aspect_ratio and white_pixel_count > black_pixel_count and y1 - y0 >= 8:
                text_regions.append(region.bbox)

    ocr_candidates = list()

    for text_region in text_regions:
        ocr_candidates.append(gray_image[text_region[0]:text_region[2], text_region[1]:text_region[3]])

    return ocr_candidates, text_regions


def perform_ocr(image, scale=10, order=5, horizontal_closing=10, vertical_closing=5):
    image = skimage.transform.resize(
        image,
        (image.shape[0] * scale, image.shape[1] * scale),
        mode="edge",
        order=order
    )

    image = image > skimage.filters.threshold_otsu(image)

    black_pixel_count = image[image == 0].size
    white_pixel_count = image[image == 1].size

    if black_pixel_count > white_pixel_count:
        image = skimage.util.invert(image)

    image = skimage.morphology.closing(image, skimage.morphology.rectangle(1, horizontal_closing))
    image = skimage.morphology.closing(image, skimage.morphology.rectangle(vertical_closing, 1))

    image = skimage.util.img_as_ubyte(image)

    return tesserocr.image_to_text(
        Image.fromarray(image),
        psm=tesserocr.PSM.SINGLE_LINE,
        oem=tesserocr.OEM.TESSERACT_ONLY
    ).strip()
