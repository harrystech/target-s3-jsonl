"""Tests standard target features using the built-in SDK tests library."""
import os

from target_s3_jsonl.sinks import S3JsonlSink
from target_s3_jsonl.target import TargetS3Jsonl
from moto import mock_s3
import boto3
import pytest

from unittest import TestCase, mock


class TestS3JsonlSink(TestCase):

    @pytest.fixture(autouse=True)
    def aws_credentials(self):
        """Mocked AWS Credentials for moto."""
        os.environ["AWS_ACCESS_KEY_ID"] = "testing"
        os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
        os.environ["AWS_SECURITY_TOKEN"] = "testing"
        os.environ["AWS_SESSION_TOKEN"] = "testing"

    def setUp(self) -> None:
        self.stream_name = 'stream_test'
        self.s3_bucket = 'unit-test-bucket'
        self.s3_prefix = 'unit-test-prefix'

    def test_get_batch_s3_key(self):
        context = {
            'filename': 'filename.jsonl'
        }
        target_s3_jsonl = TargetS3Jsonl(
            config={
                's3_bucket': self.s3_bucket,
                's3_prefix': self.s3_prefix,
                'hive_partitions': [
                    {
                        "name": "__pk_a",
                        "value": "value_a",
                    },
                    {
                        "name": "__pk_b",
                        "value": "value_b",
                    }
                ]
            }
        )

        sink = S3JsonlSink(target_s3_jsonl, key_properties=None, schema={'properties': {}},
                           stream_name=self.stream_name)

        self.assertEqual(sink._get_batch_s3_key(
            context), f"{self.s3_prefix}/{self.stream_name}/__pk_a=value_a/__pk_b=value_b/{context['filename']}")

    def test_get_batch_s3_key_no_partitions(self):
        context = {
            'filename': 'filename.jsonl'
        }
        target_s3_jsonl = TargetS3Jsonl(
            config={
                's3_bucket': self.s3_bucket,
                's3_prefix': self.s3_prefix,
            }
        )

        sink = S3JsonlSink(target_s3_jsonl,
                           key_properties=None,
                           schema={'properties': {}},
                           stream_name=self.stream_name)

        self.assertEqual(sink._get_batch_s3_key(
            context), f"{self.s3_prefix}/{self.stream_name}/{context['filename']}")

    @mock_s3
    @mock.patch("target_s3_jsonl.sinks.S3JsonlSink._get_batch_s3_key")
    def test_process_batch(self, mock_get_batch_s3_key):
        context = {
            'filename': 'filename.jsonl'
        }

        boto3_session = boto3.session.Session()
        s3_connection = boto3_session.resource("s3", region_name="us-east-1")
        s3_connection.create_bucket(Bucket=self.s3_bucket)

        target_s3_jsonl = TargetS3Jsonl(
            config={
                's3_bucket': self.s3_bucket,
                's3_prefix': ""
            }
        )

        sink = S3JsonlSink(target_s3_jsonl,
                           key_properties=None, schema={'properties': {}},
                           stream_name=self.stream_name)

        mock_get_batch_s3_key.return_value = 'path/to/file.jsonl'

        with mock.patch("builtins.open", mock.mock_open(read_data="data")) as mock_file:
            sink.process_batch(context=context, boto3_session=boto3_session)

        mock_file.assert_called_with("filename.jsonl", 'r')

        s3_client = boto3_session.client('s3')

        self.assertIn('path/to/file.jsonl', [content['Key'] for content in s3_client.list_objects_v2(
            Bucket=self.s3_bucket
        )['Contents']])
