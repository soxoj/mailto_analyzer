#!/usr/bin/python3

from email.header import decode_header

import mailbox
import ntpath
import re
import sys
import tqdm

from termcolor import colored

class Contact:
    def __init__(self, header):
        self.value = header.__str__()
        self.email = ""
        self.name = ""
        self.value = self.value.replace('\n', '')

        if ' ' in self.value:
            self.name, self.email = self.value.rsplit(' ', 1)
        elif '\t' in self.value:
            self.name, self.email = self.value.rsplit('\t', 1)
        else:
            self.email = self.value

        # print(self.email)
        # print(self.name)
        # print(self.value)

        if '=?' in self.name:
            parts = decode_header(self.name.strip('"'))
            name = ""
            for p in parts:
                if p[1]:
                    name += p[0].decode(p[1])
                else:
                    name += p[0].decode()
            self.name = name

        self.name = re.sub(r'["<>\']', '', self.name).strip()
        self.email = re.sub(r'["<>\']', '', self.email).strip()


SERVICES = {
    'uber.com': [
        'Uber',
        """Change email: Open Application => Profile log in top right corner => tap "Email" => change it to alias+uber@example.com
Remove account: https://justdeleteme.xyz/#uber"""
    ],
    'meetup.com': [
        'Meetup',
        """Change email: for now it\'s impossible to change email address, unfortunately
Remove account: https://justdeleteme.xyz/#meetup"""
    ],
    'gravatar.com': [
        'Gravatar',
        'For now it\'s impossible to change email address or remove account, but you still can change "Display name" (https://gravatar.com/profile/about) or suspend it (https://gravatar.com/profile/disable-account)'
    ],
    'pinterest.com': [
        'Pinterest',
        """Change email: Open https://pinterest.com/settings/account-settings/ => change email address to alias+pinterest@example.com => confirm via email
Remove account: https://justdeleteme.xyz/#pinterest"""
    ],
    'strava.com': [
        'Strava',
        """Change email: Open https://www.strava.com/settings/email_change => change email address to alias+strava@example.com, confirm with password
Remove account: https://justdeleteme.xyz/#strava"""
    ]
}


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: analyzer.py [path_to_mbox]')
        sys.exit(1)

    mbox_file = sys.argv[1]
    file_name = ntpath.basename(mbox_file).lower()

    addresses = {}
    print('Loading of the emails file...')

    for email in tqdm.tqdm(mailbox.mbox(mbox_file)):
        if "X-Gmail-Labels" in email and not "Inbox" in email["X-Gmail-Labels"]:
            continue

        to = email.get('to', '')
        if not to:
            print(colored('Empty header, skipping', 'red'))
            continue

        if ',' in str(to):
            print(colored('Several recepients, skipping', 'red'))
            continue

        sent_from = Contact(email["from"])
        sent_to = Contact(to)

        if sent_to == "" or sent_from == "":
            continue

        if not '@' in sent_to.email and sent_to.email != sent_to.name:
            email = sent_to.name
            sent_to.name = sent_to.email
            sent_to.email = email

        if sent_to.name:
            pair = f"{sent_to.name} <{sent_to.email}>"
        else:
            pair = sent_to.email

        if not pair in addresses:
            addresses[pair] = {"services": set(), "emails": set()}

        addresses[pair]["services"].add(sent_from.name)
        addresses[pair]["emails"].add(sent_from.email)

    print(colored('The following recepients were found:', 'green'))

    for email, senders in addresses.items():
        senders_list = list(senders["services"])
        senders = ', '.join(senders_list)
        print(f'{colored(email, "magenta")}: {senders}')

    found_services_in_emails = {}

    for email, senders in addresses.items():
        email_list = list(addresses[email]["emails"])
        for email in email_list:
            for serv, data in SERVICES.items():
                if serv in email:
                    if not serv in found_services_in_emails:
                        found_services_in_emails[serv] = {
                            "emails": set(),
                            "msg": f'Detected usage of service "{data[0]}" with email addresses: '
                        }

                    found_services_in_emails[serv]["emails"].add(email)

    print()
    for serv, data in found_services_in_emails.items():
        print(colored(data["msg"], 'green') + ", ".join(data["emails"]))
        print(colored('Instructions:\n', 'green') + colored(SERVICES[serv][1], 'yellow'))
        print()
