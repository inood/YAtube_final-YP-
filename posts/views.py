from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, NewPostForm
from .models import Comment, Follow, Group, Post, User


def index(request):
	post_list = Post.objects.all()
	paginator = Paginator(post_list, 10)

	page_number = request.GET.get('page')
	page = paginator.get_page(page_number)
	return render(
		request,
		'index.html', {'page': page, 'paginator': paginator}
	)


def group_posts(request, slug):
	group = get_object_or_404(Group, slug=slug)
	posts = group.group_posts.order_by('-pub_date').all()
	paginator = Paginator(posts, 10)

	page_number = request.GET.get('page')
	page = paginator.get_page(page_number)
	context = {
		'group': group,
		'page': page,
		'paginator': paginator
	}

	return render(request, 'group.html', context)


def post_retrieve(request, username, post_id):
	author = get_object_or_404(User, username=username)
	post = get_object_or_404(author.author_posts, id=post_id)

	comments = post.comment_post.all()
	form = CommentForm()
	context = {
		'post': post,
		'author': author,
		'form': form,
		'comments': comments
	}

	return render(request, 'post.html', context)


@login_required()
def new_post_view(request):
	if request.method == 'POST':
		form = NewPostForm(request.POST, files=request.FILES or None)
		if form.is_valid():
			post = form.save(commit=False)
			post.author = request.user
			post.save()
			return redirect('index')
		return render(request, 'post_new.html', {'form': form})
	return render(request, 'post_new.html', {'form': NewPostForm()})


@login_required
def post_edit_view(request, username, post_id):
	author = get_object_or_404(User, username=username)
	post = get_object_or_404(author.author_posts, id=post_id)

	context = {}

	if request.user != author:
		return redirect('post_retrieve', username=username, post_id=post_id)

	if request.method == 'POST':
		form = NewPostForm(
			request.POST,
			files=request.FILES or None,
			instance=post)
		if form.is_valid():
			form.save()
			return redirect(
				"post_retrieve", username=username,
				post_id=post_id)

		context['form'] = form
		return render(request, 'post_new.html', context)

	context['form'] = NewPostForm(instance=post)
	context['post'] = post
	return render(request, 'post_new.html', context)


def profile(request, username):
	author = get_object_or_404(User, username=username)
	posts = author.author_posts.order_by('-pub_date')
	paginator = Paginator(posts, 10)

	page_number = request.GET.get('page')
	page = paginator.get_page(page_number)
	is_following = request.user.is_authenticated and Follow.objects.filter(
		user=request.user, author=author
	).exists()
	context = {
		'author': author,
		'page': page,
		'paginator': paginator,
		'is_following': is_following
	}
	return render(request, 'profile.html', context)


def page_not_found(request, exception):
	return render(
		request,
		"misc/404.html",
		{"path": request.path}, status=404
	)


def server_error(request):
	return render(request, "misc/500.html", status=500)


@login_required()
def add_comment(request, username, post_id):
	post = get_object_or_404(Post, id=post_id)

	if request.method == 'POST':
		form = CommentForm(request.POST)
		if form.is_valid():
			comment = form.save(commit=False)
			comment.post = post
			comment.author = request.user
			comment.save()
			return redirect('post_retrieve', username=username, post_id=post_id)
		return render(
			request, 'comments.html',
			{'form': form, 'post': post})
	form = CommentForm()
	return render(request, 'comments.html', {'form': form, 'post': post})


@login_required
def follow_index(request):

	post_list = Post.objects.order_by("-pub_date").filter(
		author__following__user=request.user).all()
	paginator = Paginator(post_list, 10)

	page_number = request.GET.get('page')
	page = paginator.get_page(page_number)
	return render(
		request,
		'follow.html',
		{'page': page, 'paginator': paginator})


@login_required
def profile_follow(request, username):
	if not request.user == get_object_or_404(User, username=username):
		Follow.objects.get_or_create(
			user=request.user,
			author=get_object_or_404(User, username=username)
		)
	return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
	follow = Follow.objects.get(
		author__username=username,
		user=request.user
	)
	follow.delete()
	return redirect('profile', username=username)
