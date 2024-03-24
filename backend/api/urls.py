from django.urls import path

from . import views

urlpatterns = [
    path("login", views.login),
    path("signup", views.sign_up),
    path("chats", views.list_chats),
    path("chats/folder/<int:id>", views.list_chats_folder),
    path("chat/<int:pk>", views.get_chat),
    path("chat/create", views.new_chat),
    path("chat/delete/<int:pk>", views.delete_chat),
    path("check_token", views.check_token),
    path("chat/upload_prompt", views.get_prompt_from_file),
    path(
        "assign-chats-to-folder/",
        views.assign_chats_to_folder,
        name="assign-chats-to-folder",
    ),
    path("chat/reload", views.reload_chat),
    path("file/upload", views.add_pdf_to_gpt),
]
