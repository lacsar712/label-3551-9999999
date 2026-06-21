from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0006_neighborhoodhelppost_neighborhoodhelpreply'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmergencyContact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(choices=[('fire', '消防'), ('police', '派出所'), ('water_electric', '水电抢修'), ('elevator', '电梯维保'), ('medical', '医疗急救'), ('gas', '燃气抢修'), ('property', '物业值班'), ('other', '其他')], max_length=20, verbose_name='分类')),
                ('name', models.CharField(max_length=100, verbose_name='名称')),
                ('phone', models.CharField(max_length=30, verbose_name='电话')),
                ('service_hours', models.CharField(blank=True, default='', max_length=200, verbose_name='服务时间说明')),
                ('remark', models.TextField(blank=True, default='', verbose_name='备注')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_emergency_contacts', limit_choices_to={'role__in': ['admin', 'staff']}, to=settings.AUTH_USER_MODEL, verbose_name='创建人')),
            ],
            options={
                'verbose_name': '应急联系人',
                'verbose_name_plural': '应急通讯录',
                'ordering': ['category', '-created_at'],
            },
        ),
    ]
