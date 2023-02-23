from markdown.extensions.toc import TocExtension
from django.utils.text import slugify
import markdown
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .models import Post, Category, Tag

from django import forms


class PostModelForm(forms.ModelForm):
    class Meta:
        model = Post
        # fields = '__all__'
        exclude = ['views', 'modified_time', 'created_time']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs = {"class": "form-control", "placeholder": field.label}


class CategoryModelForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super(CategoryModelForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs = {"class": "form-control", "placeholder": field.label}


# def index(request):
#     latest = Post.objects.order_by("-modified_time")
#     return render(request, "post_index.html", {"post_list": latest})


class PostIndexView(ListView):
    model = Post    # queryset = Post.objects.all()
    queryset = Post.objects.order_by('-modified_time')  # decreasing order
    template_name = 'post_index.html'
    context_object_name = 'post_list'
    paginate_by = 3

    def get_context_data(self, **kwargs):
        """
            add pagination context
        """
        context = super(PostIndexView, self).get_context_data(**kwargs)
        paginator = context.get('paginator')
        page = context.get('page_obj')
        is_paginated = context.get('is_paginated')

        pagination_data = self.paginate_data(paginator, page, is_paginated)

        context.update(pagination_data)

        return context

    def paginate_data(self, paginator, page, is_paginated):
        if not is_paginated:
            return {}   # not pagination bar
        # first, left_has_more, [left], current, [right], right_has_more, last
        # <<, 1, ..., 12, 13, [14], 15, 16, ..., 20, >>

        left = []
        right = []

        left_has_more = False
        right_has_more = False
        first = False
        last = False

        page_number = page.number
        total_pages = paginator.num_pages
        page_range = paginator.page_range

        if page_number == 1:
            # [[1], 2, 3, 4, 5]
            right = page_range[page_number:page_number+2]   # [2, 3]
            if right[-1] < total_pages - 1:
                right_has_more = True   # [2, 3, ...]
            if right[-1] < total_pages:
                last = True     # [2, 3, ..., 5]
        elif page_number == total_pages:
            left = page_range[(page_number - 3) if (page_number - 3) > 0 else 0:page_number - 1]    # [3, 4]
            if left[0] > 2:
                left_has_more = True    # [..., 3, 4]
            if left[0] > 1:
                first = True    # [1, ..., 3, 4]
        else:
            left = page_range[(page_number - 3) if (page_number - 3) > 0 else 0:page_number - 1]
            right = page_range[page_number:page_number + 2]

            if right[-1] < total_pages - 1:
                right_has_more = True
            if right[-1] < total_pages:
                last = True

            if left[0] > 2:
                left_has_more = True
            if left[0] > 1:
                first = True
        data = {
            'left': left,
            'right': right,
            'left_has_more': left_has_more,
            'right_has_more': right_has_more,
            'first': first,
            'last': last,
        }
        return data


# def post_detail(request, pk):
#     post = get_object_or_404(Post, pk=pk)
#     post.increase_views()
#     post.body = markdown.markdown(post.body,
#                                   extensions=[
#                                       'markdown.extensions.extra',
#                                       'markdown.extensions.codehilite',
#                                       'markdown.extensions.toc',
#                                   ])
#     # comment form
#     # comment list
#     context = {'post': post}
#     return render(request, "post_detail.html", context=context)


class PostDetailView(DetailView):
    # DetailView help us to get post data by pk
    model = Post
    template_name = "post_detail.html"
    context_object_name = "post"

    def get(self, request, *args, **kwargs):
        """
            rewrite to call increase_views()
        """
        response = super(PostDetailView, self).get(request, *args, **kwargs)
        self.object.increase_views()    # self.object -> post
        return response

    def get_object(self, queryset=None):
        """
            rewrite to call use markdown
        """
        post = super(PostDetailView, self).get_object(queryset=None)
        md = markdown.Markdown(extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            TocExtension(slugify=slugify),
        ])
        post.body = md.convert(post.body)
        post.toc = md.toc
        return post

    # def get_context_data(self, **kwargs):
    #     comment list


