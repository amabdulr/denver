#!/usr/bin/env python3
"""
Debug script that replicates the Analysis tab flow from sidebar_app.py
WITHOUT needing Streamlit.  Traces every step so you can see exactly
what the LLM will receive in {{RECOMMENDED_GUIDE}}, {{RECOMMENDED_SECTION}},
and {{RECOMMENDED_FORMAT}}.

Usage:
    python3 debug_analysis.py                   # default RCA (mss_clamping)
    python3 debug_analysis.py --rca template    # template negotiation RCA
    python3 debug_analysis.py --rca policy      # policy configuration RCA
    python3 debug_analysis.py --no-llm          # skip the actual LLM call
    python3 debug_analysis.py --rca policy --no-llm   # combine flags
"""

import importlib
import json
import sys
import os
import textwrap

# ── Ensure we're in the right directory ──
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# ── Reload app_functions fresh ──
import app_functions
importlib.reload(app_functions)
from app_functions import (
    extract_doc_clues_data,
    match_terms_to_guides,
    format_doc_clues_for_prompt,
    _scan_for_networking_terms,
)

# ═══════════════════════════════════════════════════════════════════
# TEST RCAs — add more here as needed
# ═══════════════════════════════════════════════════════════════════

TEST_RCAS = {
    "mss_clamping": {
        "product": "Cisco SD-WAN",
        "description": "TCP MSS Clamping on cEdge C8300",
        "content": """\
Executive Summary:
This case addressed a customer inquiry regarding the behavior and configuration of TCP MSS (Maximum Segment Size) Clamping on Cisco Catalyst C8300-1N1S-4T2X routers running IOS-XE SD-WAN (cEdge) in controller mode. The customer specifically sought clarification on whether MSS clamping applies equally on both ingress and egress directions, and whether it affects both SYN and SYN+ACK packets. Additionally, they wanted to know if configuring MSS clamping only on the LAN-side interface is sufficient, or if it must also be set on tunnel interfaces. The root cause of the confusion stemmed from platform-dependent behavior and ambiguous documentation, leading to uncertainty in best practices for configuration.

Steps to Reproduce:
1. Configure `ip tcp adjust-mss` on both a tunnel interface and a LAN-side interface on a Cisco Catalyst C8300-1N1S-4T2X router.
2. Initiate TCP connections traversing both interfaces.
3. Observe MSS values in SYN and SYN+ACK packets using packet captures on both ingress and egress directions.
4. Repeat the test with MSS clamping configured only on the LAN-side interface.
5. Repeat the test with MSS clamping configured only on the tunnel interface.
6. Compare MSS values and connection behavior in all scenarios.

Condition:
- Device: Cisco Catalyst C8300-1N1S-4T2X (also referenced: C8200-1N-4T, C8000V)
- Software: IOS-XE SD-WAN (cEdge), version not explicitly stated but references to 17.x and 17.09.05 in related cases.
- Configuration:
  - `ip tcp adjust-mss <value>` applied on either or both of:
    - interface Tunnel X
    - interface XGigabitEthernet X (LAN-side)
- Traffic: TCP connections traversing the device, including both SYN and SYN+ACK packets.

Workarounds:
- If only one LAN interface is used for all tunnel traffic, apply `ip tcp adjust-mss` on the LAN interface to ensure all relevant traffic is clamped.

Procedure (Solution):
1. Identify all interfaces through which TCP traffic will traverse, especially those entering or exiting VPN tunnels.
2. Apply the MSS clamping configuration.
7. Reference official documentation for further details:
   - https://www.cisco.com/c/en/us/td/docs/routers/sdwan/configuration/system-interface/ios-xe-17/systems-interfaces-book-xe-sdwan/configure-interfaces.html#Cisco_Concept.dita_7e3ad6c7-1784-4beb-949b-a124ab4bc7f6

Root Cause:
The root cause of the confusion was the platform-dependent behavior of the `ip tcp adjust-mss` command and the lack of explicit documentation regarding its directionality (ingress/egress) on different Cisco hardware and software versions.
""",
    },

    "template": {
        "product": "Cisco SD-WAN",
        "description": "Feature template negotiation failure on vEdge",
        "content": """\
Executive Summary:
Customer reported that after upgrading vManage to 20.12.2, pushing a feature template to vEdge 2000 devices fails with error "Template negotiation failed - device unreachable". The template push worked fine on the previous vManage version 20.9.4. The issue affects all vEdge 2000 routers across the SD-WAN overlay, but Catalyst 8000v (cEdge) devices accept templates normally.

Steps to Reproduce:
1. Upgrade vManage from 20.9.4 to 20.12.2.
2. Open vManage Configuration > Templates.
3. Select an existing device feature template attached to a vEdge 2000.
4. Push the template to the vEdge 2000 device.
5. Observe the error "Template negotiation failed - device unreachable" in the task status.
6. Verify the same template pushes successfully to a cEdge (Catalyst 8000v) device.

Condition:
- vManage version: 20.12.2 (upgraded from 20.9.4)
- Device: vEdge 2000, software version 20.9.4
- Overlay: Full mesh topology with 150+ devices
- Control connections: All active, OMP sessions established
- Feature template: VPN 0 transport + VPN 512 management + system template

Workarounds:
- Downgrade vManage to 20.9.4 and re-push templates.
- Use CLI add-on template as a temporary workaround.

Procedure (Solution):
1. Verify control connections between vManage and vEdge devices using `show control connections`.
2. Check NETCONF session status on the vEdge device.
3. Reference: https://www.cisco.com/c/en/us/td/docs/routers/sdwan/configuration/sdwan-xe-gs-book/manage-devices.html
4. Upgrade vEdge devices to a compatible software version (20.12.x) to match vManage.

Root Cause:
The root cause was a NETCONF version mismatch between vManage 20.12.2 and vEdge 2000 running 20.9.4. The newer vManage uses NETCONF 1.1 by default, while older vEdge software only supports NETCONF 1.0, causing template push negotiation to fail.
""",
    },

    "policy": {
        "product": "Cisco SD-WAN",
        "description": "Centralized data policy not applying to traffic",
        "content": """\
Executive Summary:
Customer configured a centralized data policy on vManage to redirect traffic from VPN 10 to a service chain (firewall) for specific applications. The policy was successfully pushed to vSmart controllers, but traffic from branch sites is not being redirected according to the policy. Direct internet access (DIA) traffic bypasses the firewall entirely. The customer confirmed the policy shows as active on vSmart using `show running-config policy`.

Steps to Reproduce:
1. Create a centralized data policy in vManage under Configuration > Policies.
2. Define a match condition for VPN 10, matching application "Office365" traffic.
3. Define an action to redirect matching traffic to a service chain (Firewall at site 100).
4. Apply the policy to the target site list containing branch site IDs 200-210.
5. Activate the policy on vSmart controllers.
6. Generate Office365 traffic from a host in VPN 10 at branch site 200.
7. Observe that traffic takes the direct path instead of being redirected to the firewall.

Condition:
- vManage/vSmart version: 20.11.1
- Branch routers: Catalyst 8300 (cEdge), IOS-XE 17.11.1a
- Topology: Hub-and-spoke with regional hubs
- VPN 10: Corporate LAN, internet exit via DIA at branch
- Service chain: Palo Alto firewall at hub site 100
- Policy type: Centralized data policy with app-route match

Workarounds:
- Apply a localized data policy directly on the cEdge router as a temporary measure.
- Use access-list based PBR on the cEdge as a fallback.

Procedure (Solution):
1. Verify the policy is active on vSmart: `show running-config policy`.
2. Check that OMP routes include the policy from vSmart to cEdge: `show sdwan policy from-vsmart`.
3. Verify the service chain is reachable: `show sdwan service-chain database`.
4. Reference: https://www.cisco.com/c/en/us/td/docs/routers/sdwan/configuration/policies/ios-xe-17/policies-book-xe/centralized-policy.html
5. Ensure the site-list in the policy apply section includes the correct site IDs.

Root Cause:
The root cause was that the policy apply direction was set to "from-service" instead of "from-tunnel". Since branch traffic enters the SD-WAN fabric through the tunnel interface, the policy must be applied in the "from-tunnel" direction to match ingress traffic at the branch. With "from-service" direction, the policy only matches traffic originating from the local service-side (LAN) at the hub, not traffic arriving from remote branches.
""",
    },

    "ike_vpn": {
        "product": "Cisco SD-WAN",
        "description": "IKE/IPsec VPN tunnel fvrf mismatch on 8000v",
        "content": """\
Executive Summary:
The customer, Westpac Banking Corporation, reported an issue configuring and establishing an IKE/IPsec VPN tunnel between a Cisco 8000v router managed via Cisco SD-WAN vManage feature templates and a Juniper SRX device. The VPN tunnel failed to come up due to a mismatch in Forwarding VRF (fvrf) parameters within the IKEv2 policy and profile configuration. The impact was that secure connectivity between the Cisco and Juniper devices was not operational. The root cause was identified as the absence of the `match fvrf` configuration in the IKEv2 policy and profile, which vManage feature templates do not natively support. The issue was resolved by manually defining `fvrf` in both the IKEv2 profile and policy using CLI configuration snippets.

Steps to Reproduce:
1. Configure an IKE/IPsec VPN between a Cisco 8000v router and a Juniper SRX device using Cisco SD-WAN vManage feature templates.
2. Apply Phase 1 and Phase 2 parameters matching the SRX configuration:
   - IKEv2, AES-256-CBC, SHA2, DH Group 19, Main mode.
   - IPsec AES256, SHA256, PFS Group 19.
3. Attempt to bring up the tunnel.
4. Observe failure in IKEv2 negotiation with error logs indicating policy mismatch due to fvrf.

Condition:
- Device: Cisco 8000v router managed via Cisco SD-WAN vManage.
- Peer device: Juniper SRX.
- Configuration parameters:
  IKEv2
  AES-256-CBC encryption
  SHA2 hash
  DH Group 19
  IPsec AES256 encryption
  SHA256 hash
  PFS Group 19
- Tunnel configured using vManage feature templates.
- The vManage feature template does not support defining `fvrf` under IKEv2 policy or profile.

Workarounds:
The issue was mitigated by manually defining the `fvrf` parameter in both the IKEv2 policy and profile using CLI configuration snippets, as vManage feature templates do not support this configuration natively.

Procedure (Solution):
The issue was resolved by adding the following CLI configuration lines to explicitly define the `fvrf`:
crypto ikev2 policy policy1-global
   proposal p1-global
   match fvrf 50
crypto ikev2 profile if-ipsec50-ikev2-profile
   match fvrf 50
interface Tunnel00050
   tunnel vrf 50
These lines were applied manually since the vManage feature template could not handle the `fvrf` requirement. After applying this configuration, the IKE/IPsec tunnel successfully came up.

Root Cause:
The root cause was the absence of the `match fvrf` configuration in the IKEv2 policy and profile when using vManage feature templates. The vManage templates do not provide native support for defining `fvrf` under IKEv2 configurations. As a result, the IKEv2 negotiation failed. Manually defining `fvrf` in both the IKEv2 policy and profile resolved the mismatch and allowed successful tunnel establishment.

Affected Devices/Versions:
- Cisco 8000v router (managed via Cisco SD-WAN vManage)
- Cisco Catalyst C8300-1N1S-6T
""",
    },

    "dns_security": {
        "product": "Cisco SD-WAN",
        "description": "DNS regex/FQDN entries exceed limit causing C8300 crash",
        "content": """\
Executive Summary:
The customer reported that their Cisco Catalyst C8300-1N1S-6T router (serial FDO2932M00G, running IOS XE SD-WAN 17.12.5a) was constantly rebooting after being newly onboarded into SD-WAN controller mode. The impact was severe: the device was unusable, unable to collect logs, and unable to maintain network connectivity. Root cause analysis revealed that the device was crashing due to an excessive number of DNS regex (FQDN) entries configured via the SD-WAN security template, exceeding the supported limit for the platform and software version. This triggered repeated faults in the critical cpp_cp_svr process, causing system reloads.

Steps to Reproduce:
1. Onboard a Cisco Catalyst C8300-1N1S-6T router into SD-WAN controller mode, running IOS XE 17.12.5a.
2. Apply a device template from vManage that includes a security policy with more than 64 DNS regex (FQDN) entries.
3. The device will begin to reload repeatedly.
4. Each reload generates a crash file and system report, with the reboot reason indicating "Critical process cpp_cp_svr fault on fp_0_0 (rc=134)".
5. Console logs and tracebacks show repeated CPU hog events and faults in the cpp_cp_svr process.

Condition:
- Device: Cisco Catalyst C8300-1N1S-6T
- Software: IOS XE SD-WAN 17.12.5a (c8000be-universalk9.17.12.05a.SPA.bin)
- SD-WAN controller mode, managed by vManage.
- Security template applied with more than 64 DNS regex (FQDN) entries.
- Device was newly onboarded and synced with vManage after password recovery via ROMMON.
- No other hardware or environmental issues reported.
- The crash occurs specifically when the number of regex entries exceeds the documented platform limit (64).

Workarounds:
- Reduce the number of DNS regex (FQDN) entries configured on the device to 64 or fewer, as per the documented supported limit.
- Remove the security template from the device template in vManage, then reapply with a reduced number of DNS entries.
- Temporarily operate the device without DNS-based security policies until a software fix is available.

Procedure (Solution):
1. Access vManage and locate the device template assigned to the affected C8300 router.
2. Edit the security policy section of the template.
3. Count the number of DNS regex (FQDN) entries configured. If more than 64, reduce the list to 64 or fewer.
4. Save the updated template.
5. Push the updated template to the device.
6. Monitor the device for stability and confirm that it no longer reboots or generates cpp_cp_svr faults.
7. Optionally, collect "show sdwan reboot history" and "show logging" to confirm the absence of new crash events.
8. If DNS security policies require more than 64 entries, plan to upgrade to a future software release (see Fixed Versions) when available.

Root Cause:
The root cause is a software limitation in IOS XE SD-WAN 17.12.5a on the C8300 platform, where the cpp_cp_svr process (responsible for handling DNS regex/FQDN security policies) cannot reliably handle more than 64 regex entries. When the number of entries exceeds this threshold, the process encounters memory and CPU exhaustion, resulting in repeated faults and system reloads. This is evidenced by:
- Reboot history logs showing "Critical process cpp_cp_svr fault on fp_0_0 (rc=134)" as the reboot reason.
- Tracebacks in system logs showing CPU hog events and faults in cpp_cp_svr, cpp_regexp, and related libraries (cpp_tfc_svr_lib, cpp_common_os, evlib).
- Example log:
  *Oct 19 10:07:08.743: %EVENTLIB-3-CPUHOG: F0/0: cpp_cp_svr: undefined: 1946ms, Traceback=1#f4940dfb468da80738b97077c0f1f01e c:7664048F8000+3C740 cpp_regexp:76640862E000+45A3 ...
- Decoded tracebacks point to failures in DNS regex compilation and transaction handling (functions like make_deterministic, re_compile_prepare, cpp_tfc_dsa_regexp_compose_table).
- The documented supported limit for DNS regex entries is 64 for this platform and version, though some devices may handle up to 128. Exceeding this is not deterministic and leads to instability.
- Bug CSCwp83555 has been filed to increase the supported scale in future releases.

Affected Devices/Versions:
- Device: Cisco Catalyst C8300-1N1S-6T
- Software: IOS XE SD-WAN 17.12.5a (c8000be-universalk9.17.12.05a.SPA.bin)
- All C8300 platforms running affected versions with security templates exceeding 64 DNS regex entries.

Bugs:
- CSCwp83555: SD-WAN DNS Regex/FQDN scale enhancement. This bug tracks the work to increase the supported number of DNS regex entries beyond 64, targeted for release in IOS XE 17.19.x.

Fixed Versions, Patches:
- The scale enhancement for DNS regex entries will be available in IOS XE SD-WAN 17.19.x and later, per CSCwp83555.
- Until then, the only supported workaround is to limit DNS regex entries to 64 or fewer.
""",
    },

    # ── ASR 9000 test RCAs ──

    "sr_autoroute": {
        "product": "ASR 9000",
        "description": "SR-TE autoroute docs missing IPv6 endpoint IS-IS restriction",
        "content": """\
Bug: CSCws82544
Component: iosxr-pi-docs
Product: ASR 9000 / NCS 5500 / Cisco 8000
Severity: 3

Headline: Update SR-TE autoroute documentation regarding IPv6 policy endpoints

Description: SR-TE autoroute documentation should be updated to specify that autoroute feature for SR policies with IPv6 endpoints can only be used with IS-IS. OSPF supports only IPv4 endpoint policies.

RCA: Eng.Escape_Restrictions
Technology: Segment Routing
Platforms: NCS 5500, ASR 9000, Cisco 8000
Versions: 7.9.x, 7.10.x, 7.11.x, 24.1.x, 24.2.x, 24.3.x, 24.4.x

Change description: Added a restriction — the autoroute feature for SR policies with IPv6 endpoints is supported only with IS-IS. OSPF supports autoroute only for SR policies with IPv4 endpoints.

Updated URLs:
ASR 9000: https://www.cisco.com/c/en/us/td/docs/routers/asr9000/software/25xx/segment-routing/configuration/guide/b-segment-routing-cg-asr9000-25xx

Root Cause: The documentation did not include the restriction that autoroute for SR-TE policies with IPv6 endpoints requires IS-IS as the IGP. OSPF only supports autoroute for IPv4 endpoint SR policies. This caused confusion for customers attempting to use OSPF with IPv6 SR-TE autoroute and encountering unexpected behavior.
""",
    },

    "srv6_bvi_mtu": {
        "product": "ASR 9000",
        "description": "SRv6 BVI MTU limitation on Tomahawk line cards",
        "content": """\
Bug: CSCwt18764
Component: asr9k-doc
Product: asr9k
Severity: 3

Headline: Refine SRv6 BVI MTU Limitation on Tomahawk

Description: The currently documented description about the BVI MTU limitation on Tomahawk needs to be updated to explain the limitation in more granular manner.

Reference: https://www.cisco.com/c/en/us/td/docs/routers/asr9000/software/25xx/segment-routing/configuration/guide/b-segment-routing-cg-asr9000-25xx/configure-srv6-full-length-sid.html#srv6-l3vpn-bvi-support

Limitations of BVI over SRv6 on ASR 9000 3rd Generation High-Density Ethernet Line Cards:
- The limitation applies specifically when a 3rd generation high-density Ethernet line card is SRv6 core facing.
- The IPv6/SRv6 header length is not removed after SRv6 decapsulation during the BVI MTU check.
- As a result, the BVI MTU check fails even if the inner packet length is within the MTU limit.

Workarounds for BVI MTU Check Failures:
For ASR 9000 3rd generation high-density Ethernet line cards experiencing BVI MTU check failures, the following workarounds are recommended:
- Increase the MTU of the BVI interface to accommodate the additional IPv6/SRv6 header length.
- If OSPF is used as the PE-CE protocol, it might be required to configure mtu-ignore and packet-size options and increase the MTU of the BVI interface accordingly.
- Consider migrating to 5th generation Ethernet line cards as SRv6 core facing line card.

Root Cause: On ASR 9000 3rd generation high-density Ethernet line cards, the SRv6 decapsulation process does not remove the IPv6/SRv6 header length from the packet size before performing the BVI MTU check. This causes the MTU check to fail for packets whose inner payload is within the MTU limit but whose total size (including the SRv6 encapsulation overhead) exceeds the configured BVI MTU. The documentation did not adequately explain this limitation or distinguish between line card generations.
""",
    },

    "yang_pmengine": {
        "product": "ASR 9000",
        "description": "YANG pmengine-oper naming convention change breaks telemetry sensor paths",
        "content": """\
Bug: CSCwo96641
Component: iosxr-pi-docs
Product: ASR 9000 / Cisco 8000
Severity: 4
Related: CSCwn50223

Headline: Cisco-IOS-XR-pmengine-oper.yang naming convention change

Description: Format of PM engine layers have been changed to make it consistent. The naming convention has been standardized by modifying hour24fec to hour24-fec, minute15pcs to minute15-pcs, second30pcs to second30-pcs throughout all layers — otn, otnsec, pcs, fec, prbs, ether, gfp.

Example — XR Version lower than 25.2.1:
Cisco-IOS-XR-pmengine-oper:performance-management/otu/otu-ports/otu-port/otu-current/otu-minute15/otu-minute15fecs/otu-minute15fec
Cisco-IOS-XR-pmengine-oper:performance-management/otu/otu-ports/otu-port/otu-current/otu-minute15/otu-minute15otns/otu-minute15otn

Example — XR Version 25.2.1 onwards:
Cisco-IOS-XR-pmengine-oper:performance-management/otu/otu-ports/otu-port/otu-current/otu-minute15/otu-minute15-fecs/otu-minute15-fec
Cisco-IOS-XR-pmengine-oper:performance-management/otu/otu-ports/otu-port/otu-current/otu-minute15/otu-minute15-otns/otu-minute15-otn

Symptom: Sensor paths will show as "Not Resolved" after upgrade.
  Sensor Group Id: GNMI__10841413642326652779_0
    Sensor Path: Cisco-IOS-XR-pmengine-oper:performance-management/otu/otu-ports/otu-port/otu-current/otu-second30/otu-second30fecs/otu-second30fec
    Sensor Path State: Not Resolved
    Status: Invalid sensor path

Conditions: Cisco-IOS-XR-pmengine-oper.yang or sensors enabled for telemetry using the old naming convention after upgrading to 25.2.1 or later.

Root Cause: The YANG model Cisco-IOS-XR-pmengine-oper.yang changed its naming convention for performance management layers in XR 25.2.1 to standardize hyphenated names (e.g., minute15-fec instead of minute15fec). Existing telemetry sensor path configurations using the old naming convention become invalid after the upgrade, causing "Not Resolved" sensor path errors. Documentation needs to be updated to reflect this YANG model change.
""",
    },

    # ── ASR9000 #4 : Incorrect optical transmit power table for DP04QSDD-HE0 ──
    "optical_tx_power": {
        "product": "ASR 9000",
        "description": "Incorrect DP04QSDD-HE0 optical transmit power table in interfaces guide",
        "content": """
Bug ID: CSCwp97550
Component: iosxr-pi-docs
Product: all
Severity: 4
Status: A

Headline: Incorrect description of DP04QSDD-HE0 Supported Optical Tx Power

Description: Please update Table 6. format and content to on par with NCS5500/8K description regarding DP04QSDD-HE0. Current content of ASR9k is incorrect and outdated regarding DP04QSDD-HE0

Incorrect description of Configuring Optical Transmit Power - Table 6. Optical Transmit Power Values
https://www.cisco.com/c/en/us/td/docs/routers/asr9000/software/25xx/interfaces/configuration/guide/b-interfaces-hardware-component-cg-asr9000-25xx/configuring-400G-digital-coherent-optics.html

Correct description of Configuring Optical Transmit Power - Table 6. Optical Transmit Power Values
https://www.cisco.com/c/en/us/td/docs/iosxr/ncs5xx/interfaces/25xx/b-interfaces-hardware-component-cg-25xx-ncs540/configuring-400g-digital-coherent-optics.html
https://www.cisco.com/c/en/us/td/docs/iosxr/cisco8000/Interfaces/25xx/configuration/guide/b-interfaces-config-guide-cisco8k-r25xx.html

Symptom: Table 6 Optical Transmit Power Values for DP04QSDD-HE0 is incorrect and outdated in the ASR9000 interfaces hardware component configuration guide.

Conditions: Viewing the ASR9000 interfaces hardware component configuration guide section on configuring 400G digital coherent optics.

Root Cause: The documentation table for DP04QSDD-HE0 optical transmit power values in the ASR9000 interfaces hardware component guide has not been updated to match the corrected format and content present in the NCS5500 and Cisco 8000 equivalents.
""",
    },

    # ── ASR9000 #5 : cnBNG PPPoE SRG warm standby feature ──
    "cnbng_srg": {
        "product": "ASR 9000",
        "description": "cnBNG PPPoE SRG warm standby feature",
        "content": """
Bug ID: CSCwo04604
Component: cnbng_nal
Product: asr9k
Severity: 6
Status: R

Headline: cnBNG PPPoE SRG warm standby feature

Description: cnBNG PPPoE SRG warm standby feature
scoping :EDCS-25572469

Related headlines:
- [CNBNG-NAL] Handle role change to standby for WARM SRG group
- [Warm-stby] Handle PPPoE caps down for warm standby subscriber.
- [Warm-standby] Add new queue to handle SRG switchover to active
- [Warm-standby] Add new event history for warm standby subscriber

Behavior-changed:
Type of behavior change: Release introduced: 25.04.01
Old behavior: SRG group mode had type "Hot" only
New behavior: Added new SRG group mode "Warm"
Impact on customer: It will save system memory and one asr9k can act is Warm standby node for multiple SRG nodes.

Root Cause: The cnBNG (Cloud Native BNG) PPPoE implementation lacked support for Warm standby mode in Subscriber Redundancy Groups (SRG). Previously only Hot standby was available, which consumed significant memory. The new Warm SRG mode allows a single ASR9000 to act as a warm standby node for multiple SRG groups, reducing memory consumption while maintaining session redundancy for PPPoE subscribers.
""",
    },

    # ── SD-WAN #6 : vManage upgrade failure Neo4j db member count ──
    "vmanage_upgrade": {
        "product": "Cisco SD-WAN",
        "description": "vManage GUI upgrade blocked by Neo4j database member count check",
        "content": """\
Executive Summary:
The customer attempted to upgrade their Cisco SDWAN vManage controller (vmanage-293139987.sdwan.cisco.com) from version 20.15.4 to 20.18.1 in a Cisco Cloud Hosted environment. The upgrade failed during the GUI pre-checks due to a "Configuration-db: System and/or Neo4j databases do not have the required member count" error. This prevented the upgrade from proceeding and caused delays in updating the SDWAN management infrastructure. The issue was traced to Cisco bug CSCwm11883, which blocks GUI upgrades when database member counts do not meet expected thresholds. The upgrade was successfully completed using a CLI workaround. Secondary issues included vSmart controllers losing control connections and certificates post-upgrade, requiring re-enrollment and static IPv6 assignment to restore full functionality.

Steps to Reproduce:
1. Initiate upgrade of vManage from version 20.15.4 to 20.18.1 via the vManage GUI.
2. Observe pre-check failures, specifically:
   - Error: "Failed: Configuration-db: System and/or Neo4j databases do not have the required member count"
3. Attempt to proceed with upgrade; GUI blocks further progress.
4. Consider forcing activation via CLI.
5. If CLI workaround is used, upgrade completes successfully.
6. Post-upgrade, attempt to upgrade vSmart controllers.
7. vSmart upgrade fails/rolls back, vSmart loses control connection and certificate.
8. vBond controllers experience intermittent loss of connectivity and IPv6 address assignment.
9. Re-enroll vSmart and assign static IPv6 to vBond to restore control connections.

Condition:
- Cisco Cloud Hosted SDWAN environment.
- Single-node vManage (vmanage-293139987.sdwan.cisco.com), two vBonds, two vSmarts.
- Upgrade path: vManage 20.15.4 to 20.18.1.
- Pre-checks during GUI upgrade require Configuration-db and Neo4j databases to meet specific member count requirements.
- Known defect (CSCwm11883) causes pre-checks to fail in certain single-node/cloud deployments.
- vSmart controllers running on AWS, subject to cloud network reachability and certificate synchronization.
- vBond controllers rely on DHCP for IPv6; loss of DHCP or network flapping can impact control connections.

Workarounds:
- Upgrade vManage using CLI commands instead of GUI:
  - request software install VERSION
  - request software activate VERSION
- Collect configuration-db backup before upgrade:
  - request nms configuration-db backup path file_name_configdb
- For vSmart/vBond certificate or connectivity issues:
  - Re-enroll affected controllers via vManage GUI.
  - Assign static IPv6 addresses to vBond controllers if DHCP fails.
  - Bounce VPN 0 transport interfaces if control connections do not restore automatically.

Root Cause:
- The primary root cause of the vManage upgrade failure was the GUI pre-check logic enforcing Configuration-db and Neo4j database member count requirements, as described in Cisco bug CSCwm11883. In single-node or certain cloud-hosted deployments, these checks may incorrectly fail, blocking GUI upgrades even when the system is otherwise healthy.
- Secondary root cause for vSmart/vBond issues:
  - Repeated upgrade attempts and rollbacks led to certificate corruption and loss of control connections.
  - vBond controllers lost IPv6 addresses due to DHCP failure or AWS network flapping, which prevented proper control plane establishment.
  - vSmart lost its certificate, indicated by ERR_MY_CERT_REJ_BY_SERV and CRTREJSER errors in vManage logs.
- Resolution required re-enrollment of vSmart and static IPv6 assignment to vBond.
""",
    },

    # ── SD-WAN #7 : Stuck policy group deployment (Orange) ──
    "stuck_policy_group": {
        "product": "Cisco SD-WAN",
        "description": "Stuck policy group deployment blocks all migrations — Neo4j residual task",
        "content": """\
Executive Summary:
The customer, Orange, experienced a critical issue on their Cisco Catalyst C8300-1N1S-6T Router managed via vManage (software version 20.12.4.1), where it was impossible to push a new security group policy. Although the stuck deployment task was cleared from the vManage GUI using the API clean command, attempts to deploy a new policy resulted in the error: "Policy group state validation error: A deployment for Policy Group [name of the policy] is in-progress. Please wait to complete." This blocked all migrations and network changes for the customer. The root cause was a residual deployment task in the Neo4j database that was not cleared by the API, requiring manual intervention at the database level. The issue was resolved by editing the Neo4j database entry for the stuck task from "Deploying" to "Deploy Failure," which allowed policy deployment to proceed and unblocked migrations.

Steps to Reproduce:
1. Initiate a security group policy deployment from vManage to a group of cEdge routers.
2. Observe that the deployment task becomes stuck in "in_progress" state (visible via API: /dataservice/device/action/status/tasks).
3. Attempt to clean the stuck task using the API endpoint: /dataservice/device/action/status/tasks/clean?processId=<processId>.
4. Verify that no running tasks are visible in the vManage GUI.
5. Attempt to push a new security group policy.
6. Encounter the error: "Policy group state validation error: A deployment for Policy Group [name of the policy] is in-progress. Please wait to complete."
7. Confirm that migrations and policy changes are blocked.

Condition:
- vManage is running on-premises, managing Cisco Catalyst C8300-1N1S-6T routers.
- Software version: vManage 20.12.4.1.
- The stuck deployment task is for a security policy group push to cEdge devices.
- The API shows no running tasks after clean-up, but the Neo4j database still contains a task with status "in_progress" for processId "deploy_policy_group-5d19b44b-30ab-44c8-a192-305208e724be".

Workarounds:
- No effective workaround was available via the vManage GUI or API; the only temporary mitigation was to avoid further policy pushes until the database was manually corrected.
- Manual intervention in the Neo4j database was required to resolve the issue.

Procedure (Solution):
1. Access the Neo4j database on the vManage server.
2. Locate the stuck deployment task using the processId "deploy_policy_group-5d19b44b-30ab-44c8-a192-305208e724be".
3. Execute Neo4j queries to change the task status from "Deploying" to "Deploy Failure".
4. Verify that the change is reflected and no tasks are stuck in "in_progress" state.
5. Attempt to push the security group policy again from vManage.
6. Confirm successful deployment and unblock migrations.

Root Cause:
The root cause was a race condition or software defect where a deployment task for a policy group remained in the Neo4j database with a status of "in_progress" even after the API clean command was executed and the task was no longer visible in the vManage GUI. This residual database entry caused vManage to block any new policy group deployments, resulting in the error: "Policy group state validation error: A deployment for Policy Group [name of the policy] is in-progress. Please wait to complete."
""",
    },

    # ── SD-WAN #8 : Stuck config group deployment (UHS) ──
    "stuck_config_group": {
        "product": "Cisco SD-WAN",
        "description": "Stuck configuration group deployment — Neo4j database state locked in Deploying",
        "content": """\
Executive Summary:
The customer, UHS of Delaware, reported an issue on Cisco SD-WAN vManage (https://vmanage-388432205.sdwan.cisco.com) where a configuration group deployment was stuck, resulting in the error message:
"Config Group State validation error: A deployment for this Configuration Group is in-progress. Please wait for it to complete."
The Technical Consulting Engineer (TCE) confirmed that the job was stuck in the "Deploying" state. The issue was resolved by accessing the Neo4j database as root and manually changing the deployment state to "Deploy failed." This behavior is documented under Cisco bug ID CSCwf67010. After the manual correction, the deployment state was restored, and the case was confirmed resolved and closed.

Steps to Reproduce:
1. Access Cisco SD-WAN vManage at https://vmanage-388432205.sdwan.cisco.com.
2. Attempt to deploy a configuration group.
3. Observe that the deployment job becomes stuck in the "Deploying" state.
4. Attempt to clear processes using the Cisco-documented API method.
5. After clearing, observe the error message:
   "Config Group State validation error: A deployment for this Configuration Group is in-progress. Please wait for it to complete."
6. Confirm that the deployment remains in-progress and cannot be retried.

Condition:
- Platform: Cisco SD-WAN vManage (Cisco-hosted)
- The issue occurs when a configuration group deployment becomes stuck in the "Deploying" state.
- Attempts to clear the task using the API method result in a persistent validation error preventing further deployment.
- The problem is consistent with previous cases where TAC intervention was required to modify the deployment state in the Neo4j database.

Workarounds:
- The documented workaround involved accessing the Neo4j database as root and manually changing the deployment state from "Deploying" to "Deploy failed."
  neo4j query: match (n:vmanagedbCONFIGGROUPNODE) return n.name, n.state;
- No other temporary workaround was documented.

Procedure (Solution):
- The TCE accessed the Neo4j database as root.
- The deployment state was manually set to "Deploy failed."
- This action cleared the stuck deployment and restored normal operation.
- The customer confirmed resolution and the case was closed.

Root Cause:
The root cause was that the configuration group deployment process in Cisco SD-WAN vManage became stuck in the "Deploying" state and did not complete or fail automatically. This caused the system to reject new deployment attempts with the validation error:
"Config Group State validation error: A deployment for this Configuration Group is in-progress. Please wait for it to complete."
The underlying behavior is documented in Cisco bug CSCwf67010, which describes the condition where deployment states can remain locked in "Deploying," requiring manual database intervention to reset the state.
""",
    },
}

