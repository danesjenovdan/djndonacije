import requests
from requests.auth import HTTPBasicAuth

from django.conf import settings

def getBasicAuth():
    return HTTPBasicAuth(settings.MAUTIC_USER, settings.MAUTIC_PASS)

def mauticRequest(endpoint, data={}, method='post'):
    response = getattr(requests, method)(
        settings.MAUTIC_URL + endpoint,
        auth=getBasicAuth(),
        json=data
        )

    if response.status_code == 200:
        return response.json()
    else:
        # TODO: throw exception?
        return ""

def createContact(email, token, name='', surename=''):
    return mauticRequest(
        'contacts/new',
        {
            'email': email,
            'token': token,
            'name': name,
            'surename': surename
        }
    )

def deleteContact(contact_id):
    return mauticRequest(
        'contacts/%s/delete' % contact_id,
        method='delete'
    )

def addContactToACampaign(campagin_id, contact_id):
    return mauticRequest(
        'campaigns/%s/contact/%s/add' % (campagin_id, contact_id),
    )

def removeContactToACampaign(campagin_id, contact_id):
    return mauticRequest(
        'campaigns/%s/contact/%s/remove' % (campagin_id, contact_id),
    )

def removeContactFromACampaign(campagin_id, contact_id):
    return mauticRequest(
        'campaigns/%s/contact/%s/remove' % (campagin_id, contact_id),
    )

def getCampaingOfMember(contact_id):
    return mauticRequest(
        'contacts/%s/campaigns' % (contact_id),
        method='get'
    )

def sendEmail(email_id, contact_id, data):
    return mauticRequest(
        'emails/%s/contact/%s/send' % (email_id, contact_id),
        data=data
    )

def getSegments():
    return mauticRequest(
        'segments',
        method='get'
    )

def addContactToASegment(segment_id, contact_id):
    return mauticRequest(
        'segments/%s/contact/%s/add' % (segment_id, contact_id)
    )

def removeContactFromASegment(segment_id, contact_id):
    return mauticRequest(
        'segments/%s/contact/%s/remove' % (segment_id, contact_id),
    )