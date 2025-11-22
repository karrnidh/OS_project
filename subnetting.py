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

    # Try to parse the given string into an ip_network object.
    # strict=False allows host bits to be set (e.g., 192.168.1.10/24),
    # and it will internally treat it as the network 192.168.1.0/24.
    try:
        network = ipaddress.ip_network(ip_with_cidr, strict=False)
    except:
        print(" Invalid IP or CIDR. Try again.")
        return

    print("\nINPUT")
    print("IP Network:", network)
    print("Required hosts per subnet:", required_hosts)

    # Determine how many host bits are required to support the requested number of hosts.
    # We add 2 to required_hosts to account for the network and broadcast addresses.
    # host_bits_needed = smallest n such that 2^n >= required_hosts + 2
    host_bits_needed = math.ceil(math.log2(required_hosts + 2))
    # New prefix length = 32 - host_bits (for IPv4).
    new_prefix = 32 - host_bits_needed

    # If the new prefix is "less specific" (smaller) than the original,
    # the resulting subnets would be larger than the original network, which is invalid.
    if new_prefix < network.prefixlen:
        print("\n ERROR: Subnet too large to fit inside the original CIDR block.")
        return

    # Generate all subnets inside the original network with the new prefix.
    subnets = list(network.subnets(new_prefix=new_prefix))

    print("\nOUTPUT")
    print("Original CIDR:          ", network.prefixlen)
    print("New CIDR:               ", new_prefix)
    # Build a dummy network to extract the subnet mask from the new prefix.
    print("Subnet Mask:            ", ipaddress.ip_network(f'0.0.0.0/{new_prefix}').netmask)
    print("Number of Subnets:      ", len(subnets))
    # Theoretical usable hosts per subnet = 2^host_bits - 2 (excluding network + broadcast).
    print("Usable Hosts per Subnet:", (2 ** host_bits_needed) - 2)

    print("\nSUBNET DETAILS")
    # For each generated subnet, show key details.
    for i, subnet in enumerate(subnets):
        # List of usable host addresses (excluding network and broadcast).
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
        # Total usable hosts per subnet = total addresses - 2 (network + broadcast).
        print("  Total Hosts:      ", subnet.num_addresses - 2)


# Run tool only when the script is executed directly (not when imported as a module).
if _name_ == "_main_":
    subnet_tool()