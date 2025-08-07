from django.contrib import admin
from django.utils.html import format_html
from .models import Voter, Vote

@admin.register(Voter)
class VoterAdmin(admin.ModelAdmin):
    list_display = ('voter_id', 'get_full_name', 'email', 'mobile', 'age_display', 'is_active', 'has_voted')
    list_filter = ('is_active', 'has_voted', 'gender', 'state')
    search_fields = ('voter_id', 'first_name', 'last_name', 'email', 'mobile', 'aadhar_number', 'pan_number')
    ordering = ('-registration_date',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': (('voter_id', 'password'), ('first_name', 'last_name'), 'email')
        }),
        ('Personal Details', {
            'fields': (('mobile', 'date_of_birth', 'gender'), 'parent_spouse_name')
        }),
        ('Address Information', {
            'fields': ('street_address', ('city', 'state', 'pincode'), 'place_of_birth')
        }),
        ('Identity Documents', {
            'fields': ('aadhar_number', 'pan_number'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': (('is_active', 'has_voted'), ('registration_date', 'last_login')),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('registration_date', 'last_login')

    def age_display(self, obj):
        from datetime import date
        today = date.today()
        age = today.year - obj.date_of_birth.year - ((today.month, today.day) < (obj.date_of_birth.month, obj.date_of_birth.day))
        color = '#28a745' if age >= 18 else '#dc3545'
        return format_html('<span style="color: {};">{} years</span>', color, age)
    age_display.short_description = 'Age'

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('voter_id', 'aadhar_number', 'pan_number')
        return self.readonly_fields

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('voter', 'timestamp', 'is_valid')
    list_filter = ('is_valid', 'timestamp')
    search_fields = ('voter__voter_id', 'voter__first_name', 'voter__last_name')
    readonly_fields = ('timestamp',)

    def has_add_permission(self, request):
        return False  # Prevent manual addition of votes

    def has_change_permission(self, request, obj=None):
        return False  # Prevent editing of votes
