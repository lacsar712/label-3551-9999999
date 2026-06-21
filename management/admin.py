from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Estate, Building, Floor, Unit, Repair, Fee, Contract, ContractAttachment, Vote, VoteOption, VoteBallot, VoteRecord, LostItem, ClaimApplication, TemporaryParkingApplication, TemporaryParkingPermit

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


class ClaimApplicationInline(admin.TabularInline):
    model = ClaimApplication
    extra = 0
    readonly_fields = ('applicant', 'claim_description', 'contact_info', 'status', 'claimant', 'claim_date', 'handler', 'created_at')


class LostItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'found_location', 'found_date', 'storage_location', 'status', 'reporter', 'created_at')
    list_filter = ('status',)
    search_fields = ('name', 'found_location', 'description')
    inlines = [ClaimApplicationInline]


admin.site.register(LostItem, LostItemAdmin)
admin.site.register(ClaimApplication)


class TemporaryParkingPermitInline(admin.StackedInline):
    model = TemporaryParkingPermit
    extra = 0
    readonly_fields = ('permit_no', 'status', 'generated_at')


class TemporaryParkingApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'applicant', 'license_plate', 'visit_date', 'stay_start', 'stay_end', 'status', 'created_at')
    list_filter = ('status', 'visit_date')
    search_fields = ('license_plate', 'applicant__username', 'visit_reason', 'contact_phone')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [TemporaryParkingPermitInline]


admin.site.register(TemporaryParkingApplication, TemporaryParkingApplicationAdmin)
admin.site.register(TemporaryParkingPermit)
