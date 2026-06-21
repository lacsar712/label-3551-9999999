from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='/login/'), name='logout'),
    
    # 楼盘
    path('estate/', views.EstateListView.as_view(), name='estate_list'),
    path('estate/add/', views.EstateCreateView.as_view(), name='estate_add'),
    path('estate/<int:pk>/edit/', views.EstateUpdateView.as_view(), name='estate_edit'),
    path('estate/<int:pk>/delete/', views.EstateDeleteView.as_view(), name='estate_delete'),
    
    # 楼栋
    path('building/', views.BuildingListView.as_view(), name='building_list'),
    path('building/add/', views.BuildingCreateView.as_view(), name='building_add'),
    path('building/<int:pk>/edit/', views.BuildingUpdateView.as_view(), name='building_edit'),
    path('building/<int:pk>/delete/', views.BuildingDeleteView.as_view(), name='building_delete'),
    
    # 楼层
    path('floor/', views.FloorListView.as_view(), name='floor_list'),
    path('floor/add/', views.FloorCreateView.as_view(), name='floor_add'),
    path('floor/<int:pk>/edit/', views.FloorUpdateView.as_view(), name='floor_edit'),
    path('floor/<int:pk>/delete/', views.FloorDeleteView.as_view(), name='floor_delete'),
    
    # 单元(房屋)
    path('unit/', views.UnitListView.as_view(), name='unit_list'),
    path('unit/add/', views.UnitCreateView.as_view(), name='unit_add'),
    path('unit/<int:pk>/edit/', views.UnitUpdateView.as_view(), name='unit_edit'),
    path('unit/<int:pk>/delete/', views.UnitDeleteView.as_view(), name='unit_delete'),
    
    # 业主管理
    path('owner/', views.OwnerListView.as_view(), name='owner_list'),
    path('owner/add/', views.OwnerCreateView.as_view(), name='owner_add'),
    path('owner/<int:pk>/edit/', views.OwnerUpdateView.as_view(), name='owner_edit'),
    path('owner/<int:pk>/delete/', views.OwnerDeleteView.as_view(), name='owner_delete'),
    
    # 报修
    path('repair/', views.RepairListView.as_view(), name='repair_list'),
    path('repair/add/', views.RepairCreateView.as_view(), name='repair_add'),
    path('repair/<int:pk>/process/', views.RepairUpdateView.as_view(), name='repair_process'),
    
    # 费用
    path('fee/', views.FeeListView.as_view(), name='fee_list'),
    path('fee/add/', views.FeeCreateView.as_view(), name='fee_add'),
    path('fee/<int:pk>/process/', views.FeeUpdateView.as_view(), name='fee_process'),
    path('fee/<int:pk>/delete/', views.FeeDeleteView.as_view(), name='fee_delete'),

    # 合同管理
    path('contract/', views.ContractListView.as_view(), name='contract_list'),
    path('contract/add/', views.ContractCreateView.as_view(), name='contract_add'),
    path('contract/<int:pk>/edit/', views.ContractUpdateView.as_view(), name='contract_edit'),
    path('contract/<int:pk>/delete/', views.ContractDeleteView.as_view(), name='contract_delete'),
    path('contract/<int:pk>/', views.ContractDetailView.as_view(), name='contract_detail'),
    path('contract/attachment/<int:pk>/download/', views.ContractAttachmentDownloadView.as_view(), name='contract_attachment_download'),
    path('contract/attachment/<int:pk>/delete/', views.ContractAttachmentDeleteView.as_view(), name='contract_attachment_delete'),

    # 供应商管理
    path('supplier/', views.SupplierListView.as_view(), name='supplier_list'),
    path('supplier/add/', views.SupplierCreateView.as_view(), name='supplier_add'),
    path('supplier/<int:pk>/edit/', views.SupplierUpdateView.as_view(), name='supplier_edit'),
    path('supplier/<int:pk>/delete/', views.SupplierDeleteView.as_view(), name='supplier_delete'),

    # 绿化养护管理
    path('greening/', views.GreeningMaintenanceListView.as_view(), name='greening_maintenance_list'),
    path('greening/add/', views.GreeningMaintenanceCreateView.as_view(), name='greening_maintenance_add'),
    path('greening/<int:pk>/edit/', views.GreeningMaintenanceUpdateView.as_view(), name='greening_maintenance_edit'),
    path('greening/<int:pk>/delete/', views.GreeningMaintenanceDeleteView.as_view(), name='greening_maintenance_delete'),

    # 业主端 - 社区动态
    path('community-news/', views.CommunityNewsView.as_view(), name='community_news'),

    # 安全隐患排查管理
    path('safety-inspection/', views.SafetyInspectionListView.as_view(), name='safety_inspection_list'),
    path('safety-inspection/add/', views.SafetyInspectionCreateView.as_view(), name='safety_inspection_add'),
    path('safety-inspection/<int:pk>/', views.SafetyInspectionDetailView.as_view(), name='safety_inspection_detail'),
    path('safety-inspection/<int:pk>/edit/', views.SafetyInspectionUpdateView.as_view(), name='safety_inspection_edit'),
    path('safety-inspection/<int:pk>/rectify/', views.SafetyInspectionRectifyView.as_view(), name='safety_inspection_rectify'),
    path('safety-inspection/<int:pk>/delete/', views.SafetyInspectionDeleteView.as_view(), name='safety_inspection_delete'),

    path('vote/', views.VoteListView.as_view(), name='vote_list'),
    path('vote/add/', views.VoteCreateView.as_view(), name='vote_add'),
    path('vote/<int:pk>/', views.VoteDetailView.as_view(), name='vote_detail'),
    path('vote/<int:pk>/submit/', views.VoteSubmitView.as_view(), name='vote_submit'),
    path('vote/<int:pk>/delete/', views.VoteDeleteView.as_view(), name='vote_delete'),

    # 失物招领
    path('lost-item/', views.LostItemListView.as_view(), name='lost_item_list'),
    path('lost-item/add/', views.LostItemCreateView.as_view(), name='lost_item_add'),
    path('lost-item/<int:pk>/', views.LostItemDetailView.as_view(), name='lost_item_detail'),
    path('lost-item/<int:pk>/edit/', views.LostItemUpdateView.as_view(), name='lost_item_edit'),
    path('lost-item/<int:pk>/delete/', views.LostItemDeleteView.as_view(), name='lost_item_delete'),
    path('lost-item/<int:pk>/claim/', views.ClaimCreateView.as_view(), name='claim_create'),
    path('claim/<int:pk>/confirm/', views.ClaimConfirmView.as_view(), name='claim_confirm'),
    path('claim/<int:pk>/reject/', views.ClaimRejectView.as_view(), name='claim_reject'),
]
