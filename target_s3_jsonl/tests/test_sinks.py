"""Tests standard target features using the built-in SDK tests library."""
import os
from unittest import TestCase, mock

import boto3
import pytest
from moto import mock_s3

from target_s3_jsonl.sinks import S3JsonlSink
from target_s3_jsonl.target import TargetS3Jsonl


class TestS3JsonlSink(TestCase):
    @pytest.fixture(autouse=True)
    def aws_credentials(self):
        """Mocked AWS Credentials for moto."""
        os.environ["AWS_ACCESS_KEY_ID"] = "testing"
        os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
        os.environ["AWS_SECURITY_TOKEN"] = "testing"
        os.environ["AWS_SESSION_TOKEN"] = "testing"

    def setUp(self) -> None:
        self.stream_name = "stream_test"
        self.bucket = "unit-test-bucket"
        self.prefix_scheme = (
            "unit-test-prefix/{stream_name}/__pk_a=value_a/__pk_b=value_b"
        )
        self.filename_prefix = "{stream_name}"
        self.batch_id = "123"

    def test_get_batch_key(self):
        target_s3_jsonl = TargetS3Jsonl(
            config={
                "bucket": self.bucket,
                "prefix_scheme": self.prefix_scheme,
                "filename_prefix": self.filename_prefix,
            }
        )

        sink = S3JsonlSink(
            target_s3_jsonl,
            key_properties=None,
            schema={"properties": {}},
            stream_name=self.stream_name,
        )

        self.assertEqual(
            sink._get_batch_key(self.batch_id),
            f"unit-test-prefix/{self.stream_name}/__pk_a=value_a/"
            f"__pk_b=value_b/{self.stream_name}-{self.batch_id}.jsonl",
        )

    @mock_s3
    @mock.patch("pathlib.Path.unlink")
    def test_process_batch(self, mock_unlink: mock.Mock):
        filepath = "path/to/file.jsonl"
        context = {"filepath": filepath, "batch_id": mock.MagicMock()}

        boto3_session = boto3.session.Session()
        s3_connection = boto3_session.resource("s3", region_name="us-east-1")
        s3_connection.create_bucket(Bucket=self.bucket)

        target_s3_jsonl = TargetS3Jsonl(
            config={"bucket": self.bucket, "prefix_scheme": ""}
        )

        sink = S3JsonlSink(
            target_s3_jsonl,
            key_properties=None,
            schema={"properties": {}},
            stream_name=self.stream_name,
        )

        with mock.patch("builtins.open", mock.mock_open(read_data="data")) as mock_file:
            sink.process_batch(context=context, s3_client=boto3_session.client("s3"))

        mock_file.assert_called_with(filepath, "r")
        mock_unlink.assert_called_once()

        s3_client = boto3_session.client("s3")

        self.assertIn(
            filepath,
            [
                content["Key"]
                for content in s3_client.list_objects_v2(Bucket=self.bucket)["Contents"]
            ],
        )
