import requests
from requests.auth import HTTPBasicAuth

from django.conf import settings

def getBasicAuth():
    return HTTPBasicAuth(settings.MAUTIC_USER, settings.MAUTIC_PASS)

def mauticRequest(endpoint, data={}, file=None, method='post'):
    response = getattr(requests, method)(
        settings.MAUTIC_URL + endpoint,
        auth=getBasicAuth(),
        json=data,
        files=file,
        )

    if response.status_code >= 200 and response.status_code < 300:
        return response.json(), 200
    else:
        print(response.content)
        return response.content, response.status_code

def createContact(email, name='', surname='', token=None):
    data = {
        'email': email,
        'name': name,
        'surname': surname
    }
    if token:
        data.update({'token': token})
    return mauticRequest(
        'contacts/new',
        data
    )

def getContact(contact_id):
    return mauticRequest(
        'contacts/%s' % contact_id,
        method='get'
    )

def getContactByEmail(email):
    print(email)
    return mauticRequest(
        'contacts?search=email:%s' % email,
        method='get'
    )

def deleteContact(contact_id):
    return mauticRequest(
        'contacts/%s/delete' % contact_id,
        method='delete'
    )

def patchContact(id, data):
    return mauticRequest(
        f'/contacts/{id}/edit',
        method='patch',
        data=data
    )

def addContactToACampaign(campagin_id, contact_id):
    return mauticRequest(
        'campaigns/%s/contact/%s/add' % (campagin_id, contact_id),
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

def createEmail(name, title, subject, customHtml, description, emailType='template', template='cards', assetAttachments=None, lists=None, fromAddress=None, fromName=None):
    return mauticRequest(
        'emails/new',
        data={
            'name': name,
            'title': title,
            'subject': subject,
            'customHtml': customHtml,
            'description': description,
            'isPublished': 1,
            'assetAttachments': assetAttachments,
            'emailType': emailType,
            'lists': lists,
            'template': template,
            'fromAddress': fromAddress,
            'fromName': fromName
        }
    )

def getEmail(email_id):
    return mauticRequest(
        'emails/%s' % (email_id),
        method='get'
    )

def editEmailSubject(email_id, subject):
    return mauticRequest(
        'emails/%s/edit' % (email_id),
        data={
            'subject': subject
        },
        method='patch'
    )

def sendEmail(email_id, contact_id, data):
    return mauticRequest(
        'emails/%s/contact/%s/send' % (email_id, contact_id),
        data=data
    )

def sendEmailToSegment(email_id, data):
    print(email_id, data)
    return mauticRequest(
        'emails/%s/send' % (email_id),
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

def getSegmentsOfContact(contact_id):
    return mauticRequest(
        'contacts/%s/segments' % contact_id,
        method='get'
    )

def saveAsset(title, file_, storageLocation='local'):
    return mauticRequest(
        'assets/new',
        data={
            'title': title,
            'storageLocation': storageLocation,
            'file': file_
        }
    )

def saveFile(name, file_):
    return mauticRequest(
        'files/assets/new',
        file={
            'name': name,
            'file': file_
        }
    )
