import json
import os
import pathlib
from datetime import datetime
from io import BytesIO

from multiprocessing.pool import ThreadPool
import threading
from tqdm import tqdm
from pikepdf import Pdf, Encryption
import click
import pytz

from examtool.api.database import get_exam, get_roster
from examtool.api.utils import sanitize_email
from examtool.api.scramble import scramble
from examtool.api.gen_latex import render_latex
from examtool.cli.utils import (
    determine_semester,
    exam_name_option,
    hidden_output_folder_option,
    prettify,
)


@click.command()
@exam_name_option
@hidden_output_folder_option
@click.option(
    "--subtitle",
    prompt=True,
    default="Structure and Interpretation of Computer Programs",
)
@click.option(
    "--do-twice",
    is_flag=True,
    help="Run the compile twice for each student to fix weird rendering bugs.",
)
@click.option("--email", help="The email address of a particular student.")
@click.option(
    "--exam-type",
    default="Final Exam",
    help="The type of exam you are given. For example 'Final Exam' (default).",
)
@click.option(
    "--semester",
    default=determine_semester(),
    help=f"The semester of the exam. '{determine_semester()}' (default).",
)
@click.option(
    "--deadline",
    default=None,
    help="Generates exam regardless of if student is in roster with the set deadline.",
)
@click.option(
    "--num-threads",
    default=16,
    type=int,
    help="The number of simultaneous exams to process.",
)
@click.option(
    "--same-folder",
    default=False,
    is_flag=True,
    help="This flag will cause the compilation to all occur in the same folder.",
)
def compile_all(
    exam,
    out,
    subtitle,
    do_twice,
    email,
    exam_type,
    semester,
    deadline,
    num_threads,
    same_folder,
):
    """
    Compile individualized PDFs for the specified exam.
    Exam must have been deployed first.
    """
    if not out:
        out = "out/latex/" + exam

    pathlib.Path(out).mkdir(parents=True, exist_ok=True)
    try:
        exam_data = get_exam(exam=exam)
    except Exception as e:
        print(
            f"Exception: Unable to pull the exam {exam}. Received: {e}\nDid you deploy the exam first?"
        )
        return
    password = exam_data.pop("secret")[:-1]
    print(password)
    exam_str = json.dumps(exam_data)

    roster = get_roster(exam=exam, include_no_watermark=True)

    if email:
        roster = [line_info for line_info in roster if line_info[0] == email]
        if len(roster) == 0:
            if deadline:
                roster = [(email, deadline, False)]
            else:
                raise ValueError("Email does not exist in the roster!")

    def render_student_pdf(data):
        (
            email,
            deadline,
            no_watermark,
        ) = data
        if not deadline:
            return
        exam_data = json.loads(exam_str)
        scramble(email, exam_data)
        if no_watermark:
            exam_data.pop("watermark")
        deadline_utc = datetime.utcfromtimestamp(int(deadline))
        deadline_pst = pytz.utc.localize(deadline_utc).astimezone(
            pytz.timezone("America/Los_Angeles")
        )
        deadline_string = deadline_pst.strftime("%I:%M%p")

        uid = threading.get_ident()

        if same_folder:
            out_name = f"out{uid}"
            path = "temp"
        else:
            out_name = "out"
            path = f"temp/{uid}"

        with render_latex(
            exam_data,
            {
                "emailaddress": sanitize_email(email),
                "deadline": deadline_string,
                "coursecode": prettify(exam.split("-")[0]),
                "description": subtitle,
                "examtype": exam_type,
                "semester": semester,
            },
            do_twice=do_twice,
            path=path,
            out_name=out_name,
            suppress_output=True,
            return_out_path=True,
        ) as out_path:
            with open(out_path, "rb") as pdf:
                pdf = Pdf.open(BytesIO(pdf.read()))
                pdf.save(
                    os.path.join(
                        out, "exam_" + email.replace("@", "_").replace(".", "_") + ".pdf"
                    ),
                    encryption=Encryption(owner=password, user=password),
                )
                pdf.close()

    with ThreadPool(num_threads) as p:
        list(
            tqdm(
                p.imap_unordered(render_student_pdf, roster),
                total=len(roster),
                desc="Exams Generated",
                unit="Exam",
            )
        )



if __name__ == "__main__":
    compile_all()