# ═══════════════════════════════════════════════════════════════════
# Parse arguments
# ═══════════════════════════════════════════════════════════════════
SKIP_LLM = "--no-llm" in sys.argv

# Pick the RCA to test
rca_key = "mss_clamping"  # default
if "--rca" in sys.argv:
    idx = sys.argv.index("--rca")
    if idx + 1 < len(sys.argv):
        rca_key = sys.argv[idx + 1]

if rca_key not in TEST_RCAS:
    print(f"❌ Unknown RCA '{rca_key}'. Available: {', '.join(TEST_RCAS.keys())}")
    sys.exit(1)

selected_rca = TEST_RCAS[rca_key]
PRODUCT_NAME = selected_rca["product"]
RCA_CONTENT = selected_rca["content"]

print(f"🧪 Test RCA: {rca_key} — {selected_rca['description']}")
print(f"   Product: {PRODUCT_NAME}")
print(f"   Content: {len(RCA_CONTENT):,} chars\n")

def section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")


# ═══════════════════════════════════════════════════════════════════
# STEP 1: Term detection (what the "Detect" button does)
# ═══════════════════════════════════════════════════════════════════
section("STEP 1: Technology Term Detection")

clues_data = extract_doc_clues_data(RCA_CONTENT)
all_detected_terms = [term for _, term in clues_data.get('tech_terms', [])]
url_clues = clues_data.get('url_clues', [])

