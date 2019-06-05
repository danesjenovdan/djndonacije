from rest_framework import serializers

from shop.models import Article, Category, Item

class ArticleSerializer(serializers.ModelSerializer):
    stock = serializers.SerializerMethodField()
    class Meta:
        model = Article
        fields = ('id', 'name', 'price', 'tax', 'stock', 'category', 'mergable')

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