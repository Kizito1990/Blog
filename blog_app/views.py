from django.shortcuts import render, get_object_or_404,  redirect
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView,DetailView, CreateView, UpdateView, DeleteView
from .models import Post, Comment
from users.forms import CommentForm



def home(request):
    context = {
        'posts':Post.objects.all()
    }
    return render(request, 'blog_app/home.html', context)

class PostListView(ListView):
    model = Post
    template_name = 'blog_app/home.html'
    context_object_name = 'posts'
    paginate_by = 5

#view the list of posts by a user
class UserPostListView(ListView):
    model = Post
    template_name = 'blog_app/user_posts.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        # Retrieve the user by username from the URL
        username = self.kwargs.get('username')
        user = get_object_or_404(User, username=username)
        # Return the posts made by the user
        return Post.objects.filter(author=user).order_by('-date_posted')  

    #def get_queryset(self): #gets the total posts made per or by user
        #user = get_list_or_404(User, username = self.kwargs.get("username"))
        #return Post.objects.filter(author = user).order_by("-date_posted")

class PostDetailView(DetailView):
    model = Post
#Added a comment section
    
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    
class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False
    

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'
    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False
    

def about(request):
    return render(request, 'blog_app/about.html')

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.all()  # Get all comments for the post
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user  # Assign the currently logged-in user
            comment.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()
    return render(request, 'blog/post_detail.html', {'post': post, 'comments': comments, 'form': form})