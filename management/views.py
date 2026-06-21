from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView, DetailView, View
from django.contrib import messages
from datetime import date, timedelta
from .models import User, Estate, Building, Floor, Unit, Repair, Fee, Contract, ContractAttachment, Supplier, GreeningMaintenance, SafetyInspection, SafetyInspectionTrack, Vote, VoteOption, VoteBallot, VoteRecord, LostItem, ClaimApplication, TemporaryParkingApplication, TemporaryParkingPermit
from .forms import EstateForm, BuildingForm, FloorForm, UnitForm, OwnerForm, RepairOwnerForm, RepairStaffForm, FeeForm, ContractForm, ContractAttachmentForm, SupplierForm, GreeningMaintenanceForm, SafetyInspectionCreateForm, SafetyInspectionRectifyForm, SafetyInspectionUpdateForm, VoteForm, VoteOptionFormSet, LostItemForm, ClaimApplicationForm, ClaimConfirmForm, TemporaryParkingApplicationForm, TemporaryParkingReviewForm
import csv
from django.http import HttpResponse, FileResponse
import os
from django.conf import settings

class CustomLoginView(LoginView):
    template_name = 'management/login.html'
    redirect_authenticated_user = True

    def form_invalid(self, form):
        print("Login failed! Errors:", form.errors)
        print("Data received:", self.request.POST)
        return super().form_invalid(form)

class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role in ['admin', 'staff']
        
class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'management/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.role in ['admin', 'staff']:
            context['estate_count'] = Estate.objects.count()
            context['owner_count'] = User.objects.filter(role='owner').count()
            context['pending_repairs'] = Repair.objects.filter(status='pending').count()
            context['unpaid_fees'] = Fee.objects.filter(status='unpaid').count()
            today = date.today()
            first_day_of_month = today.replace(day=1)
            context['monthly_greening_count'] = GreeningMaintenance.objects.filter(
                work_date__gte=first_day_of_month,
                work_date__lte=today
            ).count()
            sixty_days_later = today + timedelta(days=60)
            expiring_contracts = Contract.objects.filter(expire_date__gte=today, expire_date__lte=sixty_days_later).order_by('expire_date')
            context['expiring_contracts_count'] = expiring_contracts.count()
            context['expiring_contracts'] = expiring_contracts[:5]
            context['expiring_contracts_total_amount'] = sum(c.amount for c in expiring_contracts)
            
            high_risk_open = SafetyInspection.objects.filter(risk_level='high', status='open').order_by('rectification_deadline')
            context['high_risk_open_count'] = high_risk_open.count()
            context['high_risk_open'] = high_risk_open[:10]
            for h in high_risk_open:
                h.overdue_flag = h.is_overdue()
                h.days_left = h.days_until_deadline()
            context['medium_risk_open_count'] = SafetyInspection.objects.filter(risk_level='medium', status='open').count()
            context['low_risk_open_count'] = SafetyInspection.objects.filter(risk_level='low', status='open').count()
            context['pending_lost_items_count'] = LostItem.objects.filter(status='pending').count()
            context['pending_claims_count'] = ClaimApplication.objects.filter(status='pending').count()
        else:
            context['my_units'] = Unit.objects.filter(owner=self.request.user)
            context['my_repairs'] = Repair.objects.filter(owner=self.request.user).order_by('-submit_time')[:5]
            context['unpaid_fees'] = Fee.objects.filter(unit__owner=self.request.user, status='unpaid')
            context['active_unvoted'] = Vote.objects.filter(status='active').exclude(voter_records__voter=self.request.user)
            context['pending_lost_items'] = LostItem.objects.filter(status='pending').order_by('-found_date')[:5]
        return context

# --- 楼盘管理 ---
class EstateListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = Estate
    template_name = 'management/estate_list.html'
    context_object_name = 'estates'

class EstateCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Estate
    form_class = EstateForm
    template_name = 'management/form.html'
    success_url = reverse_lazy('estate_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "新增楼盘"
        return context

class EstateUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Estate
    form_class = EstateForm
    template_name = 'management/form.html'
    success_url = reverse_lazy('estate_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "修改楼盘"
        return context

class EstateDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Estate
    template_name = 'management/confirm_delete.html'
    success_url = reverse_lazy('estate_list')

# --- 楼栋管理 ---
class BuildingListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = Building
    template_name = 'management/building_list.html'
    context_object_name = 'buildings'

class BuildingCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Building
    form_class = BuildingForm
    template_name = 'management/form.html'
    success_url = reverse_lazy('building_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "新增楼栋"
        return context

class BuildingUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Building
    form_class = BuildingForm
    template_name = 'management/form.html'
    success_url = reverse_lazy('building_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "修改楼栋"
        return context

class BuildingDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Building
    template_name = 'management/confirm_delete.html'
    success_url = reverse_lazy('building_list')

# --- 楼层管理 ---
class FloorListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = Floor
    template_name = 'management/floor_list.html'
    context_object_name = 'floors'

class FloorCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Floor
    form_class = FloorForm
    template_name = 'management/form.html'
    success_url = reverse_lazy('floor_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "新增楼层"
        return context

class FloorUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Floor
    form_class = FloorForm
    template_name = 'management/form.html'
    success_url = reverse_lazy('floor_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "修改楼层"
        return context

class FloorDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Floor
    template_name = 'management/confirm_delete.html'
    success_url = reverse_lazy('floor_list')

# --- 单元(房屋)管理 ---
class UnitListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = Unit
    template_name = 'management/unit_list.html'
    context_object_name = 'units'

class UnitCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Unit
    form_class = UnitForm
    template_name = 'management/form.html'
    success_url = reverse_lazy('unit_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "新增单元/房屋"
        return context

class UnitUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Unit
    form_class = UnitForm
    template_name = 'management/form.html'
    success_url = reverse_lazy('unit_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "修改单元/房屋"
        return context

class UnitDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Unit
    template_name = 'management/confirm_delete.html'
    success_url = reverse_lazy('unit_list')

# --- 业主管理 ---
class OwnerListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = User
    template_name = 'management/owner_list.html'
    context_object_name = 'owners'

    def get_queryset(self):
        return User.objects.filter(role='owner')

class OwnerCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = User
    form_class = OwnerForm
    template_name = 'management/form.html'
    success_url = reverse_lazy('owner_list')

    def form_valid(self, form):
        form.instance.role = 'owner'
        form.instance.set_password('123456') # Default password
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "新增业主信息 (默认密码123456)"
        return context

class OwnerUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = User
    form_class = OwnerForm
    template_name = 'management/form.html'
    success_url = reverse_lazy('owner_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "修改业主信息"
        return context

class OwnerDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = User
    template_name = 'management/confirm_delete.html'
    success_url = reverse_lazy('owner_list')

# --- 报修管理 ---
class RepairListView(LoginRequiredMixin, ListView):
    model = Repair
    template_name = 'management/repair_list.html'
    context_object_name = 'repairs'

    def get_queryset(self):
        qs = Repair.objects.all()
        if self.request.user.role == 'owner':
            qs = qs.filter(owner=self.request.user)
            
        # 多条件过滤
        fault_type = self.request.GET.get('fault_type')
        status = self.request.GET.get('status')
        if fault_type:
            qs = qs.filter(fault_type=fault_type)
        if status:
            qs = qs.filter(status=status)
            
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['fault_types'] = Repair.TYPE_CHOICES
        context['statuses'] = Repair.STATUS_CHOICES
        return context

class RepairCreateView(LoginRequiredMixin, CreateView):
    model = Repair
    form_class = RepairOwnerForm
    template_name = 'management/form.html'
    success_url = reverse_lazy('repair_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.user.role == 'owner':
            kwargs['owner'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, "报修申请提交成功！")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "提交报修"
        return context

class RepairUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Repair
    form_class = RepairStaffForm
    template_name = 'management/form.html'
    success_url = reverse_lazy('repair_list')

    def form_valid(self, form):
        messages.success(self.request, "处理进度更新成功！")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "处理报修"
        return context

# --- 费用中心 ---
class FeeListView(LoginRequiredMixin, ListView):
    model = Fee
    template_name = 'management/fee_list.html'
    context_object_name = 'fees'

    def get_queryset(self):
        qs = Fee.objects.all()
        if self.request.user.role == 'owner':
            qs = qs.filter(unit__owner=self.request.user)
            
        # 过滤
        status = self.request.GET.get('status')
        fee_type = self.request.GET.get('fee_type')
        if status:
            qs = qs.filter(status=status)
        if fee_type:
            qs = qs.filter(fee_type=fee_type)
            
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['statuses'] = Fee.STATUS_CHOICES
        context['fee_types'] = Fee.FEE_TYPES
        return context

    def get(self, request, *args, **kwargs):
        if 'export' in request.GET and request.user.role in ['admin', 'staff']:
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="fee_export.csv"'
            response.write('\xEF\xBB\xBF') # UTF-8 BOM

            writer = csv.writer(response)
            writer.writerow(['费用类型', '关联房屋', '业主', '金额', '状态', '截止日期', '收款日期'])

            for fee in self.get_queryset():
                owner_name = fee.unit.owner.username if fee.unit.owner else '未绑定'
                writer.writerow([
                    fee.get_fee_type_display(),
                    f"{fee.unit.floor.building.estate.name}-{fee.unit.floor.building.name}-{fee.unit.name}",
                    owner_name,
                    fee.amount,
                    fee.get_status_display(),
                    fee.due_date,
                    fee.payment_date or '-'
                ])
            return response
        return super().get(request, *args, **kwargs)

class FeeCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Fee
    form_class = FeeForm
    template_name = 'management/form.html'
    success_url = reverse_lazy('fee_list')

    def form_valid(self, form):
        messages.success(self.request, "账单生成成功！")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "生成账单"
        return context

class FeeUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Fee
    form_class = FeeForm
    template_name = 'management/form.html'
    success_url = reverse_lazy('fee_list')

    def form_valid(self, form):
        messages.success(self.request, "账单记录更新成功！")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "修改或收款"
        return context

class FeeDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Fee
    template_name = 'management/confirm_delete.html'
    success_url = reverse_lazy('fee_list')


# --- 合同管理 ---
class ContractListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = Contract
    template_name = 'management/contract_list.html'
    context_object_name = 'contracts'

    def get_queryset(self):
        qs = Contract.objects.all()
        contract_type = self.request.GET.get('contract_type')
        if contract_type:
            qs = qs.filter(contract_type=contract_type)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contract_types'] = Contract.TYPE_CHOICES
        today = date.today()
        sixty_days_later = today + timedelta(days=60)
        for contract in context['contracts']:
            contract.expiring_soon = contract.expire_date >= today and contract.expire_date <= sixty_days_later
            contract.days_left = (contract.expire_date - today).days
            contract.days_left_str = abs(contract.days_left)
        return context


class ContractCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Contract
    form_class = ContractForm
    template_name = 'management/form.html'
    success_url = reverse_lazy('contract_list')

    def form_valid(self, form):
        messages.success(self.request, "合同创建成功！")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "新增合同"
        return context


class ContractUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Contract
    form_class = ContractForm
    template_name = 'management/form.html'
    success_url = reverse_lazy('contract_list')

    def form_valid(self, form):
        messages.success(self.request, "合同更新成功！")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "编辑合同"
        return context


class ContractDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Contract
    template_name = 'management/confirm_delete.html'
    success_url = reverse_lazy('contract_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "合同删除成功！")
        return super().delete(request, *args, **kwargs)


class ContractDetailView(LoginRequiredMixin, StaffRequiredMixin, DetailView):
    model = Contract
    template_name = 'management/contract_detail.html'
    context_object_name = 'contract'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['attachment_form'] = ContractAttachmentForm()
        today = date.today()
        sixty_days_later = today + timedelta(days=60)
        contract = context['contract']
        contract.expiring_soon = contract.expire_date >= today and contract.expire_date <= sixty_days_later
        contract.days_left = (contract.expire_date - today).days
        contract.days_left_str = abs(contract.days_left)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = ContractAttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            attachment = form.save(commit=False)
            attachment.contract = self.object
            if 'file' in request.FILES:
                uploaded_file = request.FILES['file']
                attachment.file_name = uploaded_file.name
            attachment.save()
            messages.success(request, "附件上传成功！")
            return redirect(reverse('contract_detail', kwargs={'pk': self.object.pk}))
        context = self.get_context_data(object=self.object)
        context['attachment_form'] = form
        return self.render_to_response(context)


class ContractAttachmentDownloadView(LoginRequiredMixin, StaffRequiredMixin, View):
    def get(self, request, pk):
        attachment = get_object_or_404(ContractAttachment, pk=pk)
        file_path = os.path.join(settings.MEDIA_ROOT, attachment.file.name)
        if os.path.exists(file_path):
            response = FileResponse(open(file_path, 'rb'))
            response['Content-Type'] = 'application/pdf'
            response['Content-Disposition'] = f'attachment; filename="{attachment.file_name}"'
            return response
        messages.error(request, "文件不存在！")
        return redirect(reverse('contract_detail', kwargs={'pk': attachment.contract.pk}))


class ContractAttachmentDeleteView(LoginRequiredMixin, StaffRequiredMixin, View):
    def post(self, request, pk):
        attachment = get_object_or_404(ContractAttachment, pk=pk)
        contract_pk = attachment.contract.pk
        if attachment.file and os.path.exists(os.path.join(settings.MEDIA_ROOT, attachment.file.name)):
            os.remove(os.path.join(settings.MEDIA_ROOT, attachment.file.name))
        attachment.delete()
        messages.success(request, "附件删除成功！")
        return redirect(reverse('contract_detail', kwargs={'pk': contract_pk}))


# --- 供应商管理 ---
class SupplierListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = Supplier
    template_name = 'management/supplier_list.html'
    context_object_name = 'suppliers'

    def get_queryset(self):
        qs = Supplier.objects.all()
        service_category = self.request.GET.get('service_category')
        cooperation_status = self.request.GET.get('cooperation_status')
        if service_category:
            qs = qs.filter(service_category=service_category)
        if cooperation_status:
            qs = qs.filter(cooperation_status=cooperation_status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['service_categories'] = Supplier.SERVICE_CATEGORY_CHOICES
        context['cooperation_statuses'] = Supplier.COOPERATION_STATUS_CHOICES
        return context


class SupplierCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'management/form.html'
    success_url = reverse_lazy('supplier_list')

    def form_valid(self, form):
        messages.success(self.request, "供应商创建成功！")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "新增供应商"
        return context


class SupplierUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'management/form.html'
    success_url = reverse_lazy('supplier_list')

    def form_valid(self, form):
        messages.success(self.request, "供应商信息更新成功！")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "编辑供应商"
        return context


class SupplierDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Supplier
    template_name = 'management/confirm_delete.html'
    success_url = reverse_lazy('supplier_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "供应商删除成功！")
        return super().delete(request, *args, **kwargs)


# --- 绿化养护管理 ---
class GreeningMaintenanceListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = GreeningMaintenance
    template_name = 'management/greening_maintenance_list.html'
    context_object_name = 'maintenances'

    def get_queryset(self):
        qs = GreeningMaintenance.objects.all()
        estate_id = self.request.GET.get('estate')
        date_start = self.request.GET.get('date_start')
        date_end = self.request.GET.get('date_end')
        if estate_id:
            qs = qs.filter(estate_id=estate_id)
        if date_start:
            qs = qs.filter(work_date__gte=date_start)
        if date_end:
            qs = qs.filter(work_date__lte=date_end)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['estates'] = Estate.objects.all()
        context['current_estate'] = self.request.GET.get('estate', '')
        context['date_start'] = self.request.GET.get('date_start', '')
        context['date_end'] = self.request.GET.get('date_end', '')
        return context


class GreeningMaintenanceCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = GreeningMaintenance
    form_class = GreeningMaintenanceForm
    template_name = 'management/form.html'
    success_url = reverse_lazy('greening_maintenance_list')

    def form_valid(self, form):
        messages.success(self.request, "绿化养护记录创建成功！")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "录入绿化养护记录"
        return context


class GreeningMaintenanceUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = GreeningMaintenance
    form_class = GreeningMaintenanceForm
    template_name = 'management/form.html'
    success_url = reverse_lazy('greening_maintenance_list')

    def form_valid(self, form):
        messages.success(self.request, "绿化养护记录更新成功！")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "编辑绿化养护记录"
        return context


class GreeningMaintenanceDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = GreeningMaintenance
    template_name = 'management/confirm_delete.html'
    success_url = reverse_lazy('greening_maintenance_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "绿化养护记录删除成功！")
        return super().delete(request, *args, **kwargs)


# --- 业主端 - 社区动态 ---
class CommunityNewsView(LoginRequiredMixin, ListView):
    model = GreeningMaintenance
    template_name = 'management/community_news.html'
    context_object_name = 'maintenances'

    def get_queryset(self):
        thirty_days_ago = date.today() - timedelta(days=30)
        return GreeningMaintenance.objects.filter(
            work_date__gte=thirty_days_ago
        ).order_by('-work_date', '-created_at')


# --- 安全隐患排查管理 ---
class SafetyInspectionListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = SafetyInspection
    template_name = 'management/safety_inspection_list.html'
    context_object_name = 'inspections'

    def get_queryset(self):
        qs = SafetyInspection.objects.all()
        risk_level = self.request.GET.get('risk_level')
        status = self.request.GET.get('status')
        date_start = self.request.GET.get('date_start')
        date_end = self.request.GET.get('date_end')
        estate_id = self.request.GET.get('estate')
        if risk_level:
            qs = qs.filter(risk_level=risk_level)
        if status:
            qs = qs.filter(status=status)
        if estate_id:
            qs = qs.filter(estate_id=estate_id)
        if date_start:
            qs = qs.filter(discovery_date__gte=date_start)
        if date_end:
            qs = qs.filter(discovery_date__lte=date_end)
        for obj in qs:
            obj.overdue_flag = obj.is_overdue()
            obj.days_left = obj.days_until_deadline()
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['risk_levels'] = SafetyInspection.RISK_LEVEL_CHOICES
        context['statuses'] = SafetyInspection.STATUS_CHOICES
        context['estates'] = Estate.objects.all()
        context['current_risk_level'] = self.request.GET.get('risk_level', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['current_estate'] = self.request.GET.get('estate', '')
        context['date_start'] = self.request.GET.get('date_start', '')
        context['date_end'] = self.request.GET.get('date_end', '')
        context['total_count'] = SafetyInspection.objects.count()
        context['open_count'] = SafetyInspection.objects.filter(status='open').count()
        context['closed_count'] = SafetyInspection.objects.filter(status='closed').count()
        context['high_risk_count'] = SafetyInspection.objects.filter(risk_level='high').count()
        context['medium_risk_count'] = SafetyInspection.objects.filter(risk_level='medium').count()
        context['low_risk_count'] = SafetyInspection.objects.filter(risk_level='low').count()
        return context


class SafetyInspectionCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = SafetyInspection
    form_class = SafetyInspectionCreateForm
    template_name = 'management/form.html'
    success_url = reverse_lazy('safety_inspection_list')

    def form_valid(self, form):
        form.instance.inspector = self.request.user
        response = super().form_valid(form)
        SafetyInspectionTrack.objects.create(
            inspection=self.object,
            action='create',
            operator=self.request.user,
            remark='创建隐患排查记录：风险等级-{}, 区域-{}'.format(
                self.object.get_risk_level_display(),
                self.object.inspection_area
            )
        )
        messages.success(self.request, "隐患排查记录提交成功！")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "提交安全隐患排查记录"
        return context


class SafetyInspectionDetailView(LoginRequiredMixin, StaffRequiredMixin, DetailView):
    model = SafetyInspection
    template_name = 'management/safety_inspection_detail.html'
    context_object_name = 'inspection'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = context['inspection']
        obj.overdue_flag = obj.is_overdue()
        obj.days_left = obj.days_until_deadline()
        context['tracks'] = obj.tracks.all()
        return context


class SafetyInspectionUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = SafetyInspection
    form_class = SafetyInspectionUpdateForm
    template_name = 'management/form.html'
    success_url = reverse_lazy('safety_inspection_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        SafetyInspectionTrack.objects.create(
            inspection=self.object,
            action='update',
            operator=self.request.user,
            remark='更新隐患排查记录基本信息'
        )
        messages.success(self.request, "隐患排查记录更新成功！")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "编辑隐患排查记录"
        return context


class SafetyInspectionRectifyView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = SafetyInspection
    form_class = SafetyInspectionRectifyForm
    template_name = 'management/safety_inspection_rectify.html'
    success_url = reverse_lazy('safety_inspection_list')

    def form_valid(self, form):
        form.instance.status = 'closed'
        form.instance.rectifier = self.request.user
        response = super().form_valid(form)
        SafetyInspectionTrack.objects.create(
            inspection=self.object,
            action='close',
            operator=self.request.user,
            remark='完成整改并标记消项，整改措施：{}'.format(
                self.object.rectification_measures[:100]
            )
        )
        messages.success(self.request, "整改完成，已标记消项！")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = context['form'].instance
        obj.overdue_flag = obj.is_overdue()
        obj.days_left = obj.days_until_deadline()
        context['inspection'] = obj
        context['title'] = "隐患整改消项"
        return context


class SafetyInspectionDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = SafetyInspection
    template_name = 'management/confirm_delete.html'
    success_url = reverse_lazy('safety_inspection_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "隐患排查记录删除成功！")
        return super().delete(request, *args, **kwargs)


class VoteListView(LoginRequiredMixin, ListView):
    model = Vote
    template_name = 'management/vote_list.html'
    context_object_name = 'votes'

    def get_queryset(self):
        qs = Vote.objects.all()
        if self.request.user.role == 'owner':
            qs = qs.filter(status__in=['active', 'closed'])
        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['statuses'] = Vote.STATUS_CHOICES
        context['current_status'] = self.request.GET.get('status', '')
        if self.request.user.role == 'owner':
            for vote in context['votes']:
                vote.user_has_voted = vote.has_voted(self.request.user)
        return context


class VoteCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Vote
    form_class = VoteForm
    template_name = 'management/vote_form.html'
    success_url = reverse_lazy('vote_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['option_formset'] = VoteOptionFormSet(self.request.POST)
        else:
            context['option_formset'] = VoteOptionFormSet()
        context['title'] = "发起社区投票"
        return context

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        context = self.get_context_data()
        option_formset = context['option_formset']
        if option_formset.is_valid():
            self.object = form.save()
            option_formset.instance = self.object
            option_formset.save()
            messages.success(self.request, "社区投票发起成功！")
            return redirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class VoteDetailView(LoginRequiredMixin, DetailView):
    model = Vote
    template_name = 'management/vote_detail.html'
    context_object_name = 'vote'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vote = context['vote']
        from django.utils import timezone
        now = timezone.now()
        if vote.status == 'pending' and now >= vote.start_time:
            vote.status = 'active'
            vote.save(update_fields=['status'])
        elif vote.status == 'active' and now >= vote.end_time:
            vote.status = 'closed'
            vote.save(update_fields=['status'])
        options = vote.options.all()
        total_votes = vote.total_votes()
        option_stats = []
        for opt in options:
            count = opt.vote_count()
            pct = opt.vote_percentage()
            option_stats.append({
                'option': opt,
                'count': count,
                'percentage': pct,
            })
        context['option_stats'] = option_stats
        context['total_votes'] = total_votes
        context['can_vote'] = (
            self.request.user.role == 'owner'
            and vote.status == 'active'
            and not vote.has_voted(self.request.user)
        )
        context['has_voted'] = vote.has_voted(self.request.user)
        context['is_closed'] = vote.status == 'closed'
        context['show_voter_info'] = not vote.is_anonymous or self.request.user.role in ['admin', 'staff']
        return context


class VoteSubmitView(LoginRequiredMixin, View):
    def post(self, request, pk):
        vote = get_object_or_404(Vote, pk=pk)
        if vote.status != 'active':
            messages.error(request, "该投票不在进行中，无法投票！")
            return redirect(reverse('vote_detail', kwargs={'pk': pk}))
        if vote.has_voted(request.user):
            messages.error(request, "您已经参与过该投票！")
            return redirect(reverse('vote_detail', kwargs={'pk': pk}))
        if request.user.role != 'owner':
            messages.error(request, "仅业主可以参与投票！")
            return redirect(reverse('vote_detail', kwargs={'pk': pk}))

        selected_options = request.POST.getlist('options')
        if not selected_options:
            messages.error(request, "请至少选择一个选项！")
            return redirect(reverse('vote_detail', kwargs={'pk': pk}))
        if not vote.allow_multiple and len(selected_options) > 1:
            messages.error(request, "该投票不允许多选！")
            return redirect(reverse('vote_detail', kwargs={'pk': pk}))

        valid_option_ids = set(vote.options.values_list('id', flat=True))
        for opt_id in selected_options:
            opt_id_int = int(opt_id)
            if opt_id_int not in valid_option_ids:
                messages.error(request, "无效的投票选项！")
                return redirect(reverse('vote_detail', kwargs={'pk': pk}))

        voter = None if vote.is_anonymous else request.user
        for opt_id in selected_options:
            option = VoteOption.objects.get(pk=opt_id)
            VoteBallot.objects.create(vote=vote, option=option, voter=voter)
        VoteRecord.objects.create(vote=vote, voter=request.user)
        messages.success(request, "投票提交成功！")
        return redirect(reverse('vote_detail', kwargs={'pk': pk}))


class VoteDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Vote
    template_name = 'management/confirm_delete.html'
    success_url = reverse_lazy('vote_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "投票删除成功！")
        return super().delete(request, *args, **kwargs)


# --- 失物招领管理 ---
class LostItemListView(LoginRequiredMixin, ListView):
    model = LostItem
    template_name = 'management/lost_item_list.html'
    context_object_name = 'lost_items'

    def get_queryset(self):
        qs = LostItem.objects.all()
        if self.request.user.role == 'owner':
            qs = qs.filter(status='pending')

        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['statuses'] = LostItem.STATUS_CHOICES
        context['current_status'] = self.request.GET.get('status', '')
        context['pending_count'] = LostItem.objects.filter(status='pending').count()
        context['claimed_count'] = LostItem.objects.filter(status='claimed').count()
        return context


class LostItemCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = LostItem
    form_class = LostItemForm
    template_name = 'management/form.html'
    success_url = reverse_lazy('lost_item_list')

    def form_valid(self, form):
        form.instance.reporter = self.request.user
        messages.success(self.request, "失物信息发布成功！")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "发布拾获物品信息"
        return context


class LostItemDetailView(LoginRequiredMixin, DetailView):
    model = LostItem
    template_name = 'management/lost_item_detail.html'
    context_object_name = 'lost_item'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        item = context['lost_item']
        context['claims'] = item.claims.all()
        if self.request.user.role == 'owner' and item.status == 'pending':
            context['has_applied'] = item.claims.filter(applicant=self.request.user).exists()
        return context


class LostItemUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = LostItem
    form_class = LostItemForm
    template_name = 'management/form.html'
    success_url = reverse_lazy('lost_item_list')

    def form_valid(self, form):
        messages.success(self.request, "失物信息更新成功！")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "编辑失物信息"
        return context


class LostItemDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = LostItem
    template_name = 'management/confirm_delete.html'
    success_url = reverse_lazy('lost_item_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "失物信息删除成功！")
        return super().delete(request, *args, **kwargs)


class ClaimCreateView(LoginRequiredMixin, CreateView):
    model = ClaimApplication
    form_class = ClaimApplicationForm
    template_name = 'management/claim_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lost_item'] = get_object_or_404(LostItem, pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        lost_item = get_object_or_404(LostItem, pk=self.kwargs['pk'])
        if lost_item.status != 'pending':
            messages.error(self.request, "该物品已不在待认领状态！")
            return redirect(reverse('lost_item_detail', kwargs={'pk': lost_item.pk}))
        if lost_item.claims.filter(applicant=self.request.user).exists():
            messages.error(self.request, "您已提交过认领申请！")
            return redirect(reverse('lost_item_detail', kwargs={'pk': lost_item.pk}))
        form.instance.lost_item = lost_item
        form.instance.applicant = self.request.user
        messages.success(self.request, "认领申请提交成功，请等待物业审核！")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('lost_item_detail', kwargs={'pk': self.kwargs['pk']})


class ClaimConfirmView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = ClaimApplication
    form_class = ClaimConfirmForm
    template_name = 'management/claim_form.html'
    success_url = reverse_lazy('lost_item_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['claim'] = self.get_object()
        context['lost_item'] = context['claim'].lost_item
        context['is_confirm'] = True
        return context

    def form_valid(self, form):
        form.instance.status = 'approved'
        form.instance.handler = self.request.user
        response = super().form_valid(form)
        lost_item = form.instance.lost_item
        lost_item.status = 'claimed'
        lost_item.save(update_fields=['status', 'updated_at'])
        form.instance.lost_item.claims.exclude(pk=form.instance.pk).update(status='rejected')
        messages.success(self.request, "认领确认成功，物品状态已更新为已认领！")
        return response


class ClaimRejectView(LoginRequiredMixin, StaffRequiredMixin, View):
    def post(self, request, pk):
        claim = get_object_or_404(ClaimApplication, pk=pk)
        if claim.status != 'pending':
            messages.error(request, "该申请已处理！")
            return redirect(reverse('lost_item_detail', kwargs={'pk': claim.lost_item.pk}))
        claim.status = 'rejected'
        claim.handler = request.user
        claim.save(update_fields=['status', 'handler', 'updated_at'])
        messages.success(request, "认领申请已驳回！")
        return redirect(reverse('lost_item_detail', kwargs={'pk': claim.lost_item.pk}))


class OwnerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role == 'owner'


class TemporaryParkingApplicationListView(LoginRequiredMixin, ListView):
    model = TemporaryParkingApplication
    template_name = 'management/temporary_parking_list.html'
    context_object_name = 'applications'

    def get_queryset(self):
        from django.utils import timezone
        now = timezone.now()
        qs = TemporaryParkingApplication.objects.all()
        if self.request.user.role == 'owner':
            qs = qs.filter(applicant=self.request.user)
        for app in qs:
            app.current_status = app.get_current_status()
            if app.status == 'approved' and app.current_status == 'expired':
                app.update_expired_status()
        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)
        return qs.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['statuses'] = TemporaryParkingApplication.STATUS_CHOICES
        context['current_status'] = self.request.GET.get('status', '')
        return context


class TemporaryParkingApplicationCreateView(LoginRequiredMixin, OwnerRequiredMixin, CreateView):
    model = TemporaryParkingApplication
    form_class = TemporaryParkingApplicationForm
    template_name = 'management/form.html'
    success_url = reverse_lazy('temporary_parking_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['owner'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.applicant = self.request.user
        messages.success(self.request, "临时停车申请提交成功，请等待物业审核！")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "临时停车申请"
        return context


class TemporaryParkingApplicationDetailView(LoginRequiredMixin, DetailView):
    model = TemporaryParkingApplication
    template_name = 'management/temporary_parking_detail.html'
    context_object_name = 'application'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        app = context['application']
        app.current_status = app.get_current_status()
        if app.status == 'approved' and app.current_status == 'expired':
            app.update_expired_status()
        if hasattr(app, 'permit'):
            app.permit.update_status_if_expired()
            context['permit'] = app.permit
        context['can_review'] = self.request.user.role in ['admin', 'staff'] and app.status == 'pending'
        return context


class TemporaryParkingReviewListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = TemporaryParkingApplication
    template_name = 'management/temporary_parking_review_list.html'
    context_object_name = 'applications'

    def get_queryset(self):
        qs = TemporaryParkingApplication.objects.filter(status='pending').order_by('-created_at')
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pending_count'] = TemporaryParkingApplication.objects.filter(status='pending').count()
        context['approved_count'] = TemporaryParkingApplication.objects.filter(status='approved').count()
        context['rejected_count'] = TemporaryParkingApplication.objects.filter(status='rejected').count()
        context['expired_count'] = TemporaryParkingApplication.objects.filter(status='expired').count()
        return context


class TemporaryParkingReviewView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = TemporaryParkingApplication
    form_class = TemporaryParkingReviewForm
    template_name = 'management/temporary_parking_review.html'
    success_url = reverse_lazy('temporary_parking_review_list')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.status != 'pending':
            messages.error(self.request, "该申请已处理！")
            from django.http import HttpResponseRedirect
            return HttpResponseRedirect(reverse('temporary_parking_review_list'))
        return obj

    def form_valid(self, form):
        from django.utils import timezone
        from datetime import datetime
        form.instance.reviewer = self.request.user
        form.instance.reviewed_at = timezone.now()
        response = super().form_valid(form)
        if form.instance.status == 'approved':
            permit_no = f"TP{datetime.now().strftime('%Y%m%d')}{form.instance.pk:06d}"
            TemporaryParkingPermit.objects.create(
                application=form.instance,
                permit_no=permit_no,
                status='active'
            )
            messages.success(self.request, "审核通过，停车许可已生成！")
        else:
            messages.success(self.request, "审核已驳回！")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "审核临时停车申请"
        context['application'] = self.get_object()
        return context


class TemporaryParkingGateQueryView(LoginRequiredMixin, StaffRequiredMixin, TemplateView):
    template_name = 'management/temporary_parking_gate_query.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        license_plate = self.request.GET.get('license_plate', '').strip()
        context['license_plate'] = license_plate
        if license_plate:
            from datetime import date, datetime, time
            today = date.today()
            now = datetime.now()
            permits = TemporaryParkingPermit.objects.filter(
                application__license_plate__icontains=license_plate,
                status='active'
            ).select_related('application')
            valid_permits = []
            for permit in permits:
                permit.update_status_if_expired()
                app = permit.application
                end_datetime = datetime.combine(app.visit_date, app.stay_end)
                if permit.status == 'active' and today == app.visit_date and now <= end_datetime:
                    valid_permits.append(permit)
            context['permits'] = valid_permits
            context['search_performed'] = True
        return context


class TemporaryParkingPermitDetailView(LoginRequiredMixin, StaffRequiredMixin, DetailView):
    model = TemporaryParkingPermit
    template_name = 'management/temporary_parking_permit_detail.html'
    context_object_name = 'permit'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status_if_expired()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        permit = context['permit']
        from datetime import date, datetime
        today = date.today()
        now = datetime.now()
        app = permit.application
        end_datetime = datetime.combine(app.visit_date, app.stay_end)
        context['is_valid_now'] = permit.status == 'active' and today == app.visit_date and now <= end_datetime
        return context
