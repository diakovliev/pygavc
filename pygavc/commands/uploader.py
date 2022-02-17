import argparse
import os

from ..gavc.artifactory_client import ArtifactoryClient
from ..gavc.query import Query
from ..gavc.pom import Pom
from .upload import Spec, UploadFile, UploadPom

################################################################################
class Uploader:
    def __init__(self, target, uploads):
        self.__target   = target
        self.__uploads  = uploads

    def __call__(self):

        q = Query.parse(self.__target)

        if q.version() is None or not q.version().is_single_version():
            raise Exception("Gavc target '%s' is not a single version target!" % self.__target)

        print(" - Artifact path: %s" % q.artifact_path())

        client = ArtifactoryClient.from_params_handler()
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
        for upload_spec in self.__uploads:
            print(" - Parse upload spec: %s" % upload_spec)
            uploads.append(UploadFile(client, q, Spec.parse(upload_spec)))
        uploads.append(UploadPom(client, q, q.pom()))

        for o2u in uploads:
            url = o2u.url()
            print(" - Upload: %s" % url)
            client.requests().put2(url, data=o2u.read())
            for summ in o2u.all_summs():
                url_summ = url + "." + summ
                summ_value = o2u.get_summ(summ)
                print(" - Upload %s: %s <= %s" % (summ, url_summ, summ_value))
                client.requests().put2(url_summ, data=summ_value)
