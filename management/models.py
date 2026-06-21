from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', '系统管理员'),
        ('staff', '物业工作人员'),
        ('owner', '业主'),
    )
    role = models.CharField("角色", max_length=10, choices=ROLE_CHOICES, default='owner')
    phone = models.CharField("联系电话", max_length=20, blank=True, null=True)

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = "用户管理"

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class Estate(models.Model):
    name = models.CharField("楼盘名称", max_length=100)
    address = models.CharField("楼盘地址", max_length=255)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        verbose_name = "楼盘"
        verbose_name_plural = "楼盘管理"

    def __str__(self):
        return self.name

class Building(models.Model):
    estate = models.ForeignKey(Estate, on_delete=models.CASCADE, verbose_name="所属楼盘", related_name="buildings")
    name = models.CharField("楼栋名称", max_length=50)

    class Meta:
        verbose_name = "楼栋"
        verbose_name_plural = "楼栋管理"

    def __str__(self):
        return f"{self.estate.name} - {self.name}"

class Floor(models.Model):
    building = models.ForeignKey(Building, on_delete=models.CASCADE, verbose_name="所属楼栋", related_name="floors")
    name = models.CharField("楼层名称", max_length=50)

    class Meta:
        verbose_name = "楼层"
        verbose_name_plural = "楼层管理"

    def __str__(self):
        return f"{self.building} - {self.name}"

class Unit(models.Model):
    floor = models.ForeignKey(Floor, on_delete=models.CASCADE, verbose_name="所属楼层", related_name="units")
    name = models.CharField("单元名称(房号)", max_length=50)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="所属业主", related_name="properties", limit_choices_to={'role': 'owner'})
    area = models.DecimalField("面积(平米)", max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        verbose_name = "单元/房屋"
        verbose_name_plural = "单元/房屋管理"

    def __str__(self):
        return f"{self.floor} - {self.name}"

class Supplier(models.Model):
    SERVICE_CATEGORY_CHOICES = (
        ('water_electric', '水电维修'),
        ('elevator', '电梯维保'),
        ('greening', '绿化养护'),
        ('cleaning', '保洁服务'),
        ('security', '安保服务'),
        ('fire_control', '消防维保'),
        ('air_condition', '空调维保'),
        ('other', '其他服务'),
    )
    COOPERATION_STATUS_CHOICES = (
        ('active', '合作中'),
        ('inactive', '已停用'),
    )

    name = models.CharField("供应商名称", max_length=100)
    contact_person = models.CharField("联系人", max_length=50)
    phone = models.CharField("联系电话", max_length=20)
    service_category = models.CharField("服务类别", max_length=30, choices=SERVICE_CATEGORY_CHOICES)
    cooperation_status = models.CharField("合作状态", max_length=20, choices=COOPERATION_STATUS_CHOICES, default='active')
    address = models.CharField("地址", max_length=255, blank=True, null=True)
    remark = models.TextField("备注", blank=True, null=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "供应商"
        verbose_name_plural = "供应商管理"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_service_category_display()})"


class Repair(models.Model):
    TYPE_CHOICES = (
        ('water_electric', '水电维修'),
        ('door_window', '门窗维修'),
        ('public', '公共设施'),
        ('other', '其他'),
    )
    STATUS_CHOICES = (
        ('pending', '待处理'),
        ('processing', '处理中'),
        ('completed', '已完成'),
    )
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="提交业主", related_name="repairs")
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="相关房屋")
    fault_type = models.CharField("故障类型", max_length=20, choices=TYPE_CHOICES)
    location = models.CharField("故障位置", max_length=100)
    description = models.TextField("故障描述")
    status = models.CharField("状态", max_length=20, choices=STATUS_CHOICES, default='pending')
    
    processor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="处理人", related_name="handled_repairs", limit_choices_to={'role': 'staff'})
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="委外供应商", related_name="repairs")
    feedback = models.TextField("物业处理反馈", blank=True, null=True)
    
    submit_time = models.DateTimeField("提交时间", auto_now_add=True)
    update_time = models.DateTimeField("最后更新时间", auto_now=True)

    class Meta:
        verbose_name = "报修单"
        verbose_name_plural = "报修管理"
        ordering = ['-submit_time']

    def __str__(self):
        return f"报修单 #{self.id} - {self.get_fault_type_display()}"


