class Logics:
    logic_rows = [
        {
            "name": "Border",
            "trigger": {
                "type": "event",
                "event": "change"
            },
            "actions": [
                {
                    "name": "Border Left",
                    "type": "customAction",
                    "customAction": "const element = instance.element;\r\nconst tdElement = element.closest("
                                    "\"td\");\r\n\r\nif (tdElement) {\r\n  tdElement.rowSpan = '$$$rowSpan$$';\r\n  "
                                    "console.log(tdElement);\r\n} else {\r\n  console.error('No parent <td> element "
                                    "found.');\r\n}\r\n",
                    "content": "<div class=\"well\">Content</div>"
                }
            ]
        }
    ]

    logic_cols = [
        {
            "name": "Border",
            "trigger": {
                "type": "event",
                "event": "change"
            },
            "actions": [
                {
                    "name": "Border Left",
                    "type": "customAction",
                    "customAction":
                        "const element = instance.element;\r\nconst tdElement = "
                        "element.closest(\"td\");\r\n\r\nif (tdElement) {\r\n  tdElement.colSpan = '$$$colSpan$$';\r\n  "
                        "console.log(tdElement);\r\n} else {\r\n  console.error('No parent <td> element found.');\r\n}\r\n",
                    "content": "<div class=\"well\">Content</div>"
                }
            ]
        }
    ]
    logic_row_cols = [
        {
            "name": "Border",
            "trigger": {
                "type": "event",
                "event": "change"
            },
            "actions": [
                {
                    "name": "Border Left",
                    "type": "customAction",
                    "customAction":
                        "const element = instance.element;\r\nconst tdElement = "
                        "element.closest(\"td\");\r\n\r\nif (tdElement) {\r\n  tdElement.colSpan = '$$$colSpan$$';\r\n tdElement.rowSpan = '$$$rowSpan$$';\r\n  "
                        "console.log(tdElement);\r\n} else {\r\n  console.error('No parent <td> element found.');\r\n}\r\n",
                    "content": "<div class=\"well\">Content</div>"
                }
            ]
        }
    ]
    merge_compo = {
        "label": "HTML",
        "attrs": [
            {
                "attr": "",
                "value": ""
            }
        ],
        "content": "Merge",
        "refreshOnChange": False,
        "key": "htm9",
        "logic": [
            {
                "name": "Border",
                "trigger": {
                    "type": "event",
                    "event": "change"
                },
                "actions": [
                    {
                        "name": "Border Left",
                        "type": "customAction",
                        "customAction": "const element = instance.element;\r\nconst tdElement = element.closest(\"td\");\r\n\r\nif (tdElement) {\r\n  tdElement.remove();\r\n  console.log('Element removed:', tdElement);\r\n} else {\r\n  console.error('No parent <td> element found.');\r\n}\r\n",
                        "content": "<div class=\"well\">Content</div>"
                    }
                ]
            }
        ],
        "type": "htmlelement",
        "input": False,
        "tableView": False
    }
