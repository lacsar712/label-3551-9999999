from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Estate, Building, Floor, Unit, Repair, Supplier
from .forms import RepairStaffForm

User = get_user_model()


class RepairStatusTransitionTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(
            username='test_owner', password='test123', role='owner'
        )
        cls.staff = User.objects.create_user(
            username='test_staff', password='test123', role='staff'
        )
        cls.estate = Estate.objects.create(name='测试楼盘', address='测试地址')
        cls.building = Building.objects.create(estate=cls.estate, name='1号楼')
        cls.floor = Floor.objects.create(building=cls.building, name='1层')
        cls.unit = Unit.objects.create(
            floor=cls.floor, name='101', owner=cls.owner, area='100.00'
        )
        cls.supplier = Supplier.objects.create(
            name='测试供应商',
            contact_person='张三',
            phone='13800138000',
            service_category='water_electric',
        )

    def _create_repair(self, status='pending'):
        return Repair.objects.create(
            owner=self.owner,
            unit=self.unit,
            fault_type='water_electric',
            location='测试位置',
            description='测试描述',
            status=status,
        )

    def test_pending_to_processing_normal_transition(self):
        repair = self._create_repair(status='pending')
        form = RepairStaffForm(
            data={
                'status': 'processing',
                'processor': self.staff.id,
                'feedback': '开始处理',
            },
            instance=repair,
        )
        self.assertTrue(form.is_valid(), f"表单验证失败，错误: {form.errors}")
        saved = form.save()
        self.assertEqual(saved.status, 'processing')

    def test_processing_to_completed_normal_transition(self):
        repair = self._create_repair(status='processing')
        form = RepairStaffForm(
            data={
                'status': 'completed',
                'processor': self.staff.id,
                'feedback': '处理完成',
            },
            instance=repair,
        )
        self.assertTrue(form.is_valid(), f"表单验证失败，错误: {form.errors}")
        saved = form.save()
        self.assertEqual(saved.status, 'completed')

    def test_full_normal_flow_pending_processing_completed(self):
        repair = self._create_repair(status='pending')
        self.assertEqual(repair.status, 'pending')

        form1 = RepairStaffForm(
            data={
                'status': 'processing',
                'processor': self.staff.id,
                'feedback': '开始处理',
            },
            instance=repair,
        )
        self.assertTrue(form1.is_valid(), f"pending→processing 验证失败: {form1.errors}")
        repair = form1.save()
        self.assertEqual(repair.status, 'processing')

        form2 = RepairStaffForm(
            data={
                'status': 'completed',
                'processor': self.staff.id,
                'feedback': '处理完成',
            },
            instance=repair,
        )
        self.assertTrue(form2.is_valid(), f"processing→completed 验证失败: {form2.errors}")
        repair = form2.save()
        self.assertEqual(repair.status, 'completed')

    def test_completed_cannot_revert_to_pending(self):
        repair = self._create_repair(status='completed')
        form = RepairStaffForm(
            data={
                'status': 'pending',
                'processor': self.staff.id,
                'feedback': '尝试回退',
            },
            instance=repair,
        )
        self.assertFalse(form.is_valid())
        self.assertIn('status', form.errors)
        self.assertIn('已完成的工单不可回退状态', form.errors['status'][0])

    def test_completed_cannot_revert_to_processing(self):
        repair = self._create_repair(status='completed')
        form = RepairStaffForm(
            data={
                'status': 'processing',
                'processor': self.staff.id,
                'feedback': '尝试回退',
            },
            instance=repair,
        )
        self.assertFalse(form.is_valid())
        self.assertIn('status', form.errors)
        self.assertIn('已完成的工单不可回退状态', form.errors['status'][0])

    def test_pending_cannot_jump_to_completed_directly(self):
        repair = self._create_repair(status='pending')
        form = RepairStaffForm(
            data={
                'status': 'completed',
                'processor': self.staff.id,
                'feedback': '尝试跳过处理中',
            },
            instance=repair,
        )
        self.assertFalse(form.is_valid())
        self.assertIn('status', form.errors)
        self.assertIn('不允许从', form.errors['status'][0])
        self.assertIn('待处理', form.errors['status'][0])
        self.assertIn('已完成', form.errors['status'][0])

    def test_processing_cannot_revert_to_pending(self):
        repair = self._create_repair(status='processing')
        form = RepairStaffForm(
            data={
                'status': 'pending',
                'processor': self.staff.id,
                'feedback': '尝试回退',
            },
            instance=repair,
        )
        self.assertFalse(form.is_valid())
        self.assertIn('status', form.errors)
        self.assertIn('不允许从', form.errors['status'][0])
        self.assertIn('处理中', form.errors['status'][0])
        self.assertIn('待处理', form.errors['status'][0])

    def test_same_status_submission_is_valid(self):
        repair = self._create_repair(status='pending')
        form = RepairStaffForm(
            data={
                'status': 'pending',
                'processor': self.staff.id,
                'feedback': '仅更新反馈，不改变状态',
            },
            instance=repair,
        )
        self.assertTrue(form.is_valid(), f"相同状态提交被拒绝: {form.errors}")
        saved = form.save()
        self.assertEqual(saved.status, 'pending')
        self.assertEqual(saved.feedback, '仅更新反馈，不改变状态')

    def test_new_repair_creation_without_instance(self):
        form = RepairStaffForm(
            data={
                'status': 'processing',
                'processor': self.staff.id,
            },
        )
        self.assertTrue(form.is_valid(), f"新实例状态设置被拒绝: {form.errors}")
