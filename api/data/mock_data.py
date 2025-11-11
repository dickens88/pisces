"""
Mock数据文件
包含所有前端mock接口使用的数据
"""

# 告警Mock数据
MOCK_ALERTS = [
    {
        "id": 1,
        "createTime": "2023-10-27 14:30:15",
        "title": "SQL Injection Attempt Detected on Server DB01",
        "riskLevel": "high",
        "status": "open",
        "owner": "张三",
        "severity": "high",
        "ruleName": "SQL Injection Detection",
        "timestamp": "2023-10-27 14:35:10 UTC",
        "aiAnalysis": {
            "confidence": "high",
            "summary": "High Confidence SQL Injection Attempt Detected",
            "description": "The AI model detected a SQL injection attempt targeting the database server. Multiple suspicious SQL patterns were identified in the request payload.",
            "recommendation": "Immediately block the source IP and review database access logs."
        },
        "associatedEntities": [
            {"type": "host", "name": "prod-db-server-01", "label": "Host"},
            {"type": "ip", "name": "192.168.1.50", "label": "Source IP"},
            {"type": "user", "name": "admin_user", "label": "Target User"}
        ],
        "timeline": [
            {"time": "14:35:10 UTC", "event": "Alert Triggered"},
            {"time": "14:34:55 UTC", "event": "Suspicious SQL Pattern Detected"},
            {"time": "14:33:12 UTC", "event": "First Suspicious Request"}
        ],
        "comments": [
            {
                "id": 1,
                "author": "Jane Doe",
                "authorInitials": "JD",
                "time": "2 hours ago",
                "content": "Confirmed SQL injection attempt. Blocking source IP now."
            },
            {
                "id": 2,
                "author": "Alex Smith",
                "authorInitials": "AS",
                "time": "4 hours ago",
                "content": "Reviewing database logs for any successful injection attempts."
            }
        ]
    },
    {
        "id": 2,
        "createTime": "2023-10-27 13:55:02",
        "title": "Unusual Login Activity from an Unrecognized IP",
        "riskLevel": "medium",
        "status": "pending",
        "owner": "李四",
        "severity": "medium",
        "ruleName": "Unusual Login Detection",
        "timestamp": "2023-10-27 13:55:02 UTC",
        "aiAnalysis": {
            "confidence": "medium",
            "summary": "Unusual Login Pattern Detected",
            "description": "Multiple login attempts from an unrecognized IP address. The IP has no prior successful login history.",
            "recommendation": "Verify user identity and consider implementing additional authentication factors."
        },
        "associatedEntities": [
            {"type": "host", "name": "prod-web-server-01", "label": "Host"},
            {"type": "ip", "name": "203.0.113.45", "label": "Source IP"},
            {"type": "user", "name": "user123", "label": "Target User"}
        ],
        "timeline": [
            {"time": "13:55:02 UTC", "event": "Alert Triggered"},
            {"time": "13:54:30 UTC", "event": "Third Failed Login Attempt"},
            {"time": "13:53:15 UTC", "event": "First Login Attempt"}
        ],
        "comments": []
    },
    {
        "id": 3,
        "createTime": "2023-10-27 12:10:48",
        "title": "Potential Malware Detected on Workstation WS102",
        "riskLevel": "high",
        "status": "closed",
        "owner": "王五",
        "severity": "high",
        "ruleName": "Malware Detection",
        "timestamp": "2023-10-27 12:10:48 UTC",
        "aiAnalysis": {
            "confidence": "high",
            "summary": "Malware Signature Detected",
            "description": "A known malware signature was detected on the workstation. Immediate isolation recommended.",
            "recommendation": "Isolate the workstation from the network and initiate malware removal procedures."
        },
        "associatedEntities": [
            {"type": "host", "name": "workstation-ws102", "label": "Host"},
            {"type": "ip", "name": "192.168.1.102", "label": "IP Address"}
        ],
        "timeline": [
            {"time": "12:10:48 UTC", "event": "Alert Triggered"},
            {"time": "12:09:20 UTC", "event": "Malware Signature Matched"}
        ],
        "comments": [
            {
                "id": 1,
                "author": "Security Team",
                "authorInitials": "ST",
                "time": "1 hour ago",
                "content": "Workstation isolated and cleaned. Alert resolved."
            }
        ]
    },
    {
        "id": 4,
        "createTime": "2023-10-27 11:45:21",
        "title": "Multiple Failed Login Attempts for admin account",
        "riskLevel": "medium",
        "status": "open",
        "owner": "赵六",
        "severity": "medium",
        "ruleName": "Brute Force Detection",
        "timestamp": "2023-10-27 11:45:21 UTC",
        "aiAnalysis": {
            "confidence": "high",
            "summary": "Brute Force Attack Detected",
            "description": "Multiple failed login attempts detected for the admin account. This appears to be a brute force attack.",
            "recommendation": "Block the source IP and enable account lockout policy."
        },
        "associatedEntities": [
            {"type": "host", "name": "auth-server-01", "label": "Host"},
            {"type": "ip", "name": "192.168.1.100", "label": "Source IP"},
            {"type": "user", "name": "admin", "label": "Target User"}
        ],
        "timeline": [
            {"time": "11:45:21 UTC", "event": "Alert Triggered"},
            {"time": "11:44:50 UTC", "event": "10th Failed Attempt"},
            {"time": "11:43:15 UTC", "event": "First Failed Attempt"}
        ],
        "comments": []
    },
    {
        "id": 5,
        "createTime": "2023-10-27 10:20:00",
        "title": "Port Scan Detected from External IP 203.0.113.55",
        "riskLevel": "low",
        "status": "closed",
        "owner": "孙七",
        "severity": "low",
        "ruleName": "Port Scan Detection",
        "timestamp": "2023-10-27 10:20:00 UTC",
        "aiAnalysis": {
            "confidence": "medium",
            "summary": "Port Scanning Activity Detected",
            "description": "Port scanning activity detected from an external IP address. This may be reconnaissance activity.",
            "recommendation": "Monitor the IP address and consider blocking if the activity continues."
        },
        "associatedEntities": [
            {"type": "ip", "name": "203.0.113.55", "label": "Source IP"}
        ],
        "timeline": [
            {"time": "10:20:00 UTC", "event": "Alert Triggered"},
            {"time": "10:19:30 UTC", "event": "Port Scan Started"}
        ],
        "comments": [
            {
                "id": 1,
                "author": "Network Team",
                "authorInitials": "NT",
                "time": "3 hours ago",
                "content": "IP address added to monitoring list. No further action required at this time."
            }
        ]
    }
]