class Fee(models.Model):
    FEE_TYPES = (
        ('property', '物业费'),
        ('water', '水费'),
        ('electric', '电费'),
        ('other', '其他费用'),
    )
    STATUS_CHOICES = (
        ('unpaid', '未支付'),
        ('paid', '已支付'),
    )
    PAYMENT_METHODS = (
        ('wechat', '微信'),
        ('alipay', '支付宝'),
        ('bank', '银行转账'),
        ('cash', '现金'),
    )
    
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, verbose_name="相关房屋", related_name="fees")
    fee_type = models.CharField("费用类型", max_length=20, choices=FEE_TYPES)
    amount = models.DecimalField("金额", max_digits=10, decimal_places=2)
    generated_date = models.DateField("生成日期", auto_now_add=True)
    due_date = models.DateField("截止日期")
    status = models.CharField("状态", max_length=20, choices=STATUS_CHOICES, default='unpaid')
    
    payment_date = models.DateField("收款日期", null=True, blank=True)
    payment_method = models.CharField("收款方式", max_length=20, choices=PAYMENT_METHODS, null=True, blank=True)
    
    class Meta:
        verbose_name = "账单记录"
        verbose_name_plural = "费用管理"
        ordering = ['-generated_date']

    def __str__(self):
        return f"{self.unit} - {self.get_fee_type_display()} - {self.amount}元"


class Contract(models.Model):
    TYPE_CHOICES = (
        ('owner_service', '业主服务'),
        ('supplier_purchase', '供应商采购'),
        ('outsourcing_maintenance', '外包维保'),
    )
    PAYMENT_METHODS = (
        ('one_time', '一次性付款'),
        ('installment', '分期付款'),
        ('annual', '年付'),
        ('quarterly', '季付'),
        ('monthly', '月付'),
        ('other', '其他'),
    )

    contract_no = models.CharField("合同编号", max_length=50, unique=True)
    contract_type = models.CharField("合同类型", max_length=30, choices=TYPE_CHOICES)
    related_object = models.CharField("关联对象", max_length=200)
    sign_date = models.DateField("签约日期")
    expire_date = models.DateField("到期日期")
    amount = models.DecimalField("合同金额", max_digits=12, decimal_places=2)
    payment_method = models.CharField("付款方式", max_length=20, choices=PAYMENT_METHODS)
    remark = models.TextField("备注", blank=True, null=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "物业合同"
        verbose_name_plural = "合同管理"
        ordering = ['expire_date']

    def __str__(self):
        return f"{self.contract_no} - {self.get_contract_type_display()}"

    def is_expiring_soon(self, days=60):
        from datetime import date
        return 0 <= (self.expire_date - date.today()).days <= days

    def days_until_expire(self):
        from datetime import date
        return (self.expire_date - date.today()).days


class ContractAttachment(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, verbose_name="所属合同", related_name="attachments")
    file = models.FileField("附件文件", upload_to="contract_attachments/%Y/%m/")
    file_name = models.CharField("文件名", max_length=255, blank=True)
    uploaded_at = models.DateTimeField("上传时间", auto_now_add=True)

    class Meta:
        verbose_name = "合同附件"
        verbose_name_plural = "合同附件"

    def __str__(self):
        return self.file_name or self.file.name

    def save(self, *args, **kwargs):
        if not self.file_name and self.file:
            self.file_name = self.file.name
        super().save(*args, **kwargs)


class GreeningMaintenance(models.Model):
    TYPE_CHOICES = (
        ('pruning', '修剪'),
        ('fertilizing', '施肥'),
        ('pest_control', '除虫'),
        ('replanting', '补植'),
    )

    estate = models.ForeignKey(Estate, on_delete=models.CASCADE, verbose_name="养护区域", related_name="greening_maintenances")
    maintenance_type = models.CharField("养护类型", max_length=20, choices=TYPE_CHOICES)
    work_date = models.DateField("作业日期")
    worker = models.CharField("作业人员", max_length=100)
    materials = models.TextField("所用物料", blank=True, null=True)
    description = models.TextField("作业描述", blank=True, null=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "绿化养护记录"
        verbose_name_plural = "绿化养护管理"
        ordering = ['-work_date', '-created_at']

    def __str__(self):
        return f"{self.estate.name} - {self.get_maintenance_type_display()} - {self.work_date}"


class SafetyInspection(models.Model):
    RISK_LEVEL_CHOICES = (
        ('high', '高风险'),
        ('medium', '中风险'),
        ('low', '低风险'),
    )
    STATUS_CHOICES = (
        ('open', '未消项'),
        ('closed', '已消项'),
    )

    estate = models.ForeignKey(Estate, on_delete=models.CASCADE, verbose_name="所属楼盘", related_name="safety_inspections")
    inspection_area = models.CharField("排查区域", max_length=200)
    hazard_description = models.TextField("隐患描述")
    risk_level = models.CharField("风险等级", max_length=10, choices=RISK_LEVEL_CHOICES)
    discovery_date = models.DateField("发现日期")
    rectification_deadline = models.DateField("整改期限")
    site_remark = models.TextField("现场备注", blank=True, null=True)
    status = models.CharField("消项状态", max_length=10, choices=STATUS_CHOICES, default='open')
    rectification_measures = models.TextField("整改措施", blank=True, null=True)
    completion_date = models.DateField("完成日期", blank=True, null=True)

    inspector = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="排查人", related_name="inspected_hazards", limit_choices_to={'role__in': ['admin', 'staff']})
    rectifier = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="整改人", related_name="rectified_hazards", limit_choices_to={'role__in': ['admin', 'staff']})

    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "安全隐患排查记录"
        verbose_name_plural = "安全隐患排查管理"
        ordering = ['-discovery_date', '-created_at']

    def __str__(self):
        return f"[{self.get_risk_level_display()}] {self.inspection_area} - {self.discovery_date}"

    def is_overdue(self):
        from datetime import date
        return self.status == 'open' and self.rectification_deadline < date.today()

    def days_until_deadline(self):
        from datetime import date
        return (self.rectification_deadline - date.today()).days


