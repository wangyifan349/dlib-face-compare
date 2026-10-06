"""Minimal dlib face comparison demo.

First locate a face with either the HOG or the CNN detector, then straighten it
to 150x150 using 5 landmarks (both eyes, the tip of the nose and the mouth
corners), and finally let the ResNet extract a 128 dimensional feature vector.
If the euclidean distance between two vectors is below the threshold 0.6 they
are considered the same person; search mode scores every image in a given
folder and sorts them by distance, so the most similar image comes first.
The CNN detector is far more accurate but much slower, while the HOG detector
needs no weight file, runs fast and works best on clear, well lit frontal photos.

Commands:
    python face_compare.py compare a.jpg b.jpg                    compare two images
    python face_compare.py search a.jpg ./photos                  1:N search inside a folder
    python face_compare.py -d cnn search a.jpg ./photos           use the CNN face detector
    python face_compare.py -m my_model.dat search a.jpg ./photos  use a custom recognition model
"""
import os
import sys

import dlib

base_dir = os.path.dirname(os.path.abspath(__file__))                       # folder of this script
model_dir = os.path.join(base_dir, "models")                               # folder holding the weight files
recognition_model = os.path.join(model_dir, "dlib_face_recognition_resnet_model_v1.dat")  # recognition network: image -> 128-d
landmark_model = os.path.join(model_dir, "shape_predictor_5_face_landmarks.dat")           # 5 point landmark model
cnn_model = os.path.join(model_dir, "mmod_human_face_detector.dat")         # CNN face detector weights
threshold = 0.6                                                            # euclidean distance, below this value = same person
chip_size = 150                                                            # size of the straightened face, fixed input of the network
detector_type = "hog"                                                      # detector: hog = fast, cnn = accurate

args = sys.argv[1:]
if args and args[0] == "-m":                                               # custom recognition model
    recognition_model = args[1]
    args = args[2:]
if args and args[0] == "-d":                                               # pick the face detector
    detector_type = args[1]
    args = args[2:]

print("usage:\n"
      "    python face_compare.py compare a.jpg b.jpg                     compare two images\n"
      "    python face_compare.py search  a.jpg <image_dir>               1:N search, sorted by similarity\n"
      "    python face_compare.py -d cnn  search  a.jpg <image_dir>       use the CNN face detector\n"
      "    python face_compare.py -m model.dat search  a.jpg <image_dir>  use a custom recognition model\n"
      "    same person when distance < %s   current detector: %s\n" % (threshold, detector_type))

if not args:
    sys.exit(0)

predictor = dlib.shape_predictor(landmark_model)                           # landmark model, weights read on construction
recognizer = dlib.face_recognition_model_v1(recognition_model)             # recognition network, weights read on construction

if detector_type == "cnn":                                                 # CNN detector, ships its own weights
    detector = dlib.cnn_face_detection_model_v1(cnn_model)
else:                                                                      # HOG detector, needs no weight file
    detector = dlib.get_frontal_face_detector()


def get_vector(image_path):
    """Return the 128-d feature vector, or None when no face is detected."""
    image = dlib.load_rgb_image(image_path)                                 # read the image as RGB
    detections = detector(image, 1)                                         # detect faces, 1 = upsample one level
    if not detections:
        return None
    rect = detections[0].rect if detector_type == "cnn" else detections[0]  # CNN returns mmod_rect, HOG returns rectangle
    landmarks = predictor(image, rect)                                      # both eyes, nose tip and mouth corners
    face_chip = dlib.get_face_chip(image, landmarks, chip_size, chip_size)   # crop and straighten the face
    return recognizer.compute_face_descriptor(face_chip)                   # 128-d feature vector


def get_distance(vector_a, vector_b):
    """Euclidean distance between two feature vectors."""
    return sum((x - y) ** 2 for x, y in zip(vector_a, vector_b)) ** 0.5


if args[0] == "compare":
    vector_a, vector_b = get_vector(args[1]), get_vector(args[2])
    if vector_a is None or vector_b is None:
        print("no face detected")
    else:
        distance = get_distance(vector_a, vector_b)
        print("distance = %.4f" % distance)                                # the smaller, the more similar
        print("same person" if distance < threshold else "different people")

elif args[0] == "search":
    query_vector = get_vector(args[1])
    if query_vector is None:
        print("no face detected in the query image")
    else:
        results = []
        for file_name in os.listdir(args[2]):                               # walk through the folder
            if not file_name.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".webp")):
                continue
            candidate_vector = get_vector(os.path.join(args[2], file_name))
            if candidate_vector is not None:                                # skip images without a face
                results.append((get_distance(query_vector, candidate_vector), file_name))

        results.sort()                                                      # ascending distance = most similar first
        for index, (distance, file_name) in enumerate(results, 1):
            print("%2d. %.4f  %-30s %s" % (index, distance, file_name,
                                           "MATCH" if distance < threshold else ""))
