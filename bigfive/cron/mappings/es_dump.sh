# 225 global config 
elasticdump \
  --input=http://219.224.134.225:9202/holders \
  --output=http://219.224.134.225:9201/holders \
  --type=data \
  --limit=5000


# 225 global config 
elasticdump \
--input=http://219.224.134.225:9202/announcement \
--output=http://219.224.134.225:9201/announcement \
--type=data \
--limit=5000

elasticdump \
--input=http://219.224.134.225:9202/announcement_old \
--output=http://219.224.134.225:9201/announcement_old \
--type=data \
--limit=1000

elasticdump \
--input=http://219.224.134.225:9202/manipulate_credit \
--output=http://219.224.134.225:9201/manipulate_credit \
--type=data \
--limit=100

elasticdump \
  --input=http://219.224.134.225:9201/holders/all \
  --output=query.json \

elasticdump \
--input=http://219.224.134.225:9201/ \
--output=http://10.134.12.121:9201/ \

json

elasticdump \
  --input=http://219.224.134.225:9201/manipulate_day \
  --output=/home/lcr/dump_es/manipulate_day.json \
  --type=data


elasticdump \
--input=http://219.224.134.225:9201/mani_describe \
--output=/home/lcr/dump_es/mani_describe.json \
--type=data \
--searchBody '{"query":{"term":{"date": "2018-09-07"}}}'


elasticdump \
--input=http://219.224.134.225:9201/stock_list \
--output=/home/lcr/dump_es/stock_list.json \
--type=data

elasticdump \
--input=http://219.224.134.225:9201/market_daily \
--output=/home/lcr/dump_es/market_daily.json \
--type=data \
--searchBody '{"query":{"term":{"date": "2018-09-07"}}}'


elasticdump \
--input=http://219.224.134.225:9201/time_axis \
--output=/home/lcr/dump_es/time_axis.json \
--type=data \
--searchBody '{"query":{"term":{"date": "2018-09-07"}}}'


elasticdump \
--input=http://219.224.134.225:9201/market_daily \
--output=http://219.224.134.225:9208/market_daily \
--type=data \
--limit=1000

aliyun-mappings

elasticdump \
--input=http://219.224.134.225:9201/market_daily \
--output=/home/lcr/dump_es/market_daily_mapping.json \
--type=mapping

elasticdump \
--output=http://47.94.133.29:9201/market_daily \
--input=/home/lcr/dump_es/market_daily_mapping.json \
--type=mapping

elasticdump \
--input=/mnt/data/20180926mani/es_mapping0926/market_daily-mapping.json \
--output=http://127.0.0.1:9201/market_daily \
--type=mapping