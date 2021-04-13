import os
import json

from tqdm import tqdm
from pathlib import Path
from multiprocessing import Pool
from math import floor, ceil

from examtool.api.database import get_exam, get_roster, get_submissions
from examtool.api.extract_questions import extract_questions
from examtool.api.scramble import scramble


def download(exam, emails_to_download: [str] = None, debug: bool = False):
    exam_json = get_exam(exam=exam)
    exam_json.pop("secret")
    exam_json = json.dumps(exam_json)

    template_questions = list(extract_questions(json.loads(exam_json)))

    total = [
        ["Email"]
        + [question["text"] for question in extract_questions(json.loads(exam_json))]
    ]

    email_to_data_map = {}

    if emails_to_download is None:
        roster = get_roster(exam=exam)
        emails_to_download = [email for email, _ in roster]

    i = 1
    for email, response in tqdm(
        get_submissions(exam=exam), dynamic_ncols=True, desc="Downloading", unit="Exam"
    ):
        i += 1
        if emails_to_download is not None and email not in emails_to_download:
            continue

        if debug and 1 < len(response) < 10:
            tqdm.write(email, response)

        total.append([email])
        for question in template_questions:
            total[-1].append(response.get(question["id"], ""))

        student_questions = list(
            extract_questions(scramble(email, json.loads(exam_json), keep_data=True))
        )

        email_to_data_map[email] = {
            "student_questions": student_questions,
            "responses": response,
        }

    return json.loads(exam_json), template_questions, email_to_data_map, total

