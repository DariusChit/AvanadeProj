from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .models import Space, Folder, Group, Tag, Project
from .serializers import SpaceSerializer, FolderSerializer, GroupSerializer, TagSerializer, ProjectSerializer
from api.serializers import ChatSerializer
User = get_user_model()


@api_view(['GET', 'POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
# or permissions.AllowAny if you want it to be public
@permission_classes([permissions.IsAuthenticated])
def space_list(request):
    """
    Create a new space and optionally create folders within it.
    """
    if request.method == 'GET':
        spaces = Space.objects.all()
        serializer = SpaceSerializer(spaces, many=True)
        return Response(serializer.data)
    if request.method == 'POST':
        serializer = SpaceSerializer(data=request.data)
        if serializer.is_valid():
            group = Group.objects.get(id=request.data["group"])
            serializer.save(owner=request.user, group=group)

            # Example: Create predefined folders for a new space

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def create_chat(request):
    """
    Create a new chat within a specified folder.
    """
    folder_id = request.data.get('folder_id')
    try:
        # Ensure user owns the space
        folder = Folder.objects.get(id=folder_id, space__owner=request.user)
    except:
        return Response({'error': 'Folder not found or access denied'}, status=status.HTTP_404_NOT_FOUND)

    chat_data = {
        'title': request.data.get('title', ''),
        'prompt': request.data.get('prompt'),
        'response': request.data.get('response'),
        'author': request.user.id,  # Assuming author needs to be the logged-in user
        'folder': folder.id,
    }
    # Ensure you have a ChatSerializer
    serializer = ChatSerializer(data=chat_data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'DELETE', 'PUT', 'PATCH'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def space_detail(request, pk):
    """
    Retrieve, update, or delete a space instance.
    """
    space = get_object_or_404(Space, pk=pk)

    if request.method == 'GET':
        serializer = SpaceSerializer(space)
        return Response(serializer.data)

    elif request.method == 'PUT' or request.method == 'PATCH':
        serializer = SpaceSerializer(
            space, data=request.data, partial=request.method == 'PATCH')
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        space.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def folder_list(request, space_id):
    """
    List all folders for a specific space, or create a new folder in a space.
    """

    space = get_object_or_404(Space, id=space_id)

    if request.method == 'GET':
        folders = Folder.objects.filter(space=space)
        serializer = FolderSerializer(folders, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = FolderSerializer(data=request.data)
        if serializer.is_valid():
            # Linking the folder to the specified Space
            serializer.save(space=space)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def folder_detail(request, pk):
    """
    Retrieve, update, or delete a folder instance.
    """
    folder = get_object_or_404(Folder, pk=pk)

    if request.method == 'GET':
        serializer = FolderSerializer(folder)
        return Response(serializer.data)

    elif request.method in ['PUT', 'PATCH']:
        serializer = FolderSerializer(
            folder, data=request.data, partial=request.method == 'PATCH')
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        folder.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def group_list(request):
    """
    List all groups, or create a new group.
    """
    if request.method == 'GET':
        groups = Group.objects.all()
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = GroupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Add logic for owner if needed
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def group_detail(request, pk):
    """
    Retrieve, update, or delete a group instance.
    """
    group = get_object_or_404(Group, pk=pk)

    if request.method == 'GET':
        serializer = GroupSerializer(group)
        return Response(serializer.data)

    elif request.method in ['PUT', 'PATCH']:
        serializer = GroupSerializer(
            group, data=request.data, partial=request.method == 'PATCH')
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        group.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def add_member(request, pk):
    """
    Add a member to a group.
    """
    group = get_object_or_404(Group, pk=pk)
    user_id = request.data.get('user_id')
    try:
        user = User.objects.get(id=user_id)
        group.members.add(user)
        return Response({'status': 'member added'})
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def tag_list(request):
    """
    List all tags, or create a new tag.
    """
    if request.method == 'GET':
        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = TagSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Add additional logic here if necessary
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def tag_detail(request, pk):
    """
    Retrieve, update, or delete a tag instance.
    """
    tag = get_object_or_404(Tag, pk=pk)

    if request.method == 'GET':
        serializer = TagSerializer(tag)
        return Response(serializer.data)

    elif request.method in ['PUT', 'PATCH']:
        serializer = TagSerializer(
            tag, data=request.data, partial=request.method == 'PATCH')
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        tag.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def project_list(request):
    """
    List all projects, or create a new project.
    """
    if request.method == 'GET':
        projects = Project.objects.all()
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def project_detail(request, pk):
    """
    Retrieve, update, or delete a project instance.
    """
    project = get_object_or_404(Project, pk=pk)

    if request.method == 'GET':
        serializer = ProjectSerializer(project)
        return Response(serializer.data)

    elif request.method in ['PUT', 'PATCH']:
        serializer = ProjectSerializer(
            project, data=request.data, partial=request.method == 'PATCH')
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
