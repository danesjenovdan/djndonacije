import csv
from datetime import datetime
from decimal import Decimal
from dateutil.relativedelta import relativedelta

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Sum
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import TemplateView
from sentry_sdk import capture_exception
from wkhtmltopdf.views import PDFTemplateResponse

from djnd_supporters import models, utils
from djndonacije import payment
from djndonacije.qrcode import UPNQRException, generate_upnqr_svg


class TestPaymentView(TemplateView):
    template_name = "test_payment.html"

    def get_context_data(self, *args, **kwargs):
        context = super(TestPaymentView, self).get_context_data(*args, **kwargs)
        context["token"] = payment.client_token()["token"]
        return context


class TestUPNView(TemplateView):
    template_name = "poloznica.html"

    def get_context_data(self, *args, **kwargs):
        context = super(TestUPNView, self).get_context_data(*args, **kwargs)
        context["qr_code"] = generate_upnqr_svg(
            name="Janez MojeImeJepredolgoInŠumnik Novak",
            address1="Ulica z zelo dolgim imenom, ki je predolg 1",
            address2="1000 Ljubljana-Domžale-Hrastnik-Dravlje",
            amount=Decimal("123.45"),
            # amount=123,
            # amount=123.45,
            iban="SI56 6100 0000 5740 710",
            # purpose=None,
            purpose="DonacijaDonacijaDonacijaDonacijaDonacijaDonacijaDonacijaDonacija",
            reference="SI00 0000008",
            code="ADCS",
            # unused={'1': TestUPNView},
            include_xml_declaration=True,
        )
        # context['qr_code'] = None
        # print(context['qr_code'])
        return context


def getPDForDonation(request, pk):
    transaction = get_object_or_404(models.Transaction, pk=pk)

    bill = {}
    bill["id"] = transaction.id
    bill["date"] = datetime.now().strftime("%d.%m.%Y")
    bill["price"] = transaction.amount
    bill["referencemath"] = transaction.reference

    bill["code"] = "ADCS"
    bill["purpose"] = "Donacija"
    if transaction.campaign and transaction.campaign.upn_name:
        bill["purpose"] = transaction.campaign.upn_name

    address = transaction.subscriber.address.split(",")

    victim = {}
    victim["name"] = transaction.subscriber.name
    victim["address1"] = address[0]
    victim["address2"] = address[1] if len(address) > 1 else ""

    try:
        qr_code = generate_upnqr_svg(
            name=victim["name"],
            address1=victim["address1"],
            address2=victim["address2"],
            amount=bill["price"],
            code=bill["code"],
            purpose=bill["purpose"],
            reference=bill["referencemath"],
            include_xml_declaration=True,
        )
    except UPNQRException as e:
        capture_exception(e)
        qr_code = None

    return PDFTemplateResponse(
        request=request,
        template="poloznica.html",
        filename="upn_djnd.pdf",
        context={"victim": victim, "bill": bill, "pdf": True, "qr_code": qr_code},
        show_content_in_browser=True,
    )


@login_required
def braintree_export(request, braintree_api_id):
    braintree_api = get_object_or_404(models.BraintreeApi, pk=braintree_api_id)
    last_month_bt_transactions = utils.export_bt(braintree_api)
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="bt_export.csv"'},
    )

    if not last_month_bt_transactions:
        return response

    writer = csv.DictWriter(response, fieldnames=last_month_bt_transactions[0].keys())
    writer.writeheader()
    writer.writerows(last_month_bt_transactions)

    return response


def _decode_bank_transaction_csv(uploaded_file):
    raw_data = uploaded_file.read()
    for encoding in ("utf-8-sig", "iso-8859-2", "cp1250", "windows-1250", "latin-1"):
        try:
            return raw_data.decode(encoding).splitlines()
        except UnicodeDecodeError:
            continue
    return raw_data.decode("utf-8").splitlines()


@login_required
def import_bank_transactions(request):
    if request.method == "GET":
        return render(
            request,
            "admin/djnd_supporters/transaction/upload_bank_transactions.html",
            {
                "accounts": models.Account.objects.all(),
            },
        )

    if request.method == "POST":
        file = request.FILES.get("file")
        if file:
            csv_file = _decode_bank_transaction_csv(file)
            start_index = 0
            # skip header lines until we find the one that starts with "Valuta;Datum valute"
            for i, line in enumerate(csv_file):
                if line.startswith("Valuta;Datum valute"):
                    start_index = i
                    break
            csv_file = csv_file[start_index:]
            reader = csv.DictReader(csv_file, delimiter=";")
            account = models.Account.objects.get(id=request.POST.get("account_id"))
            for row in reader:
                if row["Referenca prejemnika"].startswith("SI00110000"):
                    # this is probably a donation, save as a transaction
                    reference = row["Referenca prejemnika"]
                    reference.split("0")
                    campaign_id = reference.split("0")[-1]
                    dc = models.DonationCampaign.objects.filter(id=campaign_id).first()
                    # add transaction if dont exists. nonce is unique for each transaction
                    if not dc and row["Dobro"] and row["ID transakcije"]:
                        continue
                    transaction, created = models.Transaction.objects.get_or_create(
                        nonce=row["ID transakcije"],
                        defaults={
                            "amount": Decimal(row["Dobro"].replace(",", ".")),
                            "reference": reference,
                            "subscriber": None,
                            "campaign": dc,
                            "transaction_timestamp": datetime.strptime(
                                row["Datum valute"], "%d.%m.%Y"
                            ),
                            "payment_method": "UPN",
                            "account": account,
                        },
                    )
                    transaction.save()
            return redirect("admin:djnd_supporters_transaction_changelist")

        else:
            return HttpResponse("No file uploaded.", status=400)

    return HttpResponse("Invalid request method.", status=405)


