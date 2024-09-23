# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import shutil
import subprocess
import time
from uuid import uuid4


from openrelik_worker_common.utils import (
    create_output_file,
    get_input_files,
    task_result,
)

from .app import celery


# Task name used to register and route the task to the correct queue.
TASK_NAME = "openrelik-worker-hayabusa.tasks.html_report"

# Task metadata for registration in the core system.
TASK_METADATA = {
    "display_name": "Hayabusa HTML report",
    "description": "Windows event log triage",
}


@celery.task(bind=True, name=TASK_NAME, metadata=TASK_METADATA)
def html_report(
    self,
    pipe_result=None,
    input_files=[],
    output_path=None,
    workflow_id=None,
    task_config={},
) -> str:
    input_files = get_input_files(pipe_result, input_files or [])
    output_files = []

    output_file = create_output_file(
        output_path,
        filename="Hayabusa_HTML_report",
        file_extension="html",
        data_type="openrelik:worker:hayabusa:file:html",
    )

    # Create temporary directory and hard link files for processing
    temp_dir = os.path.join(output_path, uuid4().hex)
    os.mkdir(temp_dir)
    for file in input_files:
        filename = os.path.basename(file.get("path"))
        os.link(file.get("path"), f"{temp_dir}/{filename}")

    command = [
        "/hayabusa/hayabusa",
        "csv-timeline",
        "--ISO-8601",
        "--UTC",
        "--no-wizard",
        "--quiet",
        "--clobber",
        "--HTML-report",
        output_file.path,
        "--output",
        "/dev/null",
        "--directory",
        temp_dir,
    ]

    INTERVAL_SECONDS = 2
    process = subprocess.Popen(command)
    while process.poll() is None:
        self.send_event("task-progress", data=None)
        time.sleep(INTERVAL_SECONDS)

    # Remove temp directory
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

    output_files.append(output_file.to_dict())

    if not output_files:
        raise RuntimeError("Hayabusa didn't create any output files")

    return task_result(
        output_files=output_files,
        workflow_id=workflow_id,
        command=" ".join(command),
    )
