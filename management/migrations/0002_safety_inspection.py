from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SafetyInspection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inspection_area', models.CharField(max_length=200, verbose_name='排查区域')),
                ('hazard_description', models.TextField(verbose_name='隐患描述')),
                ('risk_level', models.CharField(choices=[('high', '高风险'), ('medium', '中风险'), ('low', '低风险')], max_length=10, verbose_name='风险等级')),
                ('discovery_date', models.DateField(verbose_name='发现日期')),
                ('rectification_deadline', models.DateField(verbose_name='整改期限')),
                ('site_remark', models.TextField(blank=True, null=True, verbose_name='现场备注')),
                ('status', models.CharField(choices=[('open', '未消项'), ('closed', '已消项')], default='open', max_length=10, verbose_name='消项状态')),
                ('rectification_measures', models.TextField(blank=True, null=True, verbose_name='整改措施')),
                ('completion_date', models.DateField(blank=True, null=True, verbose_name='完成日期')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('estate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='safety_inspections', to='management.estate', verbose_name='所属楼盘')),
                ('inspector', models.ForeignKey(blank=True, limit_choices_to={'role__in': ['admin', 'staff']}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='inspected_hazards', to=settings.AUTH_USER_MODEL, verbose_name='排查人')),
                ('rectifier', models.ForeignKey(blank=True, limit_choices_to={'role__in': ['admin', 'staff']}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='rectified_hazards', to=settings.AUTH_USER_MODEL, verbose_name='整改人')),
            ],
            options={
                'verbose_name': '安全隐患排查记录',
                'verbose_name_plural': '安全隐患排查管理',
                'ordering': ['-discovery_date', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='SafetyInspectionTrack',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('create', '创建记录'), ('update', '更新记录'), ('rectify', '提交整改'), ('close', '标记消项'), ('reopen', '重新开启'), ('remark', '添加备注')], max_length=20, verbose_name='操作类型')),
                ('remark', models.TextField(blank=True, null=True, verbose_name='操作说明')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='操作时间')),
                ('inspection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tracks', to='management.safetyinspection', verbose_name='关联隐患')),
                ('operator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='操作人')),
            ],
            options={
                'verbose_name': '隐患处理轨迹',
                'verbose_name_plural': '隐患处理轨迹',
                'ordering': ['created_at'],
            },
        ),
        migrations.CreateModel(
            name='GreeningMaintenance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('maintenance_type', models.CharField(choices=[('pruning', '修剪'), ('fertilizing', '施肥'), ('pest_control', '除虫'), ('replanting', '补植')], max_length=20, verbose_name='养护类型')),
                ('work_date', models.DateField(verbose_name='作业日期')),
                ('worker', models.CharField(max_length=100, verbose_name='作业人员')),
                ('materials', models.TextField(blank=True, null=True, verbose_name='所用物料')),
                ('description', models.TextField(blank=True, null=True, verbose_name='作业描述')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('estate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='greening_maintenances', to='management.estate', verbose_name='养护区域')),
            ],
            options={
                'verbose_name': '绿化养护记录',
                'verbose_name_plural': '绿化养护管理',
                'ordering': ['-work_date', '-created_at'],
            },
        ),
    ]