term_frequencies = clues_data.get('term_frequencies', {})

print(f"Detected {len(all_detected_terms)} terms, {len(url_clues)} URL(s)")
print(f"\nURL Clues:")
for c in url_clues:
    print(f"  book_pdf:       {c['book_pdf']}")
    print(f"  book_id:        {c['book_id']}")
    print(f"  chapter_clues:  {c['chapter_clues']}")
    print(f"  url:            {c['url'][:100]}...")

print(f"\nDetected Terms ({len(all_detected_terms)}) — with frequency:")
for cat, term in clues_data.get('tech_terms', []):
    freq = term_frequencies.get(term, 1)
    freq_bar = '█' * min(freq, 30)
    print(f"  [{cat:12s}] {term:25s}  ×{freq:3d}  {freq_bar}")

# In the real UI, all terms start selected
selected_raw_terms = all_detected_terms  # user hasn't deselected any


# ═══════════════════════════════════════════════════════════════════
# STEP 2: Guide matching & scoring (what the checkbox expander does)
# ═══════════════════════════════════════════════════════════════════
section("STEP 2: Guide Matching & Scoring")

matched, available_guides = match_terms_to_guides(selected_raw_terms, PRODUCT_NAME, term_frequencies)
guide_scores = matched.pop('_guide_scores', {})
matched_term_guides = dict(matched)  # what sidebar stores in session_state

