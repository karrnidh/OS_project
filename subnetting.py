import ipaddress
import math

def subnet_tool():
    """
    Simple subnetting helper tool.

    Steps:
    1. Take an IP address with CIDR notation and required hosts per subnet.
    2. Calculate how many host bits are needed.
    3. Derive the new subnet mask / prefix.
    4. Generate subnets and display details (network, broadcast, host range).
    """
    print("\n=== SUBNETTING TOOL ===")

    # Get base network (IP + CIDR) and required number of hosts per subnet from user.
    ip_with_cidr = input("Enter IP address with CIDR (e.g., 192.168.1.0/24): ").strip()
    required_hosts = int(input("Enter required hosts per subnet: ").strip())

    try:
        network = ipaddress.ip_network(ip_with_cidr, strict=False)
    except:
        print(" Invalid IP or CIDR. Try again.")
        return

    print("\nINPUT")
    print("IP Network:", network)
    print("Required hosts per subnet:", required_hosts)

    # host bits needed so that 2^n >= hosts + 2
    host_bits_needed = math.ceil(math.log2(required_hosts + 2))
    new_prefix = 32 - host_bits_needed

    if new_prefix < network.prefixlen:
        print("\n ERROR: Subnet too large to fit inside the original CIDR block.")
        return

    subnets = list(network.subnets(new_prefix=new_prefix))

    print("\nOUTPUT")
    print("Original CIDR:          ", network.prefixlen)
    print("New CIDR:               ", new_prefix)
    print("Subnet Mask:            ", ipaddress.ip_network(f'0.0.0.0/{new_prefix}').netmask)
    print("Number of Subnets:      ", len(subnets))
    print("Usable Hosts per Subnet:", (2 ** host_bits_needed) - 2)

    print("\nSUBNET DETAILS")
    for i, subnet in enumerate(subnets):
        hosts = list(subnet.hosts())
        network_addr = subnet.network_address
        broadcast_addr = subnet.broadcast_address
        first_host = hosts[0] if hosts else None
        last_host = hosts[-1] if hosts else None

        print(f"\nSubnet {i + 1}:")
        print("  Network Address:  ", network_addr)
        print("  Broadcast Address:", broadcast_addr)
        print("  Host Range:       ", f"{first_host} - {last_host}")
        print("  Subnet Mask:      ", subnet.netmask)
        print("  Total Hosts:      ", subnet.num_addresses - 2)


if __name__ == "__main__":
    subnet_tool()
