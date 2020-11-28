from django.urls import path
from django_filters.views import FilterView
from django_filters.views import object_filter
from .filters import RoomFilter
from .models import Room
from .views import filtering_rooms, register_request, login_request, management_request,logout_request, \
        coordinator_rooms_management_request, reservation_new, user_reservation_request, cancel_reservation_by_user_request, \
        room_keeper_request, coordinator_reservation_management_request, cancel_reservation_by_roomkeeper_request, \
        show_room_detail_request, cancel_reservation_by_coordinator_request, accept_reservation_by_coordinator_request, \
        accept_reservation_by_roomkeeper_request, enable_possibility_of_reserve_room, disable_possibility_of_reserve_room, \
    new_room_request

app_name = 'rezerwacje'
urlpatterns = [
        path('', filtering_rooms, name='filtering_rooms'),
        path("register", register_request, name="register"),
        path("login", login_request, name="login"),
        path("logout", logout_request, name="logout"),
        path('room/<int:pk>/<str:start>/<str:end>/reservation/new', reservation_new, name='reservation_new'),
        path("my_reservation", user_reservation_request, name='my_reservation'),
        path("reservation/<int:pk>/cancel", cancel_reservation_by_user_request, name='cancel_reservation'),
        path("management/roomkeeper", room_keeper_request, name='room_keeper_management'),
        path("management", management_request, name="management"),
        path("management/coordinator/rooms", coordinator_rooms_management_request, name="coordinator_management_rooms"),
        path("management/coordinator", coordinator_reservation_management_request, name="coordinator_management"),
        path("reservation/<int:pk>/cancel_by_roomkeeper", cancel_reservation_by_roomkeeper_request,
             name='cancel_by_roomkeeper'),
        path("reservation/<int:pk>/cancel_by_coordinator", cancel_reservation_by_coordinator_request,
             name='cancel_by_coordinator'),
        path("room/<int:pk>", show_room_detail_request, name='room_detail'),
        path("reservation/<int:pk>/accept", accept_reservation_by_roomkeeper_request,
             name="accept_reservation_roomkeeper"),
        path("reservation/<int:pk>/accept", accept_reservation_by_coordinator_request,
             name="accept_reservation_coordinator"),
        path("room/<int:pk>/enable", enable_possibility_of_reserve_room,
             name="enable_room"),
        path("room/<int:pk>/disable", disable_possibility_of_reserve_room,
             name="disable_room"),
        path("management/coordinator/room/new", new_room_request, name="new_room" )


]
