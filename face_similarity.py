"""
Face comparison / ranking demo built on face_recognition.
No same-person decision is made here: the script only computes the Euclidean
distance between 128-d embeddings and sorts the results from the smallest distance
(most similar) to the largest, so no threshold is needed.
Single-face and multi-face images are both supported: every face found in an image
is encoded, and an image takes part in the ranking with its best matching face.
The mode is chosen from the two arguments (no subcommands, no options):
    two image files                  -> compare the two images
    one image file + one directory   -> 1:N search, recursive, sorted by distance
Usage:
    python face_similarity.py a.jpg b.jpg      compare two images
    python face_similarity.py a.jpg ./photos   1:N search inside a folder (recursive)
    python face_similarity.py ./photos a.jpg   same, the order does not matter
"""
import os
import sys
from concurrent.futures import ThreadPoolExecutor
import face_recognition
# --- settings ------------------------------------------------------------------
DETECTION_MODEL = "hog"       # "hog" = fast on CPU, "cnn" = more accurate (GPU helps)
FALLBACK_WHOLE_IMAGE = True   # if no face is detected, treat the whole image as one face
NUM_JITTERS = 1               # 1 = fast, raise it for a more stable embedding (slower)
QUERY_FACE = "largest"        # which face of a multi-face query image to search with:
                              # "largest" (default) or a 0-based index like 0, 1, 2 ...
threads_count = os.cpu_count() or 1  # one worker thread per CPU core
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp", ".webp")
command_arguments = sys.argv[1:]
if len(command_arguments) != 2:
    print("usage:\n"
          "    python face_similarity.py a.jpg b.jpg\n"
          "    python face_similarity.py a.jpg <image_dir>\n"
          "    python face_similarity.py <image_dir> a.jpg")
    sys.exit(0)
first_argument = command_arguments[0]
second_argument = command_arguments[1]
def box_size(box):
    """(top, right, bottom, left) -> pixel area of the face box."""
    top, right, bottom, left = box
    return max(0, bottom - top) * max(0, right - left)

def find_boxes(image):
    """Face boxes (top, right, bottom, left). A single-face image works either way."""
    boxes = face_recognition.face_locations(image, model=DETECTION_MODEL)
    if not boxes and FALLBACK_WHOLE_IMAGE:
        image_height, image_width = image.shape[0], image.shape[1]
        boxes = [(0, image_width, image_height, 0)]  # whole image as the only face
    return boxes

def get_faces(image_path):
    """[ (128-d embedding, face box), ... ] for every face, [] if unreadable.
    One face -> one entry, several faces -> several entries, so single-face and
    multi-face images are handled the same way.
    """
    try:
        image = face_recognition.load_image_file(image_path)
    except Exception:
        return []
    faces = []
    for box in find_boxes(image):
        try:
            encodings = face_recognition.face_encodings(
                image, known_face_locations=[box], num_jitters=NUM_JITTERS)
        except Exception:
            continue  # skip a face that cannot be aligned, keep the others
        if encodings:
            faces.append((encodings[0], box))
    return faces

def get_distance(vector_a, vector_b):
    """Euclidean distance between two embeddings, the smaller the more similar."""
    return float(face_recognition.face_distance([vector_a], vector_b)[0])

def pick_query_face(faces):
    """One face of the query image: the largest by default, or QUERY_FACE as index."""
    if isinstance(QUERY_FACE, int):
        if 0 <= QUERY_FACE < len(faces):
            return QUERY_FACE, faces[QUERY_FACE]
        return 0, faces[0]
    if QUERY_FACE == "largest" and len(faces) > 1:
        index = max(range(len(faces)), key=lambda i: box_size(faces[i][1]))
        return index, faces[index]
    return 0, faces[0]

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
    """Compare two images: every face of A against every face of B, closest first."""
    faces_a = get_faces(path_a)
    faces_b = get_faces(path_b)
    if not faces_a or not faces_b:
        print("could not read one of the images, or no face found in it")
        return
    print("%s: %d face(s)   %s: %d face(s)"
          % (path_a, len(faces_a), path_b, len(faces_b)))
    pairs = []
    for index_a, (vector_a, _) in enumerate(faces_a):
        for index_b, (vector_b, _) in enumerate(faces_b):
            pairs.append((get_distance(vector_a, vector_b), index_a, index_b))
    pairs.sort(key=lambda pair: pair[0])  # ascending distance, closest first
    for rank, (distance, index_a, index_b) in enumerate(pairs, 1):
        print("%2d. %.4f  face %d <-> face %d" % (rank, distance, index_a + 1, index_b + 1))

def run_search(query_path, image_directory):
    """1:N search: rank every image under image_directory against the query image."""
    query_faces = get_faces(query_path)
    if not query_faces:
        print("could not read the query image, or no face found in it")
        return
    query_index, (query_vector, _) = pick_query_face(query_faces)
    if len(query_faces) > 1:
        print("query %s has %d face(s), using face %d"
              % (query_path, len(query_faces), query_index + 1))
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
        candidate_faces = list(thread_pool.map(get_faces, candidate_paths))
    results = []
    for image_path, faces in zip(candidate_paths, candidate_faces):
        best = None  # (distance, face index) of the closest face in this image
        for index, (candidate_vector, _) in enumerate(faces):
            distance = get_distance(query_vector, candidate_vector)
            if best is None or distance < best[0]:
                best = (distance, index)
        if best is not None:
            results.append((best[0], best[1], len(faces), image_path))
    results.sort(key=lambda result: result[0])  # ascending distance, closest first
    for rank, (distance, face_index, face_count, image_path) in enumerate(results, 1):
        try:
            relative_path = os.path.relpath(image_path, image_directory)
        except ValueError:
            relative_path = image_path
        print("%2d. %.4f  %s   [face %d/%d]"
              % (rank, distance, relative_path, face_index + 1, face_count))

first_is_directory = os.path.isdir(first_argument)
second_is_directory = os.path.isdir(second_argument)
if first_is_directory and second_is_directory:
    # Two directories: cannot tell which one is the query image
    print("give one image and one directory, not two directories")
    sys.exit(0)
if (not first_is_directory) and (not second_is_directory):
    run_compare(first_argument, second_argument)  # two images
elif second_is_directory:
    run_search(first_argument, second_argument)   # image + directory
else:
    run_search(second_argument, first_argument)   # directory + image
