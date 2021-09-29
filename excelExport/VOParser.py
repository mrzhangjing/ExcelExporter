# -*- coding: utf-8 -*-
from Enum import ValueType, OutputType


class VOParser:
    def __init__(self, fileName, tableName):
        self.titleIndex = {}
        self.clientTitleIndex = {}
        self.fileName = fileName
        self.tableName = tableName
        self.values = {}
        self.enumList = {}

    def addTitle(self, index, key, desc, valueType, output):
        if index == None or index in self.titleIndex:
            return
        if key == None or key == '':
            return

        if valueType == None:
            return
        enumValueType = None
        for enumType in ValueType:
            if valueType == enumType.name or valueType == enumType.value:
                enumValueType = enumType
        if enumValueType == None:
            return

        if enumValueType is ValueType.KeyNumber or enumValueType is ValueType.KeyString:
            assert(index == 0)
        newKey = {'key': key, 'desc': desc,
                  'valueType': enumValueType, 'output': output}
        # print(newKey)
        self.titleIndex[index] = newKey
        if output == "All" or output == "Client":
            self.clientTitleIndex[index] = newKey

    def addValue(self, rowIndex, lineValues):
        # 第一例空表示废数据
        if lineValues[0] is None or lineValues[0] == '':
            return

        valueIndex = {}
        for index in self.titleIndex:
            valueIndex[index] = lineValues[index]
        self.values[rowIndex] = valueIndex

        for index in self.clientTitleIndex:
            title = self.clientTitleIndex[index]
            if title['valueType'] is ValueType.Enum:
                value = lineValues[index]
                if value != None and value != "":
                    self.enumList[value] = self.toInt(lineValues[0])

    def forEachLine(self, func):
        for lineIndex in self.values:
            lineValues = self.values[lineIndex]
            lineMap = self._parseLineValues(lineValues)
            if len(lineMap) > 0:
                func(lineMap)

    # 转成字典
    def _parseLineValues(self, lineValues):
        values = {}
        for index in self.titleIndex:
            title = self.titleIndex[index]

            value = None
            if index in lineValues and lineValues[index] != None:
                value = lineValues[index]

            value = self._parseValue(title['valueType'], value)

            if value != None:
                values[title['key']] = value
        return values

    def _parseValue(self, valueType, value):
        def parserNumber(value):
            if value == None or value == '':
                value = 0
            value = self.toInt(value)
            return value

        def parserArrays(value):
            if value == None or value == '':
                value = "[]"
            return value

        def parserString(value):
            if value == None:
                value = ''
            value = str(value)
            return value

        if valueType is ValueType.KeyNumber or valueType is ValueType.Number:
            value = parserNumber(value)
        if valueType is ValueType.NumberOrNull:
            if value == None or value == '':
                return None
            value = parserNumber(value)
        elif valueType is ValueType.NumberArrays:
            if value == None or value == '':
                return None
            value = parserArrays(value)
        elif valueType is ValueType.NumberMultiArrays:
            if value == None or value == '':
                return None
            value = parserArrays(value)
        elif valueType is ValueType.Enum:
            if value == None or value == '':
                return None
            value = parserString(value)
        elif valueType is ValueType.KeyString or valueType is ValueType.String:
            value = parserString(value)
        elif valueType is ValueType.StringOrNull:
            if value == None or value == '':
                return None
            value = parserString(value)
        elif valueType is ValueType.StringArrays:
            if value == None or value == '':
                return None
            value = parserArrays(value)
        return str(value)

    def toFloat(self, value):
        if value is None or value == '' or value == 'null':
            return 'null'
        try:
            float(value)
        except BaseException:
            print("---------------请检查错误---------------")
            print("value = %s" % value)
            print("toFloat：类型转换失败，这里应该填写数字")
            input("")
        value = float(value) * 100000 + 0.1
        if value > 0:
            value = int(value + 0.1) / 100000
        if value < 0:
            value = int(value - 0.1) / 100000
        return value

    def toInt(self, value):
        if value is None or value == '' or value == 'null':
            return 'null'
        try:
            float(value)
        except BaseException:
            print("---------------请检查错误---------------")
            print("value = %s" % value)
            print("toInt：类型转换失败，这里应该填写数字")
            input("")
        intValue = int(float(value))
        floatValue = self.toFloat(value)
        if intValue != floatValue:
            return floatValue
        return intValue
