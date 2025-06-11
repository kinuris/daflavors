from django import forms
from .models import Caterer, CatererImage, MenuPackage, CourseCategory, MenuItem, PackageItem, CatererAvailability, EventType

class CatererForm(forms.ModelForm):
    event_types = forms.ModelMultipleChoiceField(
        queryset=EventType.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'grid grid-cols-2 gap-2'
        }),
        required=False,
        help_text="Select the types of events you cater for"
    )
    
    class Meta:
        model = Caterer
        exclude = ['provider', 'created_at', 'updated_at']
        widgets = {
            'specialty': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'}),
            'min_guests': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'}),
            'max_guests': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'}),
            'offers_buffet': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'}),
            'offers_plated': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'}),
            'offers_cocktail': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'}),
            'offers_food_stalls': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'}),
            'service_area': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'}),
            'setup_policy': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500', 'rows': 3}),
            'delivery_policy': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500', 'rows': 3}),
            'payment_policy': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500', 'rows': 3}),
            'cancellation_policy': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500', 'rows': 3}),
        }

class CatererImageForm(forms.ModelForm):
    class Meta:
        model = CatererImage
        fields = ['image', 'caption', 'is_primary']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'w-full border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'}),
            'caption': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'}),
        }

class MenuPackageForm(forms.ModelForm):
    class Meta:
        model = MenuPackage
        exclude = ['caterer', 'created_at', 'updated_at']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500', 'rows': 4}),
            'package_type': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'}),
            'base_price_per_person': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'}),
            'min_persons': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'}),
            'is_customizable': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'}),
        }

class CourseCategoryForm(forms.ModelForm):
    class Meta:
        model = CourseCategory
        fields = ['name', 'display_order']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'}),
            'display_order': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'}),
        }

class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        exclude = ['caterer', 'created_at']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500', 'rows': 3}),
            'course_category': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'}),
            'is_vegetarian': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'}),
            'is_gluten_free': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'}),
            'is_nut_free': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'}),
            'is_halal': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'}),
            'individual_price': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'}),
            'image': forms.FileInput(attrs={'class': 'w-full border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'}),
        }

class PackageItemForm(forms.ModelForm):
    class Meta:
        model = PackageItem
        exclude = ['package']
        widgets = {
            'course_category': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'}),
            'items': forms.SelectMultiple(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'}),
            'selection_limit': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'}),
            'is_required': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'}),
            'additional_price': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'}),
        }

class CatererAvailabilityForm(forms.ModelForm):
    class Meta:
        model = CatererAvailability
        exclude = ['caterer', 'current_bookings']
        widgets = {
            'date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500',
                'type': 'date'
            }),
            'is_available': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'}),
            'morning_available': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'}),
            'afternoon_available': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'}),
            'evening_available': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'}),
            'max_bookings_per_day': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500'}),
            'notes': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500', 'rows': 2}),
        }
