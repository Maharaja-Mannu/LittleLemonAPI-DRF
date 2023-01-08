from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from decimal import Decimal
import bleach
from .models import MenuItem, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "title", "slug"]


class MenuItemSerializer(serializers.ModelSerializer):
    price_after_tax = serializers.SerializerMethodField(method_name="calculate_tax")
    category_id = serializers.IntegerField(write_only=True)
    category = CategorySerializer(read_only=True)

    def validate(self, attrs):
        attrs["title"] = bleach.clean(attrs["title"])
        if attrs["price"] < 2:
            raise serializers.ValidationError("Price should not be less than 2.")
        if attrs["inventory"] < 0:
            raise serializers.ValidationError("Stock can not be negative")
        return super().validate(attrs)

    class Meta:
        model = MenuItem
        fields = [
            "id",
            "title",
            "price",
            "stock",
            "price_after_tax",
            "category",
            "category_id",
        ]
        extra_kwargs = {
            "title": {"validators": [UniqueValidator(queryset=MenuItem.objects.all())]},
            "price": {"min_value": 2},
            "stock": {"source": "inventory", "min_value": 0},
        }

    def calculate_tax(self, product: MenuItem):
        return product.price * Decimal(1.1)
