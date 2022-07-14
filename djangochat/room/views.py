from django.shortcuts import render
from .models import Room
from django.contrib.auth.decorators import login_required

# use decorator to ensure user is logged in
@login_required
def rooms(request):
    # render the list of all rooms we have in the database
    rooms = Room.objects.all()
    return render(request, 'room/rooms.html', {'rooms': rooms})

@login_required
def room(request, slug):
    # find a specific room in the database by its slug and render it
    room = Room.objects.get(slug=slug)
    return render(request, 'room/room.html', {'room': room})