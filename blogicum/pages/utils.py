from django.core.paginator import Paginator, Page


def paginate_page(request, object_list, items_per_page=10) -> Page:
    paginator = Paginator(object_list, items_per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
