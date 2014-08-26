#!/bin/sh
curl --retry 10 -XPUT 'http://{{ hostvars[groups['elasticsearch'][0]]['container_address'] }}:{{ elasticsearch_http_port }}/_template/log_test1' -d '
{
  "template" : "*",
  "order": 0,
    "mappings" : {
      "_default_" : {
        "dynamic_templates" : [ {
          "string_fields" : {
            "mapping" : {
              "index" : "analyzed",
              "omit_norms" : true,
              "type" : "string",
              "fields" : {
                "raw" : {
                  "index" : "not_analyzed",
                  "ignore_above" : 256,
                  "type" : "string"
                }
              }
            },
            "match" : "*",
            "match_mapping_type" : "string"
          }
        } ],
        "properties" : {
          "@version" : {
            "type" : "string",
            "index" : "not_analyzed"
          },
          "geoip" : {
            "dynamic" : "true",
            "properties" : {
              "location" : {
                "type" : "geo_point"
              }
            }
          }
        }
      },
      "logs" : {
        "dynamic_templates" : [ {
          "string_fields" : {
            "mapping" : {
              "index" : "analyzed",
              "omit_norms" : true,
              "type" : "string",
              "fields" : {
                "raw" : {
                  "index" : "not_analyzed",
                  "ignore_above" : 256,
                  "type" : "string"
                }
              }
            },
            "match" : "*",
            "match_mapping_type" : "string"
          }
        } ],
        "properties" : {
          "@fields" : {
            "properties" : {
              "facility" : {
                "type" : "string",
                "norms" : {
                  "enabled" : false
                },
                "fields" : {
                  "raw" : {
                    "type" : "string",
                    "index" : "not_analyzed",
                    "ignore_above" : 256
                  }
                }
              },
              "processid" : {
                "type" : "string",
                "norms" : {
                  "enabled" : false
                },
                "fields" : {
                  "raw" : {
                    "type" : "string",
                    "index" : "not_analyzed",
                    "ignore_above" : 256
                  }
                }
              },
              "program" : {
                "type" : "string",
                "norms" : {
                  "enabled" : false
                },
                "fields" : {
                  "raw" : {
                    "type" : "string",
                    "index" : "not_analyzed",
                    "ignore_above" : 256
                  }
                }
              },
              "severity" : {
                "type" : "string",
                "norms" : {
                  "enabled" : false
                },
                "fields" : {
                  "raw" : {
                    "type" : "string",
                    "index" : "not_analyzed",
                    "ignore_above" : 256
                  }
                }
              }
            }
          },
          "@message" : {
            "type" : "string",
            "norms" : {
              "enabled" : false
            },
            "fields" : {
              "raw" : {
                "type" : "string",
                "index" : "not_analyzed",
                "ignore_above" : 256
              }
            }
          },
          "@source" : {
            "type" : "string",
            "norms" : {
              "enabled" : false
            },
            "fields" : {
              "raw" : {
                "type" : "string",
                "index" : "not_analyzed",
                "ignore_above" : 256
              }
            }
          },
          "@source_host" : {
            "type" : "string",
            "norms" : {
              "enabled" : false
            },
            "fields" : {
              "raw" : {
                "type" : "string",
                "index" : "not_analyzed",
                "ignore_above" : 256
              }
            }
          },
          "@timestamp" : {
            "type" : "date",
            "format" : "dateOptionalTime"
          },
          "@version" : {
            "type" : "string",
            "index" : "not_analyzed"
          },
          "facility" : {
            "type" : "long"
          },
          "facility_label" : {
            "type" : "string",
            "norms" : {
              "enabled" : false
            },
            "fields" : {
              "raw" : {
                "type" : "string",
                "index" : "not_analyzed",
                "ignore_above" : 256
              }
            }
          },
          "geoip" : {
            "dynamic" : "true",
            "properties" : {
              "location" : {
                "type" : "geo_point"
              }
            }
          },
          "host" : {
            "type" : "ip",
            "norms" : {
              "enabled" : false
            },
            "fields" : {
              "raw" : {
                "type" : "string",
                "index" : "not_analyzed",
                "ignore_above" : 256
              }
            }
          },
          "os_level" : {
            "type" : "string",
            "norms" : {
              "enabled" : false
            },
            "fields" : {
              "raw" : {
                "type" : "string",
                "index" : "not_analyzed",
                "ignore_above" : 256
              }
            }
          },
          "os_program" : {
            "type" : "string",
            "norms" : {
              "enabled" : false
            },
            "fields" : {
              "raw" : {
                "type" : "string",
                "index" : "not_analyzed",
                "ignore_above" : 256
              }
            }
          },
          "os_program_path" : {
            "type" : "string",
            "norms" : {
              "enabled" : false
            },
            "fields" : {
              "raw" : {
                "type" : "string",
                "index" : "not_analyzed",
                "ignore_above" : 256
              }
            }
          },
          "os_program_pid" : {
            "type" : "string",
            "norms" : {
              "enabled" : false
            },
            "fields" : {
              "raw" : {
                "type" : "string",
                "index" : "not_analyzed",
                "ignore_above" : 256
              }
            }
          },
          "os_timestamp" : {
            "type" : "string",
            "norms" : {
              "enabled" : false
            },
            "fields" : {
              "raw" : {
                "type" : "string",
                "index" : "not_analyzed",
                "ignore_above" : 256
              }
            }
          },
          "priority" : {
            "type" : "long"
          },
          "severity" : {
            "type" : "long"
          },
          "severity_label" : {
            "type" : "string",
            "norms" : {
              "enabled" : false
            },
            "fields" : {
              "raw" : {
                "type" : "string",
                "index" : "not_analyzed",
                "ignore_above" : 256
              }
            }
          },
          "tags" : {
            "type" : "string",
            "norms" : {
              "enabled" : false
            },
            "fields" : {
              "raw" : {
                "type" : "string",
                "index" : "not_analyzed",
                "ignore_above" : 256
              }
            }
          }
        }
      }
    }
  }
}'
