# <span id="page-84-0"></span>3.0 CXL Transaction Layer

## <span id="page-84-1"></span>3.1 CXL.io

<span id="page-84-3"></span>CXL.io provides a non-coherent load/store interface for I/O devices. [Figure 3-1](#page-84-2) shows where the CXL.io transaction layer exists in the Flex Bus layered hierarchy. Transaction types, transaction packet formatting, credit-based flow control, virtual channel management, and transaction ordering rules follow the PCIe\* definition; please refer to the "Transaction Layer Specification" chapter of PCIe Base Specification for details. This chapter highlights notable PCIe modes or features that are used for CXL.io.

<span id="page-84-2"></span>**Figure 3-1. Flex Bus Layers - CXL.io Transaction Layer Highlighted**

![](_page_84_Figure_6.jpeg)

![](_page_85_Picture_1.jpeg)

### <span id="page-85-0"></span>3.1.1 CXL.io Endpoint

The CXL Alternate Protocol negotiation determines the mode of operation. See [Section 9.11](#page-814-4) and [Section 9.12](#page-822-2) for descriptions of how CXL devices are enumerated with the help of CXL.io.

A Function on a CXL device must not generate INTx messages if that Function participates in CXL.cache protocol or CXL.mem protocols. A Non-CXL Function Map DVSEC (see [Section 8.1.4](#page-513-3)) enumerates functions that do not participate in CXL.cache or CXL.mem. Even though not recommended, these non-CXL functions are permitted to generate INTx messages.

Functions associated with an LD within an MLD component, including non-CXL functions, are not permitted to generate INTx messages.

### <span id="page-85-1"></span>3.1.2 CXL Power Management VDM Format

The CXL power management messages are sent as PCIe Vendor Defined Type 0 messages with a 4-DWORD data payload. These include the PMREQ, PMRSP, and PMGO messages. [Figure 3-2](#page-86-0) and [Figure 3-3](#page-86-1) provide the format for the CXL PM VDMs. The following are the characteristics of these messages:

- Fmt and Type fields are set to indicate message with data. All messages use routing of "Local-Terminate at Receiver." Message Code is set to Vendor Defined Type 0.
- Vendor ID field is set to 1E98h1.
- Byte 15 of the message header contains the VDM Code and is set to the value of "CXL PM Message" (68h).
- The 4-DWORD Data Payload contains the CXL PM Logical Opcode (e.g., PMREQ, GPF) and any other information related to the CXL PM message. Details of fields within the Data Payload are described in [Table 3-1.](#page-87-0)

If a CXL component receives PM VDM with poison (EP=1), the receiver shall drop such a message. Because the receiver is able to continue regular operation after receiving such a VDM, it shall treat this event as an advisory non-fatal error.

If the receiver Power Management Unit (PMU) does not understand the contents of PM VDM Payload, it shall silently drop that message and shall not signal an uncorrectable error.

<sup>1.</sup> **NOTICE TO USERS**: THE UNIQUE VALUE THAT IS PROVIDED IN THIS CXL SPECIFICATION IS FOR USE IN VENDOR DEFINED MESSAGE FIELDS, DESIGNATED VENDOR SPECIFIC EXTENDED CAPABILITIES, AND ALTERNATE PROTOCOL NEGOTIATION ONLY AND MAY NOT BE USED IN ANY OTHER MANNER, AND A USER OF THE UNIQUE VALUE MAY NOT USE THE UNIQUE VALUE IN A MANNER THAT (A) ALTERS, MODIFIES, HARMS OR DAMAGES THE TECHNICAL FUNCTIONING, SAFETY OR SECURITY OF THE PCI-SIG ECOSYSTEM OR ANY PORTION THEREOF, OR (B) COULD OR WOULD REASONABLY BE DETERMINED TO ALTER, MODIFY, HARM OR DAMAGE THE TECHNICAL FUNCTIONING, SAFETY OR SECURITY OF THE PCI-SIG ECOSYSTEM OR ANY PORTION THEREOF (FOR PURPOSES OF THIS NOTICE, "**PCI-SIG ECOSYSTEM**" MEANS THE PCI-SIG SPECIFICATIONS, MEMBERS OF PCI-SIG AND THEIR ASSOCIATED PRODUCTS AND SERVICES THAT INCORPORATE ALL OR A PORTION OF A PCI-SIG SPECIFICATION AND EXTENDS TO THOSE PRODUCTS AND SERVICES INTERFACING WITH PCI-SIG MEMBER PRODUCTS AND SERVICES).

<span id="page-86-0"></span>**Figure 3-2. CXL Power Management Messages Packet Format - Non-Flit Mode**

| 1                     | +0 +1 +2 +3                                    |                  |                               |      |      |     |   |          |        |   |                |      |        |                   |     |        |        |                                                       |     |                |         |      |   |   |                                        |     |     |     |      |      |     |   |   |
|-----------------------|------------------------------------------------|------------------|-------------------------------|------|------|-----|---|----------|--------|---|----------------|------|--------|-------------------|-----|--------|--------|-------------------------------------------------------|-----|----------------|---------|------|---|---|----------------------------------------|-----|-----|-----|------|------|-----|---|---|
|                       |                                                |                  |                               | +0   | )    |     |   |          | +1     |   |                |      |        |                   |     |        | +2     |                                                       |     |                |         |      |   |   |                                        | +3  |     |     |      |      |     |   |   |
|                       | 7                                              | 6                | 5 .                           | 4    | 3    | 2   | 1 | 0        | 7      | 6 | 5              | 4    | 3      | 2                 | 1   | 0      | 7      | 6                                                     | 5   | 4              | 3       | 2    | 1 | 0 |                                        | 7 6 | 5 5 |     | 4 3  | 3    | 2 / | П | 0 |
|                       |                                                | Fmt<br>011b      | I                             |      | _    | ype | ; | ⊣ | T<br>9 |   | tc             |      | T<br>8 | A<br>tt<br>r      | R   | T<br>H | T<br>D | E<br>P                                                | A   |                | A<br>00 | T    |   |   | 1                                      |     | Le  | ng  |      |      |     |   |   |
| PCle<br>VDM<br>Type 0 |                                                | Requester ID Tag |                               |      |      |     |   |          |        |   |                |      |        |                   |     |        |        | Message Code<br>Vendor Defined Type 0<br>= 0111 1110b |     |                |         |      |   |   |                                        |     |     |     |      |      |     |   |   |
| Header                |                                                | December 4       |                               |      |      |     |   |          |        |   |                |      |        |                   |     |        |        | ndorID<br>= 1E98h                                     |     |                |         |      |   |   |                                        |     |     |     |      |      |     |   |   |
|                       |                                                | Reserved         |                               |      |      |     |   |          |        |   |                |      |        |                   |     |        |        |                                                       |     |                |         |      |   |   | CXL VDM Code = CXL<br>PM Message = 68h |     |     |     |      |      |     |   |   |
|                       | PM Logical Opcode R PM Agent ID Parameter[7:0] |                  |                               |      |      |     |   |          |        |   |                | Par  | an     | netei             | r[1 | 5:8]   |        |                                                       |     |                |         |      |   |   |                                        |     |     |     |      |      |     |   |   |
| 4<br>DWORDs           |                                                | Payload[7:0]     |                               |      |      |     |   |          |        |   | Pa             | /loa | ıd[1   | 5:8]              |     |        |        |                                                       | Pay | load           | 1[23    | :16] | ] |   |                                        |     | Pa  | ylo | ad[3 | 31:2 | 24] |   |   |
| of Data<br>Payload    |                                                | P                | aylc                          | oad[ | [39: | 32] |   |          |        |   | Pay            | load | d[47   | ':40 <sub>.</sub> | ]   |        |        |                                                       | Pay | load           | d[55    | :48] | ] |   |                                        |     | Pa  | ylo | ad[6 | 3:   | 56] |   |   |
|                       |                                                | P                | Payload[71:64] Payload[79:72] |      |      |     |   |          |        |   | Payload[87:80] |      |        |                   |     |        |        |                                                       |     | Payload[95:88] |         |      |   |   |                                        |     |     |     |      |      |     |   |   |

**Figure 3-3.**

<span id="page-86-1"></span>Figure 3-3. CXL Power Management Messages Packet Format - Flit Mode

![](_page_86_Figure_5.jpeg)

<span id="page-87-1"></span><span id="page-87-0"></span>**Table 3-1. CXL Power Management Messages - Data Payload Field Definitions (Sheet 1 of 2)**

| Field                  | Description                                                                                                                                                                                                                                                                                                                                                                                         | Notes                                                                                |
|------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------|
| PM Logical Opcode[7:0] | Power Management Command<br>•<br>00h = AGENT_INFO<br>•<br>02h = RESETPREP<br>•<br>04h = PMREQ (PMRSP and PMGO)<br>•<br>06h = Global Persistent Flush (GPF)<br>•<br>FEh = CREDIT_RTN                                                                                                                                                                                                                 |                                                                                      |
| PM Agent ID[6:0]       | PM2IP: Reserved.<br>IP2PM: PM agent ID assigned to the device.<br>Host communicates the PM Agent ID to device via the<br>TARGET_AGENT_ID field of the first CREDIT_RTN<br>message.                                                                                                                                                                                                                  | A device does not consume<br>this value when it receives<br>a message from the Host. |
| Parameter[15:0]        | CREDIT_RTN (PM2IP and IP2PM): Reserved.<br>AGENT_INFO (PM2IP and IP2PM)<br>•<br>Bit[0]: REQUEST (set) /RESPONSE_N (cleared)<br>•<br>Bits[7:1]: INDEX<br>•<br>Bits[15:8]: Reserved<br>PMREQ (PM2IP and IP2PM)<br>•<br>Bit[0]: REQUEST (set) /RESPONSE_N (cleared)<br>•<br>Bit[2]: GO<br>•<br>Bits[15:3]: Reserved<br>RESETPREP (PM2IP and IP2PM)<br>•<br>Bit[0]: REQUEST (set) /RESPONSE_N (cleared) |                                                                                      |
|                        | •<br>Bits[15:1]: Reserved<br>GPF (PM2IP and IP2PM)<br>•<br>Bit[0]: REQUEST (set) /RESPONSE_N (cleared)<br>•<br>Bits[15:1]: Reserved                                                                                                                                                                                                                                                                 |                                                                                      |

**Table 3-1. CXL Power Management Messages - Data Payload Field Definitions (Sheet 2 of 2)**

| Field         | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | Notes                                                                                                                                                                                     |
|---------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Payload[95:0] | CREDIT_RTN<br>•<br>Bits[7:0]: NUM_CREDITS (PM2IP and IP2PM)<br>•<br>Bits[14:8]: TARGET_AGENT_ID (Valid during<br>the first PM2IP message, reserved in all other<br>cases)<br>•<br>Bit[15]: Reserved<br>AGENT_INFO (Request and Response)<br>If Param.Index == 0:<br>•<br>Bits[7:0]: CAPABILITY_VECTOR<br>— Bit[0]: Always set to indicate support for<br>PM messages defined in CXL 1.1 spec<br>— Bit[1]: Support for GPF messages<br>— Bits[7:2]: Reserved<br>•<br>All other bits are reserved<br>else: All reserved<br>•<br>All bits are reserved<br>RESETPREP (Request and Response)<br>•<br>Bits[7:0]: ResetType<br>— 01h = System transition from S0 to S1<br>— 03h = System transition from S0 to S3<br>— 04h = System transition from S0 to S4<br>— 05h = System transition from S0 to S5<br>— 10h = System reset<br>•<br>Bits[15:8]: PrepType<br>— 00h = General Prep<br>— All other encodings are reserved<br>•<br>Bits[17:16]: Reserved<br>•<br>All other bits are reserved<br>PMREQ<br>•<br>Bits[31:0]: PCIe LTR format (as defined in Bytes<br>12-15 of PCIe LTR message, see Table 3-2)<br>•<br>All other bits are reserved<br>GPF<br>•<br>Bits[7:0]: GPFType<br>— Bit[0]: Set to indicate that a power failure<br>is imminent. Only valid for Phase 1 request<br>messages.<br>— Bit[1]: Set to indicate device must flush its<br>caches. Only valid for Phase 1 request<br>messages.<br>— Bits[7:2]: Reserved<br>•<br>Bits[15:8]: GPF Status<br>— Bit[8]: Set to indicate that the Cache Flush<br>phase encountered an error. Only valid for<br>Phase 1 responses and Phase 2 requests.<br>— Bits[15:9]: Reserved<br>•<br>Bits[17:16]: Phase | CXL Agent must treat the<br>TARGET_AGENT_ID field<br>as reserved when<br>returning credits to Host.<br>Only Index 0 is defined for<br>AGENT_INFO. All other<br>Index values are reserved. |
|               | — 01h = Phase 1<br>— 02h = Phase 2<br>— All other encodings are reserved<br>•<br>All other bits are reserved                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |                                                                                                                                                                                           |

<span id="page-89-2"></span>**Table 3-2. PMREQ Field Definitions**

| Payload Bit Position | LTR Field              |
|----------------------|------------------------|
| [31:24]              | Snoop Latency[7:0]     |
| [23:16]              | Snoop Latency[15:8]    |
| [15:8]               | No-Snoop Latency[7:0]  |
| [7:0]                | No-Snoop Latency[15:8] |

#### <span id="page-89-0"></span>3.1.2.1 Credit and PM Initialization

PM Credits and initialization process is link local. [Figure 3-4](#page-89-1) illustrates the use of PM2IP.CREDIT\_RTN and PM2IP.AGENT\_INFO messages to initialize Power Management messaging protocol intended to facilitate communication between the Downstream Port PMU and the Upstream Port PMU. A CXL switch provides an aggregation function for PM messages as described in [Section 9.1.2.1.](#page-799-5)

GPF messages do not require credits and the receiver shall not generate CREDIT\_RTN in response to GPF messages.

<span id="page-89-1"></span>**Figure 3-4. Power Management Credits and Initialization**

<span id="page-89-3"></span>![](_page_89_Figure_8.jpeg)

The CXL Upstream Port PMU must be able to receive and process CREDIT\_RTN messages without dependency on any other PM2IP messages. Also, CREDIT\_RTN messages do not use a credit. The CREDIT\_RTN messages are used to initialize and update the Tx credits on each side, so that flow control can be appropriately managed. During the first CREDIT\_RTN message during PM Initialization, the credits being sent via NUM\_CREDITS field represent the number of credit-dependent PM messages that the initiator of CREDIT\_RTN can receive from the other end. During the subsequent CREDIT\_RTN messages, the NUM\_CREDITS field represents the number of PM credits that were freed up since the last CREDIT\_RTN message in the same direction. The first CREDIT\_RTN message is also used by the Downstream Port PMU to assign a PM\_AGENT\_ID to the Upstream Port PMU. This ID is communicated via the TARGET\_AGENT\_ID field in the CREDIT\_RTN message. The Upstream Port PMU must wait for the CREDIT\_RTN message from the Downstream Port PMU before initiating any IP2PM messages.

An Upstream Port PMU must support at least one credit, where a credit implies having sufficient buffering to sink a PM2IP message with 128 bits of payload.

After credit initialization, the Upstream Port PMU must wait for an AGENT\_INFO message from the Downstream Port PMU. This message contains the CAPABILITY\_VECTOR of the PM protocol of the Downstream Port PMU. Upstream Port PMU must send its CAPABILITY\_VECTOR to the Downstream Port PMU in response to the AGENT\_INFO Req from the Downstream Port PMU. When there is a mismatch, Downstream Port PMU may implement a compatibility mode to work with a less capable Upstream Port PMU. Alternatively, Downstream Port PMU may log the mismatch and report an error, if it does not know how to reliably function with a less capable Upstream Port PMU.

There is an expectation from the Upstream Port PMU that it restores credits to the Downstream Port PMU as soon as a message is received. Downstream Port PMU can have multiple messages in flight, if it was provided with multiple credits. Releasing credits in a timely manner provides better performance for latency sensitive flows.

The following list summarizes the rules that must be followed by an Upstream Port PMU:

- Upstream Port PMU must wait to receive a PM2IP.CREDIT\_RTN message before initiating any IP2PM messages.
- Upstream Port PMU must extract TARGET\_AGENT\_ID field from the first PM2IP message received from the Downstream Port PMU and use that as its PM\_AGENT\_ID in future messages.
- Upstream Port PMU must implement enough resources to sink and process any CREDIT\_RTN messages without dependency on any other PM2IP or IP2PM messages or other message classes.
- Upstream Port PMU must implement at least one credit to sink a PM2IP message.
- Upstream Port PMU must return any credits to the Downstream Port PMU as soon as possible to prevent blocking of PM message communication over CXL Link.
- Upstream Port PMU are recommended to not withhold a credit for longer than 10 us.

### <span id="page-90-0"></span>3.1.3 CXL Error VDM Format

The CXL Error Messages are sent as PCIe Vendor Defined Type 0 messages with no data payload. Presently, this class includes a single type of message, namely Event Firmware Notification (EFN). When EFN is utilized to report memory errors, it is referred to as Memory Error Firmware Notification (MEFN). [Figure 3-5](#page-91-2) and [Figure 3-6](#page-91-3) provide the format for EFN messages.

The following are the characteristics of the EFN message:

- Fmt and Type fields are set to indicate message with no data.
- The message is sent using routing of "Routed to Root Complex." It is always initiated by a device.
- Message Code is set to Vendor Defined Type 0.
- Vendor ID field is set to 1E98h.
- Byte 15 of the message header contains the VDM Code and is set to the value of "CXL Error Message" (00h).
- Bytes 8, 9, 12, and 13 are cleared to all 0s.
- Bits[7:4] of Byte 14 are cleared to 0h. Bits[3:0] of Byte 14 are used to communicate the Firmware Interrupt Vector (abbreviated as FW Interrupt Vector in [Figure 3-5](#page-91-2) and [Figure 3-6\)](#page-91-3).

**Figure 3-5.**

<span id="page-91-2"></span>Figure 3-5. CXL EFN Messages Packet Format - Non-Flit Mode

![](_page_91_Figure_3.jpeg)

<span id="page-91-3"></span>**Figure 3-6. CXL EFN Messages Packet Format - Flit Mode**

![](_page_91_Figure_5.jpeg)

Encoding of the FW Interrupt Vector field is Host specific and thus not defined by the CXL specification. A Host may support more than one type of Firmware environment and this field may be used to indicate to the Host which one of these environments is to process this message.

### <span id="page-91-0"></span>3.1.4 Optional PCIe Features Required for CXL

Table 3-3 lists optional features per PCIe Base Specification that are required for CXL.

<span id="page-91-4"></span>**Table 3-3. Optional PCIe Features Required for CXL**

| Optional PCIe Feature          | Notes                                                                                                        |
|--------------------------------|--------------------------------------------------------------------------------------------------------------|
| Data Poisoning by transmitter  |                                                                                                              |
| ATS                            | Only required if CXL.cache is present (e.g., only for Type 1 and Type 2 devices, but not for Type 3 devices) |
| Advanced Error Reporting (AER) |                                                                                                              |

### <span id="page-91-1"></span>3.1.5 Error Propagation

CXL.cache and CXL.mem errors detected by the device are propagated Upstream over the CXL.io traffic stream. These errors are logged as correctable and uncorrectable internal errors in the PCIe AER registers of the detecting component.

### <span id="page-92-0"></span>3.1.6 Memory Type Indication on ATS

Requests to certain memory regions can only be issued on CXL.io and cannot be issued on CXL.cache. It is up to the host to decide what these memory regions are. For example, on x86 systems, the host may choose to restrict access only to Uncacheable (UC) type memory over CXL.io. The host indicates such regions by means of an indication on ATS completion to the device.

All CXL functions that issue ATS requests must set the Page Aligned Request bit in the ATS Capability register to 1. In addition, ATS requests sourced from a CXL device must set the CXL Src bit.

<span id="page-92-3"></span>**Figure 3-7. ATS 64-bit Request with CXL Indication - Non-Flit Mode**

| ATTR         |  |  |   |  |  |  |     |  | b |  | b |  |  |  |  |  |  |  |  |  |  |   |  |  |  |  |   |  |  |  |  |  |
|--------------|--|--|---|--|--|--|-----|--|---|--|---|--|--|--|--|--|--|--|--|--|--|---|--|--|--|--|---|--|--|--|--|--|
| Requester ID |  |  |   |  |  |  |     |  |   |  |   |  |  |  |  |  |  |  |  |  |  | b |  |  |  |  |   |  |  |  |  |  |
|              |  |  |   |  |  |  |     |  |   |  |   |  |  |  |  |  |  |  |  |  |  |   |  |  |  |  |   |  |  |  |  |  |
|              |  |  |   |  |  |  |     |  |   |  |   |  |  |  |  |  |  |  |  |  |  |   |  |  |  |  |   |  |  |  |  |  |
|              |  |  | b |  |  |  | b _ |  |   |  |   |  |  |  |  |  |  |  |  |  |  |   |  |  |  |  | b |  |  |  |  |  |

DWORD3, Byte 3, Bit 3 in ATS 64-bit request and ATS 32-bit request for both Flit Mode and Non-Flit Mode carries the CXL Src bit. [Figure 3-7](#page-92-3) shows the position of this bit in ATS 64-bit request (Non-Flit mode). See PCIe Base Specification for the format of the other request messages. The CXL Src bit is defined as follows:

- 0 = Indicates request initiated by a Function that does not support CXL.io Indication on ATS.
- 1 = Indicates request initiated by a Function that supports CXL.io Indication on ATS. All CXL Functions must set this bit.

*Note:* This bit is Reserved in the ATS request as defined by PCIe Base Specification.

ATS translation completion from the Host carries the CXL.io bit in the Translation Completion Data Entry. See PCIe Base Specification for the message formats.

The CXL.io bit in the ATS Translation completion is valid when the CXL Src bit in the request is set. The CXL.io bit is as defined as follows:

- 0 = Requests to the page can be issued on all CXL protocols.
<span id="page-92-4"></span>- • 1 = Requests to the page can be issued by the Function on CXL.io only. It is a violation to issue requests to the page using CXL.cache protocol.

### <span id="page-92-1"></span>3.1.7 Deferrable Writes

<span id="page-92-5"></span>Earlier revisions of this specification captured the "Deferrable Writes" extension to the CXL.io protocol, but this protocol has been adopted by PCIe Base Specification.

### <span id="page-92-2"></span>3.1.8 PBR TLP Header (PTH)

On PBR links in a PBR fabric, all .io TLPs, with exception of NOP-TLP, carry a fixed 1- DWORD header field called the PBR TLP header (PTH). PBR links are either Inter-Switch Links (ISL) or edge links from PBR switch to G-FAM. See [Section 7.7.8](#page-441-3) for details of where this header is inserted and deleted when the .io TLP traverses the PBR fabric from source to target.

NOP-TLPs are always transmitted without a preceding PTH. For Non-NOP-TLPs, PTH is always transmitted and it is transmitted on the immediate DWORD preceding the TLP Header base. Local-prefixes, if any, associated with a TLP are always transmitted before the PTH is transmitted. This is pictorially shown in [Figure 3-8](#page-95-1).

To assist the receiver on a PBR link from disambiguating PTH from an NOP-TLP/Local-Prefix, the PCIe flit mode TLP grammar is modified as follows. Bits[7:6] of the first byte of all DWORDs, from the 1st DWORD of a TLP until a PTH is detected, are encoded as follows:

- 00b = NOP-TLP
- 01b = Rsvd
- 10b = Local Prefix
- 11b = PTH

After the receiver detects a PTH, PCIe TLP grammar rules are applied per PCIe Base Specification until the TLP ends, with the restriction that NOP-TLP and Local prefix cannot be transmitted in this region of the TLP.

#### <span id="page-93-0"></span>3.1.8.1 Transmitter Rules Summary

- For NOP-TLP and Local-Prefix *Type*1 field encodings, no PTH is pre-pended
- For all other *Type*[1](#page-93-2) field encodings, a PTH is pre-pended immediately ahead of the Header base

#### <span id="page-93-1"></span>3.1.8.2 Receiver Rules Summary

- For NOP-TLP, if bits[5:0] are not all 0s, the receiver treats it as a malformed packet and reports the error following the associated error reporting rules
- For a Local Prefix, if bits[5:0] are not one of 00 1101b through 00 1111b, the receiver treats it as a malformed packet and reports the error following the associated error reporting rules
- From beginning of a TLP to when a PTH is detected, receiver silently drops a DWORD if a reserved value of 01b is received for bits[7:6] in the DWORD
- If an NOP-TLP or Local Prefix is received immediately after a PTH, the receiver treats it as a malformed packet and reports the error following the associated error reporting rules

*Note:* Header queues in PBR switches/devices should be able to handle the additional DWORD of PTH that is needed to be carried between the source and target PBR links.

*Note:* PTH is included as part of normal link level CRC/FEC calculations/checks on PBR links to ensure reliable PTH delivery over the PBR link. For details regarding the PIF, DSAR, and Hie bits, see [Section 7.7.3.3](#page-408-3), [Section 7.7.7,](#page-438-3) and [Section 7.7.6.2](#page-416-2).

> On MLD links, in the egress direction, the SPID information in this header is used to generate the LD-ID information on VendPrefixL0 message as defined in [Section 2.4](#page-76-4). On MLD links, in the ingress direction, LD-ID in the VendPrefixL0 message is used to determine the DPID in the PBR packet.

<span id="page-93-2"></span><sup>1.</sup> Type[7:0] field as defined in PCIe Base Specification for Flit mode.

<span id="page-94-0"></span>**Table 3-4. PBR TLP Header (PTH) Format**

| Byte      |   |   |   |      | +0 |             |                  |             |   |   |   |   | +1 |            |   |   |   |   |   |   | +2 |   |   |   |   |   |            |   | +3 |   |   |   |
|-----------|---|---|---|------|----|-------------|------------------|-------------|---|---|---|---|----|------------|---|---|---|---|---|---|----|---|---|---|---|---|------------|---|----|---|---|---|
| Bits      | 7 | 6 | 5 | 4    | 3  | 2           | 1                | 0           | 7 | 6 | 5 | 4 | 3  | 2          | 1 | 0 | 7 | 6 | 5 | 4 | 3  | 2 | 1 | 0 | 7 | 6 | 5          | 4 | 3  | 2 | 1 | 0 |
| Byte 0 -> | 1 | 1 |   | Rsvd |    | Hie | DSAR | PIF |   |   |   |   |    | SPID[11:0] |   |   |   |   |   |   |    |   |   |   |   |   | DPID[11:0] |   |    |   |   |   |

<span id="page-94-1"></span>**Table 3-5. NOP-TLP Header Format**

| Byte      |                                                     |  |  |  | +0 |  |  |  |   |   |   |   | +1 |   |   |   |   |   |   |   | +2 |   |   |   |   |   |   | +3 |   |  |  |  |
|-----------|-----------------------------------------------------|--|--|--|----|--|--|--|---|---|---|---|----|---|---|---|---|---|---|---|----|---|---|---|---|---|---|----|---|--|--|--|
| Bits      | 765432<br>10765 |  |  |  |    |  |  |  | 4 | 3 | 2 | 1 | 0  | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0  | 7 | 6 | 5 | 4 | 3 | 2 | 1  | 0 |  |  |  |
| Byte 0 -> | 0<br>0<br>00 0000b<br>Per PCIe Base Specification   |  |  |  |    |  |  |  |   |   |   |   |    |   |   |   |   |   |   |   |    |   |   |   |   |   |   |    |   |  |  |  |

<span id="page-94-2"></span>**Table 3-6. Local Prefix Header Format**

| Byte      |   |   |   |   | +0 |   |   |                     | +1 |   |   |   |   |   |   |   |   |   |                             |   | +2 |   |   |   |   |   |   |   | +3 |   |   |   |
|-----------|---|---|---|---|----|---|---|---------------------|----|---|---|---|---|---|---|---|---|---|-----------------------------|---|----|---|---|---|---|---|---|---|----|---|---|---|
| Bits      | 7 | 6 | 5 | 4 | 3  | 2 | 1 | 0                   | 7  | 6 | 5 | 4 | 3 | 2 | 1 | 0 | 7 | 6 | 5                           | 4 | 3  | 2 | 1 | 0 | 7 | 6 | 5 | 4 | 3  | 2 | 1 | 0 |
| Byte 0 -> | 1 | 0 | 0 | 0 | 1  | 1 |   | 01b/<br>10b/<br>11b |    |   |   |   |   |   |   |   |   |   | Per PCIe Base Specification |   |    |   |   |   |   |   |   |   |    |   |   |   |

<span id="page-95-1"></span>**Figure 3-8. Valid .io TLP Formats on PBR Links**

### <span id="page-95-0"></span>3.1.9 VendPrefixL0

[Section 2.4.1.2](#page-76-5) describes VendPrefixL0 usage on MLD links. For non-MLD HBR links, VendPrefixL0 carries the PBR-ID field to facilitate inter-domain communication between hosts and devices (e.g., GIM; see [Section 7.7.3](#page-405-1)) and other vendor-proprietary usages (see [Section 7.7.4](#page-411-2)). HBR links that use this form of the prefix must be directly attached to a PBR switch. On the switch ingress side, this prefix carries the DPID of the target edge link. On the egress side, this message carries the SPID of the source link that originated the TLP. The prefix format is shown in [Table 3-51.](#page-160-1)

<span id="page-95-2"></span>**Table 3-7. VendPrefixL0 on Non-MLD Edge HBR Links**

![](_page_95_Figure_7.jpeg)

On the switch side, handling of this prefix is disabled by default. The FM can enable this functionality on each edge USP and DSP, via CCI mailbox. The method that the FM uses to determine the set of USPs/DSPs that are capable and trustworthy of enabling this functionality is beyond the scope of this specification.

*Note:* Edge PCIe links are not precluded from using this prefix for the same purpose described above. However, such usages are beyond the scope of this specification.

> See [Section 7.7.3](#page-405-1) and [Section 7.7.4](#page-411-2) for transaction flows that involve TLPs with this prefix.

### <span id="page-96-0"></span>3.1.10 CXL DevLoad (CDL) Field in UIO Completions

To support QoS Telemetry (see [Section 3.3.4](#page-137-0)) with UIO Direct P2P to HDM (see [Section 7.7.9](#page-441-4)), UIO Completions contain the 2-bit CDL field, which carries the CXL DevLoad indication from HDM devices that support UIO Direct P2P. If an HDM device supports UIO Direct P2P to HDM, the HDM device shall populate the CDL field with values as defined in [Table 3-51](#page-160-1). The CDL field exists in UIOWrCpl, UIORdCpl, and UIORdCplD TLPs.

### <span id="page-96-1"></span>3.1.11 CXL Fabric-related VDMs

<span id="page-96-3"></span>In CXL Fabric (described in [Section 7.7\)](#page-390-3), there are many different uses for a CXL VDM. The uses fall into two categories: within a PBR Fabric, and outside a PBR Fabric.

When a VDM has a CXL Vendor ID, bytes 14 and 15 in the VDM header distinguish the use case via a CXL VDM Code and whether the use is within a PBR fabric. If within a PBR fabric, there is also a PBR Opcode. Additionally for PBR Fabric CXL VDMs, many of the traditional PCIe-defined fields such as Requester ID have no meaning and thus are reserved or in some cases, repurposed. See [Table 3-8](#page-96-2) for a breakdown of the VDM header bytes for PBR Fabric VDMs.

<span id="page-96-2"></span>**Table 3-8. PBR VDM**

|      |                                                                    | +0<br>+1 |  |  |  |  |  |  |   |             |   |   |        |                                                                                    |                          |        | +2  |   |   |   |        |              |   |   | +3 |  |  |  |
|------|--------------------------------------------------------------------|----------|--|--|--|--|--|--|---|-------------|---|---|--------|------------------------------------------------------------------------------------|--------------------------|--------|-----|---|---|---|--------|--------------|---|---|----|--|--|--|
| Byte | 765431<br>076543<br>2<br>1 |          |  |  |  |  |  |  | 0 | 7           | 6 | 5 | 4      | 3                                                                                  | 2                        | 1      | 0   | 7 | 6 | 5 | 4<br>3 | 2            | 1 | 0 |    |  |  |  |
| 0    | Type 0011 0100b<br>TC<br>OHC<br>Type 0111 0100b<br>000b<br>0 0000b |          |  |  |  |  |  |  |   |             |   |   |        | TS<br>Attr<br>Length 00 0000 0000b<br>Length 00 00xx xxxxb1<br>000b<br>000b        |                          |        |     |   |   |   |        |              |   |   |    |  |  |  |
| 4    | PCIe Requester ID / Rsvd                                           |          |  |  |  |  |  |  |   |             |   |   | P      | Message Code<br>E<br>Vendor Defined<br>Vendor Defined Type 0<br>Rsvd<br>0111 1110b |                          |        |     |   |   |   |        |              |   |   |    |  |  |  |
| 8    | Rsvd                                                               |          |  |  |  |  |  |  |   |             |   |   |        |                                                                                    | Vendor ID<br>CXL = 1E98h |        |     |   |   |   |        |              |   |   |    |  |  |  |
| 12   | SeqLen:<br>Reserved<br>CmdSeq<br>00h = 256 DWORDs                  |          |  |  |  |  |  |  |   | svd | R |   | SeqNum |                                                                                    |                          | Opcode | PBR |   |   |   |        | CXL VDM Code |   |   |    |  |  |  |

<sup>1.</sup> x indicates don't care.

[Table 3-8](#page-96-2) shows two Type encodings, a VDM without data and a VDM with data, both routed as "terminate at receiver". If a payload is not needed, the VDM without data is used. If any payload is required, the VDM with data is used. Because the PBR VDMs use PTH to route, the 'receiver' is the end of the tunnel (i.e., the matching DPID). PBR VDMs with data can have at most 128B (=32 DWORDs) of payload. If the SeqLen is more than 32 DWORDs, multiple VDMs will be needed to convey the entire sequence of VDMs (for UCPull VDM).

Depending on the CXL VDM Code, other fields in the VDM header may have meaning. Use of these additional fields will be defined in the section covering that particular encoding. These fields include:

- PBR Opcode: Subclass of PBR Fabric VDMs
- CmdSeq: Sequence number of the Host management transaction flow
- SeqLen: Length of the VDM sequence, applies to UCPull VDM
- SeqNum: Sequential VDM count with wrap if a message requires multiple sequential VDMs

Table 3-9 summarizes the various CXL vendor defined messages, each with a CXL VDM code and PBR Opcode, a message destination, and a brief summary of the message's use. The CXL VDM Code provides the category of VDM, while the PBR Opcode makes distinctions within that category. The remainder of this section deals with GFD management-related VDMs and Route Table Update related VDMs. For details of other VDMs, see Section 7.7.11.

<span id="page-97-0"></span>Table 3-9. CXL Fabric Vendor Defined Messages

| Message               | USAR/<br>DSAR | CXL VDM<br>Code | PBR<br>Opcode | Destination      | Payload<br>(DWORDs) | Comment                                                       |
|-----------------------|---------------|-----------------|---------------|------------------|---------------------|---------------------------------------------------------------|
| Assert PERST#         | DSAR          | 80h             | 0h            | vUSP             | 0                   | Propagate fundamental reset downstream from vDSP.             |
| Assert Reset          | DSAR          | 80h             | 1h            | vUSP             | 0                   | Propagate hot reset downstream from vDSP.                     |
| Deassert Reset        | DSAR          | 80h             | 3h            | vUSP             | 0                   | Propagate reset deassertion downstream from vDSP.             |
| Link Up               | DSAR          | 80h             | 4h            | vDSP             | 0                   | Send upstream to vDSP, changing link state to L0 from detect. |
| PBR Link Partner Info | DSAR          | 90h             | 0h            | Link Partner     | 16                  | Message with Data. Data saved in recipient.                   |
| DPCmd                 | DSAR          | A0h             | 0             | GFD              | 0                   | Downstream Proxy Command from GAE.                            |
| UCPull                | DSAR          | A1h             | 1             | Host ES          | 0                   | Upstream command pull from GFD.                               |
| DCReq                 | DSAR          | A0h             | 2             | GFD              | 32                  | Downstream Command Request from GAE.                          |
| DCReq-Last            | DSAR          | A0h             | 3             | GFD              | 1 – 32              | Last DCReq.                                                   |
| UCRsp                 | DSAR          | A1h             | 4             | Host ES          | 32                  | Upstream Completion Response from GFD.                        |
| UCRsp-Last            | DSAR          | A1h             | 5             | Host ES          | 1 – 32              | Last UCRsp.                                                   |
| UCRsp-Fail            | DSAR          | A1h             | 6             | Host ES          | 0                   | Failed DCReq receipt.                                         |
| GAM                   | DSAR          | A1h             | 7             | Host ES          | 8                   | GFD log to host.                                              |
| DCReq-Fail            | DSAR          | A0h             | 8             | GFD              | 0                   | Failed UCPull response.                                       |
| RTUpdate              | DSAR          | A1h             | 10h           | Host ES          | 1 – 8               | CacheID bus update from Downstream ES.                        |
| RTUpdateAck           | DSAR          | A1h             | 12h           | Downstream<br>ES | 0                   | Acknowledgment of RTUpdate from Host ES.                      |
| RTUpdateNak           | DSAR          | A1h             | 13h           | Downstream<br>ES | 0                   | Nak for RTUpdate from Host ES.                                |
| CXL PM                | DSAR          | 68h             | 0             | Varies           | 4                   | CXL Power Management.                                         |
| CXL Error             | USAR          | 00h             | 0             | Host             | 0                   | CXL Error.                                                    |

Although they exist outside the PBR Fabric, CXL VDM Codes 00h and 68h are listed to show the complete CXL VDM mapping. Their VDM Header is defined by PCI-SIG and thus does not match the fields provided for a PBR VDM header. These two VDMs will pass through the PBR Fabric using a hierarchical route and using the VDM Header originally defined in Section 3.1.2 for CXL PM and in Section 3.1.3 for CXL Error.

#### <span id="page-98-0"></span>3.1.11.1 Host Management Transaction Flows of GFD

<span id="page-98-2"></span>[Figure 3-9](#page-98-1) summarizes the Host Management Transaction Flows of GFD.

<span id="page-98-1"></span>**Figure 3-9. Host Management Transaction Flows of GFD**

![](_page_98_Figure_5.jpeg)

The Host ES has one GAE per host port. The GAE and GFD communicate via PID-routed VDMs.

Each GAE has an array of active messages, such that a host can communicate with multiple GFDs in parallel. Host software shall ensure that there is only one host-GFD management flow active per host-GFD pair.

The Host-to-GFD message flow consists of the following steps, after first storing the GFD command in host memory:

- 1. Host writes to GAE.
  - Writes pointer to GFD command in host memory (for UCPull read)
  - Writes pointer to write responses from GFD in host memory (for UCRsp data)
  - Writes command length
  - Writes CmdSeq
  - Write a mailbox command doorbell register (see [Section 8.2.9.4.4](#page-626-1)), which causes the GAE to start the host management flow with step [2](#page-99-0)
<span id="page-99-0"></span>- 2. Host ES creates CXL PBR VDM "DPCmd" with command length that targets the GFD PID and CmdSeq to identify the current command sequence.
  - This is an unsolicited message from the GFD point of view, and the GFD must be able to sink one such message for any supported RPID and drop any message from an unsupported RPID
<span id="page-99-3"></span>- 3. GFD responds with a CXL PBR VDM "UCPull", pulling the command for the indicated CmdSeq. The GFD response time may be delayed by responding to other doorbells from other RPIDs.
<span id="page-99-1"></span>- 4. GAE converts CXL PBR VDM "UCPull" to one or more PCIe MRd TLPs.
  - a. GAE sends a series of MRds to read the command, starting at the address pointer supplied to the GAE in the Proxy GFD Management Command input payload. Each MRd size is a maximum of 128B. A command larger than 128B shall require multiple MRd to gather the full command. A total of (Nx) 128B MRd (with N from 0 to 7) and 1x (1B to 128B) MRd is needed to read any command of size up to 1024B.
  - b. The host completes each MRd with one or two CplD TLPs.
<span id="page-99-5"></span><span id="page-99-2"></span>- 5. GAE gathers the read completion data in step [4](#page-99-1)[b](#page-99-2), re-ordering and combining partial completions as needed, to create a VDM payload. The GAE sends a series of DCReq/DCReq-Last VDMs with the completion data as VDM payload in the order that matches the series of MRd in step [4.](#page-99-1) The maximum payload for PBR VDMs is 128B (= 32 DWORDs).
  - Each VDM header contains the following:
    - An incrementing SeqNum, to allow detection of missing messages, starting with 0
    - A CmdSeq, to identify the current command for this Host GFD thread
  - The last VDM in the sequence will be DCReq-Last.
  - VDMs before the last, if needed, will be DCReq.
  - The first VDM in the sequence shall start with a payload that matches the CCI Message header and payload as defined in [Section 7.6.3](#page-346-3). Subsequent VDM's payload shall contain only the remaining payload portion of the CCI Message and not repeat the header.
  - A failed command pull shall result in a DCReq-Fail VDM response instead of any DCReq and DCReq-Last.
<span id="page-99-4"></span>- 6. GFD processes the command after it receives the last VDM (the "DCReq-Last"). The GFD shall send UCRsp/UCRsp-Last VDMs in response to the Host ES.
  - Each VDM header contains the following:
    - An incrementing SeqNum, to allow detection of missing messages, starting with 0
    - A CmdSeq, to identify the current command for this Host GFD thread
  - The last VDM in the sequence will be UCRsp-Last
  - VDMs before the last, if needed, will be UCRsp

- If instead the GFD received DCReq-Fail, a UCRsp-Last shall be sent without processing the (incomplete) command
- 7. GAE converts "UCRsp" and "UCRsp-Last" series to a series of MWr with the payload the same as the VDM payload. The MWr address is supplied to the GAE in the Proxy Command input payload.
  - After the UCRsp-Last payload is written, the GAE mailbox control doorbell described in [Section 8.2.9.4.4](#page-626-1) is cleared. If the MB Doorbell Interrupt is set, an interrupt will be sent by the GAE to the host.

If at any point the GAE disables the GFD access vector, any incoming UCRsp/UCRsp-Last VDMs from the disabled GFD shall be dropped, and any UCPull shall be replied to with a DML-Fail VDM.

The CmdSeq is used to synchronize the GAE and GFD to be working on the same command sequence. A host may issue a subsequent command with a different CmdSeq to abort a prior command that may not have completed the sequence. Both the GAE (step [3](#page-99-3) UCPull and step [6](#page-99-4) UCRsp\*) and the GFD (step [2](#page-99-0) DPCmd and step [5](#page-99-5) DCReq\*) shall check that the command sequence number is the current one for communication with the partner PID (GAE uses GFD's PID, and GFD uses GAE's PID). Any stale command sequence VDM will be dropped and logged. The GFD will always update its current CmdSeq[GAE's PID] based on the value received in step [2](#page-99-0) DPCmd.

The host management flow of a GFD also includes an asynchronous notification from the GFD to inform the host of events in the GFD, using a GAM (GFD Async Message) VDM. The GAM has a payload of up to 32B (8 DWORDs). This payload passes through the GAE to write to an address supplied to the GAE in the Proxy Command input payload. Each GAM write starts at a 32B-aligned offset.

All CXL.io TLPs sent over a PBR link shall have a PTH. The host management flow of GFD VDMs have PTH fields restricted to the following values:

- SPID =
  - From Host ES: Host Edge Port PID
  - From GFD: GFD PID
- DPID =
  - To GFD: GFD PID
  - To Host ES: Host Edge Port PID
- DSAR flag = 1

VDM header fields for GFD Message VDMs:

- CXL VDM code of A0h (to GFD) or A1h (to Host ES)
- PBR Opcode 0 8 to indicate the particular VDM
- **CmdSeq**: Holds the command sequence number issued initially in step [2](#page-99-0), DPCmd.
- **SeqLen**: Holds the length in DWORDs of the subsequent stage DCReq sequence or UCRsp sequence
- **SeqNum**: Holds the sequence number for multi-VDM command or multi-VDM response, starting at 0h and wrapping after 7h back to 0h
- A list of all the CXL VDMs is provided in [Table 3-8](#page-96-2)

#### <span id="page-100-0"></span>3.1.11.2 Downstream Proxy Command (DPCmd) VDM

Initiating a Proxy GFD Management Command on the GAE shall cause the Host ES to create a 'DPCmd' VDM that targets the GFD.

The 'DPCmd' VDM fields are as follows. PTH holds:

- SPID = Host Edge Port PID
- DPID = GFD PID
- DSAR flag = 1

VDM header fields for 'DPCmd' VDMs:

- CXL VDM Code of A0h
- PBR Opcode 0 (DPCmd) DPC
- **CmdSeq**: Current host management command sequence
- **SeqLen**: Command Length (DWORDs, 1 to 256 DWORD max value of 00h is 256 DWORDs)

A 'DPCmd' VDM is an unsolicited message from the GFD point of view. A GFD must be able to successfully record every 'DPCmd' VDM that it receives, up to one from each of its registered RPIDs. The 'DPCmd' VDM is a message without data. The SeqLen part of the VDM header holds the command length that will be pulled by the 'UCPull'.

Only one active DPCmd at a time is allowed per Host Edge Port PID/GFD PID pair. A DPCmd is considered active until the GAE receives a UCRsp-Last VDM in response to a DPCmd.

A GFD should receive only a single active DPCmd per Host PID. If a second DPCmd is received from the same Host PID, the first shall be silently aborted. If a second DPCmd is received before the current DPCmd completes, the GFD updates its current command sequence to the new DPCmd CmdSeq and aborts the prior command sequence.

#### <span id="page-101-0"></span>3.1.11.3 Upstream Command Pull (UCPull) VDM

A GFD shall issue a 'UCPull' VDM when it services a received 'DPCmd' VDM. A single UCPull shall be issued for each DPCmd received, with its command length matching the command length of the DPCmd.

The 'UCPull' VDM fields are as follows. PTH holds:

- SPID = GFD PID
- DPID = Host Edge Port PID
- DSAR flag = 1

VDM header fields for 'UCPull' VDMs:

- CXL VDM Code of A1h
- PBR Opcode 1 (UCPull)
- **CmdSeq**: Matching current command sequence from DPCmd
- **SeqLen**: Length of command to pull (1 to 256 DWORDs)

A GAE must be able to successfully service every 'UCPull' VDM that it receives. The GAE advertises a maximum number of outstanding proxy threads, which defines the maximum number of UCPull VDMs that it would need to track.

A 'UCPull' is a message without data and consists of a single VDM (there is no sequence of UCPulls). The SeqLen field in the VDM header contains the targeted command length to pull from host memory via the GAE. The CmdSeq contains the current command sequence.

![](_page_102_Picture_1.jpeg)

The CmdSeq should be checked to match the current command sequence for the GFD thread; if the CmdSeq does not match, the UCPull is dropped and logged. The UCPull SeqLen shall exactly match the DPCmd SeqLen. The GAE shall issue one or more MRds to pull the command. The last MRd may be 1 to 32 DWORDs. Any prior MRd shall be for exactly 32 DWORDs. The sum of all the MRd lengths shall be the SeqLen.

#### <span id="page-102-0"></span>3.1.11.4 Downstream Command Request (DCReq, DCReq-Last, DCReq-Fail) VDMs

When the Host ES reads the command from host memory in response to a UCPull VDM, the completions for those reads are then conveyed to the GFD over a sequence of zero or more DCReq VDMs plus exactly one DCReq-Last VDM. Each completion payload is copied directly to the VDM payload. The Host ES is responsible for combining any partial completions together to make a single payload for the VDM. Each MRd issued to the host will result, when the CplDs for that MRd all return, in a single DCReq VDM or DCReq-Last VDM. The order of the DCReq/DCReq-Last VDMs shall match the order of the MRd. The DCReq-Last VDM represents the end of the Downstream Command Request series. Any missing DCReq/DCReq-Last VDMs in the sequence should result in the GFD failing the command.

The 'DCReq' / 'DCReq-Last' / 'DCReq-Fail' VDM fields are as follows. PTH holds:

- SPID = Host Edge Port PID
- DPID = GFD PID
- DSAR flag = 1

VDM header fields for 'DCReq' / 'DCReq-Last' / 'DCReq-Fail' VDMs:

- CXL VDM Code of A0h
- PBR Opcode 2 (DCReq) / PBR Opcode 3 (DCReq-Last) / PBR Opcode 8 (DCReq-Fail)
- **CmdSeq**: Command sequence to be checked by Receiver
- **SeqLen**: Defined only for DCReq-Last, holds the expected length of the Response in the next step (UCRsp); 0 for DCReq and DCReq-Fail
- **SeqNum**:
  - Defined for all DCReq and DCReq-Last VDMs, initialized to 0 at the start of the sequence and incremented for each subsequent VDM; 0 of DCReq-Fail
  - Holds the DCReq\* VDM sequence number, starting at 0h and incrementing for each subsequent VDM

Any 'DCReq' VDM shall have a payload of exactly 32 DWORDs. A short command may not have any DCReq VDMs. Every Downstream Command Request sequence shall have exactly one DCReq-Last VDM. The DCReq-Last VDM can have any payload length from 1 to 32 DWORDs.

The DCReq-Last VDM header has SeqLen defined to indicate the next step UCRsp length in DWORDs.

The GFD that is receiving the DCReq\* VDMs checks that the CmdSeq matches its current command sequence for that Host Edge Port PID; if the CmdSeq does not match, the DCReq\* VDM is dropped and logged.

The DCReq-Fail VDM shall be sent if CmdSeq is correct but the PID of the GFD is not enabled in the host's GAE's GMV and a UCPull from that GFD is received.

#### <span id="page-103-0"></span>3.1.11.5 Upstream Command Response (UCRsp, UCRsp-Last, UCRsp-Fail) VDMs

When a GFD receives a 'DCReq-Last' VDM, the GFD checks that the CmdSeq is the current command sequence for that Host Edge Port PID and that all DCReq VDMs and DCReq-Last VDM were received.

If either check fails, the command sequence stops. If all DCReq are not received, as determined by a missing SeqNum, a UCRsp-Fail VDM shall be sent.

If the checks pass, a GFD will issue a 'UCRsp' VDM after the GFD processes the earlierreceived 'DCReq-Last' VDM. The total length of the Response is dictated by the SeqLen provided in the 'DCReq-Last' SeqLen in the VDM header.

There will be zero or more 'UCRsp' VDMs and always exactly one 'UCRsp-Last' VDM, where the 'UCRsp-Last' VDM ends the sequence and is sent last. The sum of the DWORDs of response will match the length requested in the 'DCReq-Last' VDM SeqLen field. Each 'UCRsp' VDM will be 32 DWORDs. The 'UCRsp-Last' VDM can be from 1 to 32 DWORDs. Each 'UCRsp' / 'UCRsp-Last' VDM in the sequence increments the sequence number, starting at 0 and wrapping from 7 back to 0. Any missing UCRsp VDM in the sequence should result in a response error being flagged in the GAE.

The 'UCRsp' / 'UCRsp-Last' / 'UCRsp-Fail' VDM fields are as follows. PTH holds:

- SPID = GFD PID
- DPID = Host Edge Port PID
- DSAR flag = 1

VDM header fields for 'UCRsp' / 'UCRsp-Last' / 'UCRsp-Fail' VDMs:

- CXL VDM Code of A1h
- PBR Opcode 4 (UCRsp) / PBR Opcode 5 (UCRsp-Last) / PBR Opcode 6 (UCRsp-Fail)
- **CmdSeq**: Current command sequence
<span id="page-103-3"></span>- • **SeqNum**: Holds the UCRsp\* VDM sequence number, starting at 0h and incrementing for each subsequent VDM; 0 for UCRsp-Fail

#### <span id="page-103-1"></span>3.1.11.6 GFD Async Message (GAM) VDM

The GAM VDM is used to notify a host of some issue with its use of the GFD. The payload of the GAM should pass through to the host GAM buffer at a 32B-aligned offset. The GAM payload is fixed at 8 DWORDs, as shown in [Table 3-10](#page-103-2).

<span id="page-103-2"></span>**Table 3-10. GAM VDM Payload**

![](_page_103_Figure_19.jpeg)

With multibyte fields, the least significant byte of the field starts with the lowest byte offset, and subsequent bytes are strictly increasing in significance. I.e., this is little endian format within each multibyte field as well as the overall payload.

The GAM payload shall be written by the GAE endpoint to the GAE's circular GAM Buffer as described in [Section 7.7.2.7.](#page-404-3)

The 'GAM' VDM fields are as follows. PTH holds:

- SPID = GFD PID
- DPID = Host Edge Port PID
- DSAR flag = 1

VDM header fields for 'GAM' VDMs:

- CXL VDM Code of A1h
<span id="page-104-2"></span>- • PBR Opcode 7 (GAM)

#### <span id="page-104-0"></span>3.1.11.7 Route Table Update (RTUpdate) VDM

On a PBR link, the CacheID of a CXL.cache message is replaced with a PID. A table is needed at both the Host ES and Downstream ES to swap between PID and CacheID.

A VDM from the Downstream ES is needed to convey the information, a list of pairs of (PID and CacheID), to the Host ES with a maximum of 16 pairs, corresponding to 8 DWORDs. The flow to the RTUpdate VDM is described in more detail in [Section 7.7.12.5.](#page-459-1)

An RTUpdate VDM is sent from Downstream ES firmware to Host ES firmware. The DPID is the Host PID, allowing for a route to the Host ES. However, the Host ES ingress shall trap on the CXL VDM Code of A1h and handle the VDM in the Host ES.

The 'RTUpdate' VDM fields are as follows. PTH holds:

- SPID = vUSP's fabric port's PID
- DPID = Host Edge Port PID
- DSAR flag = 1

VDM header fields for 'RTUpdate' VDMs:

- CXL VDM Code of A1h
- PBR Opcode 10h (RTUpdate)

[Table 3-11](#page-104-1) shows the RTUpdate VDM payload format. Note that a value of FFFh for DSP\_PID in the payload indicates that the PID is invalid and hence the PID to CacheID information pair needs to be discarded.

<span id="page-104-1"></span>**Table 3-11. RTUpdate VDM Payload**

![](_page_104_Figure_24.jpeg)

![](_page_105_Picture_1.jpeg)

With multibyte fields, the least significant byte of the field starts with the lowest byte offset, and subsequent bytes are strictly increasing in significance. I.e., this is little endian format within each multibyte field as well as the overall payload.

#### <span id="page-105-0"></span>3.1.11.8 Route Table Update Response (RTUpdateAck, RTUpdateNak) VDMs

The response to the RTUpdate VDM shall be one of the following:

<span id="page-105-4"></span>- • RTUpdateAck VDM if the update is successful
- RTUpdateNak VDM if the update is unsuccessful
- RTUpdateNak VDM if a VDM in the sequence was lost

The DPID is set to the vUSP's fabric port's PID, which routes the RTUpdateAck VDM back to the Downstream ES. However, the Downstream ES ingress shall trap on the CXL VDM Code of A1h to direct the VDM to switch firmware.

The Downstream ES, upon receipt of the RTUpdateAck VDM, shall set the commit complete bit in the CacheID table.

The 'RTUpdateAck' / 'RTUpdateNak' VDM fields are as follows. PTH holds:

- SPID = Host Edge Port PID
- DPID = vUSP's fabric port's PID
- DSAR flag = 1

VDM header fields for 'RTUpdateAck' / 'RTUpdateNak' Response VDMs are as follows:

- CXL VDM Code of A1h
<span id="page-105-3"></span>- • PBR Opcode 12h (RTUpdateAck) / PBR Opcode 13h (RTUpdateNak)

## <span id="page-105-1"></span>3.2 CXL.cache

### <span id="page-105-2"></span>3.2.1 Overview

The CXL.cache protocol defines the interactions between the device and host as a number of requests that each have at least one associated response message and sometimes a data transfer. The interface consists of three channels in each direction: Request, Response, and Data. The channels are named for their direction, D2H for device to host and H2D for host to device, and the transactions they carry, Request, Response, and Data as shown in [Figure 3-10](#page-106-3). The independent channels allow different kinds of messages to use dedicated wires and achieve both decoupling and a higher effective throughput per wire.

A D2H Request carries new requests from the Device to the Host. The requests typically target memory. Each request will receive zero, one, or two responses and at most one 64-byte cacheline of data. The channel may be back pressured without issue. D2H Response carries all responses from the Device to the Host. Device responses to snoops indicate the state the line was left in the device caches, and may indicate that data is being returned to the Host to the provided data buffer. They may still be blocked temporarily for link layer credits. D2H Data carries all data and byte enables from the Device to the Host. The data transfers can result either from implicit (as a result of snoop) or explicit write-backs (as a result of cache capacity eviction). A full 64-byte cacheline of data is always transferred. D2H Data must make progress or deadlocks may occur. D2H Data may be temporarily blocked for link layer credits, but must not require any other D2H transaction to complete to free the credits.

An H2D Request carries requests from the Host to the Device. These are snoops to maintain coherency. Data may be returned for snoops. The request carries the location of the data buffer to which any returned data should be written. H2D Requests may be back pressured for lack of device resources; however, the resources must free up without needing D2H Requests to make progress. H2D Response carries ordering messages and pulls for write data. Each response carries the request identifier from the original device request to indicate where the response should be routed. For write data pull responses, the message carries the location where the data should be written. H2D Responses can only be blocked temporarily for link layer credits. H2D Data delivers the data for device read requests. In all cases a full 64-byte cacheline of data is transferred. H2D Data transfers can only be blocked temporarily for link layer credits.

<span id="page-106-3"></span>**Figure 3-10. CXL.cache Channels**

![](_page_106_Picture_4.jpeg)

### <span id="page-106-0"></span>3.2.2 CXL.cache Channel Description

#### <span id="page-106-1"></span>3.2.2.1 Channel Ordering

In general, all the CXL.cache channels must work independently of one another to ensure that forward progress is maintained. For example, because requests from the device to the Host to a given address X will be blocked by the Host until it collects all snoop responses for this address X, linking the channels would lead to deadlock.

However, there is a specific instance where ordering between channels must be maintained for the sake of correctness. The Host needs to wait until Global Observation (GO) messages, sent on H2D Response, are observed by the device before sending subsequent snoops for the same address. To limit the amount of buffering needed to track GO messages, the Host assumes that GO messages that have been sent over CXL.cache in a given cycle cannot be passed by snoops sent in a later cycle.

For transactions that have multiple messages on a single channel with an expected order (e.g., WritePull and GO for WrInv) the Device/Host must ensure they are observed correctly using serializing messages (e.g., the Data message between WritePull and GO for WrInv as shown in [Figure 3-14\)](#page-116-0).

#### <span id="page-106-2"></span>3.2.2.2 Channel Crediting

To maintain the modularity of the interface no assumptions can be made on the ability to send a message on a channel because link layer credits may not be available at all times. Therefore, each channel must use a credit for sending any message and collect credit returns from the receiver. During operation, the receiver returns a credit whenever it has processed the message (i.e., freed up a buffer). It is not required that all credits are accounted for on either side, it is sufficient that credit counter saturates when full. If no credits are available, the sender must wait for the receiver to return one.

Table 3-12 describes which channels must drain to maintain forward progress and which can be blocked indefinitely. Additionally, Table 3-12 defines a summary of the forward progress and crediting mechanisms in CXL.cache, but this is not the complete definition. See Section 3.4 for the complete set of the ordering rules that are required for protocol correctness and forward progress.

<span id="page-107-2"></span>Table 3-12. CXL.cache Channel Crediting Summary

| Channel            | Forward<br>Progress<br>Condition | Blocking Condition                                                                               | Description                                                                                             |
|--------------------|----------------------------------|--------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------|
| D2H Request (Req)  | Credited to Host                 | Can be blocked by all other message classes in CXL.cachemem.                                     | Needs Host buffer, could be held by earlier requests                                                    |
| D2H Response (Rsp) | Pre-allocated                    | Temporary link layer back pressure is allowed. Host may block waiting for H2D Response to drain. | Headed to specified Host buffer                                                                         |
| D2H Data           | Pre-allocated                    | Temporary link layer back pressure is allowed. Host may block for H2D Data to drain.             | Headed to specified Host buffer                                                                         |
| H2D Request (Req)  | Credited to<br>Device            | Must make progress. Temporary back pressure is allowed.                                          | May be back pressured temporarily due<br>to lack of availability of D2H Response or<br>D2H Data credits |
| H2D Response (Rsp) | Pre-allocated                    | Link layer only, must make progress.<br>Temporary back pressure is allowed.                      | Headed to specified device buffer                                                                       |
| H2D Data           | Pre-allocated                    | Link layer only, must make progress.<br>Temporary back pressure is allowed.                      | Headed to specified device buffer                                                                       |

### <span id="page-107-0"></span>3.2.3 CXL.cache Wire Description

The definition of each of the fields for each CXL.cache Channel is provided below. Each message in will support 3 variants: 68B Flit, 256B Flit, and PBR Flit. The use of each of these will be negotiated in the physical layer for each link as defined in Chapter 6.0.

#### <span id="page-107-1"></span>3.2.3.1 D2H Request

<span id="page-107-3"></span>**Table 3-13. CXL.cache - D2H Request Fields (Sheet 1 of 2)**

| D2H Request | Width (Bits) |              |             |                                                                                                                                                                                                                                                                                             |
|-------------|--------------|--------------|-------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|             | 68B<br>Flit  | 256B<br>Flit | PBR<br>Flit | Description                                                                                                                                                                                                                                                                                 |
| Valid       | 1            |              |             | The request is valid.                                                                                                                                                                                                                                                                       |
| Opcode      | 5            |              |             | The opcode specifies the operation of the request. Details in Table 3-22.                                                                                                                                                                                                                   |
| CQID        | 12           |              |             | Command Queue ID: The CQID field contains the ID of the tracker entry that is associated with the request. When the response and data are returned for this request, the CQID is sent in the response or data message indicating to the device which tracker entry originated this request. |
<span id="page-1219-0"></span>|             |              |              |             | IMPLEMENTATION NOTE  CQID usage depends on the round-trip transaction latency and desired bandwidth. A 12-bit ID space allows for 4096 outstanding requests which can saturate link bandwidth for a x16 link at 64 GT/s with average latency of up to 1 us <sup>1</sup> .                   |
| NT          | 1            |              |             | For cacheable reads, the NonTemporal bit is used as a hint to indicate to the host how it should be cached. Details in Table 3-14.                                                                                                                                                          |

Table 3-13. CXL.cache - D2H Request Fields (Sheet 2 of 2)

| D2H Request   | Width (Bits) |              |             |                                                                                                                                                |
|---------------|--------------|--------------|-------------|------------------------------------------------------------------------------------------------------------------------------------------------|
|               | 68B<br>Flit  | 256B<br>Flit | PBR<br>Flit | Description                                                                                                                                    |
| CacheID       | 0            | 4            | 0           | Logical CacheID of the source of the message. Not supported in 68B flit messages. Not applicable in PBR messages where DPID infers this field. |
| Address[51:6] | 46           |              |             | Carries the physical address of coherent requests.                                                                                             |
| SPID          | 0 12         |              | 12          | Source PID                                                                                                                                     |
| DPID          | 0            |              | 12          | Destination PID                                                                                                                                |
| RSVD          | 14 7         |              | 7           |                                                                                                                                                |
| Total         | 79           | 76           | 96          |                                                                                                                                                |

Formula assumed in this calculation is: "Latency Tolerance in ns" = "number of Requests" \* (64B per Request)
 / "Peak Bandwidth in GB/s". Assuming a peak bandwidth of 256 GB/s (raw bidirectional bandwidth of a x16
 CXL port at 64 GT/s) results in a latency tolerance of 1024 ns.

<span id="page-108-1"></span>**Table 3-14.** Non Temporal Encodings**

| NonTemporal | Definition                                                           |  |  |  |
|-------------|----------------------------------------------------------------------|--|--|--|
| 0           | Default behavior. This is Host implementation specific.              |  |  |  |
| 1           | Requested line should be moved to Least Recently Used (LRU) position |  |  |  |

#### <span id="page-108-0"></span>3.2.3.2 D2H Response

<span id="page-108-2"></span>**Table 3-15. CXL.cache - D2H Response Fields**

| D2H<br>Response | w           | idth (Bit    | ts)         | Description                                                                                                                               |
|-----------------|-------------|--------------|-------------|-------------------------------------------------------------------------------------------------------------------------------------------|
|                 | 68B<br>Flit | 256B<br>Flit | PBR<br>Flit |                                                                                                                                           |
| Valid           | 1           |              |             | The response is valid.                                                                                                                    |
| Opcode          |             | 5            |             | The opcode specifies the what kind of response is being signaled. Details in Table 3-25.                                                  |
| UQID            | 12          |              |             | Unique Queue ID: This is a reflection of the UQID sent with the H2D Request and indicates which Host entry is the target of the response. |
| DPID            | 0 12        |              | 12          | Destination PID                                                                                                                           |
| RSVD            | 2 6         |              | 5           |                                                                                                                                           |
| Total           | 20          | 24           | 36          |                                                                                                                                           |

#### <span id="page-109-0"></span>3.2.3.3 D2H Data

<span id="page-109-2"></span>**Table 3-16. CXL.cache - D2H Data Header Fields**

| D2H Data<br>Header | w           | idth (Bit    | ts)         | Description                                                                                                                                                                                                                                                                       |
|--------------------|-------------|--------------|-------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|                    | 68B<br>Flit | 256B<br>Flit | PBR<br>Flit |                                                                                                                                                                                                                                                                                   |
| Valid              | 1           |              |             | The Valid signal indicates that this is a valid data message.                                                                                                                                                                                                                     |
| UQID               |             | 12           |             | Unique Queue ID: This is a reflection of the UQID sent with the H2D Response and indicates which Host entry is the target of the data transfer.                                                                                                                                   |
| ChunkValid         | 1           | (            | )           | In case of a 32B transfer on CXL.cache, this indicates what 32-byte chunk of the cacheline is represented by this transfer. If not set, it indicates the lower 32B and if set, it indicates the upper 32B. This field is ignored for a 64B transfer.                              |
| Bogus              |             | 1            |             | The Bogus bit indicates that the data associated with this evict message was returned to a snoop after the D2H request was sent from the device, but before a WritePull was received for the evict. This data is no longer the most current, so it should be dropped by the Host. |
| Poison             |             | 1            |             | The Poison bit is an indication that this data chunk is corrupted and should not be used by the Host.                                                                                                                                                                             |
| BEP                | 0           | 1            |             | Byte-Enables Present: Indication that 5 data slots are included in the message where the 5 <sup>th</sup> data slot carries the 64-bit Byte Enables. This field is carried as part of the Flit header bits in 68B Flit mode.                                                       |
| DPID               | (           | 0 12         |             | Destination PID                                                                                                                                                                                                                                                                   |
| RSVD               | 1           | 8            |             |                                                                                                                                                                                                                                                                                   |
| Total              | 17          | 24           | 36          |                                                                                                                                                                                                                                                                                   |

##### 3.2.3.3.1 Byte Enables (68B Flit)

In 68B Flit mode, the presence of data byte enables is indicated in the flit header, but only when one or more of the byte enable bits has a value of 0. In that case, the byte enables are sent as a data chunk as described in Section 4.2.2.

##### 3.2.3.3.2 Byte-Enables Present (256B Flit)

In 256B Flit mode, a BEP (Byte-Enables Present) bit is included with the message header that indicates BE slot is included at the end of the message. The Byte Enable field is 64 bits wide and indicates which of the bytes are valid for the contained data.

#### <span id="page-109-1"></span>3.2.3.4 H2D Request

<span id="page-109-3"></span>**Table 3-17. CXL.cache – H2D Request Fields (Sheet 1 of 2)**

|               | W           | idth (Bit    | s)          |                                                                            |
|---------------|-------------|--------------|-------------|----------------------------------------------------------------------------|
| H2D Request   | 68B<br>Flit | 256B<br>Flit | PBR<br>Flit | Description                                                                |
| Valid         | 1           |              |             | The Valid signal indicates that this is a valid request.                   |
| Opcode        | 3           |              |             | The Opcode field indicates the kind of H2D request. Details in Table 3-26. |
| Address[51:6] | 46          |              |             | The Address field indicates which cacheline the request targets.           |

Table 3-17. CXL.cache – H2D Request Fields (Sheet 2 of 2)

| H2D Request | Width (Bits) |              |             |                                                                                                                                                                                                                                                                               |
|-------------|--------------|--------------|-------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|             | 68B<br>Flit  | 256B<br>Flit | PBR<br>Flit | Description                                                                                                                                                                                                                                                                   |
| UQID        |              | 12           |             | Unique Queue ID: This indicates which Host entry is the source of the request.                                                                                                                                                                                                |
| CacheID     | 0            | 4            | 0           | Logical CacheID of the destination of the message. Value is assigned by Switch edge ports and not observed by the device. Host implementation may constrain the number of encodings that the Host can support. Not applicable with PBR messages where DPID infers this field. |
| SPID        | 0            |              | 12          | Source PID                                                                                                                                                                                                                                                                    |
| DPID        | 0            |              | 12          | Destination PID                                                                                                                                                                                                                                                               |
| RSVD        | 2 6          |              | 5           |                                                                                                                                                                                                                                                                               |
| Total       | 64           | 72           | 92          |                                                                                                                                                                                                                                                                               |

#### <span id="page-110-0"></span>3.2.3.5 H2D Response

<span id="page-110-1"></span>**Table 3-18. CXL.cache - H2D Response Fields**

| H2D<br>Response | Width (Bits) |              |             |                                                                                                                                                                                                                     |  |
|-----------------|--------------|--------------|-------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--|
|                 | 68B<br>Flit  | 256B<br>Flit | PBR<br>Flit | Description                                                                                                                                                                                                         |  |
| Valid           |              | 1            |             | The Valid bit indicates that this is a valid response to the device.                                                                                                                                                |  |
| Opcode          | 4            |              |             | The Opcode field indicates the type of the response being sent. Details in Table 3-27.                                                                                                                              |  |
| RspData         |              | 12           |             | The response Opcode determines how the RspData field is interpreted as shown in Table 3-27. Thus, depending on Opcode, it can either contain the UQID or the MESI information in bits [3:0] as shown in Table 3-20. |  |
| RSP_PRE         |              | 2            |             | RSP_PRE carries performance monitoring information. Details in Table 3-19.                                                                                                                                          |  |
| CQID            |              | 12           |             | Command Queue ID: This is a reflection of the CQID sent with the D2H Request and indicates which device entry is the target of the response.                                                                        |  |
| CacheID         | 0            | 4            | 0           | Logical CacheID of the destination of the message. This value is returned by the host based on the CacheID sent in the D2H request.  Not applicable with PBR messages where DPID infers this field.                 |  |
| DPID            | 0 12         |              | 12          | Destination PID                                                                                                                                                                                                     |  |
| RSVD            | 1 5          |              | 5           |                                                                                                                                                                                                                     |  |
| Total           | 32           | 40           | 48          |                                                                                                                                                                                                                     |  |

<span id="page-110-2"></span>**Table 3-19. RSP\_PRE Encodings**

| RSP_PRE[1:0] | Response                                    |
|--------------|---------------------------------------------|
| 00b          | Host Cache Miss to Local CPU socket memory  |
| 01b          | Host Cache Hit                              |
| 10b          | Host Cache Miss to Remote CPU socket memory |
| 11b          | Reserved                                    |

<span id="page-111-3"></span>Table 3-20. Cache State Encoding for H2D Response

| Cache State              | Encoding |
|--------------------------|----------|
| Invalid (I)              | 0011b    |
| Shared (S)               | 0001b    |
| Exclusive (E)            | 0010b    |
| Modified (M)             | 0110b    |
| Error (Err) <sup>1</sup> | 0100b    |

<sup>1.</sup> Covers error conditions not covered by poison such as errors in coherence resolution.

#### <span id="page-111-0"></span>3.2.3.6 H2D Data

<span id="page-111-4"></span>**Table 3-21. CXL.cache - H2D Data Header Fields**

| H2D Data<br>Header | Width (Bits) |              |             |                                                                                                                                                                                                                                                      |
|--------------------|--------------|--------------|-------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|                    | 68B<br>Flit  | 256B<br>Flit | PBR<br>Flit | Description                                                                                                                                                                                                                                          |
| Valid              |              | 1            |             | The Valid bit indicates that this is a valid data to the device.                                                                                                                                                                                     |
| CQID               |              | 12           |             | Command Queue ID: This is a reflection of the CQID sent with the D2H Request and indicates which device entry is the target of the data transfer.                                                                                                    |
| ChunkValid         | 1            | 0            |             | In case of a 32B transfer on CXL.cache, this indicates what 32-byte chunk of the cacheline is represented by this transfer. If not set, it indicates the lower 32B and if set, it indicates the upper 32B. This field is ignored for a 64B transfer. |
| Poison             |              | 1            |             | The Poison bit indicates to the device that this data is corrupted and as such should not be used.                                                                                                                                                   |
| GO-Err             |              | 1            |             | The GO-ERR bit indicates to the agent that this data is the result of an error condition and should not be cached or provided as response to snoops. Covers error conditions not covered by poison such as errors in coherence resolution.           |
| CacheID            | 0            | 4            | 0           | Logical CacheID of the destination of the message. Host and switch must support this field to set a nonzero value. Not applicable in PBR messages where DPID infers this field.                                                                      |
| DPID               | 0 12         |              | 12          | Destination PID                                                                                                                                                                                                                                      |
| RSVD               | 8            | 8 9          |             |                                                                                                                                                                                                                                                      |
| Total              | 24           | 28           | 36          |                                                                                                                                                                                                                                                      |

### <span id="page-111-1"></span>3.2.4 CXL.cache Transaction Description

#### <span id="page-111-2"></span>3.2.4.1 Device-attached Memory Flows for HDM-D/HDM-DB

When a CXL Type 2 device exposes memory to the host using Host-managed Device Memory Device-Coherent (HDM-D/HDM-DB), the device is responsible to resolve coherence of HDM between the host and device. CXL defines two protocol options for this:

- CXL.cache Requests which is used for HDM-D
- CXL.mem Back-Invalidate Snoop (BISnp) which is used with HDM-DB

Endpoint devices supporting 256B Flit mode must support BISnp mechanism and can optionally use CXL.cache mechanism when connected to a host that has only 68B flit mode. When using CXL.cache, the host detects the address as coming from the device that owns the region which triggers the special flow that returns Mem\*Fwd, in most cases, as captured in [Table 3-24](#page-123-0).

#### <span id="page-112-0"></span>3.2.4.2 Device to Host Requests

##### 3.2.4.2.1 Device to Host (D2H) CXL.cache Request Semantics

For device to Host requests, there are four different semantics: CXL.cache Read, CXL.cache Read0, CXL.cache Read0/Write, and CXL.cache Write. All device to Host CXL.cache transactions fall into one of these four semantics, though the allowable responses and restrictions for each request type within a given semantic are different.

##### 3.2.4.2.2 CXL.cache Read

CXL.cache Reads must have a D2H request credit and send a request message on the D2H CXL.cache request channel. CXL.cache Read requests require zero or one response (GO) message and data messages totaling a single 64-byte cacheline of data. Both the response, if present, and data messages are directed at the device tracker entry provided in the initial D2H request packet's CQID field. The device entry must remain active until all the messages from the Host have been received. To ensure forward progress, the device must have a reserved data buffer able to accept 64 bytes of data immediately after the request is sent. However, the device may temporarily be unable to accept data from the Host due to prior data returns not draining. Once both the response message and the data messages have been received from the Host, the transaction can be considered complete and the entry deallocated from the device.

[Figure 3-11](#page-113-0) shows the elements required to complete a CXL.cache Read. Note that the response (GO) message can be received before, after, or between the data messages.

<span id="page-113-0"></span>**Figure 3-11. CXL.cache Read Behavior**

![](_page_113_Figure_3.jpeg)

##### 3.2.4.2.3 CXL.cache Read0

CXL.cache Read0 must have a D2H request credit and send a message on the D2H CXL.cache request channel. CXL.cache Read0 requests receive a response message but no data messages. The response message is directed at the device entry indicated in the initial D2H request message's CQID value. Once the GO message is received for these requests, they can be considered complete and the entry deallocated from the device. A data message must not be sent by the Host for these transactions. Most special cycles (e.g., CLFlush) and other miscellaneous requests fall into this category. See [Table 3-22](#page-118-1) for details.

[Figure 3-12](#page-114-0) shows the elements required to complete a CXL.cache Read0 transaction.

<span id="page-114-0"></span>**Figure 3-12. CXL.cache Read0 Behavior**

![](_page_114_Figure_3.jpeg)

##### 3.2.4.2.4 CXL.cache Write

CXL.cache Write must have a D2H request credit before sending a request message on the D2H CXL.cache request channel. Once the Host has received the request message, it is required to send a GO message and a WritePull message. The WritePull message is not required for CleanEvictNoData. The GO and the WritePull can be a combined message for some requests. The GO message must never arrive at the device before the WritePull, but it can arrive at the same time in the combined message. If the transaction requires posted semantics, then a combined GO-I/WritePull message can be used. If the transaction requires non-posted semantics, then WritePull is issued first followed by the GO-I when the non-posted write is globally observed.

Upon receiving the GO-I message, the device will consider the store done from a memory ordering and cache coherency perspective, giving up snoop ownership of the cacheline (if the CXL.cache message is an Evict).

The WritePull message triggers the device to send data messages to the Host totaling exactly 64 bytes of data, though any number of byte enables can be set.

A CXL.cache write transaction is considered complete by the device once the device has received the GO-I message, and has sent the required data messages. At this point the entry can be deallocated from the device.

The Host considers a write to be done once it has received all 64 bytes of data, and has sent the GO-I response message. All device writes and Evicts fall into the CXL.cache Write semantic.

See [Section 3.2.5.8](#page-129-4) for more information on restrictions around multiple active write transactions.

[Figure 3-13](#page-115-0) shows the elements required to complete a CXL.cache Write transaction (that matches posted behavior). The WritePull (or the combined GO\_WritePull) message triggers the data messages. There are restrictions on Snoops and WritePulls. See [Section 3.2.5.3](#page-128-3) for more details.

[Figure 3-14](#page-116-0) shows a case where the WritePull is a separate message from the GO (for example: strongly ordered uncacheable write).

[Figure 3-15](#page-117-0) shows the Host FastGO plus ExtCmp responses for weakly ordered write requests.

<span id="page-115-0"></span>**Figure 3-13. CXL.cache Device to Host Write Behavior**

![](_page_115_Figure_6.jpeg)

<span id="page-116-0"></span>**Figure 3-14. CXL.cache WrInv Transaction**

![](_page_116_Figure_3.jpeg)

<span id="page-117-0"></span>**Figure 3-15. WOWrInv/F with FastGO/ExtCmp**

![](_page_117_Figure_3.jpeg)

##### 3.2.4.2.5 CXL.cache Read0-Write Semantics

CXL.cache Read0-Write requests must have a D2H request credit before sending a request message on the D2H CXL.cache request channel. Once the Host has received the request message, it is required to send one merged GO-I and WritePull message.

The WritePull message triggers the device to send the data messages to the Host, which together transfer exactly 64 bytes of data though any number of byte enables can be set.

A CXL.cache Read0-Write transaction is considered complete by the device once the device has received the GO-I message, and has sent the all required data messages. At this point the entry can be deallocated from the device.

The Host considers a Read0-Write to be done once it has received all 64 bytes of data, and has sent the GO-I response message. ItoMWr falls into the Read0-Write category.

<span id="page-118-0"></span>**Figure 3-16. CXL.cache Read0-Write Semantics**

![](_page_118_Figure_3.jpeg)

<span id="page-118-2"></span>[Table 3-22](#page-118-1) summarizes all the opcodes that are available from the Device to the Host.

<span id="page-118-1"></span>**Table 3-22. CXL.cache – Device to Host Requests**

| CXL.cache Opcode | Semantic    | Opcode  |
|------------------|-------------|---------|
| RdCurr           | Read        | 0 0001b |
| RdOwn            | Read        | 0 0010b |
| RdShared         | Read        | 0 0011b |
| RdAny            | Read        | 0 0100b |
| RdOwnNoData      | Read0       | 0 0101b |
| ItoMWr           | Read0-Write | 0 0110b |
| WrCur            | Read0-Write | 0 0111b |
| CLFlush          | Read0       | 0 1000b |
| CleanEvict       | Write       | 0 1001b |
| DirtyEvict       | Write       | 0 1010b |
| CleanEvictNoData | Write       | 0 1011b |
| WOWrInv          | Write       | 0 1100b |
| WOWrInvF         | Write       | 0 1101b |
| WrInv            | Write       | 0 1110b |
| CacheFlushed     | Read0       | 1 0000b |

##### 3.2.4.2.6 RdCurr

These are full cacheline read requests from the device for lines to get the most current data, but not change the existing state in any cache, including in the Host. The Host does not need to track the cacheline in the device that issued the RdCurr. RdCurr gets a data but no GO. The device receives the line in the Invalid state which means that the device gets one use of the line and cannot cache it.

##### 3.2.4.2.7 RdOwn

These are full cacheline read requests from the device for lines to be cached in any writeable state. Typically, RdOwn request receives the line in Exclusive (GO-E) or Modified (GO-M) state. Lines in Modified state must not be dropped, and have to be written back to the Host.

Under error conditions, a RdOwn request may receive the line in Invalid (GO-I) or Error (GO-Err) state. Both return synthesized data of all 1s. The device is responsible for handling the error appropriately.

##### 3.2.4.2.8 RdShared

These are full cacheline read requests from the device for lines to be cached in Shared state. Typically, RdShared request receives the line in Shared (GO-S) state.

Under error conditions, a RdShared request may receive the line in Invalid (GO-I) or Error (GO-Err) state. Both will return synthesized data of all 1s. The device is responsible for handling the error appropriately.

##### 3.2.4.2.9 RdAny

These are full cacheline read requests from the device for lines to be cached in any state. Typically, RdAny request receives the line in Shared (GO-S), Exclusive (GO-E) or Modified (GO-M) state. Lines in Modified state must not be dropped, and have to be written back to the Host.

Under error conditions, a RdAny request may receive the line in Invalid (GO-I) or Error (GO-Err) state. Both return synthesized data of all 1s. The device is responsible for handling the error appropriately.

##### 3.2.4.2.10 RdOwnNoData

These are requests to get exclusive ownership of the cacheline address indicated in the address field. The typical response is Exclusive (GO-E).

Under error conditions, a RdOwnNoData request may receive the line in Error (GO-Err) state. The device is responsible for handling the error appropriately.

*Note:* A device that uses this command to write data must be able to update the entire cacheline or may drop the E-state if it is unable to perform the update. There is no support partial M-state data in a device cache. To perform a partial write in the device cache, the device must read the cacheline using RdOwn before merging with the partial write data in the cache.

##### 3.2.4.2.11 ItoMWr

This command requests exclusive ownership of the cacheline address indicated in the address field and atomically writes the cacheline back to the Host. The device guarantees the entire line will be modified, so no data needs to be transferred to the

![](_page_120_Picture_1.jpeg)

device. The typical response is GO\_WritePull, which is sent once the request is granted ownership. The device must not retain a copy of the line. If a cache exists in the host cache hierarchy before memory, the data should be written there.

If an error occurs, then GO-Err-WritePull is sent instead. The device sends the data to the Host, which drops it. The device is responsible for handling the error as appropriate.

##### 3.2.4.2.12 WrCur

The command behaves like the ItoMWr in that it atomically requests ownership of a cacheline and then writes a full cacheline back to the Fabric. However, it differs from ItoMWr in where the data is written. Only if the command hits in a cache will the data be written there; on a Miss, the data will be written directly to memory. The typical response is GO\_WritePull once the request is granted ownership. The device must not retain a copy of the line.

If an error occurs, then GO-Err-WritePull is sent instead. The device sends the data to the Host, which drops it. The device is responsible for handling the error as appropriate.

*Note:* In earlier revisions of the specification (CXL 2.0 and CXL 1.x), this command was called "MemWr", but this was a problem because that same message name is used in the CXL.mem protocol, so a new name was selected. The opcode and behavior are unchanged.

##### 3.2.4.2.13 CLFlush

<span id="page-120-0"></span>This is a request to the Host to invalidate the cacheline specified in the address field. The typical response is GO-I which is sent from the Host upon completion in memory.

However, the Host may keep tracking the cacheline in Shared state if the Core has issued a Monitor to an address belonging in the cacheline. Thus, the Device that exposes an HDM-D region must not rely on CLFlush/GO-I as a sufficient condition for which to flip a cacheline in the HDM-D region from Host to Device Bias mode. Instead, the Device must initiate RdOwnNoData and receive an H2D Response of GO-E before it updates its Bias Table to Device Bias mode to allow subsequent cacheline access without notifying the Host.

Under error conditions, a CLFlush request may receive the line in the Error (GO-Err) state. The device is responsible for handling the error appropriately.

##### 3.2.4.2.14 CleanEvict

This is a request to the Host to evict a full 64-byte Exclusive cacheline from the device. Typically, CleanEvict receives GO-WritePull or GO-WritePullDrop. The response will cause the device to relinquish snoop ownership of the line. For GO-WritePull, the device will send the data as normal. For GO-WritePullDrop, the device simply drops the data.

Once the device has issued this command and the address is subsequently snooped, but before the device has received the GO-WritePull, the device must set the Bogus field in all D2H Data messages to indicate that the data is now stale.

CleanEvict requests also guarantee to the Host that the device no longer contains any cached copies of this line. Only one CleanEvict from the device may be pending on CXL.cache for any given cacheline address.

CleanEvict is only expected for a host-attached memory range of addresses. For a device-attached memory range, the equivalent operation can be completed internally within the device without sending a transaction to the Host.

##### 3.2.4.2.15 DirtyEvict

<span id="page-121-0"></span>This is a request to the Host to evict a full 64-byte Modified cacheline from the device. Typically, DirtyEvict receives GO-WritePull from the Host at which point the device must relinquish snoop ownership of the line and send the data as normal.

Once the device has issued this command and the address is subsequently snooped, but before the device has received the GO-WritePull, the device must set the Bogus field in all D2H Data messages to indicate that the data is now stale.

DirtyEvict requests also guarantee to the Host that the device no longer contains any cached copies of this line. Only one DirtyEvict from the device may be pending on CXL.cache for any given cacheline address.

In error conditions, a GO-Err-WritePull is received. The device sends the data as normal, and the Host drops it. The device is responsible for handling the error as appropriate.

DirtyEvict is only expected for host-attached memory address ranges. For device-attached memory range, the equivalent operation can be completed internally within the device without sending a transaction to the Host.

##### 3.2.4.2.16 CleanEvictNoData

This is a request for the device to update the Host that a clean line is dropped in the device. The sole purpose of this request is to update any snoop filters in the Host and no data is exchanged.

CleanEvictNoData is only expected for host-attached memory address ranges. For device-attached memory range, the equivalent operation can be completed internally within the device without sending a transaction to the Host.

##### 3.2.4.2.17 WOWrInv

This is a weakly ordered write invalidate line request of 0-63 bytes for write combining type stores. Any combination of byte enables may be set.

Typically, WOWrInv receives a FastGO-WritePull followed by an ExtCmp. Upon receiving the FastGO-WritePull the device sends the data to the Host. For host-attached memory, the Host sends the ExtCmp once the write is complete in memory.

FastGO does not provide "Global Observation".

In error conditions, a GO-Err-WritePull is received. The device sends the data as normal, and the Host drops it. The device is responsible for handling the error as appropriate. An ExtCmp is still sent by the Host after the GO-Err in all cases.

##### 3.2.4.2.18 WOWrInvF

Same as WOWrInv (rules and flows), except it is a write of 64 bytes.

##### 3.2.4.2.19 WrInv

This is a write invalidate line request of 0-64 bytes. Typically, WrInv receives a WritePull followed by a GO. Upon getting the WritePull, the device sends the data to the Host. The Host sends GO once the write completes in memory (both, host-attached or device-attached).

In error conditions, a GO-Err is received. The device is responsible for handling the error as appropriate.

##### 3.2.4.2.20 CacheFlushed

This is an indication sent by the device to inform the Host that its caches are flushed, and it no longer contains any cachelines in the Shared, Exclusive or Modified state (a device may exclude addresses that are part its "Device-attached Memory" mapped as HDM-D/HDM-DB). The Host can use this information to clear its snoop filters, block snoops to the device, and return a GO. Once the device receives the GO, it is guaranteed to not receive any snoops from the Host until the device sends the next cacheable D2H Request.

When a CXL.cache device is flushing its cache, the device must wait for all responses for cacheable access before sending the CacheFlushed message. This is necessary because the Host must observe CacheFlushed only after all inflight messages that impact device coherence tracking in the Host are complete.

> **IMPLEMENTATION NOTE**

Snoops may be pending to the device when the Host receives the CacheFlushed command and the Host may complete the CacheFlushed command (sending a GO) while those snoops are outstanding. From the device point of view, this can be observed as receiving snoops after the CacheFlushed message is complete. The device should allow for this behavior without creating long stall conditions on the snoops by waiting for snoop queues to drain before initiating any power state transition (e.g., L1 link state) that could stall snoops.

<span id="page-122-0"></span>**Table 3-23. D2H Request (Targeting Non Device-attached Memory) Supported H2D Responses**

|                  | H2D Response |              |        |                   |                   |                  |        |      |      |      |      |
|------------------|--------------|--------------|--------|-------------------|-------------------|------------------|--------|------|------|------|------|
| D2H Request      | WritePull    | GO_WritePull | ExtCmp | GO_WritePull_Drop | Fast_GO_WritePull | GO_ERR_WritePull | GO-Err | GO-I | GO-S | GO-E | GO-M |
| RdCurr           |              |              |        |                   |                   |                  |        |      |      |      |      |
| RdOwn            |              |              |        |                   |                   |                  | X      | X    |      | X    | X    |
| RdShared         |              |              |        |                   |                   |                  | X      | X    | X    |      |      |
| RdAny            |              |              |        |                   |                   |                  | X      | X    | X    | X    | X    |
| RdOwnNoData      |              |              |        |                   |                   |                  | X      |      |      | X    |      |
| ItoMWr           |              | X            |        |                   |                   | X                |        |      |      |      |      |
| WrCur            |              | X            |        |                   |                   | X                |        |      |      |      |      |
| CLFlush          |              |              |        |                   |                   |                  | X      | X    |      |      |      |
| CleanEvict       |              | X            |        | X                 |                   |                  |        |      |      |      |      |
| DirtyEvict       |              | X            |        |                   |                   | X                |        |      |      |      |      |
| CleanEvictNoData |              |              |        |                   |                   |                  |        | X    |      |      |      |
| WOWrInv          |              |              | X      |                   | X                 | X                |        |      |      |      |      |
| WOWrInvF         |              |              | X      |                   | X                 | X                |        |      |      |      |      |
| WrInv            | X            |              |        |                   |                   |                  | X      | X    |      |      |      |
| CacheFlushed     |              |              |        |                   |                   |                  |        | X    |      |      |      |

For requests that target device-attached memory mapped as HDM-D, if the region is in Device Bias, no transaction is expected on CXL.cache because the Device can internally complete those requests. If the region is in Host Bias, Table 3-24 shows how the device should expect the response. For devices with BISnp channel support in which the memory is mapped as HDM-DB, the resolution of coherence happens separately on the CXL.mem protocol and the "Not Supported" cases in the table are never sent from a device to the device-attached memory address range. The only commands supported on CXL.cache to this address region when BISnp is enabled are ItoMWr, WrCur, and WrInv.

<span id="page-123-0"></span>**Table 3-24. D2H Request (Targeting Device-attached Memory) Supported Responses**

|                  | Response on CXL.                                                                               | cache                  | Response on CXL.mem                  |                        |  |  |
|------------------|------------------------------------------------------------------------------------------------|------------------------|--------------------------------------|------------------------|--|--|
| D2H Request      | Without BISnp (HDM-D)                                                                          | With BISnp<br>(HDM-DB) | Without BISnp<br>(HDM-D)             | With BISnp<br>(HDM-DB) |  |  |
| RdCurr           | GO-Err Bit set in H2D DH,<br>Synthesized Data with all 1s<br>(For Error Conditions)            | Not Supported          | MemRdFwd (For<br>Success Conditions) | Not Supported          |  |  |
| RdOwn            | GO-Err on H2D Response,<br>Synthesized Data with all 1s<br>(For Error Conditions) Not Supporte |                        | MemRdFwd (For<br>Success Conditions) | Not Supported          |  |  |
| RdShared         | GO-Err on H2D Response,<br>Synthesized Data with all 1s<br>(For Error Conditions) Not Suppo    |                        | MemRdFwd (For<br>Success Conditions) | Not Supported          |  |  |
| RdAny            | GO-Err on H2D Response,<br>Synthesized Data with all 1s<br>(For Error Conditions)              | Not Supported          | MemRdFwd (For<br>Success Conditions) | Not Supported          |  |  |
| RdOwnNoData      | GO-Err on H2D Response (For Error Conditions) Not Supported                                    |                        | MemRdFwd (For Success Conditions)    | Not Supported          |  |  |
| ItoMWr           | Same as host-attached memory                                                                   | y <sup>1</sup>         | None                                 |                        |  |  |
| WrCur            | Same as host-attached memory                                                                   | None                   |                                      |                        |  |  |
| CLFlush          | GO-Err on H2D Response (For Error Conditions) Not Supported                                    |                        | MemRdFwd (For<br>Success Conditions) | Not Supported          |  |  |
| CleanEvict       | Not Supported                                                                                  |                        |                                      |                        |  |  |
| DirtyEvict       | Not Supported                                                                                  |                        |                                      |                        |  |  |
| CleanEvictNoData | Not Supported                                                                                  |                        |                                      |                        |  |  |
| WOWrInv          | GO_ERR_WritePull on H2D<br>Response (For Error<br>Conditions)                                  | Not Supported          | MemWrFwd (For<br>Success Conditions) | Not Supported          |  |  |
| WOWrInvF         | GO_ERR_WritePull on H2D<br>Response (For Error<br>Conditions)                                  | Not Supported          | MemWrFwd (For<br>Success Conditions) | Not Supported          |  |  |
| WrInv            | Same as host-attached memory                                                                   | y <sup>1</sup>         | None                                 |                        |  |  |
| CacheFlushed     | N/A <sup>2</sup>                                                                               |                        | None                                 |                        |  |  |

<span id="page-123-1"></span>Flow for these commands follow the same flow as host memory regions and are not expected to check against CXL.mem coherence tracking (Bias Table or Snoop Filter) before issuing. The host will resolve coherence with the device using the CXL.mem protocol.

CleanEvict, DirtyEvict, and CleanEvictNoData targeting device-attached memory should always be completed internally by the device, regardless of bias state. For D2H Requests that receive a response on CXL.mem, the CQID associated with the CXL.cache request is reflected in the Tag of the CXL.mem MemRdFwd or MemWrFwd command. For MemRdFwd, the caching state of the line is reflected in the MetaValue field as described in Table 3-37.

<sup>2.</sup> There is no address in this command and the host must assume that this applies only to host memory regions (excluding device-attached memory).

#### <span id="page-124-0"></span>3.2.4.3 Device to Host Response

Responses are directed at the Host entry indicated in the UQID field in the original H2D request message.

<span id="page-124-1"></span>**Table 3-25. D2H Response Encodings**

| Device CXL.cache Rsp | Opcode  |
|----------------------|---------|
| RspIHitI             | 0 0100b |
| RspVHitV             | 0 0110b |
| RspIHitSE            | 0 0101b |
| RspSHitSE            | 0 0001b |
| RspSFwdM             | 0 0111b |
| RspIFwdM             | 0 1111b |
| RspVFwdV             | 1 0110b |

##### 3.2.4.3.1 RspIHitI

In general, this is the response that a device provides to a snoop when the line was not found in any caches. If the device returns RspIHitI for a snoop, the Host can assume the line has been cleared from that device.

##### 3.2.4.3.2 RspVHitV

In general, this is the response that a device provides to a snoop when the line was hit in the cache and no state change occurred. If the device returns an RspVHitV for a snoop, the Host can assume a copy of the line is present in one or more places in that device.

##### 3.2.4.3.3 RspIHitSE

In general, this is the response that a device provides to a snoop when the line was hit in a clean state in at least one cache and is now invalid. If the device returns an RspIHitSE for a snoop, the Host can assume the line has been cleared from that device.

##### 3.2.4.3.4 RspSHitSE

In general, this is the response that a device provides to a snoop when the line was hit in a clean state in at least one cache and is now downgraded to shared state. If the device returns an RspSHitSE for a snoop, the Host should assume the line is still in the device.

##### 3.2.4.3.5 RspSFwdM

This response indicates to the Host that the line being snooped is now in S state in the device, after having hit the line in Modified state. The device may choose to downgrade the line to Invalid. This response also indicates to the Host snoop tracking logic that 64 bytes of data is transferred on the D2H CXL.cache Data Channel to the Host data buffer indicated in the original snoop's destination (UQID).

##### 3.2.4.3.6 RspIFwdM

This response indicates to the Host that the line being snooped is now in I state in the device, after having hit the line in Modified state. The Host may now assume the device contains no more cached copies of this line. This response also indicates to the Host

snoop tracking logic that 64 bytes of data will be transferred on the D2H CXL.cache Data Channel to the Host data buffer indicated in the original snoop's destination (UQID).

##### 3.2.4.3.7 RspVFwdV

This response indicates that the device with E or M state (but not S state) is returning the current data to the Host and leaving the state unchanged. The Host must only forward the data to the requester because there is no state information.

#### <span id="page-125-0"></span>3.2.4.4 Host to Device Requests

Snoops from the Host need not gain any credits besides local H2D request credits. The device will always send a Snoop Response message on the D2H CXL.cache Response channel. If the response is of the Rsp\*Fwd\* format, then the device must respond with 64 bytes of data via the D2H Data channel, directed at the UQID from the original snoop request message. If the response is not Rsp\*Fwd\*, the Host can consider the request complete upon receiving the snoop response message. The device can stop tracking the snoop once the response has been sent for non-data forwarding cases, or after both the last chunk of data has been sent and the response has been sent.

[Figure 3-17](#page-125-1) shows the elements required to complete a CXL.cache snoop. Note that the response message can be received by the Host in any relative order with respect to the data messages. The byte enable field is always all 1s for Snoop data transfers.

<span id="page-125-1"></span>**Figure 3-17. CXL.cache Snoop Behavior**

![](_page_125_Figure_9.jpeg)

<span id="page-126-1"></span>**Table 3-26. CXL.cache – Mapping of H2D Requests to D2H Responses**

|         | Opcode | RspIHitI | RspVhitV | RspSHitSE | RspIHitSE | RspSFwdM | RspIFwdM | RspVFwdV |
|---------|--------|----------|----------|-----------|-----------|----------|----------|----------|
| SnpData | 001b   | X        |          | X         |           | X        | X        |          |
| SnpInv  | 010b   | X        |          |           | X         |          | X        |          |
| SnpCur  | 011b   | X        | X        | X         |           | X        | X        | X        |

##### 3.2.4.4.1 SnpData

These are snoop requests from the Host for lines that are intended to be cached in either Shared or Exclusive state at the requester (the Exclusive state can be cached at the requester only if all devices respond with RspI). This type of snoop is typically triggered by data read requests. A device that receives this snoop must either invalidate or downgrade all cachelines to Shared state. If the device holds dirty data it must return it to the Host.

##### 3.2.4.4.2 SnpInv

These are snoop requests from the Host for lines that are intended to be granted ownership and Exclusive state at the requester. This type of snoop is typically triggered by write requests. A device that receives this snoop must invalidate all cachelines. If the device holds dirty data it must return it to the Host.

##### 3.2.4.4.3 SnpCur

This snoop gets the current version of the line, but doesn't require change of any cache state in the hierarchy. It is only sent on behalf of the RdCurr request. If the device holds data in Modified state it must return it to the Host. The cache state can remain unchanged in both the device and Host, and the Host should not update its caches. To allow for varied cache implementations, devices are allowed to change cache state as captured in [Table 3-26,](#page-126-1) but it is recommended to not change cache state.

#### <span id="page-126-0"></span>3.2.4.5 Host to Device Response

<span id="page-126-2"></span>**Table 3-27. H2D Response Opcode Encodings**

| H2D Response Class | Encoding | RspData    |  |
|--------------------|----------|------------|--|
| WritePull          | 0001b    | UQID       |  |
| GO                 | 0100b    | MESI1      |  |
| GO_WritePull       | 0101b    | UQID       |  |
| ExtCmp             | 0110b    | Don't Care |  |
| GO_WritePull_Drop  | 1000b    | UQID       |  |
| Reserved           | 1100b    | Don't Care |  |
| Fast_GO_WritePull  | 1101b    | UQID       |  |
| GO_ERR_WritePull   | 1111b    | UQID       |  |

<sup>1. 4-</sup>bit MESI encoding is in LSB and the upper bits are Reserved.

##### 3.2.4.5.1 WritePull

This response instructs the device to send the write data to the Host, but not to change the state of the line. This is used for WrInv where the data is needed before the GO-I can be sent. This is because GO-I is the notification that the write was completed.

##### 3.2.4.5.2 GO

The Global Observation (GO) message conveys that read requests are coherent and that write requests are coherent and consistent. It is an indication that the transaction has been observed by the system device and the MESI state that is encoded in the RspType field indicates into which state the data associated with the transaction should be placed for the requester's caches. Details in [Table 3-20](#page-111-3).

If the Host returns Modified state to the device, then the device is responsible for the dirty data and cannot drop the line without writing it back to the Host.

If the Host returns Invalid or Error state to the device, then the device must use the data at most once and not cache the data. Error responses to reads and cacheable write requests (for example, RdOwn or ItoMWr) will always be the result of an abort condition, so modified data can be safely dropped in the device.

##### 3.2.4.5.3 GO\_WritePull

This is a combined GO + WritePull message. No cache state is transferred to the device. The GO+WritePull message is used for write types that do not require a later message to know whether write data is visible.

##### 3.2.4.5.4 ExtCmp

This response indicates that the data that was previously locally ordered (FastGO) has been observed throughout the system. Most importantly, accesses to memory will return the most up-to-date data.

##### 3.2.4.5.5 GO\_WritePull\_Drop

This message has the same semantics as GO\_WritePull, except that the device should not send data to the Host. This response can be sent in place of GO\_WritePull when the Host determines that the data is not required. This response will never be sent for partial writes because the byte enables will always need to be transferred.

##### 3.2.4.5.6 Fast\_GO\_WritePull

Similar to GO\_WritePull, but only indicates that the request is locally observed. There will be a later ExtCmp message when the transaction is fully observable in memory. Devices that do not implement the Fast\_GO feature may ignore the GO message and wait for the ExtCMP. Data must always be sent for the WritePull. No cache state is transferred to the device.

Locally Observed, in this context, is a host-specific coherence domain that may be a subset of the global coherence domain. An example is a Last Level Cache that the requesting device shares with other CXL.cache devices that are connected below a host-bridge. In that example, local observation is only within the Last Level Cache and not between other Last Level Caches.

##### 3.2.4.5.7 GO\_ERR\_WritePull

Similar to GO\_WritePull, but indicates that there was an error with the transaction that should be handled correctly in the device. Data must be sent to the Host for the WritePull, and the Host will drop the data. No cache state is transferred to the device (assumed Error). An ExtCmp is still sent if it is expected by the originating request.

### <span id="page-128-0"></span>3.2.5 Cacheability Details and Request Restrictions

These details and restrictions apply to all devices.

#### <span id="page-128-1"></span>3.2.5.1 GO-M Responses

GO-M responses from the host indicate that the device is being granted the sole copy of modified data. The device must cache this data and write it back when it is done.

#### <span id="page-128-2"></span>3.2.5.2 Device/Host Snoop-GO-Data Assumptions

When the host returns a GO response to a device, the expectation is that a snoop arriving to the same address of the request receiving the GO would see the results of that GO. For example, if the host sends GO-E for an RdOwn request followed by a snoop to the same address immediately afterwards, then one would expect the device to transition the line to M state and reply with an RspIFwdM response back to the Host. To implement this principle, the CXL.cache link layer ensures that the device will receive the two messages in separate slots to make the order completely unambiguous.

When the host is sending a snoop to the device, the requirement is that no GO response will be sent to any requests with that address in the device until after the Host has received a response for the snoop and all implicit writeback (IWB) data (dirty data forwarded in response to a snoop) has been received.

When the host returns data to the device for a read type request, and GO for that request has not yet been sent to the device, the host may not send a snoop to that address until after the GO message has been sent. Because the new cache state is encoded in the response message for reads, sending a snoop to an address without having received GO, but after having received data, is ambiguous to the device as to what the snoop response should be in that situation.

Fundamentally, the GO that is associated with a read request also applies to the data returned with that request. Sending data for a read request implies that data is valid, meaning the device can consume it even if the GO has not yet arrived. The GO will arrive later and inform the device what state to cache the line in (if at all) and whether the data was the result of an error condition (e.g., hitting an address region that the device was not allowed to access).

#### <span id="page-128-3"></span>3.2.5.3 Device/Host Snoop/WritePull Assumptions

The device requires that the host cannot have both a WritePull and H2D Snoop active on CXL.cache to a given 64-byte address. The host may not launch a snoop to a 64 byte address until all WritePull data from that address has been received by the host. Conversely, the host may not launch a WritePull for a write until the host has received the snoop response (including data in case of Rsp\*Fwd\*) for any snoops to the pending writes address. Any violation of these requirements will mean that the Bogus field on the D2H Data channel will be unreliable.

#### <span id="page-129-0"></span>3.2.5.4 Snoop Responses and Data Transfer on CXL.cache Evicts

To snoop cache evictions (for example, DirtyEvict) and maintain an orderly transfer of snoop ownership from the device to the host, cache evictions on CXL.cache must adhere to the following protocol.

If a device Evict transaction has been issued on the CXL.cache D2H request channel, but has not yet processed its WritePull from the host, and a snoop hits the writeback, the device must track this snoop hit if cache state is changed, which excludes the case when SnpCur results in a RspVFwdV response. When the device begins to process the WritePull, if snoop hit is tracked the device must set the Bogus field in all the D2H data messages sent to the host. The intent is to communicate to the host that the request data was already sent as IWB data, so the data from the Evict is potentially stale.

#### <span id="page-129-1"></span>3.2.5.5 Multiple Snoops to the Same Address

The host is only allowed to have one snoop pending at a time per cacheline address per device. The host must wait until it has received both the snoop response and all IWB data (if any) before sending the next snoop to that address.

#### <span id="page-129-2"></span>3.2.5.6 Multiple Reads to the Same Cacheline

Multiple read requests (cacheable or uncacheable) to the same cacheline are allowed only in the following specific cases where host tracking state is consistent regardless of the order requests are processed. The host can freely reorder requests, so the device is responsible for ordering requests when required. For host memory, multiple RdCurr and/or CLFlush are allowed. For these commands the device ends in I-state, so there is no inconsistent state possible for host tracking of a device cache. With Type 2 devices that use HDM-D memory, in addition to RdCurr and/or CLFlush, multiple RdOwnNoData (bias flip requests) are allowed for device-attached memory. This case is allowed because with device-attached memory, the host does not track the device's cache so re-ordering in the host will not create an ambiguous state between the device and the host.

#### <span id="page-129-3"></span>3.2.5.7 Multiple Evicts to the Same Cacheline

Multiple Evicts to the same cacheline are not allowed. All Evict messages from the device provide a guarantee to the host that the evicted cacheline will no longer be present in the device's caches.

Thus, it is a coherence violation to send another Evict for the same cacheline without an intervening cacheable Read/Read0 request to that address.

#### <span id="page-129-4"></span>3.2.5.8 Multiple Write Requests to the Same Cacheline

Multiple WrInv/WOWrInv/ItoMWr/WrCur to the same cacheline are allowed to be outstanding on CXL.cache. The host or switch can freely reorder requests, and the device may receive corresponding H2D Responses in reordered manner. However, it is generally recommended that the device should issue no more than one outstanding Write request for a given cacheline, and order multiple write requests to the same cacheline one after another whenever stringent ordering is warranted.

#### <span id="page-129-5"></span>3.2.5.9 Multiple Read and Write Requests to the Same Cacheline

Multiple RdCur/CLFlush/WrInv/WOWrInv/ItoMWr/WrCur may be issued in parallel from devices to the same cacheline address. Other reads need to issue one at a time (also known as "serialize"). To serialize, the read must not be issued until all other

![](_page_130_Picture_1.jpeg)

outstanding accesses to same cacheline address have received GO. Additionally, after the serializing read is issued, no other accesses to the same cacheline address may be issued until it has received GO.

#### <span id="page-130-0"></span>3.2.5.10 Normal Global Observation (GO)

Normal Global Observation (GO) responses are sent only after the host has guaranteed that request will have next ownership of the requested cacheline. GO messages for requests carry the cacheline state permitted through the MESI state or indicate that the data should only be used once and whether an error occurred.

#### <span id="page-130-1"></span>3.2.5.11 Relaxed Global Observation (FastGO)

FastGO is only allowed for requests that do not require strict ordering. The Host may return the FastGO once the request is guaranteed next ownership of the requested cacheline within an implementation dependent sub-domain (e.g., CPU socket), but not necessarily within the system. Requests that receive a FastGO response and require completion messages are usually of the write combining memory type and the ordering requirement is that there will be a final completion (ExtCmp) message indicating that the request is at the stage where it is fully observed throughout the system. To make use of FastGO, devices have specific knowledge of the FastGO boundary of the CXL hierarchy and know the consumer of the data is within that hierarchy; otherwise, they must wait for the ExtCmp to know the data will be visible.

#### <span id="page-130-2"></span>3.2.5.12 Evict to Device-attached Memory

Device Evicts to device-attached memory are not allowed on CXL.cache. Evictions are expected to go directly to the device's own memory; however, a device may use non-Evict writes (e.g., ItoMWr, WrCur) to write data to the host to device-attached memory.

#### <span id="page-130-3"></span>3.2.5.13 Memory Type on CXL.cache

To source requests on CXL.cache, devices need to get the Host Physical Address (HPA) from the Host by means of an ATS request on CXL.io. Due to memory type restrictions, on the ATS completion, the Host indicates to the device if an HPA can only be issued on CXL.io as described in [Section 3.1.6.](#page-92-0) The device is not allowed to issue requests to such HPAs on CXL.cache. For requests that target ranges within the Device's local HDM range, the HPA is permitted to be obtained by means of an ATS request on CXL.io, or by using device-specific means.

#### <span id="page-130-4"></span>3.2.5.14 General Assumptions

<span id="page-130-5"></span>- 1. The Host will NOT preserve ordering of the CXL.cache requests as delivered by the device. The device must maintain the ordering of requests for the case(s) where ordering matters. For example, if D2H memory writes need to be ordered with respect to an MSI (on CXL.io), it is up to the device to implement the ordering. This is made possible by the non-posted nature of all requests on CXL.cache.
- 2. The order chosen by the Host will be conveyed differently for reads and writes. For reads, a Global Observation (GO) message conveys next ownership of the addressed cacheline; the data message conveys ordering with respect to other transactions. For writes, the GO message conveys both next ownership of the line and ordering with respect to other transactions.
- 3. The device may cache ownership and internally order writes to an address if a prior read to that address received either GO-E or GO-M.
- 4. For reads from the device, the Host transfers ownership of the cacheline with the GO message, even if the data response has not yet been received by the device. The device must respond to a snoop to a cacheline which has received GO, but if

- data from the current transaction is required (e.g., a RdOwn to write the line) the data portion of the snoop is delayed until the data response is received.
- 5. The Host must not send a snoop for an address where it has sent a data response for a previous read transaction but has not yet sent the GO. Ordering will ensure that the device observes the GO in this case before any later snoop. Refer to [Section 3.2.5.2](#page-128-2) for additional details.
- 6. Write requests (other than Evicts) such as WrInv, WOWrInv\*, ItoMWr, and WrCur will never respond to WritePulls with data marked as Bogus.
- 7. The Host must not send two cacheline data responses to the same device request. The device may assume one-time use ownership (based on the request) and begin processing for any part of a cacheline received by the device before the GO message. Final state information will arrive with the GO message, at which time the device can either cache the line or drop it depending on the response.
- 8. For a given transaction, H2D Data transfers must come in consecutive packets in natural order with no interleaved transfers from other lines.
- 9. D2H Data transfer of a cacheline must come in consecutive packets with no interleaved transfers from other lines. The data must come in natural chunk order, that is, 64B transfers must complete the lower 32B half first because snoops are always cacheline aligned.
- 10. Device snoop responses in D2H Response must not be dependent on any other channel or on any other requests in the device besides the availability of credits in the D2H Response channel. The Host must guarantee that the responses will eventually be serviced and return credits to the device.
- 11. The Host must not send a second snoop request to an address until all responses, plus data if required, for the prior snoop are collected.
- 12. H2D Response and H2D Data messages to the device must drain without the need for any other transaction to make progress.
- 13. The Host must not return GO-M for data that is not actually modified with respect to memory.
- 14. The Host must not write unmodified data back to memory.
- 15. Except for WOWrInv and WOWrInF, all other writes are strongly ordered

#### <span id="page-131-0"></span>3.2.5.15 Buried Cache State Rules

Buried Cache state refers to the state of the cacheline registered in the Device's Coherency engine (DCOH) when a CXL.cache request is being sent for that cacheline from the device.

The Buried Cache state rules for a device when issuing CXL.cache requests are as follows:

- Must not issue a Read if the cacheline is buried in Modified, Exclusive, or Shared state.
- Must not issue RdOwnNoData if the cacheline is buried in Modified or Exclusive state. The Device may request for ownership in Exclusive state as an upgrade request from Shared state.
- Must not issue a Read0-Write if the cacheline is buried in Modified, Exclusive, or Shared state.
- All \*Evict opcodes must adhere to apropos use case. For example, the Device is allowed to issue DirtyEvict for a cacheline only when it is buried in Modified state. For performance benefits, it is recommended that the Device should not silently drop a cacheline in Exclusive or Shared state and instead use CleanEvict\* opcodes toward the Host.

• The CacheFlushed Opcode is not specific to a cacheline, it is an indication to the Host that all the Device's caches are flushed. Thus, the Device must not issue CacheFlushed if there is any cacheline buried in Modified, Exclusive, or Shared state.

[Table 3-28](#page-132-1) describes which Opcodes in D2H requests are allowed for a given Buried Cache State.

> **IMPLEMENTATION NOTE**

Buried state rules are requirements at the requester's Transaction Layer. It is possible snoops in flight to change the state observed at the host before the host processes the request. An example case is SnpInv sent from the host at the same time as the device issues a CleanEvictNoData from E-state, the snoop will cause the cache state in the device to change to I-state before the CleanEvictNoData is processed in the host, so the host must allow for this degraded cache state in its coherence tracking.

<span id="page-132-1"></span>**Table 3-28. Allowed Opcodes for D2H Requests per Buried Cache State**

|                  | D2H Requests | Buried Cache State |           |        |         |  |  |
|------------------|--------------|--------------------|-----------|--------|---------|--|--|
| Opcodes          | Semantic     | Modified           | Exclusive | Shared | Invalid |  |  |
| RdCurr           | Read         |                    |           |        | X       |  |  |
| RdOwn            | Read         |                    |           |        | X       |  |  |
| RdShared         | Read         |                    |           |        | X       |  |  |
| RdAny            | Read         |                    |           |        | X       |  |  |
| RdOwnNoData      | Read0        |                    |           | X      | X       |  |  |
| ItoMWr           | Read0-Write  |                    |           |        | X       |  |  |
| WrCur            | Read0-Write  |                    |           |        | X       |  |  |
| CLFlush          | Read0        |                    |           |        | X       |  |  |
| CleanEvict       | Write        |                    | X         |        |         |  |  |
| DirtyEvict       | Write        | X                  |           |        |         |  |  |
| CleanEvictNoData | Write        |                    | X         | X      |         |  |  |
| WOWrInv          | Write        |                    |           |        | X       |  |  |
| WOWrInvF         | Write        |                    |           |        | X       |  |  |
| WrInv            | Write        |                    |           |        | X       |  |  |
| CacheFlushed     | Read0        |                    |           |        | X       |  |  |

#### <span id="page-132-0"></span>3.2.5.16 H2D Req Targeting Device-attached Memory

H2D Req messages are sent by a host to a device because the host believes that the device may own a cacheline that the device previously received from this same host. The very principle of a Type 2 Device is to provide direct access to Device-attached Memory (i.e., without going through its host). Host coherence for this region is managed by using the M2S Req channel. These statements combined could lead a Type 2 Device to assume that H2D Req messages can never target addresses that belong to the Device-attached memory by design.

However, a host may decide to snoop more cache peers than strictly required, without any other consideration than the cache peer being visible to the host. This type of behavior is allowed by the CXL protocol and can occur for multiple reasons, including coarse tracking and proprietary RAS features. In that context, a host may generate an

H2D Req to a Type 2 device on addresses that belong to the Device-attached Memory. An H2D Req from the host that targets Device-attached memory can cause coherency issues if the device were to respond with data and, more generally speaking, protocol corner cases.

To avoid these issues, both HDM-D Type 2 devices and HDM-DB Type 2 devices are required to:

- Detect H2D Req that target Device-attached Memory
<span id="page-133-2"></span>- • When detected, unconditionally respond with RspIHitI, disregarding all internal states and without changing any internal states (e.g., don't touch the cache)

## <span id="page-133-0"></span>3.3 CXL.mem

### <span id="page-133-1"></span>3.3.1 Introduction

The CXL Memory Protocol is called CXL.mem, and it is a transactional interface between the CPU and Memory. It uses the phy and link layer of CXL when communicating across dies. The protocol can be used for multiple different Memory attach options including when the Memory Controller is located in the Host CPU, when the Memory Controller is within an Accelerator device, or when the Memory Controller is moved to a memory buffer chip. It applies to different Memory types (e.g., volatile, persistent, etc.) and configurations (e.g., flat, hierarchical, etc.) as well.

The CXL.mem provides 3 basic coherence models for CXL.mem Host-managed Device Memory (HDM) address regions exposed by the CXL.mem protocol:

- HDM-H (Host-only Coherent): Used only for Type 3 Devices
- HDM-D (Device Coherent): Used only for legacy Type 2 Devices that rely on CXL.cache to manage coherence with the Host
- HDM-DB (Device Coherent using Back-Invalidate): Can be used by Type 2 Devices or Type 3 Devices

*Note:* The view of the address region must be consistent on the CXL.mem path between the Host and the Device.

> The coherency engine in the CPU interfaces with the Memory (Mem) using CXL.mem requests and responses. In this configuration, the CPU coherency engine is regarded as the CXL.mem Master and the Mem device is regarded as the CXL.mem Subordinate. The CXL.mem Master is the agent which is responsible for sourcing CXL.mem requests (e.g., reads, writes, etc.) and a CXL.mem Subordinate is the agent which is responsible for responding to CXL.mem requests (e.g., data, completions, etc.).

When the Subordinate maps HDM-D/HDM-DB, CXL.mem protocol assumes the presence of a device coherency engine (DCOH). This agent is assumed to be responsible for implementing coherency related functions such as snooping of device caches based on CXL.mem commands and update of Metadata fields.

Support for memory with Metadata is optional but this needs to be negotiated with the Host in advance. If the device supports "Metabits Storage" Feature, this mechanism may be used to negotiate the Metadata configuration. Other negotiation mechanisms are beyond the scope of this specification. If Metadata is not supported by device-attached memory, the DCOH will still need to use the Host supplied Metadata updates to interpret the commands. If Metadata is supported by device-attached memory, it can be used by Host to implement a coarse snoop filter for CPU sockets. In the HDM-H address region, the usage is defined by the Host. The protocol allows for 2 bits of Metadata to be stored and returned.

CXL.mem transactions from Master to Subordinate are called "M2S" and transactions from Subordinate to Master are called "S2M".

Within M2S transactions, there are three message classes:

- Request without data generically called Requests (Req)
- Request with Data (RwD)
- Back-Invalidate Response (BIRsp)

Similarly, within S2M transactions, there are three message classes:

- Response without data generically called No Data Response (NDR)
- Response with data generically called Data Response (DRS)
- Back-Invalidate Snoop (BISnp)

The next sections describe the above message classes and opcodes in detail. Each message in will support 3 variants: 68B Flit, 256B Flit, and PBR Flit. The use of each of these will be negotiated in the physical layer for each link as defined in [Chapter 6.0](#page-286-3).

### <span id="page-134-0"></span>3.3.2 CXL.mem Channel Description

In general, the CXL.mem channels work independently of one another to ensure that forward progress is maintained. Details of the specific ordering allowances and requirements between channels are captured in [Section 3.4.](#page-164-0) Within a channel there are no ordering rules, but exceptions to this are described in [Section 3.3.12.](#page-162-0)

The device interface for CXL.mem defines 6 channels on primary memory protocol and an additional 6 to support direct P2P as shown in [Figure 3-18](#page-134-1). Devices that support HDM-DB must support the BI\* channels (S2M BISnp and M2S BIRsp). Type 2 devices that use the HDM-D memory region may not have the BI\* channels. Type 3 devices (Memory Expansion) may support HDM-DB to support direct peer-to-peer on CXL.io. MLD and G-FAM devices may use HDM-DB to enable multi-host coherence and direct peer-to-peer on CXL.mem. The HDM-DB regions will be known by software and programmed as such in the decode registers and these regions will follow the protocol flows, using the BISnp channels as defined in [Appendix C, "Memory Protocol Tables."](#page-1216-2)

<span id="page-134-1"></span>**Figure 3-18. CXL.mem Channels for Devices**

![](_page_134_Figure_16.jpeg)

For Hosts, the number of channels are defined in [Figure 3-19](#page-135-2). The channel definition is the same as for devices.

<span id="page-135-2"></span>**Figure 3-19. CXL.mem Channels for Hosts**

![](_page_135_Figure_3.jpeg)

#### <span id="page-135-0"></span>3.3.2.1 Direct P2P CXL.mem for Accelerators

<span id="page-135-3"></span>In certain topologies, an accelerator (Type 1, Type 2, or Type 3) device may optionally be enabled to communicate with peer Type 3 memories with CXL.mem protocol. Support for such communication is provided by an additional set of CXL.mem channels, with their directions reversed from conventional CXL.mem as shown in as shown in [Figure 3-18](#page-134-1). These channels exist only on a link between the device and the switch downstream port to which the link is attached. Ordering requirements, message formats, and channel semantics are the same as for conventional CXL.mem. Topologies supporting Direct P2P.mem require an accelerator (requester device) and a target Type 3 peer memory device which are both directly connected to a PBR Edge DSP. PBR routing is required because not all CXL.mem messages contain sufficient information for an HBR switch to determine whether to route between a device and the host or a device and a peer device. Edge DSPs contain tables (FAST and LDST) which enable routing to the proper destination.

Details related to the device in-out dependence covering standard CXL.mem target and the source of Direct P2P CXL.mem and are covered in [Table 3-59](#page-167-0).

#### <span id="page-135-1"></span>3.3.2.2 Snoop Handling with Direct P2P CXL.mem

It is possible for a device that is using the Direct P2P CXL.mem interface to receive a snoop on H2D Req for an address that the device had previously requested over its P2P CXL.mem interface. This could occur, for example, if the host has snoop filtering disabled. Conversely, the device could receive an S2M BISnp from a peer for a line that it had acquired over CXL.cache through the host.

As a result, devices that use the Direct P2P CXL.mem interface are required to track which interface was used when a cacheline was requested and respond normally to snoops using this channel. If the device receives a snoop on a different interface, the device shall respond as though it does not have the address cached returning RspIHitI or BIRspI and shall not change the cacheline state.

> **IMPLEMENTATION NOTE**

How the device tracks which interface was used to request each cacheline is implementation dependent. One method of tracking could be for the device to maintain a table of address ranges, programmed by software with an indication for each range whether the CXL.cache or Direct P2P CXL.mem interface should be used. This table could then be looked up when snoops are received. Other methods may also be used.

### <span id="page-136-0"></span>3.3.3 Back-Invalidate Snoop

<span id="page-136-1"></span>To enable a device to implement an inclusive Snoop Filter for tracking host caching of device memory, a Back-Invalidate Snoop (BISnp) is initiated from the device to change the cache state of the host. The flows related to this channel are captured in [Section 3.5.1](#page-168-1). The definition of "inclusive Snoop Filter" for the purpose of CXL is a device structure that tracks cacheline granular host caching and is a limited size that is a small subset of the total Host Physical Address space supported by the device.

In 68B flits, only the CXL.cache D2H Request flows can be used for device-attached memory to manage coherence with the host as shown in [Section 3.5.2.3.](#page-182-0) This flow is used for addresses with the HDM-D memory attribute. A major constraint with this flow is that the D2H Req channel can be blocked waiting on forward progress of the M2S Request channel which disallows an inclusive Snoop Filter architecture. For the HDM-DB memory region, the BISnp channel (instead of CXL.cache) is used to resolve coherence. CXL host implementations may have a mix of devices with HDM-DB and HDM-D below a Root Port.

The rules related to Back-Invalidate are spread around in different areas of the specification. The following list captures a summary and pointers to requirements:

- Ordering rules in [Section 3.4](#page-164-0)
- Conflict detection flows and blocking in [Section 3.5.1](#page-168-1)
- Protocol Tables in [Section C.1.2](#page-1227-2)
- BI-ID configuration in [Section 9.14](#page-849-2)
- If an outstanding S2M BISnp is pending to an address the device must block M2S Req to the same address until the S2M BISnp is completed with the corresponding M2S BIRsp
- M2S RwD channel must complete/drain without dependence on M2S Req or S2M BISnp

> **IMPLEMENTATION NOTE**

Detailed performance implications of the implementation of an Inclusive Snoop Filter are beyond the scope of this specification, but high-level considerations are captured here:

- The number of cachelines that are tracked in an Inclusive Snoop Filter is determined based on host-processor caching of the address space. This is a function of the use model and the cache size in the host processor with upsizing of 4x or more. The 4x is based on an imprecise estimation of the unknowns in future host implementations and mismatch in Host cache ways/sectors as compared to Snoop-Filter ways/sectors.
- Device should have the capability to track BISnp messages triggered by Snoop Filter capacity evictions without immediately blocking requests on the M2S Req channel when the Inclusive Snoop Filter becomes full. In the case that the BISnp tracking structure becomes full the M2S Req channel will need to be blocked for functional correctness, but the design should size this BISnp tracker to ensure that blocking of the M2S Req channel is a rare event.
<span id="page-137-2"></span>- • The state per cacheline could be implemented as 2 states or 3 states. For 2 states, it would track the host in I vs. A, where A-state would represent "Any" possible MESI state in the host. For 3 states, it would add the precision of S-state tracking in which the Host may have at most a shared copy of the cacheline.

### <span id="page-137-0"></span>3.3.4 QoS Telemetry for Memory

QoS Telemetry for Memory is a mechanism for memory devices to indicate their current load level (DevLoad) in each response message for CXL.mem requests and each completion for (CXL.io) UIO requests. This enables the host or peer requester to meter the issue rate of CXL.mem requests and UIO requests to portions of devices, individual devices, or groups of devices as a function of their load level, optimizing the performance of those memory devices while limiting fabric congestion. This is especially important for CXL hierarchies containing multiple memory types (e.g., DRAM and persistent memory), Multi-Logical-Device (MLD) components, and/or G-FAM Devices (GFDs).

In addition to use cases with hosts that access memory devices, QoS Telemetry for memory supports the UIO Direct P2P to HDM (see [Section 7.7.9](#page-441-4)) and Direct P2P CXL.mem for Accelerators (see [Section 7.7.10](#page-444-2)) use cases. For these, the peer requester for each UIO or .mem request receives a DevLoad indication in each UIO completion or .mem response. For the UIO Direct P2P use case, the peer requester may be native PCIe or CXL. Within this section, "hosts/peers" is a shorthand for referring to host and/or peer requesters that access HDM devices.

Certain aspects of QoS Telemetry are mandatory for current CXL memory devices while other aspects are optional. CXL switches have no unique requirements for supporting QoS Telemetry. It is strongly recommended for Hosts to support QoS Telemetry as guided by the reference model contained in this section. For peer requesters, the importance of supporting QoS Telemetry depends on the device type, its capabilities, and its specific use case(s).

#### <span id="page-137-1"></span>3.3.4.1 QoS Telemetry Overview

The overall goal of QoS Telemetry is for memory devices to provide immediate and ongoing DevLoad feedback to their associated hosts/peers, for use in dynamically adjusting their request-rate throttling. If a device or set of Devices become overloaded, the associated hosts/peers increase their amount of request rate throttling. If such

![](_page_138_Picture_1.jpeg)

Devices become underutilized, the associated hosts/peers reduce their amount of request rate throttling. QoS Telemetry is architected to help hosts/peers avoid overcompensating and/or undercompensating.

Host/peer memory request rate throttling is optional and primarily implementation specific.

<span id="page-138-1"></span>**Table 3-29. Impact of DevLoad Indication on Host/Peer Request Rate Throttling**

| DevLoad Indication Returned in Responses | Host/Peer Request Rate Throttling   |
|------------------------------------------|-------------------------------------|
| Light Load                               | Reduce throttling (if any) soon     |
| Optimal Load                             | Make no change to throttling        |
| Moderate Overload                        | Increase throttling immediately     |
| Severe Overload                          | Invoke heavy throttling immediately |

To accommodate memory devices supporting multiple types of memory more optimally, a device is permitted to implement multiple QoS Classes, which are identified sets of traffic, between which the device supports differentiated QoS and significant performance isolation. For example, a device supporting both DRAM and persistent memory might implement two QoS Classes, one for each type of supported memory. Providing significant performance isolation may require independent internal resources (e.g., individual request queues for each QoS Class).

This version of the specification does not provide architected controls for providing bandwidth management between device QoS Classes.

MLDs provide differentiated QoS on a per-LD basis. MLDs have architected controls specifying the allocated bandwidth fraction for each LD when the MLD becomes overloaded. When the MLD is not overloaded, LDs can use more than their allocated bandwidth fraction, up to specified fraction limits based on maximum sustained device bandwidth.

GFDs provide differentiated QoS on a per-host/peer basis. GFDs have architected controls that specify a QoS Limit Fraction value for each host/peer, based on maximum sustained device bandwidth.

HDM-DB devices send BISnp requests and receive BIRsp responses as a part of processing requests that they receive from host/peer requesters. BISnp and BIRsp messages shall not be tracked by QoS Telemetry mechanisms. If a BISnp triggers a host/peer requester writing back cached data, those transactions will be tracked by QoS Telemetry.

The DevLoad indication from CXL 1.1 memory devices will always indicate Light Load, allowing those devices to operate as best they can with hosts/peers that support QoS Telemetry, though they cannot have their memory request rate actively metered by the host/peer. Light Load is used instead of Optimal Load in case any CXL 1.1 devices share the same host/peer throttling range with current memory devices. If CXL 1.1 devices were to indicate Optimal Load, they would overshadow the DevLoad of any current devices indicating Light Load.

#### <span id="page-138-0"></span>3.3.4.2 Reference Model for Host/Peer Support of QoS Telemetry

Host/peer support for QoS Telemetry is strongly recommended but not mandatory.

QoS Telemetry provides no architected controls for mechanisms in hosts/peers. However, if a host/peer implements independent throttling for multiple distinct sets of memory devices through a given port, the throttling must be based on HDM ranges, which are referred to as host/peer throttling ranges.

The reference model in this section covers recommended aspects for how a host/peer should support QoS Telemetry. Such aspects are not mandatory, but they should help maximize the effectiveness of QoS Telemetry in optimizing memory device performance while providing differentiated QoS and reducing CXL fabric congestion.

Each host/peer is assumed to support distinct throttling levels on a throttling-range basis, represented by Throttle[Range]. Throttle[Range] is periodically adjusted by conceptual parameters NormalDelta and SevereDelta. During each sampling period for a given Throttle[Range], the host/peer records the highest DevLoad indication reported for that throttling range, referred to as LoadMax.

<span id="page-139-1"></span>**Table 3-30. Recommended Host/Peer Adjustment to Request Rate Throttling**

| LoadMax Recorded by Host/Peer | Recommended Adjustment to Request Rate Throttling |  |
|-------------------------------|---------------------------------------------------|--|
| Light Load                    | Throttle[Range] decremented by NormalDelta        |  |
| Optimal Load                  | Throttle[Range] unchanged                         |  |
| Moderate Overload             | Throttle[Range] incremented by NormalDelta        |  |
| Severe Overload               | Throttle[Range] incremented by SevereDelta        |  |

Any increments or decrements to Throttle[Range] should not overflow or underflow legal values, respectively.

Throttle[Range] is expected to be adjusted periodically, every tH nanoseconds unless a more immediate adjustment is warranted. The tH parameter should be configurable by platform-specific software, and ideally configurable on a per-throttling-range basis. When tH expires, the host/peer should update Throttle[Range] based on LoadMax, as shown in [Table 3-30,](#page-139-1) and then reset LoadMax to its minimal value.

Round-trip fabric time is the sum of the time for a request message to travel from host/ peer to Device, plus the time for a response message to travel from Device to host/ peer. The optimal value for tH is anticipated to be a bit larger than the average roundtrip fabric time for the associated set of devices (e.g., a few hundred nanoseconds). To avoid overcompensation by the host/peer, time is needed for the received stream of DevLoad indications in responses to reflect the last Throttle[Range] adjustment before the host/peer makes a new adjustment.

If the host/peer receives a Moderate Overload or Severe Overload indication, it is strongly recommended for the host/peer to make an immediate adjustment in throttling, without waiting for the end of the current tH sampling period. Following that, the host/peer should reset LoadMax and then wait tH nanoseconds before making an additional throttling adjustment, to avoid overcompensating.

#### <span id="page-139-0"></span>3.3.4.3 Memory Device Support for QoS Telemetry

##### 3.3.4.3.1 QoS Telemetry Register Interfaces

An MLD must support a specified set of MLD commands from the MLD Component Command Set as documented in [Section 7.6.7.4](#page-367-4). These MLD commands provide access to a variety of architected capability, control, and status registers for a Fabric Manager to use via the FM API.

A GFD must support a specified set of GFD commands from the GFD Component Management Command Set as documented in [Section 8.2.10.9.10.](#page-755-2) These GFD commands provide access to a variety of architected capability, control, and status registers for a Fabric Manager to use via the FM API.

![](_page_140_Picture_1.jpeg)

If an SLD supports the Memory Device Command set, it must support a specified set of SLD QoS Telemetry commands. See [Section 8.2.10.9](#page-717-3). These SLD commands provide access to a variety of architected capability, control, and status fields for management by system software via the CXL Device Register interface.

Each "architected QoS Telemetry" register is one that is accessible via the above mentioned MLD commands, GFD commands, and/or SLD commands.

##### 3.3.4.3.2 Memory Device QoS Class Support

Each CXL memory device may support one or more QoS Classes. The anticipated typical number is one to four, but higher numbers are not precluded. If a device supports only one type of media, it may be common for it to support one QoS Class. If a device supports two types of media, it may be common for it to support two QoS Classes. A device supporting multiple QoS Classes is referred to as a multi-QoS device.

This version of the specification does not provide architected controls for providing bandwidth management between device QoS Classes. Still, it is strongly recommended that multi-QoS devices track and report DevLoad indications for different QoS Classes independently, and that implementations provide as much performance isolation between different QoS Classes as possible.

##### <span id="page-140-2"></span>3.3.4.3.3 Memory Device Internal Loading (IntLoad)

A CXL memory device must continuously track its internal loading, referred to as IntLoad. A multi-QoS device should do so on a per-QoS-Class basis.

A device must determine IntLoad based at least on its internal request queuing. For example, a simple device may monitor the instantaneous request queue depth to determine which of the four IntLoad indications to report. It may also incorporate other internal resource utilizations, as summarized in [Table 3-31](#page-140-0).

<span id="page-140-0"></span>**Table 3-31. Factors for Determining IntLoad**

| IntLoad           | Queuing Delay inside Device | Device Internal Resource Utilization            |
|-------------------|-----------------------------|-------------------------------------------------|
| Light Load        | Minimal                     | Readily handles more requests                   |
| Optimal Load      | Modest to Moderate          | Optimally utilized                              |
| Moderate Overload | Significant                 | Limiting throughput and/or degrading efficiency |
| Severe Overload   | High                        | Heavily overloaded and/or degrading efficiency  |

The actual method of IntLoad determination is device-specific, but it is strongly recommended that multi-QoS devices implement separate request queues for each QoS Class. For complex devices, it is recommended for them to determine IntLoad based on internal resource utilization beyond just request queue depth monitoring.

Although the IntLoad described in this section is a primary factor in determining which DevLoad indication is returned in device responses, there are other factors that may need to be considered, depending upon the situation (see [Section 3.3.4.3.4](#page-140-1) and [Section 3.3.4.3.5](#page-142-0)).

##### <span id="page-140-1"></span>3.3.4.3.4 Egress Port Backpressure

<span id="page-140-3"></span>Even under a consistent Light Load, a memory device may experience flow control backpressure at its egress port. This is readily caused if an RP is oversubscribed by multiple memory devices below a switch. Prolonged egress port backpressure usually indicates that one or more upstream traffic queues between the device and the RP are full, and the delivery of responses from the device to the host/peer is significantly

delayed. This makes the QoS Telemetry feedback loop less responsive and the overall mechanism less effective. Egress Port Backpressure is an optional normative mechanism to help mitigate the negative effects of this condition.

> **IMPLEMENTATION NOTE**

**Egress Port Backpressure Leading to Larger Request Queue Swings**

When the QoS Telemetry feedback loop is less responsive, the device's request queue depth is prone to larger swings than normal.

When the queue depth is increasing, the delay in the host/peer receiving Moderate Overload or Severe Overload indications results in the queue getting more full than normal, in extreme cases filling completely and forcing the ingress port to exert backpressure to incoming downstream traffic.

When the queue depth is decreasing, the delay in the host/peer receiving Light Load indications results in the queue getting more empty than normal, in extreme cases emptying completely, and causing device throughput to drop unnecessarily.

Use of the Egress Port Backpressure mechanism helps avoid upstream traffic queues between the device and its RP from filling for extended periods, reducing the delay of responses from the device to the host/peer. This makes the QoS Telemetry feedback loop more responsive, helping avoid excessive request queue swings.

> **IMPLEMENTATION NOTE**

**Minimizing Head-of-Line Blocking with Upstream Responses from MLDs/ GFDs**

When one or more upstream traffic queues become full between the MLD and one or more of its congested RPs, head-of-line (HOL) blocking associated with this congestion can delay or block traffic targeting other RPs that are not congested.

Egress port backpressure for extended periods usually indicates that the ingress port queue in the Downstream Switch Port above the device is often full. Responses in that queue targeting congested RPs can block responses targeting uncongested RPs, reducing overall device throughput unnecessarily.

Use of the Egress Port Backpressure mechanism helps reduce the average depth of queues carrying upstream traffic. This reduces the delay of traffic targeting uncongested RPs, increasing overall device throughput.

The Egress Port Congestion Supported capability bit and the Egress Port Congestion Enable control bit are architected QoS Telemetry bits, which indicate support for this optional mechanism plus a means to enable or disable it. The architected Backpressure Average Percentage status field returns a current snapshot of the measured egress port average congestion.

QoS Telemetry architects two thresholds for the percentage of time that the egress port experiences flow control backpressure. This condition is defined as the egress port having flits or messages waiting for transmission but is unable to transmit them due to a lack of suitable flow control credits. If the percentage of congested time is greater than or equal to Egress Moderate Percentage, the device may return a DevLoad indication of Moderate Overload. If the percentage of congested time is greater than or

![](_page_142_Picture_1.jpeg)

equal to Egress Severe Percentage, the device may return a DevLoad indication of Severe Overload. The actual DevLoad indication returned for a given response may be the result of other factors as well.

A hardware mechanism for measuring Egress Port Congestion is described in [Section 3.3.4.3.9](#page-147-1).

##### <span id="page-142-0"></span>3.3.4.3.5 Temporary Throughput Reduction

<span id="page-142-1"></span>There are certain conditions under which a device may temporarily reduce its throughput. Envisioned examples include a non-volatile memory (NVM) device undergoing media maintenance, a device cutting back its throughput for power/thermal reasons, and a DRAM device performing refresh. If a device is significantly reducing its throughput capacity for a temporary period, it may help mitigate this condition by indicating Moderate Overload or Severe Overload in its responses shortly before the condition occurs and only as long as really necessary. This is a device-specific optional mechanism.

The Temporary Throughput Reduction mechanism can give proactive advanced warning to associated hosts/peers, which can then increase their throttling in time to avoid the device's internal request queue(s) from filling up and potentially causing ingress port congestion. The optimum amount of time for providing advanced warning is highly device-specific, and a function of several factors, including the current request rate, the amount of device internal buffering, the level/duration of throughput reduction, and the fabric round-trip time.

A device should not use the mechanism unless conditions truly warrant its use. For example, if the device is currently under Light Load, it's probably not necessary or appropriate to indicate an Overload condition in preparation for a coming event. Similarly, a device that indicates an Overload condition should not continue to indicate the Overload condition past the point where it's needed.

The Temporary Throughput Reduction Supported capability bit and the Temporary Throughput Reduction Enable control bit are architected QoS Telemetry bits, which indicate support for this optional mechanism plus a means to enable or disable it.

> **IMPLEMENTATION NOTE**

**Avoid Unnecessary Use of Temporary Throughput Reduction**

<span id="page-142-3"></span>Ideally, a device should be designed to limit the severity and/or duration of its temporary throughput reduction events enough to where the use of this mechanism is not needed.

##### 3.3.4.3.6 DevLoad Indication by Multi-QoS and Single-QoS SLDs

For SLDs, the DevLoad indication returned in each response is determined by the maximum of the device's IntLoad, Egress Port Congestion state, and Temporary Throughput Reduction state, as detailed in [Section 3.3.4.3.3,](#page-140-2) [Section 3.3.4.3.4](#page-140-1), and [Section 3.3.4.3.5](#page-142-0). For example, if IntLoad indicates Light Load, Egress Port Congestion indicates Moderate Overload, and Temporary Throughput Reduction does not indicate an overload, the resulting DevLoad indication for the response is Moderate Overload.

##### 3.3.4.3.7 DevLoad Indication by Multi-QoS and Single-QoS MLDs

<span id="page-142-2"></span>For MLDs, the DevLoad indication returned in each response is determined by the same factors as for SLDs, with additional factors used for providing differentiated QoS on a per-LD basis. Architected controls specify the allocated bandwidth for each LD as a fraction of total LD traffic when the MLD becomes overloaded. When the MLD is not

overloaded, LDs can use more than their allocated bandwidth fraction, up to specified fraction limits based on maximum sustained device bandwidth, independent of overall LD activity.

Bandwidth utilization for each LD is measured continuously based on current requests being serviced, plus the recent history of requests that have been completed.

Current requests being serviced are tracked by ReqCnt[LD] counters, with one counter per LD. The ReqCnt counter for an LD is incremented each time a request for that LD is received. The ReqCnt counter for an LD is decremented each time a response by that LD is transmitted. ReqCnt reflects instantaneous "committed" utilization, allowing the rapid reflection of incoming requests, especially when requests come in bursts.

The recent history of requests completed is tracked by CmpCnt[LD, Hist] registers, with one set of 16 Hist registers per LD. An architected configurable Completion Collection Interval control for the MLD determines the time interval over which transmitted responses are counted in the active (newest) Hist register/counter. At the end of each interval, the Hist register values for the LD are shifted from newer to older Hist registers, with the oldest value being discarded, and the active (newest) Hist register/ counter being cleared. Further details on the hardware mechanism for CmpCnt[LD, Hist] are described in [Section 3.3.4.3.10.](#page-148-0)

Controls for LD bandwidth management consist of per-LD sets of registers called QoS Allocation Fraction[LD] and QoS Limit Fraction[LD]. For each LD, QoS Allocation Fraction specifies the fraction of current device utilization allocated for the LD across all its QoS classes. QoS Limit Fraction for each LD specifies the fraction of maximum sustained device utilization as a fixed limit for the LD across all its QoS classes, independent of overall MLD activity.

Bandwidth utilization for each LD is based on the sum of its associated ReqCnt and CmpCnt[Hist] counters/registers. CmpCnt[Hist] reflects recently completed requests, and Completion Collection Interval controls how long this period of history covers (i.e., how quickly completed requests are "forgotten"). CmpCnt reflects recent utilization to help avoid overcompensating for bursts of requests.

Together, ReqCnt and CmpCnt[Hist] provide a simple, fair, and tunable way to compute average utilization. A shorter response history emphasizes instantaneous committed utilization, improving responsiveness. A longer response history smooths the average utilization, reducing overcompensation.

ReqCmpBasis is an architected control register that provides the basis for limiting each LD's utilization of the device, independent of overall MLD activity. Because ReqCmpBasis is compared against the sum of ReqCnt[ ] and CmpCnt[ ], its maximum value must be based on the maximum values of ReqCnt[ ] and CmpCnt[ ] summed across all configured LDs. The maximum value of Sum(ReqCnt[\*]) is a function of the device's internal queuing and how many requests it can concurrently service. The maximum value of Sum(CmpCnt[\*,\*]) is a function of the device's maximum request service rate over the period of completion history recorded by CmpCnt[ ], which is directly influenced by the setting of Completion Collection Interval.

The FM programs ReqCmpBasis, the QoS Allocation Fraction array, and the QoS Limit Fraction array to control differentiated QoS between LDs. The FM is permitted to derate ReqCmpBasis below its maximum sustained estimate as a means of limiting power and heat dissipation.

To determine the DevLoad indication to return in each response, the device performs the following calculation:

Calculate TotalLoad = max(IntLoad[QoS], Egress Port Congestion state, Temporary Throughput Reduction state);

Calculate ReqCmpTotal and populate ReqCmpCnt[LD] array element

```
ReqCmpTotal = 0;
For each LD 
   ReqCmpCnt[LD] = ReqCnt[LD] + Sum(CmpCnt[LD, *]);
   ReqCmpTotal += ReqCmpCnt[LD];
```

> **IMPLEMENTATION NOTE**

**Avoiding Recalculation of ReqCmpTotal and ReqCmpCnt[ ] Array**

ReqCmpCnt[ ] is an array that avoids having to recalculate its values later in the algorithm.

To avoid recalculating ReqCmpTotal and ReqCmpCnt[ ] array from scratch to determine the DevLoad indication to return in each response, it is strongly recommended that an implementation maintains these values on a running basis, only incrementally updating them as new requests arrive and responses are transmitted. The details are implementation specific.

> **IMPLEMENTATION NOTE**

**Calculating the Adjusted Allocation Bandwidth**

When the MLD is overloaded, some LDs may be over their allocation while others are within their allocation.

- Those LDs under their allocation (especially inactive LDs) contribute to a "surplus" of bandwidth that can be distributed across active LDs that are above their allocation.
- Those LDs over their allocation claim "their fair share" of that surplus based on their allocation, and the load value for these LDs is based on an "adjusted allocated bandwidth" that includes a prorated share of the surplus.

This adjusted allocation bandwidth algorithm avoids anomalies that otherwise occur when some LDs are using well below their allocation, especially if they are idle.

In subsequent algorithms, certain registers have integer and fraction portions, optimized for implementing the algorithms in dedicated hardware. The integer portion is described as being 16 bits unsigned, although it is permitted to be smaller or larger as needed by the specific implementation. It must be sized such that it will never overflow during normal operation. The fractional portion must be 8 bits. These registers are indicated by their name being in italics.

> **IMPLEMENTATION NOTE**

**Registers with Integer and Fraction Portions**

These registers can hold the product of a 16-bit unsigned integer and an 8-bit fraction, resulting in 24 bits with the radix point being between the upper 16 bits and the lower 8 bits. Rounding to an integer is readily accomplished by adding 0000.80h (0.5 decimal) and truncating the lower 8 bits.

If TotalLoad is Moderate Overload or Severe Overload, calculate the adjusted

```
allocated bandwidth:
   ClaimAllocTotal = 0;
   SurplusTotal = 0;
   For each LD
           AllocCnt = QoS Allocation Fraction[LD] * ReqCmpTotal;
           If this LD is the (single) LD associated with the response
               AllocCntSaved = AllocCnt;
           If ReqCmpCnt[LD] > AllocCnt then
               ClaimAllocTotal += AllocCnt;
           Else
               SurplusTotal += AllocCnt - ReqCmpCnt[LD];
   For the single LD associated with the response
       If ReqCmpCnt[LD] > (AllocCntSaved + AllocCntSaved * SurplusTotal / 
ClaimAllocTotal) then LD is over its adjusted allocated bandwidth; // Use this 
result in the subsequent table
```

> **IMPLEMENTATION NOTE**

**Determination of an LD Being Above its Adjusted Allocated Bandwidth**

The preceding equation requires a division, which is relatively expensive to implement in hardware dedicated for this determination. To enable hardware making this determination more efficiently, the following derived equivalent equation is strongly recommended:

ReqCmpCnt[LD] > (*AllocCntSaved* + *AllocCntSaved* \* *SurplusTotal* / *ClaimAllocTotal*)

(ReqCmpCnt[LD] \* *ClaimAllocTotal*) > (*AllocCntSaved* \* *ClaimAllocTotal* + *AllocCntSaved* \* *SurplusTotal*)

**(ReqCmpCnt[LD] \*** *ClaimAllocTotal***) > (***AllocCntSaved* **\* (***ClaimAllocTotal* **+**  *SurplusTotal***))**

```
// Perform the bandwidth limit calculation for this LD
If ReqCmpCnt[LD] > QoS Limit Fraction [LD] * ReqCmpBasis then LD is over its limit 
BW;
```

<span id="page-145-0"></span>**Table 3-32. Additional Factors for Determining DevLoad in MLDs (Sheet 1 of 2)**

| TotalLoad                     | LD over<br>Limit BW? | LD over Adjusted<br>Allocated BW? | Returned DevLoad Indication |
|-------------------------------|----------------------|-----------------------------------|-----------------------------|
| Light Load or<br>Optimal Load | No                   | -                                 | TotalLoad                   |
|                               | Yes                  | -                                 | Moderate Overload           |

**Table 3-32. Additional Factors for Determining DevLoad in MLDs (Sheet 2 of 2)**

| TotalLoad         | LD over<br>Limit BW? | LD over Adjusted<br>Allocated BW? | Returned DevLoad Indication |
|-------------------|----------------------|-----------------------------------|-----------------------------|
| Moderate Overload | No                   | No                                | Optimal Load                |
|                   | No                   | Yes                               | Moderate Overload           |
|                   | Yes                  | -                                 | Moderate Overload           |
| Severe Overload   | -                    | No                                | Moderate Overload           |
|                   | -                    | Yes                               | Severe Overload             |

The preceding table is based on the following policies for LD bandwidth management:

- The LD is always subject to its QoS Limit Fraction
- For TotalLoad indications of Light Load or Optimal Load, the LD can exceed its QoS Allocation Fraction, up to its QoS Limit Fraction
<span id="page-146-0"></span>- • For TotalLoad indications of Moderate Overload or Severe Overload, LDs with loads up to QoS Allocation Fraction get throttled less than LDs with loads that exceed QoS Allocation Fraction

##### 3.3.4.3.8 DevLoad Indication by Multi-QoS and Single-QoS GFDs

DevLoad indication for GFDs is similar to that for MLDs, with the exception that 12-bit GFD host/peer requester PIDs (RPIDs) scale much higher than the 4-bit LDs for MLDs, and the QoS Allocation Fraction mechanism (based on current device utilization) is not supported for GFDs due to architectural scaling challenges. However, the QoS Limit Fraction mechanism (based on a fixed maximum sustained device utilization) is supported for GFDs, and architected controls specify the fraction limits.

Bandwidth utilization for each RPID is measured continuously based on current requests being serviced, plus the recent history of requests that have been completed.

Current requests that are being serviced are tracked by ReqCnt[RPID] counters, with one counter per RPID. The ReqCnt counter for an RPID is incremented each time a request from that RPID is received. The ReqCnt counter for an RPID is decremented each time a response to that RPID is transmitted. ReqCnt reflects instantaneous "committed" utilization, allowing the rapid reflection of incoming requests, especially when requests come in bursts.

The recent history of requests completed is tracked by CmpCnt[RPID, Hist] registers, with one set of 16 Hist registers per RPID. An architected configurable Completion Collection Interval control for the GFD determines the time interval over which transmitted responses are counted in the active (newest) Hist register/counter. At the end of each interval, the Hist register values for the RPID are shifted from newer to older Hist registers, with the oldest value being discarded, and the active (newest) Hist register/counter being cleared. Further details on the hardware mechanism for CmpCnt[RPID, Hist] are described in [Section 3.3.4.3.10.](#page-148-0)

Controls for RPID bandwidth management consist of per-RPID sets of registers called QoS Limit Fraction[RPID]. QoS Limit Fraction for each RPID specifies the fraction of maximum sustained device utilization as a fixed limit for the RPID across all its QoS classes, independent of overall GFD activity.

Bandwidth utilization for each RPID is based on the sum of its associated ReqCnt and CmpCnt[Hist] counters/registers. CmpCnt[Hist] reflects recently completed requests, and Completion Collection Interval controls how long this period of history covers (i.e., how quickly completed requests are "forgotten"). CmpCnt reflects recent utilization to help avoid overcompensating for bursts of requests.

Together, ReqCnt and CmpCnt[Hist] provide a simple, fair, and tunable way to compute average utilization. A shorter response history emphasizes instantaneous committed utilization, thus improving responsiveness. A longer response history smooths the average utilization, thus reducing overcompensation.

ReqCmpBasis is an architected control register that provides the basis for limiting each RPID's utilization of the device, independent of overall GFD activity. Because ReqCmpBasis is compared against the sum of ReqCnt[ ] and CmpCnt[ ], its maximum value must be based on the maximum values of ReqCnt[ ] and CmpCnt[ ] summed across all configured RPIDs. The maximum value of Sum(ReqCnt[\*]) is a function of the device's internal queuing and how many requests it can concurrently service. The maximum value of Sum(CmpCnt[\*,\*]) is a function of the device's maximum request service rate over the period of completion history recorded by CmpCnt[ ], which is directly influenced by the setting of Completion Collection Interval.

The FM programs ReqCmpBasis and the QoS Limit Fraction array to control differentiated QoS between RPIDs. The FM is permitted to derate ReqCmpBasis below its maximum sustained estimate as a means of limiting power and heat dissipation.

To determine the DevLoad indication to return in each response, the device performs the following calculation:

Calculate TotalLoad = max(IntLoad[QoS], Egress Port Congestion state, Temporary Throughput Reduction state);

// Perform the bandwidth limit calculation for this RPID

If ReqCmpCnt[RPID] > QoS Limit Fraction[RPID] \* ReqCmpBasis then the RPID is over its limit BW;

<span id="page-147-0"></span>**Table 3-33. Additional Factors for Determining DevLoad in MLDs/GFDs**

| TotalLoad                  | RPID over<br>Limit BW? | Returned DevLoad Indication |
|----------------------------|------------------------|-----------------------------|
| Light Load or Optimal Load | No                     | TotalLoad                   |
|                            | Yes                    | Moderate Overload           |
| Moderate Overload          | No                     | Moderate Overload           |
|                            | Yes                    | Severe Overload             |
| Severe Overload            | -                      | Severe Overload             |

[Table 3-33](#page-147-0) is based on the following policies for RPID bandwidth management:

- The RPID is always subject to its QoS Limit Fraction
<span id="page-147-2"></span>- • For TotalLoad indications of Moderate Overload, RPIDs with loads up to QoS Limit Fraction get throttled less than RPIDs with loads that exceed QoS Limit Fraction

##### <span id="page-147-1"></span>3.3.4.3.9 Egress Port Congestion Measurement Mechanism

This hardware mechanism measures the average egress port congestion on a rolling percentage basis.

FCBP (Flow Control Backpressured): this binary condition indicates the instantaneous state of the egress port. It is true if the port has messages or flits available to transmit but is unable to transmit any of them due to a lack of suitable flow control credits.

Backpressure Sample Interval register: this architected control register specifies the fixed interval in nanoseconds at which FCBP is sampled. It has a range of 0-31. One hundred samples are recorded, so a setting of 1 yields 100 ns of history. A setting of 31 yields 3.1 us of history. A setting of 0 disables the measurement mechanism, and it must indicate an average congestion percentage of 0.

BPhist[100] bit array: this stores the 100 most-recent FCBP samples. It is not accessible by software.

Backpressure Average Percentage: when this architected status register is read, it indicates the current number of Set bits in BPhist[100]. It ranges in value from 0 to 100.

The actual implementation of BPhist[100] and Backpressure Average Percentage is device specific. Here is a possible implementation approach:

- BPhist[100] is a shift register
- Backpressure Average Percentage is an up/down counter
- With each new FCBP sample:
  - If the new sample (not yet in BPhist) and the oldest sample in BPhist are both 0 or both 1, no change is made to Backpressure Average Percentage.
  - If the new sample is 1 and the oldest sample is 0, increment Backpressure Average Percentage.
  - If the new sample is 0 and the oldest sample is 1, decrement Backpressure Average Percentage.
<span id="page-148-1"></span>- • Shift BPhist[100], discarding the oldest sample and entering the new sample

##### <span id="page-148-0"></span>3.3.4.3.10 Recent Transmitted Responses Measurement Mechanism

This hardware mechanism measures the number of recently transmitted responses on a per-host/peer basis in the most recent 16 intervals of a configured time period. Hosts are identified by a Requester ID (ReqID), which is the LD-ID for MLDs and the RPID for GFDs.

Completion Collection Interval register: this architected control register specifies the interval over which transmitted responses are counted in an active Hist register. It has a range is 0-127. A setting of 1 yields 16 nanoseconds of history. A setting of 127 yields about 2 us of history. A setting of 0 disables the measurement mechanism, and it must indicate a response count of 0.

CmpCnt[ReqID, 16] registers: these registers track the total of recent transmitted responses on a per-host/peer basis. CmpCnt[ReqID, 0] is a counter and is the newest value, while CmpCnt[ReqID, 1:15] are registers. These registers are not directly visible to software.

For each ReqID, at the end of each Completion Collection Interval:

- The 16 CmpCnt[ReqID, \*] register values are shifted from newer to older
- The CmpCnt[ReqID, 15] Hist register value is discarded
- The CmpCnt[ReqID, 0] register is cleared and it is armed to count transmitted responses in the next interval

### <span id="page-149-0"></span>3.3.5 M2S Request (Req)

<span id="page-149-2"></span>The Req message class generically contains reads, invalidates, and signals going from the Master to the Subordinate.

<span id="page-149-1"></span>**Table 3-34. M2S Request Fields (Sheet 1 of 2)**

|               | Width (Bits) |              |             |                                                                                                                                                                                                                                                                                                                                                                                                                                                |  |
|---------------|--------------|--------------|-------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--|
| Field         | 68B<br>Flit  | 256B<br>Flit | PBR<br>Flit | Description                                                                                                                                                                                                                                                                                                                                                                                                                                    |  |
| Valid         |              | 1            |             | The valid signal indicates that this is a valid request                                                                                                                                                                                                                                                                                                                                                                                        |  |
| MemOpcode     | 4            |              |             | Memory Operation: This specifies which, if any, operation needs to be performed on the data and associated information. Details in Table 3-35.                                                                                                                                                                                                                                                                                                 |  |
| SnpType       | 3            |              |             | Snoop Type: This specifies what snoop type, if any, needs to be issued by the DCOH and the minimum coherency state required by the Host. Details in Table 3-38.  This field is used to indicate the Length Index for the TEUpdate opcode.                                                                                                                                                                                                      |  |
| MetaField     | 2            |              |             | Metadata Field: Up to 3 Metadata Fields can be addressed. This specifies which, if any, Metadata Field needs to be updated. Details of Metadata Field in Table 3-36. If the Subordinate does not support memory with Metadata, this field will still be used by the DCOH for interpreting Host commands as described in Table 3-37.                                                                                                            |  |
| MetaValue     | 2            |              |             | Metadata Value: When MetaField is not No-Op, this specifies the value to which the field needs to be updated. Details in Table 3-37. If the Subordinate does not support memory with Metadata, this field will still be used by the device coherence engine for interpreting Host commands as described in Table 3-37.  For the TEUpdate message, this field carries the TE state change value where 00b is TE cleared and 01b is TE set.      |  |
| Tag           | 16           |              |             | The Tag field is used to specify the source entry in the Master which is pre-allocated for the duration of the CXL.mem transaction. This value needs to be reflected with the response from the Subordinate so the response can be routed appropriately. The exceptions are the MemRdFwd and MemWrFwd opcodes as described in Table 3-35.  Note: The Tag field has no explicit requirement to be unique.                                       |  |
| Address[5]    | 1            | (            | )           | Address[5] is provisioned for future usages such as critical chunk first for 68B flit, but this is not included in a 256B flit.                                                                                                                                                                                                                                                                                                                |  |
| Address[51:6] |              | 46           |             | This field specifies the Host Physical Address associated with the MemOpcode.                                                                                                                                                                                                                                                                                                                                                                  |  |
| LD-ID[3:0]    |              | 4            | 0           | Logical Device Identifier: This identifies a Logical Device within a Multiple-Logical Device. Not applicable in PBR mode where SPID infers this field.                                                                                                                                                                                                                                                                                         |  |
| SPID          |              | 0            | 12          | Source PID                                                                                                                                                                                                                                                                                                                                                                                                                                     |  |
| DPID          |              | 0            | 12          | Destination PID                                                                                                                                                                                                                                                                                                                                                                                                                                |  |
| CKID          | 0 13         |              | 3           | Context Key ID: Optional key ID that references preconfigured key material utilized for device-based data-at-rest encryption. If the device has been configured to utilize CKID-based device encryption and locked utilizing the CXL Trusted Execution Environment (TEE) Security Protocol (TSP), then this field shall be valid for Data Read access types (MemRd/MemRdTEE/MemRdData*/MemSpecRd*) and treated as reserved for other messages. |  |

Table 3-34. M2S Request Fields (Sheet 2 of 2)

|       | Width (Bits) |              |             |                                                                                                                                                 |  |
|-------|--------------|--------------|-------------|-------------------------------------------------------------------------------------------------------------------------------------------------|--|
| Field | 68B<br>Flit  | 256B<br>Flit | PBR<br>Flit | Description                                                                                                                                     |  |
| RSVD  | 6            | 7            |             | Reserved                                                                                                                                        |  |
| tc    | 2            |              |             | Traffic Class: This can be used by the Master to specify the Quality of Service associated with the request. This is reserved for future usage. |  |
| Total | 87           | 100          | 120         |                                                                                                                                                 |  |

<span id="page-150-0"></span>**Table 3-35. M2S Req Memory Opcodes (Sheet 1 of 2)**

| Opcode                    | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | Encoding |
|---------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|
| MemInv                    | Invalidation request from the Master. Primarily for Metadata updates. No data read or write required. If SnpType field contains valid commands, perform required snoops.                                                                                                                                                                                                                                                                                                                                                                                                                     | 0000b    |
| MemRd                     | Normal memory data read operation. If MetaField contains valid commands, perform Metadata updates. If SnpType field contains valid commands, perform required snoops.                                                                                                                                                                                                                                                                                                                                                                                                                        | 0001b    |
| MemRdData                 | Normal Memory data read operation. MetaField has no impact on the coherence state. MetaValue is to be ignored. Instead, update Meta0-State as follows:  If initial Meta0-State value = 'I', update Meta0-State value to 'A'  Else, no update required  If SnpType field contains valid commands, perform required snoops.  MetaField encoding of Extended Meta-State (EMS) follows the rules for it in Table 3-36.                                                                                                                                                                           | 0010b    |
| MemRdFwd                  | This is an indication from the Host that data can be directly forwarded from device-attached memory to the device without any completion to the Host. This is only sent as a result of a CXL.cache D2H read request to device-attached memory that is mapped as HDM-D. The Tag field contains the reflected CQID sent along with the D2H read request. The SnpType is always No-Op for this Opcode. The caching state of the line is reflected in the MetaO-State value.  Note: This message is not sent to devices that have device-attached memory that is mapped only as HDM-H or HDM-DB. | 0011b    |
| MemWrFwd                  | This is an indication from the Host to the device that it owns the line and can update it without any completion to the Host. This is only sent as a result of a CXL.cache D2H write request to device-attached memory that is mapped as HDM-D. The Tag field contains the reflected CQID sent along with the D2H write request. The SnpType is always No-Op for this Opcode. The caching state of the line is reflected in the Meta0-State value.  Note: This message is not sent to devices that have device-attached memory that is mapped only as HDM-H or HDM-DB.                       | 0100b    |
| MemRdTEE <sup>1</sup>     | Same as MemRd but with the Trusted Execution Environment (TEE) attribute. See Section 11.5.4.5 for description of TEE attribute handling.                                                                                                                                                                                                                                                                                                                                                                                                                                                    | 0101b    |
| MemRdDataTEE <sup>1</sup> | Same as MemRdData but with the Trusted Execution Environment (TEE) attribute. See Section 11.5.4.5 for description of TEE attribute handling.                                                                                                                                                                                                                                                                                                                                                                                                                                                | 0110b    |
| MemInvTEE                 | Same as MemInv but with the Trusted Execution Environment (TEE) attribute. See Section 11.5.4.5 for description of TEE attribute handling.                                                                                                                                                                                                                                                                                                                                                                                                                                                   | 0111b    |
| MemSpecRd                 | Memory Speculative Read is issued to start a memory access before the home agent has resolved coherence to reduce access latency. This command does not receive a completion message. The Tag, MetaField, MetaValue, and SnpType are reserved. See Section 3.5.3.1 for a description of the use case.                                                                                                                                                                                                                                                                                        | 1000b    |
| MemInvNT                  | This is similar to the MemInv command except that the NT is a hint that indicates the invalidation is non-temporal and the writeback is expected soon. However, this is a hint and not a guarantee. If the target is locked utilizing TSP, the target shall decode this opcode as MemInvP. If the target is not locked, the target shall decode this opcode as MemInvNT. See Section 11.5 for TSP.                                                                                                                                                                                           | 1001b    |
| MemInvP                   | Memory invalidation with precise TE State. If the target is locked utilizing TSP, the target shall decode this opcode as MemInvP. If the target is not locked, the target shall decode this opcode as MemInvNT. See Section 11.5 for TSP.                                                                                                                                                                                                                                                                                                                                                    |          |

**Table 3-35. M2S Req Memory Opcodes (Sheet 2 of 2)**

| Opcode        | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | Encoding |  |  |
|---------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|--|--|
| MemClnEvct    | Memory Clean Evict is a message that is similar to MemInv, but intent to indicate host<br>going to I-state and does not require Meta0-State return. This message is supported only<br>to the HDM-DB address region.                                                                                                                                                                                                                                                                                                                       | 1010b    |  |  |
| MemInvPTEE    | Same as MemInvP but with the Trusted Execution Environment (TEE) attribute. See<br>Section 11.5.4.5 for description of TEE attribute handling.                                                                                                                                                                                                                                                                                                                                                                                            | 1011b    |  |  |
| MemSpecRdTEE1 | Same as MemSpecRd but with Trusted Execution Environment (TEE) attribute. See<br>Section 11.5.4.5 for description of TEE attribute handling.                                                                                                                                                                                                                                                                                                                                                                                              | 1100b    |  |  |
| TEUpdate1     | Update of the TE state for the memory region. The memory region update is defined by<br>the length-index field (passed in SnpType bits). The lower address bits in the message<br>may be set to allow routing of the message to reach the correct interleave set target;<br>however, the lower bits are masked to the natural alignment of the length when updating<br>TE state. The MetaValue field defines the new TE state that supports 00b to clear and 01b<br>to set. See details of the use of this message in Section 11.5.4.5.3. | 1101b    |  |  |
| MemClnEvctTEE | Same as MemClnEvct but with the Trusted Execution Environment (TEE) attribute. See<br>Section 11.5.4.5 for description of TEE attribute handling.                                                                                                                                                                                                                                                                                                                                                                                         | 1110b    |  |  |
| MemClnEvctU   | Same as MemClnEvct but TE State is not conveyed and assumed to be unknown.                                                                                                                                                                                                                                                                                                                                                                                                                                                                | 1111b    |  |  |

<span id="page-151-1"></span><span id="page-155-2"></span><sup>1.</sup> Supported only in 256B and PBR Flit messages and considered Reserved in 68B Flit messages.

<span id="page-151-2"></span><span id="page-151-0"></span>**Table 3-36. Metadata Field Definition**

| MetaField                 | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | Encoding |
|---------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|
| Meta0-State               | Update the Metadata bits with the value in the Metadata Value field. Details of<br>MetaValue associated with Meta0-State in Table 3-37.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | 00b      |
| Extended Meta-State (EMS) | This encoding has different interpretation in different channels:<br>•<br>M2S Req usage indicates that the request requires the Extended<br>MetaValue to be returned from the device in the response unless an error<br>condition occurs.<br>•<br>M2S RwD and S2M DRS use this to indication that the Extended<br>MetaValue is attached to the message as a Trailer. This size of the<br>MetaValue is configurable up to 32 bits.<br>•<br>Other channels do not use this encoding and it should be considered<br>Reserved.<br>For HDM-DB, the MetaValue is defined in Table 3-37 for coherence resolution,<br>Reserved for HDM-H.<br>This encoding is not used for HDM-D. | 01b      |
| Reserved                  | Reserved                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | 10b      |
| No-Op                     | No Metadata operation. The MetaValue field is Reserved.<br>For NDR/DRS messages that would return Metadata, this encoding can be<br>used in case of an error in Metadata storage (standard 2-bits or EMD) or if the<br>device does not store Metadata.                                                                                                                                                                                                                                                                                                                                                                                                                    | 11b      |

<span id="page-152-3"></span><span id="page-152-0"></span>**Table 3-37. Meta0-State Value Definition (HDM-D/HDM-DB Devices)1**

| Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | Encoding |
|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|
| Invalid (I): Indicates the host does not have a cacheable copy of the line. The DCOH can use this<br>information to grant exclusive ownership of the line to the device.<br>Note: When paired with a MemOpcode = MemInv and SnpType = SnpInv, this is used to communicate<br>that the device should flush this line from its caches, if cached, to device-attached memory<br>resulting in all caches ending in I.                                                             | 00b      |
| Explicit No-Op: Used only when MetaField is Extended Meta-State in HDM-DB requests to indicate that a<br>coherence state update is not requested. For all other cases this is considered a Reserved.                                                                                                                                                                                                                                                                          | 01b      |
| Any (A): Indicates the host may have a shared, exclusive, or modified copy of the line. The DCOH can<br>use this information to interpret that the Host likely wants to update the line and the device should not<br>be given a copy of the line without resolving coherence with the host using the flow appropriate for the<br>memory type.                                                                                                                                 | 10b      |
| Shared (S): Indicates the host may have at most a shared copy of the line. The DCOH can use this<br>information to interpret that the Host does not have an exclusive or modified copy of the line. If the<br>device wants a shared or current copy of the line, the DCOH can provide this without informing the Host.<br>If the device wants an exclusive copy of the line, the DCOH must resolve coherence with the Host using<br>the flow appropriate for the memory type. | 11b      |

<sup>1.</sup> HDM-H use case in Type 3 devices have Meta0-State definition that is host specific, so the definition in this table does not apply for the HDM-H address region in devices.

<span id="page-152-1"></span>**Table 3-38. Snoop Type Definition**

| SnpType Description | Description                                                                                                                                                                                                | Encoding |
|---------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|
| No-Op               | No snoop needs to be performed                                                                                                                                                                             | 000b     |
| SnpData             | Snoop may be required - the requester needs at least a Shared copy of the line.<br>Device may choose to give an exclusive copy of the line as well.                                                        | 001b     |
| SnpCur              | Snoop may be required - the requester needs the current value of the line.<br>Requester guarantees the line will not be cached. Device need not change the state<br>of the line in its caches, if present. | 010b     |
| SnpInv              | Snoop may be required - the requester needs an exclusive copy of the line.                                                                                                                                 | 011b     |
| Reserved            | Reserved                                                                                                                                                                                                   | 1xxb     |

Valid uses of M2S request semantics are described in [Table 3-39](#page-152-2) but are not the complete set of legal flows. For a complete set of legal combinations, see [Appendix C](#page-1216-2).

<span id="page-152-2"></span>**Table 3-39. M2S Req Usage (Sheet 1 of 2)**

| M2S Req  | MetaField   | Meta<br>Value | SnpType | S2M NDR           | S2M DRS | Description                                                                                                                             |
|----------|-------------|---------------|---------|-------------------|---------|-----------------------------------------------------------------------------------------------------------------------------------------|
| MemRd    | Meta0-State | A             | SnpInv  | Cmp-E             | MemData | The Host wants an exclusive copy of the line                                                                                            |
| MemRd    | Meta0-State | S             | SnpData | Cmp-S or<br>Cmp-E | MemData | The Host wants a shared copy of the line                                                                                                |
| MemRd    | No-Op       | N/A1          | SnpCur  | Cmp               | MemData | The Host wants a non-cacheable but current<br>value of the line                                                                         |
| MemRd    | No-Op       | N/A1          | SnpInv  | Cmp               | MemData | The Host wants a non-cacheable value of the<br>line and the device should invalidate the line<br>from its caches                        |
| MemInv   | Meta0-State | A             | SnpInv  | Cmp-E             | N/A     | The Host wants ownership of the line without<br>data                                                                                    |
| MemInvNT | Meta0-State | A             | SnpInv  | Cmp-E             | N/A     | The Host wants ownership of the line without<br>data. However, the Host expects this to be<br>non-temporal and may do a writeback soon. |

Table 3-39. M2S Req Usage (Sheet 2 of 2)

| M2S Req    | MetaField   | Meta<br>Value    | SnpType | S2M NDR           | S2M DRS | Description                                                                                                                                             |
|------------|-------------|------------------|---------|-------------------|---------|---------------------------------------------------------------------------------------------------------------------------------------------------------|
| MemInv     | Meta0-State | 1                | SnpInv  | Cmp               | N/A     | The Host wants the device to invalidate the line from its caches                                                                                        |
| MemRdData  | No-Op       | N/A <sup>1</sup> | SnpData | Cmp-S or<br>Cmp-E | MemData | The Host wants a cacheable copy in either exclusive or shared state                                                                                     |
| MemClnEvct | Meta0-State | 1                | No-Op   | Ctp               | N/A     | Host is dropping E or S state from its cache and leaving the line in I-state. This message allows the Device to clean the Snoop Filter (or BIAS table). |

<span id="page-153-3"></span><sup>1.</sup> N/A in the MetaValue indicates that the entire field is considered Reserved (cleared to 0 by sender and ignored by receiver).

### <span id="page-153-0"></span>3.3.6 M2S Request with Data (RwD)

<span id="page-153-2"></span>The Request with Data (RwD) message class generally contains writes from the Master to the Subordinate.

<span id="page-153-1"></span>**Table 3-40. M2S RwD Fields (Sheet 1 of 2)**

|               | Width (Bits) |              |             |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |  |  |  |
|---------------|--------------|--------------|-------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--|--|--|
| Field         | 68B<br>Flit  | 256B<br>Flit | PBR<br>Flit | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |  |  |  |
| Valid         |              | 1            |             | The valid signal indicates that this is a valid request.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |  |  |  |
| MemOpcode     | 4            |              |             | Memory Operation: This specifies which, if any, operation needs to be performed on the data and associated information. Details in Table 3-41.                                                                                                                                                                                                                                                                                                                                                                                                                                                   |  |  |  |
| SnpType       | 3            |              |             | Snoop Type: This specifies what snoop type, if any, needs to be issued by the DCOH and the minimum coherency state required by the Host. Details in Table 3-38.                                                                                                                                                                                                                                                                                                                                                                                                                                  |  |  |  |
| MetaField     | 2            |              |             | Metadata Field: Up to 3 Metadata Fields can be addressed. This specifies which, if any, Metadata Field needs to be updated. Details of Metadata Field in Table 3-36. If the Subordinate does not support memory with Metadata, this field will still be used by the DCOH for interpreting Host commands as described in Table 3-37.                                                                                                                                                                                                                                                              |  |  |  |
| MetaValue     | 2            |              |             | Metadata Value: When MetaField is not No-Op, this specifies the value the field needs to be updated to. Details in Table 3-37. If the Subordinate does not support memory with Metadata, this field will still be used by the device coherence engine for interpreting Host commands as described in Table 3-37.                                                                                                                                                                                                                                                                                 |  |  |  |
| Tag           | 16           |              |             | The Tag field is used to specify the source entry in the Master which is pre-allocated for the duration of the CXL.mem transaction. This value needs to be reflected with the response from the Subordinate so the response can be routed appropriately. For BIConflict, the tag encoding must use the same value as the pending M2S Req message (if one exists) which the BISnp found to be in conflict. This requirement is necessary to use Tag for fabric ordering of S2M NDR (Cmp* and BIConflictAck ordering for same tag).  Note: The Tag field has no explicit requirement to be unique. |  |  |  |
| Address[51:6] | 46           |              |             | This field specifies the Host Physical Address associated with the MemOpcode.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |  |  |  |
| Poison        | 1            |              |             | The Poison bit indicates that the data contains an error. The handling of poisoned data is device specific. See Chapter 12.0 for more details.                                                                                                                                                                                                                                                                                                                                                                                                                                                   |  |  |  |

Table 3-40. M2S RwD Fields (Sheet 2 of 2)

|                       | Width (Bits) |              |             |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |  |
|-----------------------|--------------|--------------|-------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--|
| Field                 | 68B<br>Flit  | 256B<br>Flit | PBR<br>Flit | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |  |
| TRP<br>(formerly BEP) | 0            | ) 1          |             | Trailer Present: Indicates that a trailer is included on the message. The trailer size for RwD is defined in Table 3-43. The trailer is observed in the Link Layer as a G-Slot following a 64B data payload.  The baseline requirement for this bit is to enable only Byte Enables for partial writes (MemWrPtl). This bit is also optionally extended for Extend-Metadata indication.  Note: This bit was formerly referred to as Byte-Enables Present (BEP), but has been redefined as part of an optional extension to support message trailers. |  |
| LD-ID[3:0]            | 4 0          |              | 0           | Logical Device Identifier: This identifies a logical device within a multiple-logical device. Not applicable in PBR messages where SPID infers this field.                                                                                                                                                                                                                                                                                                                                                                                          |  |
| SPID                  | 0 12         |              | 12          | Source PID                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |  |
| DPID                  | 0 12         |              | 12          | Destination PID                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |  |
| CKID                  | 0 13         |              | 3           | Context Key ID: Optional key ID that references preconfigured key material utilized for device-based data-at-rest encryption. If the device has been configured to utilize CKID-based device encryption and locked utilizing the CXL Trusted Execution Environment (TEE) Security Protocol (TSP), then this field shall be valid for accesses that carry a non-reserved payload or cause a memory read to occur (MemWr*, MemRdFill*) and reserved for other cases (BIConflict).                                                                     |  |
| RSVD                  | 6            | 9            |             | Reserved                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |  |
| TC                    | 2            |              |             | Traffic Class: This can be used by the Master to specify the Quality of Service associated with the request. This is reserved for future usage.                                                                                                                                                                                                                                                                                                                                                                                                     |  |
| Total                 | 87           | 37 104 124   |             |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |  |

<span id="page-154-1"></span><span id="page-154-0"></span>Table 3-41. M2S RwD Memory Opcodes (Sheet 1 of 2)

| Opcode     | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | Encoding |
|------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|
| MemWr      | Memory write command. Used for full cacheline writes. If MetaField contains valid commands, perform Metadata updates. If SnpType field contains valid commands, perform required snoops. If the snoop hits a Modified cacheline in the device, the DCOH will invalidate the cache and write the data from the Host to device-attached memory.                                                                                                                                                                                                                                     | 0001b    |
| MemWrPtI   | Memory Write Partial. Contains 64 byte enables, one for each byte of data. If MetaField contains valid commands, perform Metadata updates. If SnpType field contains valid commands, perform required snoops. If the snoop hits a Modified cacheline in the device, the DCOH will need to perform a merge, invalidate the cache, and write the contents back to device-attached memory.  Note: This command cannot be used with host-side memory encryption unless byte-enable encodings are aligned with encryption boundaries (32B aligned is an example which may be allowed). | 0010b    |
| BIConflict | Part of conflict flow for BISnp indicating that the host observed a conflicting coherent request to the same cacheline address. See Section 3.5.1 for details.  This message carries a 64B payload as required by the RwD channel, but the payload bytes are reserved (cleared to all 0s). This message is sent on the RwD channel because the dependence rules on this channel allow for a low-complexity flow from a deadlock-avoidance point of view.                                                                                                                          | 0100b    |

**Table 3-41. M2S RwD Memory Opcodes (Sheet 2 of 2)**

| Opcode        | Description                                                                                                                                                                                                                                                                                                                                                                        | Encoding          |  |  |
|---------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------|--|--|
| MemRdFill1    | This is a simple read command equivalent to MemRd but never changes coherence state<br>(MetaField=No-Op, SnpType=No-Op). The use of this command is intended for partial<br>write data that is merging in the host with host-side encryption. With host-side<br>encryption, it is not possible to merge partial data in the device as an attribute of the way<br>encryption works. | 0101b             |  |  |
|               | This message carries a 64B payload as required by the RwD channel; however, the<br>payload bytes are reserved (i.e., cleared to all 0s). This message is sent on the RwD<br>channel because the dependence rules on this channel allow for a low-complexity flow<br>from a deadlock-avoidance point of view.                                                                       |                   |  |  |
| MemWrTEE1     | Same as MemWr but with the Trusted Execution Environment (TEE) attribute. See<br>Section 11.5.4.5 for description of TEE attribute handling.                                                                                                                                                                                                                                       | 1001b             |  |  |
| MemWrPtlTEE1  | Same as MemWrPtl but with the Trusted Execution Environment (TEE) attribute. See<br>Section 11.5.4.5 for description of TEE attribute handling.                                                                                                                                                                                                                                    | 1010b             |  |  |
| MemRdFillTEE1 | Same as MemRdFill but with the Trusted Execution Environment (TEE) attribute. See<br>Section 11.5.4.5 for description of TEE attribute handling.                                                                                                                                                                                                                                   | 1101b             |  |  |
| Reserved      | Reserved                                                                                                                                                                                                                                                                                                                                                                           | <others></others> |  |  |

<sup>1.</sup> Supported only in 256B and PBR Flit messages and considered reserved in 68B Flit messages.

The definition of other fields are consistent with M2S Req (see [Section 3.3.12\)](#page-162-0). Valid uses of M2S RwD semantics are described in [Table 3-42](#page-155-1) but are not complete set of legal flows. For a complete set of legal combinations, see [Appendix C](#page-1216-2).

<span id="page-155-1"></span>**Table 3-42. M2S RwD Usage**

| M2S RwD  | MetaField                        | Meta<br>Value | SnpType                                                                                                                         | S2M NDR | Description                                                                                                                                                                                                                                                                              |
|----------|----------------------------------|---------------|---------------------------------------------------------------------------------------------------------------------------------|---------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| MemWr    | Meta0-State                      | I             | No-Op                                                                                                                           | Cmp     | The Host wants to write the cacheline back to<br>memory and does not retain a cacheable copy.                                                                                                                                                                                            |
| MemWr    | Meta0-State                      | A             | No-Op                                                                                                                           | Cmp     | The Host wants to write the cacheline back to<br>memory and retains a cacheable copy in shared,<br>exclusive or modified state.                                                                                                                                                          |
| MemWr    | Meta0-State                      | I             | SnpInv                                                                                                                          | Cmp     | The Host wants to write the cacheline to memory<br>and does not retain a cacheable copy. In addition,<br>the Host did not get ownership of the cacheline<br>before doing this write and needs the device to<br>snoop-invalidate its caches before performing the<br>writeback to memory. |
| MemWrPtl | Meta0-State                      | I             | SnpInv                                                                                                                          | Cmp     | Same as the above row except the data being<br>written is partial and the device needs to merge the<br>data if it finds a copy of the cacheline in its caches.                                                                                                                           |

#### <span id="page-155-0"></span>3.3.6.1 Trailer Present for RwD (256B Flit)

In 256B Flit mode, a Trailer Present bit (TRP; formerly BEP, Byte-Enables Present) bit is included with the message header that indicates whether a Trailer slot is included at the end of the message. The trailer can be up to 96 bits.

Byte Enables field is 64 bits wide and indicates which of the bytes are valid for the contained data.

The Extended Metadata (EMD) trailer can be up to 32 bits. [Section 8.2.4.31](#page-597-1) describes the registers that aid in discovery of device's EMD capability and EMD related configuration of the device. The mechanism for discovering the host's EMD capabilities and EMD related configuration of the host is host-specific. The host and the device must be configured in a consistent manner.

<span id="page-156-4"></span><span id="page-156-1"></span>**Table 3-43. RwD Trailers** 

| Opcode/<br>Message       | MetaField | TRP | Trailer Size<br>Required | Description                                                                     |
|--------------------------|-----------|-----|--------------------------|---------------------------------------------------------------------------------|
| MemWr/                   | EMS       | 1   | 32 bits                  | Trailer bits[31:0] defined as EMD.                                              |
| MemWrTEE                 | No-OP/MS0 | 0   | No Trailer               |                                                                                 |
| MemWrPtI/<br>MemWrPtITEE | EMS       | 1   | 96 bits                  | Trailer bits[63:0] defined as Byte Enables. Trailer bits[95:64] defined as EMD. |
|                          | No-Op/MS0 |     | 64 bits                  | Trailer bits[63:0] defined as Byte Enables.                                     |
| <others></others>        | N/A       | 0   | No Trailer               | Other combinations do not encode trailers.                                      |

### <span id="page-156-0"></span>3.3.7 M2S Back-Invalidate Response (BIRsp)

The Back-Invalidate Response (BIRsp) message class contains response messages from the Master to the Subordinate as a result of Back-Invalidate Snoops. This message class is not supported in 68B Flit mode.

### <span id="page-156-2"></span>M2S BIRsp Fields Table 3-44.

|         | Width (Bits) |              |             |                                                                                                                                                                                                                                                   |  |
|---------|--------------|--------------|-------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--|
| Field   | 68B<br>Flit  | 256B<br>Flit | PBR<br>Flit | Description                                                                                                                                                                                                                                       |  |
| Valid   | 1            |              |             | The valid signal indicates that this is a valid response.                                                                                                                                                                                         |  |
| Opcode  |              | 4            |             | Response type with encodings in Table 3-45.                                                                                                                                                                                                       |  |
| BI-ID   |              | 12           | 0           | BI-ID of the device that is the destination of the message. See<br>Section 9.14 for details on how this field is assigned to devices.<br>Not applicable in PBR messages where DPID infers this field.                                             |  |
| BITag   |              | 12           |             | Tracking ID from the device.                                                                                                                                                                                                                      |  |
| LowAddr | N/A          | 2            |             | The lower 2 bits of Cacheline address (Address[7:6]). This is needed to differentiate snoop responses when a Block Snoop is sent and receives snoop response for each cacheline.  For block response (opcode names *Blk), this field is reserved. |  |
| SPID    |              | 0 12         |             | Source PID                                                                                                                                                                                                                                        |  |
| DPID    | 0 1:         |              | 12          | Destination PID                                                                                                                                                                                                                                   |  |
| RSVD    |              | 9            |             |                                                                                                                                                                                                                                                   |  |
| Total   |              | 40           | 52          |                                                                                                                                                                                                                                                   |  |

<span id="page-156-5"></span><span id="page-156-3"></span>**Table 3-45.** M2S BIRsp Memory Opcodes (Sheet 1 of 2)**

| Opcode    | Description                                                                                                                                                                | Encoding |
|-----------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|
| BIRspI    | Host completed the Back-Invalidate Snoop for one cacheline and the host cache state is I.                                                                                  | 0000b    |
| BIRspS    | Host completed the Back-Invalidate Snoop for one cacheline and the host cache state is S.                                                                                  | 0001b    |
| BIRspE    | Host completed the Back-Invalidate Snoop for one cacheline and the host cache state is E.                                                                                  | 0010b    |
| BIRspIBIk | Same as BIRspI except that the message applies to the entire block of cachelines. The size of the block is explicit in the BISnp*Blk message for which this is a response. | 0100b    |

Table 3-45. M2S BIRsp Memory Opcodes (Sheet 2 of 2)

| Opcode    | Description                                                                                                                                                                |                   |  |  |  |
|-----------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------|--|--|--|
| BIRspSBlk | Same as BIRspS except that the message applies to the entire block of cachelines. The size of the block is explicit in the BISnp*Blk message for which this is a response. | 0101b             |  |  |  |
| BIRspEBIk | Same as BIRspE except that the message applies to the entire block of cachelines. The size of the block is explicit in the BISnp*Blk message for which this is a response. | 0110b             |  |  |  |
| Reserved  | Reserved                                                                                                                                                                   | <others></others> |  |  |  |

### <span id="page-157-0"></span>3.3.8 S2M Back-Invalidate Snoop (BISnp)

The Back-Invalidate Snoop (BISnp) message class contains Snoop messages from the Subordinate to the Master. This message class is not supported in 68B Flit mode.

<span id="page-157-1"></span>**Table 3-46. S2M BISnp Fields**

| Field         | Width (Bits) |              |             |                                                                                                                                                                                                             |
|---------------|--------------|--------------|-------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|               | 68B<br>Flit  | 256B<br>Flit | PBR<br>Flit | Description                                                                                                                                                                                                 |
| Valid         |              | 1            |             | The valid signal indicates that this is a valid request.                                                                                                                                                    |
| Opcode        |              | 4            |             | Snoop type with encodings in Table 3-47.                                                                                                                                                                    |
| BI-ID         |              | 12           | 0           | BI-ID of the device that issued the message. See Section 9.14 for details on how this field is assigned. Not applicable in PBR messages where SPID infers this field.                                       |
| BITag         |              | 12           |             | Tracking ID from the device.                                                                                                                                                                                |
| Address[51:6] | N/A          | 46           |             | Host Physical Address.  For *Blk opcodes, the lower 2 bits (Address[7:6]) are encoded as defined in Table 3-48. Used for all other opcodes that represent the standard definition of Host Physical Address. |
| SPID          |              | 0            | 12          | Source PID                                                                                                                                                                                                  |
| DPID          |              | 0            | 12          | Destination PID                                                                                                                                                                                             |
| RSVD          |              | 9            |             |                                                                                                                                                                                                             |
| Total         |              | 84           | 96          |                                                                                                                                                                                                             |

<span id="page-157-2"></span>**Table 3-47. S2M BISnp Opcodes (Sheet 1 of 2)**

| Opcode       | Description                                                                                                                                                                                                                                                                                                               | Encoding |
|--------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|
| BISnpCur     | Device requesting Current copy of the line but not requiring caching state.                                                                                                                                                                                                                                               | 0000b    |
| BISnpData    | Device requesting Shared or Exclusive copy.                                                                                                                                                                                                                                                                               | 0001b    |
| BISnpInv     | Device requesting Exclusive Copy.                                                                                                                                                                                                                                                                                         | 0010b    |
| BISnpCurBlk  | Same as BISnpCur except covering 2 or 4 cachelines that are naturally aligned and contiguous. The Block Enable encoding is in Address[7:6] and defined in Table 3-48. The host may give per cacheline response or a single block response applying to all cachelines in the block.  More details are in Section 3.3.8.1.  | 0100b    |
| BISnpDataBlk | Same as BISnpData except covering 2 or 4 cachelines that are naturally aligned and contiguous. The Block Enable encoding is in Address[7:6] and defined in Table 3-48. The host may give per cacheline response or a single block response applying to all cachelines in the block.  More details are in Section 3.3.8.1. | 0101b    |

**Table 3-47. S2M BISnp Opcodes (Sheet 2 of 2)**

| Opcode          | Description                                                                                                                                                                                                                                                                                                                         | Encoding          |
|-----------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------|
| BISnpInvBlk     | Same as BISnpInv except covering 2 or 4 cachelines that are naturally<br>aligned and contiguous. The Block Enable encoding is in Address[7:6] and<br>defined in Table 3-48. The host may give per cacheline response or a single<br>block response applying to all cachelines in the block.<br>More details are in Section 3.3.8.1. | 0110b             |
| BISnpCurTEE     | Same as BISnpCur but with the Trusted Execution Environment (TEE)<br>attribute. See Section 11.5.4.5 for description of TEE attribute handling.                                                                                                                                                                                     | 1000b             |
| BISnpDataTEE    | Same as BISnpData but with the Trusted Execution Environment (TEE)<br>attribute. See Section 11.5.4.5 for description of TEE attribute handling.                                                                                                                                                                                    | 1001b             |
| BISnpInvTEE     | Same as BISnpInv but with the Trusted Execution Environment (TEE)<br>attribute. See Section 11.5.4.5 for description of TEE attribute handling.                                                                                                                                                                                     | 1010b             |
| BISnpCurBlkTEE  | Same as BISnpCurBlk but with the Trusted Execution Environment (TEE)<br>attribute. See Section 11.5.4.5 for description of TEE attribute handling.                                                                                                                                                                                  | 1100b             |
| BISnpDataBlkTEE | Same as BISnpDataBlk but with the Trusted Execution Environment (TEE)<br>attribute. See Section 11.5.4.5 for description of TEE attribute handling.                                                                                                                                                                                 | 1101b             |
| BISnpInvBlkTEE  | Same as BISnpInvBlk but with the Trusted Execution Environment (TEE)<br>attribute. See Section 11.5.4.5 for description of TEE attribute handling.                                                                                                                                                                                  | 1110b             |
| Reserved        | Reserved                                                                                                                                                                                                                                                                                                                            | <others></others> |

#### <span id="page-158-0"></span>3.3.8.1 Rules for Block Back-Invalidate Snoops

A Block Back-Invalidate Snoop applies to multiple naturally aligned contiguous cachelines (2 or 4 cachelines). The host must ensure that coherence is resolved for each line and may send combined or individual responses for each in arbitrary order. In the presence of address conflicts, it is necessary that the host resolve conflicts for each cacheline separately. This special address encoding applies only to BISnp\*Blk messages.

<span id="page-158-2"></span>**Table 3-48. Block (Blk) Enable Encoding in Address[7:6]**

| Addr[7:6] | Description                                                 |  |
|-----------|-------------------------------------------------------------|--|
| 00b       | Reserved                                                    |  |
| 01b       | Lower 128B block is valid, Lower is defined as Address[7]=0 |  |
| 10b       | Upper 128B block, Upper is defined as Address[7]=1          |  |
| 11b       | 256B block is valid                                         |  |

### <span id="page-158-1"></span>3.3.9 S2M No Data Response (NDR)

<span id="page-158-3"></span>The NDR message class contains completions and indications from the Subordinate to the Master.

<span id="page-159-0"></span>**Table 3-49. S2M NDR Fields**

| Field      | Width (Bits) |              |             |                                                                                                                                                                                                                                                                                                                                                                                     |
|------------|--------------|--------------|-------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|            | 68B Flit     | 256B<br>Flit | PBR<br>Flit | Description                                                                                                                                                                                                                                                                                                                                                                         |
| Valid      |              | 1            |             | The valid signal indicates that this is a valid request.                                                                                                                                                                                                                                                                                                                            |
| Opcode     |              | 3            |             | Memory Operation: This specifies which, if any, operation<br>needs to be performed on the data and associated<br>information. Details in Table 3-50.                                                                                                                                                                                                                                |
| MetaField  | 2            |              |             | Metadata Field: For devices that support memory with<br>Metadata, this field may be encoded with Meta0-State in<br>response to an M2S Req. For devices that do not support<br>memory with Metadata or in response to an M2S RwD, this<br>field must be set to the No-Op encoding. No-Op may also be<br>used by devices if the Metadata is unreliable or corrupted in<br>the device. |
| MetaValue  | 2            |              |             | Metadata Value: If MetaField is No-Op, this field is don't care;<br>otherwise, it is Metadata Field as read from memory.                                                                                                                                                                                                                                                            |
| Tag        |              | 16           |             | Tag: This is a reflection of the Tag field sent with the<br>associated M2S Req or M2S RwD.                                                                                                                                                                                                                                                                                          |
| LD-ID[3:0] | 4            | 4            | 0           | Logical Device Identifier: This identifies a logical device within<br>a multiple-logical device. Not applicable in PBR messages<br>where DPID infers this field.                                                                                                                                                                                                                    |
| DevLoad    |              | 2            |             | Device Load: Indicates device load as defined in Table 3-51.<br>Values are used to enforce QoS as described in Section 3.3.4.                                                                                                                                                                                                                                                       |
| DPID       | 0            | 0            | 12          | Destination PID                                                                                                                                                                                                                                                                                                                                                                     |
| RSVD       | 0            | 10           | 10          |                                                                                                                                                                                                                                                                                                                                                                                     |
| Total      | 30           | 40           | 48          |                                                                                                                                                                                                                                                                                                                                                                                     |

<span id="page-159-3"></span>Opcodes for the NDR message class are defined in [Table 3-50](#page-159-1).

<span id="page-159-1"></span>**Table 3-50. S2M NDR Opcodes**

| Opcode          | Description                                                                                                                                                           | Encoding |
|-----------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|
| Cmp             | Completions for Writebacks, Reads and Invalidates.                                                                                                                    | 000b     |
| Cmp-S           | Indication from the DCOH to the Host for Shared state.                                                                                                                | 001b     |
| Cmp-E           | Indication from the DCOH to the Host for Exclusive ownership.                                                                                                         | 010b     |
| Cmp-M           | Indication from the DCOH to the Host for Modified state. This is optionally supported<br>by host implementations and devices must support disabling of this response. | 011b     |
| BI-ConflictAck1 | Completion of the Back-Invalidate conflict handshake.                                                                                                                 | 100b     |
| CmpTEE1         | Completion for Writes (MemWr*) with TEE intent. Does not apply to any M2S Req.                                                                                        | 101b     |
| CmpTEE-S        | Indication from the DCOH to the Host for Shared state with TEE intent.                                                                                                | 110b     |
| CmpTEE-E        | Indication from the DCOH to the Host for Exclusive ownership with TEE intent.                                                                                         | 111b     |

<span id="page-159-2"></span><sup>1.</sup> Only support in 256B flit mode.

[Table 3-51](#page-160-1) defines the DevLoad value used in NDR and DRS messages. The encodings were assigned to allow CXL 1.1 backward compatibility such that the 00b value would cause the least impact in the host.

<span id="page-160-1"></span>Table 3-51. DevLoad Definition

| DevLoad Value     | Queuing Delay inside Device | Device Internal Resource Utilization                    | Encoding |
|-------------------|-----------------------------|---------------------------------------------------------|----------|
| Light Load        | Minimal                     | Readily handles more requests                           | 00b      |
| Optimal Load      | Modest to Moderate          | Optimally utilized                                      | 01b      |
| Moderate Overload | Significant                 | Limiting request throughput and/or degrading efficiency | 10b      |
| Severe Overload   | High                        | Heavily overloaded and/or degrading efficiency          | 11b      |

Definition of other fields are the same as for M2S message classes.

### <span id="page-160-0"></span>3.3.10 S2M Data Response (DRS)

The DRS message class contains memory read data from the Subordinate to the Master.

The fields of the DRS message class are defined in Table 3-52.

<span id="page-160-2"></span>**Table 3-52. S2M DRS Fields**

|            | Width (Bits) |              |             |                                                                                                                                                                                                                                                                          |  |  |  |
|------------|--------------|--------------|-------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--|--|--|
| Field      | 68B<br>Flit  | 256B<br>Flit | PBR<br>Flit | Description                                                                                                                                                                                                                                                              |  |  |  |
| Valid      |              | 1            |             | The valid signal indicates that this is a valid request.                                                                                                                                                                                                                 |  |  |  |
| Opcode     | 3            |              |             | Memory Operation: This specifies which, if any, operation needs be performed on the data and associated information. Details in Table 3-53.                                                                                                                              |  |  |  |
| MetaField  | 2            |              |             | Metadata Field: For devices that support memory with Metadata, this field can be encoded as Meta0-State. For devices that do not this field must be encoded as No-Op. No-Op encoding may also bused by devices if the Metadata is unreliable or corrupted in the device. |  |  |  |
| MetaValue  | 2            |              |             | Metadata Value: If MetaField is No-Op, this field is don't care; otherwise, it must encode the Metadata field as read from Memory                                                                                                                                        |  |  |  |
| Tag        | 16           |              |             | Tag: This is a reflection of the Tag field sent with the associated M2S Req or M2S RwD.                                                                                                                                                                                  |  |  |  |
| Poison     | 1            |              |             | The Poison bit indicates that the data contains an error. The handling of poisoned data is Host specific. See Chapter 12.0 for more details.                                                                                                                             |  |  |  |
| LD-ID[3:0] | 4 0          |              | 0           | Logical Device Identifier: This identifies a logical device within a multiple-logical device. Not applicable in PBR mode where DPID infers this field.                                                                                                                   |  |  |  |
| DevLoad    | 2            |              |             | Device Load: Indicates device load as defined in Table 3-51. Values are used to enforce QoS as described in Section 3.3.4.                                                                                                                                               |  |  |  |
| DPID       | 0 12         |              | 12          | Destination PID                                                                                                                                                                                                                                                          |  |  |  |
| TRP        | 0 1          |              | 1           | Trailer Present: Indicates that a trailer is included after the 64B payload. The Trailer size and legal encodings for DRS are defined in Table 3-54.                                                                                                                     |  |  |  |
| RSVD       | 9            | 9 8          |             |                                                                                                                                                                                                                                                                          |  |  |  |
| Total      | 40 40 48     |              | 48          |                                                                                                                                                                                                                                                                          |  |  |  |

<span id="page-161-4"></span><span id="page-161-2"></span>Table 3-53. S2M DRS Opcodes

| Opcode                                                                                | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | Encoding |  |  |
|---------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|--|--|
| MemData                                                                               | Memory read data. Sent in response to Reads.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | 000b     |  |  |
| MemData-NXM                                                                           | Memory Read Data to Non-existent Memory region. This response is only used to indicate that the device or the switch was unable to positively decode the address of the MemRd as either HDM-H or HDM-D\*. Must encode the payload with all 1s and set poison if poison is enabled. This special opcode is needed because the host will have expectation of a DRS only for HDM-H or a DRS+NDR for HDM-D\*, and this opcode allows devices/switches to send a single response to the host, allowing a deallocation of host tracking structures in an otherwise ambiguous case. See Section 3.3.11 for additional details. | 001b     |  |  |
| MemDataTEE <sup>1</sup>                                                               | Same as MemData but in response to MemRd\* with TEE attribute.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | 010b     |  |  |
| Reserved                                                                              | Reserved                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | \<Others\> |  |  |

<sup>1.</sup> Only support in 256B Flit mode.

#### <span id="page-161-0"></span>3.3.10.1 Trailer Present for DRS (256B Flit)

In 256B Flit mode, a Trailer Present (TRP) bit is included with the message header that indicates whether a trailer slot is included with the message. The trailer can be up to 32 bits for DRS.

The TRP bit can be inferred by other field decode as defined in Table 3-54 for DRS. It is included to enable simple decode in the Link Layer.

<span id="page-161-6"></span>The Extended Metadata (EMD) trailer is the only trailer supported. The Extended Metadata (EMD) trailer can be up to 32 bits. Section 8.2.4.31 describes the registers that aid in discovery of device's EMD capability and EMD related configuration of the device. The mechanism for discovering the host's EMD capabilities and EMD related configuration of the host is host-specific. The host and the device must be configured in a consistent manner.

<span id="page-161-5"></span><span id="page-161-3"></span>**Table 3-54. DRS Trailers**

| Opcode/<br>Message | MetaField | TRP | Trailer Size<br>Required | Description                        |
|--------------------|-----------|-----|--------------------------|------------------------------------|
| MemData/           | EMS       | 1   | 32 bits                  | Trailer bits[31:0] defined as EMD. |
| MemDataTEE         | No-OP/MS0 | 0   | No Trailer               |                                    |
| <others></others>  | N/A       | 0   | No Trailer               |                                    |

### <span id="page-161-1"></span>3.3.11 Responses for Requests Targeting NXM

Device responses to CXL.mem requests differ between HDM-H regions and HDM-D/HDM-DB regions, which creates an ambiguity when device receives a CXL.mem request it cannot map to a specific memory region. In this situation, devices shall respond according to Table 3-55. CXL.mem Responses for Requests to Non-existent Memory requesting device must accept and properly handle these responses regardless of its memory region decode results.

The ambiguity mentioned above is for reads and for some MemInv\* cases. For reads, the response is DRS only for HDM-H or a DRS+NDR for HDM-D\*. For MemInv\*, HDM-H returns Cmp opcode and HDM-D/HDM-DB may expect only Cmp-E or Cmp-S as show in Table C-3, "HDM-DB Memory Requests with TE state".

The capability to support MemData-NXM is exposed in the "CXL HDM Decoder Capability Register" bit 20 (see Section 8.2.4.20.1).

<span id="page-162-1"></span>**Table 3-55. CXL.mem Responses for Requests to Non-existent Memory**

| CXL.mem Request1                                                        | Device Response when NXM                                                                        |  |  |
|-------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------|--|--|
| MemRd, MemRdData, MemRdFill, MemRdTEE,<br>MemRdDataTEE, MemRdFillTEE    | MemData-NXM<br>See Table 8-27, "CXL.mem Read Response - Error<br>Cases" for additional details. |  |  |
| MemInv, MemInvNT, MemClnEvct, MemWr,<br>MemWrPtl, MemWrTEE, MemWrPtlTEE | Cmp                                                                                             |  |  |

<sup>1.</sup> TEE requests have a non-TEE response to allow requester to enforce appropriate security policy.

### <span id="page-162-0"></span>3.3.12 Forward Progress and Ordering Rules

<span id="page-162-2"></span>- • Req may be blocked by BISnp to the Host, but RwD cannot be blocked by BISnp to the Host.
  - This rule impacts RwD MemWr\* to Shared FAM HDM-DB uniquely requiring SnpType=No-Op to avoid causing BISnp to other requesters that are sharing the memory which could deadlock. The resulting is a requirement that the requester must first get ownership of the cacheline using M2S Req message referred to as a 2-phase write as described in [Section 2.4.4.](#page-78-2)
- A CXL.mem Request in the M2S Req channel must not pass a MemRdFwd or a MemWrFwd, if the Request and MemRdFwd or MemWrFwd are to the same cacheline address.
  - Reason: As described in [Table 3-35](#page-150-0), MemRdFwd and MemWrFwd opcodes, sent on the M2S Req channel are, in fact, responses to CXL.cache D2H requests. The reason the response for certain CXL.cache D2H requests are on CXL.mem M2S Req channel is to ensure subsequent requests from the Host to the same address remain ordered behind it. This allows the host and device to avoid race conditions. Examples of transaction flows using MemRdFwd are shown in [Figure 3-35](#page-182-1) and [Figure 3-40.](#page-187-2) Apart from the above, there is no ordering requirement for the Req, RwD, NDR, and DRS message classes or for different addresses within the Req message class.
- NDR and DRS message classes, each, need to be pre-allocated at the request source. This guarantees that the responses can sink and ensures forward progress.
- On CXL.mem, write data is only guaranteed to be visible to a later access after the write is complete.
- CXL.mem requests need to make forward progress at the device without any dependency on any device initiated request except for BISnp messages. This includes any request from the device on CXL.io or CXL.cache.
- S2M and M2S Data transfer of a cacheline must occur with no interleaved transfers.

> **IMPLEMENTATION NOTE**

There are two cases of bypassing with device-attached memory where messages in the M2S RwD channel may pass messages for the same cacheline address in M2S Req channel.

- 1. Host generated weakly ordered writes (as showing in [Figure 3-32](#page-179-0)) may bypass MemRdFwd and MemWrFwd. The result is the weakly ordered write may bypass older reads or writes from the Device.
- 2. For Device initiated RdCurr to the Host, the Host will send a MemRdFwd to the device after resolving coherency (as shown in [Figure 3-35\)](#page-182-1). After sending the MemRdFwd the Host may have an exclusive copy of the line (because RdCurr does not downgrade the coherency state at the target) allowing the Host to subsequently modify this line and send a MemWr to this address. This MemWr will not be ordered with respect to the previously sent MemRdFwd.

Both examples are legal because weakly ordered stores (in Case #1) and RdCurr (in Case #2) do not guarantee strong consistency.

#### <span id="page-163-0"></span>3.3.12.1 Buried Cache State Rules for HDM-D/HDM-DB

Buried Cache state for CXL.mem protocol refers to the state of the cacheline registered by the Master's Home Agent logic (HA) for a cacheline address when a new Req or RwD message is being sent. This cache state could be a cache that is controlled by the host, but does not cover the cache in the device that is the owner of the HDM-D/HDM-DB memory. These rules are applicable to only HDM-D/HDM-DB memory where the device is managing coherence.

For implementations that allow multiple outstanding requests to the same address, the possible future cache state must be included as part of the buried cache state. To avoid this complexity, it is recommended to limit to one Req/RwD per cacheline address.

Buried Cache state rules for Master-issued CXL.mem Req/RwD messages:

- Must not issue a MemRd/MemInv/MemInvNT (MetaValue=I) if the cacheline is buried in Modified, Exclusive, or Shared state.
- Shall not issue a MemRd/MemInv/MemInvNT (MetaValue=S) or MemRdData if the cacheline is buried in Modified or Exclusive state, but is allowed to issue when the host has Shared or Invalid state.
- May issue a MemRd/MemInv/MemInvNT (MetaValue = A) from any state.
- May issue a MemRd/MemInv/MemInvNT (MetaField = No-Op) from any state. Note that the final host cache state may result in a downgraded state such as Invalid when initial buried state exists and conflicting BISnp results in the buried state being downgraded.
- May issue MemClnEvct from Shared or Exclusive state.
- May issue MemWr with SnpType=SnpInv only from I-state. Use of this encoding is not allowed for HDM-DB memory regions in which coherence extends to multiple hosts (e.g., Coherent Shared FAM as described in [Section 2.4.4\)](#page-78-2).
- MemWr with SnpType=No-Op may be issued only from Modified state.

*Note:* The Master may silently degrade clean cache state (E to S, E to I, S to I) and as such the Subordinate may have more conservative view of the Master's cache state. This section is discussing cache state from the Master's view.

Table 3-56 summarizes the Req message and RwD message allowance for Buried Cache state. MemRdFwd/MemWrFwd/BIConflict are excluded from this table because they are response messages.

<span id="page-164-1"></span>Table 3-56. Allowed Opcodes for HDM-D/HDM-DB Req and RwD Messages per Buried Cache State

| CXL.mem Req/RwD                                                       |                        |                                               |                           | <b>Buried Cache State</b> |           |        |         |
|-----------------------------------------------------------------------|------------------------|-----------------------------------------------|---------------------------|---------------------------|-----------|--------|---------|
| Opcodes                                                               | MetaField              | MetaValue                                     | SnpType                   | Modified                  | Exclusive | Shared | Invalid |
| MemRdData                                                             | All I = == I C = == I  | -:                                            |                           |                           |           | X      | X       |
| MemClnEvct                                                            | All Legal Combinations |                                               |                           |                           | X         | X      |         |
| -                                                                     |                        | A                                             | All Legal<br>Combinations | X <sup>1</sup>            | X         | X      | X       |
| MemRd/                                                                | MS0/EMD                | S                                             |                           |                           |           | X      | X       |
| MemInv/                                                               |                        | 1                                             |                           |                           |           |        | X       |
| MemInvNT                                                              | No-Op                  | N/A                                           |                           | X <sup>1</sup>            | X         | x      | X       |
|                                                                       | EMD                    | Explicit No-Op                                |                           |                           |           |        |         |
|                                                                       |                        |                                               | No-Op                     | X                         |           |        |         |
| MemWr                                                                 | All Legal Comi         | All Legal Combinations                        |                           |                           |           |        | X       |
| MemRdFill/<br>MemRdFillTEE/<br>MemRdDataTEE/<br>MemRdTEE/<br>MemWrTEE | N/A (Comman            | N/A (Commands not supported for HDM-D/HDM-DB) |                           |                           |           |        |         |

<span id="page-164-2"></span><sup>1.</sup> Requesters that have active reads with buried-M state must expect data return to be stale. It is up to the requester to ensure that possible stale data case is handled in all cases including conflicts with BISnp.

## <span id="page-164-0"></span>3.4 Transaction Ordering Summary

This section presents CXL ordering rules in a series of tables and descriptions. Table 3-57 captures the upstream ordering cases. Table 3-58 captures the downstream ordering cases.

For CXL.mem and CXL.cache, the term upstream describes traffic on all S2M and D2H message classes, and the term downstream describes traffic on all M2S and H2D message classes, regardless of the physical direction of travel.

Where upstream and downstream traffic coexist in the same physical direction within PBR switches and on Inter Switch Links (ISLs) or on links from a device that issues direct P2P CXL.mem, the upstream and downstream Ordering Tables each apply to their corresponding subset of the traffic and each subset shall be independent and not block one another.

Table 3-59 lists the Device in-out dependence. Table 3-60 lists the Host in-out dependence. Additional detail is provided in Section 3.2.2.1 for CXL.cache and in Section 3.3.12 for CXL.mem.

In Table 3-57 and Table 3-58, the columns represent a first-issued message and the rows represent a subsequently issued message. The table entry indicates the ordering relationship between the two messages. The table entries are defined as follows:

- Yes: The second message (row) must be allowed to pass the first message (column) to avoid deadlock. (When blocking occurs, the second message is required to pass the first message.)
- Y/N: There are no ordering requirements. The second message may optionally pass the first message or may be blocked by it.

• No: The second message must not be allowed to pass the first message. This is required to support the protocol ordering model.

*Note:* Passing, where permitted, must not be allowed to cause the starvation of any message class.

<span id="page-165-2"></span><span id="page-165-0"></span>**Table 3-57. Upstream Ordering Summary**

| Row Pass<br>Column?                    | CXL.io TLPs<br>(Col 2-5)      | S2M NDR/DRS<br>D2H Rsp/Data<br>(Col 6) | D2H Req<br>(Col 7) | S2M BISnp<br>(Col 13) |  |
|----------------------------------------|-------------------------------|----------------------------------------|--------------------|-----------------------|--|
| CXL.io TLPs<br>(Row A-D)               | PCIe Base<br>Yes(1)<br>Yes(1) |                                        |                    | Yes(1)                |  |
| S2M NDR/DRS<br>D2H Rsp/Data<br>(Row E) |                               | a. No(3)                               |                    | Yes(2)(4)             |  |
|                                        | Yes(1)                        | b. Y/N                                 | Yes(2)             |                       |  |
| D2H Req<br>(Row F)                     | Yes(1)                        | Y/N                                    | Y/N                | Y/N                   |  |
| S2M BISnp<br>(Row M)                   | Yes(1)(4)                     |                                        | Yes(4)             | Y/N                   |  |

Explanation of row and column headers:

M7 requires BISnp to pass D2H Req in accordance with dependence relationship: D2H Req depends on M2S Req depends on S2M BISnp.

E6a requires that within the NDR channel, BIConflictAck must not pass prior Cmp\* messages with the same Cacheline Address (implied by the tag field).

E6b other cases not covered by rule E6a are Y/N.

| Color-coded rationale for cells in Table 3-57 |                                                                                                                                                                     |  |  |  |
|-----------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------|--|--|--|
| Yes(1)                                        | CXL architecture requirement for ARB/MUX.                                                                                                                           |  |  |  |
| Yes(2)                                        | CXL.cachemem: Required for deadlock avoidance.                                                                                                                      |  |  |  |
| No(3)                                         | Type 2/3 devices where BIConflictAck must not pass prior Cmp* to the same address.                                                                                  |  |  |  |
| Yes(4)                                        | Required for deadlock avoidance with the introduction of the BISnp channel. For CXL.io<br>Unordered I/O, this is necessary because Unordered I/O can trigger BISnp. |  |  |  |

<span id="page-165-3"></span><span id="page-165-1"></span>**Table 3-58. Downstream Ordering Summary (Sheet 1 of 2)**

| Row Pass<br>Column?      | CXL.io TLPs<br>(Col 2-5) | M2S Req<br>(Col 8) | M2S RwD<br>(Col 9) | H2D Req<br>(Col 10) | H2D Rsp<br>(Col 11) | H2D Data<br>(Col 12) | M2S BIRsp<br>(Col 14) |
|--------------------------|--------------------------|--------------------|--------------------|---------------------|---------------------|----------------------|-----------------------|
| CXL.io TLPs<br>(Row A-D) | PCIe Base                | Yes(1)             | Yes(1)             | Yes(1)              | Yes(1)              | Yes(1)               | Yes(1)                |
| M2S Req<br>(Row G)       | Yes(1)                   | a. No(5)           | Y/N                | Y/N(3)              | Y/N                 | Y/N                  | Y/N                   |
|                          |                          | b. Y/N             |                    |                     |                     |                      |                       |
| M2S RwD<br>(Row H)       | Yes(1)(6)                | a. Yes(6)          | Y/N                | Yes(3)<br>Y/N       |                     | Y/N                  | Y/N                   |
|                          |                          | b. Y/N             |                    |                     |                     |                      |                       |
| H2D Req<br>(Row I)       | Yes(1)                   | Yes(2)(6)          | a. Yes(2)          | Y/N                 | a. No(4)            | Y/N(3)               | Y/N                   |
|                          |                          |                    | b. Y/N             |                     | b. Y/N              |                      |                       |

**Table 3-58. Downstream Ordering Summary (Sheet 2 of 2)**

| Row Pass<br>Column?  | CXL.io TLPs<br>(Col 2-5) | M2S Req<br>(Col 8) | M2S RwD<br>(Col 9) | H2D Req<br>(Col 10) | H2D Rsp<br>(Col 11) | H2D Data<br>(Col 12) | M2S BIRsp<br>(Col 14) |
|----------------------|--------------------------|--------------------|--------------------|---------------------|---------------------|----------------------|-----------------------|
| H2D Rsp<br>(Row J)   | Yes(1)                   | Yes(2)             | Yes(2)             | Yes(2)              | Y/N                 | Y/N                  | Y/N                   |
| H2D Data<br>(Row K)  | Yes(1)                   | Yes(2)             | Yes(2)             | Yes(2)              | Y/N                 | Y/N                  | Y/N                   |
| M2S BIRsp<br>(Row N) | Yes(1)(6)                | Yes(2)             | Yes(2)             | Yes(2)              | Y/N                 | Y/N                  | Y/N                   |

Explanation of row and column headers:

In Downstream direction pre-allocated channels are kept separate because of unique ordering requirements in each.

| Color-coded rationale for cells in Table 3-58 |                                                                             |  |  |  |
|-----------------------------------------------|-----------------------------------------------------------------------------|--|--|--|
| Yes(1)                                        | CXL architecture requirement for ARB/MUX.                                   |  |  |  |
| Yes(2)                                        | CXL.cachemem: Required for deadlock avoidance.                              |  |  |  |
| Yes(3)                                        | CXL.cachemem: Performance optimization.                                     |  |  |  |
| Y/N(3)                                        | CXL.cachemem: Non-blocking recommended for performance optimization.        |  |  |  |
| No(4)                                         | Type 1/2 device: Snoop push GO requirement.                                 |  |  |  |
| No(5)                                         | Type 2 device: MemRd*/MemInv* push Mem*Fwd requirement.                     |  |  |  |
| Yes(6)                                        | Required for deadlock avoidance with the introduction of the BISnp channel. |  |  |  |

### Explanation of table entries:

G8a MemRd\*/MemInv\* must not pass prior Mem\*Fwd messages to the same cacheline address. This rule is applicable only for HDM-D memory regions in devices which result in receiving Mem\*Fwd messages (Type 3 devices with no HDM-D don't need to implement this rule). This rule does not apply to Type 2 devices that implement the HDM-DB memory region which use the BI\* channels because they do not support Mem\*Fwd.

G8b All other cases not covered by rule G8a do not have ordering requirements (Y/N).

H8a applies to components that support the BISnp/BIRsp message classes to ensure that the RwD channel can drain to the device even if the Req channel is blocked.

H8b applies to components that do not support the BISnp/BIRsp message classes.

I9a applies for PBR-capable switches, for ISLs, and for devices that can initiate P2P CXL.mem. (Possible future use case for Host-to-Host CXL.mem will require host to apply this ordering rule.)

I9b applies to all other cases.

I11a Snoops must not pass prior GO\* messages to the same cacheline address. GO messages do not carry the address, so implementations where address cannot be inferred from UQID in the GO message will need to strictly apply this rule across all messages.

I11b Other case not covered by I11a are Y/N.

<span id="page-167-0"></span>**Table 3-59. Device In-Out Ordering Summary** 

| Row (in) Independent of Column (out)? | CXL.io TLPs<br>(Col A-D) | S2M NDR/DRS<br>D2H Rsp/Data<br>(Col E) | D2H Req<br>(Col F) | S2M BISnp<br>(Col M) | M2S Req<br>(Col N) <sup>1</sup> | M2S RwD<br>(Col O) <sup>1</sup> | M2S BIRsp<br>(Col P) <sup>1</sup> |
|---------------------------------------|--------------------------|----------------------------------------|--------------------|----------------------|---------------------------------|---------------------------------|-----------------------------------|
| CXL.io TLPs                           | PCIe Base                | Y/N(1)                                 | Y/N(1)             | Y/N(1)               | Y/N(1)                          | Y/N(1)                          | Y/N(1)                            |
| (Row 2-5)                             |                          | Yes(3)                                 | Yes(3)             | Yes(3)               | Yes(3)                          | Yes(3)                          | Yes(3)                            |
| M2S Req<br>(Row 8)                    | Yes(1)                   | Y/N                                    | Yes(2)             | Y/N                  | Yes(2)                          | Y/N                             | Y/N                               |
| M2S RwD<br>(Row 9)                    | Yes(1)(2)                | Y/N                                    | Yes(2)             | Yes(2)               | Yes(2)                          | Yes(2)                          | Y/N                               |
| H2D Req<br>(Row 10)                   | Yes(1)                   | Y/N                                    | Yes(2)             | Yes(2)               | Yes(2)                          | Yes(2)                          | Y/N                               |
| H2D Rsp<br>(Row 11)                   | Yes(1)                   | Yes(2)                                 | Yes(2)             | Yes(2)               | Yes(2)                          | Yes(2)                          | Yes(2)                            |
| H2D Data<br>(Row 12)                  | Yes(1)                   | Yes(2)                                 | Yes(2)             | Yes(2)               | Yes(2)                          | Yes(2)                          | Yes(2)                            |
| M2S BIRsp<br>(Row 14)                 | Yes(1)(2)                | Yes(2)                                 | Yes(2)             | Yes(2)               | Yes(2)                          | Yes(2)                          | Yes(2)                            |
| S2M NDR/DRS<br>(Row 15) <sup>1</sup>  | Yes(1)                   | Yes(2)                                 | Yes(2)             | Yes(2)               | Yes(2)                          | Yes(2)                          | Y/N                               |
| S2M BISnp<br>(Row 16) <sup>1</sup>    | Yes(1)                   | Y/N                                    | Yes(2)             | Yes(2)               | Yes(2)                          | Y/N                             | Y/N                               |

<span id="page-167-2"></span><sup>1.</sup> These rows and columns are supported only by devices that have Direct P2P CXL.mem enabled.

In the device ordering, the row represents incoming message class and the column represents the outgoing message class. The cases in this table show when incoming must be independent of outgoing (Yes) and when it is allowed to block incoming based on outgoing (Y/N).

| Color-coded rationale for cells in Table 3-59 |                                                                         |  |  |  |  |
|-----------------------------------------------|-------------------------------------------------------------------------|--|--|--|--|
| Yes(1)                                        | CXL.cachemem is independent of outgoing CXL.io.                         |  |  |  |  |
| Y/N(1)                                        | CXL.io traffic, except UIO Completions, may be blocked by CXL.cachemem. |  |  |  |  |
| Yes(2)                                        | CXL.cachemem: Required for deadlock avoidance.                          |  |  |  |  |
| Yes(3)                                        | CXL UIO completions are independent of CXL.cachemem.                    |  |  |  |  |

<span id="page-167-1"></span>**Table 3-60. Host In-Out Ordering Summary (Sheet 1 of 2)** 

| Row (in) Independent of Column (out)? | CXL.io TLPs<br>(Col A-D) | M2S Req<br>(Col G) | M2S RwD<br>(Col H) | H2D Req<br>(Col I) | H2D Rsp<br>(Col J) | H2D Data<br>(Col K) | M2S BIRsp<br>(Col N) |
|---------------------------------------|--------------------------|--------------------|--------------------|--------------------|--------------------|---------------------|----------------------|
| CXL.io TLPs<br>(Row 2-5)              | PCIe Base                | Y/N(1)             | Y/N(1)             | Y/N(1)             | Y/N(1)             | Y/N(1)              | Y/N(1)               |
|                                       |                          | Yes(3)             | Yes(3)             | Yes(3)             | Yes(3)             | Yes(3)              | Yes(3)               |

**Table 3-60. Host In-Out Ordering Summary (Sheet 2 of 2)**

| Row (in)<br>Independent of<br>Column (out)? | CXL.io TLPs<br>(Col A-D) | M2S Req<br>(Col G) | M2S RwD<br>(Col H) | H2D Req<br>(Col I) | H2D Rsp<br>(Col J) | H2D Data<br>(Col K) | M2S BIRsp<br>(Col N) |
|---------------------------------------------|--------------------------|--------------------|--------------------|--------------------|--------------------|---------------------|----------------------|
| S2M NDR/DRS<br>D2H Rsp/Data<br>(Row 6)      | Yes(1)(2)                | Yes(2)             | Yes(2)             | Yes(2)             | Y/N                | Y/N                 | Y/N                  |
| D2H Req<br>(Row 7)                          | Yes(1)                   | Y/N                | Y/N                | Y/N                | Y/N                | Y/N                 | Y/N                  |
| S2M BISnp<br>(Row 13)                       | Yes(1)(2)                | Yes(2)             | Y/N                | Y/N                | Y/N                | Y/N                 | Y/N                  |

In the host ordering, the row represents incoming message class and the column represents the outgoing message class. The cases in this table show when incoming must be independent of outgoing (Yes) and when it is allowed to block incoming based on outgoing (Y/N).

| Color-coded rationale for cells in Table 3-60 |                                                               |  |  |  |
|-----------------------------------------------|---------------------------------------------------------------|--|--|--|
| Yes(1)                                        | Incoming CXL.cachemem must not be blocked by outgoing CXL.io. |  |  |  |
| Y/N(1)                                        | Incoming CXL.io may be blocked by outgoing CXL.cachemem.      |  |  |  |
| Yes(2)                                        | CXL.cachemem: Required for deadlock avoidance.                |  |  |  |
| Yes(3)                                        | CXL UIO completions are independent of CXL.cachemem.          |  |  |  |

## <span id="page-168-0"></span>3.5 Transaction Flows to Device-attached Memory

### <span id="page-168-1"></span>3.5.1 Flows for Back-Invalidate Snoops on CXL.mem

#### <span id="page-168-2"></span>3.5.1.1 Notes and Assumptions

<span id="page-168-3"></span>The Back-Invalidate Snoop (BISnp) channel provides a dedicated channel S2M to allow the owner of an HDM region to snoop a host that may have a cached copy of the line. The forward progress rules as defined in [Section 3.4](#page-164-0) ensure that the device can complete the BISnp while blocking new requests (M2S Req).

The term Snoop Filter (SF) in the following diagrams is a structure in the device that is inclusively tracking any host caching of device memory and is assumed to have a size that may be less than the total possible caching in the host. The Snoop Filter is kept inclusive of host caching by sending "Back-Invalidate Snoops" to the host when it becomes full. This full trigger that forces the BISnp is referred to as "SF Victim". In the diagrams, an "SF Miss" that is caused by an M2S request implies that the device must also allocate a new SF entry if the host is requesting a cached copy of the line. When allocating an SF entry, it may also trigger an SF Victim for a different cacheline address if the SF is full. [Figure 3-20](#page-169-1) provides the legend for the Back-Invalidate Snoop flow diagrams that appear in the subsections that follow. The "CXL.mem BI" type will cover the BI channel messages and any conflict message/flow (e.g., BIConflict) that flow on the RwD channels. Note that the "Dev/Host Specific" messages are just short-hand flows for the type of flow expected in the host or device.

<span id="page-169-1"></span>**Figure 3-20. [Flows for Back-Invalidate Snoops on CXL.mem](#page-168-1) Legend**

![](_page_169_Figure_3.jpeg)

#### <span id="page-169-0"></span>3.5.1.2 BISnp Blocking Example

[Figure 3-21](#page-169-2) starts out with MemRd that is an SF Miss in the device. The SF is full, which prevents SF allocation; thus, the device must create room in the SF by triggering an SF Victim for Address Y before it can complete the read. In this example, the read to device memory Address X is started in parallel with the BISnpInv to Address Y, but the device will be unable to complete the MemRd until it can allocate an SF which requires the BISnp to Y to complete. As part of the BISnpInv, the host finds modified data for Y which must be flushed to the device before the BISnpInv can complete. The device completes the MemWr to Y, which allows the host to complete the BISnpInv to Y with the BIRspI. That completion allows the SF allocation to occur for Address X, which enables the Cmp-E and MemData to be sent.

<span id="page-169-2"></span>**Figure 3-21. Example BISnp with Blocking of M2S Req**

![](_page_169_Figure_7.jpeg)

#### <span id="page-170-0"></span>3.5.1.3 Conflict Handling

A conflict is defined as a case where S2M BISnp and M2S Req are active at the same time to the same address. There are two cases to consider: Early Conflict and Late Conflict. The two cases are ambiguous to the host side of the link until observation of a Cmp message relative to BIConflictAck. The conflict handshake starts when by the host detecting a BISnp to the same address as a pending Req. The host sends a BIConflict with the Tag of the M2S Req and device responds to a BIConflict with a BIConflictAck which must push prior Cmp\* messages within the NDR channel. This ordering relationship is fundamental to allow the host to correctly resolve the two cases.

The Early Conflict case in [Figure 3-22](#page-170-1) is defined as a case where M2S Req is blocked (or in flight) at the device while S2M BISnp is active. The host observing BIConflictAck before Cmp-E determines the M2S MemRd is still pending so that it can reply with RspI.

<span id="page-170-1"></span>**Figure 3-22. BISnp Early Conflict**

![](_page_170_Figure_6.jpeg)

Late conflict is captured in [Figure 3-23](#page-171-1) and is defined as the case where M2S Req was processed and completions are in flight when BISnp is started. In the example below, the Cmp-E message is observed at the host before BIConflictAck, so the host must process the BISnpInv with E-state ownership, which requires it to degrade E to I before completing the BISnpInv with BIRspI. Note that MemData has no ordering requirement and can be observed either before or after the BIConflictAck, although this example shows it after which delays the host's ability to immediately process the internal SnpInv X.

<span id="page-171-1"></span>**Figure 3-23. BISnp Late Conflict**

![](_page_171_Figure_3.jpeg)

#### <span id="page-171-0"></span>3.5.1.4 Block Back-Invalidate Snoops

To support increased efficient snooping the BISnp channel defines messages that can Snoop multiple cachelines in the host in a single message. These messages support either 2 or 4 cachelines where the base address must be naturally aligned with the length (128B or 256B). The host is allowed to respond with either a single block response or individual snoop responses per cacheline.

[Figure 3-24](#page-172-0) is an example of a Block response case. In this example the host receives the BISnpInvBlk for Y, which is a 256B block. Internally the host logic is showing resolving coherence by snooping Y0 and Y2 and the host HA tracker knows the other portions of the block Y1 and Y3 are already in the invalid state, so it does not need to snoop for that portion of the 256B block. Once snoop responses for Y0 and Y2 are completed, the Host HA can send the BIRspIBlk indicating that the entire block is in Istate within the host, thereby allowing the device to have Exclusive access to the block. This results in the SF in I-state for the block and the device cache in E-state.

<span id="page-172-0"></span>Figure 3-24. Block BISnp with Block Response

**Figure 3-25.**

![](_page_172_Figure_3.jpeg)

Figure 3-25 is an example where the host sends individual cacheline responses on CXL.mem for each cacheline of the block. The host encodes the 2-bit Lower Address (LowAddr) of the cacheline (Address[7:6]) with each cacheline response to allow the device to determine for which portion of the block the response is intended. The device may see the response messages in any order, which is why LA must be explicitly sent. In a Block, BISnp Address[7:6] is used to indicate the offset and length of the block as defined in Table 3-48 and is naturally aligned to the length.

**Figure 3-24. Block BISnp with Block Response**

<span id="page-173-2"></span>Figure 3-25. Block BISnp with Cacheline Response

![](_page_173_Figure_3.jpeg)

### <span id="page-173-0"></span>3.5.2 Flows for Type 1 Devices and Type 2 Devices

#### <span id="page-173-1"></span>3.5.2.1 Notes and Assumptions

The transaction flow diagrams below are intended to be illustrative of the flows between the Host and device for access to device-attached Memory using the Bias-Based Coherency mechanism described in Section 2.2.2. However, these flows are not comprehensive of every Host and device interaction. The diagrams below make the following assumptions:

- The device contains a coherency engine which is called DCOH in the diagrams below.
- The DCOH contains a Snoop Filter which tracks any caches (called Dev cache) implemented on the device. This is not strictly required, and the device is free to choose an implementation specific mechanism as long as the coherency rules are obeyed.
- The DCOH contains host coherence tracking logic for the device-attached memory. This tracking logic is referred to as a Bias Table in the context of the HDM-D memory region. For HDM-DB, it is referred to as a Directory or a Host Snoop Filter. The implementation of this is device specific.
- The device-specific aspects of the flow, illustrated using red flow arrows, need not conform exactly to the diagrams below. These can be implemented in a devicespecific manner.
- Device-attached Memory exposed in a Type 2 device can be either HDM-D or HDM-DB. HDM-D will resolve coherence using a request that is issued on CXL.cache and

the Host will send a Mem\*Fwd as a response on the CXL.mem Req channel. The HDM-DB region uses the separate CXL.mem BISnp channel to manage coherence with detailed flows covered in [Section 3.5.1](#page-168-1). This section will indicate where the flows differ.

[Figure 3-26](#page-174-1) provides the legend for the diagrams that follow.

<span id="page-174-1"></span>**Figure 3-26. [Flows for Type 1 Devices and Type 2 Devices](#page-173-0) Legend**

![](_page_174_Figure_5.jpeg)

#### <span id="page-174-0"></span>3.5.2.2 Requests from Host

Please note that the flows shown in this section [\(Requests from Host\)](#page-174-0) do not change on the CXL interface regardless of the bias state of the target region. This effectively means that the device needs to give the Host a consistent response, as expected by the Host and shown in [Figure 3-27](#page-174-2).

<span id="page-174-2"></span>**Figure 3-27. Example Cacheable Read from Host**

![](_page_174_Figure_9.jpeg)

In the above example, the Host requested a cacheable non-exclusive copy of the line. The non-exclusive aspect of the request is communicated using the "SnpData" semantic. In this example, the request got a snoop filter hit in the DCOH, which caused the device cache to be snooped. The device cache downgraded the state from Exclusive to Shared and returned the Shared data copy to the Host. The Host is told of the state of the line using the Cmp-S semantic.

<span id="page-175-0"></span>**Figure 3-28. Example Read for Ownership from Host**

![](_page_175_Figure_3.jpeg)

In the above example, the Host requested a cacheable exclusive copy of the line. The exclusive aspect of the request is communicated using the "SnpInv" semantic, which asks the device to invalidate its caches. In this example, the request got a snoop filter hit in the DCOH, which caused the device cache to be snooped. The device cache downgraded the state from Exclusive to Invalid and returned the Exclusive data copy to the Host. The Cmp-E semantic is used to communicate the line state to the Host.

<span id="page-176-0"></span>**Figure 3-29. Example Non Cacheable Read from Host**

![](_page_176_Figure_3.jpeg)

In the above example, the Host requested a non-cacheable copy of the line. The noncacheable aspect of the request is communicated using the "SnpCur" semantic. In this example, the request got a snoop filter hit in the DCOH, which caused the device cache to be snooped. The device cache did not need to change its caching state; however, it gave the current snapshot of the data. The Host is told that it is not allowed to cache the line using the Cmp semantic.

<span id="page-177-0"></span>**Figure 3-30. Example Ownership Request from Host - No Data Required**

![](_page_177_Figure_3.jpeg)

In the above example, the Host requested exclusive access to a line without requiring the device to send data. It communicates that to the device using an opcode of MemInv with a MetaValue of 10b (Any), which is significant in this case. It also asks the device to invalidate its caches with the SnpInv command. The device invalidates its caches and gives exclusive ownership to the Host as communicated using the Cmp-E semantic.

<span id="page-178-0"></span>**Figure 3-31. Example Flush from Host**

![](_page_178_Figure_3.jpeg)

In the above example, the Host wants to flush a line from all caches, including the device's caches, to device memory. To do so, it uses an opcode of MemInv with a MetaValue of 00b (Invalid) and a SnpInv. The device flushes its caches and returns a Cmp indication to the Host.

<span id="page-179-0"></span>Figure 3-32. Example Weakly Ordered Write from Host

![](_page_179_Figure_3.jpeg)

In the above example, the Host issues a weakly ordered write (partial or full line). The weakly ordered semantic is communicated by the embedded SnpInv. In this example, the device had a copy of the line cached. This resulted in a merge within the device before writing it back to memory and sending a Cmp indication to the Host. The term "weakly ordered" in this context refers to an expected-use model in the host CPU in which ordering of the data is not guaranteed until after the Cmp message is received. This is in contrast to a "data visibility is guaranteed with the host" CPU cache in M-state.

<span id="page-180-0"></span>**Figure 3-33. Example Write from Host with Invalid Host Caches**

![](_page_180_Figure_3.jpeg)

In the above example, the Host performed a write while guaranteeing to the device that it no longer has a valid cached copy of the line. The fact that the Host didn't need to snoop the device's caches means that the Host previously acquired an exclusive copy of the line. The guarantee on no valid cached copy is indicated by a MetaValue of 00b (Invalid).
**Figure 3-32.**


<span id="page-181-0"></span>Figure 3-34. Example Write from Host with Valid Host Caches

![](_page_181_Figure_3.jpeg)

The above example is the same as the previous one except that the Host chose to retain a valid cacheable copy of the line after the write. This is communicated to the device using a MetaValue of not 00b (Invalid).

**Figure 3-34. Example Write from Host with Valid Host Caches**

#### <span id="page-182-0"></span>3.5.2.3 Requests from Device in Host and Device Bias

<span id="page-182-1"></span>**Figure 3-35. Example Device Read to Device-attached Memory (HDM-D)**

![](_page_182_Figure_4.jpeg)

The two flows in [Figure 3-35](#page-182-1) both start with an internal CXL.cache request (RdAny) that targets the device's HDM-D address region.

In the first flow in [Figure 3-35,](#page-182-1) a device read to device attached memory happened to find the line in Host bias. Because it is in Host bias, the device needs to send the request to the Host to resolve coherency. The Host, after resolving coherency, sends a MemRdFwd on CXL.mem to complete the transaction, at which point the device can internally complete the read.

In the second flow in [Figure 3-35](#page-182-1), the device read happened to find the line in Device Bias. Because it is in Device Bias, the read can be completed entirely within the device itself and a request doesn't need to be sent to the Host.

The same device request is shown in [Figure 3-36](#page-183-0), but in this case the target is the HDM-DB address region, meaning that the BISnp channel is used to resolve coherence with the host. In this flow, the difference is that the SF Hit (similar to BIAS=host) indicates that the host could have a cached copy, so BISnpData is sent to the host to resolve coherence. After the host resolves coherence, the host responds with BIRspI indicating that the host is in I-state and that the device can proceed to access its data.

<span id="page-183-0"></span>**Figure 3-36. Example Device Read to Device-attached Memory (HDM-DB)**

![](_page_183_Figure_3.jpeg)

<span id="page-184-0"></span>**Figure 3-37. Example Device Write to Device-Attached Memory in Host Bias (HDM-D)**

![](_page_184_Figure_3.jpeg)

There are two flows shown above in [Figure 3-37](#page-184-0) for the HDM-D region. Both start with the line in Host Bias: a weakly ordered write request and a strongly ordered write request.

In the case of the weakly ordered write request, the request is issued by the device to the Host to resolve coherency. The Host resolves coherency and sends a CXL.mem MemWrFwd opcode, which carries the completion for the WOWrInv\* command on CXL.cache. The CQID associated with the CXL.cache WOWrInv\* command is reflected in the Tag of the CXL.mem MemWrFwd command. At this point, the device is allowed to complete the write internally. After sending the MemWrFwd, because the Host no longer prevents future accesses to the same line, this is considered a weakly ordered write.

In the second flow, the write is strongly ordered. To preserve the strongly ordered semantic, the Host can prevent future accesses to the same line while this write completes. However, as can be seen, this involves two transfers of the data across the link, which is inefficient. Unless strongly ordered writes are absolutely required, better performance can be achieved with weakly ordered writes.

<span id="page-185-0"></span>**Figure 3-38. Example Device Write to Device-attached Memory in Host Bias (HDM-DB)**

![](_page_185_Figure_4.jpeg)

[Figure 3-38](#page-185-0) for HDM-DB is in contrast to [Figure 3-37](#page-184-0) for the HDM-D region. In the HDM-DB flow, the BISnp channel in the CXL.mem protocol is used to resolve coherence with the host for the internal weakly ordered write. The strongly ordered write follows the same flow for both HDM-DB and HDM-D.

<span id="page-186-0"></span>**Figure 3-39. Example Device Write to Device-attached Memory**

![](_page_186_Figure_4.jpeg)

Again, two flows are shown above in [Figure 3-39](#page-186-0). In the first case, if a weakly or strongly ordered write finds the line in Device Bias, the write can be completed entirely within the device without having to send any indication to the Host.

The second flow shows a device writeback to device-attached memory. Note that if the device is doing a writeback to device-attached memory, regardless of bias state, the request can be completed within the device without having to send a request to the Host.

The HDM-DB vs. HDM-D regions have the same basic assumption in these flows such that no interaction is required with the host.

<span id="page-187-2"></span>**Figure 3-40. Example Host to Device Bias Flip (HDM-D)**

![](_page_187_Figure_3.jpeg)

[Figure 3-40](#page-187-2) captures the "Bias Flip" flows for HDM-D memory. For the HDM-DB memory region, see [Section 3.3.3](#page-136-0) for details regarding how this case is handled. Please note that the MemRdFwd will carry the CQID of the RdOwnNoData transaction in the Tag. The reason for putting the RdOwnNoData completion (MemRdFwd) on CXL.mem is to ensure that subsequent M2S Req Channel requests from the Host to the same address are ordered behind the MemRdFwd. This allows the device to assume ownership of a line as soon as the device receives a MemRdFwd without having to monitor requests from the Host.

### <span id="page-187-0"></span>3.5.3 Type 2 Memory Flows and Type 3 Memory Flows

#### <span id="page-187-1"></span>3.5.3.1 Speculative Memory Read

To support latency saving, CXL.mem includes a speculative memory read command (MemSpecRd) which is used to start memory access before the home agent has resolved coherence. This command does not receive a completion message and can be arbitrarily dropped. The host, after resolving coherence, may issue a demand read (i.e., MemRd or MemRdData) that the device should merge with the earlier MemSpecRd to achieve latency savings. See [Figure 3-41](#page-188-1) for an example of this type of flow.

The MemSpecRd command can be observed while another memory access is in progress in the device to the same cacheline address. In this condition, it is recommended that the device drops the MemSpecRd.

To avoid performance impact, it is recommended that MemSpecRd commands are treated as low priority to avoid adding latency to demand accesses. Under loaded conditions the MemSpecRd can hurt performance because of the extra bandwidth it

consumes and should be dropped when loading of memory or loading of the CXL link is detected. QoS Telemetry data as indicated by the DevLoad field is one way that loading of memory can be detected in the host or switch.

<span id="page-188-1"></span>**Figure 3-41. Example MemSpecRd**

![](_page_188_Figure_4.jpeg)

## <span id="page-188-0"></span>3.6 Flows to HDM-H in a Type 3 Device

The HDM-H address region in a Type 3 device is used as a memory expander or for Shared FAM device with software coherence where the device does not require active management of coherence with the Host. Thus, access to HDM-H does not use a DCOH agent. This allows the transaction flows to HDM-H to be simplified to just two classes, reads and writes, as shown below.

In [Figure 3-42,](#page-188-2) the optimized read flow is shown for the HDM-H address region. In this flow, only a Data message is returned. In contrast, in the HDM-D/HDM-DB address region, both NDR and Data are returned. The legend shown in [Figure 3-26](#page-174-1) also applies to the transaction flows.

<span id="page-188-2"></span>**Figure 3-42. Read from Host to HDM-H**

![](_page_188_Figure_9.jpeg)

Unlike reads, writes to the HDM-H region use the same flow as the HDM-D/HDM-DB region and always complete with an S2M NDR Cmp message. This common write flow is shown in [Figure 3-43.](#page-189-0)

<span id="page-189-0"></span>**Figure 3-43. Write from Host to All HDM Regions**

![](_page_189_Figure_4.jpeg)