# 威胁情报Mock数据
MOCK_THREAT_INTELLIGENCE = {
    1: [
        {
            "id": 1,
            "type": "ip",
            "title": "Malicious IP: 192.168.1.100",
            "description": "IP associated with known botnet activity and SSH brute-force campaigns. Classified as high-confidence threat.",
            "source": "SOC Team",
            "timestamp": "2023-10-26 09:15:00"
        },
        {
            "id": 2,
            "type": "ttp",
            "title": "TTP: T1078 - Valid Accounts",
            "description": "Adversaries may obtain and abuse credentials of existing accounts as a means of gaining initial access, persistence, privilege escalation, or defense evasion.",
            "source": "Threat Intel Feed",
            "timestamp": "2023-10-25 11:30:21"
        },
        {
            "id": 3,
            "type": "campaign",
            "title": "Campaign: \"Winter Dragon\"",
            "description": "Ongoing campaign targeting financial institutions using SSH brute-force and credential stuffing. The source IP is a known indicator for this campaign.",
            "source": "Alex Smith",
            "timestamp": "2023-10-24 18:05:44"
        },
        {
            "id": 4,
            "type": "vulnerability",
            "title": "Vulnerability: CVE-2023-4863",
            "description": "Heap buffer overflow in WebP in Google Chrome prior to 116.0.5845.187 and libwebp 1.3.2 allowed a remote attacker to perform an out of bounds memory write.",
            "source": "NVD Feed",
            "timestamp": "2023-09-11 10:00:00"
        }
    ],
    2: [
        {
            "id": 1,
            "type": "ip",
            "title": "Suspicious IP: 203.0.113.45",
            "description": "IP address with no prior successful login history. Multiple failed login attempts detected.",
            "source": "Security Team",
            "timestamp": "2023-10-27 13:50:00"
        }
    ],
    4: [
        {
            "id": 1,
            "type": "ip",
            "title": "Malicious IP: 192.168.1.100",
            "description": "IP associated with known brute-force attacks targeting admin accounts.",
            "source": "Threat Intel Feed",
            "timestamp": "2023-10-27 11:40:00"
        },
        {
            "id": 2,
            "type": "ttp",
            "title": "TTP: T1110 - Brute Force",
            "description": "Adversaries may use brute force techniques to gain access to accounts when passwords are unknown or when password hashes are obtained.",
            "source": "MITRE ATT&CK",
            "timestamp": "2023-10-27 11:35:00"
        }
    ]
}

