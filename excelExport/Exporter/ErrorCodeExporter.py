# -*- coding: utf-8 -*-
import json
from Enum import ValueType, OutputType
from Exporter.Exporter import Exporter


class ErrorCodeExporter(Exporter):
    def __init__(self, fileName="", tableName=""):
        # print('TsParser')
        Exporter.__init__(self, fileName, tableName)
        self.path = self.config.get('ErrorCode', 'path')
        self.errorCodeJson = self.config.get('ErrorCode', 'json_path')

    def exportOther(self):
        # 生成 ErrorCode
        LuaErrorCodeTmp = self.readTemplet("errorcode.lua.tmp")
        TsErrorCodeTmp = self.readTemplet("ErrorCode.ts.tmp")

        ModuleList = []
        LuaModuleIndex = {}
        TsModuleIndex = {}
        ErrorList = ""
        with open(self.errorCodeJson, 'rb') as load_f:
            load_dict = json.load(load_f)
            load_dict.pop(0)
            for info in load_dict:
                if info[1] not in LuaModuleIndex:
                    LuaModuleIndex[info[1]] = info[1]+" = {\n"
                    TsModuleIndex[info[1]] = "export const "+info[1]+" = {\n"
                    ModuleList.append(info[1])
                LuaModuleIndex[info[1]] = LuaModuleIndex[info[1]] + "    " + \
                    info[2]+" = add {code = "+info[0] + \
                    ", message = \""+info[3]+"\"},\n"
                TsModuleIndex[info[1]] = TsModuleIndex[info[1]] + \
                    "    "+info[2]+": "+info[0]+", // "+info[3]+"\n"
                ErrorList = ErrorList + "    "+info[0]+": \""+info[3]+"\",\n"

        for module in ModuleList:
            LuaErrorCodeTmp = LuaErrorCodeTmp.replace(
                "%ModuleError%", LuaModuleIndex[module]+"}\n\n%ModuleError%")
            TsErrorCodeTmp = TsErrorCodeTmp.replace(
                "%ModuleError%", TsModuleIndex[module]+"}\n\n%ModuleError%")

        LuaErrorCodeTmp = LuaErrorCodeTmp.replace("\n\n%ModuleError%", "")
        TsErrorCodeTmp = TsErrorCodeTmp.replace("%ErrorList%", ErrorList)
        TsErrorCodeTmp = TsErrorCodeTmp.replace("\n\n%ModuleError%", "")
        # print(TsErrorCode)
        self.writeFile(self.path, 'errorcode.lua', LuaErrorCodeTmp)
        print("生成：> errorcode.lua")

        self.writeFile(self.path, 'ErrorCode.ts', TsErrorCodeTmp)
        print("生成：> ErrorCode.ts")
