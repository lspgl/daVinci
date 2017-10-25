import platform
import time

if __name__ == "__main__":
    import sys
    sys.path.append('../..')
    # sys.path.append("..")
    print("import classes in 'class testmode'")

import helper.helper_functions as hf

OS = platform.system()
if OS == 'Windows':
    import visa


class class_IR_Camera(object):
    """description of class"""

    def __init__(self):
        self.camera = None
        self.address = None
        self.rm = visa.ResourceManager()
        self.lastexception = None

    def CommandIsKnow(self, CommandReturn):
        return "Unknown Command:" not in str(CommandReturn)

    def ErrorCodeToText(self, iErrorCode):
        if iErrorCode == -1:
            return self.lastexception
        elif iErrorCode == -2:
            return "command unknown"
        elif iErrorCode == -4:
            return "wrong temp area"
        elif iErrorCode == -3:
            return "camara port not available"
        elif iErrorCode == -5:
            return "no temerpature red"
        elif iErrorCode == -6:
            return "no windows = no camera"
        else:
            return "unknown error"

    ##########################################################################
    # initialised?
    ##########################################################################
    def is_initialised(self):
        if self.address:
            return True
        else:
            return False

    ##########################################################################
    # init methode for user
    ##########################################################################
    def init(self, addr):
        try:
            self.address = addr
            if OS != 'Windows':
                return [-6, 0]
                # print "no windows = no camera"
            else:
                # print self.address
                # print self.rm.list_resources()
                if self.address in self.rm.list_resources():
                    self.camera = self.rm.open_resource(self.address)
                    self.camera.read_termination = '\r'
                    self.camera.write_termination = '\r'
                    #self.camera.write_termination = ''
                    self.camera.timeout = 1  # Seconds
                    self.camera.encoding = 'cp1250'
                    print("Optris initialised")
                else:
                    self.address = None
                    return [-5, 0]
        except Exception as e:
            self.address = None
            self.lastexception = e
            return [-1, 0]

    def close(self):
        try:
            self.camera.close()
            return [0, 0]
        except Exception as e:
            self.lastexception = e
            return [-1, 0]

    def query(self, s):
        try:
            result = self.camera.query(s)
            return [0, result]
        except Exception as e:
            self.lastexception = e
            return [-1, 0]

    def read_t_main_area(self):
        self.camera.clear()
        try:
            result = self.query("?T")
            # print result
            # print self.CommandIsKnow(result)
            if result[0] < 0:
                #print("result < 0")
                return result[0, 0]
            elif self.CommandIsKnow(result):
                resulting_temp = hf.extract_nbr_from_string(result[1].encode('ascii', 'ignore'))[0]
                if resulting_temp:
                    return [0, resulting_temp]
                else:
                    #print("-3, 0")
                    return [-3, 0]
            else:
                #print("-2, 0")
                return [-2, 0]
        except Exception as e:
            self.lastexception = e
            return [-1, 0]

    def read_t_areaX(self, area_no):
        self.camera.clear()
        try:
            query_string = '?T(' + str(area_no) + ')'
            result = self.query(query_string)
            # print result
            # print self.CommandIsKnow(result)
            if result[0] < 0:
                #print("result < 0")
                return result[0, 0]
            elif self.CommandIsKnow(result):
                resulting_temp = hf.extract_nbr_from_string(result[1].encode('ascii', 'ignore'))
                # print(resulting_temp)
                if resulting_temp:
                    if resulting_temp[0] == str(area_no):
                        return [0, resulting_temp[1]]
                    else:
                        return [-4, 0]
                else:
                    #print("-3, 0")
                    return [-3, 0]
            else:
                #print("-2, 0")
                return [-2, 0]
        except Exception as e:
            self.lastexception = e
            return [-1, 0]

    def read_t_no_of_areaX(self, no_of_area=3, retrymax=10):
        self.camera.clear()
#        if True:
        try:
            #            self.camera.write_termination = ''
            query_string = ''

            # predefine result matrix
            result = []
            result.append([0, no_of_area])
            for actualarea in range(0, no_of_area):
                result.append([-1, 0])  # set each area_no to error
            # print(result)

            # get all temperatures from no of areas
            for actualarea in range(0, no_of_area):
                query_string = '?T(' + str(actualarea) + ')'
                # print(query_string)
                retrymax = 10
                trace_ok = 0
                for retry in range(0, retrymax):
                    queryresult = self.query(query_string)
                    #print(query_string.replace("\r", "") + " result " + str(queryresult))
                    if queryresult[0] >= 0:
                        actualresult = hf.extract_nbr_from_string(queryresult[1].encode('ascii', 'ignore'))
                        if actualresult[0] == str(actualarea) and trace_ok == 0:
                            #print("encode " + str(actualresult))
                            result[actualarea + 1][0] = actualresult[0]  # replace erro with area number
                            result[actualarea + 1][1] = actualresult[1]
                            trace_ok = 1
                            # time.sleep(0.5)   # sleeptime not necessary anymore
                            break
                        else:
                            # time.sleep(0.5)
                            pass
                    else:
                        # time.sleep(0.5)
                        pass
            # print(result)
            for actualarea in range(0, no_of_area):
                if not result[actualarea + 1][0] == str(actualarea) or result[actualarea + 1][0] < 0:
                    result[0][0] = -1
            return result
        except Exception as e:
            self.lastexception = e
            return [-1, 0]

    def read_count_of_areas(self, retrymax=10):
        # Read count of measure areas
        self.camera.clear()
