"""s3-jsonl target class."""

from __future__ import annotations

from singer_sdk import typing as th
from singer_sdk.target_base import Target

from target_s3_jsonl.sinks import S3JsonlSink


class TargetS3Jsonl(Target):
    """Sample target for s3-jsonl."""

    name = "target-s3-jsonl"
    config_jsonschema = th.PropertiesList(
        th.Property(
            "bucket",
            th.StringType,
            description="The scheme with which output files will be named."
            " Required when specifying storage type S3",
            required=True,
        ),
        th.Property(
            "prefix_scheme",
            th.StringType,
            description="The scheme with which output files will be named",
        ),
        th.Property(
            "filename_prefix",
            th.StringType,
            description="The scheme with which to name each file. "
            "Make sure it is unique per stream.",
            default="{stream_name}",  # type: ignore
        ),
        th.Property(
            "max_size",
            th.IntegerType,
            description="Max number of record per batch",
            default=10000,  # type: ignore
        ),
    ).to_dict()

    default_sink_class = S3JsonlSink


if __name__ == "__main__":
    TargetS3Jsonl.cli()
