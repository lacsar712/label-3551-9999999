from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0007_emergencycontact'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeliveryOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('delivery_date', models.DateField(verbose_name='交付日期')),
                ('status', models.CharField(choices=[('pending', '待验收'), ('inspecting', '验收中'), ('rectifying', '待整改'), ('delivered', '已交付')], default='pending', max_length=20, verbose_name='交付状态')),
                ('remark', models.TextField(blank=True, null=True, verbose_name='备注')),
                ('completed_date', models.DateField(blank=True, null=True, verbose_name='完成交付日期')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('created_by', models.ForeignKey(limit_choices_to={'role__in': ['admin', 'staff']}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_delivery_orders', to=settings.AUTH_USER_MODEL, verbose_name='创建人')),
                ('unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='delivery_orders', to='management.unit', verbose_name='关联房屋')),
            ],
            options={
                'verbose_name': '房屋交付单',
                'verbose_name_plural': '房屋交付验收管理',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='DeliveryInspectionItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_name', models.CharField(max_length=200, verbose_name='验收项目名称')),
                ('status', models.CharField(choices=[('unchecked', '未检查'), ('pass', '通过'), ('fail', '不通过'), ('rectify', '待整改')], default='unchecked', max_length=20, verbose_name='验收状态')),
                ('staff_remark', models.TextField(blank=True, null=True, verbose_name='物业验收备注')),
                ('owner_remark', models.TextField(blank=True, null=True, verbose_name='业主确认/补充说明')),
                ('owner_confirmed', models.BooleanField(default=False, verbose_name='业主已确认')),
                ('inspected_at', models.DateTimeField(blank=True, null=True, verbose_name='验收时间')),
                ('owner_updated_at', models.DateTimeField(blank=True, null=True, verbose_name='业主更新时间')),
                ('delivery_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='management.deliveryorder', verbose_name='所属交付单')),
                ('inspected_by', models.ForeignKey(limit_choices_to={'role__in': ['admin', 'staff']}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='inspected_items', to=settings.AUTH_USER_MODEL, verbose_name='验收人')),
            ],
            options={
                'verbose_name': '交付验收项目',
                'verbose_name_plural': '交付验收项目',
                'ordering': ['id'],
            },
        ),
    ]