#        if True:
        try:
            AreaCount = 0
            query_string = "?AreaCount"
            #queryresult = self.query(query_string)
            # print(queryresult[1].encode('ascii','ignore'))
            retrymax = 10
            trace_ok = 0
            for retry in range(0, retrymax):
                queryresult = self.query(query_string)
                #print(query_string.replace("\r", "") + " result " + str(queryresult))
                if queryresult[0] >= 0:
                    if "!AreaCount" in queryresult[1] and trace_ok == 0:
                        # SH:ToDo: nicht elegant. funktioniert aber. evtl vereinfachen
                        AreaCount = str(hf.extract_nbr_from_string(queryresult[1].encode('ascii', 'ignore'))).replace(
                            "'", "").replace("[", "").replace("]", "")
                        # print(int(AreaCount))
                        trace_ok = 1
                        break
                    else:
                        pass
                else:
                    # time.sleep(0.5)
                    pass
                self.camera.clear()

            return [0, AreaCount]
        except Exception as e:
            self.lastexception = e
            return [-1, 0]

    def check_Serial(self, retrymax=10):
        # Read SerialNumber
        self.camera.clear()
#        if True:
        try:
            SN = ""
            query_string = "?SN"
            #queryresult = self.query(query_string)
            # print(queryresult[1].encode('ascii','ignore'))
            retrymax = 10
            trace_ok = 0
            for retry in range(0, retrymax):
                queryresult = self.query(query_string)
                #print(query_string.replace("\r", "") + " result " + str(queryresult))
                if queryresult[0] >= 0:
                    if "!SN" in queryresult[1] and trace_ok == 0:
                        # SH:ToDo: nicht elegant. funktioniert aber. evtl vereinfachen
                        #queryresult = queryresult[1].split("!SN=")[1]
                        SN = str(hf.extract_nbr_from_string(queryresult[1].encode('ascii', 'ignore'))).replace(
                            "'", "").replace("[", "").replace("]", "")
                        # print(int(SN))
                        trace_ok = 1
                        break
                    else:
                        pass
                else:
                    # time.sleep(0.5)
                    pass
                self.camera.clear()

            return [0, SN]
        except Exception as e:
            self.lastexception = e
            return [-1, 0]

    def check_camera_connection(self):
        check_camera_connection = self.check_Serial()
        if not check_camera_connection[1] == "0" and not str(check_camera_connection[1]) == "0" and not str(check_camera_connection[1]) == "":
            return [0, True]
        else:
            return [-1, False]

# ToDo impementation of improved error handling

            #print("no of areas " + str(result))
            # print self.CommandIsKnow(result)
#            if  result[0] < 0:
#                #print("result < 0")
#                return result[0, 0]
#            elif self.CommandIsKnow(result):
#                resulting_temp = []
#                for actualarea in range(0, no_of_area):
#                    dummy = hf.extract_nbr_from_string(result[actualarea][1].encode('ascii','ignore'))
#                    #print(dummy)
#                    resulting_temp.append(dummy)
#
#                #print("resulting_temp " + str(resulting_temp))
#                if resulting_temp:
#                    if resulting_temp[0] == str(no_of_area):
#                        return [0, resulting_temp[1]]
#                    else:
#                        return [-4, 0]
#                else:
#                    print("-3, 0")
#                    return [-3, 0]
#            else:
#                print("-2, 0")
#                return [-2, 0]
#        except Exception as e:
#            self.lastexception = e
#            return [-1, 0]


if __name__ == "__main__":
    Address = "ASRL11::INSTR"
#    Address = "11"
    Cam = class_IR_Camera()
    Cam.init(Address)
#    time.sleep(1)
    #temperature_all_areas = Cam.read_t_no_of_areaX(no_of_area = 8, retrymax = 10 )
    # print(temperature_all_areas)
    # print(str(Cam.query("!Reinit")))
    print(str(Cam.check_Serial()))
    print(Cam.check_camera_connection())
    print(str(Cam.read_count_of_areas()))
    print(Cam.read_t_main_area())
    print(Cam.read_t_no_of_areaX(no_of_area=9, retrymax=10))
    print("close")
    Cam.close()