# def new(request):
#     if request.method == "GET":     # default page
#         form = PostModelForm()
#         return render(request, "post_create.html", {'form': form})
#     form = PostModelForm(data=request.POST)
#     if form.is_valid():
#         form.save()
#         return redirect("/")
#     return render(request, "post_create.html", {'form': form})  # with error information


class PostCreateForm(CreateView):
    def get(self, request, *args, **kwargs):
        # form is filled with default value
        form = PostModelForm()
        return render(request, "post_create.html", {'form': form})

    def post(self, request, *args, **kwargs):
        form = PostModelForm(data=request.POST)
        if form.is_valid():
            post = form.save()  # important
            post.category.increase_number()
            return redirect('/post')
        return render(request, "post_create.html", {'form': form})  # with error information


# def edit(request, pk):
#     """
#         edit post
#     """
#     row = Post.objects.filter(id=pk).first()
#     if request.method == "GET":
#         form = PostModelForm(instance=row)
#         return render(request, "post_update.html", {"form": form})
#     form = PostModelForm(data=request.POST, instance=row)    # update instead of create
#     if form.is_valid():
#         form.save()
#         return redirect("/")
#     return render(request, "post_create.html", {'form': form})  # with error information


class PostUpdateView(UpdateView):
    model = Post
    template_name = 'post_update.html'
    form_class = PostModelForm

    def get(self, request, *args, **kwargs):
        row = Post.objects.get(id=self.kwargs['pk'])
        form = self.form_class(instance=row)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        row = Post.objects.get(id=self.kwargs['pk'])
        form = PostModelForm(request.POST, instance=row)
        if form.is_valid():
            post = form.save()
            return redirect('/post')
        return render(request, "post_create.html", {'form': form})  # with error information


# def delete(request, pk):
#     Post.objects.filter(id=pk).delete()
#     return redirect("/")


class PostDeleteView(DeleteView):
    def get(self, request, *args, **kwargs):
        post = Post.objects.filter(id=self.kwargs['pk'])
        post.category.decrease_number()
        post.delete()
        return redirect('/post')


# def category(request):
#     """
#         show all the categories
#     """
#     if request.method == "GET":
#         form = CategoryModelForm()
#         category_list = Category.objects.order_by('name')
#         return render(request, "category_index.html", {'category_list': category_list, 'form': form})
#     form = CategoryModelForm(data=request.POST)
#     if form.is_valid:
#         form.save()
#         return redirect('/category')
#     return render(request, "category_index.html", {'form': form})  # with error information


class CategoryIndexView(ListView):
    model = Category
    template_name = 'category_index.html'
    context_object_name = 'category_list'


# def category_detail(request, category_name):
#     """
#         show all the posts with certain category
#     """
#     category_ = Category.objects.filter(category=category_name).first()
#     row = Post.objects.filter(category=category_)
#     return render(request, "category_detail.html", {'category': category_, 'post_list': row})

class CategoryDetailView(DetailView):
    model = Category
    template_name = 'category_detail.html'
    context_object_name = 'category'

    def get_context_data(self, **kwargs):
        context = super(CategoryDetailView, self).get_context_data(**kwargs)
        context['post_list'] = Post.objects.filter(category=self.object)
        return context


class CategoryCreateView(CreateView):
    model = Category
    template_name = 'category_create.html'

    def get(self, request, *args, **kwargs):
        # form is filled with default value
        form = CategoryModelForm()
        return render(request, "category_create.html", {'form': form})

    def post(self, request, *args, **kwargs):
        form = CategoryModelForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('/category')
        return render(request, "category_create.html", {'form': form})  # with error information


# def delete_category(request, pk):
#     """
#         **remove all the posts with this category
#     """
#     Category.objects.filter(id=pk).delete()
#     return redirect("category")

class CategoryDeleteView(DeleteView):
    def get(self, request, *args, **kwargs):
        Category.objects.filter(id=self.kwargs['pk']).delete()
        return redirect('/category')


def search_view(request):
    keyword = request.GET.get('keyword')
    post_list = Post.objects.filter(title__icontains=keyword)
    return render(request, "search.html", {'post_list': post_list})


