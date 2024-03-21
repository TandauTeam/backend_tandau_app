from django.contrib import admin
from .models import CustomUser,Question


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    list_display = ('first_name','last_name','username','image')



@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id','question_text_ru','question_text_kz','person_type')