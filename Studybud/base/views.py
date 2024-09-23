from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Room, Message, Topic, User
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .forms import RoomForm, UserForm, MyUserCreationForm
from django.http import HttpResponse



# rooms = [
#     {'id': 1, 'name':'Lets learn python'},
#     {'id': 2, 'name':'Designing with Me'},
#     {'id': 3, 'name':'Front end developers'},
# ]

def LoginView(request): 
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or password does not exist')
        
    context = {'page': page}
    return render(request, 'base/login_form.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occurred during registration')

    return render(request, 'base/login_form.html', {'form': form})



def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    rooms = Room.objects.filter(
        Q(topic__top_name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)) #here we are creating a room object. give us all the information.

    topics = Topic.objects.all()
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__top_name__icontains=q))

    context = {'rooms': rooms, 'topics': topics, 'room_count': room_count, 'room_messages': room_messages} #we are passing the rooms available in the database to the home.html template
    return render(request, 'base/home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk) #get id and set it to the primary key
    room_messages = room.message_set.all()
    participants = room.participants.all()

    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=room, #room id
            body=request.POST.get('body')
        )
        room.participants.add(request.user) #add the user to the room participants
        return redirect('room', pk=room.id)
    

    context = {'room': room, 'room_messages': room_messages, 'participants': participants, 'room_messages': room_messages}
    return render(request, 'base/room.html', context)
                                #^                  #^
                                #|               #   | describes what information to return in form of a dicationary
                                #|
                                #|
                                #describes where the information is being returned
# When you use context = {'room': room}, you're creating a dictionary where the key 'room' represents the data you want 
# to pass (the selected room) and the value is the variable room, which contains the room details retrieved in the view

def userProfile(request, pk):
    #get user by primary key
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms': rooms, 'room_messages': room_messages,
               'topics': topics} #we are passing the user's information to the userProfile.html template
    return render(request, 'base/profile.html', context)


@login_required(login_url='login')
def createRoom(request):
    form = RoomForm() #form without any information
    type = 'Create'
    topics = Topic.objects.all()

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(top_name=topic_name)

        Room.objects.create(
            host = request.user,# current user.No input
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description')
        )
        
    context = {'form': form, 'type': type}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def updateform(request, pk):
    room = get_object_or_404(Room, id=pk)  # Fetch room or return 404
    form = RoomForm(instance=room)  # Populate form with existing room data
    type = 'Edit'

    if request.user != room.host:
        return HttpResponse('You are not the owner of this room')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(top_name=topic_name)

        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')


    context = {'form': form, 'room': room, 'type': type}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': room})


@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    # Ensure only the message owner can delete
    if request.user != message.user:
        return HttpResponse('You are not the owner of this room')

    # Check if the deletion is confirmed via a POST request
    if request.method == 'POST':
        message.delete()
        return redirect('home')

    # Render a confirmation page before deletion
    return render(request, 'base/delete.html', {'obj': message})



@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    return render(request, 'base/update-user.html', {'form': form})