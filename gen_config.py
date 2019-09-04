from __future__ import division, print_function, absolute_import

import yaml
from os.path import basename, splitext, join
from glob import glob
import sys
import random


def utt_id(path):
    return splitext(basename(path))[0].replace("_ref", "").replace("_gen", "")


def template(testname, testId):
    return {
        "testname": testname,
        "testId": testId,
        "bufferSize": 2048,
        "stopOnErrors": True,
        "showButtonPreviousPage": True,
        "remoteService": "service/write.php",
        "pages": [],
    }


def first_page():
    return {
        "type": "generic",
        "name": "welcome",
        "id": "first page",
        "content": "Welcome to the listening test.",
    }


def finish_page():
    return {
        "type": "finish",
        "name": "Thank you",
        "content": "Thank you for attending!",
        "showResults": False,
        "writeResults": True,
        "questionnaire": [{
            "type": "text",
            "label": "email",
            "name": "email",
        }],
    }


def template_mushra(ref, gen, label, name, id=None, content=""):
    genname = utt_id(gen)
    stimuli_name = "{}:{}".format(label, genname)
    if id is None:
        id = name
    return {
        "type": "mushra",
        "name": name,
        "id": id,
        "content": content,
        "reference": ref,
        "showWaveform": True,
        "enableLooping": False,
        "createAnchor35": False,
        "createAnchor70": False,
        "showConditionNames": False,
        "strict": False,
        "stimuli":
            {stimuli_name: gen},
    }


categories = [
    "00-ground-truth",
    "01-taco2",
]
base_dir = "./configs/resources/00-subjective-test/"
seed = 1234

# LIMIST FOR EACH SET
# for N in [2, 3, 5, None]: # this is for testing to create subset (N utt.) of exp.
# None means use all wav files
for N in [None]:
    name_suffix = "_N{}".format(N) if N is not None else ""
    wav_files = []
    labels = []
    for c in categories:
        in_dir = join(base_dir, c)
        wf = sorted(glob(join(in_dir, "*.wav")))
        if N is not None and N > 0:
            wf = wf[:N]
        wav_files.extend(wf)
        labels.extend([c] * len(wf))

    # Make YAML
    data_mos = template("MOS evaluation", "espnet_tts_mos{}".format(name_suffix))

    random.seed(seed)
    random.shuffle(wav_files)
    random.seed(seed)
    random.shuffle(labels)

    for idx, (label, f) in enumerate(zip(labels, wav_files)):
        name = splitext(basename(f))[0].replace("_gen", "").replace("_ref", "")
        id = "{}:{}".format(label, name)
        name = "{}/{}:{}".format(idx+1, len(wav_files), name)
        page = template_mushra(f, f, label, name, id)
        data_mos["pages"].append(page)

    data_mos["pages"].insert(0, first_page())
    data_mos["pages"].append(finish_page())

    with open("./configs/espnet_tts_mos{}.yaml".format(name_suffix), "w") as f:
        f.write(yaml.dump(data_mos))

print("config files are generated")
sys.exit(0)
