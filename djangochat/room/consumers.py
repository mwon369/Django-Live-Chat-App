import json
from channels.generic.websocket import AsyncWebsocketConsumer # used to create consumer
from asgiref.sync import sync_to_async # storing asynchornous data in the database

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # get name of the room we're trying to connect to based on its URL
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # join the room by using both the names of the channel and room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
    
    async def disconnect(self, close_code):
        # same as joining except we use group_discard
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        ) 