class SafetyInspectionTrack(models.Model):
    ACTION_CHOICES = (
        ('create', '创建记录'),
        ('update', '更新记录'),
        ('rectify', '提交整改'),
        ('close', '标记消项'),
        ('reopen', '重新开启'),
        ('remark', '添加备注'),
    )

    inspection = models.ForeignKey(SafetyInspection, on_delete=models.CASCADE, verbose_name="关联隐患", related_name="tracks")
    action = models.CharField("操作类型", max_length=20, choices=ACTION_CHOICES)
    operator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="操作人")
    remark = models.TextField("操作说明", blank=True, null=True)
    created_at = models.DateTimeField("操作时间", auto_now_add=True)

    class Meta:
        verbose_name = "隐患处理轨迹"
        verbose_name_plural = "隐患处理轨迹"
        ordering = ['created_at']

    def __str__(self):
        return f"{self.inspection.id} - {self.get_action_display()} - {self.created_at}"


class Vote(models.Model):
    STATUS_CHOICES = (
        ('pending', '未开始'),
        ('active', '进行中'),
        ('closed', '已结束'),
    )

    title = models.CharField("投票议题", max_length=200)
    description = models.TextField("投票说明", blank=True, null=True)
    start_time = models.DateTimeField("开始时间")
    end_time = models.DateTimeField("结束时间")
    allow_multiple = models.BooleanField("允许多选", default=False)
    is_anonymous = models.BooleanField("匿名计票", default=False)
    status = models.CharField("投票状态", max_length=10, choices=STATUS_CHOICES, default='pending')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="发起人", related_name="created_votes", limit_choices_to={'role__in': ['admin', 'staff']})
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "社区投票"
        verbose_name_plural = "投票管理"
        ordering = ['-created_at']

    def __str__(self):
        return f"投票 #{self.id} - {self.title}"

    def total_votes(self):
        return self.voter_records.count()

    def has_voted(self, user):
        return self.voter_records.filter(voter=user).exists()


