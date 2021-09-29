# -*- coding: utf-8 -*-
from Enum import ValueType, OutputType
from Exporter.Exporter import Exporter


class JsonExporter(Exporter):
    def __init__(self, fileName, tableName):
        # print('JsonParser')
        Exporter.__init__(self, fileName, tableName)
        self.server_path = self.config.get('Json', 'server_path')
        self.client_path = self.config.get('Json', 'client_path')

    def exportConfig(self, VOParser):
        self._exportJsonConfig(VOParser)

    def _exportJsonConfig(self, VOParser):
        lineStrList = []

        def func(lineValues):
            lineStr = "    ["
            for i in VOParser.clientTitleIndex:
                title = VOParser.clientTitleIndex[i]
                key = title["key"]
                value = None
                if key in lineValues:
                    if key not in lineValues:
                        continue
                    value = lineValues[key]

                if value == None:
                    value = "null"
                else:
                    if title['valueType'] is ValueType.KeyString or title['valueType'] is ValueType.Enum or title['valueType'] is ValueType.String or title['valueType'] is ValueType.StringOrNull:
                        value = value.replace("\"", "\\\"")
                        value = '\"' + value + '\"'
                    if title['valueType'] is ValueType.StringArrays:
                        value = value.replace('[', '[\"')
                        value = value.replace(',', '\",\"')
                        value = value.replace(']', '\"]')

                lineStr = lineStr + value + ", "

            lineStr = lineStr + "],\n"
            lineStrList.append(lineStr)

        VOParser.forEachLine(func)

        if len(lineStrList) == 0:
            return

        JsonData = '[\n'

        JsonData = JsonData + "    [\"" + self.fileName + "\", "
        for i in VOParser.clientTitleIndex:
            JsonData = JsonData + "\"" + VOParser.clientTitleIndex[i]['key'] + \
                "(" + VOParser.clientTitleIndex[i]['desc'] + ')\", '
        JsonData = JsonData + '],\n'

        for lineStr in lineStrList:
            JsonData = JsonData + lineStr
        JsonData = JsonData.replace(", ],\n", "],\n")
        JsonData = JsonData + ']'

        JsonData = JsonData.replace('],\n]', "]\n]")
        # print(JsonData)

        # self.writeFile(self.server_path, self.tableName + '.json', JsonData)
        self.writeFile(self.client_path, self.tableName + '.json', JsonData)