print(f"\nGuide Scores (top 10):")
for g, s in sorted(guide_scores.items(), key=lambda x: -x[1])[:10]:
    terms_for_guide = [t for t, gl in matched_term_guides.items() if not t.startswith('_') and g in gl]
    print(f"  score={s:6.2f}  {g}")
    if terms_for_guide:
        print(f"          terms: {', '.join(terms_for_guide[:8])}")

print(f"\nMatched term → guide mapping ({len(matched_term_guides)} terms):")
for term, guides in sorted(matched_term_guides.items()):
    if term.startswith('_'):
        continue
    print(f"  {term:25s} → {guides}")

# Simulate auto-checked guides (what the UI does)
auto_matched_guides = set()
for term, guide_list in matched_term_guides.items():
    if term.startswith('_'):
        continue
    for g in guide_list:
        auto_matched_guides.add(g)

selected_guides = list(auto_matched_guides)
print(f"\nAuto-selected guides ({len(selected_guides)}):")
for g in sorted(selected_guides, key=lambda g: guide_scores.get(g, 0), reverse=True):
    print(f"  {'✅':2s} {g} (score={guide_scores.get(g, 0)})")


# ═══════════════════════════════════════════════════════════════════
# STEP 3: Simulate run_agent replacement logic
# ═══════════════════════════════════════════════════════════════════
section("STEP 3: run_agent() Replacement Logic")

