# Syslog data
message = """Aug 1 2024 12:18:22 
            GPN-1220_PEL-PRI-SCH_AR12-01 
            %%01QOS/4/SACL_LOG(l)
            [556016]:Ipv4 acl 3500,
            rule 120 deny 17 10.197.119.209(52650)-> 8.8.4.4(53) (2) packets."""

# NCE data
'''
Huawei imaster - NCE tool , like NMS
'''


message = {
    "Header":{"header":""},
    "Body":{
        "notify":{"topic":"Fault",
                  "message":{
                      "alarm":{
                      "notificationId":"160883389",
                      "sourceTime":"2024-07-31T06:24:54.000Z",
                      "objectType":"CTP",
                      "objectName":{
                          "rdn":[
                              {"type":"MD","value":"Huawei/NCE"},
                              {"type":"ME","value":"3145762"},
                              {"type":"PTP","value":"/shelf=1/slot=5/domain=wdm/port=1"},
                              {"type":"CTP","value":"/och=6"}
                              ]
                          },
                      "osTime":"2024-07-31T06:24:56.000Z",
                      "probableCauseQualifier":"160883389",
                      "isClearable":"true",
                      "aliasNameList":{
                          "alias":{
                              "aliasName":"NativeEMSName",
                              "aliasValue":"GBN-0002_GST-6800_DWDM-1"
                              }
                          },
                      "layerRate":"LR_Optical_Channel",
                      "probableCause":{"probableCause":"LOS"},
                      "nativeProbableCause":"CHAN_LOS",
                      "additionalText":"Single-channel signals lost",
                      "perceivedSeverity":"WARNING",
                      "serviceAffecting":"SERVICE_AFFECTING",
                      "rootCauseAlarmIndication":"false",
                      "acknowledgeIndication":"UNACKNOWLEDGED",
                      "X733_EventType":"equipmentAlarm",
                      "X733_SpecificProblems":{
                          "specificProblem":"(1)The configuration for wavelength monitoring is incorrect. The non-accessed wavelength is set to be the monitored wavelength; \n(2)The laser of the board on the opposite station is shutdown; \n(3)The attenuation of the input optical power of the multiplexing unit is overlarge or the fiber is cut; \n(4)The board on the opposite station is faulty; \n(5)The MCA board is faulty."},
                      "X733_CorrelatedNotificationList":"",
                      "X733_AdditionalInformation":{
                          "nv":[
                              {
                                  "name":"ProductName",
                                  "value":"OptiX OSN 6800"
                                  },
                              {
                                  "name":"LocationInfo",
                                  "value":"1-1B_Slave Shelf1 (To WRD)-5-12OPM8-1(IN1 (To WRD))-OCH:1:6"
                                  },
                              {
                                  "name":"EquipmentName",
                                  "value":"12OPM8(2355)"
                                  },
                              {
                                  "name":"MaintenanceStatus",
                                  "value":"NotInMaintenance"
                                  },
                              {
                                  "name":"AlarmType",
                                  "value":"268374017-187"
                                  }
                              ]
                                                    }     
                              }
                             }
                 }
            }
                     }


# TACACS data

message = """Jul 29 08:06:46 172.31.210.13 
            nms_admin vty0  172.31.25.125 stop  
            task_id=2094590 timezone=2  
            service=shell disc-cause=3  
            disc-cause-ext=1022 elapsed_time=597"""
            

# TACACS Alarm data

