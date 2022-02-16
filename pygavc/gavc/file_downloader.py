import os
import requests
import tqdm

from .fs_utils import FsUtils

class FileDownloader:
    def __init__(self, requests, destination_file, url, enable_progress_bar):
        self.__requests             = requests
        self.__destination_file     = destination_file
        self.__url                  = url
        self.__enable_progress_bar  = enable_progress_bar


    def __call__(self):

        FsUtils.ensure_parent_dir(self.__destination_file)

        r = self.__requests.get2(self.__url, stream=True)
        if r.status_code != self.__requests.HTTP_OK:
            raise self.__requests.make_http_error(r.status_code)

        progress_bar = None
        if self.__enable_progress_bar:
            total_size_in_bytes = int(r.headers.get('content-length', 0))
            block_size          = 1024*1024
            progress_bar        = tqdm.tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)

        with open(self.__destination_file, 'wb') as f:
            for chunk in r.iter_content(block_size):
                if progress_bar: progress_bar.update(len(chunk))
                f.write(chunk)

        if progress_bar: progress_bar.close()
