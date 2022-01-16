# -*- coding: utf-8 -*-
import os
import json
from typing import List

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
            'AccessKeyID': '',
            'AccessKeySecret': '',
            'Domain': '',
            'Records': []
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


def get_ipv4():
    return requests.get('https://api4.ipify.org/?format=json').json()['ip']


def get_ipv6():
    return requests.get('https://api6.ipify.org/?format=json').json()['ip']


def get_old_records(domain: str, client: AcsClient) -> List[dict]:
    request = DescribeDomainRecordsRequest.DescribeDomainRecordsRequest()
    request.set_accept_format('json')
    request.set_DomainName(domain)
    response = client.do_action_with_exception(request)
    return json.loads(response)['DomainRecords']['Record']


def get_old_record(records: List[dict], RR: str, type_: str) -> dict:
    for i in records:
        if i['RR'] == RR and i['Type'] == type_:
            return i


def set_record(RR: str, type_: str, record_id: str, value: str,
               client: AcsClient):
    request = UpdateDomainRecordRequest.UpdateDomainRecordRequest()
    request.set_accept_format('json')
    request.set_RR(RR)
    request.set_RecordId(record_id)
    request.set_Type(type_)
    request.set_Value(value)

    print(json.loads(client.do_action_with_exception(request)))


def main():
    config = Config()
    client = AcsClient(config['AccessKeyID'], config['AccessKeySecret'])
    # 获取所有记录
    old_records = get_old_records(config['Domain'], client)

    # 遍历配置记录
    for i in config['Records']:
        # 获取匹配的记录
        old_record = get_old_record(old_records, i['RR'], i['Type'])
        # 获取IP
        if i['Type'] == 'A':
            ip = get_ipv4()
        elif i['Type'] == 'AAAA':
            ip = get_ipv6()
        else:
            continue
        # 判断IP是否变化
        if old_record['Value'] == ip:
            print(f'Record "{i["RR"]}" Type {i["Type"]} has no change')
        else:
            # 设置新IP
            set_record(i['RR'], i['Type'], old_record['RecordId'], ip, client)


if __name__ == '__main__':
    main()
