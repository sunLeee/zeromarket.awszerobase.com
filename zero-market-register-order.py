import json
import os
from datetime import datetime, timezone

import boto3

TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME")
table_orders = boto3.resource("dynamodb").Table(TABLE_NAME)


def lambda_handler(event, context):

    dt = datetime.utcnow().replace(tzinfo=timezone.utc)
    order_id = f'{event["client_id"]}_{str(int(dt.timestamp()))}'

    response = table_orders.put_item(Item={
        "order_id": order_id,
        "client_id": event["client_id"],
        "order_list": event["order_list"],
        "payment": event.get("payment") or "success",
        "delivery": {
            "address": event["delivery"]["address"],
            "status": event["delivery"].get("status") or "requested",
        },
        "created_at": dt.isoformat(timespec="milliseconds"),
        "created_date": dt.date().isoformat(),
        "last_modified_at": dt.isoformat(timespec="milliseconds"),
    })

    return {
        "statusCode": 200,
        "body": json.dumps(f"Successfully registered your order! Your order ID is {order_id}")
    }
