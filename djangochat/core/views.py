from django.contrib.auth import login
from django.shortcuts import render, redirect
from .forms import SignUpForm

def frontpage(request):
    return render(request, 'core/frontpage.html')

def signup(request):
    # if form has been submitted, create form instance and pass in request data
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        # if valid, save the user to the database
        if form.is_valid():
            user = form.save()
            # login user and redirect to frontpage
            login(request, user)
            return redirect('frontpage')
    # else just render empty form on the signup page
    else:
        form = SignUpForm()

    return render(request, 'core/signup.html', {'form': form})