# 关联告警Mock数据
MOCK_ASSOCIATED_ALERTS = {
    1: [
        {
            "id": 4,
            "title": "Multiple Failed Login Attempts for admin account",
            "description": "Detected 15 failed login attempts within 5 minutes from IP 192.168.1.100 targeting the admin account. This may indicate a brute force attack.",
            "createTime": "2023-10-27 11:45:21",
            "owner": "John Smith",
            "riskLevel": "medium",
            "status": "open",
            "severity": "medium"
        },
        {
            "id": 2,
            "title": "Unusual Login Activity from an Unrecognized IP",
            "description": "Successful login detected from IP address 203.0.113.45 which has not been seen in the past 90 days. User account: jane.doe@company.com",
            "createTime": "2023-10-27 13:55:02",
            "owner": "Sarah Johnson",
            "riskLevel": "medium",
            "status": "pending",
            "severity": "medium"
        }
    ],
    2: [
        {
            "id": 1,
            "title": "SQL Injection Attempt Detected on Server DB01",
            "description": "Potential SQL injection attack detected in web application logs. Malicious payload identified in POST request to /api/users endpoint.",
            "createTime": "2023-10-27 14:30:15",
            "owner": "Mike Chen",
            "riskLevel": "high",
            "status": "open",
            "severity": "high"
        }
    ],
    4: [
        {
            "id": 1,
            "title": "SQL Injection Attempt Detected on Server DB01",
            "description": "Potential SQL injection attack detected in web application logs. Malicious payload identified in POST request to /api/users endpoint.",
            "createTime": "2023-10-27 14:30:15",
            "owner": "Mike Chen",
            "riskLevel": "high",
            "status": "open",
            "severity": "high"
        },
        {
            "id": 2,
            "title": "Unusual Login Activity from an Unrecognized IP",
            "description": "Successful login detected from IP address 203.0.113.45 which has not been seen in the past 90 days. User account: jane.doe@company.com",
            "createTime": "2023-10-27 13:55:02",
            "owner": "Sarah Johnson",
            "riskLevel": "medium",
            "status": "pending",
            "severity": "medium"
        }
    ]
}

# 事件Mock数据
MOCK_INCIDENTS = [
    {
        "id": 73519,
        "severity": "high",
        "name": "检测到恶意软件: Trojan.GenericKD.312...",
        "responsibleDepartment": "安全运营部",
        "rootCause": "弱口令",
        "occurrenceTime": "2023-10-27 14:30:15",
        "status": "pending",
        "fullName": "检测到恶意软件: Trojan.GenericKD.312456789",
        "eventId": 73519
    },
    {
        "id": 73518,
        "severity": "medium",
        "name": "多次登录失败",
        "responsibleDepartment": "IT运维部",
        "rootCause": "弱配置",
        "occurrenceTime": "2023-10-27 14:25:01",
        "status": "inProgress",
        "fullName": "多次登录失败",
        "eventId": 73518
    },
    {
        "id": 73517,
        "severity": "low",
        "name": "策略变更: 防火墙规则更新",
        "responsibleDepartment": "网络管理部",
        "rootCause": "弱配置",
        "occurrenceTime": "2023-10-27 14:20:55",
        "status": "closed",
        "fullName": "策略变更: 防火墙规则更新",
        "eventId": 73517
    },
    {
        "id": 73516,
        "severity": "high",
        "name": "检测到数据泄露企图",
        "responsibleDepartment": "安全运营部",
        "rootCause": "高危端口暴露",
        "occurrenceTime": "2023-10-27 14:15:23",
        "status": "pending",
        "fullName": "检测到数据泄露企图",
        "eventId": 73516
    },
    {
        "id": 73515,
        "severity": "medium",
        "name": "检测到异常网络扫描",
        "responsibleDepartment": "IT运维部",
        "rootCause": "未授权接口",
        "occurrenceTime": "2023-10-27 14:10:02",
        "status": "pending",
        "fullName": "检测到异常网络扫描",
        "eventId": 73515
    }
]