# Load BugAnalyze.md (what the text area holds)
with open("BugAnalyze.md", "r") as f:
    question = f.read()

# --- Replicate run_agent logic exactly ---

# Pre-extract URL clues from RCA
clues_data_agent = extract_doc_clues_data(RCA_CONTENT)
url_clues_agent = clues_data_agent.get('url_clues', [])

recommended_label = None
section_label = None

# HIGHEST PRIORITY: URL clue
if url_clues_agent:
    url_book = url_clues_agent[0]['book_pdf']
    chapter_tokens = url_clues_agent[0].get('chapter_clues', [])
    url_score = guide_scores.get(url_book, 'n/a')
    recommended_label = f"{url_book} (from URL reference, score: {url_score})"
    if chapter_tokens:
        section_label = " ".join(t.title() for t in chapter_tokens)
    print(f"URL override active:")
    print(f"  url_book:        {url_book}")
    print(f"  chapter_tokens:  {chapter_tokens}")
    print(f"  url_score:       {url_score}")
else:
    print("No URL clues found — falling back to term scoring")

# FALLBACK: term-based scoring
if not recommended_label:
    if guide_scores:
        top_guide = max(guide_scores, key=guide_scores.get)
        top_score = guide_scores[top_guide]
        recommended_label = f"{top_guide} (confidence score: {top_score})"
    else:
        top_guide = None
        recommended_label = "(no guide scores available — use your best judgment from search results)"
