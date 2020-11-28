import django_filters
from .models import Room, RoomType, Building, Software, Equipment, Reservation
from django import forms



class RoomFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name')
    maxNumberOfPeople = django_filters.NumberFilter(field_name='maxNumberOfPeople')
    type = django_filters.ModelChoiceFilter(queryset=RoomType.objects.all(), widget=forms.RadioSelect)
    building = django_filters.ModelChoiceFilter(queryset=Building.objects.all(),
                                                        widget=forms.RadioSelect)
    softwares = django_filters.ModelMultipleChoiceFilter(queryset=Software.objects.all(),
                                                         widget=forms.CheckboxSelectMultiple)
    equipments = django_filters.ModelMultipleChoiceFilter(queryset=Equipment.objects.all(),
                                                          widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Room
        fields = ['name', 'maxNumberOfPeople', 'type', 'building', 'softwares', 'equipments']