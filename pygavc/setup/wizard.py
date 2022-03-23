import sys
import json
from PyQt5 import QtCore, QtWidgets

from ..gavc.gavc_parameters import GavcClientBaseParamsHandler, GavcClientParamsHandler
from ..gavc.artifactory_client import ArtifactoryClient
from ..gavc.client_cache import ClientCache
from ..gavc.user_config import UserConfig

################################################################################
class CacheParamsPage(QtWidgets.QWizardPage):
    cachePathSelected = QtCore.pyqtSignal(str)

    def __init__(self, params_handler):
        QtWidgets.QWizardPage.__init__(self)
        self.setTitle("Artifactory client cache parameters")

        self.__complete         = True
        self.__params_handler   = params_handler

        current_cache_path      = self.__params_handler.get_param(GavcClientParamsHandler.CACHE_PATH_PARAM)

        layout = QtWidgets.QGridLayout()
        rowIndex = 0

        cachePathLabel = QtWidgets.QLabel()
        cachePathLabel.setText("Cache path")

        cachePathEditor = QtWidgets.QLineEdit()
        cachePathEditor.setText(current_cache_path)
        cachePathEditor.textChanged.connect(self.on_cache_path_changed)
        self.cachePathSelected.connect(cachePathEditor.setText)

        cachePathSelectButton = QtWidgets.QPushButton()
        cachePathSelectButton.setText("...")
        cachePathSelectButton.clicked.connect(self.on_select_button_clicked)

        layout.addWidget(cachePathLabel, rowIndex, 0)
        layout.addWidget(cachePathEditor, rowIndex, 1)
        layout.addWidget(cachePathSelectButton, rowIndex, 2)
        rowIndex += 1

        self.setLayout(layout)

    def isComplete(self):
        return self.__complete

    def __reset_complete(self):
        self.__complete = False
        self.completeChanged.emit()

    def on_cache_path_changed(self, cache_path_value):
        if not cache_path_value:
            self.__reset_complete()

        self.__params_handler.set_param(GavcClientParamsHandler.CACHE_PATH_PARAM, cache_path_value)
        self.__complete = True
        self.completeChanged.emit()

    def on_select_button_clicked(self):
        current_cache_path      = self.__params_handler.get_param(GavcClientParamsHandler.CACHE_PATH_PARAM)

        dialog = QtWidgets.QFileDialog(self)
        dialog.setFileMode(QtWidgets.QFileDialog.Directory)
        dialog.selectFile(current_cache_path)
        if dialog.exec():
            self.cachePathSelected.emit(dialog.selectedFiles()[0])

################################################################################
class ConnectionParamsPage(QtWidgets.QWizardPage):
    checkingComplete = QtCore.pyqtSignal(str)

    def __init__(self, params_handler):
        QtWidgets.QWizardPage.__init__(self)
        self.setTitle("Artifactory connection parameters")

        self.__complete         = False
        self.__params_handler   = params_handler

        current_server          = self.__params_handler.get_param(GavcClientBaseParamsHandler.SERVER_PARAM)
        current_repository      = self.__params_handler.get_param(GavcClientBaseParamsHandler.REPOSITORY_PARAM)
        current_token           = self.__params_handler.get_param(GavcClientBaseParamsHandler.TOKEN_PARAM)

        layout = QtWidgets.QGridLayout()
        rowIndex = 0

        #####
        serverLabel = QtWidgets.QLabel()
        serverLabel.setText("Server url")

        serverEditor = QtWidgets.QLineEdit()
        serverEditor.setText(current_server)
        serverEditor.textChanged.connect(self.on_server_changed)

        layout.addWidget(serverLabel, rowIndex, 0)
        layout.addWidget(serverEditor, rowIndex, 1)
        rowIndex += 1

        #####
        tokenLabel = QtWidgets.QLabel()
        tokenLabel.setText("API access token")

        tokenEditor = QtWidgets.QLineEdit()
        tokenEditor.setText(current_token)
        tokenEditor.textChanged.connect(self.on_token_changed)

        layout.addWidget(tokenLabel, rowIndex, 0)
        layout.addWidget(tokenEditor, rowIndex, 1)
        rowIndex += 1

        #####
        repoLabel = QtWidgets.QLabel()
        repoLabel.setText("Repository")

        repoEditor = QtWidgets.QLineEdit()
        repoEditor.setText(current_repository)
        repoEditor.textChanged.connect(self.on_repository_changed)

        layout.addWidget(repoLabel, rowIndex, 0)
        layout.addWidget(repoEditor, rowIndex, 1)
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

        self.setLayout(layout)

    def isComplete(self):
        return self.__complete

    def __reset_complete(self, text = "Not checked"):
        self.checkingComplete.emit(text)
        self.__complete = False
        self.completeChanged.emit()

    def on_token_changed(self, token_value):
        self.__params_handler.set_param(GavcClientBaseParamsHandler.TOKEN_PARAM, token_value)
        self.__reset_complete()

    def on_server_changed(self, server_value):
        self.__params_handler.set_param(GavcClientBaseParamsHandler.SERVER_PARAM, server_value)
        self.__reset_complete()

    def on_repository_changed(self, repository_value):
        self.__params_handler.set_param(GavcClientBaseParamsHandler.REPOSITORY_PARAM, repository_value)
        self.__reset_complete()

    def check_connection(self):
        current_repository  = self.__params_handler.get_param(GavcClientBaseParamsHandler.REPOSITORY_PARAM)
        client              = ArtifactoryClient.from_params_handler(self.__params_handler)
        try:
            r = client.requests().get_local_repos()
            repos_info = json.loads(r.text)
            repo_info = list(filter(lambda x: x['key'] == current_repository, repos_info))
            if len(repo_info) == 0:
                raise Exception("No requested repository '%s'!" % self.__repository)
            self.checkingComplete.emit("OK")
            self.__complete = True
            self.completeChanged.emit()

        except:
            self.__reset_complete("FAILED")

