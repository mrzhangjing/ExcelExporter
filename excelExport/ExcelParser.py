# -*- coding: utf-8 -*-
import xlrd
import re

from SheetParser import SheetParser


def getTableName(sheetName):
    mm = re.findall("(\(.*?\))", sheetName)
    if(len(mm) > 0):
        mm = mm[0]
        mm = mm.replace('[', '').replace(']', '')
        mm = mm.replace('(', '').replace(')', '')
        return mm
    else:
        return


class ExcelParser:
    def __init__(self, filePath):
        self.fileName = filePath
        self.sheetList = []
        self._load(filePath)

    def _load(self, filePath):
        workbook = xlrd.open_workbook(filePath)
        if not workbook:
            print('配置表不存在:' + filePath)
            return

        for sheet in workbook.sheets():
            tableName = getTableName(sheet.name)
            if not tableName:
                continue
            sheetParser = SheetParser(self.fileName, sheet, tableName)
            self.sheetList.append(sheetParser)
