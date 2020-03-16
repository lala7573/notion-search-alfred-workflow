#-*- coding: utf-8 -*-

import sys
import json
import httplib, urllib
import os

# config
notionSpaceId = os.environ['notionSpaceId']
cookie = os.environ['cookie']
notion_protocol = 'notion'  # or https

alfredQuery = "{query}"
class Payload(object):
    def __init__(self, j):
        self.__dict__ = json.loads(j)


class searchResult(object):
    def __init__(self, id):
        self._id = id
        self._title = None
        self._icon = None
        self._link = None
        self._subtitle = None

    @property
    def id(self):
        return self._id

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value

    @property
    def icon(self):
        return self._icon

    @icon.setter
    def icon(self, value):
        self._icon = value

    @property
    def link(self):
        return self._link

    @link.setter
    def link(self, value):
        self._link = value

    @property
    def subtitle(self):
        return self._subtitle

    @subtitle.setter
    def subtitle(self, value):
        self._subtitle = value


def buildNotionSearchQueryData(spaceId):
    def f(query):
        return json.dumps({
            'type': 'BlocksInSpace',
            'query': query,
            'spaceId': spaceId,
            'sort': 'Relevance',
            'source': 'quick_find',
            'limit': 20,
            'filters': {
                'isDeletedOnly': False,
                'excludeTemplates': False,
                'isNavigableOnly': True,
                'requireEditPermissions': False,
                'ancestors': [],
                'createdBy': [],
                'editedBy': [],
                'lastEditedTime': [],
                'createdTime': []
            }
        })
    return f


def http_request(method, host, path, header, query):
    conn = httplib.HTTPSConnection(host)
    conn.request(method, path, query, header)
    response = conn.getresponse()
    # print response.status, response.reason
    data = response.read()
    conn.close()
    return data


buildQuery = buildNotionSearchQueryData(notionSpaceId)

# Call Notion
headers = {
    "Content-type": "application/json",
    "Cookie": cookie}
query = buildQuery(alfredQuery)
data = http_request('POST', 'www.notion.so', '/api/v3/search', headers, buildQuery(alfredQuery))

# Extract search results from notion response
searchResultList = []
searchResults = Payload(data)
for x in searchResults.results:
    obj = searchResult(x.get('id'))
    value = searchResults.recordMap.get('block').get(obj.id).get('value')
    highlight = x.get('highlight')

    obj.title = highlight.get('text', '')
    if not obj.title:
        if value.get('type') == 'page':
            obj.title = value.get('properties').get('title')[0][0]

    obj.subtitle = highlight.get('pathText', None)
    if not obj.subtitle:
        obj.subtitle = ""

    obj.icon = value.get('format', {}).get('page_icon', None)
    if obj.icon:
        obj.title = obj.icon + " " + obj.title
    obj.link = "%s://www.notion.so/%s" % (notion_protocol, obj.id.replace('-', ''))
    searchResultList.append(obj)

itemList = []
for obj in searchResultList:
    itemList.append({
        'uid': obj.id,
        'type': 'default',
        'title':  obj.title.replace('<gzkNfoUU>', '').replace('</gzkNfoUU>', ''),
        'arg': obj.link,
        'subtitle': obj.subtitle.replace('<gzkNfoUU>', '').replace('</gzkNfoUU>', ''),
        # 'autocomplete': searchResultObject.title
    })

if not itemList:
    itemList.append({
        'uid': 1,
        'type': 'default',
        'title': 'No results - go to Notion homepage',
        'arg': '%s://www.notion.so' % notion_protocol,
    })

sys.stdout.write(json.dumps({'items': itemList}))
