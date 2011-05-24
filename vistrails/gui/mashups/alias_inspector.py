############################################################################
##
## Copyright (C) 2006-2010 University of Utah. All rights reserved.
##
## This file is part of VisTrails.
##
## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following to ensure GNU General Public
## Licensing requirements will be met:
## http://www.opensource.org/licenses/gpl-license.php
##
## If you are unsure which license is appropriate for your use (for
## instance, you are interested in developing a commercial derivative
## of VisTrails), please contact us at vistrails@sci.utah.edu.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################

"""This file contains the widget for displaying the properties panel for a
selected alias in the list

Classes defined in this file:

QAliasInspector

"""

import copy
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import pyqtSignal, pyqtSlot
from core.mashup.alias import Alias
from core.modules.module_registry import get_module_registry
from core.modules.constant_configuration import StandardConstantWidget
from gui.theme import CurrentTheme
from gui.utils import show_warning
################################################################################
class QAliasInspector(QtGui.QScrollArea):
    """
    QAliasInspector is a widget to display the details of an alias.
    """
    #signals
    aliasChanged = pyqtSignal(Alias)
    
    def __init__(self, alias_list, parent=None):
        QtGui.QScrollArea.__init__(self,parent)
        self.setAcceptDrops(False)
        self.setWidgetResizable(True)
        self.vWidget = QAliasDetailsWidget(alias_list)
        self.setWidget(self.vWidget)
        self.vWidget.setVisible(False)
        
        #connecting signals
        self.vWidget.aliasChanged.connect(self.aliasChanged)
        
    def updateContents(self, alias_item=None, controller=None):
        self.vWidget.updateContents(alias_item, controller)
 
