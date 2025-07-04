import json
import time
from random import randint
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from .models import Profile, Comment, Post, Followers, LikePost, ChatMessage, RoomMember

# If you're using Agora token builder, ensure it's installed and imported
from agora_token_builder import RtcTokenBuilder


def signup(request):
    if request.method == 'POST':
        name = request.POST.get('fnm')
        email = request.POST.get('emailid')
        password = request.POST.get('pwd')

        if User.objects.filter(email=email).exists():
            return render(request, 'signup.html', {'invalid': 'Email already exists.'})

        user = User.objects.create_user(username=email, email=email, password=password, first_name=name)
        Profile.objects.create(user=user)
        return redirect('login')

    return render(request, 'signup.html')


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('emailid')
        password = request.POST.get('pwd')

        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            user = None

        if user:
            auth_login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'invalid': 'Invalid credentials.'})

    return render(request, 'login.html')


@login_required
def logout_view(request):
    auth_logout(request)
    return redirect('login')


@login_required
def home(request):
    following_users = Followers.objects.filter(follower=request.user.username).values_list('user', flat=True)
    posts = Post.objects.filter(Q(user=request.user.username) | Q(user__in=following_users)).order_by('-created_at')
    profile, created = Profile.objects.get_or_create(user=request.user)

    context = {
        'profile': profile,
        'posts': posts,
        'comments': Comment.objects.all(),
    }
    return render(request, 'main.html', context)


@login_required
def upload(request):
    if request.method == 'POST':
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']
        Post.objects.create(user=request.user.username, image=image, caption=caption)
    return redirect('/')


@login_required
def likes(request, id):
    username = request.user.username
    post = get_object_or_404(Post, id=id)

    like_filter = LikePost.objects.filter(post_id=id, username=username).first()

    if like_filter is None:
        LikePost.objects.create(post_id=id, username=username)
        post.no_of_likes += 1
    else:
        like_filter.delete()
        post.no_of_likes -= 1

    post.save()
    return redirect(request.META.get('HTTP_REFERER', f'/post/{id}/'))


@login_required
def explore(request):
    post = Post.objects.all().order_by('-created_at')
    profile = Profile.objects.get(user=request.user)

    context = {
        'post': post,
        'profile': profile
    }
    return render(request, 'explore.html', context)


@login_required
def profile(request, id_user):
    user_object = get_object_or_404(User, username=id_user)
    profile = Profile.objects.get(user=request.user)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=id_user).order_by('-created_at')

    is_following = Followers.objects.filter(follower=request.user.username, user=id_user).exists()
    follow_unfollow = 'Unfollow' if is_following else 'Follow'

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_posts.count(),
        'profile': profile,
        'follow_unfollow': follow_unfollow,
        'user_followers': Followers.objects.filter(user=id_user).count(),
        'user_following': Followers.objects.filter(follower=id_user).count(),
    }

    if request.user.username == id_user and request.method == 'POST':
        image = request.FILES.get('image', user_profile.profileimg)
        bio = request.POST['bio']
        location = request.POST['location']

        user_profile.profileimg = image
        user_profile.bio = bio
        user_profile.location = location
        user_profile.save()
        return redirect(f'/profile/{id_user}/')

    return render(request, 'profile.html', context)


@login_required
def delete(request, id):
    post = get_object_or_404(Post, id=id)
    if post.user == request.user.username:
        post.delete()
    return redirect(f'/profile/{request.user.username}/')


@login_required
def search_results(request):
    query = request.GET.get('q', '')
    users = Profile.objects.filter(user__username__icontains=query)
    posts = Post.objects.filter(caption__icontains=query)

    return render(request, 'search_user.html', {
        'query': query,
        'users': users,
        'posts': posts,
    })


@login_required
def home_post(request, id):
    post = get_object_or_404(Post, id=id)
    profile = Profile.objects.get(user=request.user)

    return render(request, 'main.html', {
        'post': post,
        'profile': profile
    })


@login_required
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comment_text = request.POST.get('comment_text', '').strip()

    if comment_text:
        Comment.objects.create(
            post=post,
            user=request.user,
            comment_text=comment_text
        )

    return redirect(request.META.get('HTTP_REFERER', f'/post/{post_id}/'))


@login_required
def follow(request):
    if request.method == 'POST':
        follower = request.POST['follower']
        user = request.POST['user']

        follow_obj = Followers.objects.filter(follower=follower, user=user).first()

        if follow_obj:
            follow_obj.delete()
        else:
            Followers.objects.create(follower=follower, user=user)

        return redirect(f'/profile/{user}/')
    return redirect('/')


@login_required
def message_list(request):
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'message_list.html', {'users': users})


@login_required
def chat_view(request, username):
    other_user = get_object_or_404(User, username=username)
    messages = ChatMessage.objects.filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user, receiver=request.user)
    )

    if request.method == 'POST':
        message_text = request.POST.get('message')
        if message_text:
            ChatMessage.objects.create(sender=request.user, receiver=other_user, message=message_text)
            return redirect('chat_view', username=other_user.username)

    return render(request, 'chat.html', {
        'other_user': other_user,
        'messages': messages
    })


def lobby(request):
    return render(request, 'lobby.html')


def room(request):
    return render(request, 'lobby.html')


def getToken(request):
    appId = 'f3bd7777211642db8e3c596c7b72ac35'
    appCertificate = '453f4d99e23743a3bd42215166ce65e8'
    channelName = request.GET.get('channelName')
    uid = randint(1, 230)
    expirationTimeInSecond = 3600
    currentTimestamp = int(time.time())
    privilegeExpiredTs = currentTimestamp + expirationTimeInSecond
    role = 1

    token = RtcTokenBuilder.buildTokenWithUid(appId, appCertificate, channelName, uid, role, privilegeExpiredTs)
    return JsonResponse({'token': token, 'uid': uid, 'channelName': channelName})


@csrf_exempt
def createMember(request):
    data = json.loads(request.body)
    member, created = RoomMember.objects.get_or_create(
        name=data['name'],
        uid=data['uid'],
        room_name=data['roomName']
    )
    return JsonResponse({'name': data['name']}, safe=False)


@csrf_exempt
def getMembers(request):
    uid = request.GET.get('UID')
    room_name = request.GET.get('roomName')
    member = RoomMember.objects.filter(room_name=room_name, uid=uid).first()
    name = member.name if member else None
    return JsonResponse({'name': name}, safe=False)


@csrf_exempt
def deleteMember(request):
    data = json.loads(request.body)
    member = RoomMember.objects.filter(
        name=data['name'],
        uid=data['uid'],
        room_name=data['roomName']
    ).first()

    if member:
        member.delete()
        return JsonResponse({'message': 'Member deleted successfully'}, status=200)
    else:
        return JsonResponse({'message': 'Member not found'}, status=404)
