from djnd_supporters.mautic_api import MauticApi

mautic_api = MauticApi()

def add_user_to_mautic(email, name, password, segment_id):
    """
    add user to mautic
    arguments:
        email
        name
        password
    returns:
        if success
            mautic_id
        else
            None
    """
    response_contact, response_status = mautic_api.createContact(
        email=email,
        name=name,
        password=password
    )
    if response_status == 200:
        mautic_id = response_contact['contact']['id']
        response, response_status = mautic_api.addContactToASegment(segment_id, mautic_id)
        return mautic_id
    else:
        return None

def send_email(email_id, contact_id, municipality, username):
    """
    send_email to contact
    arguments:
        email_id: mautic email id
        contact_id: mautic contact id
        municipality: municipality name
    """
    response, response_status = mautic_api.sendEmail(
        email_id=email_id,
        contact_id=contact_id,
        data={
            'tokens': {
                'municipality': municipality,
                'username': username
            }
        })
    return response_status
