# -*- coding: utf-8 -*-
import os
import json

import requests
from aliyunsdkcore.client import AcsClient
from aliyunsdkalidns.request.v20150109 import (
    DescribeDomainRecordsRequest,
    UpdateDomainRecordRequest
)


class Config:
    def __init__(self):
        self.path = 'config.json'
        self.default = {
            'IPV6': True,
            'AccessKeyID': '',
            'AccessKeySecret': '',
            'Domain': '',
            'RR': ''
        }
        self.data = None
        self._check()

    def _check(self):
        self._read()
        save_flag = False
        for key, value in self.default.items():
            if key not in self.data.keys():
                self.data[key] = value
                save_flag = True
        if save_flag:
            self._save()

    def _read(self):
        if os.path.isfile(self.path):
            with open(self.path) as f:
                self.data = json.load(f)
        else:
            self.data = self.default
            self._save()

    def _save(self):
        with open(self.path, 'w') as f:
            json.dump(self.data, f, indent=4)

    def get(self, key):
        if key not in self.data.keys():
            raise ValueError(key + ' is not in configuration')
        else:
            return self.data[key]

    def __getitem__(self, key):
        return self.get(key)


def get_ip(ipv6=False):
    if ipv6:
        return requests.get('https://api6.ipify.org/?format=json').json()['ip']
    else:
        return requests.get('https://api4.ipify.org/?format=json').json()['ip']


def get_old_record(domain: str, RR: str, client: AcsClient):
    request = DescribeDomainRecordsRequest.DescribeDomainRecordsRequest()
    request.set_accept_format('json')

    request.set_DomainName(domain)

    response = client.do_action_with_exception(request)
    for i in json.loads(response)['DomainRecords']['Record']:
        if i['RR'] == RR:
            return i


def main():
    config = Config()
    client = AcsClient(config['AccessKeyID'], config['AccessKeySecret'])

    old_record = get_old_record(config['Domain'], config['RR'], client)
    ip = get_ip(config['IPV6'])
    if old_record['Value'] == ip:
        print('No changed')
        return
    request = UpdateDomainRecordRequest.UpdateDomainRecordRequest()
    request.set_accept_format('json')

    request.set_RR(config['RR'], )
    request.set_RecordId(old_record['RecordId'])
    request.set_Type('AAAA' if config['IPV6'] else 'A')
    request.set_Value(ip)

    print(json.loads(client.do_action_with_exception(request)))


if __name__ == '__main__':
    main()
