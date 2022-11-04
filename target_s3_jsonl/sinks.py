"""s3-jsonl target sink class, which handles writing streams."""

from __future__ import annotations

import json

import boto3 as boto3
from singer_sdk.sinks import BatchSink

s3_client = boto3.client('s3')


class S3JsonlSink(BatchSink):
    """s3-jsonl target sink class."""

    max_size = 10000  # Max records to write in one batch

    def start_batch(self, context: dict) -> None:
        """Start a batch.

        Developers may optionally add additional markers to the `context` dict,
        which is unique to this batch.
        """
        # Sample:
        # ------
        batch_key = context["batch_id"]
        context["file_path"] = f"{self.config['file_path'].rtrim('/')}/{self.stream_name}_{batch_key}.jsonl"

    def process_record(self, record: dict, context: dict) -> None:
        """Process the record.

        Developers may optionally read or write additional markers within the
        passed `context` dict from the current batch.
        """
        # Sample:
        # ------
        # with open(context["file_path"], "a") as csvfile:
        #     csvfile.write(record)

        filename_path = [self.stream_name]
        if 'filepath' in self.config:
            filename_path.append(self.config['filepath'])

        with open(context['file_path'], 'a', encoding='utf-8') as json_file:
            json_file.write(json.dumps(record) + '\n')

    def process_batch(self, context: dict) -> None:
        """Write out any prepped records and return once fully written."""
        # Sample:
        # ------
        s3_client.upload(context["file_path"], self.batch_config)  # Upload file
