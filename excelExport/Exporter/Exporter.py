# -*- coding: utf-8 -*-
import io
import os
import configparser


class Exporter:
    def __init__(self, fileName, tableName):
        self.fileName = fileName
        self.tableName = tableName
        root_dir = os.path.dirname(os.path.abspath('.'))
        self.config = configparser.ConfigParser()
        self.config.read(root_dir + '/excelExport/config.ini')

    # 导出配置
    def exportConfig(self, VOParser):
        return

    # 定制化导出（导出配置表后调用，子类重写）
    def exportOther(self):
        return

    def writeFile(self, path, fileName, str):
        if not os.path.exists(path):
            os.makedirs(path)
        filePath = path + '/' + fileName
        fd = io.open(filePath, 'w', encoding='utf-8')
        fd.write(str)
        fd.close()

    def readTemplet(self, templetFile):
        fd = io.open("./Exporter/templet/"+templetFile, 'r', encoding='utf-8')
        fileStr = fd.read()
        fd.close()
        return fileStr