class VoteOption(models.Model):
    vote = models.ForeignKey(Vote, on_delete=models.CASCADE, verbose_name="所属投票", related_name="options")
    content = models.CharField("选项内容", max_length=200)

    class Meta:
        verbose_name = "投票选项"
        verbose_name_plural = "投票选项"
        ordering = ['id']

    def __str__(self):
        return f"{self.vote.title} - {self.content}"

    def vote_count(self):
        return self.ballots.count()

    def vote_percentage(self):
        total = self.vote.total_votes()
        if total == 0:
            return 0
        return round(self.vote_count() / total * 100, 1)


class VoteBallot(models.Model):
    vote = models.ForeignKey(Vote, on_delete=models.CASCADE, verbose_name="所属投票", related_name="ballot_records")
    option = models.ForeignKey(VoteOption, on_delete=models.CASCADE, verbose_name="所选选项", related_name="ballots")
    voter = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="投票人", related_name="cast_ballots", null=True, blank=True)
    created_at = models.DateTimeField("投票时间", auto_now_add=True)

    class Meta:
        verbose_name = "投票记录"
        verbose_name_plural = "投票记录"


class LostItem(models.Model):
    STATUS_CHOICES = (
        ('pending', '待认领'),
        ('claimed', '已认领'),
    )

    name = models.CharField("物品名称", max_length=100)
    found_location = models.CharField("拾取地点", max_length=200)
    found_date = models.DateField("拾取日期")
    description = models.TextField("物品描述", blank=True, null=True)
    storage_location = models.CharField("存放地点", max_length=200)
    status = models.CharField("当前状态", max_length=10, choices=STATUS_CHOICES, default='pending')

    reporter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="登记人", related_name="reported_lost_items", limit_choices_to={'role__in': ['admin', 'staff']})
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "失物招领"
        verbose_name_plural = "失物招领管理"
        ordering = ['-found_date', '-created_at']

    def __str__(self):
        return f"失物 #{self.id} - {self.name}"


class ClaimApplication(models.Model):
    STATUS_CHOICES = (
        ('pending', '待审核'),
        ('approved', '已通过'),
        ('rejected', '已驳回'),
    )

    lost_item = models.ForeignKey(LostItem, on_delete=models.CASCADE, verbose_name="关联失物", related_name="claims")
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="认领申请人", related_name="claim_applications")
    claim_description = models.TextField("认领说明")
    contact_info = models.CharField("联系方式", max_length=100)
    status = models.CharField("审核状态", max_length=10, choices=STATUS_CHOICES, default='pending')

    claimant = models.CharField("认领人", max_length=100, blank=True, null=True)
    claim_date = models.DateField("认领日期", blank=True, null=True)
    handler = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="经办人", related_name="handled_claims", limit_choices_to={'role__in': ['admin', 'staff']})

    created_at = models.DateTimeField("申请时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "认领申请"
        verbose_name_plural = "认领申请管理"
        ordering = ['-created_at']

    def __str__(self):
        return f"认领申请 #{self.id} - {self.lost_item.name}"


class VoteRecord(models.Model):
    vote = models.ForeignKey(Vote, on_delete=models.CASCADE, verbose_name="所属投票", related_name="voter_records")
    voter = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="投票业主", related_name="vote_participations")
    voted_at = models.DateTimeField("投票时间", auto_now_add=True)

    class Meta:
        verbose_name = "业主投票参与记录"
        verbose_name_plural = "业主投票参与记录"
        unique_together = ['vote', 'voter']