# 事件详情Mock数据
MOCK_INCIDENT_DETAIL = {
    "id": 73519,
    "eventId": 73519,
    "name": "Potential Ransomware Activity Detected on SRV-FIN-02",
    "title": "Potential Ransomware Activity Detected on SRV-FIN-02",
    "severity": "high",
    "status": "inProgress",
    "affectedAssets": 4,
    "category": "platform",
    "responsibleDepartment": "安全运营部",
    "responsiblePerson": "Anna Lawson",
    "rootCause": "weakPassword",
    "occurrenceTime": "2023-10-27T14:30:15",
    "createTime": "2023-10-27T14:30:15",
    "updateTime": "2023-10-27T15:45:30",
    "description": "This event correlates multiple high-severity alerts indicating a sophisticated attack targeting financial server SRV-FIN-02. The attack chain began with a successful phishing attempt, followed by PowerShell execution for persistence, command and control communication, and culminating in widespread file encryption activity characteristic of ransomware. The affected asset is a critical server containing sensitive financial data, elevating the incident's impact. Immediate response is required to contain the threat and prevent further data loss.",
    "associatedAlerts": [
        {
            "id": 1,
            "timestamp": "2023-10-27 14:30:15",
            "description": "SQL Injection Attempt Detected on Server DB01",
            "severity": "high",
            "status": "open"
        },
        {
            "id": 2,
            "timestamp": "2023-10-27 13:55:02",
            "description": "Unusual Login Activity from an Unrecognized IP",
            "severity": "medium",
            "status": "pending"
        },
        {
            "id": 3,
            "timestamp": "2023-10-27 12:10:48",
            "description": "Potential Malware Detected on Workstation WS102",
            "severity": "high",
            "status": "closed"
        },
        {
            "id": 4,
            "timestamp": "2023-10-27 11:45:21",
            "description": "Multiple Failed Login Attempts for admin account",
            "severity": "medium",
            "status": "open"
        },
        {
            "id": 5,
            "timestamp": "2023-10-27 10:20:00",
            "description": "Port Scan Detected from External IP 203.0.113.55",
            "severity": "low",
            "status": "closed"
        }
    ],
    "comments": [
        {
            "id": 1,
            "author": "Anna Lawson",
            "authorInitials": "AL",
            "avatarColor": "bg-teal-500",
            "time": "2 hours ago",
            "content": "Initial analysis complete. The activity appears to originate from user 'john.doe's workstation. I've isolated the host from the network and am proceeding with digital forensics to determine the full scope of the compromise. Assigning this to myself for now."
        },
        {
            "id": 2,
            "author": "Robert Miles",
            "authorInitials": "RM",
            "avatarColor": "bg-rose-500",
            "time": "1 hour ago",
            "content": "Good work, Anna. I've checked the firewall logs and found corresponding C2 traffic from the isolated host to 198.51.100.24:4444. I've added a block rule for this IP address across the entire network."
        },
        {
            "id": 3,
            "author": "Sarah Chen (Manager)",
            "authorInitials": "SC",
            "avatarColor": "bg-indigo-500",
            "time": "35 minutes ago",
            "content": "Thanks for the quick response, team. Let's make sure we document all IOCs and update the incident response plan with our findings. Keep me posted on the forensics report."
        },
        {
            "id": 4,
            "author": "Anna Lawson",
            "authorInitials": "AL",
            "avatarColor": "bg-teal-500",
            "time": "5 minutes ago",
            "content": "Forensics image is being captured. ETA is approximately 45 minutes. I will start the analysis as soon as it's ready."
        }
    ],
    "timeline": [
        {
            "time": "10:20:00 AM",
            "title": "Port Scan Detected from External IP",
            "description": "Port scanning activity detected from an external IP address.",
            "alertId": 5,
            "icon": "network_check",
            "severity": "low"
        },
        {
            "time": "11:45:21 AM",
            "title": "Multiple Failed Login Attempts for admin account",
            "description": "Multiple failed login attempts detected for the admin account.",
            "alertId": 4,
            "icon": "lock",
            "severity": "medium"
        },
        {
            "time": "12:10:48 PM",
            "title": "Potential Malware Detected on Workstation",
            "description": "A known malware signature was detected on the workstation.",
            "alertId": 3,
            "icon": "security",
            "severity": "high"
        },
        {
            "time": "1:55:02 PM",
            "title": "Unusual Login Activity from an Unrecognized IP",
            "description": "Multiple login attempts from an unrecognized IP address.",
            "alertId": 2,
            "icon": "login",
            "severity": "medium"
        },
        {
            "time": "2:30:15 PM",
            "title": "SQL Injection Attempt Detected on Server",
            "description": "SQL injection attempt targeting the database server detected.",
            "alertId": 1,
            "icon": "bug_report",
            "severity": "high"
        }
    ],
    "attackChainImage": "https://lh3.googleusercontent.com/aida-public/AB6AXuCKh_sUB5SQUBCbBOxHH4SP4hVt31y_aYmZDI29LgiJNMW14lw9g285Ca0bAi2DpUCcD8XumNMBjNYsDNUWONOiBDUWhX0YkwnkYbaakOyh_9PvKmsIS_2xyr-zF2S2MW9U9T5aVyURip4pe-LyVw9XUAB1nI3Y5gqy5PCXD-gGM7h4PpIJ5hvMBBJmGKcTIvJ3YQJ1IiPrvyjXexda43jh3Pfg0fArfIT5PCEQVYUGr1kK57zbehza2uu4O1TJadCMTDfFF4D7YPE_"
}

