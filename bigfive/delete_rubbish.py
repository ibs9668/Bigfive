# -*- coding: utf-8 -*-
from elasticsearch.helpers import scan

from bigfive.config import es


def delete_event_rubbish():
    index_list = [
        'event_wordcloud',
        'event_river',
        'event_message_type',
        'event_geo',
        'event_emotion_geo',
        'event_emotion',
        'event_emotion',
    ]
    needed_item_event_id_list = []
    for i in scan(client=es, index='event_information', doc_type='text', query={"query": {"bool": {"must": [{"match_all": {}}]}}}):
        needed_item_event_id_list.append(i['_source']['event_id'])

    for index in index_list:
        print(index)
        event_cur = scan(client=es, index=index, doc_type='text', query={"query": {"bool": {"must": [{"match_all": {}}]}}})
        for item in event_cur:
            if item['_source']['event_id'] not in needed_item_event_id_list:
                try:
                    es.delete(index=index, doc_type='text', id=item['_id'])
                except:
                    pass


def delete_group_rubbish():
    index_list = [
        'group_activity',
        'group_domain_topic',
        'group_emotion',
        'group_influence',
        'group_information',
        'group_personality',
        'group_task',
        'group_text_analysis_sta',
    ]

    needed_item_group_id_list = []
    for i in scan(client=es, index='group_ranking', doc_type='text',
                  query={"query": {"bool": {"must": [{"match_all": {}}]}}}):
        needed_item_group_id_list.append(i['_source']['group_id'])

    for index in index_list:
        print(index)
        group_cur = scan(client=es, index=index, doc_type='text', query={"query": {"bool": {"must": [{"match_all": {}}]}}})
        for item in group_cur:
            try:
                if item['_source']['group_id'] not in needed_item_group_id_list:
                    try:
                        # print(item['_id'])
                        es.delete(index=index, doc_type='text', id=item['_id'])
                    except:
                        pass
            except:
                if item['_id'] not in needed_item_group_id_list:
                    try:
                        # print(item['_id'])
                        es.delete(index=index, doc_type='text', id=item['_id'])
                    except:
                        pass


if __name__ == '__main__':
    # delete_event_rubbish()
    # delete_group_rubbish()
    pass
