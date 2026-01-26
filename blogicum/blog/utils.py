from django.core.paginator import Paginator, Page


def paginate_page(request, post_list, posts_per_page=10) -> Page:
    paginator = Paginator(post_list, posts_per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
