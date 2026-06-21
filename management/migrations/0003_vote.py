from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0002_safety_inspection'),
    ]

    operations = [
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='投票议题')),
                ('description', models.TextField(blank=True, null=True, verbose_name='投票说明')),
                ('start_time', models.DateTimeField(verbose_name='开始时间')),
                ('end_time', models.DateTimeField(verbose_name='结束时间')),
                ('allow_multiple', models.BooleanField(default=False, verbose_name='允许多选')),
                ('is_anonymous', models.BooleanField(default=False, verbose_name='匿名计票')),
                ('status', models.CharField(choices=[('pending', '未开始'), ('active', '进行中'), ('closed', '已结束')], default='pending', max_length=10, verbose_name='投票状态')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('created_by', models.ForeignKey(blank=True, limit_choices_to={'role__in': ['admin', 'staff']}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_votes', to=settings.AUTH_USER_MODEL, verbose_name='发起人')),
            ],
            options={
                'verbose_name': '社区投票',
                'verbose_name_plural': '投票管理',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='VoteOption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(max_length=200, verbose_name='选项内容')),
                ('vote', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='options', to='management.vote', verbose_name='所属投票')),
            ],
            options={
                'verbose_name': '投票选项',
                'verbose_name_plural': '投票选项',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='VoteBallot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='投票时间')),
                ('option', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ballots', to='management.voteoption', verbose_name='所选选项')),
                ('vote', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ballot_records', to='management.vote', verbose_name='所属投票')),
                ('voter', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cast_ballots', to=settings.AUTH_USER_MODEL, verbose_name='投票人')),
            ],
            options={
                'verbose_name': '投票记录',
                'verbose_name_plural': '投票记录',
            },
        ),
        migrations.CreateModel(
            name='VoteRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('voted_at', models.DateTimeField(auto_now_add=True, verbose_name='投票时间')),
                ('vote', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='voter_records', to='management.vote', verbose_name='所属投票')),
                ('voter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vote_participations', to=settings.AUTH_USER_MODEL, verbose_name='投票业主')),
            ],
            options={
                'verbose_name': '业主投票参与记录',
                'verbose_name_plural': '业主投票参与记录',
                'unique_together': {('vote', 'voter')},
            },
        ),
    ]
