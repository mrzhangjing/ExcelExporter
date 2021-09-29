# -*- coding: utf-8 -*-
from Enum import ValueType, OutputType


class LineParser:
    def __init__(self):
        self.keys = {}
        self.keyMap = {}

    def addKey(self, index, key, desc, valueType, output):
        if index == None or index in self.keys:
            return
        if key == None or key == '' or key in self.keyMap:
            return
        if valueType == None or valueType not in ValueType.__members__:
            return

        for enumType in ValueType:
            if valueType == enumType.name:
                valueType = enumType

        if valueType is ValueType.KeyNumber or valueType is ValueType.KeyString:
            assert(index == 0)
        newKey = {'key': key, 'desc': desc,
                  'valueType': valueType, 'output': output}
        print(newKey)
        self.keys[index] = newKey
        self.keyMap[key] = True

    def parse(lineValues):
        return {}

    def toFloat(self, value):
        if value is None or value == '' or value == 'null':
            return null
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
