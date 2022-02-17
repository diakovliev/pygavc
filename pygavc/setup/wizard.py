import sys
from PyQt5 import QtCore, QtWidgets

from ..gavc.gavc_parameters import GavcClientBaseParamsHandler
from ..gavc.artifactory_client import ArtifactoryClient
from ..gavc.client_cache import ClientCache
from ..gavc.user_config import UserConfig

################################################################################
class ConnectionParamsPage(QtWidgets.QWizardPage):
    checkingComplete = QtCore.pyqtSignal(str)

    def __init__(self):
        QtWidgets.QWizardPage.__init__(self)
        self.setTitle("Artifactory connection parameters")

        params_handler = GavcClientBaseParamsHandler()

        self.__complete     = False
        self.__server       = params_handler.get_param(GavcClientBaseParamsHandler.SERVER_PARAM)
        self.__repository   = params_handler.get_param(GavcClientBaseParamsHandler.REPOSITORY_PARAM)
        self.__token        = params_handler.get_param(GavcClientBaseParamsHandler.TOKEN_PARAM)

        layout = QtWidgets.QGridLayout()
        rowIndex = 0

        #####
        serverLabel = QtWidgets.QLabel()
        serverLabel.setText("Server url")

        serverEditor = QtWidgets.QLineEdit()
        serverEditor.setText(self.__server)
        serverEditor.textChanged.connect(self.on_server_changed)

        layout.addWidget(serverLabel, rowIndex, 0)
        layout.addWidget(serverEditor, rowIndex, 1)
        rowIndex += 1

        #####
        tokenLabel = QtWidgets.QLabel()
        tokenLabel.setText("API access token")

        tokenEditor = QtWidgets.QLineEdit()
        tokenEditor.setText(self.__token)
        tokenEditor.textChanged.connect(self.on_token_changed)

        layout.addWidget(tokenLabel, rowIndex, 0)
        layout.addWidget(tokenEditor, rowIndex, 1)
        rowIndex += 1

        #####
        checkButton = QtWidgets.QPushButton()
        checkButton.setText("Check connection...")
        checkButton.clicked.connect(self.check_connection)

        checkLabel = QtWidgets.QLabel()
        checkLabel.setText("Not checked")
        self.checkingComplete.connect(checkLabel.setText)

        layout.addWidget(checkButton, rowIndex, 0)
        layout.addWidget(checkLabel, rowIndex, 1)
        rowIndex += 1

        #####
        repoLabel = QtWidgets.QLabel()
        repoLabel.setText("Repository")

        repoEditor = QtWidgets.QLineEdit()
        repoEditor.setText(self.__repository)
        repoEditor.textChanged.connect(self.on_repository_changed)

        layout.addWidget(repoLabel, rowIndex, 0)
        layout.addWidget(repoEditor, rowIndex, 1)
        rowIndex += 1

        self.setLayout(layout)

    def __reset_complete(self, text = "Not checked"):
        self.checkingComplete.emit(text)
        self.__complete = False
        self.completeChanged.emit()

    def on_token_changed(self, token_value):
        self.__token = token_value
        self.__reset_complete()

    def on_server_changed(self, server_value):
        self.__server = server_value
        self.__reset_complete()

    def on_repository_changed(self, repository_value):
        self.__repository = repository_value

    def check_connection(self):
        cache   = ClientCache.from_params_handler()
        client  = ArtifactoryClient(cache, self.__server, self.__repository, self.__token)
        try:
            r = client.requests().get_local_repos()
            self.checkingComplete.emit("OK")
            self.__complete = True
            self.completeChanged.emit()

        except:
            self.__reset_complete("FAILED")

    def isComplete(self):
        return self.__complete

    def server(self):
        return self.__server

    def repository(self):
        return self.__repository

    def token(self):
        return self.__token

################################################################################
class Wizard(QtWidgets.QWizard):

    def __init__(self):
        QtWidgets.QWizard.__init__(self)
        self.setWindowTitle("PyGAVC parameters")

        self.__connection_params_page = ConnectionParamsPage()

        self.addPage(self.__connection_params_page)

        self.accepted.connect(self.on_accept)
        self.rejected.connect(self.on_cancel)
        self.finished.connect(self.on_finish)

    def on_accept(self):
        config = UserConfig.load()
        config.set_value(GavcClientBaseParamsHandler.SERVER_PARAM,      self.__connection_params_page.server())
        config.set_value(GavcClientBaseParamsHandler.REPOSITORY_PARAM,  self.__connection_params_page.repository())
        config.set_value(GavcClientBaseParamsHandler.TOKEN_PARAM,       self.__connection_params_page.token())
        config.store()

    def on_cancel(self):
        pass

    def on_finish(self):
        pass


################################################################################
def main():
    app = QtWidgets.QApplication(sys.argv)

    wizard = Wizard()
    wizard.show()

    app.exec()

################################################################################
if __name__ == "__main__":
    main()