else:
    top_guide = url_clues_agent[0]['book_pdf'] if url_clues_agent else None

# Section fallback
if not section_label:
    effective_guide = top_guide or (max(guide_scores, key=guide_scores.get) if guide_scores else None)
    if effective_guide and matched_term_guides:
        term_weights = []
        for term, guides in matched_term_guides.items():
            if term.startswith('_'):
                continue
            if effective_guide in guides:
                weight = 1.0 / len(guides)
                term_weights.append((term, weight))
        term_weights.sort(key=lambda x: -x[1])
        top_terms = [t.title() for t, _ in term_weights[:5]]
        section_label = ", ".join(top_terms) if top_terms else "(see location recommendations above)"
    else:
        section_label = "(see location recommendations above)"

print(f"\n--- FINAL REPLACEMENTS ---")
print(f"  {{{{RECOMMENDED_GUIDE}}}}   => {recommended_label}")
print(f"  {{{{RECOMMENDED_SECTION}}}} => {section_label}")

# Apply replacements
question = question.replace('{{RECOMMENDED_GUIDE}}', recommended_label)
question = question.replace('{{RECOMMENDED_SECTION}}', section_label)

# Check for any remaining unresolved placeholders
import re
remaining = re.findall(r'\{\{[^}]+\}\}', question)
if remaining:
    print(f"\n⚠️  UNRESOLVED PLACEHOLDERS ({len(remaining)}):")
    for p in remaining:
        print(f"    {p}")
