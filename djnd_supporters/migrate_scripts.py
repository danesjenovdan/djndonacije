from djnd_supporters.mautic_api import MauticApi
from djnd_supporters import models

import requests
import csv

old_api = MauticApi(username='tomaz@djnd.si', password='aaaaaaaa', url='https://mautic.djnd.si/api/')
new_api = MauticApi()

# TODO pageing

# copy assets
asssets, response_status = old_api.getAssets()
assets_map = {}
segments_map = {}
categories_map = {}

for i, asset in enumerate(asssets["assets"][:100]):
    url = asset['downloadUrl']
    content = requests.get(url).content

    extension = asset['extension']
    title = asset['title']
    if '.' not in title:
        if not extension:
            extension = 'pdf'
        title = f'{title}.{extension}'

    response, response_status = new_api.saveFile(title, content)
    if response_status == 200:
        print(response_status)
        print(title)
        print(response['file']['name'])
        print()
        response, response_status = new_api.saveAsset(title, response['file']['name'])
        asset_id = response['asset']['id']
        assets_map[asset['id']] = asset_id


categories, reponse_status = old_api.getCategories()
for category in categories['categories']:
    old_category_id = category.pop('id')
    response, response_status = new_api.setCategories(category)
    if response_status == 200:
        categories_map[old_category_id] = response['category']['id']

# copy segments
segments, response_status = old_api.getSegments()
print('segments')
for id, segment in segments['lists'].items():
    old_segment_id = segment.pop('id')
    print(segment)
    if not 'filters' in segment.keys() or not segment['filters']:
        response, response_status = new_api.setSegments(segment)
        segments_map[int(old_segment_id)] = response['list']['id']

# copy emails
emails, response_status = old_api.getEmails()
for id, email in emails["emails"].items():
    print('email')
    lists = [segments_map[segment['id']] for segment in email['lists'] if segment['id'] in segments_map.keys()]
    if lists:
        print(lists)
        email['lists'] = lists
    else:
        print('empty list')
        print(email.pop('lists'))
        email['lists'] = [6]

    assetAttachments = [assets_map[asset] for asset in email['assetAttachments'] if asset in segments_map.keys()]
    if assetAttachments:
        email['assetAttachments'] = assetAttachments
    else:
        email.pop('assetAttachments')

    if email['template'] == 'cards':
        email.pop('template')

    if email['category']:
        email['category'] = [categories_map[email['category']] for cat in email['category'] if cat in categories_map.keys()]

    response_mail, response_status = new_api.setEmail(
        email
    )
    print(response_status, type(response_status))
    if response_status != 200 or response_status != '200':
        print("no 200 od 201")
        print(lists)
        #print(response_mail)


# copy companies
companies, response_status = old_api.getCompanies()

for id, company in companies['companies'].items():
    company.pop('id')
    company['companyname'] = company['fields']['core']['companyname']['value']
    new_api.setCompany(company)

# copy contacts from csv
file_name = 'contacts_december-2-2022.csv'
with open(file_name) as csvfile:
    csv_contacts = csv.DictReader(csvfile, delimiter=',', quotechar='"')

    for contact in csv_contacts:
        print(contact['email'], contact['token'])
        # check if is contact on mautic.

        old_mautic_id = contact['id']

        email = contact['email']
        response, response_status = new_api.getContactByEmail(email)
        if response_status == 200:
            contacts = response['contacts']
        else:
            # something went wrong with mautic, return
            print('Error by adding contact')
        print(contacts)
        mautic_id = None
        if contacts:
            # subscriber exists on mautic
            mautic_id = list(contacts.keys())[0]
            try:
                subscriber = models.Subscriber.objects.get(mautic_id=mautic_id)
            except:
                print(mautic_id, contact['email'])
        else:
            # subscriber does not exist on mautic
            if models.Subscriber.objects.filter(token=contact['token']):
                subscriber = models.Subscriber(
                    token=contact['token'],
                    username=contact['token']
                )
            else:
                subscriber = models.Subscriber.objects.create(username=contact['token'], token=contact['token'])
            subscriber.save()
            response, response_status = subscriber.save_to_mautic(email)
            if response_status != 200:
                # something went wrong with saving to mautic, abort
                print('something went wrong with saving to mautic, abort')
            mautic_id = subscriber.mautic_id

        # add contact to segments
        response, response_status = old_api.getSegmentsOfContact(old_mautic_id)
        if response['total'] > 0:
            for id, segment in response['lists'].items():
                segmnet_id = segments_map.get(segment['id'], None)
                if segmnet_id:
                    response, response_status = new_api.addContactToASegment(segmnet_id, mautic_id)


