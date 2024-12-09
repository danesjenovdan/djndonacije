from rest_framework import serializers

from shop.models import Article, ArticleImage, Category, Item


class BaseArticleSerializer(serializers.ModelSerializer):
    stock = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    category = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Article
        fields = ("id", "name", "price", "tax", "stock", "category", "images")

    def get_stock(self, obj):
        return obj.get_stock

    def get_images(self, obj):
        return [i.image.url for i in obj.images.all() if i.image]


class InStockListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        data = data.filter(stock__gte=1)
        return super().to_representation(data)


class VariantArticleSerializer(BaseArticleSerializer):
    name = serializers.SerializerMethodField()
    variant = serializers.SerializerMethodField()

    class Meta(BaseArticleSerializer.Meta):
        list_serializer_class = InStockListSerializer
        fields = BaseArticleSerializer.Meta.fields + ("variant",)

    def get_name(self, obj):
        return obj.variant_of.name if obj.variant_of else obj.name

    def get_variant(self, obj):
        return obj.name if obj.variant_of else None

    def get_images(self, obj):
        images = super().get_images(obj)
        if obj.variant_of:
            images += super().get_images(obj.variant_of)
        return images


class ArticleSerializer(BaseArticleSerializer):
    variants = VariantArticleSerializer(many=True, read_only=True)

    class Meta(BaseArticleSerializer.Meta):
        fields = BaseArticleSerializer.Meta.fields + ("variants",)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name")


class ItemSerializer(serializers.ModelSerializer):
    article = VariantArticleSerializer(read_only=True)

    class Meta:
        model = Item
        fields = ("id", "article", "quantity")