@login_required
def export_monthly_report_form(request):
    if request.method == "POST":
        month = request.POST.get("month")
        year = request.POST.get("year")
        if not month or not year:
            return HttpResponse("Mesec in leto sta obvezna.", status=400)

        return redirect(
            "supporters:transaction-export-monthly", year=int(year), month=int(month)
        )

    now = datetime.today()
    months = list(range(1, 13))
    years = list(range(now.year - 5, now.year + 1))

    return render(
        request,
        "admin/djnd_supporters/transaction/export_monthly_report.html",
        {
            "months": months,
            "years": years,
            "selected_month": now.month,
            "selected_year": now.year,
        },
    )


@login_required
def export_monthly_report(request, month, year):
    month = int(month)
    year = int(year)
    if month < 1 or month > 12:
        return HttpResponse("Invalid month.", status=400)

    start_selected_month = datetime(day=1, month=month, year=year)
    start_next_month = start_selected_month + relativedelta(months=1)
    start_previous_month = start_selected_month - relativedelta(months=1)

    transactions = models.Transaction.objects.filter(
        transaction_timestamp__gte=start_selected_month,
        transaction_timestamp__lt=start_next_month,
    ).select_related("campaign", "subscriber")

    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="export.csv"'},
    )

    csv_writer = csv.writer(
        response, delimiter=";", quotechar='"', quoting=csv.QUOTE_MINIMAL
    )
    csv_writer.writerow(
        [
            "start_selected_month",
            start_selected_month.strftime("%d.%m.%Y"),
            "start_next_month",
            start_next_month.strftime("%d.%m.%Y"),
            "start_previous_month",
            start_previous_month.strftime("%d.%m.%Y"),
        ]
    )
    csv_writer.writerow([])
    csv_writer.writerow(
        [
            "Št transakcije",
            "ID transakcije",
            "Datum transakcije",
            "Vrednost",
            "Kampanja",
            "Izvor transakcije",
            "Način plačila",
            "Naročnina",
            "ID naročnine",
            "Datum pričetka naročnine",
        ]
    )
    for i, transaction in enumerate(transactions):
        csv_writer.writerow(
            [
                i + 1,
                transaction.transaction_id,
                (
                    transaction.transaction_timestamp.strftime("%d.%m.%Y %H:%M:%S")
                    if transaction.transaction_timestamp
                    else ""
                ),
                transaction.amount,
                transaction.campaign.name if transaction.campaign else "",
                transaction.referrer,
                transaction.payment_method,
                "da" if transaction.subscription else "ne",
                (
                    transaction.subscription.subscription_id
                    if transaction.subscription
                    else ""
                ),
                (
                    transaction.subscription.created.strftime("%d.%m.%Y %H:%M:%S")
                    if transaction.subscription
                    else ""
                ),
            ]
        )
    csv_writer.writerow([])
    csv_writer.writerow([])
    csv_writer.writerow(
        [
            "Kampanja",
            "Vrednost",
            "Premik +/- glede na prejšnji mesec",
            "",
            "Kampanja",
            "Vrednost",
            "Premik +/- glede na prejšnji mesec",
            "Št naročnin",
            "Premik +/- glede na prejšnji mesec",
        ]
    )
    campaigns = transactions.values_list("campaign__id", flat=True).distinct()
    for campaign_id in campaigns:
        campaign = models.DonationCampaign.objects.get(id=campaign_id)
        current_month_amount = transactions.filter(
            campaign__id=campaign_id,
            subscription__isnull=True,
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0")
        previous_month_amount = models.Transaction.objects.filter(
            campaign__id=campaign_id,
            subscription__isnull=True,
            transaction_timestamp__gte=start_previous_month,
            transaction_timestamp__lt=start_selected_month,
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0")
        amount_diff = current_month_amount - previous_month_amount
        subscription_tr = transactions.filter(
            campaign__id=campaign_id, subscription__isnull=False
        )
        subscription_amount = subscription_tr.aggregate(total=Sum("amount"))[
            "total"
        ] or Decimal("0")
        previous_subscription_tr = models.Transaction.objects.filter(
            campaign__id=campaign_id,
            subscription__isnull=False,
            transaction_timestamp__gte=start_previous_month,
            transaction_timestamp__lt=start_selected_month,
        )
        previous_subscription_amount = previous_subscription_tr.aggregate(
            total=Sum("amount")
        )["total"] or Decimal("0")
        subscription_count_diff = (
            subscription_tr.count() - previous_subscription_tr.count()
        )
        subscription_amount_diff = subscription_amount - previous_subscription_amount
        csv_writer.writerow(
            [
                campaign.name,
                current_month_amount,
                amount_diff,
                "",
                campaign.name,
                subscription_amount,
                subscription_amount_diff,
                subscription_tr.count(),
                subscription_count_diff,
            ]
        )

    referrers_dict = {}

    referrers = (
        transactions.filter(subscription=False)
        .values_list("referrer", flat=True)
        .distinct()
    )
    for referrer in referrers:
        referrer_name = referrer
        current_month_amount = transactions.filter(
            referrer=referrer, subscription__isnull=True
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0")
        previous_month_amount = models.Transaction.objects.filter(
            referrer=referrer[0],
            subscription__isnull=True,
            transaction_timestamp__gte=start_previous_month,
            transaction_timestamp__lt=start_selected_month,
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0")
        amount_diff = current_month_amount - previous_month_amount
        amount_diff_str = f"+{amount_diff}" if amount_diff >= 0 else str(amount_diff)

        referrers_dict[referrer_name] = {
            "current_month_amount": current_month_amount,
            "amount_diff_str": amount_diff_str,
            "new_subscription_amount": Decimal("0"),
            "new_subscription_count": 0,
            "previous_subscription_amount": Decimal("0"),
            "previous_subscription_count": 0,
        }
    this_month_new_subscriptions = models.Subscription.objects.filter(
        created__gte=start_selected_month,
        created__lt=start_next_month,
    ).select_related("campaign", "subscriber")
    prev_month_new_subscriptions = models.Subscription.objects.filter(
        created__gte=start_previous_month,
        created__lt=start_selected_month,
    ).select_related("campaign", "subscriber")
    for sub in this_month_new_subscriptions:
        referrer_name = sub.referrer
        if referrer_name not in referrers_dict:
            referrers_dict[referrer_name] = {
                "current_month_amount": Decimal("0"),
                "amount_diff_str": "+0",
                "subscription_amount": Decimal("0"),
                "subscription_amount_diff_str": "+0",
                "new_subscription_amount": Decimal("0"),
                "new_subscription_count": 0,
                "previous_subscription_amount": Decimal("0"),
                "previous_subscription_count": 0,
            }
        referrers_dict[referrer_name]["new_subscription_amount"] += sub.amount
        referrers_dict[referrer_name]["new_subscription_count"] += 1

    for sub in prev_month_new_subscriptions:
        referrer_name = sub.referrer
        if referrer_name not in referrers_dict:
            referrers_dict[referrer_name] = {
                "current_month_amount": Decimal("0"),
                "amount_diff_str": "+0",
                "subscription_amount": Decimal("0"),
                "subscription_amount_diff_str": "+0",
                "new_subscription_amount": Decimal("0"),
                "new_subscription_count": 0,
                "previous_subscription_amount": Decimal("0"),
                "previous_subscription_count": 0,
            }
        referrers_dict[referrer_name]["previous_subscription_amount"] += sub.amount
        referrers_dict[referrer_name]["previous_subscription_count"] += 1

    csv_writer.writerow([])
    csv_writer.writerow([])
    csv_writer.writerow(
        [
            "Referrer",
            "Vrednost skupaj transakicj brez subscriptionov",
            "Premik +/- glede na prejšnji mesec",
            "Vrednost skupaj novih subscriptionov",
            "Premik +/- glede na prejšnji mesec",
            "Št novih subscriptionov",
            "Premik +/- glede na prejšnji mesec",
        ]
    )
    for referrer_name, data in referrers_dict.items():
        subscription_amount_diff = (
            data["new_subscription_amount"] - data["previous_subscription_amount"]
        )
        subscription_amount_diff_str = (
            f"+{subscription_amount_diff}"
            if subscription_amount_diff >= 0
            else str(subscription_amount_diff)
        )
        new_subscription_count_diff = (
            data["new_subscription_count"] - data["previous_subscription_count"]
        )
        new_subscription_count_diff_str = (
            f"+{new_subscription_count_diff}"
            if new_subscription_count_diff >= 0
            else str(new_subscription_count_diff)
        )
        csv_writer.writerow(
            [
                referrer_name,
                data["current_month_amount"],
                data["amount_diff_str"],
                data["new_subscription_amount"],
                subscription_amount_diff_str,
                data["new_subscription_count"],
                new_subscription_count_diff_str,
            ]
        )

    return response