################################################################################       
class QAliasDetailsWidget(QtGui.QWidget):
    #signals
    aliasChanged = pyqtSignal(Alias)
    
    def __init__(self, table, parent=None):
        QtGui.QWidget.__init__(self,parent)
        self.alias = None
        self.table = table
        self.createWidgets()
        self.updateContents()
        
    def createWidgets(self):
        self.main_layout = QtGui.QVBoxLayout()
        self.label = QtGui.QLabel("Alias Details")
        self.main_layout.addWidget(self.label)
        
        self.name_label = QtGui.QLabel("Name")
        self.name_edit = QtGui.QLineEdit()
        l1 = QtGui.QVBoxLayout()
        l1.setContentsMargins(0, 11, 0, 0)
        l1.setSpacing(3)
        l1.addWidget(self.name_label)
        l1.addWidget(self.name_edit)
        
        self.order_label = QtGui.QLabel("Order")
        self.order_spinbox = QtGui.QSpinBox()
        self.order_spinbox.setRange(0,self.table.topLevelItemCount()-1)
        if self.alias:
            self.order_spinbox.setValue(self.alias.component.pos)
        l2 = QtGui.QVBoxLayout()
        l2.setContentsMargins(0, 11, 0, 0)
        l2.setSpacing(3)
        l2.addWidget(self.order_label)
        l2.addWidget(self.order_spinbox)
        
        l3 = QtGui.QHBoxLayout()
        l3.addLayout(l1)
        l3.addLayout(l2)
        self.main_layout.addLayout(l3)
        
        #Display Widget
        self.dw_groupbox = QtGui.QGroupBox()
        self.dw_groupbox.setFlat(True)
        self.dw_label = QtGui.QLabel("Display Widget")
        self.dw_combobox = QtGui.QComboBox()
        self.dw_combobox.addItem("combobox")
        self.dw_combobox.addItem("slider")
        self.dw_combobox.addItem("numericstepper")
        
        self.dw_layout = QtGui.QVBoxLayout()
        self.dw_layout.setContentsMargins(0, 11, 0, 0)
        self.dw_slider_layout = QtGui.QHBoxLayout()
        self.dw_minval_label = QtGui.QLabel("Min Val")
        self.dw_maxval_label = QtGui.QLabel("Max Val")
        self.dw_stepsize_label = QtGui.QLabel("Step Size")
        self.dw_minval_edit = QtGui.QLineEdit()
        self.dw_maxval_edit = QtGui.QLineEdit()
        self.dw_stepsize_edit = QtGui.QLineEdit()
        l = QtGui.QVBoxLayout()
        l.setMargin(0)
        l.setSpacing(0)
        l.addWidget(self.dw_minval_label)
        l.addWidget(self.dw_minval_edit)
        self.dw_slider_layout.addLayout(l)
        l = QtGui.QVBoxLayout()
        l.setMargin(0)
        l.setSpacing(0)
        l.addWidget(self.dw_maxval_label)
        l.addWidget(self.dw_maxval_edit)
        self.dw_slider_layout.addLayout(l)
        l = QtGui.QVBoxLayout()
        l.setMargin(0)
        l.setSpacing(0)
        l.addWidget(self.dw_stepsize_label)
        l.addWidget(self.dw_stepsize_edit)
        self.dw_slider_layout.addLayout(l)
        self.dw_layout.addWidget(self.dw_label)
        self.dw_layout.addWidget(self.dw_combobox)
        self.dw_layout.addLayout(self.dw_slider_layout)
        self.dw_groupbox.setLayout(self.dw_layout)
        self.toggle_dw_combobox(0)
        
        #Default Value
        self.dv_groupbox = QtGui.QGroupBox()
        self.dv_groupbox.setFlat(True)
        self.dv_label = QtGui.QLabel("Default Value")
        self.dv_layout = QtGui.QVBoxLayout()
        self.dv_layout.setContentsMargins(0, 11, 0, 0)
        self.dv_layout.addWidget(self.dv_label)
        self.dv_groupbox.setLayout(self.dv_layout)
        self.dv_widget = None
        
        #Values List
        self.vl_groupbox = QtGui.QGroupBox()
        self.vl_groupbox.setFlat(True)
        self.vl_label = QtGui.QLabel("Values List")
        self.vl_layout = QtGui.QVBoxLayout()
        self.vl_layout.setContentsMargins(0, 11, 0, 0)
        self.vl_layout.addWidget(self.vl_label)
        self.vl_editor = None
        self.vl_groupbox.setLayout(self.vl_layout)
        
        self.main_layout.addWidget(self.dw_groupbox)
        self.main_layout.addWidget(self.dv_groupbox)
        self.main_layout.addWidget(self.vl_groupbox)
        self.main_layout.addStretch(1)
        
        self.deleteButton = QtGui.QPushButton("Delete Alias")
        self.deleteButton.clicked.connect(self.table.removeCurrentAlias)
        self.deleteButton.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed,
                                                           QtGui.QSizePolicy.Fixed))
        self.main_layout.addWidget(self.deleteButton)
        
        self.setLayout(self.main_layout)
        
        #connect signals
        self.dw_combobox.currentIndexChanged.connect(self.toggle_dw_combobox)
        
