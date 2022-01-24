# Copyright (c) 2022, FOSS United and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import ipaddress
import requests

class MonSchoolUserSubdomain(Document):
    def before_save(self):
        if self.ip:
            self.ip = self.ip.strip()
            self._validate_ip(self.ip)

    def on_update(self):
        if not self.subdomain or not self.ip:
            return
        token = self.get_digital_ocean_token()
        do_api = DigitalOcean(token)
        self._add_dns_record(do_api, self.subdomain, self.ip)
        self._add_dns_record(do_api, "*." + self.subdomain, self.ip)

    def _add_dns_record(self, do_api, subdomain, ip):
        records = do_api.query_records("monschool.net", subdomain)
        for r in records:
            do_api.delete_record("monschool.net", r['id'])
        do_api.insert_record("monschool.net", subdomain, ip)

    def get_digital_ocean_token(self):
        doc = frappe.get_doc("Mon School Settings")
        if not doc.digitalocean_api_token:
            frappe.msgprint("Please set digitalocean_api_token in the Mon School Settings")
            raise Exception("The digitalocean_api_token is not set in the Mon School Settings")
        return doc.digitalocean_api_token

    def _validate_ip(self, ip):
        try:
            ipaddress.IPv4Address(ip)
        except ValueError:
            frappe.msgprint(f"Invalid IP Address: {self.ip}")
            raise frappe.exceptions.ValidationError(f"Invalid IP address: {self.ip}")


class DigitalOcean:
    def __init__(self, token):
        self.token = token
        self.headers = {"Authorization": f"Bearer {token}"}

    def query_records(self, domain, name):
        fqdn = f"{name}.{domain}"
        url = f"https://api.digitalocean.com/v2/domains/{domain}/records"
        params = {"name": fqdn}

        response = requests.get(url, params=params, headers=self.headers)
        response.raise_for_status()
        d = response.json()
        return d['domain_records']

    def insert_record(self, domain, name, ip):
        url = f"https://api.digitalocean.com/v2/domains/{domain}/records"
        data = {
            "type": "A",
            "name": name,
            "data": ip,
        }
        try:
            response = requests.post(url, json=data, headers=self.headers)
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            print("ERROR: " + response.text)
            raise
        print(f"Inserted DNS record: {name}.{domain} A {ip}")

    def delete_record(self, domain, record_id):
        url = f"https://api.digitalocean.com/v2/domains/{domain}/records/{record_id}"
        response = requests.delete(url, headers=self.headers)
        response.raise_for_status()
        print(f"Deleted DNS record: {domain} {record_id}")

