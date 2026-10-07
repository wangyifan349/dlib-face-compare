"""
Minimal dlib face comparison demo (no detector, no threshold, fixed models).
Each image is assumed to contain exactly one face, so the whole image is used as the
face box: no HOG/CNN detector and no detector weights are needed. The 5-point landmark
model (both eyes, the tip of the nose and the mouth corners) straightens the face to
150x150, and the ResNet converts it into a 128-dimensional feature vector.
The mode is chosen from the two arguments (no subcommands, no options):
    two image files                  -> compare the two images
    one image file + one directory   -> 1:N search, recursive, sorted by similarity
Search walks the whole directory tree, computes feature vectors for every image using
all CPU cores in parallel, and sorts them by Euclidean distance ascending, so the most
similar image (smallest distance) comes first.
Usage:
    python face_compare.py a.jpg b.jpg        compare two images
    python face_compare.py a.jpg ./photos     1:N search inside a folder (recursive)
    python face_compare.py ./photos a.jpg     same, the order does not matter
"""


import os
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

import dlib

script_directory = os.path.dirname(os.path.abspath(__file__))
model_directory = os.path.join(script_directory, "models")

# Fixed models, no command line override
recognition_model_path = os.path.join(model_directory, "dlib_face_recognition_resnet_model_v1.dat")
landmark_model_path = os.path.join(model_directory, "shape_predictor_5_face_landmarks.dat")

chip_size = 150  # aligned face size, the fixed input size of the ResNet
threads_count = os.cpu_count() or 1  # one worker thread per CPU core
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp", ".webp")

command_arguments = sys.argv[1:]

if len(command_arguments) != 2:
    print("usage:\n"
          "    python face_compare.py a.jpg b.jpg\n"
          "    python face_compare.py a.jpg <image_dir>\n"
          "    python face_compare.py <image_dir> a.jpg")
    sys.exit(0)

first_argument = command_arguments[0]
second_argument = command_arguments[1]

# dlib models are not thread-safe, so each worker thread keeps its own copy
thread_local_storage = threading.local()


def get_models():
    """Landmark predictor and recognition model for the current thread, loaded once."""
    models = getattr(thread_local_storage, "models", None)
    if models is None:
        models = (
            dlib.shape_predictor(landmark_model_path),
            dlib.face_recognition_model_v1(recognition_model_path),
        )
        thread_local_storage.models = models
    return models


def get_vector(image_path):
    """128-dimensional embedding of the image, or None if it cannot be read.

    The whole image is used as the face box (one face per image), so the landmarks
    come from the image rectangle and the face chip is aligned to chip_size square.
    """
    try:
        image = dlib.load_rgb_image(image_path)
    except Exception:
        return None

    landmark_predictor, recognition_model = get_models()
    image_height, image_width = image.shape[0], image.shape[1]
    face_rectangle = dlib.rectangle(0, 0, image_width, image_height)
    landmarks = landmark_predictor(image, face_rectangle)  # eyes, nose tip, mouth corners
    face_chip = dlib.get_face_chip(image, landmarks, chip_size, chip_size)  # align and crop
    return recognition_model.compute_face_descriptor(face_chip)


def get_distance(vector_a, vector_b):
    """Euclidean distance between two embeddings, the smaller the more similar."""
    squared_sum = 0.0
    for value_a, value_b in zip(vector_a, vector_b):
        squared_sum += (value_a - value_b) ** 2
    return squared_sum ** 0.5


def collect_images(root_directory):
    """Every image under root_directory, recursively. A single file is returned as is."""
    if os.path.isfile(root_directory):
        return [root_directory]
    image_paths = []
    for directory_path, subdirectories, file_names in os.walk(root_directory):
        for file_name in file_names:
            if file_name.lower().endswith(IMAGE_EXTENSIONS):
                image_paths.append(os.path.join(directory_path, file_name))
    return image_paths


def run_compare(path_a, path_b):
    """Compare two images and print their distance."""
    vector_a = get_vector(path_a)
    vector_b = get_vector(path_b)
    if vector_a is None or vector_b is None:
        print("could not read one of the images")
        return
    print("distance = %.4f" % get_distance(vector_a, vector_b))


def run_search(query_path, image_directory):
    """1:N search: rank every image under image_directory against the query image."""
    query_vector = get_vector(query_path)
    if query_vector is None:
        print("could not read the query image")
        return
    # Skip the query image itself, comparing it with itself would always rank first
    try:
        query_real_path = os.path.realpath(query_path)
    except OSError:
        query_real_path = query_path
    candidate_paths = []
    for image_path in collect_images(image_directory):
        try:
            if os.path.realpath(image_path) != query_real_path:
                candidate_paths.append(image_path)
        except OSError:
            if image_path != query_path:
                candidate_paths.append(image_path)
    if not candidate_paths:
        print("no other images found under %s" % image_directory)
        return

    # Compute all embeddings in parallel, pool.map keeps the input order
    with ThreadPoolExecutor(max_workers=threads_count) as thread_pool:
        candidate_vectors = list(thread_pool.map(get_vector, candidate_paths))
    results = []
    for image_path, candidate_vector in zip(candidate_paths, candidate_vectors):
        if candidate_vector is not None:
            results.append((get_distance(query_vector, candidate_vector), image_path))
    results.sort(key=lambda result: result[0])  # ascending distance, most similar first
    for index, (distance, image_path) in enumerate(results, 1):
        try:
            relative_path = os.path.relpath(image_path, image_directory)
        except ValueError:
            relative_path = image_path
        print("%2d. %.4f  %s" % (index, distance, relative_path))


first_is_directory = os.path.isdir(first_argument)
second_is_directory = os.path.isdir(second_argument)
if first_is_directory and second_is_directory:
    # Two directories: cannot tell which one is the query image
    print("give one image and one directory, not two directories")
    sys.exit(0)
if (not first_is_directory) and (not second_is_directory):
    run_compare(first_argument, second_argument)  # two images
elif second_is_directory:
    run_search(first_argument, second_argument)  # image + directory
else:
    run_search(second_argument, first_argument)  # directory + image
    
"""Thanks, everyone. May technology serve humanity — and may the world know peace."""