#        self.connect(self.dw_combobox, QtCore.SIGNAL("currentIndexChanged(int)"),
#                     self.toggle_dw_combobox)
        self.connect(self.name_edit, QtCore.SIGNAL("editingFinished()"),
                     self.nameChanged)
        self.connect(self.order_spinbox, QtCore.SIGNAL("valueChanged(int)"),
                     self.orderChanged)
        self.connect(self.dw_minval_edit, QtCore.SIGNAL("editingFinished()"),
                     self.minvalChanged)
        self.connect(self.dw_stepsize_edit, QtCore.SIGNAL("editingFinished()"),
                     self.stepsizeChanged)
        self.connect(self.dw_maxval_edit, QtCore.SIGNAL("editingFinished()"),
                     self.maxvalChanged)
        
    def valuesListChanged(self):
        self.aliasChanged.emit(self.alias)
        
    def minvalChanged(self):
        if self.alias:
            old_minval = self.alias.component.minVal
            new_minval = str(self.dw_minval_edit.text())
            if old_minval == new_minval:
                return
            self.alias.component.minVal = new_minval
            self.aliasChanged.emit(self.alias)

    def maxvalChanged(self):
        if self.alias:
            old_maxval = self.alias.component.maxVal
            new_maxval = str(self.dw_maxval_edit.text())
            if old_maxval == new_maxval:
                return
            self.alias.component.maxVal = new_maxval
            self.aliasChanged.emit(self.alias)
        
    def stepsizeChanged(self):
        if self.alias:
            old_stepsize = self.alias.component.stepSize
            new_stepsize = str(self.dw_stepsize_edit.text())
            if old_stepsize == new_stepsize:
                return
            self.alias.component.stepSize = new_stepsize
            self.aliasChanged.emit(self.alias)
        
    def nameChanged(self):
        old_alias = self.alias.name
        new_alias = str(self.name_edit.text())
        if old_alias == new_alias:
            return
        if new_alias in self.table.aliases.keys():
            show_warning("Mashup",
                         """Label name %s already exists. 
Please type a different name. """ % new_alias)
            self.name_edit.setText(old_alias)
            self.name_edit.setFocus()
        elif new_alias == '':
            show_warning("Mashup",
                         """Variables with empty name are not allowed. 
Please type a unique name. """ % new_alias)
            self.name_edit.setText(old_alias)
            self.name_edit.setFocus()
        else:
            self.table.aliases[new_alias] = self.table.aliases[old_alias]
            #self.table.alias_cache[new_alias] = self.table.alias_cache[old_alias]
            del self.table.aliases[old_alias]
            #del self.table.alias_cache[old_alias]
            self.alias.name = new_alias
            self.aliasChanged.emit(self.alias)
            
    def orderChanged(self, neworder):
        if self.alias.component.pos == neworder:
            return
        oldorder = self.alias.component.pos
        self.alias.component.pos = neworder
        self.table.moveItemToNewPos(oldorder, neworder)
        
    @pyqtSlot(int)
    def toggle_dw_combobox(self, index):
        if index == 0:
            self.dw_minval_label.setVisible(False)
            self.dw_minval_edit.setVisible(False)
            self.dw_maxval_label.setVisible(False)
            self.dw_maxval_edit.setVisible(False)
            self.dw_stepsize_label.setVisible(False)
            self.dw_stepsize_edit.setVisible(False)
        elif index in [1,2]:
            self.dw_minval_label.setVisible(True)
            self.dw_minval_edit.setVisible(True)
            self.dw_maxval_label.setVisible(True)
            self.dw_maxval_edit.setVisible(True)
            self.dw_stepsize_label.setVisible(True)
            self.dw_stepsize_edit.setVisible(True)
        if self.alias:
            self.alias.component.widget = str(self.dw_combobox.currentText())
            self.aliasChanged.emit(self.alias)
            
    def updateContents(self, alias=None, controller=None):
        self.alias = alias
        self.controller = controller
        if alias is not None and controller is not None:
            self.name_edit.setText(self.alias.name)
            print "widget:", self.alias.component.widget
            self.dw_combobox.setCurrentIndex(self.dw_combobox.findText(QtCore.QString(self.alias.component.widget)))
            self.order_spinbox.setRange(0,self.table.topLevelItemCount()-1)
            self.order_spinbox.setValue(self.alias.component.pos)
        
            self.dw_minval_edit.setText(self.alias.component.minVal)
            self.dw_maxval_edit.setText(self.alias.component.maxVal)
            self.dw_stepsize_edit.setText(self.alias.component.stepSize)
            
            if self.dv_widget:
                self.dv_layout.removeWidget(self.dv_widget)
                self.disconnect(self.dv_widget,
                                QtCore.SIGNAL("contentsChanged"),
                                self.widgetContentsChanged)
                self.dv_widget.deleteLater()
            
            self.dv_widget = QAliasDetailsWidget.createAliasWidget(self.alias, self.controller, None)
            self.dv_layout.addWidget(self.dv_widget)
            self.connect(self.dv_widget,
                         QtCore.SIGNAL("contentsChanged"),
                         self.widgetContentsChanged)
        
            if self.vl_editor:
                self.vl_layout.removeWidget(self.vl_editor)
                self.disconnect(self.vl_editor,
                                QtCore.SIGNAL("valuesChanged"),
                                self.valuesListChanged)
                self.vl_editor.deleteLater()
           
            self.vl_editor = QValuesListEditor(self.alias,self.controller)
            self.vl_layout.addWidget(self.vl_editor)
        
            #capturing widget changes to update alias
            self.connect(self.vl_editor,
                         QtCore.SIGNAL("valuesChanged"),
                         self.valuesListChanged)
            self.setEnabled(True)
        else:
            self.name_edit.setText("")
            
            if self.dv_widget:
                self.dv_layout.removeWidget(self.dv_widget)
                self.disconnect(self.dv_widget,
                                QtCore.SIGNAL("contentsChanged"),
                                self.widgetContentsChanged)
                self.dv_widget.deleteLater()
                
            if self.vl_editor:
                self.vl_layout.removeWidget(self.vl_editor)
                self.disconnect(self.vl_editor,
                                QtCore.SIGNAL("valuesChanged"),
                                self.valuesListChanged)
                self.vl_editor.deleteLater()
            self.setEnabled(False)
            
    @staticmethod
    def createAliasWidget(alias, controller, parent=None):
        v = controller.vtController.vistrail
        p = v.db_get_object(alias.component.vttype, alias.component.vtid)
        if p.identifier == '':
            idn = 'edu.utah.sci.vistrails.basic'
        else:
            idn = p.identifier
        reg = get_module_registry()
        p_module = reg.get_module_by_name(idn, p.type, p.namespace)
        if p_module is not None:
            widget_type = p_module.get_widget_class()
        else:
            widget_type = StandardConstantWidget
        p.strValue = alias.component.val
        return widget_type(p, parent)
    
    def widgetContentsChanged(self, info):
        self.alias.component.val = info[0].contents()
        if self.alias.component.val not in self.alias.component.valueList:
            self.alias.component.valueList.append(self.alias.component.val)
            self.alias.component.valueList.sort()
            self.vl_editor.alias_item_updated()
        self.aliasChanged.emit(self.alias)
        
