"""s3-jsonl target sink class, which handles writing streams."""

from __future__ import annotations

import json
import logging
from pathlib import Path

import boto3
from singer_sdk.sinks import BatchSink


class S3JsonlSink(BatchSink):
    """s3-jsonl target sink class."""

    @property
    def include_sdc_metadata_properties(self):
        """Include extra columns with sdc metadata properties."""
        return self.config["include_sdc_metadata_properties"]

    @property
    def max_size(self) -> int:
        """Override max batch size.

        Returns: Max number of records to batch before `is_full=True`
        """
        return self.config["max_size"]

    def _hive_partitions_to_key(self):
        return [
            f"{hive_partition['name']}={hive_partition['value']}"
            for hive_partition in self.config["hive_partitions"]
        ]

    def _get_batch_key(self, batch_id):
        path = self.config["prefix_scheme"].format(
            stream_name=self.stream_name, batch_id=batch_id
        )
        filename = "-".join(
            [
                self.config["filename_prefix"].format(stream_name=self.stream_name),
                batch_id,
            ]
        )
        return f"{path}/{filename}.jsonl"

    def start_batch(self, context: dict) -> None:
        """Start a batch.

        Developers may optionally add additional markers to the `context` dict,
        which is unique to this batch.
        """
        # Sample:
        # ------
        context["filepath"] = self._get_batch_key(context["batch_id"])
        Path(context["filepath"]).parent.mkdir(parents=True, exist_ok=True)

    def process_record(self, record: dict, context: dict) -> None:
        """Process the record.

        Developers may optionally read or write additional markers within the
        passed `context` dict from the current batch.
        """
        with open(context["filepath"], "a", encoding="utf-8") as json_file:
            json_file.write(json.dumps(record, default=str) + "\n")

    def process_batch(self, context: dict, boto3_session=None) -> None:
        """Write out any prepped records and return once fully written."""
        if not boto3_session:
            boto3_session = boto3._get_default_session()

        bucket = self.config["bucket"]
        filepath = context["filepath"]

        s3_client = boto3_session.client("s3")
        logging.info(
            f"{self.stream_name}: Writing {context['batch_id']} "
            f"to s3://{bucket}/{filepath}",
            extra={"stream_name": self.stream_name, "batch_id": context["batch_id"]},
        )
        with open(context["filepath"], "r") as f:
            s3_client.put_object(Body=f.read(), Bucket=bucket, Key=filepath)
        logging.info(
            f"Deleting file locally after a successful upload: {context['filepath']}"
        )
        Path(context["filepath"]).unlink()
