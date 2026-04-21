# <span id="page-190-0"></span>4.0 CXL Link Layers

## <span id="page-190-1"></span>4.1 CXL.io Link Layer

<span id="page-190-4"></span><span id="page-190-3"></span>The CXL.io link layer acts as an intermediate stage between the CXL.io transaction layer and the Flex Bus Physical layer. Its primary responsibility is to provide a reliable mechanism for exchanging transaction layer packets (TLPs) between two components on the link. The PCIe\* Data Link Layer is utilized as the link layer for CXL.io Link layer. Please refer to chapter titled "Data Link Layer Specification" in PCIe Base Specification for details. In 256B Flit mode, the PCIe-defined PM and Link Management DLLPs are not applicable for CXL.io and must not be used.

<span id="page-190-2"></span>**Figure 4-1. Flex Bus Layers - CXL.io Link Layer Highlighted**

![](_page_190_Figure_6.jpeg)

In addition, for 68B Flit mode, the CXL.io link layer implements the framing/deframing of CXL.io packets. CXL.io uses the Encoding for 8 GT/s, 16 GT/s, and 32 GT/s data rates only (see "128b/130b Encoding for 8.0 GT/s, 16.0 GT/s, and 32.0 GT/s Data Rates" in PCIe Base Specification for details).

This chapter highlights the notable framing and application of symbols to lanes that are specific for CXL.io. Note that when viewed on the link, the framing symbol-to-lane mapping will be shifted as a result of additional CXL framing (i.e., two bytes of Protocol ID and two reserved bytes) and of interleaving with other CXL protocols.

For CXL.io, only the x16 Link transmitter and receiver framing requirements described in PCIe Base Specification apply regardless of the negotiated link width. The framing related rules for N = 1, 2, 4, and 8 do not apply. For downgraded Link widths, where number of active lanes is less than x16, a single x16 data stream is formed using x16 framing rules and transferred over x16/(degraded link width) degraded link width streams.

