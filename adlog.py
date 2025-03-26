import random
import datetime
import faker
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import os
load_dotenv()

# Elasticsearch 設定
if "cloud_id" in os.environ:
    cloud_id = os.environ['cloud_id']
    esapi_key = os.environ['esapi_key']
    es = Elasticsearch(cloud_id=cloud_id, api_key=esapi_key,request_timeout=10)
else:
    print("Define cloud_id")
    exit()

print(es.info())
INDEX_NAME = "logs-ad"

# Elasticsearch クライアント作成
es = Elasticsearch(
    cloud_id=cloud_id,
    api_key=esapi_key
)
# Fakerでユーザー名を生成
fake = faker.Faker()

def create_index():
    """インデックスを作成する"""
    body = {
    "settings": {
      "index": {
        "mode": "lookup"
      }
    },
        "mappings": {
            "properties": {
            "source.ip": {
                "type": "ip"
            }
            }
        }
    }
    es.indices.create(index=INDEX_NAME, body=body)

from elasticsearch import helpers

def generate_fake_ad_logs(num_entries=200):
    create_index()
    """Windows ADの疑似ログ（ログインイベントのみ）をElastic Cloudに送信する"""
    bulk_actions = []
    for _ in range(num_entries):
        timestamp = datetime.datetime.now() - datetime.timedelta(minutes=random.randint(1, 60))
        event_id = random.randint(4624, 4625)  # 4624: 成功, 4625: 失敗
        user = fake.user_name()
        event = "User Logon"
        ip_address = f"192.168.1.{random.randint(0, 100)}"
        
        log_entry = {
            "@timestamp": timestamp.strftime('%Y-%m-%dT%H:%M:%S'),
            "event_id": event_id,
            "user.name": user,
            "event": event,
            "source.ip": ip_address
        }
        
        # バルク用アクション追加
        bulk_actions.append({
            "_index": INDEX_NAME,
            "_source": log_entry
        })

        # 1000件毎にバルク投入
        if len(bulk_actions) % 1000 == 0:
            helpers.bulk(es, bulk_actions)
            bulk_actions = []
            print(f"Bulk inserted 1000 entries")

    # 残りのデータを投入
    if bulk_actions:
        helpers.bulk(es, bulk_actions)
        print(f"Bulk inserted {len(bulk_actions)} remaining entries")

if __name__ == "__main__":
    generate_fake_ad_logs()
