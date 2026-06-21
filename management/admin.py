from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Estate, Building, Floor, Unit, Repair, Fee, Contract, ContractAttachment, Vote, VoteOption, VoteBallot, VoteRecord

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('角色信息', {'fields': ('role', 'phone')}),
    )

class ContractAttachmentInline(admin.TabularInline):
    model = ContractAttachment
    extra = 0
    readonly_fields = ('uploaded_at',)

class ContractAdmin(admin.ModelAdmin):
    list_display = ('contract_no', 'contract_type', 'related_object', 'sign_date', 'expire_date', 'amount', 'payment_method')
    list_filter = ('contract_type', 'payment_method')
    search_fields = ('contract_no', 'related_object')
    inlines = [ContractAttachmentInline]

admin.site.register(User, CustomUserAdmin)
admin.site.register(Estate)
admin.site.register(Building)
admin.site.register(Floor)
admin.site.register(Unit)
admin.site.register(Repair)
admin.site.register(Fee)
admin.site.register(Contract, ContractAdmin)
admin.site.register(ContractAttachment)


class VoteOptionInline(admin.TabularInline):
    model = VoteOption
    extra = 2


class VoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'status', 'start_time', 'end_time', 'allow_multiple', 'is_anonymous', 'created_by')
    list_filter = ('status', 'allow_multiple', 'is_anonymous')
    search_fields = ('title',)
    inlines = [VoteOptionInline]


admin.site.register(Vote, VoteAdmin)
admin.site.register(VoteBallot)
admin.site.register(VoteRecord)
