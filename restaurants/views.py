from django.shortcuts import render, redirect
from .models import Restaurant, Menu
from reviews.models import Review, ReviewPhoto
from reviews.forms import Review
from .forms import RestaurantForm, MenuForm
from reviews.forms import ReviewForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, Avg, Q
from django.utils.html import escape
from django.utils.safestring import mark_safe
import os
from dotenv import load_dotenv


load_dotenv()
KAKAO_JS_KEY = os.getenv('KAKAO_JS_KEY')


# Create your views here.
def index(request):
    # Restaurant 평균 평점 갱신
    avg_restaurants = Restaurant.objects.annotate(avg_rate=Avg('review__rate'))
    for restaurant in avg_restaurants:
        if restaurant.avg_rate:
            restaurant.rate = round(restaurant.avg_rate, 1)
            restaurant.save()
    # for restaurant in restaurants:
    #     reviews_averagerate = Review.objects.filter(restaurant_id=restaurant.pk).aggregate(Avg('rate'))['rate__avg']
    #     rt = Restaurant.objects.get(pk=restaurant.pk)
    #     rt.rate = round(reviews_averagerate, 1)
    #     rt.save()
    # Restaurant thumbnail 갱신
    restaurants = Restaurant.objects.all()
    cate_restaurants = Restaurant.objects.all().order_by('category')
    region_restaurants = Restaurant.objects.all().order_by('region')
    flag = False
    for restaurant in restaurants:
        flag = False
        for review in restaurant.review_set.all():
            if flag == True:
                    break    
            for reviewphoto in review.reviewphoto_set.all():
                if reviewphoto.image_review:
                    restaurant.image_first = reviewphoto.image_review
                    restaurant.save()
                    flag = True
                    break
    rankings = restaurants.order_by('-rate')[:12]
    eatdeals = Restaurant.objects.filter(eatdeal=True).order_by('-rate')[:12]
    context = {
        'restaurants': restaurants,
        'eatdeals': eatdeals,
        'rankings': rankings,
        'cate_restaurants': cate_restaurants,
        'region_restaurants': region_restaurants,
    }
    return render(request, 'restaurants/index.html', context)

@login_required
def create(request):
    if request.method == 'POST':
        restaurant_form = RestaurantForm(request.POST)
        if restaurant_form.is_valid():
            restaurant = restaurant_form.save(commit=False)
            restaurant.user = request.user
            restaurant.save()
            return redirect('restaurants:detail', restaurant.pk)
    else:
        restaurant_form = RestaurantForm()
    context = {
        'restaurant_form': restaurant_form,
    }
    return render(request, 'restaurants/create.html', context)

def detail(request, restaurant_id):
    restaurant = Restaurant.objects.get(pk=restaurant_id)
    restaurant.views = restaurant.views + 1
    restaurant.save()
    
    menus = restaurant.menu_set.all()

    reviews = Review.objects.filter(restaurant_id=restaurant_id)
    select_rate = request.GET.get('rate')

    # review_counts = reviews.filter(rate__in=[1, 3, 5]).values('rate').annotate(count=Count('id'))
    review_counts = reviews.values('rate').annotate(count=Count('id'))
    review_count_1, review_count_3, review_count_5 = 0, 0, 0
    for review in review_counts:
        if review['rate'] == 1:
            review_count_1 = review['count']
        elif review['rate'] == 3:
            review_count_3 = review['count']
        elif review['rate'] == 5:
            review_count_5 = review['count']
    # review_count_1 = next((r['count'] for r in review_counts if r['rate'] == 1), 0)
    # review_count_3 = next((r['count'] for r in review_counts if r['rate'] == 3), 0)
    # review_count_5 = next((r['count'] for r in review_counts if r['rate'] == 5), 0)
    # print(review_counts)

    reviews_filter = review_filter(reviews, select_rate)
    
    # 리뷰 평균 
    reviews_averagerate = Review.objects.filter(restaurant_id=restaurant_id).aggregate(Avg('rate'))['rate__avg']
    menu_form = MenuForm()
    review_form = ReviewForm()
    context = {
        'restaurant': restaurant,
        'menus': menus,
        'reviews': reviews,
        'menu_form': menu_form,
        'review_form': review_form,
        'reviews_averagerate': reviews_averagerate,
        
        'reviews_filter': reviews_filter,
        'review_count_5': review_count_5,
        'review_count_3': review_count_3,
        'review_count_1': review_count_1,

        'KAKAO_JS_KEY': KAKAO_JS_KEY,
    }
    return render(request, 'restaurants/detail.html', context)

def review_filter(queryset, rate):
    if rate:
        return queryset.filter(rate=int(rate))
    else:
        return queryset

@login_required
def delete(request, restaurant_id):
    restaurant = Restaurant.objects.get(pk=restaurant_id)
    if request.user == restaurant.user:
        restaurant.delete()
    return redirect('restaurants:index')

