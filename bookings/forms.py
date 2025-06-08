from django import forms
from .models import Booking, MenuSelection, CourseSelection, Quote, Payment, Message
from venues.models import Venue
from caterers.models import Caterer, MenuPackage, CourseCategory, MenuItem

class BookingForm(forms.ModelForm):
    """
    Form for creating and updating bookings
    """
    event_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50'}),
    )
    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50'}),
    )
    end_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50'}),
    )
    venue = forms.ModelChoiceField(
        queryset=Venue.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50'}),
    )
    caterer = forms.ModelChoiceField(
        queryset=Caterer.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50'}),
    )
    
    class Meta:
        model = Booking
        fields = ['event_type', 'event_date', 'start_time', 'end_time', 'guest_count', 
                  'venue', 'caterer', 'special_requests']
        widgets = {
            'event_type': forms.TextInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50'}),
            'guest_count': forms.NumberInput(attrs={'min': 1, 'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50'}),
            'special_requests': forms.Textarea(attrs={'rows': 4, 'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50'}),
        }
    
    def __init__(self, *args, **kwargs):
        venue_id = kwargs.pop('venue_id', None)
        super(BookingForm, self).__init__(*args, **kwargs)
        
        # If we have a venue, set it as the initial selection
        if venue_id:
            self.fields['venue'].initial = venue_id

class MenuSelectionForm(forms.ModelForm):
    """
    Form for selecting a menu package and specifying dietary requirements
    """
    menu_package = forms.ModelChoiceField(
        queryset=MenuPackage.objects.none(),
        widget=forms.Select(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50'}),
    )
    
    class Meta:
        model = MenuSelection
        fields = ['menu_package', 'vegetarian_count', 'gluten_free_count', 
                  'nut_free_count', 'halal_count', 'other_dietary_requirements', 'notes']
        widgets = {
            'vegetarian_count': forms.NumberInput(attrs={'min': 0, 'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50'}),
            'gluten_free_count': forms.NumberInput(attrs={'min': 0, 'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50'}),
            'nut_free_count': forms.NumberInput(attrs={'min': 0, 'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50'}),
            'halal_count': forms.NumberInput(attrs={'min': 0, 'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50'}),
            'other_dietary_requirements': forms.Textarea(attrs={'rows': 3, 'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50'}),
        }
    
    def __init__(self, *args, **kwargs):
        caterer_id = kwargs.pop('caterer_id', None)
        menu_id = kwargs.pop('menu_id', None)
        super(MenuSelectionForm, self).__init__(*args, **kwargs)
        
        # Filter menu packages by caterer
        if caterer_id:
            self.fields['menu_package'].queryset = MenuPackage.objects.filter(caterer_id=caterer_id)
            
            # If a specific menu package was requested
            if menu_id:
                self.fields['menu_package'].initial = menu_id

class CourseSelectionForm(forms.ModelForm):
    """
    Form for selecting menu items for a specific course category
    """
    selected_items = forms.ModelMultipleChoiceField(
        queryset=MenuItem.objects.none(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'mt-1'}),
        required=False
    )
    
    class Meta:
        model = CourseSelection
        fields = ['course_category', 'selected_items']
        widgets = {
            'course_category': forms.HiddenInput(),
        }
    
    def __init__(self, *args, **kwargs):
        course_category = kwargs.pop('course_category', None)
        caterer_id = kwargs.pop('caterer_id', None)
        super(CourseSelectionForm, self).__init__(*args, **kwargs)
        
        if course_category and caterer_id:
            self.fields['course_category'].initial = course_category.id
            self.fields['selected_items'].queryset = MenuItem.objects.filter(
                caterer_id=caterer_id, 
                course_category=course_category
            )

class QuoteForm(forms.ModelForm):
    """
    Form for creating quotes (provider use)
    """
    valid_until = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50'}),
    )
    
    class Meta:
        model = Quote
        fields = ['venue_cost', 'catering_cost', 'service_charges', 'additional_charges', 
                  'additional_charges_description', 'total_amount', 'valid_until', 
                  'client_notes', 'provider_notes']
        widgets = {
            'venue_cost': forms.NumberInput(attrs={'min': 0, 'step': '0.01', 'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50'}),
            'catering_cost': forms.NumberInput(attrs={'min': 0, 'step': '0.01', 'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50'}),
            'service_charges': forms.NumberInput(attrs={'min': 0, 'step': '0.01', 'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50'}),
            'additional_charges': forms.NumberInput(attrs={'min': 0, 'step': '0.01', 'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50'}),
            'additional_charges_description': forms.Textarea(attrs={'rows': 2, 'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50'}),
            'total_amount': forms.NumberInput(attrs={'min': 0, 'step': '0.01', 'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50'}),
            'client_notes': forms.Textarea(attrs={'rows': 3, 'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50'}),
            'provider_notes': forms.Textarea(attrs={'rows': 3, 'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50'}),
        }

class PaymentForm(forms.ModelForm):
    """
    Form for recording payments
    """
    payment_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50'}),
    )
    
    class Meta:
        model = Payment
        fields = ['amount', 'payment_type', 'payment_method', 'reference_number', 'payment_date']
        widgets = {
            'amount': forms.NumberInput(attrs={'min': 0, 'step': '0.01', 'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50'}),
            'payment_type': forms.Select(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50'}),
            'payment_method': forms.Select(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50'}),
            'reference_number': forms.TextInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50'}),
        }

class MessageForm(forms.ModelForm):
    """
    Form for sending messages between clients and providers
    """
    class Meta:
        model = Message
        fields = ['subject', 'content']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50'}),
            'content': forms.Textarea(attrs={'rows': 4, 'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50'}),
        }
