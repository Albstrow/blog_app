from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse

from django.contrib.auth.decorators import login_required
from django.db.models import Q

from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.forms import UserCreationForm

from app.models import Room, Topic, Message, User, Profile
from app.forms import RoomForm, ProfileForm, MyUserCreationForm

# rooms = [
#     {'id': 1, 'name': "C++"},
#     {'id': 2, 'name': "Python"},
#     {'id': 3, 'name': "Java"},

# ]
# Create your views here.


def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        username = request.POST.get('Username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username)
        except:
            messages.error(request, "User does not exist")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Username OR password does not exist")

    context = {'page': page}
    return render(request, "app/login_register.html", context)


def logoutUser(request):
    logout(request)
    return redirect('home')


def registerPage(request):
    form = MyUserCreationForm()
    profile_form = ProfileForm()

    if request.method == "POST":
        form = MyUserCreationForm(request.POST)
        profile_form = ProfileForm(request.POST, request.FILES)
        if form.is_valid() and profile_form.is_valid():
            user = form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(
                request, " Username already exists or the password is too short. It must contain at least 8 characters.")

    return render(request, 'app/register.html', {'form': form, 'profile_form': profile_form})


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )
# limit the topics to 5
    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))

    context = {"rooms": rooms, 'topics': topics,
               'room_count': room_count, 'room_messages': room_messages}
    return render(request, "app/home.html", context)


def room(request, pk):
    # room=None
    # for i in rooms:
    #     if i['id']==int(pk):
    #         room=i
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()

    if request.method == "POST":
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        return redirect('room', pk=room.id)

    context = {'room': room, 'room_messages': room_messages}
    return render(request, "app/room.html", context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    # Profile = request.user.Profile.objects.all()
    Profile = 1
    context = {'user': user, 'rooms': rooms,
               'room_messages': room_messages, 'topics': topics, 'Profile': Profile}
    return render(request, 'app/profile.html', context)


@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        # print(request.POST)
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description')
        )
        return redirect('home')
    context = {'form': form, 'topics': topics}
    return render(request, 'app/room_form.html', context)


@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse('You are not allowed here')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')
    context = {'form': form, 'topics': topics}
    return render(request, 'app/room_form.html', context)


@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('Your are mnot allowed here!!')
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'app/delete.html', {"obj": room})


@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('Your are not allowed here!!')
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'app/delete.html', {"obj": message})


@login_required(login_url='login')
def updateUser(request):
    # profile_form = ProfileForm()
    # if request.method == "POST":
    #     profile_form = ProfileForm(request.POST, request.FILES)

    #     if profile_form.is_valid():
    #         print("hello save")
    #         # profile = form.save(commit=False)
    #         # profile.user = request.user
    #         # profile.save()
    #         profile_form.save()
    #         return redirect('user-profile', pk=request.user.id)
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            print("ekek")
            form.save()
        return redirect('user-profile', pk=request.user.id)
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'app/update-user.html', {'form': form})


def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'app/topics.html', {'topics': topics})


def activityPage(request):
    room_messages = Message.objects.all()
    return render(request, 'app/activity.html', {'room_messages': room_messages})
