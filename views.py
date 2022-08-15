from django.shortcuts import render, get_object_or_404
from .models import Review, Movie

from .form import ReviewForm
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.models import User
import datetime

from django.contrib.auth import logout
from django.shortcuts import redirect

from django.views import generic
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth.models import User
import pandas as pd
import numpy as np
import scipy as sp
from sklearn.neighbors import NearestNeighbors

def review_list(request):
    latest_review_list = Review.objects.order_by('-pub_date')[:9]
    context = {'latest review list':latest_review_list}
    return render(request, 'review_list.html', context)

def review_detail(request, pk):
    review = get_object_or_404(Review, id=pk)
    return render(request, 'review_detail.html', {'review': review})

def movie_list(request):
    movie_list = Movie.objects.order_by('-title')[:20]
    context = {'movie_list':movie_list}
    return render(request, 'movie_list.html', context)

def movie_detail(request, pk):
    movie = get_object_or_404(Movie, id=pk)
    form = ReviewForm()
    return render(request, 'movie_detail.html', {'movie': movie})

def add_review(request, pk):
    movie = get_object_or_404(Movie, id= pk)
    form = ReviewForm(request.POST)
    if form.is_valid():
        rating = form.cleaned_data['rating']
        comment = form.cleaned_data['comment']
        user_name = form.cleaned_data['user_name']
        review = Review()
        review.movie = movie
        review.user_name = user_name
        review.rating = rating
        review.comment = comment
        review.pub_date = datetime.datetime.now()
        review.save()
        return HttpResponseRedirect(reverse('movie_detail', args=(movie.id)))
    return render(request, 'movie_detail.html', {'movie': movie, 'form': form})  

def logout_view(request):
    logout(request)
    return redirect('/')

class SignUp(generic.CreateView):
    form_class = UserCreationForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('login')
def get_suggestions(request):
    num_reviews = Review.objects.count()
    all_user_names = set(map(lambda x: x.id, User.objects.only("id")))
    all_movie_ids = set(map(lambda x: x.movie.id, Review.objects.only("movie")))
    num_users = len(list(all_user_names)) 
    movieRatings_m = Review.objects.filter(user_id=all_user_names[i])
    for i in range(num_users): #each user corresponds to row, in the order of all user names
        user_reviews = Review>objects.filter(user_id=all_user_names[i])
        for user_review in user_reviews:
            movieRatings_m[i,user_review.movie.id] = user_review.rating
    movieRatings = movieRatings_m.transpose()
    coo = movieRatings.tocoo(copy=false)
    df = pd.DataFrame({'movies': coo.row, 'users': coo.col, 'rating': coo.data})[['movies', 'users','rating']].sort_values(['movies','users']).reset_index(drop=True)
    mo = df.pivot_table(index=['movies'], columns=['users'], values='rating')
    mo.replace({np.nan: 0}, regex=True, inplace=True)
    model_knn = NearestNeighbors(algorithm='brute', metric='cosine',n_neighbor=5)
    model.knn.fit(mo.values)
    distances, indices = model_knn.kneighbors(mo.iloc[100,:].reshape(1,-1),return_distance=True)
    context = list(map(lambda x: Movie.objects.get(id=indices.flatten()[x]),range(0, len(distances.flatten()))))
    return render(request, 'get_suggestions.html',{'context':context})