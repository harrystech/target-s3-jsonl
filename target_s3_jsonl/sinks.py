"""s3-jsonl target sink class, which handles writing streams."""

from __future__ import annotations

import json

import boto3 as boto3
from singer_sdk.sinks import BatchSink


class S3JsonlSink(BatchSink):
    """s3-jsonl target sink class."""

    max_size = 10000  # Max records to write in one batch

    def _hive_partitions_to_key(self):
        return [f"{hive_partition['name']}={hive_partition['value']}" for hive_partition in
                self.config['hive_partitions']]

    def _get_batch_s3_key(self, context):
        return "/".join(
            [self.config['s3_prefix'], self.stream_name, *self._hive_partitions_to_key(), context['filename']])

    def start_batch(self, context: dict) -> None:
        """Start a batch.

        Developers may optionally add additional markers to the `context` dict,
        which is unique to this batch.
        """
        # Sample:
        # ------
        batch_key = context["batch_id"]
        context["filename"] = f"{self.stream_name}_{batch_key}.jsonl"

    def process_record(self, record: dict, context: dict) -> None:
        """Process the record.

        Developers may optionally read or write additional markers within the
        passed `context` dict from the current batch.
        """
        with open(context['filename'], 'a', encoding='utf-8') as json_file:
            json_file.write(json.dumps(record) + '\n')

    def process_batch(self, context: dict, boto3_session=None) -> None:
        """Write out any prepped records and return once fully written."""
        # Sample:
        # ------
        if not boto3_session:
            boto3_session = boto3._get_default_session()

        s3_client = boto3_session.client('s3')
        with open(context['filename'], 'r') as f:
            s3_client.put_object(Body=f.read(), Bucket=self.config['s3_bucket'], Key=self._get_batch_s3_key(context))