################################################################################
class SummaryPage(QtWidgets.QWizardPage):
    def __init__(self, params_handler):
        QtWidgets.QWizardPage.__init__(self)
        self.setTitle("Summary")

        self.__params_handler   = params_handler
        self.__values_labels    = {}

        self.__layout = QtWidgets.QGridLayout()
        self.setLayout(self.__layout)

    def initializePage(self):
        current_cache_path      = self.__params_handler.get_param(GavcClientParamsHandler.CACHE_PATH_PARAM)
        current_server          = self.__params_handler.get_param(GavcClientBaseParamsHandler.SERVER_PARAM)
        current_repository      = self.__params_handler.get_param(GavcClientBaseParamsHandler.REPOSITORY_PARAM)
        current_token           = self.__params_handler.get_param(GavcClientBaseParamsHandler.TOKEN_PARAM)

        rowIndex = 0

        self.__add_value_view(rowIndex, "Cache path", current_cache_path)
        rowIndex += 1

        self.__add_value_view(rowIndex, "Server url", current_server)
        rowIndex += 1

        self.__add_value_view(rowIndex, "API access token", current_token)
        rowIndex += 1

        self.__add_value_view(rowIndex, "Repository", current_repository)
        rowIndex += 1

    def __add_value_view(self, row, title, value):
        if title in self.__values_labels:
            self.__values_labels[title].setText(value)
            return

        titleLabel = QtWidgets.QLabel()
        titleLabel.setText(title)

        valueLabel = QtWidgets.QLabel()
        valueLabel.setText(value)

        self.__layout.addWidget(titleLabel, row, 0)
        self.__layout.addWidget(valueLabel, row, 1)

        self.__values_labels[title] = valueLabel

################################################################################
class Wizard(QtWidgets.QWizard):

    def __init__(self):
        QtWidgets.QWizard.__init__(self)
        self.setWindowTitle("PyGAVC parameters")

        self.__params_handler = GavcClientParamsHandler()

        self.addPage(CacheParamsPage(self.__params_handler))
        self.addPage(ConnectionParamsPage(self.__params_handler))
        self.addPage(SummaryPage(self.__params_handler))

        self.accepted.connect(self.on_accept)
        self.rejected.connect(self.on_cancel)
        self.finished.connect(self.on_finish)

    def on_accept(self):
        current_cache_path      = self.__params_handler.get_param(GavcClientParamsHandler.CACHE_PATH_PARAM)
        current_server          = self.__params_handler.get_param(GavcClientBaseParamsHandler.SERVER_PARAM)
        current_repository      = self.__params_handler.get_param(GavcClientBaseParamsHandler.REPOSITORY_PARAM)
        current_token           = self.__params_handler.get_param(GavcClientBaseParamsHandler.TOKEN_PARAM)

        config = UserConfig.load()
        config.set_value(GavcClientParamsHandler.CACHE_PATH_PARAM,      current_cache_path)
        config.set_value(GavcClientBaseParamsHandler.SERVER_PARAM,      current_server)
        config.set_value(GavcClientBaseParamsHandler.REPOSITORY_PARAM,  current_repository)
        config.set_value(GavcClientBaseParamsHandler.TOKEN_PARAM,       current_token)
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
