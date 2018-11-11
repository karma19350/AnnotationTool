from pymongo import MongoClient
from datetime import datetime
import numpy as np
import time

client = MongoClient('mongodb://10.0.2.180:27017')
xiaomu = client.xiaomu
message = xiaomu.message


def get_messages(course_id):
    message_set = message.find(
        {'course_id': course_id, 'flag': {"$in": [None, 'more', 'try', "cached", "cached_more"]}, 'question_source': None}).sort('_id', -1)
    q_dict, a_dict = {}, {}
    for m in message_set:
        if 'flag' in m.keys() and m['flag'] == 'say_hello':
            continue
        elif 'message' in m.keys() and m['type'] == 'question':
            q_dict[m['_id']] = m

        elif 'message' in m.keys() and m['type'] == 'answer':
            a_dict[m['_id']] = m
    
    print(course_id)
    stored_questions = set([x['question'] for x in xiaomu.qa_annotation.find({"course_id": course_id})])
    
    q_text, a_text, times, tags = [], [], [], []
    for k, v in a_dict.items():
        if 'origin_question' not in v.keys():
            continue
        
        q_id = v['origin_question']
        if q_id not in q_dict:
            continue

        if q_dict[q_id]['message'] in stored_questions:
            continue

        q_text.append(q_dict[q_id]['message'])        
        # a_text.append(v['message'].replace('<br>', ' '))
        a_text.append(v['message'])        
        times.append(v['time'])
        tags.append(v.get('tag', -1))

    sort_index = np.argsort([time.mktime(x.timetuple()) for x in times])[::-1]

    response = [np.asarray(a_text)[sort_index], np.asarray(q_text)[sort_index], np.asarray(times)[sort_index], np.asarray(tags)[sort_index]]
    return [x[:100] for x in response]
