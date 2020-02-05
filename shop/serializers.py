from rest_framework import serializers

from shop.models import ArticleImage, Article, Category, Item


class BaseArticleSerializer(serializers.ModelSerializer):
    stock = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    category = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Article
        fields = ('id', 'name', 'price', 'tax', 'stock', 'category', 'images')

    def get_stock(self, obj):
        return obj.get_stock

    def get_images(self, obj):
        return [i.image.url for i in obj.images.all() if i.image]


class VariantArticleSerializer(BaseArticleSerializer):
    name = serializers.SerializerMethodField()
    variant = serializers.SerializerMethodField()

    class Meta(BaseArticleSerializer.Meta):
        fields = BaseArticleSerializer.Meta.fields + ('variant',)

    def get_name(self, obj):
        return obj.variant_of.name

    def get_variant(self, obj):
        return obj.name


class ArticleSerializer(BaseArticleSerializer):
    variants = VariantArticleSerializer(many=True, read_only=True)

    class Meta(BaseArticleSerializer.Meta):
        fields = BaseArticleSerializer.Meta.fields + ('variants',)


class ItemArticleSerializer(BaseArticleSerializer):
    name = serializers.SerializerMethodField()
    variant = serializers.SerializerMethodField()

    class Meta(BaseArticleSerializer.Meta):
        fields = BaseArticleSerializer.Meta.fields + ('variant',)

    def get_name(self, obj):
        return obj.variant_of.name if obj.variant_of else obj.name

    def get_variant(self, obj):
        return obj.name if obj.variant_of else None


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')


class ItemSerializer(serializers.ModelSerializer):
    article = ItemArticleSerializer(read_only=True)

    class Meta:
        model = Item
        fields = ('id', 'article', 'quantity')