@login_required
def menu(request, restaurant_id):
    restaurant = Restaurant.objects.get(pk=restaurant_id)
    menu_form = MenuForm(request.POST)
    if menu_form.is_valid():
        menu = menu_form.save(commit=False)
        menu.restaurant = restaurant
        menu.user = request.user
        menu.save()
        return redirect('restaurants:detail', restaurant.pk)
    context = {
        'restaurant': restaurant,
        'menu_form': menu_form,
    }
    return render(request, 'restaurants/detail.html', context)

@login_required
def menu_delete(request, restaurant_id, menu_id):
    menu = Menu.objects.get(pk=menu_id)
    restaurant = Restaurant.objects.get(pk=restaurant_id)
    if request.user == restaurant.user:
        menu.delete()
    return redirect('restaurants:detail', restaurant_id)

@login_required
def wish(request, restaurant_id):
    restaurant = Restaurant.objects.get(pk=restaurant_id)
    if request.user in restaurant.wish_users.all():
        restaurant.wish_users.remove(request.user)
        is_wished = False
    else:
        restaurant.wish_users.add(request.user)
        is_wished = True
    context = {
        'is_wished': is_wished,
        'wish_count': restaurant.wish_users.count(),
    }
    return JsonResponse(context)

@login_required
def wish_srt(request, restaurant_id):
    restaurant = Restaurant.objects.get(pk=restaurant_id)
    if request.user in restaurant.wish_users.all():
        restaurant.wish_users.remove(request.user)
        is_wished = False
    else:
        restaurant.wish_users.add(request.user)
        is_wished = True
    context = {
        'is_wished': is_wished,
        'wish_count': restaurant.wish_users.count(),
    }
    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

def category(request, restaurant_category):
    restaurants = Restaurant.objects.all()
    for restaurant in restaurants:
        reviews_averagerate = Review.objects.filter(restaurant_id=restaurant.pk).aggregate(Avg('rate'))['rate__avg']
        rt = Restaurant.objects.get(pk=restaurant.pk)
        rt.rate = reviews_averagerate
        rt.save()
    category_restaurants = Restaurant.objects.filter(category=restaurant_category).order_by('-rate')
    reviews = Review.objects.all()
    context = {
            'restaurant_category': restaurant_category,
            'category_restaurants': category_restaurants,
            'reviews': reviews,
        }
    return render(request, 'restaurants/category.html', context)

def eatdeal(request):
    restaurants = Restaurant.objects.all()
    for restaurant in restaurants:
        reviews_averagerate = Review.objects.filter(restaurant_id=restaurant.pk).aggregate(Avg('rate'))['rate__avg']
        rt = Restaurant.objects.get(pk=restaurant.pk)
        rt.rate = reviews_averagerate
        rt.save()
    restaurants = Restaurant.objects.filter(eatdeal=True).order_by('-rate')
    reviews = Review.objects.all()
    context = {
        'restaurants': restaurants,
        'reviews': reviews,
    }
    return render(request, 'restaurants/eatdeal.html', context)

def region(request, restaurant_region):
    restaurants = Restaurant.objects.all()
    for restaurant in restaurants:
        reviews_averagerate = Review.objects.filter(restaurant_id=restaurant.pk).aggregate(Avg('rate'))['rate__avg']
        rt = Restaurant.objects.get(pk=restaurant.pk)
        rt.rate = reviews_averagerate
        rt.save()
    region_restaurants = Restaurant.objects.filter(region=restaurant_region).order_by('-rate')
    reviews = Review.objects.all()
    context = {
        'restaurant_region': restaurant_region,
        'region_restaurants': region_restaurants,
        'reviews': reviews,
    }
    return render(request, 'restaurants/region.html', context)

def search(request):
    restaurant_list = Restaurant.objects.all()
    search_text = request.GET.get('search')
    search_list = []
    if search_text:
        search_list = restaurant_list.filter(
            Q(name__icontains=search_text) |
            Q(menu__name__icontains=search_text) |
            Q(address__icontains=search_text)
        ).distinct()
    
        for search_item in search_list:
            search_item.name = mark_safe(search_item.name.replace(search_text, '<span class="text-color-main">{}</span>'.format(escape(search_text))))
            search_item.address = mark_safe(search_item.address.replace(search_text, '<span class="text-color-main">{}</span>'.format(escape(search_text))))

            menus = [escape(menu.name) for menu in search_item.menu_set.all()]
            menus_highlighted = [name.replace(search_text, '<span class="text-color-main">{}</span>'.format(escape(search_text))) for name in menus]
            search_item.menus = mark_safe(' / '.join(menus_highlighted))

    context = {
        'search_list': search_list,
        'search_text': search_text,
    }
    return render(request,'restaurants/search.html', context)