from django import forms
from django.forms import inlineformset_factory
from .models import User, Estate, Building, Floor, Unit, Repair, Fee, Contract, ContractAttachment, Supplier, GreeningMaintenance, SafetyInspection, SafetyInspectionTrack, Vote, VoteOption, LostItem, ClaimApplication, TemporaryParkingApplication, TemporaryParkingPermit, NeighborhoodHelpPost, NeighborhoodHelpReply, EmergencyContact, DeliveryOrder, DeliveryInspectionItem

class OwnerForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'phone']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class EstateForm(forms.ModelForm):
    class Meta:
        model = Estate
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
        }

class BuildingForm(forms.ModelForm):
    class Meta:
        model = Building
        fields = '__all__'
        widgets = {
            'estate': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class FloorForm(forms.ModelForm):
    class Meta:
        model = Floor
        fields = '__all__'
        widgets = {
            'building': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = '__all__'
        widgets = {
            'floor': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'owner': forms.Select(attrs={'class': 'form-select'}),
            'area': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class RepairStaffForm(forms.ModelForm):
    class Meta:
        model = Repair
        fields = ['status', 'processor', 'supplier', 'feedback']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'processor': forms.Select(attrs={'class': 'form-select'}),
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'feedback': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['supplier'].queryset = Supplier.objects.filter(cooperation_status='active')
        self.fields['supplier'].empty_label = "请选择委外供应商（可选）"

class RepairOwnerForm(forms.ModelForm):
    class Meta:
        model = Repair
        fields = ['unit', 'fault_type', 'location', 'description']
        widgets = {
            'unit': forms.Select(attrs={'class': 'form-select'}),
            'fault_type': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        
    def __init__(self, *args, **kwargs):
        owner = kwargs.pop('owner', None)
        super().__init__(*args, **kwargs)
        if owner:
            # 只显示属于当前业主的房产
            self.fields['unit'].queryset = Unit.objects.filter(owner=owner)

class FeeForm(forms.ModelForm):
    class Meta:
        model = Fee
        fields = '__all__'
        widgets = {
            'unit': forms.Select(attrs={'class': 'form-select'}),
            'fee_type': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'payment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
        }


class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = ['contract_no', 'contract_type', 'related_object', 'sign_date', 'expire_date', 'amount', 'payment_method', 'remark']
        widgets = {
            'contract_no': forms.TextInput(attrs={'class': 'form-control'}),
            'contract_type': forms.Select(attrs={'class': 'form-select'}),
            'related_object': forms.TextInput(attrs={'class': 'form-control'}),
            'sign_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expire_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ContractAttachmentForm(forms.ModelForm):
    class Meta:
        model = ContractAttachment
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
        }


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'phone', 'service_category', 'cooperation_status', 'address', 'remark']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'service_category': forms.Select(attrs={'class': 'form-select'}),
            'cooperation_status': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class GreeningMaintenanceForm(forms.ModelForm):
    class Meta:
        model = GreeningMaintenance
        fields = ['estate', 'maintenance_type', 'work_date', 'worker', 'materials', 'description']
        widgets = {
            'estate': forms.Select(attrs={'class': 'form-select'}),
            'maintenance_type': forms.Select(attrs={'class': 'form-select'}),
            'work_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'worker': forms.TextInput(attrs={'class': 'form-control'}),
            'materials': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': '请输入所用物料，如：复合肥5kg、杀虫剂3瓶等'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '请输入作业描述'}),
        }


class SafetyInspectionCreateForm(forms.ModelForm):
    class Meta:
        model = SafetyInspection
        fields = ['estate', 'inspection_area', 'hazard_description', 'risk_level', 'discovery_date', 'rectification_deadline', 'site_remark']
        widgets = {
            'estate': forms.Select(attrs={'class': 'form-select'}),
            'inspection_area': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入排查区域，如：3号楼2层消防通道'}),
            'hazard_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': '请详细描述隐患情况'}),
            'risk_level': forms.Select(attrs={'class': 'form-select'}),
            'discovery_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'rectification_deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'site_remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': '请输入现场备注（可选）'}),
        }


class SafetyInspectionRectifyForm(forms.ModelForm):
    class Meta:
        model = SafetyInspection
        fields = ['rectification_measures', 'completion_date']
        widgets = {
            'rectification_measures': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': '请详细填写整改措施'}),
            'completion_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rectification_measures'].required = True
        self.fields['completion_date'].required = True


class SafetyInspectionUpdateForm(forms.ModelForm):
    class Meta:
        model = SafetyInspection
        fields = ['estate', 'inspection_area', 'hazard_description', 'risk_level', 'discovery_date', 'rectification_deadline', 'site_remark']
        widgets = {
            'estate': forms.Select(attrs={'class': 'form-select'}),
            'inspection_area': forms.TextInput(attrs={'class': 'form-control'}),
            'hazard_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'risk_level': forms.Select(attrs={'class': 'form-select'}),
            'discovery_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'rectification_deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'site_remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class VoteForm(forms.ModelForm):
    class Meta:
        model = Vote
        fields = ['title', 'description', 'start_time', 'end_time', 'allow_multiple', 'is_anonymous']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入投票议题'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '请输入投票说明（可选）'}),
            'start_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'allow_multiple': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_anonymous': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        if start_time and end_time and end_time <= start_time:
            raise forms.ValidationError("结束时间必须晚于开始时间")
        return cleaned_data


class VoteOptionForm(forms.ModelForm):
    class Meta:
        model = VoteOption
        fields = ['content']
        widgets = {
            'content': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入选项内容'}),
        }

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if content:
            content = content.strip()
            if not content:
                raise forms.ValidationError("选项内容不能为空")
        return content


VoteOptionFormSet = inlineformset_factory(
    Vote, VoteOption, form=VoteOptionForm,
    extra=2, min_num=2, validate_min=True, can_delete=True
)


class LostItemForm(forms.ModelForm):
    class Meta:
        model = LostItem
        fields = ['name', 'found_location', 'found_date', 'description', 'storage_location']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入物品名称'}),
            'found_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入拾取地点'}),
            'found_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '请输入物品描述（可选）'}),
            'storage_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入存放地点'}),
        }