################################################################################

class QValuesListEditor(QtGui.QWidget):
    """
    QValuesListEditor is the actual widget allowing users to
    enter a list of values
    
    """
    def __init__(self, alias, controller, parent=None):
        """ QValuesListEditor(alias_item: AliasTableItem, parent: QWidget)
                                     -> QValuesListEditor
        Construct an edit box with a button for bringing up the dialog
        
        """
        QtGui.QWidget.__init__(self, parent)
        self._alias = alias
        self.type = alias.component.type
        self.controller = controller
        
        hLayout = QtGui.QHBoxLayout(self)
        hLayout.setMargin(0)
        hLayout.setSpacing(0)
        self.setLayout(hLayout)
        
        self.listValues = QtGui.QLineEdit()
    
        self.listValues.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                      QtGui.QSizePolicy.Maximum)
        self.alias_item_updated()
        
        hLayout.addWidget(self.listValues)
        
        self.connect(self.listValues, QtCore.SIGNAL('textEdited(QString)'),
                     self.values_were_edited)

        inputButton = QtGui.QToolButton()
        inputButton.setText('...')
        self.connect(inputButton, QtCore.SIGNAL('clicked()'),
                     self.editListValues)
        hLayout.addWidget(inputButton)
        
    def alias_item_updated(self):
        if self._alias.component.type not in ['Float', 'Integer']:
            values = []
            for v in self._alias.component.valueList:
                values.append("'%s'"% v.replace("'", "\'"))
                
            self.listValues.setText("[%s]" % ", ".join(values))
        else:
            self.listValues.setText('[%s]' % ", ".join(self._alias.component.valueList))
        if self._alias.component.type in ['String','Integer','Float']:
            self.listValues.setReadOnly(False)
        else:
            self.listValues.setReadOnly(True)
        self.listValues.home(False)
        
    def values_were_edited(self, new_text):
        """values_were_edited(new_text): None

        Connected to self.listValues.textEdited. 
        Updates self._alias.valueList.
        
        NB: Allowing the user to edit the LineEdit field directly is
        not a very good idea, because we don't know what are the
        syntactic rules for the translate_to_python() calls in
        arbitrary classes.  Right now, I'm assuming removing the
        leading and trailing brackets and splitting on ',' is
        enough. (in passing, The previous call to eval() is just
        broken is a general scenario like we have now)

        For example, this will break horribly if the user manually edits
        a list of strings with commas in them."""

        print "values_were_edited"
        t = str(new_text)
        if len(t) < 2:
            self._alias.component.valueList = []
            return
        if not (t[0] == '[' and t[-1] == ']'):
            self._alias.valueList = []
        else: 
            self._alias.component.valueList = t[1:-1].split(',')
            if self._alias.component.type not in ['Float', 'Integer']:
                for i, val in enumerate(self._alias.component.valueList):
                    val = val.strip()
                    if len(val) >= 2 and  \
                            ((val[0] == "'" and val[-1] == "'") or 
                             (val[0] == '"' and val[-1] == '"')):
                        self._alias.component.valueList[i] = val.strip()[1:-1]

    def editListValues(self):
        """ editListValues() -> None
        Show a dialog for editing the values
        
        """
        dialog = QListEditDialog(self._alias, self.controller, None)
        if dialog.exec_() == QtGui.QDialog.Accepted:
            values = dialog.getList()
            print values
            self._alias.component.valueList = copy.copy(values)
            self._str_values = [str(v) for v in values]
            values2 = values
            if self.type not in ['Float', 'Integer']:
                values2 = ["'%s'" % v.replace("'", "\'")
                          for v in values]
            self.listValues.setText('[%s]' % ', '.join(values2))
            self.listValues.home(False)
            self.emit(QtCore.SIGNAL("valuesChanged"))
        dialog.deleteLater()

