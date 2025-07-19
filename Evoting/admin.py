from django.contrib import admin
from django.utils.html import format_html_join
from .models import Voter, Candidate, Vote
from django.utils.html import format_html

class VoterAdmin(admin.ModelAdmin):
    list_display = ('national_id', 'name', 'date_of_birth', 'age', 'department', 'has_voted', 'is_verified', 'registered_by', 'registered_at', 'verified_by', 'verified_at')

admin.site.register(Voter, VoterAdmin)

class CandidateAdmin(admin.ModelAdmin):

    list_display = ('name', 'position', 'party', 'votes', 'voters_list', 'is_faculty_representative', 'faculty', 'display_photo')
    list_filter = ('position', 'party', 'is_faculty_representative', 'faculty', 'photo')

    def voters_list(self, obj):
        voters = obj.vote_set.select_related('voter').all()
        return format_html_join(
            '<br>',
            '{} ({})',
            ((vote.voter.name, vote.voter.national_id) for vote in voters)
        ) if voters else "-"
    voters_list.short_description = "Voters"

    def display_photo(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />', obj.photo.url)

        return 'No Photo'
    display_photo.allow_tags = True
    display_photo.short_description = 'Photo'

admin.site.register(Candidate, CandidateAdmin)
admin.site.register(Vote)