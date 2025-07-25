from django.shortcuts import render, redirect , get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from .models import LikePost, Profile, Post , Followers
from django.db.models import Q
from django.contrib.auth.decorators import login_required

def signup(request):
    if request.method == 'POST':
        fnm = request.POST.get('fnm')
        email_id = request.POST.get('email_id')
        password = request.POST.get('password')

        if User.objects.filter(username=fnm).exists():
            invalid = "USER ALREADY EXISTS"
            return render(request, 'signup.html', {'invalid': invalid})

        my_user = User.objects.create_user(fnm, email_id, password)
        my_user.save()

        new_profile = Profile.objects.create(user=my_user, id_user=my_user.id)
        new_profile.save()

        auth_login(request, my_user)
        return redirect('/')

    return render(request, 'signup.html')

def login_view(request):
    if request.method == 'POST':
        fnm = request.POST.get('fnm')
        password = request.POST.get('password')
        user = authenticate(request, username=fnm, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('/')
        error = "INVALID CREDENTIALS"
        return render(request, 'login.html', {'error': error})
    
    return render(request, 'login.html')


@login_required(login_url='/login')
def logout_view(request):
    auth_logout(request)
    return redirect('/login')

@login_required(login_url='/login')
def upload(request):
    if request.method == 'POST':
        user = request.user.username
        image = request.FILES.get('image-upload')
        caption = request.POST.get('caption')
        new_post = Post.objects.create(user=user, image=image, caption=caption) 
        new_post.save()  
        return redirect('/')
    else:
        return redirect('/')


@login_required(login_url='/login')
def home(request):
    following_users = Followers.objects.filter(follower=request.user.username).values_list('user', flat=True)
    post = Post.objects.filter(
        Q(user=request.user.username) | Q(user__in=following_users)
    ).order_by('-created_at')

    profile_data = Profile.objects.get(user=request.user)
    context = {
        'post': post,
        'profile_data': profile_data,
    }
    return render(request, 'main.html', context)
@login_required(login_url='/login')
def likes(request, id):
    username = request.user.username
    post = get_object_or_404(Post, id=id)

    like_filter = LikePost.objects.filter(post_id=id, username=username).first()

    if like_filter is None:
        # User has not liked yet
        LikePost.objects.create(post_id=id, username=username)
        post.no_of_likes += 1
    else:
        # User already liked → unlike
        like_filter.delete()
        post.no_of_likes -= 1

    post.save()

    return redirect('/#' + str(id))

@login_required(login_url='/login')
def home_posts(request):
    post = Post.objects.get(id=id)
    profile= profile.objects.get
    context={
        'post':post,
        'profile':profile,
    }

    return render(request , "main.html", context)


def explore(request):
    post = Post.objects.all().order_by('-created_at')
    profile = Profile.objects.get(user=request.user)
    context = {
        'post': post,
        'profile': profile
    }
    return render(request, 'explore.html', context)

@login_required(login_url='/login')
def profile(request, id_user):
    user_object = get_object_or_404(User, username=id_user)
    user_profile, created = Profile.objects.get_or_create(user=user_object, id_user=user_object.id)
    user_post = Post.objects.filter(user=user_object).order_by('-created_at')
    user_post_len = user_post.count()
    follower=request.user.username
    user=id_user
    if Followers.objects.filter(follower=follower, user = user).first():
        follow_unfollow='Unfollow'
    else:
        follow_unfollow='Follow'
    
    user_followers=len(Followers.objects.filter(user=id_user))
    user_following=len(Followers.objects.filter(follower=id_user))

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_post': user_post,
        'user_post_len': user_post_len,
        'follow_unfollow':follow_unfollow,
        'user_following':user_following,
        'user_followers':user_followers,
    }


    if request.user.username ==id_user:
        if request.method == 'POST':
            if request.FILES.get('image')==None:
                image=user_profile.profileimg
                bio=request.POST['bio']
                location=request.POST['location']

                user_profile.profileimg=image
                user_profile.bio=bio
                user_profile.location=location
                user_profile.save()
            if request.FILES.get('image')!=None:
                image=request.FILES.get('image')
                bio=request.POST['bio']
                location=request.POST['location']

                user_profile.profileimg=image
                user_profile.bio=bio
                user_profile.location=location
                user_profile.save()
            return redirect('/profile/'+id_user)
        else:
            return render(request, 'profile.html', context)

    return render(request, 'profile.html', context)

def follow(request):
    if request.method == 'POST':
        follower = request.POST['follower']
        user = request.POST['user']

        if Followers.objects.filter(follower=follower, user=user).exists():
            delete_follower = Followers.objects.get(follower=follower, user=user)
            delete_follower.delete()
        else:
            new_follower = Followers.objects.create(follower=follower, user=user)
            new_follower.save()

        return redirect('/profile/' + user)
    else:
        return redirect('/')

@login_required(login_url='/login')
def delete(request,id):
    post=Post.objects.get(id=id)
    post.delete()
    return redirect('/profile/'+request.user.username)

@login_required(login_url='/login')
def search_results(request):
    query=request.GET.get('q')
    users=Profile.objects.filter(user__username__icontains=query)
    posts=Post.objects.filter(caption__icontains=query)
    context={
        'query':query,
        'users':users,
        'posts':posts,
    }

    return render(request,'search_user.html',context)