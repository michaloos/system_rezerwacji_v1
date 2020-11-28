from bootstrap_datepicker.widgets import DatePicker
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Reservation, ReservationType, Room, Software, Equipment, RoomType, Building
from django.forms import DateTimeField


# Create your forms here.


class NewUserForm(UserCreationForm):
	email = forms.EmailField(required=True)

	class Meta:
		model = User
		fields = ("username", "email", "password1", "password2")

	def save(self, commit=True):
		user = super(NewUserForm, self).save(commit=False)
		user.email = self.cleaned_data['email']
		if commit:
			user.save()
		return user


class MyModelChoiceField(forms.ModelChoiceField):
	def label_from_instance(self, obj):
		return obj.name


class NewReservationForm(forms.ModelForm):
	amountOfPeople = forms.IntegerField(label='Amount of people', min_value=1)
	type = forms.ModelChoiceField(queryset=ReservationType.objects.all(), required=True, label="Reservation type")

	class Meta:
		model = Reservation
		fields = ('amountOfPeople', 'type')


class NewRoomForm(forms.ModelForm):
	maxNumberOfPeople = forms.IntegerField(label='Maximum number of people', min_value=1)
	softwares = forms.ModelMultipleChoiceField(queryset=Software.objects.all(), required=False, label="Softwares")
	equipments = forms.ModelMultipleChoiceField(queryset=Equipment.objects.all(), required=False, label="Equipments")
	type = forms.ModelChoiceField(queryset=RoomType.objects.all(), required=True, label='Room type')
	building = forms.ModelChoiceField(queryset=Building.objects.all(), required=True, label='Building')


	class Meta:
		model= Room
		fields = ('name', 'maxNumberOfPeople', 'building', 'type', 'softwares', 'equipments')


class ChangeStatusReservationForm(forms.ModelForm):
	class Meta:
		model = Reservation
		fields = ('comment',)