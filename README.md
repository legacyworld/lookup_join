# Psuedo Log for Elasticsearch LOOKUP JOIN
This program creates Psuedo log of AD and NGINX. With IP address as key, join the user name of AD log to NGINX log.

# How to use
Create .env file for Elasticsearch credentials.

```
cloud_id=<cloud id of Elasticsearch>
esapi_key=<API Key>
```
Execute followings:
```
docker compose up -d
docker exec -it join python /src/adlog.py 
docker exec -it join python /src/nginxlog.py
```