else:
    print(f"\n✅ All placeholders resolved!")


# ═══════════════════════════════════════════════════════════════════
# STEP 4: Show the key lines the LLM will see
# ═══════════════════════════════════════════════════════════════════
section("STEP 4: Key Lines the LLM Sees (from BugAnalyze.md)")

for i, line in enumerate(question.split('\n'), 1):
    stripped = line.strip()
    if any(k in stripped for k in ['Recommended Guide:', 'Recommended Section:', 'Recommended Format:']):
        print(f"  Line {i}: {stripped}")


# ═══════════════════════════════════════════════════════════════════
# STEP 5: Build full_question (question + RCA)
# ═══════════════════════════════════════════════════════════════════
section("STEP 5: full_question Construction")

full_question = question + RCA_CONTENT
print(f"  question length:      {len(question):,} chars")
print(f"  rca_content length:   {len(RCA_CONTENT):,} chars")
print(f"  full_question length: {len(full_question):,} chars")


# ═══════════════════════════════════════════════════════════════════
# STEP 6: Build the agent prompt template
# ═══════════════════════════════════════════════════════════════════
section("STEP 6: Agent Prompt (what the LLM actually gets)")

doc_clues = format_doc_clues_for_prompt(clues_data_agent, selected_terms=selected_raw_terms, product_name=PRODUCT_NAME)

doc_clues_section = ""
if doc_clues:
    doc_clues_section = f"\n\n{doc_clues}\n"

guide_filter_message = ""
if selected_guides:
    guides_list = ', '.join(selected_guides)
    guide_filter_message = f"""

🎯 SEARCH SCOPE LIMITATION:
The user has selected specific guides to search. You MUST limit your search to these guides only:
{guides_list}

When calling get_product_info, the results will automatically be filtered to these guides.
"""

