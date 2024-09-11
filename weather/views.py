import requests
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import City, SearchHistory, FavoriteCity
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic

class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'
def get_weather_data(city):
    api_key = settings.OPENWEATHERMAP_API_KEY
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def index(request):
    if request.method == 'POST':
        city = request.POST.get('city')
        weather_data = get_weather_data(city)
        if weather_data:
            context = {
                'city': city,
                'temperature': weather_data['main']['temp'],
                'description': weather_data['weather'][0]['description'],
                'icon': weather_data['weather'][0]['icon'],
                'humidity': weather_data['main']['humidity'],
                'wind_speed': weather_data['wind']['speed'],
            }
            if request.user.is_authenticated:
                city_obj, _ = City.objects.get_or_create(
                    name=weather_data['name'],
                    country=weather_data['sys']['country']
                )
                SearchHistory.objects.create(user=request.user, city=city_obj)
            return render(request, 'weather/index.html', context)
    return render(request, 'weather/index.html')

@login_required
def search_history(request):
    history = SearchHistory.objects.filter(user=request.user).order_by('-search_date')
    return render(request, 'weather/search_history.html', {'history': history})

@login_required
def favorite_cities(request):
    favorites = FavoriteCity.objects.filter(user=request.user)
    return render(request, 'weather/favorite_cities.html', {'favorites': favorites})

@login_required
def add_favorite(request, city_id):
    city = City.objects.get(id=city_id)
    FavoriteCity.objects.get_or_create(user=request.user, city=city)
    return redirect('favorite_cities')

@login_required
def remove_favorite(request, city_id):
    city = City.objects.get(id=city_id)
    FavoriteCity.objects.filter(user=request.user, city=city).delete()
    return redirect('favorite_cities')