##############################################################################

class QListEditDialog(QtGui.QDialog):
    """
    QListEditDialog provides an interface for user to edit a list of
    values and export to a string
    
    """
    def __init__(self, alias, controller, parent=None):
        """ QListEditDialog(pType: str, strValues: list, parent: QWidget)
                            -> QListEditDialog
        Parse values and setup the table
        
        """
        QtGui.QDialog.__init__(self, parent)
        self._alias = alias
        vLayout = QtGui.QVBoxLayout()
        vLayout.setMargin(0)
        vLayout.setSpacing(0)
        self.controller = controller
        self.setLayout(vLayout)
        
        label = QtGui.QLabel("Please enter values in boxes below. "
                             "'Add' appends an empty value to the list. "
                             "And 'Del' removes the selected values.")
        label.setMargin(5)
        label.setWordWrap(True)
        vLayout.addWidget(label)

        self.table = QtGui.QTableWidget(0, 1, parent)
        self.table.setHorizontalHeaderLabels(QtCore.QStringList('Values'))
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setMovable(True)
        
        self.delegate = QListEditItemDelegate(alias, controller)
        self.table.setItemDelegate(self.delegate)
        self.table.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        for v in alias.component.valueList:
            self.addRow(v)
        self.connect(self.table.verticalHeader(),
                     QtCore.SIGNAL('sectionMoved(int,int,int)'),
                     self.rowMoved)
        
        vLayout.addWidget(self.table)

        hLayout = QtGui.QHBoxLayout()        
        vLayout.addLayout(hLayout)

        okButton = QtGui.QPushButton('&OK')
        okButton.setSizePolicy(QtGui.QSizePolicy.Maximum,
                               QtGui.QSizePolicy.Maximum)
        self.connect(okButton, QtCore.SIGNAL('clicked()'), self.okButtonPressed)
        hLayout.addWidget(okButton)

        cancelButton = QtGui.QPushButton('&Cancel')
        cancelButton.setSizePolicy(QtGui.QSizePolicy.Maximum,
                                   QtGui.QSizePolicy.Maximum)
        self.connect(cancelButton, QtCore.SIGNAL('clicked()'), self.reject)
        hLayout.addWidget(cancelButton)

        addButton = QtGui.QPushButton('&Add')
        addButton.setIcon(CurrentTheme.ADD_STRING_ICON)
        addButton.setSizePolicy(QtGui.QSizePolicy.Maximum,
                                QtGui.QSizePolicy.Maximum)
        self.connect(addButton, QtCore.SIGNAL('clicked()'), self.addRow)
        hLayout.addWidget(addButton)
        
        removeButton = QtGui.QPushButton('&Del')
        removeButton.setIcon(QtGui.QIcon(
            self.style().standardPixmap(QtGui.QStyle.SP_DialogCancelButton)))
        removeButton.setSizePolicy(QtGui.QSizePolicy.Maximum,
                                   QtGui.QSizePolicy.Maximum)
        self.connect(removeButton, QtCore.SIGNAL('clicked()'),
                     self.removeSelection)
        hLayout.addWidget(removeButton)
        
    def sizeHint(self):
        """ sizeHint() -> QSize
        Return the recommended size for the widget
        
        """
        return QtCore.QSize(256, 384)
        
    def okButtonPressed(self):
        """ okButtonPressed() -> None
        Make sure to commit the editor data before accepting
        
        """
        self.table.itemDelegate().finishEditing()
        self.accept()

    def getList(self):
        """ getList() -> list of str values
        Return a list of values
        
        """
        result = []
        for i in xrange(self.table.rowCount()):
            logicalIndex = self.table.verticalHeader().logicalIndex(i)
            value = self.table.cellWidget(logicalIndex, 0).contents()            
            result.append(str(value))
        return result

    def rowMoved(self, row, old, new):
        """ rowMove(row: int, old: int, new: int) -> None
        Renumber the vertical header labels when row moved
        
        """
        vHeader = self.table.verticalHeader()
        labels = QtCore.QStringList()        
        for i in xrange(self.table.rowCount()):
            labels << str(vHeader.visualIndex(i)+1)
        self.table.setVerticalHeaderLabels(labels)

    def addRow(self, text=''):
        """ addRow(text: str) -> QListStringEdit
        Add an extra row to the end of the table
        
        """    
        self.table.setRowCount(self.table.rowCount()+1)
        alias = copy.copy(self._alias)
        alias.component.val = text
        widget = \
          QAliasDetailsWidget.createAliasWidget(alias, self.controller, None)
        if type(widget) != StandardConstantWidget:
            item = QtGui.QTableWidgetItem()
        else:
            item = QtGui.QTableWidgetItem(text)
        row = self.table.rowCount()-1
        
        self.table.setItem(row, 0, item)
        self.table.setCellWidget(row,
                                 0,
                                 widget)
        h = widget.sizeHint().height()
        self.table.setRowHeight(row,h)
        
    def removeSelection(self):
        """ removeSelection() -> None
        Remove selected rows on the table
        
        """
        for item in self.table.selectedItems():
            self.table.removeRow(item.row())

