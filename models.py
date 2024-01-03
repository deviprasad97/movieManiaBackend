import boto3
from botocore.exceptions import ClientError
import logging
import config
import json

logger = logging.getLogger(__name__)

class MovieCollection:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', 
                            aws_access_key_id=config.aws_access_key_id,
                            aws_secret_access_key=config.aws_secret_access_key,
                            region_name=config.region_name)
        self.table = self.dynamodb.Table('MovieCollection')

    def add(self, data):
        try:
            response = self.table.put_item(Item=data)
            return response
        except ClientError as e:
            logger.error(f"Error in add_movie_collection: {e}")
            raise

    def delete(self, aid, movieid):
        try:
            response = self.table.delete_item(
                Key={'aid': aid, 'movieid': movieid}
            )
            return response
        except ClientError as e:
            logger.error(f"Error in delete_movie_collection: {e}")
            raise

    def list(self, aid, start_key=None, limit=10):
        try:
            if start_key != 0:
                response = self.table.query(
                    KeyConditionExpression=boto3.dynamodb.conditions.Key('aid').eq(aid),
                    Limit=limit,
                    ExclusiveStartKey=start_key
                )
            else:
                response = self.table.query(
                    KeyConditionExpression=boto3.dynamodb.conditions.Key('aid').eq(aid),
                    Limit=limit
                )
            items = response.get('Items', [])
            for item in items:
                if 'release_data' in item and item['release_data']:
                    item['release_data'] = json.loads(item['release_data'])
            last_evaluated_key = response.get('LastEvaluatedKey')
            return items, last_evaluated_key
        except ClientError as e:
            logger.error(f"Error in list_movie_collection: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON in list_movie_collection: {e}")
            raise