# ── Build pinned recs (replicate run_agent logic) ──
def _section_hints_for_guide(guide_name):
    """Get the top term-based section hints for a specific guide."""
    if not matched_term_guides:
        return None
    tw = []
    for term, guides in matched_term_guides.items():
        if term.startswith('_'):
            continue
        if guide_name in guides:
            w = 1.0 / len(guides)
            tw.append((term, w))
    tw.sort(key=lambda x: -x[1])
    top = [t.title() for t, _ in tw[:5]]
    return ", ".join(top) if top else None

sorted_guides_list = sorted(guide_scores.items(), key=lambda x: -x[1]) if guide_scores else []

pinned_rec_section = ""
rec1_guide = None

if url_clues_agent and section_label and section_label != "(see location recommendations above)":
    rec1_guide = url_clues_agent[0]['book_pdf']
    chapter_query = ' '.join(url_clues_agent[0].get('chapter_clues', []))
    pinned_rec_section = f"""
🔒 MANDATORY LOCATION RECOMMENDATION #1 (from documentation URL — DO NOT SKIP OR REPLACE):
══════════════════════════════════════════════════════════════════════
Document name: {rec1_guide}
Chapter/Section: {section_label}
Page number: <SEARCH THIS GUIDE and fill in>
Actual content location indicator: <SEARCH THIS GUIDE and quote 8-15 words>
Detailed reasoning: The bug/RCA explicitly references this document and chapter via URL.
══════════════════════════════════════════════════════════════════════
🔍 REQUIRED SEARCH: call get_product_info with query targeting "{chapter_query}" in {rec1_guide}
"""
elif top_guide and section_label and section_label != "(see location recommendations above)":
    rec1_guide = top_guide
    pinned_rec_section = f"""
🔒 MANDATORY LOCATION RECOMMENDATION #1 (highest scoring guide — DO NOT SKIP OR REPLACE):
══════════════════════════════════════════════════════════════════════
Document name: {rec1_guide}
Likely section topics: {section_label}
Page number: <SEARCH THIS GUIDE and fill in>
Actual content location indicator: <SEARCH THIS GUIDE and quote 8-15 words>
Detailed reasoning: This guide scored highest ({guide_scores.get(rec1_guide, 'n/a')}) based on detected technology terms.
══════════════════════════════════════════════════════════════════════
🔍 REQUIRED SEARCH: call get_product_info with query targeting "{section_label}" in {rec1_guide}
"""

# Mandatory #2 and #3
remaining = [(g, s) for g, s in sorted_guides_list if g != rec1_guide]
for rank, (gname, gscore) in enumerate(remaining[:2], start=2):
    hints = _section_hints_for_guide(gname)
    hint_text = hints if hints else "(search this guide for relevant sections)"
    pinned_rec_section += f"""
🔒 MANDATORY LOCATION RECOMMENDATION #{rank} (DO NOT SKIP — search this DIFFERENT guide):
══════════════════════════════════════════════════════════════════════
Document name: {gname}
Likely section topics: {hint_text}
Page number: <SEARCH THIS GUIDE and fill in>
Actual content location indicator: <SEARCH THIS GUIDE and quote 8-15 words>
Detailed reasoning: This guide scored #{rank} ({gscore}) based on detected technology terms matching: {hint_text}
══════════════════════════════════════════════════════════════════════
🔍 REQUIRED SEARCH: call get_product_info with query targeting "{hint_text}" in {gname}
"""

# Build the PromptTemplate equivalent
product_version_prompt = f"""
given a Cisco product name and a question from a user, return the answer.
Use your tools to fetch context to answer the question to provide a more accurate answer.

Cisco product: {PRODUCT_NAME}
{doc_clues_section}
{pinned_rec_section}
question: {full_question[:500]}...

[FULL QUESTION TRUNCATED — {len(full_question):,} chars total]
{guide_filter_message}

🚨 MANDATORY FIRST ACTIONS (before anything else):
1. If � MANDATORY LOCATION RECOMMENDATIONS appear above, you MUST make a SEPARATE get_product_info call
   for EACH of the 3 guides listed. Do NOT skip any. Do NOT combine searches. 3 guides = 3 separate searches.
2. Your final Location Recommendations #1, #2, #3 MUST match the 3 mandatory guides above — same order, same guides.
3. If SUGGESTED SEARCH QUERIES (🔍) are listed, use THOSE EXACT queries
4. Use the "Book PDF" name as your primary search source filter
5. Only AFTER exhausting the suggested queries, try your own search terms

answer:
"""

# Show the prompt (doc_clues section can be huge, so show separately)
print(product_version_prompt[:3000])
if len(product_version_prompt) > 3000:
    print(f"\n... [doc_clues section truncated]")

# Always show pinned recommendations clearly
if pinned_rec_section.strip():
    section("STEP 6b: Pinned Location Recommendations (sent to LLM)")
    print(pinned_rec_section)
else:
    print("\n⚠️  No pinned recommendations generated (missing URL clues and guide scores)")


# ═══════════════════════════════════════════════════════════════════
# STEP 7: (Optional) Run the actual LLM call
# ═══════════════════════════════════════════════════════════════════
if not SKIP_LLM:
    section("STEP 7: Actual LLM Call")
    print("Calling run_agent() — this will make real API calls...")
    print("(Use --no-llm flag to skip this step)\n")

    # We need to fake st.session_state since we're not in Streamlit
    import unittest.mock
    mock_session = {
        '_guide_scores': guide_scores,
        '_matched_term_guides': matched_term_guides,
        'selected_guides_for_search': selected_guides,
        'selected_model': 'gpt-4o',  # Model selection — change to test Claude/Gemini
    }

    # Patch streamlit session_state
    import streamlit as st
    for k, v in mock_session.items():
        st.session_state[k] = v

    try:
        from app_functions import run_agent
        result = run_agent(PRODUCT_NAME, open("BugAnalyze.md").read(), RCA_CONTENT, selected_guides, selected_raw_terms)

        section("STEP 8: LLM OUTPUT")
        output = result.get('output', str(result))
        print(output)

        # Check what the LLM said for Recommended Guide
        section("STEP 9: Checking LLM's Recommended Guide")
        for line in output.split('\n'):
            stripped = line.strip()
            if any(k in stripped.lower() for k in ['recommended guide', 'recommended section', 'recommended format']):
                print(f"  {stripped}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
else:
    section("STEP 7: Skipped (--no-llm)")
    print("Run without --no-llm to make actual LLM calls")

print(f"\n{'='*70}")
print("  Debug complete!")
print(f"{'='*70}")
