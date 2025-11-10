import os
from obs import ObsClient, CompletePart, CompleteMultipartUploadRequest

from tenacity import wait_random_exponential, stop_after_attempt, retry
from utils.app_config import Configuration
from utils.common_utils import decrypt
from utils.logger_init import logger


class OBSUtil(object):
    ak = None
    sk = None
    conf = Configuration()

    def __init__(self, HW_AK, HW_SK):
        self.ak = HW_AK
        self.sk = HW_SK

    def get_client(self, region):
        if self.conf.get('application.proxy.disabled') == "false":
            return ObsClient(
                access_key_id=self.ak,
                secret_access_key=self.sk,
                server=region if ("https://" in region) else self.conf.get(region)['uri'],
                proxy_host=self.conf.get('application.proxy.proxy_host'),
                proxy_port=self.conf.get('application.proxy.proxy_port'),
                proxy_username=decrypt(self.conf.get('application.proxy.username')),
                proxy_password=decrypt(self.conf.get('application.proxy.password')),
            )
        else:
            return ObsClient(
                access_key_id=self.ak,
                secret_access_key=self.sk,
                server=region if ("https://" in region) else self.conf.get(region)['uri'])

    def get_obj_metadata(self, bucket_name, object_key, region='cn-north-4'):
        obs_client = self.get_client(region)

        resp = obs_client.getObjectMetadata(bucket_name, object_key)
        if resp.status >= 300:
            return None
        else:
            return resp

    def download_object(self, bucket_name, object_key, region='cn-north-4', download_path=None):
        obs_client = self.get_client(region)
        if os.path.exists(download_path):
            os.remove(download_path)
        resp = obs_client.getObject(bucket_name, object_key, downloadPath=download_path)
        if resp.status < 300:
            logger.info(f"downloaded {bucket_name}/{object_key} to local server {download_path}.")
        else:
            raise Exception("fail to download from obs: " + resp.reason)

    @retry(wait=wait_random_exponential(min=1, max=3), stop=stop_after_attempt(3))
    def download_object_with_checkpoint(self, bucket_name, object_key, download_path, part_size=10 * 1024 * 1024, task_num=10, region='cn-north-4'):
        obs_client = self.get_client(region)
        resp = obs_client.downloadFile(bucket_name, object_key, download_path, part_size, task_num, enableCheckpoint=True)
        if resp.status < 300:
            logger.info(f"downloaded {bucket_name}/{object_key} to local server {download_path}.")
        else:
            raise Exception("fail to download from obs: " + resp.reason)

    def upload_object(self, bucket_name, object_name, file_path, region='cn-north-4'):
        obs_client = self.get_client(region)

        resp = obs_client.putFile(bucket_name, object_name, file_path=file_path)
        if resp.status < 300:
            logger.info(f'[*] upload file from {file_path} to obs://{bucket_name}/{object_name}.')
            return True
        else:
            logger.info(f'[*] fail to upload {object_name} with error: {resp.reason}.')
            raise Exception(f'[*] fail to upload {object_name} with error: {resp.reason}.')

    def multiple_upload_object(self, bucket_name, object_name, file_path, region='cn-north-4'):
        obs_client = self.get_client(region)
        resp = obs_client.initiateMultipartUpload(bucket_name, object_name, contentType='text/plain')
        upload_id = resp.body["uploadId"]
        part_num = 1
        offset = 0
        etags = {}
        part_size = 512 * 1024 * 1024
        content_length = os.path.getsize(file_path)
        while offset < content_length:
            part_size = min(part_size, (content_length - offset))
            # 用于上传段
            resp1 = obs_client.uploadPart(bucket_name, object_name, part_num, upload_id, file_path, True, part_size, offset)
            etags[part_num] = resp1.body.etag
            offset = offset + part_size
            part_num = part_num + 1
        completes = []
        for i in range(1, part_num):
            completes.append(CompletePart(i, etags[i]))
        # 用于合并段
        completeMultipartUploadRequest = CompleteMultipartUploadRequest(parts=completes)
        resp = obs_client.completeMultipartUpload(bucket_name, object_name, upload_id, completeMultipartUploadRequest)
        # 返回码为2xx时，接口调用成功，否则接口调用失败
        if resp.status < 300:
            logger.info(f'[*] upload file from {file_path} to obs://{bucket_name}/{object_name}.')
            return True
        else:
            logger.info(f'[*] fail to upload {object_name} with error: {resp.reason}.')
            raise Exception(f'[*] fail to upload {object_name} with error: {resp.reason}.')

    def upload_object_process(self, bucket_name, object_name, file_path, region='cn-north-4', process=None):
        obs_client = self.get_client(region)

        def callback(transferred_amount, total_amount, total_seconds):
            if process["item"]["process"] != int(transferred_amount * 100.0 / total_amount):
                process["item"]["process"] = int(transferred_amount * 100.0 / total_amount)

        resp = obs_client.putFile(bucket_name, object_name, file_path=file_path, progressCallback=callback)
        if resp.status < 300:
            logger.info(f'[*] upload {object_name} from {file_path} to {bucket_name}.')
            return True
        else:
            logger.info(f'[*] fail to upload {object_name} with error: {resp.reason}.')
            raise Exception(f'[*] fail to upload {object_name} with error: {resp.reason}.')

    def check_connection(self, uri):
        obs_client = self.get_client(uri)
        resp = obs_client.listBuckets(True)
        if resp.status < 300:
            return True
        else:
            return False

    def list_object(self, bucket_name, region, prefix):
        obs_client = self.get_client(region)
        resp = obs_client.listObjects(bucket_name, prefix)
        try:
            return resp.body.contents
        except Exception as ex:
            logger.exception(ex)
            raise Exception(resp.body)

