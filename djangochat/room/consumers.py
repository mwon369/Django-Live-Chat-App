import json
from channels.generic.websocket import AsyncWebsocketConsumer # used to create consumer
from asgiref.sync import sync_to_async
from .models import Message, Room
from django.contrib.auth.models import User

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

        # sync function will finish saving the message to the database before sending to the chatroom
        await self.save_message(username, room, message)

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

    # makes it possible to store data in the database while we await for the async functions
    @sync_to_async
    def save_message(self, username, room, message):
        # get user/room data based on the username and room (slug) that is passed in
        user = User.objects.get(username=username)
        room = Room.objects.get(slug=room)
        # save the message to the database
        Message.objects.create(user=user, room=room, content=message)