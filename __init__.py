import requests
import json
import time
from typing import Optional
class Client:
    def __init__(self, token):
        self.token = token
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'User-Agent': 'NextGuild/1.0'
        }
        self.base_url = 'https://www.guilded.gg/api/v1'
        self.cache = {}
    def send_message(self, channel_id, content):
        url = f'{self.base_url}/channels/{channel_id}/messages'
        data = {'content': content}
        response = self.request('POST', url, json=data)
        return response
    def send_reply(self, channel_id, content, replyids):
        url = f'{self.base_url}/channels/{channel_id}/messages'
        data = {'content': content, 'replyMessageIds': replyids}
        response = self.request('POST', url, json=data)
        return response
    def edit_message(self, channel_id, message_id, content):
        url = f'{self.base_url}/channels/{channel_id}/messages/{message_id}'
        data = {'content': content}
        response = self.request('PUT', url, json=data)
        return response
    def delete_message(self, channel_id, message_id):
     url = f'{self.base_url}/channels/{channel_id}/messages/{message_id}'
     response = self.request('DELETE', url)
     return response
    def get_message(self, channel_id, message_id):
        url = f'{self.base_url}/channels/{channel_id}/messages/{message_id}'
        response = self.request('GET', url)
        return response
    def get_channel_messages(self, channel_id):
        if channel_id in self.cache:
            return self.cache[channel_id]
        else:
            url = f'{self.base_url}/channels/{channel_id}/messages'
            messages = []
            response = self.request('GET', url)
            while response:
                messages.extend(response)
                last_message_id = response
                response = self.request('GET', url, params={'before': last_message_id})
            self.cache[channel_id] = messages
            return messages
    def purge(self, channel_id, amount):
     messages = self.get_channel_messages(channel_id)[:amount]
     message_ids = [message['id'] for message in messages]
     for message_id in message_ids:
        self.delete_message(channel_id, message_id)
     return len(message_ids)
    def request(self, method, url, **kwargs):
        response = requests.request(method, url, headers=self.headers, **kwargs)
        if response.status_code == 429:
            retry_after = int(response.headers.get('retry-after', '1'))
            print(f'Received 429 status. Retrying after {retry_after} seconds.')
            time.sleep(retry_after)
            return self.request(method, url, **kwargs)
        else:
            data = response.json()
            if 200 <= response.status_code < 300:
                # Write response data to txt file
                #with open('response.txt', 'w') as f:
                    #f.write(json.dump(data, f))
                return data
            else:
                raise ValueError(f'Request failed with status {response.status_code}: {data}')
    def create_channel(self, name, type, serverid, groupid=None, categoryid=None, ispublic=None):
        data = {'name': name, 'type': type}
        url = f'{self.base_url}/channels'
        if categoryid:
            categoryid = {'categoryId': categoryid}
            data.update(categoryid)
        if groupid:
            groupid = {'groupId': groupid}
            data.update(groupid)
        if serverid:
            serverid = {'serverId': serverid}
            data.update(serverid)
        if ispublic:
            ispublic = {"isPublic": ispublic}
            data.update(ispublic)
        response = self.request('POST', url, json=data)
        return response
    def get_channel(self, channelid):
        url = f'{self.base_url}/channels/{channelid}'
        response = self.request('GET', url)
        return response
    def delete_channel(self, channelid):
        url = f'{self.base_url}/channels/{channelid}'
        response = self.request('DELETE', url)
        return response
    def update_channel(self, channelid, name=None, topic=None, ispublic=None):
        data = {}
        url = f'{self.base_url}/channels/{channelid}'
        if name:
            name = {'name': name}
            data.update(name)
        if topic:
            topic = {'topic': topic}
            data.update(topic)
        if ispublic:
            ispublic = {'ispublic': ispublic}
            data.update(ispublic)
        response = self.request('PATCH', url, json=data)
        return response
    def get_server(self, serverid):
        url = f'{self.base_url}/servers/{serverid}'
        response = self.request('GET', url)
        return response
    def create_listitem(self, channelid, title, note=None):
        data = {'message': title}
        url = f'{self.base_url}/channels/{channelid}/items'
        if note:
            note = {'note': {'content': note}}
            data.update(note)
        response = self.request('POST', url, json=data)
        return response
    def get_listitem(self, channelid, listitemid):
        url = f'{self.base_url}/channels/{channelid}/items/{listitemid}'
        response = self.request('GET', url)
        return response