class ClaimApplicationForm(forms.ModelForm):
    class Meta:
        model = ClaimApplication
        fields = ['claim_description', 'contact_info']
        widgets = {
            'claim_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': '请详细描述认领说明，如物品特征、遗失经过等'}),
            'contact_info': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入联系方式，如手机号'}),
        }


class ClaimConfirmForm(forms.ModelForm):
    class Meta:
        model = ClaimApplication
        fields = ['claimant', 'claim_date']
        widgets = {
            'claimant': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入认领人姓名'}),
            'claim_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['claimant'].required = True
        self.fields['claim_date'].required = True


class TemporaryParkingApplicationForm(forms.ModelForm):
    class Meta:
        model = TemporaryParkingApplication
        fields = ['unit', 'license_plate', 'visit_date', 'stay_start', 'stay_end', 'visit_reason', 'contact_phone']
        widgets = {
            'unit': forms.Select(attrs={'class': 'form-select'}),
            'license_plate': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入车牌号，如：京A12345'}),
            'visit_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'stay_start': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'stay_end': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'visit_reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '请输入来访事由'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入联系人电话'}),
        }

    def __init__(self, *args, **kwargs):
        owner = kwargs.pop('owner', None)
        super().__init__(*args, **kwargs)
        if owner:
            self.fields['unit'].queryset = Unit.objects.filter(owner=owner)
        self.fields['unit'].empty_label = "请选择关联房屋"

    def clean(self):
        cleaned_data = super().clean()
        stay_start = cleaned_data.get('stay_start')
        stay_end = cleaned_data.get('stay_end')
        visit_date = cleaned_data.get('visit_date')
        from datetime import date, datetime
        if visit_date and visit_date < date.today():
            raise forms.ValidationError("来访日期不能早于今日")
        if stay_start and stay_end and stay_end <= stay_start:
            raise forms.ValidationError("停留结束时间必须晚于开始时间")
        return cleaned_data


class TemporaryParkingReviewForm(forms.ModelForm):
    class Meta:
        model = TemporaryParkingApplication
        fields = ['status', 'review_remark']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}, choices=[('approved', '已通过'), ('rejected', '已驳回')]),
            'review_remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '请输入审核备注（可选）'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].required = True
        self.fields['status'].empty_label = None


class NeighborhoodHelpPostForm(forms.ModelForm):
    class Meta:
        model = NeighborhoodHelpPost
        fields = ['post_type', 'title', 'content', 'show_contact']
        widgets = {
            'post_type': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入帖子标题'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': '请详细描述您的需求或提供的帮助'}),
            'show_contact': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['post_type'].empty_label = "请选择帖子类型"
        self.fields['show_contact'].help_text = "勾选后其他业主可看到您的联系方式"


class NeighborhoodHelpReplyForm(forms.ModelForm):
    class Meta:
        model = NeighborhoodHelpReply
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '请留下您的简短留言或联系方式'}),
        }


class EmergencyContactForm(forms.ModelForm):
    class Meta:
        model = EmergencyContact
        fields = ['category', 'name', 'phone', 'service_hours', 'remark']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入联系人名称'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入电话号码'}),
            'service_hours': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '如：24小时、工作日 8:00-18:00'}),
            'remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': '备注信息（可选）'}),
        }


class DeliveryOrderCreateForm(forms.ModelForm):
    class Meta:
        model = DeliveryOrder
        fields = ['unit', 'delivery_date', 'remark']
        widgets = {
            'unit': forms.Select(attrs={'class': 'form-select'}),
            'delivery_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '请输入备注（可选）'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['unit'].empty_label = "请选择房屋单元"


class DeliveryInspectionItemForm(forms.ModelForm):
    class Meta:
        model = DeliveryInspectionItem
        fields = ['item_name', 'status', 'staff_remark']
        widgets = {
            'item_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入验收项目名称'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'staff_remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': '请输入验收备注（可选）'}),
        }


DeliveryInspectionItemFormSet = inlineformset_factory(
    DeliveryOrder, DeliveryInspectionItem, form=DeliveryInspectionItemForm,
    extra=5, min_num=1, validate_min=True, can_delete=True
)


class DeliveryInspectionItemUpdateForm(forms.ModelForm):
    class Meta:
        model = DeliveryInspectionItem
        fields = ['status', 'staff_remark']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'staff_remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': '请输入验收备注（可选）'}),
        }


class DeliveryInspectionItemOwnerForm(forms.ModelForm):
    confirm = forms.BooleanField(label="我已确认该整改项", required=False)

    class Meta:
        model = DeliveryInspectionItem
        fields = ['owner_remark']
        widgets = {
            'owner_remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '请输入确认意见或补充说明（可选）'}),
        }