message = {
    "schema":{
        "type":"struct",
        "fields":[
            {"type":"string",
             "optional":true,
             "doc":"",
             "field":"name"
             },
            {"type":"string",
             "optional":false,
             "doc":"Type of message received",
             "field":"type"
             },
            {"type":"string",
             "optional":true,
             "doc":"",
             "field":"message"
             },
            {"type":"string",
             "optional":true,
             "doc":"",
             "field":"host"
             },
            {"type":"int32",
             "optional":true,
             "doc":"",
             "field":"version"
             },
            {"type":"int32",
             "optional":true,
             "doc":"",
             "field":"level"
             },
            {"type":"string",
             "optional":true,
             "doc":"",
             "field":"tag"
             },
            {"type":"map",
             "keys":{
                "type":"string",
                "optional":false
                },
             "values":{
                "type":"string",
                "optional":false
                },
             "optional":true,
             "doc":"",
             "field":"extension"
             },
            {"type":"string",
             "optional":true,
             "doc":"","field":"severity"
             },
            {"type":"string",
             "optional":true,
             "doc":"",
             "field":"appName"
             },
            {"type":"int32",
             "optional":true,
             "doc":"",
             "field":"facility"
             },
            {"type":"string"
             ,"optional":true,
             "doc":"",
             "field":"remoteAddress"
             },
            {"type":"string",
             "optional":true,
             "doc":""
             ,"field":"rawMessage"
             },
            {"type":"string",
             "optional":true,
             "doc":"",
             "field":"processId"
             },
            {"type":"string",
             "optional":true,
             "doc":"",
             "field":"messageId"
             },
            {"type":"array",
             "items":{
                 "type":"struct",
                 "fields":[
                     {"type":"string",
                      "optional":true,
                      "doc":"",
                      "field":"id"
                      },
                     {"type":"map",
                      "keys":{
                          "type":"string",
                          "optional":false
                          },
                      "values":{
                          "type":"string",
                          "optional":false
                          },
                      "optional":true,
                      "doc":"",
                      "field":"structuredDataElements"
                      }
                     ],
                 "optional":false,
                 "name":"io.confluent.syslog.StructuredData"
                 },
             "optional":true,
             "doc":"",
             "field":"structuredData"
             },
            {"type":"string",
             "optional":true,
             "doc":"Product name of the device.",
             "field":"deviceVendor"
             },
            {"type":"string",
             "optional":true,
             "doc":"Product name of the device.",
             "field":"deviceProduct"
             },
            {"type":"string",
             "optional":true,
             "doc":"Version of the device.",
             "field":"deviceVersion"
             },
            {"type":"string",
             "optional":true,
             "doc":"Device Event Class ID is a unique identifier per event-type. This can be a string or an integer. Device Event ClassID identifies the type of event reported. In the intrusion detection system (IDS) world, each signature or rule that detects certain activity has a unique Device Event ClassID assigned. This is a requirement for other types of devices as well, and helps correlation engines process the events. Also known as Signature ID.","field":"deviceEventClassId"
             },
            {"type":"int64",
             "optional":true,
             "name":"org.apache.kafka.connect.data.Timestamp",
             "version":1,
             "doc":"Time of the message.",
             "field":"timestamp"
             },
            {"type":"int64",
             "optional":true,
             "name":"org.apache.kafka.connect.data.Timestamp",
             "version":1,
             "doc":"Timestamp when syslog message is received.",
             "field":"receivedDate"
             }
            ],
        "optional":false,
        "name":"io.confluent.syslog.Message"
        },
    "payload":{
        "name":null,
        "type":"UNKNOWN",
        "message":null,
        "host":null,
        "version":null,
        "level":null,
        "tag":null,
        "extension":null,
        "severity":null,
        "appName":null,
        "facility":null,
        "remoteAddress":"172.18.2.46",
        "rawMessage":"<188>Aug  1 2024 12:33:22 GPN-1220_PEL-PRI-SCH_AR12-01 %%01QOS/4/SACL_LOG(l)[559101]:Ipv4 acl 3500,rule 120 deny 17 10.197.119.209(48903)-> 8.8.4.4(53) (2) packets. ",
        "processId":null,
        "messageId":null,
        "structuredData":null,
        "deviceVendor":null,
        "deviceProduct":null,
        "deviceVersion":null,
        "deviceEventClassId":null,
        "timestamp":1722515830694,
        "receivedDate":null
        }
    }