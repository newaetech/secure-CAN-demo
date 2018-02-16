import sys
from PySide import QtGui, QtCore
from can_thread import can_thread
import can_thread as mycan
import secure_can as seccan

class test_can_gui(QtGui.QWidget):
	def __init__(self):
		super(test_can_gui, self).__init__()
		self.can = can_thread(self.rxcallback)
		self.seccan = seccan.secure_can()
		
		self.num_rows = 1
		self.is_connected = False
		self.max_rows = 20
		
		self.initUI()

	#called when we receive a CAN packet
	def rxcallback(self, addr, data):
		id_parts = self.seccan.get_id_cnt(addr)
		decrypt_data = self.seccan.decrypt(data, id_parts[0], id_parts[1])
		
		def arr2uint(arr, len):
			rtn = 0
			for i in range(0,len):
				rtn |= (arr[i] & 0xFF ) << (8 * i)
			return rtn;
		
		pedal = ((decrypt_data[0][1] << 8) | decrypt_data[0][0]) / 40.95
		data_str = ""
		for i in data:
			data_str += " 0x{:02X} ".format(i)
			
		row_str = ["0x{:04X}".format(id_parts[0]), "0x{:05X}".format(id_parts[1]),
		"0x{:08X}".format(arr2uint(decrypt_data[0], 4)), "{:3.2f}%".format(pedal), 
		"Passed" if decrypt_data[1] else "Failed", data_str]
			
		def update_table(row):
			for i,str in enumerate(row_str):
				item = self._table.item(row, i)
				if item:
					item.setText(str)
				else: 
					self._table.setItem(row, i, QtGui.QTableWidgetItem(str))
				

		#move rows up, from start to end, wraps around
		def move_rows(start, end):
			endcpy = []
			for columns in range(self._table.columnCount()):
				endcpy.append(self._table.takeItem(end, columns))
				for rows in range(end, start):
					self._table.setItem(rows, columns, self._table.takeItem(rows + 1, columns))
				self._table.setItem(start, columns, endcpy[columns])
			
		if (id_parts[0] == 0x200):
			update_table(0)
		elif self.num_rows < self.max_rows:
			update_table(self.num_rows)
			self.num_rows += 1
		else:
			move_rows(self.num_rows - 1, 1)
			update_table(self.num_rows - 1)
			
	def closeEvent(self, event):
		self.can.disconnect()
		self.can.quit()
		event.accept()
	
	def connected(self):
		if self.can.connect():
			self.is_connected = True
			self.setWindowTitle('Can Viewer - Connected')
		print 'Connected'
		
	def disconnect(self):
		self.can.disconnect()
		self.is_connected = False
		print 'Disconnected'
		
		self.setWindowTitle('Can Viewer - Disconnected')
		
	def initTable(self):
		headers = ["msg id", "msg #", "dec data", "throttle", "auth", "raw"]
	
		table = QtGui.QTableWidget()
		table.setColumnCount(len(headers))
		table.setHorizontalHeaderLabels(headers)
		table.resizeColumnsToContents()
		table.setRowCount(self.max_rows)
		table.resizeColumnsToContents()
		
		#stretch all but raw
		table.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
		table.horizontalHeader().setResizeMode(len(headers) - 1, QtGui.QHeaderView.ResizeToContents)
		
		table.verticalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
		return table
		
	def initUI(self):
		
		hlayout = QtGui.QHBoxLayout()
		vlayout = QtGui.QVBoxLayout()
		
		self._table = self.initTable()
		
		connect = QtGui.QPushButton('Connect')
		connect.setToolTip('Connects to can bus')
		connect.resize(connect.sizeHint())
		connect.clicked.connect(self.connected)
		
		disconnect = QtGui.QPushButton('Disconnect')
		disconnect.setToolTip('Disconnects from can bus')
		disconnect.resize(disconnect.sizeHint())
		disconnect.clicked.connect(self.disconnect)
		
		hlayout.addWidget(connect)
		hlayout.addWidget(disconnect)
		
		vlayout.addWidget(self._table)
		vlayout.addLayout(hlayout)
		self.setLayout(vlayout)
		
		self.setGeometry(300, 300, 500, 400)
		self.setWindowTitle('Can Viewer - Disconnected')
		self.can.start()
		self.show()
		
def main():
	app = QtGui.QApplication(sys.argv)
	app.setFont("Courier")
	ex = test_can_gui()
	sys.exit(app.exec_())
	
if __name__ == '__main__':
	main()
