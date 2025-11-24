from urllib.parse import urlparse

import requests

from utils.apig_sdk import signer
from utils.app_config import config
from utils.common_utils import decrypt, get_proxy

SECMASTER_ALERT_TEMPLATE = {"description": "", "title": "", "alert_type":{"category": "1111", "alert_type": "1111"}, "workspace_id": "1", "domain_id": "1", "verification_state": "Unknown", "handle_status": "Open", "severity": "Tips", "creator": "hwstaff_intl_eu_CBUSOC", "create_time": "2025-11-13T21:08:39.255Z+0000", "region_id": "eu-west-101", "version": "1.0.0", "data_source":{"domain_id": "111", "product_feature": "1", "project_id": "111", "company_name": "Huawei", "region_id": "1", "source_type":1, "product_name": "1"}, "environment":{"domain_id": "1", "project_id": "1", "region_id": "111", "vendor_type": "HWC"}}
SECMASTER_INCIDENT_TEMPLATE = {"incident_type":{"incident_type": "AKSK风险", "id": "34657b3a7f8e00a23a973edbada77e31", "category": "数据泄露"}, "simulation": "false", "description": "123123", "title": "test123", "workspace_id": "1", "domain_id": "1", "verification_state": "Unknown", "handle_status": "Open", "id": "1", "severity": "Tips", "creator": "1", "create_time": "2025-11-14T18:35:36.968Z+0000", "ttd":0, "region_id": "1", "count":1, "version": "1.0.0", "data_source":{"domain_id": "1", "product_feature": "hss", "project_id": "1", "company_name": "Huawei", "region_id": "1", "source_type":1, "product_name": "hss"}, "data_sources":[{"domain_id": "1", "product_feature": "hss", "project_id": "1", "company_name": "Huawei", "region_id": "1", "source_type":1, "product_name": "hss"}], "labels": "", "environment":{"domain_id": "1", "project_id": "1", "region_id": "1", "vendor_type": "HWC"}, "ipdrr_phase": "Preparation", "creator_id": "def", "creator_name": "abc"}

def _sign(method, uri, headers, AK, SK, body=None):
    sig = signer.Signer()
    # Set the AK/SK to sign and authenticate the request.
    sig.Key = AK
    sig.Secret = SK

    r = signer.HttpRequest(method, uri)
    r.headers = headers
    if body:
        r.body = body
    sig.Sign(r)
    return r


def _remove_last_slash(url):
    if url:
        return url if not url.endswith("/") else url[:-1]
    else:
        return url


def _get_domain_from_url(url):
    return url if not url else urlparse(url).hostname


def build_conditions_and_logics(input_conditions):
    conditions = []
    logics = []
    i = 0
    for data in input_conditions:
        for field, value in data.items():
            condition = {
                "name": field + str(i),
                "data": [
                    field,
                    "contains",
                    value
                ]
            }
            conditions.append(condition)
            logics.append("and")
            logics.append(field + str(i))
            i = i + 1

    logics = logics[1:]
    return conditions, logics


# Get IAM token by username and password
def _get_iam_token(domain_name, username, password, project_id, proxies=None):
    iam_url = config.get("application.secmaster.iam_auth_url")

    headers = {
        "Content-Type": "application/json;charset=utf8"
    }

    payload = {
        "auth": {
            "identity": {
                "methods": [
                    "password"
                ],
                "password": {
                    "user": {
                        "domain": {
                            "name": domain_name
                        },
                        "name": username,
                        "password": password
                    }
                }
            },
            "scope": {
                "project": {
                    "id": project_id
                }
            }
        }
    }

    resp = requests.post(url=iam_url, json=payload, headers=headers, proxies=proxies, verify=False, timeout=10)

    if resp.status_code > 300:
        raise Exception(resp.text)
    else:
        return resp.headers["X-Subject-Token"]


def _wrap_http_auth_headers(method, url, headers, body=None):
    """
    add signature to headers and return final url and headers
    """
    # AK/SK sign
    secmaster_base_url = config.get("application.secmaster.base_url")
    ak = config.get("application.secmaster.ak")
    sk = decrypt(config.get("application.secmaster.sk"))

    if ak and sk:
        r = _sign(method, url, headers, ak, sk, body)
        headers = r.headers

        # 在使用API代理的情况下需要确保签名使用真正的API网关URL，发送的时候修改URL和host指向代理，代理收到请求后替换URL和HOST
        if config.get("application.secmaster.apig_proxy_base_url"):
            apig_proxy_base_url = config.get("application.secmaster.apig_proxy_base_url")
            proxy_base_url = _remove_last_slash(apig_proxy_base_url)
            url = url.replace(secmaster_base_url, proxy_base_url)
            headers["host"] = _get_domain_from_url(proxy_base_url)
    elif config.get("application.secmaster.password"):
        # 获取iam_token
        enable_proxy = config.get("application.proxy.enabled")
        proxy_host = config.get("application.proxy.host")
        proxy_username = config.get("application.proxy.username")
        proxy_password = decrypt(config.get("application.proxy.password"))
        proxies = get_proxy(proxy_host, proxy_username, proxy_password) if enable_proxy else None

        iam_token = _get_iam_token(domain_name=config.get("application.secmaster.domainname"),
                                  username=config.get("application.secmaster.username"),
                                  password=decrypt(config.get("application.secmaster.password")),
                                  project_id=config.get("application.secmaster.project_id"),
                                  proxies=proxies)
        headers["X-Auth-Token"] = iam_token

    return url, headers


def request_with_auth(method, url, headers, data=None):
    """
    request url with auth headers
    """
    url, headers = _wrap_http_auth_headers(method, url, headers, data)

    enable_proxy = config.get("application.proxy.enabled")
    proxy_host = config.get("application.proxy.host")
    proxy_username = config.get("application.proxy.username")
    proxy_password = decrypt(config.get("application.proxy.password"))
    proxies = get_proxy(proxy_host, proxy_username, proxy_password) if enable_proxy else None

    return requests.request(method, url=url, data=data, headers=headers, proxies=proxies, verify=False, timeout=20)

