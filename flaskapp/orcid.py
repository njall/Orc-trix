"""
API wrapper to Orcid.
"""
import requests
import json
import logging
import hashlib

logging.basicConfig(level=logging.DEBUG)

BASE_URL = "https://pub.orcid.org/"

def _get_raw_json(orcid_id, action=""):
    """Get raw JSON file for orcid_id."""
    url = orcid_url(orcid_id, action)
    logging.info(url)
    resp = requests.get(url,
                        headers={'Accept':'application/orcid+json'})
    return resp.json()


def orcid_url(orcid_id, action=""):
    return BASE_URL + orcid_id + action


def get_profile(orcid_id):
    """Get JSON for Orcid and clean it."""
    raw_json = _get_raw_json(orcid_id)

    # TODO Add information
    profile = {}
    for name in ('credit_name', 'given_names', 'family_name'):
        try:
            profile[name] = raw_json.get("orcid-profile").get("orcid-bio").get("personal-details").get(name.replace('_', '-')).get("value")
        except:
            profile[name] = None
    if profile['credit_name']:
        profile['name'] = profile['credit_name']
    else:
        profile['name'] = profile['given_names'] + ' ' + profile['family_name']
    try:
        profile['email'] = raw_json.get("orcid-profile").get("orcid-bio").get("contact-details").get("email")[0].get("value").lower().strip()
    except:
        profile['email']
    profile['affiliation'] = get_current_affiliation(orcid_id)
    try:
        profile['bio'] = raw_json.get('orcid-profile').get('orcid-bio').get('biography').get('value')
    except:
        profile['bio'] = None
    profile['gravatarhash'] = hashlib.md5(profile['email'].encode('utf-8')).hexdigest()

    return profile


def get_works(orcid_id):
    """ Return dictionary containing work of person with ORCID id. Dict indexed by DOI of works """
    raw_json = _get_raw_json(orcid_id, "/orcid-works")
    works = raw_json['orcid-profile']['orcid-activities']['orcid-works']['orcid-work']
    d = []
    for item in works:
        doi, tmp_d = work_item(item)
        if tmp_d:
            d.append({"doi": doi,
                      "image": ""})
            d[-1].update(tmp_d)
    return d

def get_current_affiliation(orcid_id):
    #raw_json = _get_raw_json(orcid_id, "orcid-employment")
    string = "I am from the university of life mate"
    return string
    
def work_item(item):
    dobj={}
    if item['work-external-identifiers'] and item['work-citation']:
        doi = item['work-external-identifiers']['work-external-identifier'][0]['work-external-identifier-id']['value']
        dobj['cite'] = item['work-citation']['citation']
        if item['url']:
            dobj['url'] = item['url'].get("value")
        else:
            dobj['url'] = "Not available"
        dobj['title'] = item['work-title']['title']['value']
        dobj['subtitle'] = item.get('work-title').get("subtitle")
        dobj['description'] = item.get('short-description')
        #dobj['type'] = item['type']
        return doi, dobj,
    else:
        return None, None
