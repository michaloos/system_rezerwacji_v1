from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import Building, Room, Software, Equipment, RoomType, Reservation, ReservationType, RoomKeeper, Coordinator
from .filters import RoomFilter
from django.db.models import Q, Count
from django.shortcuts import render, get_object_or_404, redirect
from .forms import NewUserForm, NewReservationForm, ChangeStatusReservationForm, NewRoomForm
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout


def is_valid_queryparam(param):
    return param != '' and param is not None


def user_is_room_keeper_in_selected_room(room, user):
    room_keeper = RoomKeeper.objects.filter(user=user, room=room)
    if room_keeper:
        return True
    else:
        return False


def user_is_coordinator_in_selected_building(building, user):
    coordinator = Coordinator.objects.filter(user=user, building=building)
    if coordinator:
        return True
    else:
        return False


def user_is_room_keeper(user):
    room_keeper = RoomKeeper.objects.filter(user=user)
    if room_keeper:
        return True
    else:
        return False


def user_is_coordinator(user):
    coordinator = Coordinator.objects.filter(user=user)
    if coordinator:
        return True
    else:
        return False


def cancel_reservation_by_user_request(request, pk):
    reservation_to_cancel = get_object_or_404(Reservation, pk=pk)
    user=request.user

    if user.is_staff:
        reservation_to_cancel.status= 'rejected'
        reservation_to_cancel.comment = 'User canceled this reservation'
        reservation_to_cancel.save()

    return redirect("rezerwacje:my_reservation")


def cancel_reservation(form, reservation_to_cancel, request):
    reservation_to_cancel.comment = form.cleaned_data.get('comment')
    reservation_to_cancel.status = 'rejected'
    reservation_to_cancel.save()
    messages.info(request, "You rejected reservation.")


def accept_reservation(reservation):
    reservation.status = 'accepted'
    reservation.comment = "reservation accepted"
    reservation.save()


