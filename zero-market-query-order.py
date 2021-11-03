import json
import os

import boto3
from boto3.dynamodb.conditions import Key

TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME")
table_orders = boto3.resource("dynamodb").Table(TABLE_NAME)


def dynamodb_query(
    table: "boto3.resources.factory.dynamodb.Table",
    /,
    **kwargs,
):
    resp = table.query(
        **kwargs,
    )
    yield from resp["Items"]
    while "LastEvaluatedKey" in resp:
        resp = table.query(
            **kwargs,
            ExclusiveStartKey=resp["LastEvaluatedKey"],
        )
        yield from resp["Items"]


def lambda_handler(event, context):
    client_id = event["queryStringParameters"]["client_id"]
    ret = list(dynamodb_query(
        table_orders,
        KeyConditionExpression=Key("client_id").eq(client_id),
    ))

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
        },
        "body": json.dumps(ret)
    }
