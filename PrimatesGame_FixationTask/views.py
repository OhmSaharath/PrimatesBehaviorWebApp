from django.shortcuts import render

# Create your views here.
def game_view(request, gameinstance):
    return render(request, "fixation.html")
