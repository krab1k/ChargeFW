import sys
import importlib
import subprocess

from charge_method import get_charge_methods

from PyQt5.QtWidgets import (QWidget, QApplication, QLabel, QVBoxLayout, QAction, QHBoxLayout,
                             QPushButton, QTextEdit, qApp, QComboBox, QStackedLayout, QGridLayout, QLineEdit,
                             QDesktopWidget, QFileDialog, QPlainTextEdit)

from PyQt5.QtGui import QIcon, QDoubleValidator, QPixmap
from PyQt5.QtCore import QTimer

from structures.molecule_set import MoleculeSet
from charges import Charges


class CalculateCharges(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def centerUI(self):
        frame = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        frame.moveCenter(center_point)
        self.move(frame.topLeft())

    def select_structures(self):
        fname = QFileDialog().getOpenFileName(self, 'Choose file with structures',
                                              '/home/krab1k/Research/NEEMP/examples', 'Structures (*.sdf)')
        if fname[0]:
            self.structures_edit.setText(fname[0])

    def select_output(self):
        fname = QFileDialog().getSaveFileName(self, 'Choose output file', '.')
        if fname[0]:
            self.output_edit.setText(fname[0])

    def change_method(self, i):
        self.properties.setCurrentIndex(i)

    def initUI(self):
        self.centerUI()
        vbox = QVBoxLayout()
        buttons_box = QHBoxLayout()
        grid = QGridLayout()
        self.properties = QStackedLayout()

        for method_name in get_charge_methods():
            method_properties = QWidget()
            method_grid = QGridLayout()
            method_properties.setLayout(method_grid)
            module = importlib.import_module('methods.' + method_name)
            method = module.ChargeMethod
            for i, option in enumerate(method.OPTIONS):
                name_label = QLabel(option.name)
                name_label.setToolTip(option.help)
                value_edit = QLineEdit(str(option.default))

                if option.type == 'float':
                    value_edit.setValidator(QDoubleValidator())
                method_grid.addWidget(name_label, i, 1)
                method_grid.addWidget(value_edit, i, 2)

            self.properties.addWidget(method_properties)

        self.setWindowTitle('Calculate charges')

        self.methods_combo = QComboBox(self)
        self.methods_combo.addItems(get_charge_methods())
        self.methods_combo.currentIndexChanged.connect(self.change_method)


        grid.addWidget(QLabel('Structures:'), 1, 1)
        self.structures_edit = QLineEdit()
        grid.addWidget(self.structures_edit, 1, 2)
        self.structures_button = QPushButton()
        self.structures_button.setIcon(QIcon('/usr/share/icons/breeze/actions/32/document-open.svg'))
        self.structures_button.clicked.connect(self.select_structures)
        grid.addWidget(self.structures_button, 1, 3)

        grid.addWidget(QLabel('Output:'), 2, 1)
        self.output_edit = QLineEdit()
        grid.addWidget(self.output_edit, 2, 2)
        self.output_button = QPushButton()
        self.output_button.setIcon(QIcon('/usr/share/icons/breeze/actions/32/document-open.svg'))
        self.output_button.clicked.connect(self.select_output)

        grid.addWidget(self.output_button, 2, 3)

        vbox.addLayout(grid)
        vbox.addWidget(self.methods_combo)
        vbox.addLayout(self.properties)
        vbox.addLayout(buttons_box)
        self.quit_button = QPushButton('&Quit')
        self.quit_button.setShortcut('Ctrl+Q')

        self.calculate_button = QPushButton('Calculate')
        buttons_box.addWidget(self.quit_button)
        self.quit_button.clicked.connect(qApp.quit)
        buttons_box.addWidget(self.calculate_button)
        self.calculate_button.clicked.connect(self.calculate_charges)
        self.setLayout(vbox)
        self.show()

    def calculate_charges(self):
        molecules = MoleculeSet.load_from_file(self.structures_edit.text())

        module = importlib.import_module('methods.' + get_charge_methods()[self.methods_combo.currentIndex()])
        method = module.ChargeMethod()
        method.initialize({})

        charges = Charges()
        for molecule in molecules:
            charges[molecule.name] = method.calculate_charges(molecule)

        charges.save_to_file(self.output_edit.text())

class MethodSource(QWidget):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.initUI()

    def initUI(self):

        close_action = QAction(self)
        close_action.setShortcut('Ctrl+W')
        close_action.triggered.connect(self.close)

        self.addAction(close_action)

        text_edit = QTextEdit(self)
        text_edit.setReadOnly(True)
        text_edit.resize(800, 600)
        self.resize(800, 600)

        with open(f'methods/{self.name}.py') as file:
            data = file.read()

        text_edit.setText(data)

        self.show()


class MethodList(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):

        quit_action = QAction(self)
        quit_action.setShortcut('Ctrl+Q')
        quit_action.triggered.connect(qApp.quit)

        self.addAction(quit_action)


        self.method_labels = []

        self.setWindowTitle('Charge calculation methods')
        self.move(400, 400)
        layout = QVBoxLayout()

        for method_name in get_charge_methods():

            module = importlib.import_module('methods.' + method_name)
            method = module.ChargeMethod
            label = QLabel(f'<b>{method.FULL_NAME:}</b>')
            common_parameters = ", ".join(method.COMMON_PARAMETERS) if method.COMMON_PARAMETERS else '<i>None</i>'
            atom_parameters = ", ".join(method.ATOM_PARAMETERS) if method.ATOM_PARAMETERS else '<i>None</i>'
            common_parameters_label = QLabel(f'Common parameters: {common_parameters}')
            atom_parameters_label = QLabel(f'Atom parameters: {atom_parameters}')

            self.method_labels.append(label)
            hbox = QHBoxLayout()
            vbox = QVBoxLayout()
            layout.addWidget(label)
            layout.addLayout(hbox)
            hbox.addLayout(vbox)
            hbox.addStretch(1)

            source_button = QPushButton('Source', self)
            source_button.custom_name = method.NAME
            source_button.clicked.connect(self.show_source)
            source_button.resize(source_button.sizeHint())
            hbox.addWidget(source_button)
            vbox.addWidget(common_parameters_label)
            vbox.addWidget(atom_parameters_label)

        self.setLayout(layout)
        self.show()


    def show_source(self):
        sender = self.sender()
        name = sender.custom_name

        self.method_source = MethodSource(name)



class RenderTeX(QWidget):
    def __init__(self):
        super().__init__()
        self.timer = QTimer()
        self.timer.start(1000)
        self.timer.timeout.connect(self.update_text)

        self.text = ''
        self.initUI()

    def initUI(self):
        hbox = QHBoxLayout()

        self.editor = QPlainTextEdit(self)
        self.image = QLabel()
        self.image.setFixedSize(600, 400)

        hbox.addWidget(self.editor)
        hbox.addWidget(self.image)

        self.setLayout(hbox)

        close_action = QAction(self)
        close_action.setShortcut('Ctrl+W')
        close_action.triggered.connect(self.close)
        self.addAction(close_action)

        self.show()


    def update_text(self):
        text = self.editor.toPlainText()
        if self.text == text:
            return

        self.text = text.replace('\n', '\\\\')

        template = \
f'''\
\\nonstopmode
\documentclass{{article}}
\\pagestyle{{empty}}
\\begin{{document}}
\\begin{{eqnarray*}}
{self.text}
\\end{{eqnarray*}}
\\end{{document}}
'''
        with open('/tmp/editor.tex', 'w') as file:
            file.write(template)

        res = subprocess.run('pdflatex /tmp/editor.tex'.split(), cwd='/tmp', stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        res = subprocess.run('pdfcrop /tmp/editor.pdf'.split(), cwd='/tmp', stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        res = subprocess.run('convert -density 200 editor-crop.pdf editor.png'.split(), cwd='/tmp')
        if res.returncode == 0:
            self.image.setPixmap(QPixmap('/tmp/editor.png'))


if __name__ == '__main__':


    app = QApplication(sys.argv)

    window = RenderTeX()

    sys.exit(app.exec_())