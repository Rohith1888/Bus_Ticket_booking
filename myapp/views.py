from django.shortcuts import render
from decimal import Decimal

# Create your views here.
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .models import User, Bus, Book
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .forms import UserLoginForm, UserRegisterForm
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from django.utils import timezone


def home(request):
    if request.user.is_authenticated:
        return render(request, 'myapp/home.html')
    else:
        return render(request, 'myapp/signin.html')


from django.shortcuts import render
from django.utils import timezone


@login_required(login_url='signin')
def findbus(request):
    context = {}
    if request.method == 'POST':
        source_r = request.POST.get('source')
        dest_r = request.POST.get('destination')
        date_r = request.POST.get('date')

        # Convert string date to datetime.date object if necessary
        # Assuming date_r is in 'YYYY-MM-DD' format
        try:
            input_date = timezone.datetime.strptime(date_r, '%Y-%m-%d').date()
        except ValueError:
            context["error"] = "Invalid date format. Please use YYYY-MM-DD."
            return render(request, 'myapp/findbus.html', context)

        # Check if the input date is not older than the current date
        if input_date < timezone.now().date():
            context["error"] = "Cannot search for buses on a past date."
            return render(request, 'myapp/findbus.html', context)

        # Fetch buses that match the criteria
        bus_list = Bus.objects.filter(source=source_r, dest=dest_r, date=date_r)
        if bus_list.exists():
            context["bus_list"] = bus_list
            return render(request, 'myapp/list.html', context)
        else:
            context["error"] = "Sorry, no buses available for the selected criteria."
            return render(request, 'myapp/findbus.html', context)
    elif 'avl' in request.GET:  # Check if "Available Buses" button is clicked
        # Fetch all available buses for the current date
        current_date = timezone.now().date()
        bus_list = Bus.objects.filter(date=current_date)
        if bus_list.exists():
            context["bus_list"] = bus_list
            return render(request, 'myapp/list.html', context)
        else:
            context["error"] = "No buses available for the current date."
            return render(request, 'myapp/list.html', context)
    else:
        return render(request, 'myapp/findbus.html')





from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from .models import Bus, Book

@login_required(login_url='signin')
def bookings(request):
    context = {}
    if request.method == 'POST':
        id_r = request.POST.get('bus_id')
        seats_r = request.POST.get('num_seats')

        # Check if the bus_id is provided and not empty
        if not id_r:
            context["error"] = "Bus ID is required."
            return render(request, 'myapp/findbus.html', context)

        try:
            seats_r = int(seats_r)
        except (TypeError, ValueError):
            context["error"] = "Invalid number of seats."
            return render(request, 'myapp/findbus.html', context)

        if seats_r > 6:
            context["error"] = "Sorry, you can book a maximum of 6 seats at once."
            return render(request, 'myapp/findbus.html', context)

        try:
            bus = Bus.objects.get(id=id_r)
        except Bus.DoesNotExist:
            context["error"] = "Invalid bus ID."
            return render(request, 'myapp/findbus.html', context)

        if bus and bus.rem >= seats_r:
            name_r = bus.bus_name
            cost = seats_r * bus.price
            source_r = bus.source
            dest_r = bus.dest
            nos_r = Decimal(bus.nos)
            price_r = bus.price
            date_r = bus.date
            time_r = bus.time
            username_r = request.user.username
            email_r = request.user.email
            userid_r = request.user.id
            rem_r = bus.rem - seats_r
            Bus.objects.filter(id=id_r).update(rem=rem_r)
            book = Book.objects.create(name=username_r, email=email_r, userid=userid_r, bus_name=name_r,
                                       source=source_r, busid=id_r,
                                       dest=dest_r, price=price_r, nos=seats_r, date=date_r, time=time_r,
                                       status='BOOKED')
            book.save()
            return render(request, 'myapp/bookings.html', context)
        else:
            context["error"] = "Sorry, there are not enough seats available for the selected bus."
            return render(request, 'myapp/findbus.html', context)
    else:
        return render(request, 'myapp/findbus.html', context)


@login_required(login_url='signin')
def cancellings(request):
    context = {}
    if request.method == 'POST':
        id_r = request.POST.get('bus_id')
        #seats_r = int(request.POST.get('no_seats'))

        try:
            book = Book.objects.get(id=id_r)
            bus = Bus.objects.get(id=book.busid)
            rem_r = bus.rem + book.nos
            Bus.objects.filter(id=book.busid).update(rem=rem_r)
            #nos_r = book.nos - seats_r
            Book.objects.filter(id=id_r).update(status='CANCELLED')
            Book.objects.filter(id=id_r).update(nos=0)
            return redirect(seebookings)
        except Book.DoesNotExist:
            context["error"] = "Sorry You have not booked that bus"
            return render(request, 'myapp/error.html', context)
    else:
        return render(request, 'myapp/findbus.html')


@login_required(login_url='signin')
def seebookings(request,new={}):
    context = {}
    id_r = request.user.id
    book_list = Book.objects.filter(userid=id_r)
    if book_list:
        return render(request, 'myapp/booklist.html', locals())
    else:
        context["error"] = "Sorry no buses booked"
        return render(request, 'myapp/findbus.html', context)


def signup(request):
    context = {}
    if request.method == 'POST':
        name_r = request.POST.get('name')
        email_r = request.POST.get('email')
        password_r = request.POST.get('password')
        user = User.objects.create_user(name_r, email_r, password_r)
        if user:
            login(request, user)
            return render(request, 'myapp/thank.html')
        else:
            context["error"] = "Provide valid credentials"
            return render(request, 'myapp/signup.html', context)
    else:
        return render(request, 'myapp/signup.html', context)


def signin(request):
    context = {}
    if request.method == 'POST':
        name_r = request.POST.get('name')
        password_r = request.POST.get('password')
        if name_r == 'admin' and password_r == 'admin':
            # Redirect to the admin dashboard URL
            return redirect('admin/login')
        user = authenticate(request, username=name_r, password=password_r)
        if user:
            login(request, user)
            # username = request.session['username']
            context["user"] = name_r
            context["id"] = request.user.id
            return render(request, 'myapp/success.html', context)
            # return HttpResponseRedirect('success')
        else:
            context["error"] = "Provide valid credentials"
            return render(request, 'myapp/signin.html', context)
    else:
        context["error"] = "You are not logged in"
        return render(request, 'myapp/signin.html', context)


def signout(request):
    context = {}
    logout(request)
    context['error'] = "You have been logged out"
    return render(request, 'myapp/signin.html', context)


def success(request):
    context = {}
    context['user'] = request.user
    return render(request, 'myapp/success.html', context)


def admin_dash(request):
    return render(request, template_name='myapp/admin_home.html')

# views.py

from django.shortcuts import render, redirect


from django.shortcuts import render, redirect

from django.shortcuts import render, redirect

from django.shortcuts import redirect
from django.shortcuts import render

def seat_confirmation(request):
    if request.method == 'POST':
        bus_id = request.POST.get('bus_id')
        request.session['bus_id'] = bus_id
        return redirect('seat_selection', bus_id=bus_id)
    else:
        # If it's a GET request, retrieve the bus_id from the session (if it exists)
        bus_id = request.session.get('bus_id')
        # Pass the bus_id to the template context
        context = {'bus_id': bus_id}
        return render(request, 'myapp/seat_confirmation.html', context)



from django.shortcuts import render

def seat_selection(request, bus_id):
    # Your view logic here
    return render(request, 'myapp/seat_selection.html')





