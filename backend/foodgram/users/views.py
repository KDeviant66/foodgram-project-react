from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from api.paginations import PagePagination
from api.serializers import SubscribeAuthorSerializer, SubscribeSerializer
from recipes.models import User
from users.models import Follow


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    pagination_class = PagePagination

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
        url_path='subscribe',
        permission_classes=(permissions.IsAuthenticatedOrReadOnly,)
    )
    def subscribe(self, request, id=None):
        user = get_object_or_404(User, id=id)

        if request.method == 'POST':
            serializer = SubscribeAuthorSerializer(
                data={'user': request.user.id, 'following': user.id}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        Follow.objects.filter(user=request.user, following=user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=('GET',),
        permission_classes=(permissions.IsAuthenticatedOrReadOnly,)
    )
    def subscriptions(self, request):
        pages = self.paginate_queryset(
            Follow.objects.filter(user=request.user)
        )

        serializer = SubscribeSerializer(
            pages, many=True, context={'request': request}
        )

        return self.get_paginated_response(serializer.data)
