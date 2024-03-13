from django.shortcuts import render, redirect
from .models import Post, Comment, Tag  
from .forms import CommentForm, PostForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User 
from django.views.generic import DetailView


def job_list(request):
# 검색 q가 있을 경우 title과 content에서 해당 내용이 있는지 검색
    q = request.GET.get("q", "")
    if q:
        posts = Post.objects.filter(title__contains=q) | Post.objects.filter(
            content__contains=q
        )
        return render(request, "jobs/job_list.html", {"posts": posts, "q": q})
    posts = Post.objects.all()
    return render(request, "jobs/job_list.html", {"posts": posts})


def job_detail(request, pk):
    post = Post.objects.get(pk=pk)
    form = CommentForm()
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            author = request.user
            message = form.cleaned_data["message"]
            c = Comment.objects.create(author=author, message=message, post=post)
            c.save()
    if request.method == "GET":
        post.view_count += 1
        post.save()
    return render(request, "jobs/job_detail.html", {"post": post, "form": form})


@login_required
def job_create(request):
    if request.method == "POST":
        title = request.POST["title"]
        company = request.POST["company"]
        content = request.POST["content"]
        close_date = request.POST["close_date"]
        # author_id를 추가
        author = request.user
        post = Post.objects.create(title=title, content=content, author=author, company=company)
        post.save()
        return redirect("jobs/job_list")
    return render(request, "jobs/job_create.html")


def job_update(request, pk):
    post = Post.objects.get(pk=pk)
    # 내가 쓴 게시물만 업데이트 가능
    if post.author != request.user:
        return redirect("jobs")
    if request.method == "GET":
        return render(request, "jobs/job_update.html", {"post": post})
    if request.method == "POST":
        title = request.POST["title"]
        content = request.POST["content"]
        post.title = title
        post.content = content
        post.save()
    return redirect("jobs/<int:pk>/", pk)


@login_required
def job_delete(request, pk):
    post = Post.objects.get(pk=pk)
    # 내가 쓴 게시물만 삭제 가능
    if post.author != request.user:
        return redirect("jobs/job_list")
    if request.method == "POST":
        post.delete()
    return redirect("jobs/job_list")


def job_tag(request, tag):
    posts = Post.objects.filter(tags__name__iexact=tag)
    return render(request, "jobs/job_list.html", {"posts": posts})