# 漏洞Mock数据
MOCK_VULNERABILITIES = [
    {
        "id": 1,
        "name": "CVE-2023-4863: Heap buffer overflow in WebP",
        "cve": "CVE-2023-4863",
        "riskLevel": "critical",
        "affectedAsset": "192.168.1.101",
        "firstDiscoveryTime": "2023-09-15",
        "status": "pending",
        "department": "研发部"
    },
    {
        "id": 2,
        "name": "CVE-2023-38545: SOCKS5 heap buffer overflow in curl",
        "cve": "CVE-2023-38545",
        "riskLevel": "high",
        "affectedAsset": "192.168.1.102",
        "firstDiscoveryTime": "2023-09-12",
        "status": "fixed",
        "department": "运维部"
    },
    {
        "id": 3,
        "name": "Log4Shell: RCE in Apache Log4j",
        "cve": "CVE-2021-44228",
        "riskLevel": "critical",
        "affectedAsset": "10.0.0.5",
        "firstDiscoveryTime": "2023-09-10",
        "status": "inProgress",
        "department": "产品部"
    },
    {
        "id": 4,
        "name": "OpenSSH User Enumeration Vulnerability",
        "cve": "CVE-2018-15473",
        "riskLevel": "medium",
        "affectedAsset": "172.16.0.20",
        "firstDiscoveryTime": "2023-09-08",
        "status": "pending",
        "department": "测试部"
    },
    {
        "id": 5,
        "name": "SSL/TLS: Weak Cipher Suites Supported",
        "cve": "CVE-2016-2183",
        "riskLevel": "low",
        "affectedAsset": "webapp.internal.net",
        "firstDiscoveryTime": "2023-09-05",
        "status": "ignored",
        "department": "市场部"
    },
    {
        "id": 6,
        "name": "CVE-2023-34362: MOVEit SQL Injection",
        "cve": "CVE-2023-34362",
        "riskLevel": "critical",
        "affectedAsset": "192.168.1.105",
        "firstDiscoveryTime": "2023-09-20",
        "status": "pending",
        "department": "研发部"
    },
    {
        "id": 7,
        "name": "CVE-2023-22515: Confluence RCE",
        "cve": "CVE-2023-22515",
        "riskLevel": "high",
        "affectedAsset": "192.168.1.106",
        "firstDiscoveryTime": "2023-09-18",
        "status": "inProgress",
        "department": "运维部"
    },
    {
        "id": 8,
        "name": "CVE-2023-20887: VMware vCenter Server RCE",
        "cve": "CVE-2023-20887",
        "riskLevel": "high",
        "affectedAsset": "10.0.0.10",
        "firstDiscoveryTime": "2023-09-15",
        "status": "fixed",
        "department": "产品部"
    }
]

