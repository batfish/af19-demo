import os
import re

from .test_utils import record_results, TEST_STATUS_FAIL, TEST_STATUS_PASS


def test_no_undefined_refs(bf):
    os.environ['bf_policy_name'] = "Base configuration Hygiene Policies"
    bf.asserts.assert_no_undefined_references()


def test_no_duplicate_ips(bf):
    global e
    os.environ['bf_policy_name'] = "Base configuration Hygiene Policies"
    bf.asserts.current_assertion = 'Assert no duplicate IP addresses are configured'

    dup_ips = bf.q.ipOwners(duplicatesOnly=True).answer().frame()

    try:
        assert len(dup_ips.index) == 0
        record_results(bf, status=TEST_STATUS_PASS, message='No duplicate IP addresses present in the network')
    except Exception as e:
        record_results(bf, status=TEST_STATUS_FAIL, message='{} Found duplicate IP address assignment'.format(dup_ips))
        raise e


def test_no_illegal_mtu(bf):
    os.environ['bf_policy_name'] = "Base configuration Hygiene Policies"
    bf.asserts.current_assertion = 'Assert that all MTUs are 1500 bytes'

    ans = bf.q.interfaceProperties(properties="MTU").answer().frame()
    bad_mtu = ans[ans.MTU != 1500]

    try:
        assert len(bad_mtu) == 0
        record_results(bf, status=TEST_STATUS_PASS, message='All interface MTUs are correct')
    except Exception as e:
        record_results(bf, status=TEST_STATUS_FAIL,
                       message='{} Found interfaces with incorrect MTUs'.format(bad_mtu))
        raise e


def _illegal_bandwidth(interface, bandwidth):
    # interfaces like spine[swp23]
    if re.search("^spine", interface.hostname) and re.search(r'^swp\d+$', interface.interface):
        return bandwidth != 1000000000000
    # interfaces like leaf[swp23]
    elif re.search("^leaf", interface.hostname) and re.search(r'^swp\d+$', interface.interface):
        return bandwidth != 10000000000
    # interfaces like swp23s1
    elif re.search(r'^swp\d+s\d+$', interface.interface):
        return bandwidth != 250000000000
    # interfaces like eth0
    elif re.search(r'^eth\d+$', interface.interface):
        return bandwidth != 10000000000
    return False


def test_interface_bandwidth(bf):
    os.environ['bf_policy_name'] = "Base configuration Hygiene Policies"
    bf.asserts.current_assertion = 'Assert that all interface bandwidth are correct'

    ans = bf.q.interfaceProperties(properties="Bandwidth").answer().frame()
    bad_bw = ans[ans.apply(lambda row: _illegal_bandwidth(row['Interface'], row['Bandwidth']), axis=1)]

    try:
        assert len(bad_bw) == 0
        record_results(bf, status=TEST_STATUS_PASS, message='All interface bandwidths are correct')
    except Exception as e:
        record_results(bf, status=TEST_STATUS_FAIL,
                       message='{} Found interfaces with incorrect bandwidths'.format(bad_bw))
        raise e


def _illegal_speed(interface, bandwidth):
    # interfaces like spine[swp23]
    if re.search("^spine", interface.hostname) and re.search(r'^swp\d+$', interface.interface):
        return bandwidth != 1000000000000
    # interfaces like swp23s1
    elif re.search("^spine", interface.hostname) and re.search(r'^swp\d+s\d+$', interface.interface):
        return bandwidth != 250000000000
    return False


def test_interface_speed(bf):
    os.environ['bf_policy_name'] = "Base configuration Hygiene Policies"
    bf.asserts.current_assertion = 'Assert that all interface speeds are correct'

    ans = bf.q.interfaceProperties(properties="Speed").answer().frame()
    bad_speed = ans[ans.apply(lambda row: _illegal_speed(row['Interface'], row['Speed']), axis=1)]

    try:
        assert len(bad_speed) == 0
        record_results(bf, status=TEST_STATUS_PASS, message='All interface speeds are correct')
    except Exception as e:
        record_results(bf, status=TEST_STATUS_FAIL,
                       message='{} Found interfaces with incorrect speeds'.format(bad_speed))
        raise e


def test_proxy_arp(bf):
    os.environ['bf_policy_name'] = "Base configuration Hygiene Policies"
    bf.asserts.current_assertion = 'Assert that proxy ARP is turned off on all interfaces'

    ans = bf.q.interfaceProperties(properties="Proxy_ARP").answer().frame()
    bad_speed = ans[ans.Proxy_ARP != False]

    try:
        assert len(bad_speed) == 0
        record_results(bf, status=TEST_STATUS_PASS, message='Proxy ARP is off for all interfaces')
    except Exception as e:
        record_results(bf, status=TEST_STATUS_FAIL,
                       message='{} Found interfaces with incorrect proxy ARP setting'.format(bad_speed))
        raise e


def test_mask_for_host_subnet(bf):
    os.environ['bf_policy_name'] = "Base configuration Hygiene Policies"
    bf.asserts.current_assertion = 'Assert all host subnets are configured with a /24 netmask'

    # get ipAddress for all VLAN interfaces on all leaf routers
    tip = bf.q.ipOwners().answer().frame()
    leaf_tip = tip[(tip['Node'].str.contains('leaf'))]
    leaf_vlan_tip = tip[(tip['Node'].str.contains('leaf')) & (tip['Interface'].str.contains('vlan'))]
    df = leaf_vlan_tip[leaf_vlan_tip['Mask'] != 24]

    try:
        assert len(df.index) == 0
        record_results(bf, status=TEST_STATUS_PASS, message='All host subnets have correct /24 mask')
    except Exception as e:
        record_results(bf, status=TEST_STATUS_FAIL,
                       message='Host-subnet mask is not /24 on following router-interface pairs:\n{}'.format(
                           df))
        raise e
