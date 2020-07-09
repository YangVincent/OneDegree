# I've removed commas from 
# 10,000 degrees
# A Caring Mind, Inc
# A Woman's Place Community Awareness & Treatment Services, Inc. (CATS)

import csv
import pycurl
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
    return None, None


if __name__ == "__main__":
    #websites = get_websites()
    websites = get_only_websites()

    modified_count = 0
    unknown_count = 0
    error_count = 0

    for site in websites[0:500]:
        content, err = curl_website(site)
        if err is not None:
            print("Got an error for " + site + " -- error is " + str(err))
            error_count = error_count + 1
            continue

        if 'last-modified' in headers:
            print("Last modified:")
            print(headers['last-modified'])
            print('-' * 20)
            modified_count = modified_count + 1
        else:
            print("Skipping")
            unknown_count = unknown_count + 1

    print("Final modified count: " + str(modified_count))
    print("Final unknown count: " + str(unknown_count))


