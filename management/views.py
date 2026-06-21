from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView, DetailView, View
from django.contrib import messages
from datetime import date, timedelta
from .models import User, Estate, Building, Floor, Unit, Repair, Fee, Contract, ContractAttachment
from .forms import EstateForm, BuildingForm, FloorForm, UnitForm, OwnerForm, RepairOwnerForm, RepairStaffForm, FeeForm, ContractForm, ContractAttachmentForm
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
            sixty_days_later = today + timedelta(days=60)
            expiring_contracts = Contract.objects.filter(expire_date__gte=today, expire_date__lte=sixty_days_later).order_by('expire_date')
            context['expiring_contracts_count'] = expiring_contracts.count()
            context['expiring_contracts'] = expiring_contracts[:5]
            context['expiring_contracts_total_amount'] = sum(c.amount for c in expiring_contracts)
        else:
            context['my_units'] = Unit.objects.filter(owner=self.request.user)
            context['my_repairs'] = Repair.objects.filter(owner=self.request.user).order_by('-submit_time')[:5]
            context['unpaid_fees'] = Fee.objects.filter(unit__owner=self.request.user, status='unpaid')
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
