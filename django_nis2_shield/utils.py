import ipaddress

def anonymize_ip(ip_address: str, mask_ipv4: int = 24, mask_ipv6: int = 48) -> str:
    """
    Anonymizes an IP address by masking the last bits.
    Default: /24 for IPv4 (keeps first 3 octets), /48 for IPv6.
    """
    try:
        ip = ipaddress.ip_address(ip_address)
        if ip.version == 4:
            network = ipaddress.ip_network(f"{ip}/{mask_ipv4}", strict=False)
            return str(network.network_address)
        elif ip.version == 6:
            network = ipaddress.ip_network(f"{ip}/{mask_ipv6}", strict=False)
            return str(network.network_address)
    except ValueError:
        return "0.0.0.0"  # Fallback for invalid IPs

def get_client_ip(request) -> str:
    """
    Retrieves the client IP address from the request.
    Handles X-Forwarded-For header.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_subnet(ip_address: str, mask_ipv4: int = 24, mask_ipv6: int = 48) -> str:
    """
    Returns the subnet of an IP address.
    Used for Session Guard tolerance.
    """
    return anonymize_ip(ip_address, mask_ipv4, mask_ipv6)
