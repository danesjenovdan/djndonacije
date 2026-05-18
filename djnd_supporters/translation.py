from modeltranslation.translator import TranslationOptions, translator

from .models import CampaignQuestion, DonationCampaign


class CampaignQuestionTranslationOptions(TranslationOptions):
    fields = ("question", "url_text")


class DonationCampaignTranslationOptions(TranslationOptions):
    fields = ("title", "subtitle", "terms_of_use_text")


translator.register(CampaignQuestion, CampaignQuestionTranslationOptions)
translator.register(DonationCampaign, DonationCampaignTranslationOptions)