class TemporaryParkingApplication(models.Model):
    STATUS_CHOICES = (
        ('pending', '待审核'),
        ('approved', '已通过'),
        ('rejected', '已驳回'),
        ('expired', '已失效'),
    )

    applicant = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="申请人", related_name="parking_applications", limit_choices_to={'role': 'owner'})
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, verbose_name="关联房屋", related_name="parking_applications")
    license_plate = models.CharField("车牌号", max_length=20)
    visit_date = models.DateField("来访日期")
    stay_start = models.TimeField("停留开始时间")
    stay_end = models.TimeField("停留结束时间")
    visit_reason = models.TextField("来访事由")
    contact_phone = models.CharField("联系人电话", max_length=20)
    status = models.CharField("申请状态", max_length=10, choices=STATUS_CHOICES, default='pending')

    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="审核人", related_name="reviewed_parking_applications", limit_choices_to={'role__in': ['admin', 'staff']})
    review_remark = models.TextField("审核备注", blank=True, null=True)
    reviewed_at = models.DateTimeField("审核时间", null=True, blank=True)

    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "临时停车申请"
        verbose_name_plural = "临时停车申请管理"
        ordering = ['-created_at']

    def __str__(self):
        return f"停车申请 #{self.id} - {self.license_plate}"

    def update_expired_status(self):
        from datetime import date, time, datetime
        now = datetime.now()
        end_datetime = datetime.combine(self.visit_date, self.stay_end)
        if self.status == 'approved' and now > end_datetime:
            self.status = 'expired'
            self.save(update_fields=['status', 'updated_at'])
            return True
        return False

    def get_current_status(self):
        from datetime import date, time, datetime
        now = datetime.now()
        end_datetime = datetime.combine(self.visit_date, self.stay_end)
        if self.status == 'approved' and now > end_datetime:
            return 'expired'
        return self.status


class TemporaryParkingPermit(models.Model):
    STATUS_CHOICES = (
        ('active', '有效'),
        ('expired', '已失效'),
    )

    application = models.OneToOneField(TemporaryParkingApplication, on_delete=models.CASCADE, verbose_name="关联申请", related_name="permit")
    permit_no = models.CharField("许可编号", max_length=50, unique=True)
    status = models.CharField("许可状态", max_length=10, choices=STATUS_CHOICES, default='active')
    generated_at = models.DateTimeField("生成时间", auto_now_add=True)

    class Meta:
        verbose_name = "临时停车许可"
        verbose_name_plural = "临时停车许可管理"
        ordering = ['-generated_at']

    def __str__(self):
        return f"停车许可 {self.permit_no} - {self.application.license_plate}"

    def is_valid_today(self):
        from datetime import date, time, datetime
        today = date.today()
        now = datetime.now()
        app = self.application
        end_datetime = datetime.combine(app.visit_date, app.stay_end)
        return self.status == 'active' and today == app.visit_date and now <= end_datetime

    def update_status_if_expired(self):
        from datetime import date, time, datetime
        now = datetime.now()
        app = self.application
        end_datetime = datetime.combine(app.visit_date, app.stay_end)
        if self.status == 'active' and now > end_datetime:
            self.status = 'expired'
            self.save(update_fields=['status'])
            app.status = 'expired'
            app.save(update_fields=['status', 'updated_at'])
            return True
        return False


class NeighborhoodHelpPost(models.Model):
    TYPE_CHOICES = (
        ('borrow', '求借'),
        ('gift', '赠送'),
        ('inquiry', '问询'),
    )

    post_type = models.CharField("帖子类型", max_length=20, choices=TYPE_CHOICES)
    title = models.CharField("标题", max_length=200)
    content = models.TextField("正文")
    show_contact = models.BooleanField("是否公开联系方式", default=False)

    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="发帖人", related_name="help_posts")
    created_at = models.DateTimeField("发布时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "邻里互助帖子"
        verbose_name_plural = "邻里互助管理"
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_post_type_display()}] {self.title}"

    def reply_count(self):
        return self.replies.count()


class NeighborhoodHelpReply(models.Model):
    post = models.ForeignKey(NeighborhoodHelpPost, on_delete=models.CASCADE, verbose_name="所属帖子", related_name="replies")
    content = models.TextField("留言内容")
    replier = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="留言人", related_name="help_replies")
    created_at = models.DateTimeField("留言时间", auto_now_add=True)

    class Meta:
        verbose_name = "邻里互助留言"
        verbose_name_plural = "邻里互助留言"
        ordering = ['created_at']

    def __str__(self):
        return f"{self.replier.username} - {self.content[:30]}"
