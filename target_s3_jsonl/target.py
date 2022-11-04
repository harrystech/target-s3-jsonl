"""s3-jsonl target class."""

from __future__ import annotations

from singer_sdk.target_base import Target
from singer_sdk import typing as th

from target_s3_jsonl.sinks import (
    S3JsonlSink,
)


class TargetS3Jsonl(Target):
    """Sample target for s3-jsonl."""

    name = "target-s3-jsonl"
    config_jsonschema = th.PropertiesList(
        th.Property(
            "s3_bucket",
            th.StringType,
            description="The scheme with which output files will be named",
            required=True
        ),
        th.Property(
            "s3_prefix",
            th.StringType,
            description="The path to the target output file",
            required=True
        ),
        # th.Property(
        #     "file_naming_scheme",
        #     th.StringType,
        #     description="The scheme with which output files will be named"
        # ),
        th.Property(
            "hive_partitions",
            th.ArrayType(th.ObjectType(
                th.Property(
                    'name',
                    th.StringType,
                    description="Name of the hive partition"
                ),
                th.Property(
                    'value',
                    th.StringType,
                    description="Value of the hive partition"
                )
            )),
            description="List of name-value pairs for hive partitioning when writing to S3. "
                        "Preserve the other of the key dfines.",
            default=[]
        )

    ).to_dict()

    default_sink_class = S3JsonlSink


if __name__ == "__main__":
    TargetS3Jsonl.cli()