The CXL.io link layer forwards a framed I/O packet to the Flex Bus Physical layer. The Flex Bus Physical layer framing rules are defined in [Chapter 6.0.](#page-286-3)

For 256B Flit mode, NOP-TLP alignment rules from PCIe Base Specification for PCIe Flit mode are shifted as a result of two bytes of Flit Type at the beginning of the flit.

The CXL.io link layer must guarantee that if a transmitted TLP ends exactly at the flit boundary, there must be a subsequent transmitted CXL.io flit. Please refer to [Section 6.2.2.7](#page-295-3) for more details.

## <span id="page-191-0"></span>4.2 CXL.cache and CXL.mem 68B Flit Mode Common Link Layer

### <span id="page-191-1"></span>4.2.1 Introduction

[Figure 4-2](#page-192-0) shows where the CXL.cache and CXL.mem link layer exists in the Flex Bus layered hierarchy. The link layer has two modes of operation: 68B flit and 256B flit. 68B flit, which defines 66B in the link layer and 2B in the ARB/MUX, supports the physical layer up to 32 GT/s. To support higher speeds a flit definition of 256B is defined; the reliability flows for that flit definition are handled in the Physical layer, so retry flows from 68B Flit mode are not applicable. 256B flits can support any legal transfer rate, but are required for >32 GT/s. The 256B flit definition and requirements are captured in [Section 4.3](#page-229-1). There are Transaction Layer features that require 256B flits and those features include CacheID, Back-Invalidate Snoop (BISnp), and Port Based Routing (PBR).

<span id="page-192-0"></span>**Figure 4-2. Flex Bus Layers - CXL.cache + CXL.mem Link Layer Highlighted**

<span id="page-192-1"></span>![](_page_192_Figure_3.jpeg)

As previously mentioned, CXL.cache and CXL.mem protocols use a common Link Layer. This chapter defines the properties of this common Link Layer. Protocol information, including definition of fields, opcodes, transaction flows, etc., can be found in [Section 3.2](#page-105-3) and [Section 3.3](#page-133-2), respectively.

### <span id="page-193-0"></span>4.2.2 High-Level CXL.cachemem Flit Overview

<span id="page-193-2"></span>The CXL.cachemem flit size is a fixed 528b. There are 2B of CRC code and 4 slots of 16B each as shown below.

<span id="page-193-1"></span>**Figure 4-3. CXL.cachemem Protocol Flit Overview**

|                                                                                                                                                                                                                  | Bit #<br>67<br>345<br>012 |  |
|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------|--|
| 001122<br>3<br>3                                                                                                                                                                             | Flit Header               |  |
| 445566<br>Slot Byte #<br>778899<br>10<br>10<br>11<br>11<br>12<br>12<br>13<br>13<br>14<br>14<br>15<br>15                                                                  | Header Slot               |  |
| 16<br>0<br>17<br>1<br>18<br>2<br>19<br>3<br>20<br>4<br>21<br>5<br>22<br>6<br>Slot Byte #<br>23<br>7<br>24<br>8<br>25<br>9<br>26<br>10<br>27<br>11<br>28<br>12<br>29<br>13<br>30<br>14<br>31<br>15                | Generic Slot              |  |
| Slot Byte #<br>32<br>0<br>33<br>1<br>34<br>2<br>35<br>3<br>36<br>4<br>37<br>5<br>38<br>6<br>Slot Byte #<br>39<br>7<br>40<br>8<br>41<br>9<br>42<br>10<br>43<br>11<br>44<br>12<br>45<br>13<br>46<br>14<br>47<br>15 | Generic Slot              |  |
| 48<br>0<br>49<br>1<br>50<br>2<br>51<br>3<br>52<br>4<br>53<br>5<br>54<br>6<br>Slot Byte #<br>55<br>7<br>56<br>8<br>57<br>9<br>58<br>10<br>59<br>11<br>60<br>12<br>61<br>13<br>62<br>14                            | Generic Slot              |  |
| 63<br>15<br>64<br>0<br>65<br>1                                                                                                                                                                                   | CRC                       |  |

<span id="page-194-0"></span>**Figure 4-4. CXL.cachemem All Data Flit Overview**

<span id="page-194-1"></span>![](_page_194_Figure_3.jpeg)

An example of a Protocol flit in the device to Host direction is shown below. For detailed descriptions of slot formats, see Section 4.2.3.

<span id="page-195-0"></span>Figure 4-5. Example of a Protocol Flit from Device to Host

**Figure 4-5.**

![](_page_195_Figure_4.jpeg)

A "Header" Slot is defined as one that carries a "Header" of link-layer specific information, including the definition of the protocol-level messages contained in the remainder of the header as well as in the other slots in the flit.

A "Generic" Slot can carry one or more request/response messages or a single 16B data chunk.

The flit can be composed of a Header Slot and 3 Generic Slots or four 16B Data Chunks.

The Link Layer flit header uses the same definition for both the Upstream Ports, as well as the Downstream Ports, as summarized in [Table 4-1](#page-196-0).

<span id="page-196-0"></span>**Table 4-1. CXL.cachemem Link Layer Flit Header Definition**

| Field Name | Brief Description                                                                                            | Length in Bits |
|------------|--------------------------------------------------------------------------------------------------------------|----------------|
| Type       | This field distinguishes between a Protocol or a Control flit.                                               | 1              |
| Ak         | This is an acknowledgment of 8 successful flit transfers.<br>Reserved for RETRY, and for INIT control flits. | 1              |
| BE         | Byte Enable (Reserved for control flits).                                                                    | 1              |
| Sz         | Size (Reserved for control flits).                                                                           | 1              |
| ReqCrd     | Request Credit Return.<br>Reserved for RETRY, and for INIT control flits.                                    | 4              |
| DataCrd    | Data Credit Return.<br>Reserved for RETRY, and for INIT control flits.                                       | 4              |
| RspCrd     | Response Credit Return.<br>Reserved for RETRY, and for INIT control flits.                                   | 4              |
| Slot 0     | Slot 0 Format Type (Reserved for control flits).                                                             | 3              |
| Slot 1     | Slot 1 Format Type (Reserved for control flits).                                                             | 3              |
| Slot 2     | Slot 2 Format Type (Reserved for control flits).                                                             | 3              |
| Slot 3     | Slot 3 Format Type (Reserved for control flits).                                                             | 3              |
| RSVD       | Reserved                                                                                                     | 4              |
| Total      |                                                                                                              | 32             |

In general, bits or encodings that are not defined will be marked "Reserved" or "RSVD" in this specification. These bits should be cleared to 0 by the sender of the packet and the receiver should ignore them. Please also note that certain fields with static 0/1 values will be checked by the receiving Link Layer when decoding a packet. For example, Control flits have several static bits defined. A Control flit that passes the CRC check but fails the static bit check should be treated as a standard CRC error or as a fatal error when in "RETRY\_LOCAL\_NORMAL state of the LRSM. Logging and reporting of such errors is device specific. Checking of these bits reduces the probability of silent error under conditions where the CRC check fails to detect a long burst error. However, link layer must not cause fatal error whenever it is under shadow of CRC errors (i.e., its LRSM is not in RETRY\_LOCAL\_NORMAL state). This is prescribed because all-data-flit can alias to control messages after a CRC error and those alias cases may result in static bit check failure.

The following describes how the flit header information is encoded.

<span id="page-196-1"></span>**Table 4-2. Type Encoding**

| Value | Flit Type | Description                                                                                                                               |
|-------|-----------|-------------------------------------------------------------------------------------------------------------------------------------------|
| 0     | Protocol  | This is a flit that carries CXL.cache or CXL.mem protocol-related information.                                                            |
| 1     | Control   | This is a flit inserted by the link layer only for link layer-specific functionality.<br>These flits are not exposed to the upper layers. |

The Ak field is used as part of the link layer retry protocol to signal CRC-passing receipt of flits from the remote transmitter. The transmitter sets the Ak bit to acknowledge successful receipt of 8 flits; a cleared Ak bit is ignored by the receiver.

The BE (Byte Enable) and Sz (Size) fields have to do with the variable size of data messages. To reach its efficiency targets, the CXL.cachemem link layer assumes that generally all bytes are enabled for most data, and that data is transmitted at the full cacheline granularity. When all bytes are enabled, the link layer does not transmit the byte enable bits, but instead clears the Byte Enable field of the corresponding flit header. When the receiver decodes that the Byte Enable field is cleared, it must regenerate the byte enable bits as all 1s before passing the data message on to the transaction layer. If the Byte Enable bit is set, the link layer Rx expects an additional data chunk slot that contains byte enable information. Note that this will always be the last slot of data for the associated request.

Similarly, the Sz field reflects the fact that the CXL.cachemem protocol allows transmission of data at the half cacheline granularity. When the Size bit is set, the link layer Rx expects four slots of data chunks, corresponding to a full cacheline. When the Size bit is cleared, it expects only two slots of data chunks. In the latter case, each half cacheline transmission will be accompanied by its own data header. A critical assumption of packing the Size and Byte Enable information in the flit header is that the Tx flit packet may begin at most one data message per flit.

*Note:* Multi-Data-Headers are not allowed to be sent when Sz=0 or BE=1 as described in the flit packing rules in [Section 4.2.5](#page-211-1).

> [Table 4-3](#page-197-0) describes legal values of Sz and BE for various data transfers. For cases where a 32B split transfer is sent that includes Byte Enables, the trailing Byte Enables apply only to the 32B sent. The Byte Enable bits that are applicable to that transfer are aligned based on which half of the cacheline is applicable to the transfer (BE[63:32] for Upper half of the cacheline or BE[31:0] for the lower half of the cacheline). This means that each of the split 32B transfers that are used to form a cacheline of data will include Byte Enables if Byte Enables are needed. Illegal use will cause an uncorrectable error. The reserved bits included in the BE slot may not be preserved when passing through a switch.

<span id="page-197-1"></span><span id="page-197-0"></span>**Table 4-3. Legal Values of Sz and BE Fields**

| Type of Data Transfer | 32B Transfer Permitted in 68B Flit?1 | BE Permitted? |
|-----------------------|--------------------------------------|---------------|
| CXL.cache H2D Data    | Yes                                  | No            |
| CXL.mem M2S Data      | No                                   | Yes           |
| CXL.cache D2H Data    | Yes                                  | Yes           |
| CXL.mem S2M Data      | Yes                                  | No            |

1. The 32B transfer allowance is only defined for 68B flit definition and does not apply for 256B flit.

The transmitter sets the CRD fields to indicate freed resources that are available in the co-located receiver for use by the remote transmitter. Credits are given for transmission per message class, which is why the flit header contains independent Request, Response, and Data CRD fields. Note that there are no Requests sourced in the S2M direction, and that there are no Responses sourced in the M2S direction. Details of the channel mapping are captured in [Table 4-5.](#page-198-1) Credits returned for channels not supported by the device or the host should be silently discarded. The granularity of credits is per message. These fields are encoded exponentially, as delineated in [Table 4-4.](#page-198-0)

*Note:* Messages sent on Data channels require a single data credit for the entire message. This means that 1 credit allows for one data transfer, including the header of the message, regardless of whether the transfer is 64B, or 32B, or contains Byte Enables.

The transaction layer requires all messages that carry payload to send 64B and the link layer allows for those to be sent as independent 32B messages to optimize latency for implementation-specific cases in which only 32B of data is ready to send.

<span id="page-198-0"></span>**Table 4-4. CXL.cachemem Credit Return Encodings**

| Credit Return Encoding[3]   | Protocol          |  |  |
|-----------------------------|-------------------|--|--|
| 0                           | CXL.cache         |  |  |
| 1                           | CXL.mem           |  |  |
| Credit Return Encoding[2:0] | Number of Credits |  |  |
| 000b                        | 0                 |  |  |
| 001b                        | 1                 |  |  |
| 010b                        | 2                 |  |  |
| 011b                        | 4                 |  |  |
| 100b                        | 8                 |  |  |
| 101b                        | 16                |  |  |
| 110b                        | 32                |  |  |
| 111b                        | 64                |  |  |

<span id="page-198-1"></span>**Table 4-5. ReqCrd/DataCrd/RspCrd Channel Mapping**

| Credit Field | Credit Bit 3 Encoding | Link Direction | Channel     |
|--------------|-----------------------|----------------|-------------|
|              |                       | Upstream       | D2H Request |
|              | 0 - CXL.cache         | Downstream     | H2D Request |
| ReqCrd       |                       | Upstream       | Reserved    |
|              | 1 - CXL.mem           | Downstream     | M2S Request |
|              | 0 - CXL.cache         | Upstream       | D2H Data    |
| DataCrd      |                       | Downstream     | H2D Data    |
|              | 1 - CXL.mem           | Upstream       | S2M DRS     |
|              |                       | Downstream     | M2S RwD     |
|              | 0 - CXL.cache         | Upstream       | D2H Rsp     |
| RspCrd       |                       | Downstream     | H2D Rsp     |
|              | 1 - CXL.mem           | Upstream       | S2M NDR     |
|              |                       | Downstream     | Reserved    |

Finally, the Slot Format Type fields encode the Slot Format of both the header slot and of the other generic slots in the flit (if the Flit Type bit specifies that the flit is a Protocol flit). The subsequent sections detail the protocol message contents of each slot format, but [Table 4-6](#page-199-0) provides a quick reference for the Slot Format field encoding.

*Note:* Format H6 is defined for use with Integrity and Data Encryption. See details of requirements for its use in [Chapter 11.0](#page-891-2).

<span id="page-199-0"></span>**Table 4-6. Slot Format Field Encoding**

| Slot Format | H2D/M2S |                   | D2H/S2M |                   |
|-------------|---------|-------------------|---------|-------------------|
| Encoding    | Slot 0  | Slots 1, 2, and 3 | Slot 0  | Slots 1, 2, and 3 |
| 000b        | H0      | G0                | H0      | G0                |
| 001b        | H1      | G1                | H1      | G1                |
| 010b        | H2      | G2                | H2      | G2                |
| 011b        | H3      | G3                | H3      | G3                |
| 100b        | H4      | G4                | H4      | G4                |
| 101b        | H5      | G5                | H5      | G5                |
| 110b        | H6      | RSVD              | H6      | G6                |
| 111b        | RSVD    | RSVD              | RSVD    | RSVD              |

[Table 4-7](#page-199-1) and [Table 4-8](#page-200-1) describe the slot format and the type of message contained by each format for both directions.

<span id="page-199-1"></span>**Table 4-7. H2D/M2S Slot Formats**

| Format to Req | H2D/M2S                                               |                |  |
|---------------|-------------------------------------------------------|----------------|--|
| Type Mapping  | Type                                                  | Length in Bits |  |
| H0            | CXL.cache Req + CXL.cache Rsp                         | 96             |  |
| H1            | CXL.cache Data Header + 2 CXL.cache Rsp               | 88             |  |
| H2            | CXL.cache Req + CXL.cache Data Header                 | 88             |  |
| H3            | 4 CXL.cache Data Header                               | 96             |  |
| H4            | CXL.mem RwD Header                                    | 87             |  |
| H5            | CXL.mem Req Only                                      | 87             |  |
| H6            | MAC slot used for link integrity                      | 96             |  |
| G0            | CXL.cache/ CXL.mem Data Chunk                         | 128            |  |
| G1            | 4 CXL.cache Rsp                                       | 128            |  |
| G2            | CXL.cache Req + CXL.cache Data Header + CXL.cache Rsp | 120            |  |
| G3            | 4 CXL.cache Data Header + CXL.cache Rsp               | 128            |  |
| G4            | CXL.mem Req + CXL.cache Data Header                   | 111            |  |
| G5            | CXL.mem RwD Header + CXL.cache Rsp                    | 119            |  |

<span id="page-200-1"></span>**Table 4-8. D2H/S2M Slot Formats**

| Format to Req<br>Type Mapping | D2H/S2M                                               |                |  |  |  |  |
|-------------------------------|-------------------------------------------------------|----------------|--|--|--|--|
|                               | Type                                                  | Length in Bits |  |  |  |  |
| H0                            | CXL.cache Data Header + 2 CXL.cache Rsp + CXL.mem NDR | 87             |  |  |  |  |
| H1                            | CXL.cache Req + CXL.cache Data Header                 | 96             |  |  |  |  |
| H2                            | 4 CXL.cache Data Header + CXL.cache Rsp               | 88             |  |  |  |  |
| H3                            | CXL.mem DRS Header + CXL.mem NDR                      | 70             |  |  |  |  |
| H4                            | 2 CXL.mem NDR                                         | 60             |  |  |  |  |
| H5                            | 2 CXL.mem DRS Header                                  | 80             |  |  |  |  |
| H6                            | MAC slot used for link integrity                      | 96             |  |  |  |  |
| G0                            | CXL.cache/ CXL.mem Data Chunk                         | 128            |  |  |  |  |
| G1                            | CXL.cache Req + 2 CXL.cache Rsp                       | 119            |  |  |  |  |
| G2                            | CXL.cache Req + CXL.cache Data Header + CXL.cache Rsp | 116            |  |  |  |  |
| G3                            | 4 CXL.cache Data Header                               | 68             |  |  |  |  |
| G4                            | CXL.mem DRS Header + 2 CXL.mem NDR                    | 100            |  |  |  |  |
| G5                            | 2 CXL.mem NDR                                         | 60             |  |  |  |  |
| G6                            | 3 CXL.mem DRS Header                                  | 120            |  |  |  |  |

### <span id="page-200-0"></span>4.2.3 Slot Format Definition

Slot diagrams in this section include abbreviations for bit field names to allow them to fit into the diagram. In the diagrams, most abbreviations are obvious, but the following abbreviation list ensures clarity:

- Bg = Bogus
- Ch = ChunkValid
- LA0 = LowerAddr[0]
- LA1 = LowerAddr[1]
- LI3 = LD-ID[3]
- MV0 = MetaValue[0]
- MV1 = MetaValue[1]
- O4 = Opcode[4]
- Op0 = Opcode[0]
- Poi = Poison
- R11 = RspData[11]
- RSVD = Reserved
- RV = Reserved
- SL3 = Slot3[2]
- Tag15 = Tag[15]
- U11 = UQID[11]
- Val = Valid

#### <span id="page-201-0"></span>4.2.3.1 H2D and M2S Formats

<span id="page-201-1"></span>**Figure 4-6. H0 - H2D Req + H2D Rsp**

![](_page_201_Figure_4.jpeg)

<span id="page-201-2"></span>**Figure 4-7. H1 - H2D Data Header + H2D Rsp + H2D Rsp**

![](_page_201_Figure_6.jpeg)

<span id="page-202-0"></span>**Figure 4-8. H2 - H2D Req + H2D Data Header**

![](_page_202_Figure_3.jpeg)

<span id="page-202-1"></span>**Figure 4-9. H3 - 4 H2D Data Header**

![](_page_202_Figure_5.jpeg)

<span id="page-202-2"></span>**Figure 4-10. H4 - M2S RwD Header**

![](_page_202_Figure_7.jpeg)

<span id="page-203-0"></span>**Figure 4-11. H5 - M2S Req**

![](_page_203_Figure_3.jpeg)

<span id="page-203-1"></span>**Figure 4-12. H6 - MAC**

<span id="page-203-3"></span>![](_page_203_Figure_5.jpeg)

<span id="page-203-2"></span>**Figure 4-13. G0 - H2D/M2S Data**

![](_page_203_Figure_7.jpeg)

<span id="page-204-0"></span>**Figure 4-14. G0 - M2S Byte Enable**

![](_page_204_Figure_3.jpeg)

<span id="page-204-1"></span>**Figure 4-15. G1 - 4 H2D Rsp**

![](_page_204_Figure_5.jpeg)

<span id="page-204-2"></span>**Figure 4-16. G2 - H2D Req + H2D Data Header + H2D Rsp**

![](_page_204_Figure_7.jpeg)

<span id="page-205-0"></span>**Figure 4-17. G3 - 4 H2D Data Header + H2D Rsp**

![](_page_205_Figure_3.jpeg)

<span id="page-205-1"></span>**Figure 4-18. G4 - M2S Req + H2D Data Header**

![](_page_205_Figure_5.jpeg)

<span id="page-205-2"></span>**Figure 4-19. G5 - M2S RwD Header + H2D Rsp**

![](_page_205_Figure_7.jpeg)

#### <span id="page-206-0"></span>4.2.3.2 D2H and S2M Formats

The original slot definitions ensured that all header bits for a message are in contiguous bits. The S2M NDR message expanded by two bits to fit the 2-bit DevLoad field. Some slot formats that carry NDR messages include non-contiguous bits within the slot to account for the DevLoad. The formats impacted are H4, G4, and G5 and the noncontiguous bits are denoted as "DevLoad\*" ("\*" is the special indicator with separate color/pattern for the NDR message with non-contiguous bits). By expanding the slots in this way, backward compatibility with the original contiguous bit definition is maintained by ensuring that only RSVD slot bits are used to expand the headers. Other slot formats that carry a single NDR message can be expanded and keep the contiguous header bits because the NDR message is the last message in the slot formats (see Formats H0 and H3).

<span id="page-206-1"></span>Figure 4-20. HO - D2H Data Header + 2 D2H Rsp + S2M NDR

![](_page_206_Figure_5.jpeg)

**Figure 4-20. D2H and S2M Formats**

<span id="page-206-2"></span>Figure 4-21. H1 - D2H Req + D2H Data Header

![](_page_206_Figure_7.jpeg)

<span id="page-207-0"></span>Figure 4-22. H2 - 4 D2H Data Header + D2H Rsp

![](_page_207_Figure_3.jpeg)
**Figure 4-21. The original slot definitions ensured that all header bits for a message are in contiguous**


<span id="page-207-1"></span>Figure 4-23. H3 - S2M DRS Header + S2M NDR

**Figure 4-22. 0**

![](_page_207_Figure_5.jpeg)

**Figure 4-23. Figure 4-24.**

<span id="page-207-2"></span>Figure 4-24. H4 - 2 S2M NDR

![](_page_207_Figure_7.jpeg)

**Figure 4-24.**

<span id="page-208-0"></span>**Figure 4-25. H5 - 2 S2M DRS Header**

![](_page_208_Figure_3.jpeg)

<span id="page-208-1"></span>**Figure 4-26. H6 - MAC**

![](_page_208_Figure_5.jpeg)

<span id="page-208-2"></span>**Figure 4-27. G0 - D2H/S2M Data**

![](_page_208_Figure_7.jpeg)

<span id="page-209-0"></span>**Figure 4-28. G0 - D2H Byte Enable**

![](_page_209_Figure_3.jpeg)

<span id="page-209-1"></span>**Figure 4-29. G1 - D2H Req + 2 D2H Rsp**

![](_page_209_Figure_5.jpeg)

<span id="page-209-2"></span>**Figure 4-30. G2 - D2H Req + D2H Data Header + D2H Rsp**

![](_page_209_Figure_7.jpeg)

<span id="page-210-0"></span>**Figure 4-31. G3 - 4 D2H Data Header**

![](_page_210_Figure_3.jpeg)

<span id="page-210-1"></span>**Figure 4-32. G4 - S2M DRS Header + 2 S2M NDR**

![](_page_210_Figure_5.jpeg)

<span id="page-210-2"></span>**Figure 4-33. G5 - 2 S2M NDR**

![](_page_210_Figure_7.jpeg)

<span id="page-211-2"></span>**Figure 4-34. G6 - 3 S2M DRS Header**

![](_page_211_Figure_3.jpeg)

### <span id="page-211-0"></span>4.2.4 Link Layer Registers

Architectural registers associated with CXL.cache and CXL.mem are defined in [Section 8.2.4.19.](#page-556-2)

### <span id="page-211-1"></span>4.2.5 68B Flit Packing Rules

The packing rules are defined below. It is assumed that a given queue has credits toward the Rx and any protocol dependencies (SNP-GO ordering, for example) have already been considered:

- Rollover is defined as any time a data transfer needs more than one flit. Note that a data chunk that contains 128b (Format G0), can only be scheduled in Slot 1, Slot 2, and Slot 3 of a protocol flit since Slot 0 has only 96b available, as 32b are taken up by the flit header. The following rules apply to Rollover data chunks:
  - If there's a rollover of more than 3 16B data chunks, the next flit must necessarily be an all-data flit.
  - If there's a rollover of 3 16B data chunks, Slot 1, Slot 2, and Slot 3 must necessarily contain the 3 rollover data chunks. Slot 0 will be packed independently (it is allowed for Slot 0 to have the Data Header for the next data transfer).
  - If there's a rollover of 2 16B data chunks, Slot 1 and Slot 2 must necessarily contain the 2 rollover data chunks. Slot 0 and Slot 3 will be packed independently.
  - If there's a rollover of 1 16B data chunk, Slot 1 must necessarily contain the rollover data chunk. Slot 0, Slot 2, and Slot 3 will be packed independently.
  - If there's no rollover, each of the 4 slots will be packed independently.
- Care must be taken to ensure fairness between packing of CXL.cache and CXL.mem transactions. Similarly, care must be taken to ensure fairness between channels within a given protocol. The exact mechanism to ensure fairness is implementation specific.
- Valid messages within a given slot must be tightly packed. Which means, if a slot contains multiple possible locations for a given message, the Tx must pack the message in the first available location before advancing to the next available location.

- Valid messages within a given flit must be tightly packed. Which means, if a flit contains multiple possible slots for a given message, the Tx must pack the message in the first available slot before advancing to the next available slot.
- Empty slots are defined as slots without any valid bits set and they may be mixed with other slots in any order as long as all other packing rules are followed. For an example refer to [Figure 4-5](#page-195-0) where slot H3 could have no valid bits set indicating an empty slot, but the 1st and 2nd generic slots, G1 and G2 in the example, may have mixed valid bits set.
- If a valid Data Header is packed in a given slot, the next available slot for data transfer (Slot 1, Slot 2, Slot 3 or an all-data flit) will be guaranteed to have data associated with the header. The Rx will use this property to maintain a shadow copy of the Tx Rollover counts. This enables the Rx to expect all-data flits where a flit header is not present.
- For data transfers, the Tx must send 16B data chunks in cacheline order. That is, chunk order 01 for 32B transfers and chunk order 0123 for 64B transfers.
- A slot with more than one data header (e.g., H5 in the S2M direction, or G3 in the H2D direction) is called a multi-data header slot or an MDH slot. MDH slots can only be sent for full cacheline transfers when both 32B chunks are immediately available to pack (i.e., BE = 0, Sz = 1). An MDH slot can only be used if both agents support MDH (defeature is defined in [Section 8.2.4.19.7\)](#page-561-0). If MDH is received when it is disabled it is considered a fatal error.
- An MDH slot format may be selected by the Tx only if there is more than 1 valid Data Header to pack in that slot.
- Control flits cannot be interleaved with all-data flits. This also implies that when an all-data flit is expected following a protocol flit (due to Rollover), the Tx cannot send a Control flit before the all-data flit.
- For non-MDH containing flits, there can be at most 1 valid Data Header in that flit. Also, an MDH containing flit cannot be packed with another valid Data Header in the same flit.
- The maximum number of messages that can be sent in a given flit is restricted to reduce complexity in the receiver, which writes these messages into credited queues. By restricting the number of messages across the entire flit, the number of write ports into the receiver's queues are constrained. The maximum number of messages per type within a flit (sum, across all slots) is:

```
D2H Request --> 4
D2H Response --> 2
D2H Data Header --> 4
D2H Data --> 4*16B 
S2M NDR --> 2
S2M DRS Header --> 3
S2M DRS Data --> 4*16B
```

```
H2D Request --> 2
H2D Response --> 4
H2D Data Header --> 4
H2D Data --> 4*16B
M2S Req --> 2
M2S RwD Header --> 1
M2S RwD Data --> 4*16B
```

• For a given slot, lower bit positions are defined as bit positions that appear starting from lower order Byte #. That is, bits are ordered starting from (Byte 0, Bit 0) through (Byte 15, Bit 7).

- For multi-bit message fields like Address[MSB:LSB], the least significant bits will appear in lower order bit positions.
- Message ordering within a flit is based on flit bit numbering (i.e., the earliest messages are placed at the lowest flit bit positions and progressively later messages are placed at progressively higher bit positions). Examples: An M2S Req 0 packed in Slot 0 precedes an M2S Req 1 packed in Slot 1. Similarly, a Snoop packed in Slot 1 follows a GO packed in Slot 0, and this ordering must be maintained. Finally, for Header Slot Format H1, an H2D Response packed starting from Byte 7 precedes an H2D Response packed starting from Byte 11.

### <span id="page-213-0"></span>4.2.6 Link Layer Control Flit

Link Layer Control flits do not follow flow control rules applicable to protocol flits. That is, they can be sent from an entity without any credits. These flits must be processed and consumed by the receiver within the period to transmit a flit on the channel since there are no storage or flow control mechanisms for these flits. [Table 4-9](#page-213-1) lists all the Controls flits supported by the CXL.cachemem link layer.

<span id="page-213-1"></span>**Table 4-9. CXL.cachemem Link Layer Control Types**

| LLCTRL<br>Encoding | LLCTRL<br>Type Name | Description                                                                                                                   | Retryable?<br>(Enters the<br>LLRB) |
|--------------------|---------------------|-------------------------------------------------------------------------------------------------------------------------------|------------------------------------|
| 0001b              | RETRY               | Link layer RETRY flit                                                                                                         | No                                 |
| 0000b              | LLCRD               | Flit containing link layer credit return and/or Ack<br>information, but no protocol information.                              | Yes                                |
| 0010b              | IDE                 | Integrity and Data Encryption control messages.<br>Use in flows described in Chapter 11.0 that were<br>introduced in CXL 2.0. | Yes                                |
| 1100b              | INIT                | Link layer initialization flit                                                                                                | Yes                                |
| Others             | Reserved            | N/A                                                                                                                           | N/A                                |

The 3-bit CTL\_FMT field was added to control messages and uses bits that were reserved in CXL 1.1 control messages. All control messages used in CXL 1.1 have this field encoded as 000b to maintain backward compatibility. This field is used to distinguish formats added in CXL 2.0 control messages that require a larger payload field. The new format increases the payload field from 64 bits to 96 bits and uses CTL\_FMT encoding of 001b.

<span id="page-214-1"></span>A detailed description of the control flits is presented below.

<span id="page-214-0"></span>CXL.cachemem Link Layer Control Details (Sheet 1 of 2) **Table 4-10.** 

| Flit Type | CTL_FMT/<br>LLCTRL | SubType | SubType<br>Description | Payload | Payload Description                                                                                                                                                                                                                                                                             |
|-----------|--------------------|---------|------------------------|---------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| LLCRD     | 000b/0000b         | 0000b   | RSVD                   | 63:0    | RSVD                                                                                                                                                                                                                                                                                            |
|           |                    |         |                        | 2:0     | Acknowledge[2:0]                                                                                                                                                                                                                                                                                |
|           |                    | 0001b   | Acknowledge            | 3       | RSVD                                                                                                                                                                                                                                                                                            |
|           |                    |         |                        | 7:4     | Acknowledge[7:4]                                                                                                                                                                                                                                                                                |
|           |                    |         |                        | 63:8    | RSVD                                                                                                                                                                                                                                                                                            |
|           |                    | Others  | RSVD                   | 63:0    | RSVD                                                                                                                                                                                                                                                                                            |
|           |                    | 0000b   | RETRY.Idle             | 63:0    | RSVD                                                                                                                                                                                                                                                                                            |
|           |                    |         | RETRY.Req              | 7:0     | Requester's Retry Sequence Number (Eseq)                                                                                                                                                                                                                                                        |
|           |                    |         |                        | 15:8    | RSVD                                                                                                                                                                                                                                                                                            |
|           |                    | 0001b   |                        | 20:16   | Contains NUM_RETRY                                                                                                                                                                                                                                                                              |
|           |                    |         |                        | 25:21   | Contains NUM_PHY_REINIT (for debug)                                                                                                                                                                                                                                                             |
|           |                    |         |                        | 63:26   | RSVD                                                                                                                                                                                                                                                                                            |
|           | 000b/0001b         | 0010b   | RETRY.Ack              | 0       | Empty: The Empty bit indicates that the LLR contains no valid data and therefore the NUM_RETRY value should be reset                                                                                                                                                                            |
|           |                    |         |                        | 1       | Viral: The Viral bit indicates that the transmitting agent is in a Viral state                                                                                                                                                                                                                  |
|           |                    |         |                        | 2       | RSVD                                                                                                                                                                                                                                                                                            |
| RETRY     |                    |         |                        | 7:3     | Contains an echo of the NUM_RETRY value from the LLR.Req                                                                                                                                                                                                                                        |
|           |                    |         |                        | 15:8    | Contains the WrPtr value of the retry queue for debug purposes                                                                                                                                                                                                                                  |
|           |                    |         |                        | 23:16   | Contains an echo of the Eseq from the LLR.Req                                                                                                                                                                                                                                                   |
|           |                    |         |                        | 31:24   | Contains the NumFreeBuf value of the retry queue for debug purposes                                                                                                                                                                                                                             |
|           |                    |         |                        | 47:32   | Viral LD-ID Vector[15:0]: Included for MLD links to indicate which LD-ID is impacted by viral. Applicable only when the Viral bit (bit 1 of this payload) is set. Bit 0 of the vector encodes LD-ID=0, bit 1 is LD-ID=1, etc. Field is treated as Reserved for ports that do not support LD-ID. |
|           |                    |         |                        | 63:48   | RSVD                                                                                                                                                                                                                                                                                            |
|           |                    | 0011b   | RETRY.Frame            | 63:0    | Payload is RSVD.  Flit required to be sent before a RETRY.Req or RETRY.Ack flit to allow said flit to be decoded without risk of aliasing.                                                                                                                                                      |
|           |                    | Others  | RSVD                   | 63:0    | RSVD                                                                                                                                                                                                                                                                                            |

Table 4-10. CXL.cachemem Link Layer Control Details (Sheet 2 of 2)

| Flit Type | CTL_FMT/<br>LLCTRL | SubType | SubType<br>Description | Payload | Payload Description                                                                                                                                 |
|-----------|--------------------|---------|------------------------|---------|-----------------------------------------------------------------------------------------------------------------------------------------------------|
| IDE       | 001b/0010b         | 0000b   | IDE.Idle               | 95:0    | Payload RSVD Message Sent as part of IDE flows to pad sequences with idle flits. Refer to Chapter 11.0 for details on the use of this message.      |
|           |                    | 0001b   | IDE.Start              | 95:0    | Payload RSVD<br>Message sent to begin flit encryption.                                                                                              |
|           |                    | 0010b   | IDE.TMAC               | 95:0    | MAC Field uses all 96 bits of payload. Truncated MAC Message sent to complete a MAC epoch early. Only used when no protocol messages exist to send. |
|           |                    | Others  | RSVD                   | 95:0    | RSVD                                                                                                                                                |
| INIT      | 000b/1100b         | 1000b   | INIT.Param             | 3:0     | Interconnect Version: Version of CXL the port is compliant with.  CXL 1.0/1.1 = 0001b  CXL 2.0 and above = 0010b  Others Reserved                   |
|           |                    |         |                        | 7:4     | RSVD                                                                                                                                                |
|           |                    |         |                        | 12:8    | RSVD                                                                                                                                                |
|           |                    |         |                        | 23:13   | RSVD                                                                                                                                                |
|           |                    |         |                        | 31:24   | LLR Wrap Value: Value after which LLR sequence counter should wrap to 0.                                                                            |
|           |                    |         |                        | 63:32   | RSVD                                                                                                                                                |
|           |                    | Others  | RSVD                   | 63:0    | RSVD                                                                                                                                                |

In the LLCRD flit, the total number of flit acknowledgments being returned is determined by creating the Full\_Ack return value, where:

Full\_Ack = {Acknowledge[7:4],Ak,Acknowledge[2:0]}, where the Ak bit is from the flit header.

The flit formats for the control flit are illustrated below.

<span id="page-215-0"></span>**Figure 4-35. LLCRD Flit Format (Only Slot 0 is Valid; Others are Reserved)** 

![](_page_215_Figure_8.jpeg)

<span id="page-216-0"></span>**Figure 4-36. RETRY Flit Format (Only Slot 0 is Valid; Others are Reserved)**

![](_page_216_Figure_3.jpeg)

<span id="page-216-1"></span>**Figure 4-37. IDE Flit Format (Only Slot 0 is Valid; Others are Reserved)**

![](_page_216_Figure_5.jpeg)

<span id="page-216-2"></span>**Figure 4-38. INIT Flit Format (Only Slot 0 is Valid; Others are Reserved)**

![](_page_216_Figure_7.jpeg)

*Note:* The RETRY.Req and RETRY.Ack flits belong to the type of flit to which receiving devices must respond, even in the shadow of a previous CRC error. In addition to checking the CRC of a RETRY flit, the receiving device should also check as many defined bits (those listed as having hardcoded 1/0 values) as possible to increase confidence in qualifying an incoming flit as a RETRY message.

### <span id="page-217-0"></span>4.2.7 Link Layer Initialization

Link Layer Initialization must be started after a Physical Layer Link Down to Link Up transition and the link has trained successfully to L0. During Initialization and after the INIT flit has been sent, the CXL.cachemem Link Layer can only send Control-RETRY flits until Link Initialization is complete. The following describes how the link layer is initialized and credits are exchanged.

- The Tx portion of the Link Layer must wait until the Rx portion of the Link Layer has received at least one valid flit that is CRC clean before sending the Control-INIT.Param flit. Before this condition is met, the Link Layer must transmit only Control-RETRY flits (i.e., RETRY.Frame/Req/Ack/Idle flits).
  - If for any reason the Rx portion of the Link Layer is not ready to begin processing flits beyond Control-INIT and Control-RETRY, the Tx will stall transmission of LLCTR-INIT.Param flit
  - RETRY.Frame/Req/Ack are sent during this time as part of the regular Retry flow.
  - RETRY.Idle flits are sent prior to sending a INIT.Param flit even without a retry condition to ensure the remote agent can observe a valid flit.
- The Control-INIT.Param flit must be the first non-Control-RETRY flit transmitted by the Link Layer
- The Rx portion of the Link Layer must be able to receive a Control-INIT.Param flit immediately upon completion of Physical Layer initialization because the first valid flit may be a Control-INIT.Param
- Received Control-INIT.Param values (i.e., LLR Wrap Value) must be made "active", that is, applied to their respective hardware states within 8 flit clocks of error-free reception of Control-INIT.Param flit.
  - Until an error-free INIT.Param flit is received and these values are applied, LLR Wrap Value shall assume a default value of 9 for the purposes of ESEQ tracking.
- Any non-RETRY flits received before Control-INIT.Param flit will trigger an Uncorrectable Error.
- Only a single Control-INIT.Param flit is sent. Any CRC error conditions with a Control-INIT.Param flit will be dealt with by the Retry state machine and replayed from the Link Layer Retry Buffer.
- Receipt of a Control-INIT.Param flit after a Control-INIT.Param flit has already been received should be considered an Uncorrectable Error.
- It is the responsibility of the Rx to transmit credits to the sender using standard credit return mechanisms after link initialization. Each entity should know how many buffers it has and set its credit return counters to these values. Then, during normal operation, the standard credit return logic will return these credits to the sender.
- Immediately after link initialization, the credit exchange mechanism will use the LLCRD flit format.
- It is possible that the receiver will make more credits available than the sender can track for a given message class. For correct operation, it is therefore required that the credit counters at the sender be saturating. Receiver will drop all credits it receives for unsupported channels (e.g., Type 3 device receiving any CXL.cache credits).

• Credits should be sized to achieve desired levels of bandwidth considering roundtrip time of credit return latency. This is implementation and usage dependent.

### <span id="page-218-0"></span>4.2.8 CXL.cachemem Link Layer Retry

The link layer provides recovery from transmission errors using retransmission, or Link Layer Retry (LLR). The sender buffers every retryable flit sent in a local Link Layer Retry Buffer (LLRB). To uniquely identify flits in this buffer, the retry scheme relies on sequence numbers which are maintained within each device. Unlike in PCIe, CXL.cachemem sequence numbers are not communicated between devices with each flit to optimize link efficiency. The exchange of sequence numbers occurs only through link layer control flits during an LLR sequence. The sequence numbers are set to a predetermined value (0) during Link Layer Initialization and they are implemented using a wraparound counter. The counter wraps back to 0 after reaching the depth of the retry buffer. This scheme makes the following assumptions:

- The round-trip delay between devices is more than the maximum of the link layer clock or flit period.
- All protocol flits are stored in the retry buffer. See [Section 4.2.8.5.1](#page-223-1) for further details on the handling of non-retryable control flits.

Note that for efficient operation, the size of the retry buffer must be larger than the round-trip delay. This includes:

- Time to send a flit from the sender
- Flight time of the flit from sender to receiver
- Processing time at the receiver to detect an error in the flit
- Time to accumulate and, if needed, force Ack return and send embedded Ack return back to the sender
- Flight time of the Ack return from the receiver to the sender
- Processing time of Ack return at the original sender

Otherwise, the LLR scheme will introduce latency, as the transmitter will have to wait for the receiver to confirm correct receipt of a previous flit before the transmitter can free space in its LLRB and send a new flit. Note that the error case is not significant because transmission of new flits is effectively stalled until successful retransmission of the erroneous flit anyway.

#### <span id="page-218-1"></span>4.2.8.1 LLR Variables

The retry scheme maintains two state machines and several state variables. Although the following text describes them in terms of one transmitter and one receiver, both the transmitter and receiver side of the retry state machines and the corresponding state variables are present at each device because of the bidirectional nature of the link. Since both sides of the link implement both transmitter and receiver state machines, for clarity this discussion will use the term "local" to refer to the entity that detects a CRC error, and "remote" to refer to the entity that sent the flit that was erroneously received.

The receiving device uses the following state variables to keep track of the sequence number of the next flit to arrive.

• **ESeq**: This indicates the expected sequence number of the next valid flit at the receiving link layer entity. ESeq is incremented by one (modulo the size of the LLRB) on error-free reception of a retryable flit. ESeq stops incrementing after an error is detected on a received flit until retransmission begins (RETRY.Ack message is received). Link Layer Initialization sets ESeq to 0. Note that there is no way for the receiver to know that an error was for a non-retryable vs. retryable flit. For any CRC error, it will initiate the link layer retry flow as usual, and effectively the transmitter will resend from the first retryable flit sent.

The sending entity maintains two indexes into its LLRB, as indicated below.

• **WrPtr**: This indexes the entry of the LLRB that will record the next new flit. When an entity sends a flit, it copies that flit into the LLRB entry indicated by the WrPtr and then increments the WrPtr by one (modulo the size of the LLRB). This is implemented using a wraparound counter that wraps around to 0 after reaching the depth of the LLRB. Non-Retryable Control flits do not affect the WrPtr. WrPtr stops incrementing after receiving an error indication at the remote entity (RETRY.Req message) except as described in the implementation note below, until normal operation resumes again (all flits from the LLRB have been retransmitted). WrPtr is initialized to 0 and is incremented only when a flit is placed into the LLRB.

> **IMPLEMENTATION NOTE**

WrPtr may continue to increment after receiving RETRY.Req message if there are prescheduled All Data Flits that are not yet sent over the link. This implementation will ensure that All Data Flits not interleaved with other flits are correctly logged into the Link Layer Retry Buffer.

• **RdPtr**: This is used to read the contents out of the LLRB during a retry scenario. The value of this pointer is set by the sequence number sent with the retransmission request (RETRY.Req message). The RdPtr is incremented by one (modulo the size of the LLRB) whenever a flit is sent, either from the LLRB in response to a retry request or when a new flit arrives from the transaction layer and regardless of the states of the local or remote retry state machines. If a flit is being sent when the RdPtr and WrPtr are the same, then it indicates that a new flit is being sent; otherwise, it must be a flit from the retry buffer.

The LLR scheme uses an explicit acknowledgment that is sent from the receiver to the sender to remove flits from the LLRB at the sender. The acknowledgment is indicated via an ACK bit in the headers of flits flowing in the reverse direction. In CXL.cachemem, a single ACK bit represents 8 acknowledgments. Each entity keeps track of the number of available LLRB entries and the number of received flits pending acknowledgment through the following variables.

- **NumFreeBuf**: This indicates the number of free LLRB entries at the entity. NumFreeBuf is decremented by 1 whenever an LLRB entry is used to store a transmitted flit. NumFreeBuf is incremented by the value encoded in the Ack/ Full\_Ack (Ack is the protocol flit bit AK, Full\_Ack defined as part of LLCRD message) field of a received flit. NumFreeBuf is initialized at reset time to the size of the LLRB. The maximum number of retry queue entries at any entity is limited to 255 (8-bit counter). Also, note that the retry buffer at any entity is never filled to its capacity, therefore NumFreeBuf is never 0. If there is only 1 retry buffer entry available, then the sender cannot send a Retryable flit. This restriction is required to avoid ambiguity between a full or an empty retry buffer during a retry sequence that may result into incorrect operation. This implies if there are only 2 retry buffer entries left (NumFreeBuf = 2), then the sender can send an Ack bearing flit only if the outgoing flit encodes a value of at least 1 (which may be a Protocol flit with Ak bit set), else an LLCRD control flit is sent with Full\_Ack value of at least 1. This is required to avoid deadlock at the link layer due to retry buffer becoming full at both entities on a link and their inability to send ACK through header flits. This rule also creates an implicit expectation that you cannot start a sequence of "All Data Flits" that cannot be completed before NumFreeBuf=2 because you must be able to inject the Ack bearing flit when NumFreeBuf=2 is reached.
- **NumAck**: This indicates the number of acknowledgments accumulated at the receiver. NumAck increments by 1 when a retryable flit is received. NumAck is decremented by 8 when the ACK bit is set in the header of an outgoing flit. If the

outgoing flit is coming from the LLRB and its ACK bit is set, NumAck does not decrement. At initialization, NumAck is set to 0. The minimum size of the NumAck field is the size of the LLRB. NumAck at each entity must be able to keep track of at least 255 acknowledgments.

The LLR protocol requires that the number of retry queue entries at each entity must be at least 22 entries (Size of Forced Ack (16) + Max All-Data-Flit (4) + 2) to prevent deadlock.

#### <span id="page-220-0"></span>4.2.8.2 LLCRD Forcing

<span id="page-220-1"></span>Recall that the LLR protocol requires space available in the LLRB to transmit a new flit, and that the sender must receive explicit acknowledgment from the receiver before freeing space in the LLRB. In scenarios where the traffic flow is asymmetric, this requirement could result in traffic throttling and possibly even starvation.

Suppose that the A→B direction has heavy traffic, but there is no traffic in the B→<sup>A</sup> direction. In this case, A could exhaust its LLRB size, while B never has any return traffic in which to embed Acks. In CXL, we want to minimize injected traffic to reserve bandwidth for the other traffic stream(s) sharing the link.

To avoid starvation, CXL must permit LLCRD Control message forcing (injection of a non-traffic flit to carry an Acknowledge and a Credit return (ACK/CRD)), but this function must be constrained to avoid wasting bandwidth. In CXL, when B has accumulated a programmable minimum number of Acks to return, B's CXL.cachemem link layer will inject an LLCRD flit to return an Acknowledge. The threshold of pending Acknowledges before forcing the LLCRD can be adjusted using the "Ack Force Threshold" field in the CXL Link Layer Ack Timer Control register (see [Section 8.2.4.19.6\)](#page-560-0).

There is also a timer-controlled mechanism to force LLCRD when the timer reaches a threshold. The timer will clear whenever an ACK/CRD carrying message is sent. It will increment every link layer clock in which an ACK/CRD carrying message is not sent and any Credit value to return is greater than 0 or Acknowledge to return is greater than 1. The reason the Acknowledge threshold value is specified as "greater than 1" instead of "greater than 0" is to avoid repeated forcing of LLCRD when no other retryable flits are being sent. If the timer incremented when the pending Acknowledge count is "greater than 0," there would be a continuous exchange of LLCRD messages carrying Acknowledges on an otherwise idle link; this is because the LLCRD is itself retryable and results in a returning Acknowledge in the other direction. The result is that the link layer would never be truly idle when the transaction layer traffic is idle. The timer threshold to force LLCRD is configurable using the Ack or CRD Flush Retimer field in the CXL Link Layer Ack Timer Control register. It should also be noted that the CXL.cachemem link layer must accumulate a minimum of 8 Acks to set the ACK bit in a CXL.cachemem flit header. If LLCRD forcing occurred after the accumulation of 8 Acks, it could result in a negative beat pattern where real traffic always arrives soon after a forced Ack, but not long enough after for enough Acks to re-accumulate to set the ACK bit. In the worst case, this could double the bandwidth consumption of the CXL.cachemem side. By waiting for at least 16 Acks to accumulate, the CXL.cachemem link layer ensures that it can still opportunistically return Acks in a protocol flit avoiding the need to force an LLCRD for Ack return. It is recommended that the Ack Force Threshold value be set to 16 or greater in the CXL Link Layer Ack Timer Control register to reduce overhead of LLCRD injection.

It is recommended that link layer prioritize other link layer flits before LLCRD forcing.

Pseudo-code for forcing function below:

```
IF (SENDING_ACK_CRD_MESSAGE==FALSE AND (ACK_TO_RETURN >1 OR CRD_TO_RETURN>0))
   TimerValue++
ELSE 
   TimerValue=0
IF (TimerValue >=Ack_or_CRD_Flush_Retimer OR ACK_TO_RETURN >= Ack Force_Threshold)
   Force_LLCRD = TRUE
ELSE
   Force_LLCRD=FALSE
```

*Note:* Ack or CRD Flush Retimer and Ack Force Threshold are values that come from the CXL Link Layer Ack Timer Control register (see [Section 8.2.4.19.6](#page-560-0)).

<span id="page-221-1"></span>**Figure 4-39. Retry Buffer and Related Pointers**

![](_page_221_Figure_7.jpeg)

#### <span id="page-221-0"></span>4.2.8.3 LLR Control Flits

The LLR Scheme uses several link layer control flits of the RETRY format to communicate the state information and the implicit sequence numbers between the entities.

• RETRY.Req: This flit is sent from the entity that received a flit in error to the sending entity. The flit contains the expected sequence number (ESeq) at the receiving entity, indicating the index of the flit in the retry queue at the remote entity that must be retransmitted. It also contains the NUM\_RETRY value of the sending entity which is defined in [Section 4.2.8.5.1](#page-223-1). This message is also triggered as part of the Initialization sequence even when no error is observed as described in [Section 4.2.7](#page-217-0).

- RETRY.Ack: This flit is sent from the entity that is responding to an error detected at the remote entity. It contains a reflection of the NUM\_RETRY value from the corresponding RETRY.Req message. The flit contains the WrPtr value at the sending entity for debug purposes only. The WrPtr value should not be used by the retry state machines in any way. This flit will be followed by the flit identified for retry by the ESeq number.
- RETRY.Idle: This flit is sent during the retry sequence when there are no protocol flits to be sent (see [Section 4.2.8.5.2](#page-225-0) for details) or a retry queue is not ready to be sent. For example, it can be used for debug purposes for designs that need additional time between sending the RETRY.Ack and the actual contents of the LLR queue.
- RETRY.Frame: This flit is sent along with a RETRY.Req or RETRY.Ack flit to prevent aliased decoding of these flits (see [Section 4.2.8.5](#page-223-0) for further details).

[Table 4-11](#page-222-1) describes the impact of RETRY messages on the local and remote retry state machines. In this context, the "sender" refers to the Device sending the message and the "receiver" refers to the Device receiving the message. Note that how this maps to which device detected the CRC error and which sent the erroneous message depends on the message type. For example, for a RETRY.Req sequence, the sender detected the CRC error, but for a RETRY.Ack sequence, it's the receiver that detected the CRC error.

#### <span id="page-222-0"></span>4.2.8.4 RETRY Framing Sequences

Recall that the CXL.cachemem flit formatting specifies an all-data flit for link efficiency. This flit is encoded as part of the header of the preceding flit and contains no header information of its own. This introduces the possibility that the data contained in this flit could happen to match the encoding of a RETRY flit.

This introduces a problem at the receiver. It must be certain to decode the actual RETRY flit, but it must not falsely decode an aliasing data flit as a RETRY flit. In theory it might use the header information of the stream it receives in the shadow of a CRC error to determine whether it should attempt to decode the subsequent flit. Therefore, the receiver cannot know with certainty which flits to treat as header-containing (decode) and which to ignore (all-data).

CXL introduces the RETRY.Frame flit for this purpose to disambiguate a control sequence from an All-Data Flit (ADF). Due to MDH, 4 ADF can be sent back-to-back. Hence, a RETRY.Req sequence comprises 5 RETRY.Frame flits immediately followed by a RETRY.Req flit, and a RETRY.Ack sequence comprises 5 RETRY.Frame flits immediately followed by a RETRY.Ack flit. This is shown in [Figure 4-40](#page-227-2).

<span id="page-222-1"></span>**Table 4-11. Control Flits and Their Effect on Sender and Receiver States**

| RETRY Message                                                                                     | Sender State                                                                                           | Receiver State                                                                                                         |  |
|---------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------|--|
| RETRY.Idle                                                                                        | Unchanged.                                                                                             | Unchanged.                                                                                                             |  |
| RETRY.Frame + RETRY.Req<br>Sequence                                                               | Local Retry State Machine (LRSM)<br>is updated. NUM_RETRY is<br>incremented. See<br>Section 4.2.8.5.1. | Remote Retry State Machine<br>(RRSM) is updated. RdPtr is set to<br>ESeq sent with the flit. See<br>Section 4.2.8.5.3. |  |
| RETRY.Frame + RETRY.Ack<br>Sequence                                                               | RRSM is updated.                                                                                       | LRSM is updated.                                                                                                       |  |
| RETRY.Frame, RETRY.Req, or<br>RETRY.Ack message that is not as<br>part of a valid framed sequence | Unchanged.                                                                                             | Unchanged (drop the flit).                                                                                             |  |

*Note:* A RETRY.Ack sequence that arrives when a RETRY.Ack is not expected will be treated as an error by the receiver. Error resolution in this case is device specific though it is recommended that this results in the machine halting operation. It is recommended that this error condition not change the state of the LRSM.

#### <span id="page-223-0"></span>4.2.8.5 LLR State Machines

The LLR scheme is implemented with two state machines: Remote Retry State Machine (RRSM) and Local Retry State Machine (LRSM). These state machines are implemented by each entity and together determine the overall state of the transmitter and receiver at the entity. The states of the retry state machines are used by the send and receive controllers to determine what flit to send and the actions needed to process a received flit.

##### <span id="page-223-1"></span>4.2.8.5.1 Local Retry State Machine (LRSM)

This state machine is activated at the entity that detects an error on a received flit. The possible states for this state machine are:

<span id="page-223-2"></span>- • RETRY\_LOCAL\_NORMAL: This is the initial or default state indicating normal operation (no CRC error has been detected).
- RETRY\_LLRREQ: This state indicates that the receiver has detected an error on a received flit and a RETRY.Req sequence must be sent to the remote entity.
- RETRY\_LOCAL\_IDLE: This state indicates that the receiver is waiting for a RETRY.Ack sequence from the remote entity in response to its RETRY.Req sequence. The implementation may require substates of RETRY\_LOCAL\_IDLE to capture, for example, the case where the last flit received is a Frame flit and the next flit expected is a RETRY.Ack.
- RETRY\_PHY\_REINIT: The state machine remains in this state for the duration of the virtual Link State Machine (vLSM) being in Retrain.
- RETRY\_ABORT: This state indicates that the retry attempt has failed and the link cannot recover. Error logging and reporting in this case is device specific. This is a terminal state.

The local retry state machine also has the three counters described below. The counters and thresholds described below are implementation specific.

• **TIMEOUT**: This counter is enabled whenever a RETRY.Req request is sent from an entity and the LRSM state becomes RETRY\_LOCAL\_IDLE. The TIMEOUT counter is disabled and the counting stops when the LRSM state changes to some state other than RETRY\_LOCAL\_IDLE. The TIMEOUT counter is reset to 0 at link layer initialization and whenever the LRSM state changes from RETRY\_LOCAL\_IDLE to RETRY\_LOCAL\_NORMAL or RETRY\_LLRREQ. The TIMEOUT counter is also reset when the vLSM transitions from Retrain to Active (the LRSM transition through RETRY\_PHY\_REINIT to RETRY\_LLRREQ). If the counter has reached its threshold without receiving a RETRY.Ack sequence, then the RETRY.Req request is sent again to retry the same flit. See [Section 4.2.8.5.2](#page-225-0) for a description of when TIMEOUT increments.

*Note:* It is suggested that the value of TIMEOUT should be no less than 4096 transfers.

• **NUM\_RETRY**: This counter is used to count the number of RETRY.Req requests sent to retry the same flit. The counter remains enabled during the whole retry sequence (state is not RETRY\_LOCAL\_NORMAL). It is reset to 0 at initialization. It is also reset to 0 when a RETRY.Ack sequence is received with the Empty bit set or whenever the LRSM state is RETRY\_LOCAL\_NORMAL and an error-free retryable flit is received. The counter is incremented whenever the LRSM state changes from RETRY\_LLRREQ to RETRY\_LOCAL\_IDLE. If the counter reaches a threshold (called MAX\_NUM\_RETRY), then the local retry state machine transitions to the RETRY\_PHY\_REINIT. The NUM\_RETRY counter is also reset when the vLSM transitions from Retrain to Active (the LRSM transition through RETRY\_PHY\_REINIT to RETRY\_LLRREQ).

*Note:* It is suggested that the value of MAX\_NUM\_RETRY should be no less than Ah.

Revision 3.2, Version 1.0 224

• **NUM\_PHY\_REINIT**: This counter is used to count the number of transitions to RETRY\_PHY\_REINIT that are generated during an LLR sequence due to the number of retries that exceed MAX\_NUM\_RETRY. The counter remains enabled during the whole retry sequence (state is not RETRY\_LOCAL\_NORMAL). It is reset to 0 at initialization and after successful completion of the retry sequence. The counter is incremented whenever the LRSM changes from RETRY\_LLRREQ to RETRY\_PHY\_REINIT due to the number of retries that exceed MAX\_NUM\_RETRY. If the counter reaches a threshold (called MAX\_NUM\_PHY\_REINIT) instead of transitioning from RETRY\_LLRREQ to RETRY\_PHY\_REINIT, the LRSM will transition to RETRY\_ABORT. The NUM\_PHY\_REINIT counter is also reset whenever a RETRY.Ack sequence is received with the Empty bit set.

*Note:* It is suggested that the value of MAX\_NUM\_PHY\_REINIT should be no less than Ah.

Note that the condition of TIMEOUT reaching its threshold is not mutually exclusive with other conditions that cause the LRSM state transitions. RETRY.Ack sequences can be assumed to never arrive at the time at which the retry requesting device times out and sends a new RETRY.Req sequence (by appropriately setting the value of TIMEOUT – see [Section 4.2.8.5.2\)](#page-225-0). If this case occurs, no guarantees are made regarding the behavior of the device (behavior is "undefined" from a Spec perspective and is not validated from an implementation perspective). Consequently, the LLR Timeout value should not be reduced unless it can be certain this case will not occur. If an error is detected at the same time as TIMEOUT reaches its threshold, then the error on the received flit is ignored, TIMEOUT is taken, and a repeat RETRY.Req sequence is sent to the remote entity.

<span id="page-224-0"></span>**Table 4-12. Local Retry State Transitions (Sheet 1 of 2)**

| Current Local Retry<br>State                                                                | Condition                                                                        | Next Local Retry State | Actions                                                                                                                                                                                                                                                          |
|---------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------|------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| RETRY_LOCAL_NORMAL                                                                          | An error free retryable flit is<br>received.                                     | RETRY_LOCAL_NORMAL     | Increment NumFreeBuf using the<br>amount specified in the ACK or<br>Full_Ack fields.<br>Increment NumAck by 1.<br>Increment Eseq by 1.<br>NUM_RETRY is reset to 0.<br>NUM_PHY_REINIT is reset to 0.<br>Received flit is processed<br>normally by the link layer. |
| RETRY_LOCAL_NORMAL                                                                          | Error free non-retryable flit<br>(other than RETRY.Req<br>sequence) is received. | RETRY_LOCAL_NORMAL     | Received flit is processed.                                                                                                                                                                                                                                      |
| RETRY_LOCAL_NORMAL                                                                          | Error free RETRY.Req sequence<br>is received.                                    | RETRY_LOCAL_NORMAL     | RRSM is updated.                                                                                                                                                                                                                                                 |
| RETRY_LOCAL_NORMAL                                                                          | Error is detected on a received<br>flit.                                         | RETRY_LLRREQ           | Received flit is discarded.                                                                                                                                                                                                                                      |
| RETRY_LOCAL_NORMAL                                                                          | PHY_RESET1 / PHY_REINIT2 is<br>detected.                                         | RETRY_PHY_REINIT       | None.                                                                                                                                                                                                                                                            |
| RETRY_LLRREQ                                                                                | NUM_RETRY ==<br>MAX_NUM_RETRY and<br>NUM_PHY_REINIT ==<br>MAX_NUM_PHY_REINIT     | RETRY_ABORT            | Indicate link failure.                                                                                                                                                                                                                                           |
| NUM_RETRY ==<br>MAX_NUM_RETRY and<br>RETRY_LLRREQ<br>NUM_PHY_REINIT <<br>MAX_NUM_PHY_REINIT |                                                                                  | RETRY_PHY_REINIT       | If an error-free RETRY.Req or<br>RETRY.Ack sequence is received,<br>process the flit.<br>Any other flit is discarded.<br>RetrainRequest is sent to physical<br>layer. Increment<br>NUM_PHY_REINIT.                                                               |

Table 4-12. Local Retry State Transitions (Sheet 2 of 2)

| Current Local Retry<br>State                                                                                                                                                                                | Condition                                                             | Next Local Retry State | Actions                                                                                                                                 |  |
|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------|------------------------|-----------------------------------------------------------------------------------------------------------------------------------------|--|
| RETRY_LLRREQ                                                                                                                                                                                                | NUM_RETRY < MAX_NUM_RETRY and a RETRY.Req sequence has not been sent. | RETRY_LLRREQ           | If an error-free RETRY.Req or<br>RETRY.Ack sequence is received,<br>process the flit.<br>Any other flit is discarded.                   |  |
| RETRY_LLRREQ                                                                                                                                                                                                | NUM_RETRY < MAX_NUM_RETRY and a RETRY.Req sequence has been sent.     | RETRY_LOCAL_IDLE       | If an error free RETRY.Req or RETRY.Ack sequence is received, process the flit. Any other flit is discarded. Increment NUM_RETRY.       |  |
| RETRY_LLRREQ                                                                                                                                                                                                | PHY_RESET <sup>1</sup> / PHY_REINIT <sup>2</sup> is detected.         | RETRY_PHY_REINIT       | None.                                                                                                                                   |  |
| RETRY_LLRREQ                                                                                                                                                                                                | Error is detected on a received flit                                  | RETRY_LLRREQ           | Received flit is discarded.                                                                                                             |  |
| RETRY_PHY_REINIT                                                                                                                                                                                            | Physical layer is still in reinit.                                    | RETRY_PHY_REINIT       | None.                                                                                                                                   |  |
| RETRY_PHY_REINIT                                                                                                                                                                                            | Physical layer returns from Reinit.                                   | RETRY_LLRREQ           | Received flit is discarded.  NUM_RETRY is reset to 0.                                                                                   |  |
| RETRY_LOCAL_IDLE  RETRY_LOCAL_IDLE  RETRY_LOCAL_IDLE  RETRY_Req sent by the local entity.                                                                                                                   |                                                                       | RETRY_LOCAL_NORMAL     | TIMEOUT is reset to 0.  If RETRY.Ack sequence is received with Empty bit set, NUM_RETRY is reset to 0 and NUM_PHY_REINIT is reset to 0. |  |
| RETRY_LOCAL_IDLE  RETRY_LOCAL_IDLE  RETRY_LOCAL_IDLE  RETRY_LOCAL_IDLE  RETRY.Ack sequence is received and NUM_RETRY from RETRY.Ack does NOT match the value of the last RETRY.Req sen by the local entity. |                                                                       | RETRY_LOCAL_IDLE       | Any received retryable flit is discarded.                                                                                               |  |
| RETRY_LOCAL_IDLE                                                                                                                                                                                            | TIMEOUT has reached its threshold.                                    | RETRY_LLRREQ           | TIMEOUT is reset to 0.                                                                                                                  |  |
| RETRY_LOCAL_IDLE                                                                                                                                                                                            | Error is detected on a received flit.                                 | RETRY_LOCAL_IDLE       | Any received retryable flit is discarded.                                                                                               |  |
| RETRY_LOCAL_IDLE  A flit other than RETRY.Ack/ RETRY.Req sequence is received.                                                                                                                              |                                                                       | RETRY_LOCAL_IDLE       | Any received retryable flit is discarded.                                                                                               |  |
| RETRY_LOCAL_IDLE                                                                                                                                                                                            | A RETRY.Req sequence is received.                                     | RETRY_LOCAL_IDLE       | RRSM is updated.                                                                                                                        |  |
| RETRY_LOCAL_IDLE                                                                                                                                                                                            | PHY_RESET <sup>1</sup> / PHY_REINIT <sup>2</sup> is detected.         | RETRY_PHY_REINIT       | None.                                                                                                                                   |  |
| RETRY_ABORT                                                                                                                                                                                                 | A flit is received.                                                   | RETRY_ABORT            | All received flits are discarded.                                                                                                       |  |

<span id="page-225-1"></span><sup>1.</sup> PHY\_RESET is the condition of the vLSM informing the Link Layer that it needs to initiate a Link Layer Retry due to exit from Retrain state.

##### <span id="page-225-0"></span>4.2.8.5.2 TIMEOUT Definition

After the local receiver has detected a CRC error, triggering the LRSM, the local Tx sends a RETRY.Reg sequence to initiate LLR. At this time, the local Tx also starts its TIMEOUT counter.

The purpose of this counter is to decide that either the RETRY.Reg sequence or corresponding RETRY.Ack sequence has been lost, and that another RETRY.Req attempt should be made. Recall that it is a fatal error to receive multiple RETRY. Ack sequences (i.e., a subsequent Ack without a corresponding Req is unexpected). To reduce the risk of this fatal error condition we check NUM\_RETRY value returned to filter out RETRY.Ack messages from the prior retry sequence. This is done to remove fatal condition where a

<span id="page-225-2"></span><sup>2.</sup> PHY\_REINIT is the condition of the Link Layer instructing the Phy to retrain.

![](_page_226_Picture_1.jpeg)

single retry sequence incurs a timeout while the Ack message is in flight. The TIMEOUT counter should be capable of handling worst-case latency for a RETRY.Req sequence to reach the remote side and for the corresponding RETRY.Ack sequence to return.

Certain unpredictable events (e.g., low power transitions, etc.) that interrupt link availability could add a large amount of latency to the RETRY round-trip. To make the TIMEOUT robust to such events, instead of incrementing per link layer clock, TIMEOUT increments whenever the local Tx transmits a flit, protocol, or control. Due to the TIMEOUT protocol, TIMEOUT must force injection of RETRY.Idle flits if it has no real traffic to send, so that the TIMEOUT counter continues to increment.

##### <span id="page-226-1"></span>4.2.8.5.3 Remote Retry State Machine (RRSM)

The remote retry state machine is activated at an entity if a flit sent from that entity is received in error by the local receiver, resulting in a link layer retry request (RETRY.Req sequence) from the remote entity. The possible states for this state machine are:

- RETRY\_REMOTE\_NORMAL: This is the initial or default state indicating normal operation.
- RETRY\_LLRACK: This state indicates that a link layer retry request (RETRY.Req sequence) has been received from the remote entity and a RETRY.Ack sequence followed by flits from the retry queue must be (re)sent.

The remote retry state machine transitions are described in [Table 4-13.](#page-226-0)

<span id="page-226-0"></span>**Table 4-13. Remote Retry State Transition**

| Current Remote Retry State | Condition                                                           | Next Remote Retry State |  |  |
|----------------------------|---------------------------------------------------------------------|-------------------------|--|--|
| RETRY_REMOTE_NORMAL        | Any flit, other than error free<br>RETRY.Req sequence, is received. | RETRY_REMOTE_NORMAL     |  |  |
| RETRY_REMOTE_NORMAL        | Error free RETRY.Req sequence is<br>received.                       | RETRY_LLRACK            |  |  |
| RETRY_LLRACK               | RETRY.Ack sequence is not sent.                                     | RETRY_LLRACK            |  |  |
| RETRY_LLRACK               | RETRY.Ack sequence is sent.                                         | RETRY_REMOTE_NORMAL     |  |  |
| RETRY_LLRACK               | vLSM in Retrain state.                                              | RETRY_REMOTE_NORMAL     |  |  |

*Note:* To select the priority of sending flits, the following rules apply:

- 1. Whenever the RRSM state becomes RETRY\_LLRACK, the entity must give priority to sending the Control flit with RETRY.Ack.
- 2. Except RRSM state of RETRY\_LLRACK, the priority goes to LRSM state of RETRY\_LLRREQ and in that case the entity must send a Control flit with RETRY.Req over all other flits except an all-data flit sequence.

The overall sequence of replay is shown in [Figure 4-40](#page-227-2).

<span id="page-227-2"></span>**Figure 4-40. CXL.cachemem Replay Diagram**

![](_page_227_Figure_3.jpeg)

#### <span id="page-227-0"></span>4.2.8.6 Interaction with vLSM Retrain State

On detection by the Link Layer of the vLSM transition from Active to Retrain state, the receiver side of the link layer must force a link layer retry on the next flit. Forcing an error will either initiate LLR or cause a current LLR to follow the correct error path. The LLR will ensure that no retryable flits are dropped during the physical layer reinit. Without initiating an LLR it is possible that packets/flits in flight on the physical wires could be lost or the sequence numbers could get mismatched.

Upon detection of a vLSM transition to Retrain, the LLR RRSM needs to be reset to its initial state and any instance of RETRY.Ack sequence needs to be cleared in the link layer and physical layer. The device needs to ensure that it receives a RETRY.Req sequence before it transmits a RETRY.Ack sequence.

#### <span id="page-227-1"></span>4.2.8.7 CXL.cachemem Flit CRC

The CXL.cachemem Link Layer uses a 16b CRC for transmission error detection. The 16b CRC is over the 528-bit flit. The assumptions about the type errors is as follows:

- Bit ordering runs down each lane.
- Bit Errors occur randomly or in bursts down a lane, with the majority of the errors being single-bit random errors.
- Random errors can statistically cause multiple bit errors in a single flit, so it is more likely to get 2 errors in a flit than 3 errors, and more likely to get 3 errors in a flit than 4 errors, and so on.
- There is no requirement for primitive polynomial (a polynomial that generates all elements of an extension field from a base field) because there is no fixed payload. Primitive may be the result, but it's not required.

##### 4.2.8.7.1 CRC-16 Polynomial and Detection Properties

The CRC polynomial to be used is 1F053h. The 16b CRC Polynomial has the following properties:

- All single, double, and triple bit errors detected
- Polynomial selection based on best 4-bit error detection characteristics and perfect 1-bit, 2-bit, and 3-bit error detection

##### 4.2.8.7.2 CRC-16 Calculation

Below are the 512 bit data masks for use with an XOR tree to produce the 16 CRC bits. Data Mask bits [511:0] for each CRC bit are applied to the flit bits [511:0] and XOR is performed. The resulting CRC bits are included as flit bits [527:512] are defined to be CRC[15:00]. Pseudo code example for CRC bit 15 of this is CRC[15] = XOR (DM[15][511:0] AND Flit[511:0]).

The flit Data Masks for the 16 CRC bits are located below:

DM[15][511:0] =

512'hEF9C\_D9F9\_C4BB\_B83A\_3E84\_A97C\_D7AE\_DA13\_FAEB\_01B8\_5B20\_4A4C\_AE1E\_79D9\_7753\_5D21\_DC7F\_DD6A\_ 38F0\_3E77\_F5F5\_2A2C\_636D\_B05C\_3978\_EA30\_CD50\_E0D9\_9B06\_93D4\_746B\_2431

DM[14][511:0] =

512'h9852\_B505\_26E6\_6427\_21C6\_FDC2\_BC79\_B71A\_079E\_8164\_76B0\_6F6A\_F911\_4535\_CCFA\_F3B1\_3240\_33DF\_ 2488\_214C\_0F0F\_BF3A\_52DB\_6872\_25C4\_9F28\_ABF8\_90B5\_5685\_DA3E\_4E5E\_B629

DM[13][511:0] =

512'h23B5\_837B\_57C8\_8A29\_AE67\_D79D\_8992\_019E\_F924\_410A\_6078\_7DF9\_D296\_DB43\_912E\_24F9\_455F\_C485\_ AAB4\_2ED1\_F272\_F5B1\_4A00\_0465\_2B9A\_A5A4\_98AC\_A883\_3044\_7ECB\_5344\_7F25

DM[12][511:0] =

512'h7E46\_1844\_6F5F\_FD2E\_E9B7\_42B2\_1367\_DADC\_8679\_213D\_6B1C\_74B0\_4755\_1478\_BFC4\_4F5D\_7ED0\_3F28\_ EDAA\_291F\_0CCC\_50F4\_C66D\_B26E\_ACB5\_B8E2\_8106\_B498\_0324\_ACB1\_DDC9\_1BA3

DM[11][511:0] =

512'h50BF\_D5DB\_F314\_46AD\_4A5F\_0825\_DE1D\_377D\_B9D7\_9126\_EEAE\_7014\_8DB4\_F3E5\_28B1\_7A8F\_6317\_C2FE\_ 4E25\_2AF8\_7393\_0256\_005B\_696B\_6F22\_3641\_8DD3\_BA95\_9A94\_C58C\_9A8F\_A9E0

DM[10][511:0] =

512'hA85F\_EAED\_F98A\_2356\_A52F\_8412\_EF0E\_9BBE\_DCEB\_C893\_7757\_380A\_46DA\_79F2\_9458\_BD47\_B18B\_E17F\_ 2712\_957C\_39C9\_812B\_002D\_B4B5\_B791\_1B20\_C6E9\_DD4A\_CD4A\_62C6\_4D47\_D4F0

DM[09][511:0] =

512'h542F\_F576\_FCC5\_11AB\_5297\_C209\_7787\_4DDF\_6E75\_E449\_BBAB\_9C05\_236D\_3CF9\_4A2C\_5EA3\_D8C5\_F0BF\_ 9389\_4ABE\_1CE4\_C095\_8016\_DA5A\_DBC8\_8D90\_6374\_EEA5\_66A5\_3163\_26A3\_EA78

DM[08][511:0] =

512'h2A17\_FABB\_7E62\_88D5\_A94B\_E104\_BBC3\_A6EF\_B73A\_F224\_DDD5\_CE02\_91B6\_9E7C\_A516\_2F51\_EC62\_F85F\_ C9C4\_A55F\_0E72\_604A\_C00B\_6D2D\_6DE4\_46C8\_31BA\_7752\_B352\_98B1\_9351\_F53C

DM[07][511:0] =

512'h150B\_FD5D\_BF31\_446A\_D4A5\_F082\_5DE1\_D377\_DB9D\_7912\_6EEA\_E701\_48DB\_4F3E\_528B\_17A8\_F631\_7C2F\_ E4E2\_52AF\_8739\_3025\_6005\_B696\_B6F2\_2364\_18DD\_3BA9\_59A9\_4C58\_C9A8\_FA9E

DM[06][511:0] =

512'h8A85\_FEAE\_DF98\_A235\_6A52\_F841\_2EF0\_E9BB\_EDCE\_BC89\_3775\_7380\_A46D\_A79F\_2945\_8BD4\_7B18\_BE17\_ F271\_2957\_C39C\_9812\_B002\_DB4B\_5B79\_11B2\_0C6E\_9DD4\_ACD4\_A62C\_64D4\_7D4F

DM[05][511:0] =

512'hAADE\_26AE\_AB77\_E920\_8BAD\_D55C\_40D6\_AECE\_0C0C\_5FFC\_C09A\_F38C\_FC28\_AA16\_E3F1\_98CB\_E1F3\_8261\_ C1C8\_AADC\_143B\_6625\_3B6C\_DDF9\_94C4\_62E9\_CB67\_AE33\_CD6C\_C0C2\_4601\_1A96

DM[04][511:0] =

512'hD56F\_1357\_55BB\_F490\_45D6\_EAAE\_206B\_5767\_0606\_2FFE\_604D\_79C6\_7E14\_550B\_71F8\_CC65\_F0F9\_C130\_ E0E4\_556E\_0A1D\_B312\_9DB6\_6EFC\_CA62\_3174\_E5B3\_D719\_E6B6\_6061\_2300\_8D4B

DM[03][511:0] =

512'h852B\_5052\_6E66\_4272\_1C6F\_DC2B\_C79B\_71A0\_79E8\_1647\_6B06\_F6AF\_9114\_535C\_CFAF\_3B13\_2403\_3DF2\_ 4882\_14C0\_F0FB\_F3A5\_2DB6\_8722\_5C49\_F28A\_BF89\_0B55\_685D\_A3E4\_E5EB\_6294

DM[02][511:0] =

512'hC295\_A829\_3733\_2139\_0E37\_EE15\_E3CD\_B8D0\_3CF4\_0B23\_B583\_7B57\_C88A\_29AE\_67D7\_9D89\_9201\_9EF9\_ 2441\_0A60\_787D\_F9D2\_96DB\_4391\_2E24\_F945\_5FC4\_85AA\_B42E\_D1F2\_72F5\_B14A

DM[01][511:0] =

512'h614A\_D414\_9B99\_909C\_871B\_F70A\_F1E6\_DC68\_1E7A\_0591\_DAC1\_BDAB\_E445\_14D7\_33EB\_CEC4\_C900\_CF7C\_ 9220\_8530\_3C3E\_FCE9\_4B6D\_A1C8\_9712\_7CA2\_AFE2\_42D5\_5A17\_68F9\_397A\_D8A5

DM[00][511:0] =

512'hDF39\_B3F3\_8977\_7074\_7D09\_52F9\_AF5D\_B427\_F5D6\_0370\_B640\_9499\_5C3C\_F3B2\_EEA6\_BA43\_B8FF\_BAD4\_ 71E0\_7CEF\_EBEA\_5458\_C6DB\_60B8\_72F1\_D461\_9AA1\_C1B3\_360D\_27A8\_E8D6\_4863

### <span id="page-229-0"></span>4.2.9 Viral

Viral is a containment feature as described in [Section 12.4, "CXL Viral Handling."](#page-1007-3) As such, when the local socket is in a viral state, it is the responsibility of all off-die interfaces to convey this state to the remote side for appropriate handling. The CXL.cachemem link layer conveys viral status information. As soon as the viral status is detected locally, the link layer forces a CRC error on the next outgoing flit. If there is no traffic to send, the transmitter will send an LLCRD flit with a CRC error. It then embeds viral status information in the RETRY.Ack message it generates as part of the defined CRC error recovery flow.

There are two primary benefits to this methodology. First, by using the RETRY.Ack to convey viral status, we do not have to allocate a bit for this in protocol flits. Second, it allows immediate indication of viral and reduces the risk of race conditions between the viral distribution path and the data path. These risks could be particularly exacerbated by the large CXL.cache flit size and the potential limitations in which components (header, slots) allocate dedicated fields for viral indication.

To support MLD components, first introduced in CXL 2.0, a Viral LD-ID Vector is defined in the RETRY.Ack to encode which LD-ID is impacted by the viral state. This allows viral to be indicated to any set of Logical Devices. This vector is applicable only when the primary viral bit is set, and only to links that support multiple LD-ID (referred to as MLD - Multi-Logical Device). Links without LD-ID support (referred to as SLD - Single Logical Device) will treat the vector as Reserved. For MLD, the encoding of all 0s indicates that all LD-ID are in viral and is equivalent to an encoding of all 1s.

## <span id="page-229-1"></span>4.3 CXL.cachemem Link Layer 256B Flit Mode

### <span id="page-229-2"></span>4.3.1 Introduction

This mode of operation builds on PCIe Flit mode, in which the reliability flows are handled in the Physical Layer. The flit definition in the link layer defines the slot boundary, slot packing rules, and the message flow control. The flit overall has fields that are defined in the physical layer and are shown in this chapter; however, details are not defined in this chapter. The concept of "all Data" as defined in 68B Flit mode does not exist in 256B Flit mode.

### <span id="page-229-3"></span>4.3.2 Flit Overview

There are 2 variations of the 256B flit: Standard, and Latency-Optimized (LOpt). The mode of operation must be in sync with the physical layer. The Standard 256B flit supports either standard messages or Port Based Routing (PBR) messages where PBR messages carry additional ID space (DPID and sometimes SPID) to enable more-advanced scaling/routing solutions as described in [Chapter 3.0](#page-84-3).

*Note:* 256B flit messages are also referred to as Hierarchy Based Routing (HBR) messages, when comparing to PBR flits/messages. A message default is HBR unless explicitly stated as being PBR.

[Figure 4-41](#page-230-0) is the Standard 256B flit. The Physical Layer controls 16B of the flit in this mode where the fields are: HDR, CRC, and FEC. All other fields are defined in the link layer.

<span id="page-230-0"></span>**Figure 4-41. Standard 256B Flit**

![](_page_230_Figure_4.jpeg)

[Figure 4-42](#page-230-1) is the latency-optimized flit definition. In this definition, more bytes are allocated to the physical layer to enable less store-and-forward when the transmission is error free. In this flit, 20B are allocated to the Physical Layer, where the fields are: 12B CRC (split across 2 6B CRC codes), 6B FEC, and 2B HDR.

<span id="page-230-1"></span>**Figure 4-42. Latency-Optimized (LOpt) 256B Flit**

![](_page_230_Figure_7.jpeg)

In both flit modes, the flit message packing rules are common, with the exception of Slot 8, which in LOpt 256B flits is a 12B slot with special packing rules. These are a subset of Slot 0 packing rules. This slot format is referred to as the H Subset (HS) format.

PBR packing is a subset of HBR message packing rules. PBR messages are not supported in LOpt 256B Flits, so HS-Slot does not apply.

*Note:* Some bits of Slot 7 are split across the 128B halves of the flit, and the result is that some messages in Slot 7 cannot be consumed until the CRC for the second half of the flit is checked.

> Slot formats are defined by a 4-bit field at the beginning of each slot that carries header information, which is a departure from the 68B formats, where the 3-bit format field is within the flit header. The packing rules are constrained to a subset of messages for upstream and downstream links to match the Transaction Layer requirements. The encodings are non-overlapping between upstream and downstream except when the message(s) in the format are enabled to be sent in both directions. This is a change from the 68B flit definition where the slot format was uniquely defined for upstream and downstream.

> The packing rules for the H-slot are a strict subset of the G-slot rules. The subset relationship is defined by the 14B H-slot size where any G-slot messages that extend beyond the 14th byte are not supported in the H-slot format. HS-slot follows the same subset relationship where the cutoff size is 12B.

> For the larger PBR message packing, the messages in each slot are a subset of 256B flit message packing rules because of the larger message size required for PBR. PBR flits and messages can be fully symmetric when flowing between switches where the link is not upstream or downstream (also known as "Cross-Link" or "Inter-Switch Link" (ISL)).

> For Data and Byte-Enable Slots, a slot-format field is not explicitly included, but is instead known based on prior header messages that must be decoded. This is similar to the "all-data-flit" definition in 68B flit where expected data slots encompass the flit's entire payload.

<span id="page-231-1"></span>[Table 4-14](#page-231-0) defines the 256B G-Slots for HBR and PBR messages.

<span id="page-231-0"></span>**Table 4-14. 256B G-Slot Formats (Sheet 1 of 2)**

| Format |                     | HBR                 |             |           |                                   | PBR         |                                   |
|--------|---------------------|---------------------|-------------|-----------|-----------------------------------|-------------|-----------------------------------|
|        | SlotFmt<br>Encoding | Messages            | Downstream1 | Upstream1 | Length<br>in Bits<br>(Max<br>124) | Messages    | Length<br>in Bits<br>(Max<br>124) |
| G0     | 0000b               | H2D Req + H2D Rsp   | X           |           | 112                               | H2D Req     | 92                                |
| G1     | 0001b               | 3 H2D Rsp           | X           |           | 120                               | 2 H2D Rsp   | 96                                |
| G2     | 0010b               | D2H Req + 2 D2H Rsp |             | X         | 124                               | D2H Req     | 96                                |
| G3     | 0011b               | 4 D2H Rsp           |             | X         | 96                                | 3 D2H Rsp   | 108                               |
| G4     | 0100b               | M2S Req             | X           | D         | 100                               | M2S Req     | 120                               |
| G5     | 0101b               | 3 M2S BIRsp         | X           | D         | 120                               | 2 M2S BIRsp | 104                               |
| G6     | 0110b               | S2M BISnp + S2M NDR | D           | X         | 124                               | S2M BISnp   | 96                                |
| G7     | 0111b               | 3 S2M NDR           | D           | X         | 120                               | 2 S2M NDR   | 96                                |

**Table 4-14. 256B G-Slot Formats (Sheet 2 of 2)**

| Format | SlotFmt<br>Encoding | HBR       |             |           |                                   | PBR       |                                   |
|--------|---------------------|-----------|-------------|-----------|-----------------------------------|-----------|-----------------------------------|
|        |                     | Messages  | Downstream1 | Upstream1 | Length<br>in Bits<br>(Max<br>124) | Messages  | Length<br>in Bits<br>(Max<br>124) |
| G8     | 1000b               | RSVD      |             |           |                                   |           |                                   |
| G9     | 1001b               |           |             |           |                                   | RSVD      |                                   |
| G10    | 1010b               |           |             |           |                                   |           |                                   |
| G11    | 1011b               |           |             |           |                                   |           |                                   |
| G12    | 1100b               | 4 H2D DH  | X           |           | 112                               | 3 H2D DH  | 108                               |
| G13    | 1101b               | 4 D2H DH  |             | X         | 96                                | 3 D2H DH  | 108                               |
| G14    | 1110b               | M2S RwD   | X           | D         | 104                               | M2S RwD   | 124                               |
| G15    | 1111b               | 3 S2M DRS | D           | X         | 120                               | 2 S2M DRS | 96                                |

<span id="page-232-1"></span><sup>1.</sup> D = Supported only for Direct P2P CXL.mem-capable ports.

<span id="page-232-2"></span>[Table 4-15](#page-232-0) captures the H-Slot formats. Notice that "zero extended" is used in PBR messages sent using slot formats H4 and H14 because they do not fit in the slot. This method allows the messages to use this format provided the unsent bits are 0s. The zero-extended method can be avoided by using the G-slot format, but use is allowed for these cases to optimize link efficiency. An example PBR H14, in [Figure 4-65, "256B](#page-245-1)  [Packing: G14/H14 PBR Messages" on page 246,](#page-245-1) requires that the bits in Bytes 14 and 15 are all 0s to be able to use the format. This includes CKID[12:8], TC field, and reserved bits within those bytes. Any other field, including CKID[7:0], will be sent normally and can have supported encodings.

<span id="page-232-0"></span>**Table 4-15. 256B H-Slot Formats (Sheet 1 of 2)**

|        | SlotFmt<br>Encoding | HBR                  |             |           |                                   | PBR                        |                                   |
|--------|---------------------|----------------------|-------------|-----------|-----------------------------------|----------------------------|-----------------------------------|
| Format |                     | Messages             | Downstream1 | Upstream1 | Length<br>in Bits<br>(Max<br>108) | Messages                   | Length<br>in Bits<br>(Max<br>108) |
| H0     | 0000b               | H2D Req2             | X           |           | 72                                | H2D Req                    | 92                                |
| H1     | 0001b               | 2 H2D Rsp2           | X           |           | 80                                | 2 H2D Rsp                  | 96                                |
| H2     | 0010b               | D2H Req + 1 D2H Rsp2 |             | X         | 100                               | D2H Req                    | 96                                |
| H3     | 0011b               | 4 D2H Rsp            |             | X         | 96                                | 3 D2H Rsp                  | 108                               |
| H4     | 0100b               | M2S Req              | X           | D         | 100                               | M2S Req<br>(Zero Extended) | 108 (120)                         |
| H5     | 0101b               | 2 M2S BIRsp2         | X           | D         | 80                                | 2 M2S BIRsp                | 104                               |
| H6     | 0110b               | S2M BISnp2           | D           | X         | 84                                | S2M BISnp                  | 96                                |
| H7     | 0111b               | 2 S2M NDR2           | D           | X         | 80                                | 2 S2M NDR                  | 96                                |
| H8     | 1000b               | LLCTRL               |             |           | LLCTRL                            |                            |                                   |
| H9     | 1001b               |                      |             |           |                                   |                            |                                   |
| H10    | 1010b               | RSVD                 |             |           |                                   | RSVD                       |                                   |
| H11    | 1011b               |                      |             |           |                                   |                            |                                   |
| H12    | 1100b               | 3 H2D DH2            | X           |           | 84                                | 3 H2D DH                   | 108                               |

**Table 4-15. 256B H-Slot Formats (Sheet 2 of 2)**

| Format | SlotFmt<br>Encoding | HBR        |             |           |                                   | PBR                        |                                   |
|--------|---------------------|------------|-------------|-----------|-----------------------------------|----------------------------|-----------------------------------|
|        |                     | Messages   | Downstream1 | Upstream1 | Length<br>in Bits<br>(Max<br>108) | Messages                   | Length<br>in Bits<br>(Max<br>108) |
| H13    | 1101b               | 4 D2H DH   |             | X         | 96                                | 3 D2H DH                   | 108                               |
| H14    | 1110b               | M2S RwD    | X           | D         | 104                               | M2S RwD<br>(Zero Extended) | 108 (124)                         |
| H15    | 1111b               | 2 S2M DRS2 | D           | X         | 80                                | 2 S2M DRS                  | 96                                |

<span id="page-233-2"></span><span id="page-233-3"></span>- 1. D = Supported only for Direct P2P CXL.mem-capable ports.
<span id="page-233-1"></span>- 2. Cases in which the H-Slot is a subset of the corresponding G-slot because not all messages fit into the format.

<span id="page-233-5"></span>[Table 4-16](#page-233-0) captures the HS-Slot formats. The HS-slot format is used only in LOpt 256B flits. Notice that "zero extended" for slot formats are used in HS4 and HS14.

*Note:* PBR messages never use LOpt 256B flits, and therefore do not use the HS-Slot format.

<span id="page-233-0"></span>**Table 4-16. 256B HS-Slot Formats**

| Format | SlotFmt<br>Encoding | HBR                     |             |           |                            |  |  |  |
|--------|---------------------|-------------------------|-------------|-----------|----------------------------|--|--|--|
|        |                     | Messages                | Downstream1 | Upstream1 | Length in Bits<br>(Max 92) |  |  |  |
| HS0    | 0000b               | H2D Req                 | X           |           | 72                         |  |  |  |
| HS1    | 0001b               | 2 H2D Rsp               | X           |           | 80                         |  |  |  |
| HS2    | 0010b               | D2H Req2                |             | X         | 76                         |  |  |  |
| HS3    | 0011b               | 3 D2H Rsp2              |             | X         | 72                         |  |  |  |
| HS4    | 0100b               | M2S Req (Zero Extended) | X           | D         | 92 (100)                   |  |  |  |
| HS5    | 0101b               | 2 M2S BIRsp             | X           | D         | 80                         |  |  |  |
| HS6    | 0110b               | S2M BISnp               | D           | X         | 84                         |  |  |  |
| HS7    | 0111b               | 2 S2M NDR               | D           | X         | 80                         |  |  |  |
| HS8    | 1000b               | LLCTRL                  |             |           |                            |  |  |  |
| HS9    | 1001b               |                         |             |           |                            |  |  |  |
| HS10   | 1010b               | RSVD                    |             |           |                            |  |  |  |
| HS11   | 1011b               |                         |             |           |                            |  |  |  |
| HS12   | 1100b               | 3 H2D DH                | X           |           | 84                         |  |  |  |
| HS13   | 1101b               | 3 D2H DH2               |             | X         | 72                         |  |  |  |
| HS14   | 1110b               | M2S RwD (Zero Extended) | X           | D         | 92 (104)                   |  |  |  |
| HS15   | 1111b               | 2 S2M DRS               | D           | X         | 80                         |  |  |  |

- 1. D = Supported only for Direct P2P CXL.mem-capable ports.
<span id="page-233-4"></span>- 2. Cases in which the HS-Slot is a subset of the corresponding H-slot because not all messages fit into the format.

### <span id="page-234-0"></span>4.3.3 Slot Format Definition

The slot diagrams in this section capture the detailed bit field placement within the slot. Each Diagram is inclusive of G-slot, H-slot, and HS-slot where a subset is created such that H-slot is a subset of G-slot where messages that extend beyond the 14-byte boundary are excluded. Similarly, the HS-slot format is a subset of H-slot and G-slot where messages that extend beyond the 12-byte boundary are excluded.

This G to H to HS subset relationship is captured in [Figure 4-43,](#page-234-1) where the size of each subset is shown.

All messages within the slots are aligned to nibble (4 bit) boundary. This results in some variation in number of reserved bits to align to that boundary.

<span id="page-234-1"></span>**Figure 4-43. 256B Packing: Slot and Subset Definition**

![](_page_234_Figure_7.jpeg)

Slot diagrams in the section include abbreviations for bit field names to allow them to fit into the diagram. In the diagrams, most abbreviations are obvious, but the following abbreviation list ensures clarity:

- Bg = Bogus
- BT11 = BITag[11]
- Ch = ChunkValid
- CID3 = CacheID[3]
- CK12 = CKID[12]
- CQ0 = CQID[0]
- CQ11 = CQID[11]
- DP0 = DPID[0]
- LD0 = LD-ID[0]

- MO3 = MemOpcode[3]
- Op3 = Opcode[3]
- Poi = Poison
- RSVD = Reserved
- RV = Reserved
- SP11 = SPID[11]
- UQ11 = UQID[11]
- Val = Valid

<span id="page-235-0"></span>**Figure 4-44. 256B Packing: G0/H0/HS0 HBR Messages**

![](_page_235_Figure_11.jpeg)

<span id="page-235-1"></span>**Figure 4-45. 256B Packing: G0/H0 PBR Messages**

![](_page_235_Figure_13.jpeg)

<span id="page-236-0"></span>**Figure 4-46. 256B Packing: G1/H1/HS1 HBR Messages**

![](_page_236_Figure_3.jpeg)

<span id="page-236-1"></span>**Figure 4-47. 256B Packing: G1/H1 PBR Messages**

![](_page_236_Figure_5.jpeg)

<span id="page-237-0"></span>**Figure 4-48. 256B Packing: G2/H2/HS2 HBR Messages**

![](_page_237_Figure_3.jpeg)

<span id="page-237-1"></span>**Figure 4-49. 256B Packing: G2/H2 PBR Messages**

![](_page_237_Figure_5.jpeg)

<span id="page-238-0"></span>**Figure 4-50. 256B Packing: G3/H3/HS3 HBR Messages**

![](_page_238_Figure_3.jpeg)

<span id="page-238-1"></span>**Figure 4-51. 256B Packing: G3/H3 PBR Messages**

![](_page_238_Figure_5.jpeg)

<span id="page-239-0"></span>**Figure 4-52. 256B Packing: G4/H4/HS4 HBR Messages**

![](_page_239_Figure_3.jpeg)

<span id="page-239-1"></span>**Figure 4-53. 256B Packing: G4/H4 PBR Messages**

![](_page_239_Figure_5.jpeg)

<span id="page-240-0"></span>Figure 4-54. 256B Packing: G5/H5/HS5 HBR Messages

![](_page_240_Figure_3.jpeg)
**Figure 4-54. 7**


<span id="page-240-1"></span>Figure 4-55. 256B Packing: G5/H5 PBR Messages

**Figure 4-55. 256B Packing: G5/H5/HS5 HBR Messages**

![](_page_240_Figure_5.jpeg)

**Figure 4-56. 3**

<span id="page-241-0"></span>Figure 4-56. 256B Packing: G6/H6/HS6 HBR Messages

![](_page_241_Figure_3.jpeg)

**Figure 4-57. 256B Packing: G6/H6/HS6 HBR Messages**

<span id="page-241-1"></span>Figure 4-57. 256B Packing: G6/H6 PBR Messages

![](_page_241_Figure_5.jpeg)
**Figure 4-58. Tag[15:12]**


<span id="page-242-0"></span>Figure 4-58. 256B Packing: G7/H7/HS7 HBR Messages

**Figure 4-59. 256B Packing: G7/H7/HS7 HBR Messages**

![](_page_242_Figure_3.jpeg)

<span id="page-242-1"></span>Figure 4-59. 256B Packing: G7/H7 PBR Messages

![](_page_242_Figure_5.jpeg)

<span id="page-243-0"></span>**Figure 4-60. 256B Packing: G12/H12/HS12 HBR Messages**

![](_page_243_Figure_3.jpeg)

**Figure 4-62. 5**

<span id="page-243-1"></span>**Figure 4-61. 256B Packing: G12/H12 PBR Messages**

![](_page_243_Figure_5.jpeg)

**Figure 4-63. 256B Packing: G13/H13/HS13 HBR Messages**

<span id="page-244-0"></span>Figure 4-62. 256B Packing: G13/H13/HS13 HBR Messages

![](_page_244_Figure_3.jpeg)

<span id="page-244-1"></span>Figure 4-63. 256B Packing: G13/H13 PBR Messages

![](_page_244_Figure_5.jpeg)

<span id="page-245-0"></span>**Figure 4-64. 256B Packing: G14/H14/HS14 HBR Messages**

![](_page_245_Figure_3.jpeg)
**Figure 4-66. 6**


<span id="page-245-1"></span>**Figure 4-65. 256B Packing: G14/H14 PBR Messages**

**Figure 4-67. 256B Packing: G15/H15/HS15 HBR Messages**

![](_page_245_Figure_5.jpeg)

<span id="page-246-0"></span>Figure 4-66. 256B Packing: G15/H15/HS15 HBR Messages

![](_page_246_Figure_3.jpeg)

<span id="page-246-1"></span>Figure 4-67. 256B Packing: G15/H15 PBR Messages

![](_page_246_Figure_5.jpeg)

<span id="page-247-0"></span>**Figure 4-68. 256B Packing: Implicit Data**

![](_page_247_Figure_3.jpeg)

<span id="page-247-1"></span>**Figure 4-69. 256B Packing: Implicit Trailer RwD**

![](_page_247_Figure_5.jpeg)

<span id="page-247-2"></span>**Figure 4-70. 256B Packing: Implicit Trailer DRS**

![](_page_247_Figure_7.jpeg)

<span id="page-248-1"></span>**Figure 4-71. 256B Packing: Byte-Enable Trailer for D2H Data**

![](_page_248_Figure_3.jpeg)
**Figure 4-72.**


#### <span id="page-248-0"></span>4.3.3.1 Implicit Data Slot Decode

Data and Byte-Enable slots are implicitly known for G-slots based on prior message headers. To simplify decode of the slot format fields, SlotFmt can be used as a quick decode to know if the next 4 G-slots are data slots. Additional G-slots beyond the next 4 may also carry data depending on rollover values, the number of valid Data Headers, and BE bit within headers.

H-slots and HS-slots never carry data, so they always have an explicit 4-bit encoding defining the format.

> **IMPLEMENTATION NOTE**

The quick decode of the current slot is used to determine whether the next 4 G-slots are data slots. The decode required is different for H/HS-slot compared to G-slots. The H/HS slots comparing SlotFmt[3:2] are equal to 11b, and for G slots reduce the compare to only SlotFmt[3] equal to 1. The difference in decode requirement is because the formats H8/HS8 indicates LLCTRL message where G8 is a reserved encoding.

More generally, the optimization for quick decode can be used to limit the logic levels required to determine whether later slots (by number) are data vs. header slots.

> **IMPLEMENTATION NOTE**

With Link Layer data path of 64B wide, only 4 slots are processed per clock, which enables a simplified decode to reduce critical paths in the logic to determine whether a G-slot is a data slot vs. a header slot. All further decode is carried over from the previous clock cycle.

[Figure 4-72](#page-249-1) shows examples where a quick decode of the SlotFmt field can be used to determine which slots are implicit data slots. The Rollover column is the number of data slots carried over from previous flits. Because H-slots never carry data, their decode can proceed without knowledge of prior headers.

<span id="page-249-1"></span>Figure 4-72. Header Slot Decode Example

![](_page_249_Figure_3.jpeg)

#### <span id="page-249-0"></span>4.3.3.2 Trailer Decoder

<span id="page-249-3"></span>A trailer is defined to be included with data carrying messages when the TRP or BEP bit is set in the header. The trailer size can vary depending on the link's capability. The base functionality requires support of the Byte-Enable use case for trailers. The Extended Metadata (EMD) use of trailers is optional. Table 4-17 defines the use cases that are supported for each data-carrying channel.

<span id="page-249-2"></span>**Table 4-17.** Trailer Size and Modes Supported per Channel**

| Channel              | Trailer Use                                         | Trailer Size Max                                                              |  |
|----------------------|-----------------------------------------------------|-------------------------------------------------------------------------------|--|
| M2S RwD              | Byte-Enables (BE) and/or<br>Extended Metadata (EMD) | 96-bit if Extended Metadata is supported; otherwise, 64-bit for Byte-Enables. |  |
| S2M DRS              | Extended Metadata (EMD)                             | 96 bits max (32 bits per DRS message) when EMD is enabled; otherwise, 0-bits. |  |
| D2H Data Header (DH) | Byte-Enables                                        | 64-bit for Byte-Enables.                                                      |  |
| Other Channels       | None                                                | 0 bits                                                                        |  |

For RwD and D2H DH messages, the Trailer always follow 4 Data Slots if TRP or BEP is set for the message.

For DRS, the Trailer enables packing of up to 3 trailers together after the first 64B data transfer for Header 0 even when Header 0 does not have an associated trailer. The trailers are tightly packed for each header with TRP bit set. Figure 4-73 illustrates an example case in which the 3 DRS (G15) format is sent where the 1st and 3rd headers have TRP=1 and the 2nd has TRP=0. The trailer comes after the first data transfer (D0) and the valid trailers are tightly packed.

Note:

The "tightly packed" trailer rule is for future extensibility with larger trailers where a complete set of trailers for a multi-data header will not fit into a single slot and sparse use of TRP=1 with tightly packed trailers enables higher efficiency.

Byte # 01234567 Bit # 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 SlotFmt=15 RSVD 3 S2M DRS MemOp Val MetaValue MetaField Tag[11:4] Poi Tag[15:12] RSVD LD-ID[3:1] Tag[3:0] RSVD MemOp Val MetaValue MetaField Tag[11:4] Poi Tag[15:12] RSVD LD-ID[3:1] Tag[3:0] RSVD MemOp Val MetaValue MetaField Tag[11:4] Poi Tag[15:12] RSVD LD-ID[3:1] DevLoad Tag[3:0] LD0 RSVD **G15 TRP=1 TRP=0 TRP=1** S1 G15 256B Flit S2 D0 S3 D0 S4 D0 S5 D0 S6 Trailer S7 D1 S8 D1 S9 D1 S10 D1 S11 D2 S12 D2 S13 D2 S14 D2 CRC/ FEC S0 H7 Implicit Trailer DRS D0 Trailer0[31:0] RSVD D2 Trailer1[31:0] 4 5 6 7 Byte # 8 9 10 11 12 13 14 15 1 2 3 01234567 Bit # <Unused> Trailer2[31:0]

<span id="page-250-1"></span>**Figure 4-73. DRS Trailer Slot Decode Example**

### <span id="page-250-0"></span>4.3.4 256B Flit Packing Rules

Rules for 256B flits follow the same basic requirements as 68B flits, in terms of bit order and tightly packed rules. The tightly packed rules apply within groups of up to 4 slots together instead of across the entire flit. The groups are defined as: 0 to 3, 4 to 7, 8 to 11, and 12 to 14. Note that the final group spans only 3 slots.

• The Tx must not inject data headers in H-slots/HS-slots unless the remaining data slots to send is less than or equal to 16.

*Note:* This limits the maximum count of the remaining data to be 36 (16 + 4 (new Data headers) \* 5 (4 Data Slots + 1 Byte Enable slot) = 36):

- The MDH disable control bit is used to restrict the number of valid data header bits to one per slot
- If a Data Header slot format is used (G/H/HS 12 to 15) the first message must have the valid bit set
- Tightly packed rules for valid messages in a group are applied to slot formats that support zero extended message packing. The result is that a transmit packing must not use a format of HS/H type message with Valid=0 where it is unable to pack because of non-zero bits in the zero-extended portion of the message followed by

Valid=1 for same message type in G format (e.g., it would always be illegal to use HS4 with valid=0 for M2S Req followed by G4 with Valid=1 for M2S Req in the same group).

The maximum message rules are applicable on a rolling 128B group in which the groups are A="Slot 0 to 3", B="Slot 4 to 7", C="Slot 8 to 11", D="Slot 12 to 14". Extending these rules to 128B boundary enables the 256B flit slot formats to be fully utilized. The 256B flit slots often have more messages per slot than the legacy 68B flit message rate would allow. Extending to 128B enables the use of these high message count slots while not increasing the message rate per bandwidth.

The definition of rolling is such that the groups combine into 128B rolling groups: AB (Slot 0 to 7), BC (Slot 4 to 11), CD (Slot 8 to 14), and DA (Slot 12 to 14 in current flit and Slot 0 to 3 in the following flit). The maximum message rates apply to each group. The LOpt 256B flit creates one modification to this rule such that Slot 7 is included in groups B and C: B="Slot 4 to 7" and C="Slot 7 to 11". Sub-Group C has 5 slots with this change. Note that this special case is applicable only to the maximum message rate requirement where CD group considers Slot 7 to 14 instead of Slot 8 to 14.

The maximum message rate per 128B group is defined in [Table 4-18,](#page-251-0) and the 68B flit message rate is included for comparison.

*Note:* The term "128B group" is looking at the 128B grouping boundaries of the 256B flit. The actual number of bytes in the combined slots does vary depending on where the

alignment is within the 256B flit which has other overhead like CRC, FEC, 2B Hdr.

*Note:* The maximum message count was selected based on a worst-case workload requirement for steady-state message requirement in conjunction with the packing rules to achieve the most-efficient operating point. In some cases, this is 2x from the 68B message rate, which is what would be expected, but that is not true in all cases.

<span id="page-251-0"></span>**Table 4-18. 128B Group Maximum Message Rates**

| Message Type         | Maximum Message Count<br>per 128B Group | Maximum Message Count<br>for Each 68B Flit |
|----------------------|-----------------------------------------|--------------------------------------------|
| D2H Req              | 4                                       | 4                                          |
| D2H Rsp              | 4                                       | 2                                          |
| D2H Data Header (DH) | 4                                       | 4                                          |
| S2M BISnp            | 2                                       | N/A                                        |
| S2M NDR              | 6                                       | 2                                          |
| S2M DRS-DH           | 3                                       | 3                                          |
| H2D Req              | 2                                       | 2                                          |
| H2D Rsp              | 6                                       | 4                                          |
| H2D Data Header (DH) | 4                                       | 4                                          |
| M2S Req              | 4                                       | 2                                          |
| M2S RwD-DH           | 2                                       | 1                                          |
| M2S BIRsp            | 3                                       | N/A                                        |

Other 68B rules that do not apply to 256B flits:

- MDH rule that requires >1 valid header per MDH. In 256B slots, only one format is provided for packing each message type, so this rule is not applicable.
- Rules related to BE do not apply because they are handled with a separate message header bit instead of a flit header bit, and because there are no special constraints placed on the number of messages when the TRP or BEP bit is set.
- 32B transfer rules don't apply because only 64B transfers are supported.

> **IMPLEMENTATION NOTE**

Packing choices between H-slot and G-slot can have a direct impact on efficiency in many traffic patterns. Efficiency may be improved if messages that can fully utilize an H-slot (or HS-slot) are prioritized for those slots compared to messages that can better utilize a G-slot.

An example analyzed CXL.mem traffic pattern that sends steady state downstream traffic of MemRd, MemWr, and BIRsp. In this example, MemRd and MemWr can fully utilize an H-slot and do not see a benefit from being packed into a G-slot. The BIRsp packing allows more messages to fit into G-slot (3) compared to an H-slot (2), so prioritizing it for G-slot allows for improvement. In this example, we can see approximately 1.5% bandwidth improvement from prioritizing BIRsp to G-slots as compared to a simple weighted round-robin arbitration.

Prioritizing must be carefully handled to ensure that fairness is provided between each message class.

### <span id="page-253-0"></span>4.3.5 Credit Return

<span id="page-253-2"></span>[Table 4-19](#page-253-1) defines the 2-byte credit return encoding in the 256B flit.

<span id="page-253-1"></span>**Table 4-19. Credit Returned Encoding (Sheet 1 of 3)**

| Field    | Encoding<br>(hex) | Definition                                                                               |             |             |           |              |  |
|----------|-------------------|------------------------------------------------------------------------------------------|-------------|-------------|-----------|--------------|--|
|          |                   | Protocol                                                                                 | Channel     | Downstream1 | Upstream1 | Credit Count |  |
|          | 00h               | No credit return                                                                         | 0           |             |           |              |  |
|          | 01h               | No Credit Return and the current flit is an Empty flit as<br>defined in Section 4.3.8.1. | 0           |             |           |              |  |
|          | 02h-03h           | Reserved                                                                                 |             |             |           |              |  |
|          | 04h               |                                                                                          |             | X           |           | 1            |  |
|          | 05h               |                                                                                          |             |             |           | 4            |  |
|          | 06h               |                                                                                          | H2D Request |             |           | 8            |  |
|          | 07h               |                                                                                          |             |             |           | 12           |  |
|          | 08h               |                                                                                          |             |             |           | 16           |  |
|          | 09h               | Cache                                                                                    |             |             | X         | 1            |  |
|          | 0Ah               |                                                                                          |             |             |           | 4            |  |
|          | 0Bh               |                                                                                          | D2H Request |             |           | 8            |  |
|          | 0Ch               |                                                                                          |             |             |           | 12           |  |
| CRD[4:0] | 0Dh               |                                                                                          |             |             |           | 16           |  |
|          | 0Eh-13h           | Reserved                                                                                 |             |             |           |              |  |
|          | 14h               | Memory                                                                                   | M2S Request | X           | D         | 1            |  |
|          | 15h               |                                                                                          |             |             |           | 4            |  |
|          | 16h               |                                                                                          |             |             |           | 8            |  |
|          | 17h               |                                                                                          |             |             |           | 12           |  |
|          | 18h               |                                                                                          |             |             |           | 16           |  |
|          | 19h               |                                                                                          | S2M BISnp   | D           | X         | 1            |  |
|          | 1Ah               |                                                                                          |             |             |           | 4            |  |
|          | 1Bh               |                                                                                          |             |             |           | 8            |  |
|          | 1Ch               |                                                                                          |             |             |           | 12           |  |
|          | 1Dh               |                                                                                          |             |             |           | 16           |  |
|          | 1Eh-1Fh           | Reserved                                                                                 |             |             |           |              |  |

**Table 4-19. Credit Returned Encoding (Sheet 2 of 3)**

| Field    | Encoding<br>(hex) | Definition       |          |             |           |              |  |
|----------|-------------------|------------------|----------|-------------|-----------|--------------|--|
|          |                   | Protocol         | Channel  | Downstream1 | Upstream1 | Credit Count |  |
|          | 00h               | No credit return | 0        |             |           |              |  |
|          | 01h-03h           | Reserved         |          |             |           |              |  |
|          | 04h               |                  |          | X           |           | 1            |  |
|          | 05h               |                  |          |             |           | 4            |  |
|          | 06h               |                  | H2D Data |             |           | 8            |  |
|          | 07h               |                  |          |             |           | 12           |  |
|          | 08h               |                  |          |             |           | 16           |  |
|          | 09h               | Cache            | D2H Data |             |           | 1            |  |
|          | 0Ah               |                  |          |             | X         | 4            |  |
|          | 0Bh               |                  |          |             |           | 8            |  |
|          | 0Ch               |                  |          |             |           | 12           |  |
|          | 0Dh               |                  |          |             |           | 16           |  |
| CRD[9:5] | 0Eh-13h           | Reserved         |          |             |           |              |  |
|          | 14h               | Memory           | M2S RwD  | X           | D         | 1            |  |
|          | 15h               |                  |          |             |           | 4            |  |
|          | 16h               |                  |          |             |           | 8            |  |
|          | 17h               |                  |          |             |           | 12           |  |
|          | 18h               |                  |          |             |           | 16           |  |
|          | 19h               |                  | S2M DRS  | D           | X         | 1            |  |
|          | 1Ah               |                  |          |             |           | 4            |  |
|          | 1Bh               |                  |          |             |           | 8            |  |
|          | 1Ch               |                  |          |             |           | 12           |  |
|          | 1Dh               |                  |          |             |           | 16           |  |
|          | 1Eh-1Fh           | Reserved         |          |             |           |              |  |

**Table 4-19. Credit Returned Encoding (Sheet 3 of 3)**

| Field      | Encoding<br>(hex) | Definition            |           |             |           |              |  |
|------------|-------------------|-----------------------|-----------|-------------|-----------|--------------|--|
|            |                   | Protocol              | Channel   | Downstream1 | Upstream1 | Credit Count |  |
|            | 00h               | No credit return<br>0 |           |             |           |              |  |
|            | 01h-03h           | Reserved              |           |             |           |              |  |
|            | 04h               |                       |           | X           |           | 1            |  |
|            | 05h               |                       |           |             |           | 4            |  |
|            | 06h               |                       | H2D Rsp   |             |           | 8            |  |
|            | 07h               |                       |           |             |           | 12           |  |
|            | 08h               |                       |           |             |           | 16           |  |
|            | 09h               | Cache                 |           |             |           | 1            |  |
|            | 0Ah               |                       |           |             | X         | 4            |  |
|            | 0Bh               |                       | D2H Rsp   |             |           | 8            |  |
|            | 0Ch               |                       |           |             |           | 12           |  |
|            | 0Dh               |                       |           |             |           | 16           |  |
| CRD[14:10] | 0Eh-13h           | Reserved              |           |             |           |              |  |
|            | 14h               | Memory                | M2S BIRsp | X           | D         | 1            |  |
|            | 15h               |                       |           |             |           | 4            |  |
|            | 16h               |                       |           |             |           | 8            |  |
|            | 17h               |                       |           |             |           | 12           |  |
|            | 18h               |                       |           |             |           | 16           |  |
|            | 19h               |                       |           | D           | X         | 1            |  |
|            | 1Ah               |                       |           |             |           | 4            |  |
|            | 1Bh               |                       | S2M NDR   |             |           | 8            |  |
|            | 1Ch               |                       |           |             |           | 12           |  |
|            | 1Dh               |                       |           |             |           | 16           |  |
|            | 1Eh-1Fh           | Reserved              |           |             |           |              |  |
| CRD[15]    | Reserved          |                       |           |             |           |              |  |

<span id="page-255-1"></span><sup>1.</sup> D = Credit channel mapping is applicable only on a Direct P2P CXL.mem link between a device and the switch Downstream Port to which it is attached.

### <span id="page-255-0"></span>4.3.6 Link Layer Control Messages

In 256B Flit mode, control messages are encoded using the H8 format and sometimes using the HS8 format. [Figure 4-74](#page-257-2) captures the 256B packing for LLCTRL messages. H8 provides 108 bits to be used to encode the control message after accounting for 4-bit slot format encoding. 8 bits are used to encode LLCTRL/SubType, and 4 bits are kept as reserved, with a 96-bit payload. For HS8, it is limited to 2 bytes less, which cuts the available payload to 80 bits. [Table 4-20](#page-256-0) captures the defined control messages. In almost all cases, the remaining slots after the control message are considered to be reserved (i.e., cleared to all 0s) and do not carry any protocol information. The exception case is IDE.MAC, which allows for protocol messages in the other slots within the flit. For messages that are injected in the HS slot, the slots prior to the HS slot may carry protocol information but the slots after the HS slot are reserved.

<span id="page-256-1"></span><span id="page-256-0"></span>**Table 4-20.** 256B Flit Mode Control Message Details

| Flit<br>Type                  | LLCTRL                                    | SubType   | SubType<br>Description                                                                                                                                                                           | Payload                                                            | Payload Description                                                                                                                                                                                                                                                  | Remaining<br>Slots are<br>Reserved? <sup>1</sup> |  |
|-------------------------------|-------------------------------------------|-----------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------|--|
|                               | 0010b                                     | 0000b     | IDE.Idle                                                                                                                                                                                         | 95:0                                                               | Payload RSVD Message sent as part of IDE flows to pad sequences with idle flits. See Chapter 11.0 for details on the use of this message.                                                                                                                            |                                                  |  |
|                               |                                           | 0001b     | IDE.Start                                                                                                                                                                                        | IDE.Start 95:0 Payload RSVD Message sent to begin flit encryption. |                                                                                                                                                                                                                                                                      | Yes                                              |  |
| IDE <sup>2</sup>              |                                           | 0010b     | IDE.TMAC                                                                                                                                                                                         | 95:0                                                               | MAC Field uses all 96 bits of payload. Truncated MAC Message sent to complete a MAC epoch early. Used only when no protocol messages exist to send.                                                                                                                  | s                                                |  |
|                               |                                           | 0011b     | IDE.MAC  95:0  MAC Field uses all 96 bits of payload.  This encoding is the standard MAC used at the natural end of the MAC epoch and is sent with other protocol slots encoded within the flit. |                                                                    | No                                                                                                                                                                                                                                                                   |                                                  |  |
|                               |                                           | 0100b     | IDE.Stop                                                                                                                                                                                         | 95:0                                                               | Payload RSVD.  Message used to disable IDE.  See Chapter 11.0 for details on the use of this message.                                                                                                                                                                | Yes                                              |  |
|                               |                                           | Others    | RSVD                                                                                                                                                                                             | 95:0                                                               | RSVD                                                                                                                                                                                                                                                                 |                                                  |  |
|                               | 0011b                                     | 0000b     | Viral                                                                                                                                                                                            | 15:0                                                               | Viral LD-ID Vector[15:0]: Included for MLD links to indicate which LD-ID is impacted by viral. Bit 0 of the vector encodes LD-ID=0, bit 1 is LD-ID=1, etc. Field is treated as Reserved for ports that do not support LD-ID.                                         |                                                  |  |
|                               |                                           |           |                                                                                                                                                                                                  | 79:16                                                              | S RSVD                                                                                                                                                                                                                                                               |                                                  |  |
|                               |                                           |           |                                                                                                                                                                                                  | 95:80                                                              | RSVD (these bits do not exist in HS format).                                                                                                                                                                                                                         | 1                                                |  |
| In-band<br>Error <sup>3</sup> |                                           |           | Poison                                                                                                                                                                                           | 3:0                                                                | Poison Message Offset is the encoding of which of the active or upcoming messages will have poison applied. There can be up to 8 active Data carrying messages and up to 4 new data carrying messages where the poison can be applied.                               | Yes                                              |  |
| . 2.101                       |                                           |           |                                                                                                                                                                                                  |                                                                    | <ul> <li>Oh = Poison the currently active data message</li> <li>1h = Poison the message 1 after the current data message</li> <li></li> <li>7h = Poison the message 7 after the current data message</li> <li>See Section 4.3.6.3 for additional details.</li> </ul> |                                                  |  |
|                               |                                           |           |                                                                                                                                                                                                  | 79:4                                                               | RSVD                                                                                                                                                                                                                                                                 | -                                                |  |
|                               |                                           |           |                                                                                                                                                                                                  | 95:80                                                              | RSVD (these bits do not exist in HS format).                                                                                                                                                                                                                         |                                                  |  |
| L                             |                                           | Others    | RSVD                                                                                                                                                                                             | 95:0                                                               | RSVD                                                                                                                                                                                                                                                                 |                                                  |  |
| INIT <sup>2</sup>             | 1100b                                     | 1000b INI |                                                                                                                                                                                                  | 0                                                                  | Direct P2P CXL.mem-capable port. Credits for the channels enabled in this feature are not returned unless both sides support it.                                                                                                                                     |                                                  |  |
|                               |                                           |           |                                                                                                                                                                                                  | 95:1                                                               | RSVD                                                                                                                                                                                                                                                                 | Yes                                              |  |
|                               |                                           | Others    | RSVD                                                                                                                                                                                             | 95:0                                                               | RSVD                                                                                                                                                                                                                                                                 |                                                  |  |
**Figure 4-75.**

| Reserved                      | eserved Others <all> RSVD 95:0 RSVD</all> |           |                                                                                                                                                                                                  |                                                                    |                                                                                                                                                                                                                                                                      |                                                  |  |

If yes, all the slots in the current flit after this message are Reserved, If no, the slots after this may carry protocol messages (header or data).
 Supported only in H-slot.
 Supported in either H-slot or HS-slot.

<span id="page-257-2"></span>**Figure 4-74. 256B Packing: H8/HS8 Link Layer Control Message Slot Format**

![](_page_257_Figure_3.jpeg)

#### <span id="page-257-0"></span>4.3.6.1 Link Layer Initialization

After initial link training (from Link Down), the link layer must send and receive the INIT.Param flit before beginning normal operation. After reaching normal operation, the Link Layer will start by returning all possible credits using the standard credit return mechanism. Normal operation is also required before sending other control messages (IDE, In-band Error).

#### <span id="page-257-1"></span>4.3.6.2 Viral Injection and Containment

<span id="page-257-3"></span>The Viral control flit is injected as soon as possible after the viral condition is observed. For cases in which the error that triggers Viral can impact the current flit, the link layer should signal to the physical layer to stop the currently partially sent CXL.cachemem flit (Flit 0) by injection of a CRC/FEC corruption that ensures a retry condition (note that this does not directly impact CXL.io flits or flits that are being replayed from the Physical Layer retry buffer). Then the Logical Physical Layer will also remove that flit (flit 0) from the retry buffer and replace it with the Viral control flit (flit 1) that must be sent immediately by the link layer. The Link Layer must also resend the flit that was corrupted (flit 0) after the viral flit. [Figure 4-75](#page-258-1) captures an example of a Link Layer to Logical Physical Layer (LogPhy) with a half-flit interface where CRC is corrupted and Viral is injected. At Cycle "x3", it is signaled to corrupt the current flit (FlitA). At cycle "x4", the CRC(bad) is indicated and the link layer starts sending the Viral control. In Cycle "x5", the retry buffer pointer (WrPtr) is stepped back to ensure the FlitA is removed from the retry buffer and then replaced with the Viral flit sent from the link layer. At Cycle "x6", the CTRL-Viral flit is also sent with corrupted CRC to ensure the full retry flow (disallowing the single flit retry). Also starting at cycle "x6", FlitA is resent from the link layer and forwarded on normally through the LogPhy and retry buffer. FlitA is identical to the flit started in Cycle "x2".

With link IDE enabled this flow works the same and FlitA is retransmitted with the same encryption mask and without altering the integrity state. The control message is not included in link IDE and thus does not impact the IDE requirements.

<span id="page-258-1"></span>Figure 4-75. Viral Error Message Injection Standard 256B Flit

![](_page_258_Figure_3.jpeg)

The Error signaling with CRC corruption flow requires special handling for LOpt flits. If the link layer is in the first 128B phase of the flit, the flow is identical to Standard Flit mode. However, if the link layer is in the second phase of the 128B flit (when the first 128B was committed), then the flit corruption is guaranteed only on the second half, but the Physical Layer will remove the entire flit from the retry buffer. The link layer will send the first 128B identically to what was sent before, and then the link layer will inject the Viral control message in Slot 8 (HS-format) and Slots 9-14 are considered RSVD and normal operation continues in the next flit. Any data slots and other message encodings are continued in the next flit. Figure 4-76 captures the unique case for the LOpt flit. The difference from the standard 256B flit is in three areas of this flow. First at Cycle "x4", the link layer resends FlitA-0 because this half of the flit may have already been consumed. Then at Cycle "x5", in the second-half of that flit, the link layer injects the control message for Viral (after the final portion of Slot 7). At Cycle "x6", the second half of the original flit (starting with Slot 8) is repacked in the first half of FlitB following the standard packing rules.

This flow cannot be supported with link IDE, thus any error containment must either be detected sufficiently early to corrupt CRC in the first half of the flit or must be injected in the second half without corrupting the CRC.

<span id="page-258-2"></span>**Figure 4-76. Viral Error Message Injection LOpt 256B Flit** 

![](_page_258_Figure_7.jpeg)

#### <span id="page-258-0"></span>4.3.6.3 Late Poison

<span id="page-258-3"></span>Poison can be injected at a point after the header was sent by injecting an Error Control message with the Poison sub-type. The message includes a payload encoding that indicates the data message offset at which the poison applies. It is possible that any one of up to 8 active messages can be targeted. The encoding is an offset that is relative to the data that is yet to be sent, including the currently active data transmission. The poison applies to the entire message payload, just as it does when poison is included in the message header.

If a message is currently active, but not all data slots have been sent, the offset value of zero applies to that message. If a receiver implementation uses "wormhole switching" techniques, where data is forwarded through the on-die fabric before all the data has arrived, then it is possible that data already sent may be consumed. In this case, the only guarantee is that the poison is applied to the remaining data after the poison control message. The following are examples of how this would apply in specific cases.

**Example 1:**

- Flit 1 1st 3 slots of data Message A in Slots 12 to 14.
- Flit 2 In-band error poison message in Slot 0 with a poison message offset value of 0.
- Flit 3 4th slot of data Message A in Slot 1 and data Message B in Slots 2 to 5.
- The poison control message applies to Message A, but is only guaranteed to be applied to the final data slot of that message. But it may also be applied to the entire message.

**Example 2:**

- Flit 1 4 slots of data Message A in Slots 11 to 14 where the message header has Byte-Enables Present (BEP) or Trailer Present (TRP) bit set.
- Flit 2 In-band error poison message in Slot 0 with a poison message offset value of 0.
- Flit 3 The Trailer (e.g., Byte enables) for data Message A in Slot 1 and data Message B in Slots 2 to 5.
- The poison control message applies to Message A, but is not guaranteed to be applied to any of the data because it was already sent. Note that the use of Trailer in this example could be any supported trailer (e.g., Extended Meta Data and/or Byte-Enables).

To inject poison on data that is scheduled to be sent in the current flit, and no H-slot/ HS-slot exists to interrupt the data transmission, the same CRC corruption flows as described in [Section 4.3.6.2, "Viral Injection and Containment,"](#page-257-1) are used.

#### <span id="page-259-0"></span>4.3.6.4 Link Integrity and Data Encryption (IDE)

For the IDE flow, see [Chapter 11.0](#page-891-2).

### <span id="page-259-1"></span>4.3.7 Credit Return Forcing

To avoid starvation, credit return rules ensure that Credits are sent even when there are no protocol messages pending. In 68B Flit mode, this uses a special control message called LLCRD (its algorithm is described in [Section 4.2.8.2\)](#page-220-0). For 256B Flit mode, the same underlying algorithm for forcing is used, but with the following changes:

- Ack forcing is not applicable with 256B flit.
- With 256B flits, CRD is part of standard flit definition, so no special control message is required.
- There is a packing method described in [Section 4.3.8](#page-259-2). When implementing this algorithm, the end of the flit is tagged as empty if no valid messages or Credit return is included. With this flit packing method, the flit should return a nonzero credit value only if there are other valid messages sent unless the credit forcing algorithm has triggered.
- No requirement to prioritize protocol messages vs. CRD because they are both part of 256B flits.

### <span id="page-259-2"></span>4.3.8 Latency Optimizations

To get the best latency characteristics, the 256B flit is expected to be sent with a link layer implementing 64B or 128B pipeline and the Latency-Optimized flit (which is optional). The basic reasoning for these features is self-evident.

Additional latency optimization is possible sending idle slot scheduling of flits to the ARB/MUX which avoids needing to wait for the next start of flit alignment. There are trade-offs between CXL.io vs. empty slots being scheduled, so overall bandwidth should be considered.

> **IMPLEMENTATION NOTE**

A case to consider for idle slot scheduling is with a Link Layer pipeline of 64B in which idle slots allow late-arriving messages to be packed later in the flit. By doing this, the Transmitter can avoid stalls by starting the flit with empty slots. An example case of this is with a x4 port in which a message shows and just misses the first 64B of the flit. In this case, it is necessary to wait an additional 192B before sending the message because the ARB/MUX is injecting an empty flit or a flit from CXL.io. In this example, the observed additional latency in x4 is 6 ns (192 bytes/x4 \* 8 bits/byte / 64 GT/s).

#### <span id="page-260-0"></span>4.3.8.1 Empty Flit

As part of the latency optimizations described in this chapter, the Link Layer needs to include a way to indicate that the current flit does not have messages or CRD information. The definition of Empty in this context is that the entire flit can be dropped without side effects in the Link Layer:

- No Data Slots are sent
- No Valid bits are set in any protocol slots
- No control message is sent
- No Credits are returned in the CRD field

A special encoding of the CRD field provides this such that CRD[4:0] = 01h as captured in [Table 4-19.](#page-253-1)

When IDE is enabled, the Empty Encoding shall not used as all protocol flits are required to be fully processed.
