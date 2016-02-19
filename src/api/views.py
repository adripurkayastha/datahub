from django.contrib.auth.models import User

from psycopg2 import Error

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.views import exception_handler
from rest_framework.response import Response


from .serializer import (
    UserSerializer, RepoSerializer, CollaboratorSerializer,
    TableSerializer, QuerySerializer)


class CurrentUser(APIView):
    """
    The current user.

    GET details on current user.
    Accepts: None
    """

    def get(self, request, format=None):
        username = request.user.get_username()
        user = User.objects.get(username=username)

        serializer = UserSerializer(user, many=False)
        return Response(serializer.data)


class CurrentUserRepos(APIView):
    """
    The current user's owned repos.

    GET the repos owned by the current user.
    Accepts: None
    """

    def get(self, request, format=None):
        username = request.user.get_username()
        repo_base = username

        serializer = RepoSerializer(username=username, repo_base=repo_base)
        return Response(serializer.user_owned_repos())


class Repos(APIView):
    """
    The current user's visible repos.

    GET the repos visible to the current user.
    Accepts: None
    """

    def get(self, request, format=None):
        username = request.user.get_username()
        repo_base = username

        serializer = RepoSerializer(username=username, repo_base=repo_base)
        return Response(serializer.user_accessible_repos())


class ReposForUser(APIView):
    """
    Repos of the specified user.

    GET the repos of a specific user.
    Accepts: None
    ---
    POST to create a repo under the specified user.
    Fails if the specified user has not authorized this.
    Accepts: { "repo": str }
    """

    def get(self, request, repo_base, format=None):
        username = request.user.get_username()
        serializer = RepoSerializer(username=username, repo_base=repo_base)

        if username == repo_base:
            return Response(serializer.user_owned_repos())
        else:
            return Response(serializer.specific_collab_repos(repo_base))

    def post(self, request, repo_base, format=None):
        username = request.user.get_username()
        serializer = RepoSerializer(username=username, repo_base=repo_base)

        repo_name = request.data['repo']
        serializer.create_repo(repo_name)

        return Response(serializer.user_accessible_repos(),
                        status=status.HTTP_201_CREATED)


class Repo(APIView):
    """
    A specific repo of a specific user.

    DELETE to delete the repo.
    Accepts: None
    ---
    PATCH to rename the repo.
    Accepts: { "new_name": }
    """

    def delete(self, request, repo_base, repo_name, format=None):
        username = request.user.get_username()
        serializer = RepoSerializer(username=username, repo_base=repo_base)
        serializer.delete_repo(repo_name=repo_name, force=True)
        return Response(None, status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, repo_base, repo_name, format=None):
        username = request.user.get_username()
        serializer = RepoSerializer(username=username, repo_base=repo_base)
        new_repo_name = request.data['new_name']
        serializer.rename_repo(repo=repo_name, new_name=new_repo_name)

        return Response(serializer.user_accessible_repos(),
                        status=status.HTTP_200_OK)


class Collaborators(APIView):
    """
    List and create collaborators.

    GET to list the collaborators.
    Accepts: None
    ---
    POST to add a collaborator.
    Accepts: { "user":, "privileges": }
    """

    def get(self, request, repo_base, repo, format=None):
        username = request.user.get_username()
        serializer = CollaboratorSerializer(username=username,
                                            repo_base=repo_base)
        collaborators = serializer.list_collaborators(repo)

        return Response(collaborators, status=status.HTTP_200_OK)

    def post(self, request, repo_base, repo, format=None):
        username = request.user.get_username()
        serializer = CollaboratorSerializer(username=username,
                                            repo_base=repo_base)
        data = request.data
        collaborator = data['user']
        privileges = data['privileges']
        serializer.add_collaborator(repo, collaborator, privileges)
        collaborators = serializer.list_collaborators(repo)

        return Response(collaborators, status=status.HTTP_200_OK)


class Collaborator(APIView):
    """
    Modify and delete existing collaborators.

    DELETE to remove the specified collaborator from the repo.
    Accepts: None
    ---
    PUT to modify the privileges of an existing collaborator.
    Accepts: { "privileges": }
    """

    def delete(self, request, repo_base, repo, collaborator, format=None):
        username = request.user.get_username()
        serializer = CollaboratorSerializer(username=username,
                                            repo_base=repo_base)
        serializer.remove_collaborator(repo, collaborator)
        return Response(None, status=status.HTTP_204_NO_CONTENT)

    def put(self, request, repo_base, repo, collaborator, format=None):
        username = request.user.get_username()
        serializer = CollaboratorSerializer(username=username,
                                            repo_base=repo_base)
        data = request.data
        privileges = data['privileges']
        serializer.add_collaborator(repo, collaborator, privileges)
        collaborators = serializer.list_collaborators(repo)

        return Response(collaborators, status=status.HTTP_200_OK)


class Tables(APIView):
    """
    List and create tables.

    GET to list existing tables.
    Accepts: None
    ---
    POST to create a new table.
    Accepts: { "table_name":, "params": []}
    """

    def get(self, request, repo_base, repo, format=None):
        username = request.user.get_username()
        serializer = TableSerializer(
            username=username, repo_base=repo_base)

        tables = serializer.list_tables(repo)
        return Response(tables, status=status.HTTP_200_OK)

    def post(self, request, repo_base, repo, format=None):
        username = request.user.get_username()
        serializer = TableSerializer(
            username=username, repo_base=repo_base)

        params = request.data['params']
        table_name = request.data['table_name']
        serializer.create_table(repo, table_name, params)

        tables = serializer.list_tables(repo)
        return Response(tables, status=status.HTTP_200_OK)


class Table(APIView):
    """
    View or delete a single table.

    GET to view info about a table.
    Accepts: None
    ---
    DELETE to delete a table.
    Accepts: None
    """

    def get(self, request, repo_base, repo, table):
        username = request.user.get_username()
        serializer = TableSerializer(
            username=username, repo_base=repo_base)

        table_info = serializer.describe_table(repo, table, detail=False)
        return Response(table_info, status=status.HTTP_200_OK)

    def delete(self, request, repo_base, repo, table):
        username = request.user.get_username()
        serializer = TableSerializer(
            username=username, repo_base=repo_base)

        serializer.delete_table(repo, table, False)
        return Response(None, status=status.HTTP_204_NO_CONTENT)


class Query(APIView):
    """
    Manage SQL queries.

    POST execute a SQL statement and receive the result.
    Accepts: { "sql": }
    """

    def post(self, request, repo_base, repo=None, format=None):
        username = request.user.get_username()
        data = request.data
        query = data['sql']
        serializer = QuerySerializer(username=username, repo_base=repo_base)

        result = serializer.execute_sql(query=query, repo=repo)
        return Response(result, status=status.HTTP_200_OK)


def custom_exception_handler(exc, context):
    result = {}

    # Now add the HTTP status code to the response.
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)
    if response is not None:
        response.data['status_code'] = response.status_code
    elif issubclass(type(exc), Error):
        result['error_type'] = type(exc).__name__
        result['message'] = exc.message
        result['pgcode'] = exc.pgcode
        result['severity'] = exc.diag.severity
    else:
        result = exc

    return Response(result, status=status.HTTP_400_BAD_REQUEST)
