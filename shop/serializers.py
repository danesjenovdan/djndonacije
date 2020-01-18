from rest_framework import serializers

from shop.models import ArticleImage, Article, Category, Item


class ArticleImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleImage
        fields = ('image',)


class VariantSerializer(serializers.ModelSerializer):
    stock = serializers.SerializerMethodField()
    images = ArticleImageSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = ('id', 'name', 'price', 'tax', 'stock', 'category', 'mergable', 'images')

    def get_stock(self, obj):
        return obj.get_stock


class ArticleSerializer(serializers.ModelSerializer):
    stock = serializers.SerializerMethodField()
    images = ArticleImageSerializer(many=True, read_only=True)
    variants = VariantSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = ('id', 'name', 'price', 'tax', 'stock', 'category', 'mergable', 'images', 'variants')

    def get_stock(self, obj):
        return obj.get_stock


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')


class ItemSerializer(serializers.ModelSerializer):
    article = ArticleSerializer(read_only=True)

    class Meta:
        model = Item
        fields = ('id', 'article', 'quantity')
