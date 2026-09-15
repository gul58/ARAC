from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("giris/", views.AppLoginView.as_view(), name="login"),
    path("cikis/", views.AppLogoutView.as_view(), name="logout"),
    # İhale
    path("ihale/bolgeler/", views.ihale_regions, name="ihale_regions"),
    path("ihale/bolgeler/<int:pk>/sil/", views.ihale_region_delete, name="ihale_region_delete"),
    path("ihale/firmalar/", views.ihale_companies, name="ihale_companies"),
    path("ihale/firmalar/<int:pk>/sil/", views.ihale_company_delete, name="ihale_company_delete"),
    path("ihale/formenler/", views.ihale_foremen, name="ihale_foremen"),
    path("ihale/formenler/<int:pk>/sil/", views.ihale_foreman_delete, name="ihale_foreman_delete"),
    path("ihale/araclar/", views.ihale_vehicles, name="ihale_vehicles"),
    path("ihale/araclar/<int:pk>/sil/", views.ihale_vehicle_delete, name="ihale_vehicle_delete"),
    path("ihale/soforler/", views.ihale_drivers, name="ihale_drivers"),
    path("ihale/soforler/<int:pk>/sil/", views.ihale_driver_delete, name="ihale_driver_delete"),
    # Formen
    path("formen/", views.formen_home, name="formen_home"),
    path("formen/gorev-emri/yeni/", views.formen_task_create, name="formen_task_create"),
    path("formen/gorev-emri/", views.formen_task_list, name="formen_task_list"),
    path("formen/gorev-emri/<int:pk>/duzenle/", views.formen_task_edit, name="formen_task_edit"),
    path("formen/gorev-emri/<int:pk>/sil/", views.formen_task_delete, name="formen_task_delete"),
    path(
        "formen/api/arac/<int:vehicle_id>/soforler/",
        views.formen_vehicle_drivers,
        name="formen_vehicle_drivers",
    ),
]
