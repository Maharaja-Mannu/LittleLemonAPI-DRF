from rest_framework import generics, viewsets
from rest_framework.renderers import TemplateHTMLRenderer, StaticHTMLRenderer
from rest_framework.decorators import (
    api_view,
    renderer_classes,
    permission_classes,
    throttle_classes,
)
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_200_OK, HTTP_400_BAD_REQUEST
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from django.contrib.auth.models import User, Group
from django.contrib.auth import get_user_model

# from rest_framework_csv.renderers import CSVRenderer
# from rest_framework_yaml.renderers import YAMLRenderer
from .models import MenuItem, Category
from .serializers import MenuItemSerializer, CategorySerializer
from .throttles import TenCallsPerMinute

# from .serializers import MenuItemSerializer


class MenuItemsView(viewsets.ModelViewSet):
    # throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_throttles(self):
        if self.action == "create":
            throttle_classes = [UserRateThrottle]
        else:
            throttle_classes = []
        return [throttle() for throttle in throttle_classes]


class SingleMenuItemView(generics.RetrieveUpdateAPIView, generics.DestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer


@api_view(["GET", "POST"])

# @renderer_classes([CSVRenderer]) # to render response in csv or
# @renderer_classes([YAMLRenderer]) # to render response in yaml

# Instead of importing the CSV and YAML renderer classes individually in the views.py file and then passing them to the renderer_classes decorator above each function, we can make them available globally in our API project. In this way, the client can get the desired output with a valid Accept header.
# To make these renderers available globally, add the following two lines in the settings.py file in the DEFAULT_RENDERER_CLASSES section.
# like 'rest_framework_csv.renderers.CSVRenderer'


def menu_items(request):
    if request.method == "GET":
        items = MenuItem.objects.select_related("category").all()
        category_name = request.query_params.get("category")
        to_price = request.query_params.get("to_price")
        search = request.query_params.get("search")
        ordering = request.query_params.get("ordering")
        perpage = request.query_params.get("perpage", default=2)
        page = request.query_params.get("page", default=1)
        if category_name:
            items = items.filter(category__title=category_name)
        if to_price:
            items = items.filter(price__lte=to_price)
        if search:
            items = items.filter(title__startswith=search)
        if ordering:
            ordering_fields = ordering.split(",")
            items = items.order_by(*ordering_fields)
        paginator = Paginator(items, per_page=perpage)
        try:
            items = paginator.page(number=page)
        except EmptyPage:
            items = []
        serialized_item = MenuItemSerializer(
            items, many=True, context={"request": request}
        )
        return Response(serialized_item.data)
    if request.method == "POST":
        serialized_item = MenuItemSerializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)
        serialized_item.save()
        return Response(serialized_item.data, status=HTTP_201_CREATED)


@api_view(["GET", "POST"])
def category(request):
    if request.method == "GET":
        items = Category.objects.all()
        serialized_item = CategorySerializer(
            items, many=True, context={"request": request}
        )
        return Response(serialized_item.data)
    if request.method == "POST":
        serialized_item = CategorySerializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)
        serialized_item.save()
        return Response(serialized_item.data, status=HTTP_201_CREATED)


@api_view()
def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    serialized_category = CategorySerializer(category)
    return Response(serialized_category.data)


@api_view()
@renderer_classes([TemplateHTMLRenderer])
def menu(request):
    items = MenuItem.objects.select_related("category").all()
    serialized_item = MenuItemSerializer(items, many=True)
    return Response({"data": serialized_item.data}, template_name="menu-items.html")


@api_view()
@renderer_classes([StaticHTMLRenderer])
def welcome(request):
    data = "<html><body><h1>Welcome To Little Lemon API Project</h1></body></html>"
    return Response(data)


@api_view()
@permission_classes([IsAuthenticated])
def secret(request):
    return Response({"message": "some secret message"})


@api_view()
@throttle_classes([AnonRateThrottle])
def throttle_check(request):
    return Response({"message": "Successfull"})


@api_view()
@permission_classes([IsAuthenticated])
# @throttle_classes([UserRateThrottle])
@throttle_classes([TenCallsPerMinute])  # custom throttling
def throttle_check_auth(request):
    return Response({"message": "message for logged in user only"})


@api_view(["POST"])
@permission_classes([IsAdminUser])
def managers(request):
    username = request.data["username"]
    if username:
        user = get_object_or_404(User, username=username)
        managers = Group.objects.get(name="Manager")
        if request.method == "POST":
            managers.user_set.add(user)
        elif request.method == "DELETE":
            managers.user_set.remove(user)
        return Response({"message": "ok"})
    return Response({"message": "error"}, HTTP_400_BAD_REQUEST)


""" Improperly configured;
We must not keep this endpoint in production,
Any user can change one's password """


@api_view(["POST"])
@permission_classes([IsAdminUser])
def reset_password(request):
    # validate
    username = request.data["username"]
    new_password = request.data["new_password"]
    user = get_object_or_404(User, username=username)
    user.set_password(new_password)
    user.save()
    return Response({"message": "Password has been changed successfully"}, HTTP_200_OK)
