import json
from channels.generic.websocket import AsyncWebsocketConsumer # used to create consumer
from asgiref.sync import async_to_sync

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # get name of the room we're trying to connect to based on its URL
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # join the room by adding the user's channel to a channel layer group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name # Django will assign channel names for us
        )

        await self.accept()
    
    async def disconnect(self, close_code):
        # same as joining except we use group_discard
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        ) 

    async def receive(self, text_data):
        # convert JSON to object/dictionary
        data = json.loads(text_data)
        # filter through the object for the data we want
        message = data['message']
        username = data['username']
        room = data['room']

        # send the message to other consumers listening to the same group/channel
        # this will allow different instances of the application to talk to each other
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
                'room': room,
            }
        )

    # function to receive events and turn them into websocket frames
    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        room = event['room']

        # send the message to the client
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            'room': room,
        }))