##############################################################################

class QListEditItemDelegate(QtGui.QItemDelegate):
    """
    QListEditItemDelegate sets up the editor for the QListEditDialog
    table
    
    """

    def __init__(self, alias_item, controller, parent=None):
        """ QListEditItemDelegate(parent: QWidget) -> QListEditItemDelegate
        Store the uncommit editor for commit later
        
        """
        QtGui.QItemDelegate.__init__(self, parent)
        self.controller = controller
        self.alias_item = alias_item
        self.editor = None
        
    def createEditor(self, parent, option, index):
        """ createEditor(parent: QWidget,
                         option: QStyleOptionViewItem,
                         index: QModelIndex) -> QStringEdit
        Return the editor widget for the index
        
        """        
        self.editor = QAliasDetailsWidget.createAliasWidget(self.alias_item, 
                                                            self.controller, 
                                                            parent)
        print "editor created"
        return self.editor

    def updateEditorGeometry(self, editor, option, index):
        """ updateEditorGeometry(editor: QStringEdit,
                                 option: QStyleOptionViewItem,
                                 index: QModelIndex) -> None
        Update the geometry of the editor based on the style option
        
        """
        editor.setGeometry(option.rect)

    def setModelData(self, editor, model, index):
        """ setModelData(editor: QStringEdit,
                         model: QAbstractItemModel,
                         index: QModelIndex) -> None
        Set the text of the editor back to the item model
        
        """
        model.setData(index, QtCore.QVariant(editor.contents()))        
        self.editor = None

    def finishEditing(self):
        print "finishEditing"
        if self.editor:
            self.emit(QtCore.SIGNAL('commitData(QWidget*)'), self.editor)

##############################################################################