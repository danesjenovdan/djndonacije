import requests
from django.conf import settings
from requests.auth import HTTPBasicAuth


class MauticApi(object):
    def __init__(
        self,
        username=settings.MAUTIC_USER,
        password=settings.MAUTIC_PASS,
        url=settings.MAUTIC_URL,
    ):
        self.username = username
        self.password = password
        self.url = url

    def getBasicAuth(self):
        return HTTPBasicAuth(self.username, self.password)

    def mauticRequest(
        self, endpoint, data={}, file=None, method="post", start=0, limit=100
    ):
        url = self.url + endpoint
        if "?" in url:
            url += "&"
        else:
            url += "?"
        url += "start=%s&limit=%s" % (start, limit)
        response = getattr(requests, method)(
            url,
            auth=self.getBasicAuth(),
            json=data,
            files=file,
        )

        if response.status_code >= 200 and response.status_code < 300:
            out_data = response.json()
            if "total" in out_data.keys() and int(out_data["total"]) > start + limit:
                new_page, status = self.mauticRequest(
                    endpoint, data, file, method, start + limit, limit
                )
                if status == 200:
                    data_key = list(new_page.keys())[1]
                    out_data[data_key].update(new_page[data_key])
                else:
                    return new_page, status
            return out_data, 200
        else:
            print(response.content)
            return response.content, response.status_code

    def createContact(self, email, name="", surname="", token=None, password=None):
        data = {"email": email, "name": name, "surname": surname}
        if token:
            data.update({"token": token})
        if password:
            data.update({"password": password})
        return self.mauticRequest("contacts/new", data)

    def getContact(self, contact_id):
        return self.mauticRequest("contacts/%s" % contact_id, method="get")

    def getContacts(self, segment_alias=None, without_token=None):
        if segment_alias:
            query_parameters = f"?search=segment:{segment_alias}"
        elif without_token:
            query_parameters = f"?where[0][expr]=isNull&where[0][col]=token"
        else:
            query_parameters = ""
        return self.mauticRequest(f"contacts{query_parameters}", method="get")

    def patchContact(self, id, data):
        return self.mauticRequest(f"contacts/{id}/edit", method="patch", data=data)

    def add_tag_to_contact(self, id, tag_name):
        mautic_result = self.mauticRequest(
            f"contacts/{id}/edit", method="patch", data={"tags": [tag_name]}
        )
        return mautic_result

    def setContact(self, data):
        return self.mauticRequest("contacts/new", data=data)

    def getContactByEmail(self, email):
        print(email)
        return self.mauticRequest("contacts?search=email:%s" % email, method="get")

    def deleteContact(self, contact_id):
        return self.mauticRequest("contacts/%s/delete" % contact_id, method="delete")

    def addContactToACampaign(self, campagin_id, contact_id):
        return self.mauticRequest(
            "campaigns/%s/contact/%s/add" % (campagin_id, contact_id),
        )

    def removeContactFromACampaign(self, campagin_id, contact_id):
        return self.mauticRequest(
            "campaigns/%s/contact/%s/remove" % (campagin_id, contact_id),
        )

    def getCampaingOfMember(self, contact_id):
        return self.mauticRequest("contacts/%s/campaigns" % (contact_id), method="get")

    def createEmail(
        self,
        name,
        title,
        subject,
        customHtml,
        description,
        emailType="template",
        template="cards",
        assetAttachments=None,
        lists=None,
        fromAddress=None,
        fromName=None,
        category=None,
        replyToAddress=None,
        isPublished=True,
    ):
        return self.mauticRequest(
            "emails/new",
            data={
                "name": name,
                "title": title,
                "subject": subject,
                "customHtml": customHtml,
                "description": description,
                "assetAttachments": assetAttachments,
                "emailType": emailType,
                "lists": lists,
                "template": template,
                "fromAddress": fromAddress,
                "fromName": fromName,
                "category": category,
                "replyToAddress": replyToAddress,
                "isPublished": isPublished,
            },
        )

    def getEmail(self, email_id):
        return self.mauticRequest("emails/%s" % (email_id), method="get")

    def getCategories(self):
        return self.mauticRequest("categories", method="get")

    def setEmail(self, data):
        return self.mauticRequest("emails/new", data=data)

    def getEmails(self):
        return self.mauticRequest("emails", method="get")

    def getCompanies(self):
        return self.mauticRequest("companies", method="get")

    def setCompany(self, data):
        return self.mauticRequest("companies/new", data=data)

    def editEmailSubject(self, email_id, subject):
        return self.mauticRequest(
            "emails/%s/edit" % (email_id), data={"subject": subject}, method="patch"
        )

    def sendEmail(self, email_id, contact_id, data):
        return self.mauticRequest(
            "emails/%s/contact/%s/send" % (email_id, contact_id), data=data
        )

    def sendEmailToSegment(self, email_id, data):
        print(email_id, data)
        return self.mauticRequest("emails/%s/send" % (email_id), data=data)

    def getSegments(self):
        return self.mauticRequest("segments", method="get")

    def setSegments(self, data):
        return self.mauticRequest("segments/new", data)

    def setCategories(self, data):
        return self.mauticRequest("categories/new", data)

    def addContactToASegment(self, segment_id, contact_id):
        return self.mauticRequest(
            "segments/%s/contact/%s/add" % (segment_id, contact_id)
        )

    def removeContactFromASegment(self, segment_id, contact_id):
        return self.mauticRequest(
            "segments/%s/contact/%s/remove" % (segment_id, contact_id),
        )

    def getSegmentsOfContact(self, contact_id):
        return self.mauticRequest("contacts/%s/segments" % contact_id, method="get")

    def saveAsset(self, title, file_, storageLocation="local"):
        return self.mauticRequest(
            "assets/new",
            data={"title": title, "storageLocation": storageLocation, "file": file_},
        )

    def getAssets(self):
        return self.mauticRequest("assets", method="get")

    def saveFile(self, name, file_):
        return self.mauticRequest("files/media/new", file={"name": name, "file": file_})
