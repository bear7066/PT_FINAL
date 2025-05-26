import hashlib
import ipaddress
from time import time
def ua_hash(ua: str) -> str:
    return hashlib.sha256(ua.encode()).hexdigest()

# 取得子網的網路位址
# mask=24 表示子網遮罩 255.255.255.0
def get_subnet(ip: str, mask: int = 24) -> str:
    net = ipaddress.ip_network(f"{ip}/{mask}", strict=False)
    return str(net.network_address)

# 要防禦的類型： 1. UA不匹配 2. IP變更 3. 新設備指紋 4. 高頻率請求 5. Session過期
BASE_RULES: dict[str, int] = {
    "UA_MISMATCH": 40,
    "IP_CHANGE": 30,
    "NEW_DEVICE_FP": 40,
    "HI_FREQ": 20,
    "SESSION_EXPIRE": 10,
    "NEW_DEVICE_FP": 10,
    "UNKNOWN_SUBNET": 10
}

def score_request(session: dict[str, any], request: dict[str, any]) -> int:
    risk = 0
    # 檢查 UA 是否匹配
    if ua_hash(request["ua"]) != session["ua_hash"]:
        risk += BASE_RULES["UA_MISMATCH"]

    # 檢查IP是否變更
    subnet = get_subnet(request["ip"])
    if subnet != session["subnet"]:
        risk += BASE_RULES["IP_CHANGE"]
        if subnet not in request["known_subnets"]:
            # 沒看過的子網
            risk += BASE_RULES["UNKNOWN_SUBNET"]
    
    # 檢查設備指紋是否變更
    if request["fp"] and request["fp"] != session["device_fp_hash"]:
        risk += BASE_RULES["NEW_DEVICE_FP"]

    # 0.35 秒內頻繁請求則有風險
    delta = time() - float(session["last_request_time"])
    if delta < 0.35:
        risk += BASE_RULES["HI_FREQ"]

    # 檢查 session 是否過期
    if time() > float(session["expire_time"]):
        risk += BASE_RULES["SESSION_EXPIRE"]
    return risk


# testing example
session = {
    "ua_hash": ua_hash("Mozilla/5.0"),
    "subnet": "192.168.1.0",
    "device_fp_hash": "abc123fp",
    "last_request_time": str(time() - 5),
    "expire_time": str(time() + 3600)
}

request = {
    "ua": "Mozila/5.0", 
    "ip": "192.68.1.54",  
    "fp": "ab123fp",      
    "known_subnets": ["192.168.1.0"]
}

print(score_request(session, request))  