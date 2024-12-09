from django.contrib import admin
from django.db.models import (
    Case,
    CharField,
    Count,
    ImageField,
    IntegerField,
    Sum,
    Value,
    When,
)
from django.db.models.functions import Concat
from django.urls import reverse
from django.utils.safestring import mark_safe

from shop.models import (
    Article,
    ArticleImage,
    Basket,
    BoundleItem,
    Category,
    Item,
    Order,
)


class ArticleImageInline(admin.TabularInline):
    model = ArticleImage
    fields = ["image"]


class ArticleAdmin(admin.ModelAdmin):
    list_display = ["computed_name", "price", "tax", "computed_stock"]
    search_fields = ["name", "variant_of__name"]

    inlines = [ArticleImageInline]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _has_variants=Count("variants"),
        )
        queryset = queryset.annotate(
            _computed_stock=Case(
                When(_has_variants__gt=0, then=Sum("variants__stock")),
                default="stock",
                output_field=IntegerField(),
            )
        )
        queryset = queryset.annotate(
            _computed_name=Case(
                When(variant_of=None, then="name"),
                default=Concat("variant_of__name", Value(" - "), "name"),
                output_field=CharField(),
            )
        )
        queryset = queryset.order_by("_computed_name")
        return queryset

    def computed_stock(self, obj):
        return obj._computed_stock

    computed_stock.admin_order_field = "_computed_stock"
    computed_stock.short_description = "stock"

    def computed_name(self, obj):
        return obj._computed_name

    computed_name.admin_order_field = "_computed_name"
    computed_name.short_description = "name"


class ItemInline(admin.TabularInline):
    model = Item
    fk_name = "basket"
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "is_donation",
        "address",
        "is_payed",
        "is_sent",
        "payment_method",
        "payment_id",
        "delivery_method",
        "link_to_basket",
    ]
    search_fields = [
        "name",
    ]
    list_filter = ["name", "is_payed"]
    readonly_fields = ("items",)

    def link_to_basket(self, obj):
        link = reverse("admin:shop_basket_change", args=[obj.basket.id])
        return mark_safe('<a href="%s">Basket</a>' % (link))

    # link_to_basket.allow_tags = True

    def is_donation(self, obj):
        return bool(obj.basket.items.filter(article__name__icontains="donacija"))

    def items(self, obj):
        data = [["Item", "Quantity"]]
        data = data + [
            [
                (
                    i.article.variant_of.name + " --> " + i.article.name
                    if i.article.variant_of
                    else i.article.name
                ),
                i.quantity,
            ]
            for i in obj.basket.items.all()
        ]
        return mark_safe(array2htmltable(data))


class BasketAdmin(admin.ModelAdmin):
    list_display = ("id", "session", "total", "is_open")

    inlines = [
        ItemInline,
    ]
    search_fields = ["session"]


admin.site.register(Category)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Basket, BasketAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Item)
admin.site.register(BoundleItem)


def array2htmltable(data):
    q = "<table>\n"
    for i in [(data[0:1], "th"), (data[1:], "td")]:
        q += (
            "\n".join(
                [
                    "<tr>%s</tr>" % str(_mm)
                    for _mm in [
                        "".join(["<%s>%s</%s>" % (i[1], str(_q), i[1]) for _q in _m])
                        for _m in i[0]
                    ]
                ]
            )
            + "\n"
        )
    q += "</table>"
    return q
