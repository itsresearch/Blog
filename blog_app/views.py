from django.shortcuts import render, redirect

from blog_app.models import Post
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from blog_app.forms import PostForm

from django.views.generic import ListView

from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.


class PostListView(ListView):
    model = Post
    template_name = "post_list.html"
    context_object_name = "posts"

    def get_queryset(self):
        posts = Post.objects.filter(published_at__isnull = False).order_by(
            "-published_at"
        )
        return posts
    
class PostDetailView(DetailView):
    model = Post
    template_name = "post_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        queryset = Post.objects.filter(pk = self.kwargs["pk"], published_at__isnull = False)
        return queryset

class DraftListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = "draft_list.html"
    context_object_name = "posts"

    def get_queryset(self):
        queryset = Post.objects.filter(published_at__isnull = True)
        return queryset
    
@login_required
def draft_detail(request,pk):
    post = Post.objects.get(pk=pk, published_at__isnull=True)
    return render(request, "draft_detail.html",{"post":post},)

@login_required
def draft_publish(request, pk):
    post = Post.objects.get(pk=pk, published_at__isnull = True)
    post.published_at = timezone.now()
    post.save()
    return redirect("post-list")

@login_required
def post_delete(request, pk):
    post=Post.objects.get(pk=pk)
    post.delete()
    return redirect("post-list")

@login_required
def post_create(request):
    if request.method =="GET":
        form =PostForm()
        return render(request, "post_create.html", {"form": form},)
    else:
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit = False)
            post.author = request.user
            post.save()
            return redirect("draft-detail", pk = post.pk)
        else:
            return render(request, "post_create.html", {"form": form},)
        
@login_required
def post_update(request, pk):
    if request.method == "GET":
        post = Post.objects.get(pk = pk)
        form = PostForm(instance = post)
        return render(request, "post_create.html", {"form": form},)
    
    else:
        post = Post.objects.get(pk = pk)
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save()
            if post.published_at:
                return redirect("post-detail", post.pk)
            else:
                return redirect("draft-detail", post.pk)
        else:
            return render(request, "post_create.html", {"form": form},)
