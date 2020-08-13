# I've removed commas from 
# 10,000 degrees
# A Caring Mind, Inc
# A Woman's Place Community Awareness & Treatment Services, Inc. (CATS)

import csv
import pycurl
import hashlib
from io import BytesIO

headers = {}

def display_header(header_line):
    header_line = header_line.decode('iso-8859-1')

    # Ignore all lines without a colon
    if ':' not in header_line:
        return

    # Break the header line into name and value
    h_name, h_value = header_line.split(':', 1)

    # Remove whitespace that may be present
    h_name = h_name.strip()
    h_value = h_value.strip()
    h_name = h_name.lower()
    headers[h_name] = h_value



"""
get_websites retrieves all websites from the csv.
"""
def get_websites():
    print("Getting Websites")
    websites = []
    with open('organizations.csv', newline='') as csvfile:
        orgreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for org in orgreader:
            websites.append(org[2].replace('"', ''))
    # Remove the header, which isn't a website
    return websites[1:]

def get_only_websites():
    websites = []
    with open('org2.csv') as f:
        sites = f.readlines()
        for site in sites[1:]:
            websites.append(site.strip())

    return websites


def curl_website(site):
    print("site is " + site)
    b_obj = BytesIO()
    crl = pycurl.Curl()

    # Set URL Value
    crl.setopt(crl.URL, site)

    # Get headers
    crl.setopt(crl.HEADERFUNCTION, display_header)

    # Write bytes that are utf-8 encoded
    crl.setopt(crl.WRITEDATA, b_obj)

    # Follow location
    crl.setopt(pycurl.FOLLOWLOCATION, True)

    # Set timeout (if the site is down)
    crl.setopt(pycurl.TIMEOUT, 5)

    # Perform file transfer
    try: 
        crl.perform()
    except pycurl.error as e:
        return None, e

    # End curl session
    crl.close()

    # Get content stored in BytesIO object (in bytes characters)
    get_body = b_obj.getvalue()

    # Decode bytes stored in get_body to HTML and print the result
    #print('Output of GET request:\n%s' % get_body.decode('utf8')) 
    #return None, None
    try:
        return get_body.decode('utf8'), None
    except:
        print("Decoding utf8 error. Returning none")
        return None, None


# Return a list of sites that MAY have changed.
if __name__ == "__main__":
    #websites = get_websites()
    websites = get_only_websites()

    modified_count = 0
    modified_new_count = 0
    unknown_count = 0
    error_count = 0

    changed = [] # list of sites that may have changed


    # Store the hash of each site url -> hash
    old_cache = {} # TODO(yangvincent): Upload old cache from file.
    new_cache = {}

    for site in websites:
        content, err = curl_website(site)
        new_cache[site] = hashlib.md5(content)

        # We don't know if it's changed if we can't pull it, so ask people to check.
        if err is not None:
            print("Got an error for " + site + " -- error is " + str(err))
            error_count = error_count + 1
            changed.append(site) 
            continue

        # If we can tell that it definitely didn't change due to last-modified, skip.
        if 'last-modified' in headers:
            print("Last modified:")
            print(headers['last-modified'])
            print('-' * 20)
            # TODO(yangvincent): Make this detection more granular/sustainable.
            if '2020' not in headers['last-modified']:
                continue
        # Check to see if our hashed results have changed
        if site in old_cache and site in new_cache:
            if old_cache[site] != new_cache[site]:
                # Store that this site has changed
                changed.append(site)
            continue
        # If it's missing from either of our caches, add.
        changed.append(site)


    print("Final modified new count (possibly new): " + str(modified_new_count))
    print("Final modified old count (definitely old): " + str(modified_count))
    print("Final unknown count: " + str(unknown_count))

    # TODO(yangvincent): Save new cache to file.


