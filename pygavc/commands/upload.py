import hashlib
import os
import tqdm



################################################################################
class Spec:
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
        assert Spec.SEPA in input_string
        parts = input_string.split(Spec.SEPA, 1)
        classifier  = parts[0]
        filepath    = parts[1]
        if Spec.EXT in classifier:
            parts = classifier.split(Spec.EXT, 1)
            classifier  = parts[0]
            ext         = parts[1]
        if not ext:
            ext         = os.path.splitext(filepath)
            if ext: ext = ext[1][1:]
        return Spec(classifier, ext, filepath)



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
        self.__progress_bar = tqdm.tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True, desc="Upload object")

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
class UploadFile(UploadObject):
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
class UploadPom(UploadObject):
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
