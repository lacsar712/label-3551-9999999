from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django.contrib.auth.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('role', models.CharField(choices=[('admin', '系统管理员'), ('staff', '物业工作人员'), ('owner', '业主')], default='owner', max_length=10, verbose_name='角色')),
                ('phone', models.CharField(blank=True, max_length=20, null=True, verbose_name='联系电话')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': '用户',
                'verbose_name_plural': '用户管理',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Estate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='楼盘名称')),
                ('address', models.CharField(max_length=255, verbose_name='楼盘地址')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
            ],
            options={
                'verbose_name': '楼盘',
                'verbose_name_plural': '楼盘管理',
            },
        ),
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='供应商名称')),
                ('contact_person', models.CharField(max_length=50, verbose_name='联系人')),
                ('phone', models.CharField(max_length=20, verbose_name='联系电话')),
                ('service_category', models.CharField(choices=[('water_electric', '水电维修'), ('elevator', '电梯维保'), ('greening', '绿化养护'), ('cleaning', '保洁服务'), ('security', '安保服务'), ('fire_control', '消防维保'), ('air_condition', '空调维保'), ('other', '其他服务')], max_length=30, verbose_name='服务类别')),
                ('cooperation_status', models.CharField(choices=[('active', '合作中'), ('inactive', '已停用')], default='active', max_length=20, verbose_name='合作状态')),
                ('address', models.CharField(blank=True, max_length=255, null=True, verbose_name='地址')),
                ('remark', models.TextField(blank=True, null=True, verbose_name='备注')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '供应商',
                'verbose_name_plural': '供应商管理',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Building',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='楼栋名称')),
                ('estate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='buildings', to='management.estate', verbose_name='所属楼盘')),
            ],
            options={
                'verbose_name': '楼栋',
                'verbose_name_plural': '楼栋管理',
            },
        ),
        migrations.CreateModel(
            name='Floor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='楼层名称')),
                ('building', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='floors', to='management.building', verbose_name='所属楼栋')),
            ],
            options={
                'verbose_name': '楼层',
                'verbose_name_plural': '楼层管理',
            },
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='单元名称(房号)')),
                ('area', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, verbose_name='面积(平米)')),
                ('floor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='units', to='management.floor', verbose_name='所属楼层')),
                ('owner', models.ForeignKey(blank=True, limit_choices_to={'role': 'owner'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='properties', to=settings.AUTH_USER_MODEL, verbose_name='所属业主')),
            ],
            options={
                'verbose_name': '单元/房屋',
                'verbose_name_plural': '单元/房屋管理',
            },
        ),
        migrations.CreateModel(
            name='Repair',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fault_type', models.CharField(choices=[('water_electric', '水电维修'), ('door_window', '门窗维修'), ('public', '公共设施'), ('other', '其他')], max_length=20, verbose_name='故障类型')),
                ('location', models.CharField(max_length=100, verbose_name='故障位置')),
                ('description', models.TextField(verbose_name='故障描述')),
                ('status', models.CharField(choices=[('pending', '待处理'), ('processing', '处理中'), ('completed', '已完成')], default='pending', max_length=20, verbose_name='状态')),
                ('feedback', models.TextField(blank=True, null=True, verbose_name='物业处理反馈')),
                ('submit_time', models.DateTimeField(auto_now_add=True, verbose_name='提交时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='最后更新时间')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='repairs', to=settings.AUTH_USER_MODEL, verbose_name='提交业主')),
                ('processor', models.ForeignKey(blank=True, limit_choices_to={'role': 'staff'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='handled_repairs', to=settings.AUTH_USER_MODEL, verbose_name='处理人')),
                ('supplier', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='repairs', to='management.supplier', verbose_name='委外供应商')),
                ('unit', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='management.unit', verbose_name='相关房屋')),
            ],
            options={
                'verbose_name': '报修单',
                'verbose_name_plural': '报修管理',
                'ordering': ['-submit_time'],
            },
        ),
        migrations.CreateModel(
            name='Fee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fee_type', models.CharField(choices=[('property', '物业费'), ('water', '水费'), ('electric', '电费'), ('other', '其他费用')], max_length=20, verbose_name='费用类型')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='金额')),
                ('generated_date', models.DateField(auto_now_add=True, verbose_name='生成日期')),
                ('due_date', models.DateField(verbose_name='截止日期')),
                ('status', models.CharField(choices=[('unpaid', '未支付'), ('paid', '已支付')], default='unpaid', max_length=20, verbose_name='状态')),
                ('payment_date', models.DateField(blank=True, null=True, verbose_name='收款日期')),
                ('payment_method', models.CharField(blank=True, choices=[('wechat', '微信'), ('alipay', '支付宝'), ('bank', '银行转账'), ('cash', '现金')], max_length=20, null=True, verbose_name='收款方式')),
                ('unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fees', to='management.unit', verbose_name='相关房屋')),
            ],
            options={
                'verbose_name': '账单记录',
                'verbose_name_plural': '费用管理',
                'ordering': ['-generated_date'],
            },
        ),
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contract_no', models.CharField(max_length=50, unique=True, verbose_name='合同编号')),
                ('contract_type', models.CharField(choices=[('owner_service', '业主服务'), ('supplier_purchase', '供应商采购'), ('outsourcing_maintenance', '外包维保')], max_length=30, verbose_name='合同类型')),
                ('related_object', models.CharField(max_length=200, verbose_name='关联对象')),
                ('sign_date', models.DateField(verbose_name='签约日期')),
                ('expire_date', models.DateField(verbose_name='到期日期')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='合同金额')),
                ('payment_method', models.CharField(choices=[('one_time', '一次性付款'), ('installment', '分期付款'), ('annual', '年付'), ('quarterly', '季付'), ('monthly', '月付'), ('other', '其他')], max_length=20, verbose_name='付款方式')),
                ('remark', models.TextField(blank=True, null=True, verbose_name='备注')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '物业合同',
                'verbose_name_plural': '合同管理',
                'ordering': ['expire_date'],
            },
        ),
        migrations.CreateModel(
            name='ContractAttachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='contract_attachments/%Y/%m/', verbose_name='附件文件')),
                ('file_name', models.CharField(blank=True, max_length=255, verbose_name='文件名')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True, verbose_name='上传时间')),
                ('contract', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attachments', to='management.contract', verbose_name='所属合同')),
            ],
            options={
                'verbose_name': '合同附件',
                'verbose_name_plural': '合同附件',
            },
        ),
    ]
