from django.db import models
from django.template.loader import get_template

from behaviors.behaviors import Timestamped
from .cebelca import Cebelca

from tinymce.models import HTMLField

# Create your models here.

class Category(Timestamped):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class Article(Timestamped):
    variant_of = models.ForeignKey(
        'self',
        verbose_name='variant of',
        on_delete=models.CASCADE,
        related_name='variants',
        null=True,
        blank=True)
    name = models.CharField(max_length=64)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.CASCADE)
    upc = models.CharField(max_length=64, null=True, blank=True)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    tax = models.DecimalField(decimal_places=2, max_digits=10)
    stock = models.IntegerField(default=0)
    image = models.ImageField(upload_to='images/', height_field=None, width_field=None, max_length=1000, null=True, blank=True)
    mergable = models.BooleanField(default=False)
    articles = models.ManyToManyField('self', blank=True, through='BoundleItem', symmetrical=False)
    custom_mail = HTMLField(null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def get_stock(self):
        articles = self.boundle_items.all()
        if articles:
            print(self.name, ' je boundle ', self.stock, min([article.article.stock for article in articles]))
            return min([article.article.stock for article in articles])
        else:
            if self.variants.all():
                return sum(self.variants.values_list('stock', flat=True))
            return self.stock


class BoundleItem(Timestamped):
    article = models.ForeignKey('Article', related_name='in_boundle', on_delete=models.CASCADE)
    boundle = models.ForeignKey('Article', related_name='boundle_items', on_delete=models.CASCADE)

    def __str__(self):
        return 'Boundle: ' + (self.boundle.name if self.boundle else '') + ' <--> Article: ' + (self.article.name if self.article else '')


class Basket(Timestamped):
    session = models.CharField(max_length=64)
    articles = models.ManyToManyField(Article, through='Item')
    total = models.DecimalField(default=0.0, decimal_places=2, max_digits=10)
    is_open = models.BooleanField(default=True)


class Item(Timestamped):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    basket = models.ForeignKey(Basket, related_name="items", on_delete=models.CASCADE)
    price =  models.DecimalField(decimal_places=2, max_digits=10)
    quantity = models.IntegerField(default=1)
    def __str__(self):
        return "item " + self.article.name

class Order(Timestamped):
    basket = models.ForeignKey(Basket, related_name='order', on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    address = models.CharField(max_length=256)
    phone = models.CharField(max_length=64, null=True, blank=True)
    is_payed = models.BooleanField(default=False)
    payment_id = models.CharField(max_length=64, null=True, blank=True)
    payer_id = models.CharField(max_length=64, null=True, blank=True)
    payment_method = models.CharField(max_length=64, null=True, blank=True)
    delivery_method = models.CharField(max_length=64, null=True, blank=True)
    email = models.CharField(max_length=64, null=True, blank=True)
    info = models.CharField(max_length=256, null=True, blank=True)
    is_sent = models.BooleanField(default=False)
    is_on_cebelca = models.BooleanField(default=False)

    def __str__(self):
        return "order of:" + self.name

    def is_donation(self):
        return bool(self.basket.items.filter(article__name__icontains="donacija"))

    def save(self, *args, **kwargs):
        if not self.is_donation():
            if self.is_payed:
                if not self.is_on_cebelca:
                    # prepare address
                    address = self.address.split(',')
                    if len(address) > 1:
                        post = address[1].strip().split(" ")
                        city = " ".join(post[1:])
                        post = post[0]
                    else:
                        post = ""
                        city = ""

                    payment_methods = {'upn': 1,
                                       'paypal': 5}

                    try:
                        pay_method = payment_methods[self.payment_method]
                    except:
                        pay_method = 1

                    c = Cebelca(api_type="prod")
                    c.add_partner(self.name, address[0], post, city)
                    c.add_header()
                    items = self.basket.items.all()

                    # prepare mail content
                    html = get_template('thanksgiving.html')
                    html_content = None
                    if len(items) == 1:
                        if items[0].article.custom_mail:
                            html_content = html.render({'custom_msg': items[0].article.custom_mail})
                    if not html_content:
                        html_content = html.render({})

                    # add items to cebelca invoice
                    for item in items:
                        price = item.price * 100 / (100 + item.article.tax)
                        c.add_item(item.article.name, item.quantity, price, vat=item.article.tax)
                    c.set_invoice_paid(pay_method, self.basket.total)
                    c.finalize_invoice()
                    c.send_mail(self.email, 'Hvala <3', html_content, self.name)
                    self.is_on_cebelca = True
                    self.save()
        super(Order, self).save(*args, **kwargs)