def accept_reservation_by_roomkeeper_request(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    user=request.user
    room = reservation.room

    if user_is_room_keeper_in_selected_room(room, user):
        accept_reservation(reservation)
    return redirect('rezerwacje:room_keeper_management')


def accept_reservation_by_coordinator_request(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    user=request.user
    room = reservation.room
    building = room.building
    if user_is_coordinator_in_selected_building(building, user):
        accept_reservation(reservation)
    return redirect('rezerwacje:coordinator_management')


def disable_possibility_of_reserve_room(request, pk):
    room = get_object_or_404(Room, pk=pk)
    user=request.user
    building = room.building
    if user_is_coordinator_in_selected_building(building, user):
        room.available = False
        room.save()
    return redirect('rezerwacje:coordinator_management')


def enable_possibility_of_reserve_room(request, pk):
    room = get_object_or_404(Room, pk=pk)
    user=request.user
    building = room.building
    if user_is_coordinator_in_selected_building(building, user):
        room.available = True
        room.save()
    return redirect('rezerwacje:coordinator_management')



def cancel_reservation_by_roomkeeper_request(request, pk):
    reservation_to_cancel = get_object_or_404(Reservation, pk=pk)
    user=request.user
    room = reservation_to_cancel.room
    form = ChangeStatusReservationForm(instance=reservation_to_cancel, data=request.POST)

    if user_is_room_keeper_in_selected_room(room, user):
        if request.method == 'POST':
            if form.is_valid():
                cancel_reservation(form,reservation_to_cancel,request)
                return redirect('rezerwacje:room_keeper_management')
        else:
            form = ChangeStatusReservationForm(data=request.POST)

    return render(request, 'rezerwacje/reservation/change_status.html', {'form': form})


def cancel_reservation_by_coordinator_request(request, pk):
    reservation_to_cancel = get_object_or_404(Reservation, pk=pk)
    user=request.user
    room = reservation_to_cancel.room
    building = room.building
    form = ChangeStatusReservationForm(instance=reservation_to_cancel, data=request.POST)

    if user_is_coordinator_in_selected_building(building, user):
        if request.method == 'POST':
            if form.is_valid():
                cancel_reservation(form,reservation_to_cancel,request)
                return redirect('rezerwacje:coordinator_management')
        else:
            form = ChangeStatusReservationForm(data=request.POST)

    return render(request, 'rezerwacje/reservation/change_status.html', {'form': form})

def reservation_filter(request, reservations):

    room_name_query = request.GET.get('room_name')
    reservation_type = request.GET.get('type')
    reservation_status = request.GET.get('status')

    if is_valid_queryparam(room_name_query):
        reservations = reservations.filter(room__name = room_name_query, room__avaiable = True)

    if is_valid_queryparam(reservation_type) and reservation_type != 'Choose...':
        reservations = reservations.filter(type__name = reservation_type)

    if is_valid_queryparam(reservation_status) and reservation_status != 'Choose...':
        reservations = reservations.filter(status=reservation_status)

    return reservations


def get_context_to_filer_reservations(reservations):

    types = ReservationType.objects.all()
    status_options = dict((v, k) for k, v in Reservation.STATUS_CHOICES)
    context = {
        'reservations': reservations,
        'types': types,
        'status_options': status_options
    }

    return context


def room_filter(request, rooms):
    name_query = request.GET.get('name')
    building = request.GET.get('building')
    room_type = request.GET.get('room_type')

    if is_valid_queryparam(name_query):
        rooms = rooms.filter(name=name_query, avaiable=True)

    if is_valid_queryparam(room_type) and room_type != 'Choose...':
        rooms = rooms.filter(type__name=room_type)

    if is_valid_queryparam(building) and building != 'Choose...':
        rooms = rooms.filter(building__name=building)

    return rooms


def extra_room_filter(request,date_start, date_end, qs):
    amount_of_people = request.GET.get('amountPeople')
    software = request.GET.get('software')
    equipment = request.GET.get('equipment')

    if is_valid_queryparam(amount_of_people):
        qs = qs.filter(maxNumberOfPeople__gt=amount_of_people)

    if is_valid_queryparam(date_start):
        qs = qs.exclude(
            reservation__start__lte=date_start,
            reservation__end__gte=date_start, reservation__status='accepted'
        )

    if is_valid_queryparam(date_end):
        qs = qs.exclude(
            reservation__start__lte=date_end,
            reservation__end__gte=date_end, reservation__status='accepted'
        )

    if is_valid_queryparam(software) and software != 'Choose...':
        qs = qs.filter(softwares__name=software)

    if is_valid_queryparam(equipment) and equipment != 'Choose...':
        qs = qs.filter(equipments__name=equipment)

    return qs


def get_coordinator_rooms(coordinator):
    buildings = Building.objects.filter(coordinator__user=coordinator)
    rooms_to_manage = Room.objects.none()
    for building in buildings:
        rooms_to_add = Room.objects.filter(building=building)
        rooms_to_manage = rooms_to_add | rooms_to_manage

    return rooms_to_manage


def get_reservation_to_manage(rooms):
    reservations_to_manage = Reservation.objects.none()
    for room in rooms:
        reservations_to_add = Reservation.objects.filter(room=room, room__available=True)
        reservations_to_manage = reservations_to_add | reservations_to_manage

    return reservations_to_manage


def management_request(request):
    user = request.user
    user_reservations = Reservation.objects.filter(user=user)
    user_reservations_waiting = user_reservations.filter(status='Waiting')
    user_reservations_waiting_count = user_reservations_waiting.count()
    user_reservations_rejected = user_reservations.filter(status='Rejected')
    user_reservations_rejected_count = user_reservations_rejected.count()
    user_reservations_accepted = user_reservations.filter(status='Accepted')
    user_reservations_accepted_count = user_reservations_accepted.count()
    all_reservations_count = user_reservations_accepted_count + user_reservations_rejected_count \
                             + user_reservations_waiting_count
    room_keeper = user_is_room_keeper(user)
    coordinator = user_is_coordinator(user)

    context = {
        'reservation_waiting': user_reservations_waiting_count,
        'reservation_rejected': user_reservations_rejected_count,
        'reservation_accepted': user_reservations_accepted_count,
        'all_reservations': all_reservations_count,
        'room_keeper': room_keeper,
        'coordinator': coordinator

    }

    return render(request, 'rezerwacje/reservation/management.html', context)


def room_keeper_request(request):
    room_keeper = request.user
    rooms = Room.objects.filter(roomkeeper__user=room_keeper)
    reservations_to_manage = get_reservation_to_manage(rooms)
    reservations_to_manage = reservation_filter(request,reservations_to_manage)
    context = get_context_to_filer_reservations(reservations_to_manage)

    return render(request, 'rezerwacje/room_keeper/room_management.html', context)


def coordinator_reservation_management_request(request):
    coordinator = request.user
    rooms_to_manage = get_coordinator_rooms(coordinator)
    reservations_to_manage = get_reservation_to_manage(rooms_to_manage)
    reservations_to_manage = reservation_filter(request,reservations_to_manage)
    context = get_context_to_filer_reservations(reservations_to_manage)

    return render(request, 'rezerwacje/coordinator/reservation_management.html', context)


def coordinator_rooms_management_request(request):
    coordinator = request.user
    rooms_to_manage = get_coordinator_rooms(coordinator)

    rooms_to_manage = room_filter(request, rooms_to_manage)
    context = {
        'rooms': rooms_to_manage,
        'types': RoomType.objects.all(),
        'buildings': Building.objects.filter(coordinator__user = coordinator)
    }

    return render(request, 'rezerwacje/coordinator/room_management.html', context)

def show_room_detail_request(request, pk):
    room = get_object_or_404(Room, pk=pk)

    return render(request, 'rezerwacje/room/detail.html', {'room':room})


@login_required
def user_reservation_request(request):

    user_reservations = Reservation.objects.filter(user=request.user)
    user_reservations = reservation_filter(request, user_reservations)

    context = get_context_to_filer_reservations(user_reservations)

    return render(request, 'rezerwacje/reservation/my_reservation.html', context)


@login_required(login_url='/rezerwacje/login/')
def reservation_new(request, pk, start, end):
    room = get_object_or_404(Room, pk=pk)
    if request.method == "POST":
        form = NewReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.room = room
            reservation.comment = " "
            reservation.user = request.user
            reservation.start = start
            reservation.end = end
            reservation.save()
            messages.info(request, "You have successfully reserve room .")
            return redirect('rezerwacje:filtering_rooms')

    else:

        form = NewReservationForm()

    return render(request, 'rezerwacje/reservation/new.html', {'form': form})


@login_required(login_url='/rezerwacje/login/')
def new_room_request(request):
    if request.method == "POST":
        form = NewRoomForm(request.POST)
        if form.is_valid():
            room= form.save(commit=False)
            room.available = True
            room.save()
            messages.info(request, "You have successfully create a room .")
            return redirect('rezerwacje:coordinator_management_rooms')

    else:

        form = NewRoomForm()

    return render(request, 'rezerwacje/room/new.html', {'form': form})


def logout_request(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect("rezerwacje:filtering_rooms")


def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("rezerwacje:filtering_rooms")
            else:
                messages.error(request,"Invalid username or password.")
        else:
            messages.error(request,"Invalid username or password.")
    form = AuthenticationForm()
    return render(request=request, template_name="rezerwacje/user/login.html", context={"login_form":form})


def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful." )
            return redirect("rezerwacje:filtering_rooms")

        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm
    return render (request=request, template_name="rezerwacje/user/register.html", context={"register_form":form})


def filtering_rooms(request):
    qs = Room.objects.filter(available=True)
    buildings = Building.objects.all()
    softwares = Software.objects.all()
    equipments = Equipment.objects.all()
    types = RoomType.objects.all()

    date_start = request.GET.get('dateStart')
    date_end = request.GET.get('dateEnd')

    qs=room_filter(request,qs)
    qs=extra_room_filter(request,date_start, date_end,qs)


    context = {
        'queryset': qs,
        'buildings': buildings,
        'types': types,
        'softwares': softwares,
        'equipments': equipments,
        'date_start': date_start,
        'date_end': date_end

    }

    return render(request, 'rezerwacje/room/search.html', context)



