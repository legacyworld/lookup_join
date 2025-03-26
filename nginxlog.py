import random
import datetime
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
INDEX_NAME = "logs-nginx"

# Elasticsearch クライアント作成
es = Elasticsearch(
    cloud_id=cloud_id,
    api_key=esapi_key
)

def create_index():
    """インデックスを作成する"""
    body = {
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

def generate_nginx_log_entry(num_entries=5000):
    """Nginxの疑似ログエントリをバルク投入"""
    create_index()
    
    bulk_actions = []
    for i in range(num_entries):
        timestamp = datetime.datetime.now() - datetime.timedelta(minutes=random.randint(1, 60))
        ip_address = f"192.168.1.{random.randint(0, 100)}"
        http_method = random.choice(["GET", "POST", "PUT", "DELETE"])
        endpoint = f"/page-{random.randint(1, 20)}.html"
        http_version = "HTTP/1.1"
        status_code = random.choice([200, 301, 404, 500])
        response_size = random.randint(500, 5000)
        referer = "-"
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"

        log_entry = {
            "@timestamp": timestamp.strftime('%Y-%m-%dT%H:%M:%S'),
            "source.ip": ip_address,
            "method": http_method,
            "endpoint": endpoint,
            "http_version": http_version,
            "status": status_code,
            "response_size": response_size,
            "referer": referer,
            "user.agent": user_agent
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
    generate_nginx_log_entry()
