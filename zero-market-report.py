import json
import os
from datetime import datetime, timedelta, timezone

import boto3
import telegram
from boto3.dynamodb.conditions import Key

TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME")
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
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

    dt = datetime.utcnow().replace(tzinfo=timezone.utc)
    dt_to = (
        dt
        - timedelta(minutes=dt.minute %
                    10, seconds=dt.second, microseconds=dt.microsecond)
        - timedelta(milliseconds=1)
    )
    dt_from = (
        dt_to
        - timedelta(minutes=10)
        + timedelta(milliseconds=1)
    )

    orders = list(dynamodb_query(
        table_orders,
        IndexName="created_date-created_at-index",
        KeyConditionExpression=(
            Key("created_date").eq(dt_from.date().isoformat())
            & Key("created_at").between(
                dt_from.isoformat(timespec="milliseconds"),
                dt_to.isoformat(timespec="milliseconds"),
            )
        )
    ))
    orders_by_client = dict()
    for order in orders:
        orders_by_client.setdefault(
            order["client_id"], []).append(order["order_list"])

    bot = telegram.Bot(token=TOKEN)
    bot.sendMessage(chat_id=CHAT_ID, text=json.dumps(orders_by_client))

    return {
        "statusCode": 200,
        "body": json.dumps("Hello from Lambda!")
    }
