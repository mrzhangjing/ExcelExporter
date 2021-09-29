# -*- coding: utf-8 -*-

from VOParser import VOParser

from Exporter.JsonExporter import JsonExporter
from Exporter.TsExporter import TsExporter
from Exporter.LuaExporter import LuaExporter


class SheetParser:
    def __init__(self, fileName, sheet, tableName):
        print("%s > %s" % (fileName, sheet.name))
        self._ExportList = []
        self._ExportList.append(LuaExporter(fileName, tableName))
        self._ExportList.append(TsExporter(fileName, tableName))
        self._ExportList.append(JsonExporter(fileName, tableName))

        self._parse(fileName, sheet, tableName)

    def _parse(self, fileName, sheet, tableName):
        nrows = sheet.nrows
        if nrows <= 4:
            print('表至少多于4行：' + sheet.name)
            return False

        # 解析表格字段
        voParser = VOParser(fileName, tableName)
        keyLine = sheet.row_values(1)
        for i, key in enumerate(keyLine):
            desc = sheet.row_values(0)[i]
            valueType = sheet.row_values(2)[i]
            output = sheet.row_values(3)[i]
            voParser.addTitle(i, key, desc, valueType, output)

        # 缓存表格数据
        for rowIndex in range(4, sheet.nrows):
            lineValues = sheet.row_values(rowIndex)
            voParser.addValue(rowIndex, lineValues)

        # print(voParser.titleIndex)
        # print(voParser.values)

        # 导出数据
        for parser in self._ExportList:
            parser.exportConfig(voParser)
