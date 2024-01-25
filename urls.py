from django.urls import path
from tools import views

app_name = "tools"

urlpatterns = [
    path("tool/download/", views.download_view, name="download_test"),
    path("tool/<slug>/", views.single_tool_view, name="single"),
    path("tool/<slug>/raw", views.single_tool_view_raw, name="single_raw"),
    path("download/<cid>/", views.download_view, name="download"),
]
