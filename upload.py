import argparse
import hashlib
import os
import tqdm

from gavc.artifactory_client import ArtifactoryClient
from gavc.query import Query
from gavc.pom import Pom

################################################################################
class UploadSpec:
    SEPA    = ':'
    EXT     = '.'

    def __init__(self, classifier, ext, filepath):
        self.__classifier   = classifier
        self.__ext          = ext
        self.__filepath     = filepath

    def __str__(self):
        return "classifier: '%s' ext: '%s' filepath: '%s'" % (self.__classifier, self.__ext, self.__filepath)

    @property
    def classifier(self):
        return self.__classifier

    @property
    def ext(self):
        return self.__ext

    @property
    def filepath(self):
        return self.__filepath

    @staticmethod
    def parse(input_string):
        classifier  = ""
        ext         = ""
        filepath    = ""
        assert UploadSpec.SEPA in input_string
        parts = input_string.split(UploadSpec.SEPA, 1)
        classifier  = parts[0]
        filepath    = parts[1]
        if UploadSpec.EXT in classifier:
            parts = classifier.split(UploadSpec.EXT, 1)
            classifier  = parts[0]
            ext         = parts[1]
        if not ext:
            ext         = os.path.splitext(filepath)
            if ext: ext = ext[1][1:]
        return UploadSpec(classifier, ext, filepath)

################################################################################
class UploadObject:
    __CHECKSUMS_CLASSES = {
        "md5": hashlib.md5,
        "sha1": hashlib.sha1,
        "sha256": hashlib.sha256,
    }

    def __init__(self, client, query):
        self._client = client
        self._query = query
        self.__progress_bar = None
        self._init_checksums()

    def _init_progress_bar(self, total_size_in_bytes):
        self.__progress_bar = tqdm.tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)

    def update_progress_bar(self, chunk):
        if self.__progress_bar:
            self.__progress_bar.update(len(chunk))

    def close_progress_bar(self):
        if self.__progress_bar:
            self.__progress_bar.close()
        self.__progress_bar = None

    def _init_checksums(self):
        self.__checksums = {}
        for name, cls in self.__CHECKSUMS_CLASSES.items():
            self.__checksums[name] = cls()

    def update_checksums(self, chunk):
        for name, summ in self.__checksums.items():
            summ.update(chunk)

    def get_summ(self, name):
        assert name in self.__checksums
        return self.__checksums[name].hexdigest()

    def all_summs(self):
        for name, _ in self.__checksums.items():
            yield name


################################################################################
class FileToUpload(UploadObject):
    __CHUNK_SIZE = 1 * 1024 * 1024

    def __init__(self, client, query, upload_spec):
        UploadObject.__init__(self, client, query)
        self.__spec = upload_spec

    def url(self):
        return self._client.repository_url(self._query.object_path(self.__spec.classifier, self.__spec.ext))

    def read(self):
        s = os.stat(self.__spec.filepath)
        self._init_progress_bar(s.st_size)
        self._init_checksums()
        with open(self.__spec.filepath, 'rb') as f:
            while True:
                chunk = f.read(self.__CHUNK_SIZE)
                if not chunk:
                    break
                self.update_checksums(chunk)
                yield chunk
                self.update_progress_bar(chunk)
        self.close_progress_bar()


################################################################################
class PomToUpload(UploadObject):
    def __init__(self, client, query, pom):
        UploadObject.__init__(self, client, query)
        self.__pom = pom

    def url(self):
        return self._client.repository_url(self._query.pom_path())

    def read(self):
        chunk = self.__pom.tobytes()
        self._init_progress_bar(len(chunk))
        self._init_checksums()
        self.update_checksums(chunk)
        yield chunk
        self.update_progress_bar(chunk)
        self.close_progress_bar()


################################################################################
def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--upload",
        required=True,
        action="append",
        help="List of files to upload (required). Expected format is: <classifier>[.<ext>]:<filepath>"
    )

    parser.add_argument(
        "target",
        nargs=1,
        help="Gavc target."
    )

    args = parser.parse_args()

    print(" - Uploads: %s" % repr(args.upload))
    print(" - Gavc: %s" % repr(args.target))

    q = Query.parse(args.target[0])

    if q.version() is None or not q.version().is_single_version():
        raise Exception("Gavc target '%s' is not a single version target!" % args.target[0])

    print(" - Artifact path: %s" % q.artifact_path())

    client = ArtifactoryClient()
    client.cache().disable()

    versions    = []
    if not q.version().is_const():
        versions.extend(client.requests().versions_for(q))
    else:
        versions.append(str(q.version()))

    if len(versions) != 1:
        raise Exception("Can't resolve version for upload target '%s'!" % args.target[0])

    q.set_version(versions[0])

    print(" - Version url: %s" % client.repository_url(q.version_path()))

    uploads = []
    for upload_spec in args.upload:
        print(" - Parse upload spec: %s" % upload_spec)
        uploads.append(FileToUpload(client, q, UploadSpec.parse(upload_spec)))
    uploads.append(PomToUpload(client, q, q.pom()))

    for o2u in uploads:
        url = o2u.url()
        print(" - Upload: %s" % url)
        client.requests().put2(url, data=o2u.read())
        for summ in o2u.all_summs():
            url_summ = url + "." + summ
            summ_value = o2u.get_summ(summ)
            print(" - Upload %s: %s <= %s" % (summ, url_summ, summ_value))
            client.requests().put2(url_summ, data=summ_value)

################################################################################
if __name__ == "__main__":
    main()
