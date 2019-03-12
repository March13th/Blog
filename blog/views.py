from django.shortcuts import render_to_response, get_object_or_404
from  django.core.paginator import Paginator
from django.core.cache import cache
from .models import Blog, BlogType
from django.db.models import Count
from django.conf import settings
from read_statistics.utils import read_statistics_once_read, get_seven_days_read_data, get_today_hot_data, \
    get_yesterday_hot_data,get_7_days_hot_data
from django.contrib.contenttypes.models import ContentType


def get_blog_list_common_data(request, blog_all_list):
    paginator = Paginator(blog_all_list, settings.EACH_PAGE_BLOGS_NUMBER)  # 每7篇分一页
    page_num = request.GET.get('page', 1)  # 获取url页面参数
    page_of_blogs = paginator.get_page(page_num)
    current_page_num = page_of_blogs.number  # 获取当前页码
    page_range = [x for x in range(current_page_num - 2, current_page_num + 3) if
                  0 < x <= paginator.num_pages]  # .num_pages是总页数

    # 加上省略号标记
    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    # 加上首页尾页
    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    # 获取博客分类的对应博客数量
    # BlogType.objects.annotate(blog_count=Count('blog'))
    '''blog_types = BlogType.objects.all()
    blog_types_list = []
    for blog_type in blog_types:
        blog_type.blog_count = Blog.objects.filter(blog_type=blog_type).count()
        blog_types_list.append(blog_type)
    '''

    # 获取日期归档对应的博客数量
    blog_dates = Blog.objects.dates('created_time', 'month', order='DESC')
    blog_dates_dict = {}
    for blog_date in blog_dates:
        blog_count = Blog.objects.filter(created_time__year=blog_date.year,
                                         created_time__month=blog_date.month).count()
        blog_dates_dict[blog_date] = blog_count

    context = {}
    context['blogs'] = page_of_blogs.object_list
    context['page_of_blogs'] = page_of_blogs
    context['page_range'] = page_range
    context['blogs_type'] = BlogType.objects.annotate(blog_count=Count('blog'))
    context['blog_dates'] = blog_dates_dict
    return context


def home(request):
    blog_content_type = ContentType.objects.get_for_model(Blog)
    dates, read_nums = get_seven_days_read_data(blog_content_type)

    #获取7天热门博客的缓存数据
    hot_blogs_gor_7_days = cache.get('hot_blogs_for_7_days')
    if hot_blogs_gor_7_days is None:
        hot_blogs_gor_7_days = get_7_days_hot_data()
        cache.set('hot_blogs_for_7_days',hot_blogs_gor_7_days,3600)





    blog_all_list = Blog.objects.all()
    context = get_blog_list_common_data(request, blog_all_list)
    context['dates'] = dates
    context['read_nums'] = read_nums
    context['today_hot_data'] = get_today_hot_data(blog_content_type)
    context['yesterday_hot_data'] = get_yesterday_hot_data(blog_content_type)
    context['hot_blogs_for_7_days'] = get_7_days_hot_data()

    return render_to_response('home.html', context)


def contact(request):
    return render_to_response('contact.html')

def lulu(request):
    return render_to_response('lulu.html')

def blog_list(request):
    blog_all_list = Blog.objects.all()
    context = get_blog_list_common_data(request, blog_all_list)
    return render_to_response('blog_list.html', context)


def blogs_with_type(request, blog_type_pk):
    blog_type = get_object_or_404(BlogType, pk=blog_type_pk)
    blog_all_list = Blog.objects.filter(blog_type=blog_type)

    context = get_blog_list_common_data(request, blog_all_list)
    context['blog_type'] = blog_type
    return render_to_response('blog/blogs_with_type.html', context)


def blogs_with_date(request, year, month):
    blog_all_list = Blog.objects.filter(created_time__year=year, created_time__month=month)
    context = get_blog_list_common_data(request, blog_all_list)
    context['blogs_with_date'] = '{}年{}月'.format(year, month)
    return render_to_response('blogs_with_date.html', context)


def blog_detail(request, blog_pk):
    blog = get_object_or_404(Blog, pk=blog_pk)
    read_cookie_key = read_statistics_once_read(request, blog)
    context = {}
    context['previous_blog'] = Blog.objects.filter(created_time__gt=blog.created_time).last()
    context['next_blog'] = Blog.objects.filter(created_time__lt=blog.created_time).first()
    context['blog'] = blog
    response = render_to_response('blog/blog_detail.html', context)  # 响应
    response.set_cookie('blog_{}_read'.format(blog_pk), 'true')  # 阅读cookie标记
    return response
