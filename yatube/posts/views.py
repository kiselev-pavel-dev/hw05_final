from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect

from yatube.settings import POSTS_ON_PAGE

from .models import Follow, Group, Post, User
from .forms import CommentForm, PostForm


def pagination(request, list):
    paginator = Paginator(list, POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    template = 'posts/index.html'
    posts_list = Post.objects.all()
    page_obj = pagination(request, posts_list)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts_list = group.posts.all()
    page_obj = pagination(request, posts_list)
    template = 'posts/group_list.html'
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(author=author)
    posts = author.posts.all()
    count_posts = posts.count()
    page_obj = pagination(request, posts)
    following = follow.exists() and request.user.is_authenticated
    context = {
        'posts': posts,
        'count': count_posts,
        'page_obj': page_obj,
        'author': author,
        'following': following
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    count_posts = post.author.posts.all().count()
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    context = {
        'post': post,
        'count': count_posts,
        'form': form,
        'comments': comments

    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', request.user)
    context = {
        'form': form
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    current_post = get_object_or_404(Post, pk=post_id)
    if current_post.author != request.user:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=current_post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'form': form,
        'is_edit': True
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = get_object_or_404(Post, pk=post_id)
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    template = "posts/follow.html"
    user = get_object_or_404(User, username=request.user)
    posts = Post.objects.filter(author__following__user=user).all()
    page_obj = pagination(request, posts)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(user=request.user, author=author).exists()
    if not follow and username != request.user.username:
        Follow.objects.create(user=request.user, author=author)
    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    query = Follow.objects.filter(user=request.user, author=author)
    follow = query.exists()
    if follow:
        query.delete()
    return redirect('posts:follow_index')
