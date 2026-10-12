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
DETECTION_MODEL = "cnn"       # "hog" = fast on CPU, "cnn" = more accurate (GPU helps)
FALLBACK_WHOLE_IMAGE = True   # if no face is detected, treat the whole image as one face
NUM_JITTERS = 1               # 1 = fast, raise it for a more stable embedding (slower)
QUERY_FACE = "largest"        # which face of a multi-face query image to search with:
                              # "largest" (default) or a 0-based index like 0, 1, 2 ...
THREAD_COUNT = os.cpu_count() or 1  # one worker thread per CPU core
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

def box_size(face_box):
    """(top, right, bottom, left) -> pixel area of the face box."""
    top, right, bottom, left = face_box
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
    for face_box in find_boxes(image):
        try:
            encodings = face_recognition.face_encodings(
                image, known_face_locations=[face_box], num_jitters=NUM_JITTERS)
        except Exception:
            continue  # skip a face that cannot be aligned, keep the others
        if encodings:
            faces.append((encodings[0], face_box))
    return faces
def get_distance(first_embedding, second_embedding):
    """Euclidean distance between two embeddings, the smaller the more similar."""
    return float(face_recognition.face_distance([first_embedding], second_embedding)[0])
def pick_query_face(faces):
    """One face of the query image: the largest by default, or QUERY_FACE as index."""
    if isinstance(QUERY_FACE, int):
        if 0 <= QUERY_FACE < len(faces):
            return QUERY_FACE, faces[QUERY_FACE]
        return 0, faces[0]
    if QUERY_FACE == "largest" and len(faces) > 1:
        largest_face_index = max(range(len(faces)),
                                 key=lambda face_index: box_size(faces[face_index][1]))
        return largest_face_index, faces[largest_face_index]
    return 0, faces[0]
def collect_images(root_directory):
    """Every image under root_directory, recursively. A single file is returned as is."""
    if os.path.isfile(root_directory):
        return [root_directory]
    image_paths = []
    for directory_path, subdirectory_names, file_names in os.walk(root_directory):
        for file_name in file_names:
            if file_name.lower().endswith(IMAGE_EXTENSIONS):
                image_paths.append(os.path.join(directory_path, file_name))
    return image_paths
def run_compare(first_image_path, second_image_path):
    """Compare two images: every face of the first against every face of the second,
    closest pair first.
    """
    first_faces = get_faces(first_image_path)
    second_faces = get_faces(second_image_path)
    if not first_faces or not second_faces:
        print("could not read one of the images, or no face found in it")
        return
    print("%s: %d face(s)   %s: %d face(s)"
          % (first_image_path, len(first_faces), second_image_path, len(second_faces)))
    pairs = []
    for first_face_index, (first_embedding, first_face_box) in enumerate(first_faces):
        for second_face_index, (second_embedding, second_face_box) in enumerate(second_faces):
            pairs.append((get_distance(first_embedding, second_embedding),
                          first_face_index, second_face_index))
    pairs.sort(key=lambda pair: pair[0])  # ascending distance, closest first
    for rank, (distance, first_face_index, second_face_index) in enumerate(pairs, 1):
        print("%2d. %.4f  face %d <-> face %d"
              % (rank, distance, first_face_index + 1, second_face_index + 1))
def run_search(query_image_path, image_directory):
    """1:N search: rank every image under image_directory against the query image."""
    query_faces = get_faces(query_image_path)
    if not query_faces:
        print("could not read the query image, or no face found in it")
        return
    query_face_index, (query_embedding, query_face_box) = pick_query_face(query_faces)
    if len(query_faces) > 1:
        print("query %s has %d face(s), using face %d"
              % (query_image_path, len(query_faces), query_face_index + 1))
    # Skip the query image itself, comparing it with itself would always rank first
    try:
        query_real_path = os.path.realpath(query_image_path)
    except OSError:
        query_real_path = query_image_path
    candidate_image_paths = []
    for image_path in collect_images(image_directory):
        try:
            if os.path.realpath(image_path) != query_real_path:
                candidate_image_paths.append(image_path)
        except OSError:
            if image_path != query_image_path:
                candidate_image_paths.append(image_path)
    if not candidate_image_paths:
        print("no other images found under %s" % image_directory)
        return
    # Compute all embeddings in parallel, pool.map keeps the input order
    with ThreadPoolExecutor(max_workers=THREAD_COUNT) as thread_pool:
        candidate_faces = list(thread_pool.map(get_faces, candidate_image_paths))
    results = []
    for image_path, faces in zip(candidate_image_paths, candidate_faces):
        closest_match = None  # (distance, face index) of the closest face in this image
        for face_index, (candidate_embedding, candidate_face_box) in enumerate(faces):
            distance = get_distance(query_embedding, candidate_embedding)
            if closest_match is None or distance < closest_match[0]:
                closest_match = (distance, face_index)
        if closest_match is not None:
            results.append((closest_match[0], closest_match[1], len(faces), image_path))
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
