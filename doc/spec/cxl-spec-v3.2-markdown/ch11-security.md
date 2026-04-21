# <span id="page-891-0"></span>11.0 CXL Security

## <span id="page-891-1"></span>11.1 CXL IDE Overview

<span id="page-891-2"></span>CXL Integrity and Data Encryption (CXL IDE) defines mechanisms for providing Confidentiality, Integrity, and Replay protection for data that traverses the CXL link. The cryptographic schemes are aligned with current industry best practices. CXL IDE supports a variety of usage models while providing for broad interoperability. CXL IDE can be used to secure traffic within a Trusted Execution Environment (TEE) that is composed of multiple components (see [Section 11.5\)](#page-931-0).

This chapter focuses on the changes for CXL.cache and CXL.mem traffic that traverses the link, and updates and constraints to PCIe\* Base Specification that govern CXL.io traffic.

- CXL.io IDE definition including CXL.io IDE key establishment is based on PCIe IDE. Differences and constraints for CXL.io usage are identified in [Section 11.2](#page-893-0).
- CXL.cachemem IDE may use the CXL.io-based mechanisms for discovery, negotiation, device attestation, and key negotiation using a standard mechanism as described in [Section 11.4.](#page-917-2)

In this specification, the term CXL IDE is used to refer to the scheme that protects CXL.io, CXL.cache, and CXL.mem traffic. The term CXL.cachemem IDE is used to refer to the protections associated with CXL.cache and CXL.mem traffic.

**IMPLEMENTATION NOTE: SECURITY MODEL**

**Assets**

Assets that are in scope are as follows:

• Transactions (data + metadata communicated) between the two sides of the physical link. Only the definition for providing integrity, replay protection and encryption/decryption of traffic between the ports is included in this specification.

**Notes:**

- This threat model does not cover the security exposure due to inadequate Device implementation.
- Agents that are on each side of the physical link are within the trust boundary of the respective devices/hardware blocks in which they reside. These agents will need to provide implementation-specific mechanisms to protect data internal to the device and any external connections over which such data can be sent by the device. Mechanisms for such protection are beyond the scope of this definition.
- Symmetric cryptographic keys are used to provide confidentiality, integrity, and replay protection of data in transit between physically connected CXL ports. This specification does not define mechanisms for protecting these keys inside the host and the device.
- Certificates and asymmetric keys that are used for device authentication and key exchange are beyond the scope of this specification. The device attestation and key exchange mechanism determine the security model for those assets.

**TCB**

The TCB consists of the following:

- Functional blocks on each side of the link that implement the link encryption and integrity.
- Agents that are used to configure the cryptographic engines in the functional blocks on each side of link. For example, trusted firmware/software agent and/or security agent hardware and firmware that implement key exchange protocol or facilitate programming of the keys.
- Other hardware blocks in the device that may have direct or indirect access to the assets, including those that perform operations such as reset, debug, and link power management.

### Adversaries and Threats

- Threats from physical attacks on links, including cases where an adversary can examine data intended to be confidential, modify data or protocol metadata, record and replay recorded transactions, reorder and/or delete data flits, inject transactions including requests/data or nondata responses, using lab equipment, purpose-built interposers, and/or malicious Extension Devices.
- Threats arising from physical replacement of a trusted device with an untrusted device, and/or removal of a trusted device and accessing the trusted device with a system that is under an adversary's control.
- CXL.cachemem IDE provides point-to-point protection. Any switches present in the path between the Host and the Endpoint, or between two Endpoints, must support this specification. In these cases, such switches will be in the TCB.

Denial of service attacks are beyond the scope of this specification.

## <span id="page-893-0"></span>11.2 CXL.io IDE

CXL.io IDE follows the PCIe IDE definition. This section covers the notable constraints and differences between the CXL.io IDE definition and the PCIe IDE definition.

<span id="page-893-2"></span>**Table 11-1. Mapping of PCIe IDE to CXL.io**

| PCIe IDE Definition                                 | CXL.io Support | Notes                                                                                                                                                                           |  |  |  |  |  |  |
|-----------------------------------------------------|----------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--|--|--|--|--|--|
| Link IDE stream                                     | Supported      |                                                                                                                                                                                 |  |  |  |  |  |  |
| Selective IDE stream                                | Supported      | Selective IDE stream applies only to CXL.io.                                                                                                                                    |  |  |  |  |  |  |
| Aggregation                                         | Supported      | PCIe-defined aggregation levels apply only to<br>CXL.io traffic.                                                                                                                |  |  |  |  |  |  |
| Switches with flow-through selective IDE<br>streams | Supported      | CXL switches may support CXL.io link IDE streams.<br>CXL Switches may either operate as a boundary for<br>selective IDE streams or forward the IDE streams<br>toward Endpoints. |  |  |  |  |  |  |
| PCRC mechanism                                      | Supported      | PCRC mechanism may be optionally enabled for the<br>CXL.io ports.                                                                                                               |  |  |  |  |  |  |

One of the PCIe IDE reserved sub-stream encodings (1000b) is assigned for CXL.cachemem usage.

## <span id="page-893-1"></span>11.3 CXL.cachemem IDE

All protocol-level retryable flits are encrypted and integrity protected.

When operating in 68B Flit mode:

- Link Layer control flits and flit CRC are not encrypted or integrity protected. There is no confidentiality or integrity on these flits.
- Link CRC shall be calculated on encrypted flits. Link retries occur first and only flits that pass Link CRC will be decrypted and then integrity checked.

When operating in 256B Flit mode:

- Link Layer control information, flit header, and flit CRC/FEC is not encrypted or integrity protected. There is no confidentiality protection, integrity protection, or replay protection for this content.
- Link CRC shall be calculated on encrypted flits. Link retries occur first and only flits that pass Link CRC will be decrypted and then integrity checked.

Any integrity check failures shall result in all future secure traffic being dropped.

Multi-Data Header capability must be supported. This allows packing of multiple (up to 4) data headers into a single slot, followed immediately by 16 slots of all-data.

IDE will operate on a flit granularity for CXL.cache and CXL.mem protocols. IDE makes use of the Advanced Encryption Standard-Galois Counter Mode Advanced Encryption and Advanced Decryption Functions (referred to herein as AES-GCM), as defined in NIST\* Special Publication 800-38D. AES-GCM with a 256-bit key size shall be used for confidentiality protection, integrity protection, and replay protection. The AES-GCM Functions take three inputs:

- additional authentication data (AAD; denoted as *A*)
- plaintext (denoted as *P*)
- initialization vector (denoted as *IV*)

Key refresh without any data loss must be supported. There are a number of scenarios where the keys need to be refreshed. Some examples include:

- An accelerator device that is migrated from one VM (or process) to a different VM (or process).
- Crypto considerations (concerns about key wear-out) for long-running devices or devices that are part of the platform.

Key refresh is not expected to occur frequently. It is acceptable to take a latency/ bandwidth hit; however, there must not be any data loss.

Encrypted PCRC mechanism is supported to provide robustness against hard and soft faults that are internal to the encryption and decryption engines. Encrypted PCRC integrates into the standard MAC check mechanism, does not consume incremental link bandwidth, and can be implemented without adding significant incremental latency. PCRC is mandatory for CXL.cachemem IDE and is enabled by default.

### <span id="page-894-0"></span>11.3.1 CXL.cachemem IDE Architecture in 68B Flit Mode

IDE shall operate on a flit granularity for CXL.cachemem protocols. IDE makes use of the AES-GCM algorithm, and AES-GCM takes three inputs – *A*, *P*, and *IV* – as described earlier in [Section 11.3](#page-893-1).

In the case of CXL.cachemem protocol header flits, the 32 bits of the flit header that are part of Slot 0 map to *A* – it is not encrypted, but it is integrity protected. The remainder of the Slot 0/1/2/3 contents maps to *P*, which is encrypted and integrity protected (see handling of MAC slot below). CXL.cachemem protocol also supports ADF. In the case of an ADF, all 4 slots in the flit map to *P*.

The link CRC is not encrypted or integrity protected. The CRC is calculated on the flit content after the flit has been encrypted.

As with other protocol flits, IDE flits shall be covered by link layer mechanisms for detecting and correcting errors. This process shall operate on flits after the flits are cryptographically processed by the transmitter and before the flits are submitted for cryptographic processing by the receiver.

AES-GCM is applied to an aggregation of multiple flits referred to as a MAC epoch. The number of flits in the aggregation is determined by the Aggregation Flit Count (see [Section 11.3.5](#page-905-1) for details). If PCRC (see [Section 11.3.3\)](#page-903-0) is enabled in the CXL IDE Control register (see [Section 8.2.4.22.2\)](#page-578-0), the 32 bits of PCRC shall be appended to the end of the aggregated flit content to contribute to the final *P* value that is integrity protected. However, the 32 bits of PCRC are not transmitted across the link. [Figure 11-1](#page-894-1) shows the mapping of the flit contents into *A* and *P* for the case of aggregation of MAC across 5 flits.

<span id="page-894-1"></span>**Figure 11-1. Mapping of Flit Contents to A and P for AES-GCM MAC Aggregation**

![](_page_894_Figure_13.jpeg)

![](_page_894_Figure_14.jpeg)

The Message Authentication Code (MAC), also referred to as the authentication tag in NIST Special Publication 800-38D, shall be 96 bits. The MAC must be transmitted in a Slot 0 header of type H6 (see [Figure 4-12](#page-203-3)). Unlike other Slot 0 headers, the MAC itself is neither encrypted nor integrity protected. [Figure 11-2](#page-895-0) shows the mapping of flit contents to *A* and *P* for the case of aggregation of MAC across 5 flits with one of the flits carrying a MAC.

<span id="page-895-0"></span>**Figure 11-2. 68B Flit: CXL.cachemem IDE Showing Aggregation across 5 Flits where One Flit Contains MAC Header in Slot 0**

![](_page_895_Figure_4.jpeg)

[Figure 11-3](#page-896-0) provides a more-detailed view of the 5-flit MAC epoch example. Flit0 shown on the top is the first flit to be transmitted in this MAC epoch. The figure shows the header fields that are only integrity protected, and plaintext content that is encrypted and integrity protected. Flit0 plaintext0 byte0 is the first byte of the plaintext. Flit1 plaintext0 byte0 shall immediately follow flit0 plaintext3 byte15.

<span id="page-896-0"></span>**Figure 11-3. 68B Flit: More-detailed View of a 5-Flit MAC Epoch Example**

![](_page_896_Figure_3.jpeg)

[Figure 11-4](#page-896-1) shows the mapping of the header bytes to AES-GCM AAD (*A*) for the example in [Figure 11-3](#page-896-0).

<span id="page-896-1"></span>**Figure 11-4. 68B Flit: Mapping of AAD Bytes for the Example Shown in [Figure 11-3](#page-896-0)**

![](_page_896_Figure_6.jpeg)

### <span id="page-897-0"></span>11.3.2 CXL.cachemem IDE Architecture in 256B Flit Mode

If the header slot is used for sending control messages other than IDE.MAC, the entire flit shall not carry any protocol traffic. This applies for other usages of IDE type (IDE.TMAC, IDE.Start, and IDE.Idle), In-band Error, and INIT.

The receiver uses 4 bits of the header slot that encode the slot type to determine whether the slot contains control or protocol information. If the header slot is carrying protocol information, then 4 bits of the header slot that encode the slot type will map to AES-GCM input *A*. Although the slot type will not be encrypted, it is integrity protected. If the header slot is carrying control information, then the entire slot is neither encrypted nor integrity protected.

In case the header slot is carrying protocol information, then the plaintext (*P*) starts at bit 20. To simplify implementation and align to the AES block size of 128 bits, 20 bits of 0s shall be padded in front of the header slot content and the padded 128 bits of information shall be mapped to AES-GCM input *P*.

- The padded header slot will be used when calculating PCRC (see [Section 11.3.3\)](#page-903-0).
- Encrypted pad will not be transmitted on the link. Receiver must reconstruct the ciphertext for the padded region when calculating the AES-GCM MAC.

Credit return (CRD) field does not carry any confidential data. The CRD field needs to be integrity protected, so the CRD field shall map to AES-GCM input *A*.

The rules for handling latency-optimized flits are as follows:

- Slot 7 bytes shall be packed together before mapping to AES-GCM input *P*.
- Slot 8 is only 12 bytes long. It shall be padded with 32 bits of 0 at the end of slot content. This will enable subsequent slots to be aligned on the 128-bit AES block boundary.
- Packed Slot 7 and padded Slot 8 should be used when calculating PCRC (see [Section 11.3.3\)](#page-903-0).
- Receiver must reconstruct the ciphertext for the padded region in Slot 8 when calculating AES-GCM MAC.
- AES-GCM input *A* for each flit shall be padded with 0s to align it to 32 bits.
- Header slot contains protocol header: slot\_type|CRD|012.
- Header slot contains MAC: CRD|016.

In the case of 256B flits, only Slot 0 and Slot 15 contribute to the AAD. [Figure 11-5](#page-898-0), [Figure 11-6](#page-898-1), [Figure 11-7](#page-899-0), [Figure 11-8](#page-899-1), [Figure 11-9](#page-899-2), and [Figure 11-10](#page-900-0) depict handling of the AAD field.

[Figure 11-5](#page-898-0) depicts the case when Slot 0 contains LLCTRL (H8) slot format encoding with an IDE.MAC message. In this case, Slot 0 does not contain any bits that require integrity protection; therefore, Slot 0 is not IDE protected.

<span id="page-898-0"></span>**Figure 11-5. 256B Flit: Handling of Slot 0 when it Carries H8**

![](_page_898_Figure_3.jpeg)

[Figure 11-6](#page-898-1) shows the case where Slot 0 contains protocol header slot format encoding (H0 - H7, H9 - H15). The first 2 bytes that contain the flit header are not IDE protected. Bits 0 - 3 of Slot 0 that carry the slot format encoding are not encrypted, but are integrity protected and therefore map to the AAD field. The remaining bits of the slot are encrypted and integrity protected (additional details regarding mapping to the *P* field are provided in [Figure 11-11\)](#page-900-1).

<span id="page-898-1"></span>**Figure 11-6. 256B Flit: Handling of Slot 0 when it Does Not Carry H8**

![](_page_898_Figure_6.jpeg)

Handling of Slot 15 is shown in [Figure 11-7.](#page-899-0) When the flit carries protocol information, the CRD field carried in Slot 15 needs to be integrity protected. In this case, the first two bytes of CRD information (Credit return byte 0 and Credit return byte 1) map to the AES-GCM AAD field.

<span id="page-899-0"></span>**Figure 11-7. 256B Flit: Handling of Slot 15**

![](_page_899_Figure_3.jpeg)

[Figure 11-8](#page-899-1) shows how the bits that only need to be integrity protected are mapped to the AAD field when the first flit carries a protocol header in Slot 0 and the second flit carries IDE.MAC in Slot 0.

<span id="page-899-1"></span>**Figure 11-8. Mapping of Integrity-only Protected Bits to AAD - Case 1**

|           |           | Flit0    | H8 MAC      |           | FI       | it1 proto | col head | ler |
|-----------|-----------|----------|-------------|-----------|----------|-----------|----------|-----|
| bit       |           |          |             | by        | tes      |           |          |     |
|           | C         | )        | 1 2         | 3         | 4        | 5         | 6        | 7   |
| 0         | C0b0      | C1b0     | 0           | 0         |          | C0b4      | C1b4     | 0   |
| 1         | C0b1      | C1b1     | 0           | 0         | b0-3     | C0b5      | C1b5     | 0   |
| 2         | C0b2      | C1b2     | 0           | 0         | 50-3     | C0b6      | C1b6     | 0   |
| 3         | C0b3      | C1b3     | 0           | 0         |          | C0b7      | C1b7     | 0   |
| 4         | C0b4      | C1b4     | 0           | 0         | C0b0     | C1b0      | 0        | 0   |
| 5         | C0b5      | C1b5     | 0           | 0         | C0b1     | C1b1      | 0        | 0   |
| 6         | C0b6      | C1b6     | 0           | 0         | C0b2     | C1b2      | 0        | 0   |
| 7         | C0b7      | C1b7     | 0           | 0         | C0b3     | C1b3      | 0        | 0   |
| (b) First | flit carr | es MA    | in Slot 0   |           |          |           |          |     |
|           |           |          |             |           |          |           |          |     |
| No IDE p  | rotectio  | on       |             |           |          |           |          |     |
| Header I  | bits for  | Integrit | y protectio | on only ( | AES GCM  | 1 AAD)    |          |     |
|           | _         |          | by CXL.cac  |           | IDE. Inc | lude the  | se bits  |     |

[Figure 11-9](#page-899-2) shows how the bits that only need to be integrity protected are mapped to the AAD field when the first flit carries IDE.MAC in Slot 0 and the second flit carries a protocol header.

<span id="page-899-2"></span>**Figure 11-9. Mapping of Integrity-only Protected Bits to AAD - Case 2**

|                                                                                                 |          | Flit1     | нa мac    |          | Fli      | Flit1 protocol header |      |     |  |  |  |
|-------------------------------------------------------------------------------------------------|----------|-----------|-----------|----------|----------|-----------------------|------|-----|--|--|--|
| bit                                                                                             | bytes    |           |           |          |          |                       |      |     |  |  |  |
|                                                                                                 | 4        | 5         | 6         | 7        | 4        | . 5                   | 5 6  | 5 7 |  |  |  |
| 0                                                                                               | C0b0     | C1b0      | 0         | 0        |          | C0b4                  | C1b4 | 0   |  |  |  |
| 1                                                                                               | C0b1     | C1b1      | 0         | 0        | b0-3     | C0b5                  | C1b5 | 0   |  |  |  |
| 2                                                                                               | C0b2     | C1b2      | 0         | 0        | DU-3     | C0b6                  | C1b6 | 0   |  |  |  |
| 3                                                                                               | C0b3     | C1b3      | 0         | 0        |          | C0b7                  | C1b7 | 0   |  |  |  |
| 4                                                                                               | C0b4     | C1b4      | 0         | 0        | C0b0     | C1b0                  | (    | 0 0 |  |  |  |
| 5                                                                                               | C0b5     | C1b5      | 0         | 0        | C0b1     | C1b1                  | (    | 0 0 |  |  |  |
| 6                                                                                               | C0b6     | C1b6      | 0         | 0        | C0b2     | C1b2                  | (    | 0 0 |  |  |  |
| 7                                                                                               | C0b7     | C1b7      | 0         | 0        | C0b3     | C1b3                  | (    | 0 0 |  |  |  |
| First fli                                                                                       | t carrie | s MAC i   | n Slot 0  |          |          |                       |      |     |  |  |  |
|                                                                                                 |          |           |           |          |          |                       |      |     |  |  |  |
| No IDE                                                                                          | protec   | tion      |           |          |          |                       |      |     |  |  |  |
| Header                                                                                          | bits fo  | or Integr | rity prot | ection o | only (AE | S GCM                 | AAD) |     |  |  |  |
| Zero padding required by CXL.cachemem IDE. Include these bits in the computation of AAD length. |          |           |           |          |          |                       |      |     |  |  |  |

[Figure 11-10](#page-900-0) shows the third case of how the bits that only need to be integrity protected are mapped to the AAD field. In this case, both flits carry protocol headers in Slot 0. When the flit carries a protocol header, there are 20 bits that require integrity protection. These 20 bits are made up of 4 bits of Slot encoding (Slot 0) and 16 bits of CRD (Slot 15). These are padded with trailing 0s to create a 32-bit AAD input.

<span id="page-900-0"></span>**Figure 11-10. Mapping of Integrity-only Protected Bits to AAD - Case 3**

|          | FI                                           | it0 prot | tocol he  |           | Flit1 protocol header |        |       |      |   |   |
|----------|----------------------------------------------|----------|-----------|-----------|-----------------------|--------|-------|------|---|---|
| bit      |                                              |          |           | yte       | tes                   |        |       |      |   |   |
|          | 0                                            | 1        | 1 2       | 2 3       | 3                     | 4      | 5     | 5    | 6 | 7 |
| 0        |                                              | C0b4     | C1b4      | C         | 0                     |        | C0b4  | C1b4 |   | 0 |
| 1        | b0-3                                         | C0b5     | C1b5      | (         | 0                     | b0-3   | C0b5  | C1b5 | , | 0 |
| 2        | 50-3                                         | C0b6     | C1b6      | (         | )                     | DU-3   | C0b6  | C1b6 | 5 | 0 |
| 3        |                                              | C0b7     | C1b7      | (         | 0                     |        | C0b7  | C1b7 | 7 | 0 |
| 4        | C0b0                                         | C1b0     | C         | ) (       | C                     | 0b0    | C1b0  |      | 0 | 0 |
| 5        | C0b1                                         | C1b1     | C         | ) (       | O                     | 0b1    | C1b1  |      | 0 | 0 |
| 6        | C0b2                                         | C1b2     | C         | ) (       | ) C                   | 0b2    | C1b2  |      | 0 | 0 |
| 7        | C0b3                                         | C1b3     | C         | ) (       | o <mark>C</mark>      | 0b3    | C1b3  |      | 0 | 0 |
| Both fli | ts carn                                      | y proto  | ol heade  | er in Slo | t O                   |        |       |      |   |   |
|          |                                              |          |           |           |                       |        |       |      |   |   |
| No IDE   | protec                                       | tion     |           |           |                       |        |       |      |   |   |
| Header   | bits fo                                      | r Integ  | rity prot | tection   | onl                   | ly (AE | S GCM | AAD) |   |   |
|          | _                                            |          | ed by CX  |           |                       |        |       | de   |   |   |
| these b  | these bits in the computation of AAD length. |          |           |           |                       |        |       |      |   |   |

Because there can be only one IDE.MAC within any given MAC epoch, it is impossible for both flits to carry IDE.MAC. Such a case does not exist and hence not shown here.

[Figure 11-11](#page-900-1) shows the transmitter's handling of bits that require both encryption and integrity protection for the standard 256B flit when Slot 0 contains LLCTRL (H8) Slot format encoding with an IDE.MAC message. Slot 0 content is not IDE protected. Slots 1 - 14 are mapped to *P*.

<span id="page-900-1"></span>**Figure 11-11. Standard 256B Flit - Mapping to AAD and P bits when Slot 0 carries H8**

|          | bit    | (        | 0 1        |         | 2       | 3       | 4        | 5        | 6      | 7  | 8  | 9   | 10  | 11  | 12      | 13  | 14  |
|----------|--------|----------|------------|---------|---------|---------|----------|----------|--------|----|----|-----|-----|-----|---------|-----|-----|
| slot0    |        | 2E       | HDR        | B0      | B1      | B2      | B3       | B4       | B5     | B6 | B7 | B8  | B9  | B10 | B11     | B12 | B13 |
| slot1    | 0-7    | B0       | B1         | B2      | B3      | B4      | B5       | B6       | B7     | B8 | B9 | B10 | B11 | B12 | B13     | B14 | B15 |
| slot2    | 0-7    | B0       | B1         | B2      | B3      | B4      | B5       | B6       | B7     | B8 | B9 | B10 | B11 | B12 | B13     | B14 | B15 |
| slot3    | 0-7    | B0       | B1         | B2      | B3      | B4      | B5       | B6       | B7     | B8 | B9 | B10 | B11 | B12 | B13     | B14 | B15 |
| slot4    | 0-7    | B0       | B1         | B2      | B3      | B4      | B5       | B6       | B7     | B8 | B9 | B10 | B11 | B12 | B13     | B14 | B15 |
| slot5    | 0-7    | B0       | B1         | B2      | B3      | B4      | B5       | B6       | B7     | B8 | B9 | B10 | B11 | B12 | B13     | B14 | B15 |
| slot6    | 0-7    | B0       | B1         | B2      | B3      | B4      | B5       | B6       | B7     | B8 | B9 | B10 | B11 | B12 | B13     | B14 | B15 |
| slot7    | 0-7    | B0       | B1         | B2      | B3      | B4      | B5       | B6       | B7     | B8 | B9 | B10 | B11 | B12 | B13     | B14 | B15 |
| slot8    | 0-7    | B0       | B1         | B2      | B3      | B4      | B5       | B6       | B7     | B8 | B9 | B10 | B11 | B12 | B13     | B14 | B15 |
| slot9    | 0-7    | B0       | B1         | B2      | B3      | B4      | B5       | B6       | B7     | B8 | B9 | B10 | B11 | B12 | B13     | B14 | B15 |
| slot10   | 0-7    | B0       | B1         | B2      | B3      | B4      | B5       | B6       | B7     | B8 | B9 | B10 | B11 | B12 | B13     | B14 | B15 |
| slot11   | 0-7    | B0       | B1         | B2      | B3      | B4      | B5       | B6       | B7     | B8 | B9 | B10 | B11 | B12 | B13     | B14 | B15 |
| slot12   | 0-7    | B0       | B1         | B2      | B3      | B4      | B5       | B6       | B7     | B8 | B9 | B10 | B11 | B12 | B13     | B14 | B15 |
| slot13   | 0-7    | B0       | B1         | B2      | B3      | B4      | B5       | B6       | B7     | B8 | B9 | B10 | B11 | B12 | B13     | B14 | B15 |
| slot14   | 0-7    | B0       | B1         | B2      | B3      | B4      | B5       | B6       | B7     | B8 | B9 | B10 | B11 | B12 | B13     | B14 | B15 |
| slot15   |        | COBO     | COB1       |         |         |         |          | CRC (8B) |        |    |    |     |     | -   | EC (6B) |     |     |
| Slot 0 a | ontain | s LLCTR  | RL (H8) sl | ot form | at e no | oding v | vith IDE | .MAC m   | essage |    |    |     |     |     |         |     |     |
|          |        |          |            |         |         |         |          |          |        |    |    |     |     |     |         |     |     |
|          |        |          |            |         |         |         |          |          |        |    |    |     |     |     |         |     |     |
| No IDE   |        |          |            |         |         |         |          |          |        |    |    |     |     |     |         |     |     |
|          |        |          | only (AE   |         | -       |         |          |          |        |    |    |     |     |     |         |     |     |
| Encrypt  | and I  | ntegrity | protect    | (AES-G  | CM P)   |         |          |          |        |    |    |     |     |     |         |     |     |
| Zero pa  | dding  | require  | ed by CX   | L.cache | mem l   | DE. En  | crypt an | d        |        |    |    |     |     |     |         |     |     |
| Integrit | y prot | ect (AE  | S-GCM F    | ). Indu | de the  | se bits | in the   |          |        |    |    |     |     |     |         |     |     |
| comput   |        | •        |            |         |         |         |          |          |        |    |    |     |     |     |         |     |     |

[Figure 11-12](#page-901-0) shows the transmitter's handling of bits that require both encryption and integrity protection for the standard 256B flit when Slot 0 contains protocol header slot format encoding (H0 - H7, H9 - H 15). Slot 0 contains 108 bits, starting from bit 4 of the slot header. These bits are padded with leading 0s to align the content to a 128-bit boundary. The padded Slot 0 content, and Slots 1 - 14, are mapped to *P*.

<span id="page-901-0"></span>**Figure 11-12. Standard 256B Flit - Mapping to AAD and P bits when Slot 0 Does Not Carry H8**

|                 |            |          |          |                 |       |          |                      |          |          | by       | /tes     |          |            |            |            |            |            |            |
|-----------------|------------|----------|----------|-----------------|-------|----------|----------------------|----------|----------|----------|----------|----------|------------|------------|------------|------------|------------|------------|
|                 | bit        | 0        | 1        |                 | 2     | 3        | 4                    | 5        | 5        |          |          | 8        | 9 1        | 0 11       | . 12       | 2 1        | 3 14       | 1 1        |
|                 | 0          | 0        |          | 0               | 0     |          |                      |          |          |          |          |          |            |            |            |            |            |            |
|                 | 1          | 0        |          | 0               | 0     |          |                      |          |          |          |          |          |            |            |            |            |            |            |
|                 | 2          | 0        |          | 0               | 0     |          |                      |          |          |          |          |          |            |            |            |            |            |            |
| slot0           | 3          | 0        |          | 00              | 0     | B1       | B2                   | B3       | B4       | B5       | B6       | B7       | B8         | B9         | B10        | B11        | B12        | B13        |
| 31000           | 4          | 0        |          | 0               |       | DI       | UZ                   | 55       |          | - 63     | 50       | - 57     | 50         | 65         | 910        | 011        | 512        | 013        |
|                 | 5          | 0        |          | 0 <sub>b4</sub> | -7    |          |                      |          |          |          |          |          |            |            |            |            |            |            |
|                 | 6          | 0        |          | 0               |       |          |                      |          |          |          |          |          |            |            |            |            |            |            |
|                 | 7          | 0        |          | 0               |       |          |                      |          |          |          |          |          |            |            |            |            |            |            |
| slot1           | 0-7        | B0       | B1       | B2              |       | 33       | B4                   | B5       | B6       | B7       | B8       | B9       | B10        | B11        | B12        | B13        | B14        | B15        |
| slot2           | 0-7        | B0       | B1       | B2              |       | _        | B4                   | B5       | B6       | B7       | B8       | B9       | B10        | B11        | B12        | B13        | B14        | B15        |
| slot3           | 0-7        | B0       | B1       | B2              |       | 33       | B4                   | B5       | B6       | B7       | B8       | B9       | B10        | B11        | B12        | B13        | B14        | B15        |
| slot4           | 0-7        | B0       | B1       | B2              |       | _        | B4                   | B5       | B6       | B7       | B8       | B9       | B10        | B11        | B12        | B13        | B14        | B15        |
| slot5           | 0-7        | B0       | B1       | B2              |       | 33       | B4                   | B5       | B6       | B7       | B8       | B9       | B10        | B11        | B12        | B13        | B14        | B15        |
| slot6           | 0-7        | B0       | B1       | B2              |       | -        | B4                   | B5       | B6       | B7       | B8       | B9       | B10        | B11        | B12        | B13        | B14        | B15        |
| slot7           | 0-7        | B0       | B1       | B2              |       | 33       | B4                   | B5       | B6       | B7       | B8       | B9       | B10        | B11        | B12        | B13        | B14        | B15        |
| slot8           | 0-7<br>0-7 | B0       | B1<br>B1 | B2<br>B2        |       | 33<br>33 | B4<br>R4             | B5<br>B5 | B6<br>B6 | B7<br>B7 | B8<br>B8 | B9<br>B9 | B10<br>B10 | B11        | B12<br>B12 | B13<br>B13 | B14        | B15<br>B15 |
| slot9<br>slot10 | 0-7        | BO<br>BO | B1       | B2<br>B2        |       | 33<br>33 | B4<br>B4             | B5       | B6       | B7       | B8       | B9       | B10<br>B10 | B11<br>B11 | B12        | B13        | B14<br>B14 | B15        |
|                 | 0-7        | B0       | B1       | B2<br>B2        |       | 33<br>33 | B4<br>B4             | B5       | B6       | B7       | B8       | B9       | B10        | B11        | B12        | B13        | B14<br>B14 | B15        |
|                 | 0-7        | BO<br>BO | B1       | B2<br>B2        |       | 33<br>33 | в4<br>B4             | B5       | B6       | B7       | B8       | B9       | B10        | B11        | B12        | B13        | B14        | B15        |
|                 | 0-7        | BO       | B1       | B2              |       | 33       | в4<br>B4             | B5       | B6       | B7       | B8       | B9       | B10        | B11        | B12        | B13        | B14        | B15        |
|                 | 0-7        | B0       | B1       | B2              |       | _        | Б <del>4</del><br>B4 | B5       | B6       | B7       | B8       | B9       | B10        | B11        | B12        | B13        | B14        | B15        |
| slot15          | 0,         | COBO     | COB1     | 52              |       | ~        |                      |          | (8B)     | ٠,       |          |          | 510        | 011        |            | (6B)       | 524        | 010        |
| Slot 0 $\alpha$ | ntains     |          |          | der slo         | ot fo | rmat e i | ncodina              |          | 1/       | – H 15)  |          |          |            |            | , 20       | (30)       |            |            |
|                 |            |          |          |                 | Ť     |          |                      |          |          |          |          |          |            |            |            | +          |            |            |
| No IDE          | orotect    | ion      |          |                 |       |          |                      |          |          |          |          |          |            |            |            | 1          |            |            |
| Integrit        |            |          | nly (Al  | ES GCI          | ИAA   | D)       |                      |          |          |          |          |          |            |            |            |            |            |            |
| Encrypt         |            |          |          |                 |       |          |                      |          |          |          |          |          |            |            |            |            |            |            |
| Zero pa         |            | · ·      | •        | •               |       | •        | Encry                | pt and   |          |          |          |          |            |            |            |            |            |            |
| Integrit        | _          | •        | •        |                 |       |          | •                    | •        |          |          |          |          |            |            |            |            |            |            |
| _               |            | of P len |          | ,               |       |          |                      |          |          |          |          |          |            |            |            |            |            |            |

[Figure 11-13](#page-902-0) shows the transmitter's handling of bits that require both encryption and integrity protection for the latency-optimized 256B flit when Slot 0 contains LLCTRL (H8) Slot format encoding with an IDE.MAC message. Slot 0 content is not IDE protected. Slots 1 - 14 are mapped to *P*.

<span id="page-902-0"></span>**Figure 11-13. Latency-Optimized 256B Flit - Mapping to AAD and P Bits when Slot 0 Carries H8**

|          |        |          |           |         |                     |        |            |       | ŀ       | oytes |    |     |     |     |        |     |     |
|----------|--------|----------|-----------|---------|---------------------|--------|------------|-------|---------|-------|----|-----|-----|-----|--------|-----|-----|
|          | bit    | 0        | 1         | 2       | 3                   | 4      | 5          | 6     | 7       | 8     | 9  | 10  | 11  | 12  | 13     | 14  | 15  |
| slot0    |        | 2B       | HDR       | B0      | B1                  | B2     | B3         | B4    | B5      | B6    | B7 | B8  | B9  | B10 | B11    | B12 | B13 |
| slot1    | 0-7    | B0       | B1        | B2      | B3                  | B4     | B5         | B6    | B7      | B8    | B9 | B10 | B11 | B12 | B13    | B14 | B15 |
| slot2    | 0-7    | B0       | B1        | B2      | B3                  | B4     | B5         | B6    | B7      | B8    | B9 | B10 | B11 | B12 | B13    | B14 | B15 |
| slot3    | 0-7    | B0       | B1        | B2      | B3                  | B4     | B5         | B6    | B7      | B8    | B9 | B10 | B11 | B12 | B13    | B14 | B15 |
| slot4    | 0-7    | B0       | B1        | B2      | B3                  | B4     | B5         | B6    | B7      | B8    | B9 | B10 | B11 | B12 | B13    | B14 | B15 |
| slot5    | 0-7    | B0       | B1        | B2      | B3                  | B4     | B5         | B6    | B7      | B8    | B9 | B10 | B11 | B12 | B13    | B14 | B15 |
| slot6    | 0-7    | B0       | B1        | B2      | B3                  | B4     | B5         | B6    | B7      | B8    | B9 | B10 | B11 | B12 | B13    | B14 | B15 |
| slot7    | 0-7    | B0       | B1        | B2      | B3                  | B4     | B5         | B6    | B7      | B8    | B9 | B10 | B11 | B12 | B13    | B14 | B15 |
| slot8    | 0-7    | B0       | B1        | B2      | B3                  | B4     | B5         | B6    | B7      | B8    | B9 | B10 | B11 | 0   | 0      | 0   | 0   |
| slot9    | 0-7    | B0       | B1        | B2      | B3                  | B4     | B5         | B6    | B7      | B8    | B9 | B10 | B11 | B12 | B13    | B14 | B15 |
| slot10   | 0-7    | B0       | B1        | B2      | B3                  | B4     | B5         | B6    | B7      | B8    | B9 | B10 | B11 | B12 | B13    | B14 | B15 |
| slot11   | 0-7    | B0       | B1        | B2      | B3                  | B4     | B5         | B6    | B7      | B8    | B9 | B10 | B11 | B12 | B13    | B14 | B15 |
| slot12   | 0-7    | B0       | B1        | B2      | B3                  | B4     | B5         | B6    | B7      | B8    | B9 | B10 | B11 | B12 | B13    | B14 | B15 |
| slot13   | 0-7    | B0       | B1        | B2      | B3                  | B4     | B5         | B6    | B7      | B8    | B9 | B10 | B11 | B12 | B13    | B14 | B15 |
| slot14   | 0-7    | B0       | B1        | B2      | B3                  | B4     | B5         | B6    | B7      | B8    | B9 | B10 | B11 | B12 | B13    | B14 | B15 |
| slot15   |        | COBO     | COB1      |         | B10, B11            | _      |            |       | RC (8B) |       |    |     |     | FE  | C (6B) |     |     |
| Slot 0 a | ontair | ns LLCT  | RL (H8) s | lot for | mat enco            | ding v | vith IDE.I | MAC m | essage  |       |    |     |     |     |        |     |     |
|          |        |          |           |         |                     |        |            |       |         |       |    |     |     | -   | -      |     |     |
| No IDE   |        |          |           |         |                     |        |            |       |         |       |    |     |     |     | -      |     |     |
|          |        |          | only (A   |         |                     |        |            |       |         |       |    |     |     | -   | -      |     | +   |
| Encrypt  | and I  | ntegrit  | y proteo  | t (AES- | -GCMP)              |        |            |       |         |       |    |     | -   | -   | -      |     | +   |
| •        | y pro  | tect (Al | ES-GCM    |         | emem IC<br>ude thes |        |            | i     |         |       |    |     |     |     |        |     |     |

[Figure 11-14](#page-903-1) shows the transmitter's handling of bits that require both encryption and integrity protection for the latency-optimized 256B flit when Slot 0 contains protocol header slot format encoding (H0 - H7, H9 - H 15). Slot 0 contains 108 bits, starting from bit 4 of the slot header. These bits are padded with leading 0s to align the content to a 128-bit boundary. The padded Slot 0 content, and Slots 1 - 14, are mapped to *P*.

<span id="page-903-1"></span>**Figure 11-14. Latency-Optimized 256B Flit - Mapping to AAD and P Bits when Slot 0 Does Not Carry H8**

|           |        |          |          |         |         |         |           |         |         | bytes |    |     |     |     |        |     |     |
|-----------|--------|----------|----------|---------|---------|---------|-----------|---------|---------|-------|----|-----|-----|-----|--------|-----|-----|
|           | bit    | 0        | 1        | 2       | 3       | 4       | 5         | 6       | 7       | 8     | 9  | 10  | 11  | 12  | 13     | 14  | 15  |
|           | 0      | 0        | 0        | 0       |         |         |           |         |         |       |    |     |     |     |        |     |     |
|           | 1      | 0        | 0        | 0       | 0       |         |           |         |         |       |    |     |     |     |        |     |     |
|           | 2      | 0        | 0        | 0 0     |         |         |           |         |         |       |    |     |     |     |        |     |     |
| slot0     | 3      | 0        | 0        | 0       | B1      | B2      | B3        | B4      | B5      | B6    | B7 | B8  | B9  | B10 | B11    | B12 | B13 |
| SIULU     | 4      | 0        | 0        |         | DI      | DZ      | 65        | D4      | 85      | Bo    | Б/ | БO  | 65  | 510 | 511    | D12 | D13 |
|           | 5      | 0        | 0        | b4-7    |         |         |           |         |         |       |    |     |     |     |        |     |     |
|           | 6      | 0        | 0        | 547     |         |         |           |         |         |       |    |     |     |     |        |     |     |
|           | 7      | 0        | 0        |         |         |         |           |         |         |       |    |     |     |     |        |     |     |
| slot1     | 0-7    | B0       | B1       | B2      | B3      | B4      | B5        | B6      | B7      | B8    | B9 | B10 | B11 | B12 | B13    | B14 | B15 |
| slot2     | 0-7    | B0       | B1       | B2      | B3      | B4      | B5        | B6      | B7      | B8    | B9 | B10 | B11 | B12 | B13    | B14 | B15 |
| slot3     | 0-7    | B0       | B1       | B2      | B3      | B4      | B5        | B6      | B7      | B8    | B9 | B10 | B11 | B12 | B13    | B14 | B15 |
| slot4     | 0-7    | B0       | B1       | B2      | B3      | B4      | B5        | B6      | B7      | B8    | B9 | B10 | B11 | B12 | B13    | B14 | B15 |
| slot5     | 0-7    | B0       | B1       | B2      | B3      | B4      | B5        | B6      | B7      | B8    | B9 | B10 | B11 | B12 | B13    | B14 | B15 |
| slot6     | 0-7    | B0       | B1       | B2      | B3      | B4      | B5        | B6      | B7      | B8    | B9 | B10 | B11 | B12 | B13    | B14 | B15 |
| slot7     | 0-7    | B0       | B1       | B2      | B3      | B4      | B5        | B6      | B7      | B8    | B9 | B10 | B11 | B12 | B13    | B14 | B15 |
| slot8     | 0-7    | B0       | B1       | B2      | B3      | B4      | B5        | B6      | B7      | B8    | B9 | B10 | B11 | 0   | 0      | 0   | 0   |
| slot9     | 0-7    | B0       | B1       | B2      | B3      | B4      | B5        | B6      | B7      | B8    | B9 | B10 | B11 | B12 | B13    | B14 | B15 |
| slot10    | 0-7    | B0       | B1       | B2      | B3      | B4      | B5        | B6      | B7      | B8    | B9 | B10 | B11 | B12 | B13    | B14 | B15 |
| slot11    | 0-7    | B0       | B1       | B2      | B3      | B4      | B5        | B6      | B7      | B8    | B9 | B10 | B11 | B12 | B13    | B14 | B15 |
|           | 0-7    | B0       | B1       | B2      | B3      | B4      | B5        | B6      | B7      | B8    | B9 | B10 | B11 | B12 | B13    | B14 | B15 |
| slot13    | 0-7    | B0       | B1       | B2      | B3      | B4      | B5        | B6      | B7      | B8    | B9 | B10 | B11 | B12 | B13    | B14 | B15 |
| slot14    | 0-7    | B0       | B1       | B2      | B3      | B4      | B5        | B6      | B7      | B8    | B9 | B10 | B11 | B12 | B13    | B14 | B15 |
| slot15    |        | COBO     | COB1     |         | B10, B1 |         |           |         | RC (8B) |       |    |     |     | FE  | C (6B) |     |     |
| Slot 0 co | ontair | ns proto | col hea  | derslo  | t forma | t encod | ing (HO   | -H7, H9 | – H 15) |       |    |     |     |     |        |     |     |
|           |        |          |          |         |         |         |           |         |         |       |    |     |     |     |        |     |     |
| No IDE    | prote  | ction    |          |         |         |         |           |         |         |       |    |     |     |     |        |     |     |
|           |        |          | only (A  |         |         |         |           |         |         |       |    |     |     |     |        |     |     |
| Encrypt   | and I  | ntegrit  | y protec | t (AES- | GCMP)   |         |           |         |         |       |    |     |     |     |        |     |     |
| •         | y pro  | tect (AE | S-GCM    |         |         |         | crypt and | d       |         |       |    |     |     |     |        |     |     |

When operating in Skid mode, implementations can choose to maximize the benefits of latency optimization by decrypting and processing Slot 8 bytes 0 - 9, and Slots 9 - 14 as soon as they are received. Only MAC computation and decryption of Slot 8 bytes 10 - 11 needs to wait until Slot 14 is received. In such cases, implementation-specific mechanisms should exist to unwind IDE processing if CRC/FEC checks fail.

### <span id="page-903-0"></span>11.3.3 Encrypted PCRC

A polynomial with the coefficients 1EDC 6F41h shall be used for PCRC calculation. PCRC calculation shall begin with an initial value of FFFF FFFFh. The PCRC shall be calculated across all the bytes of plaintext in the aggregated flits that are part of the given MAC epoch. PCRC calculation shall begin with bit0 byte0 of flit plaintext content and sequentially include bits 0 - 7 for each byte of the flit contents that are mapped to the plaintext. After accumulating the 32-bit value across the flit contents, the PCRC value shall be finalized by taking 1's complement of the bits of accumulated value to obtain PCRC[31:0].

On the transmitter side (see [Figure 11-15](#page-904-0)), the PCRC value shall be appended to the end of the aggregated flit plaintext content, encrypted, and then included in the MAC calculation. The encrypted PCRC value is not transmitted across the link.

On the receiver side (see [Figure 11-16](#page-904-1)), the PCRC value shall be recalculated based on the received, decrypted ciphertext. When the last flit of the current MAC epoch has been processed, the accumulated PCRC value shall be XORed (encrypted) with the AES keystream bits that immediately follow the values that are used for decrypting the received cipher flit. This encrypted PCRC value shall be appended to the end of the received ciphertext for the purposes of MAC computation.

<span id="page-904-0"></span>**Figure 11-15. Inclusion of the PCRC Mechanism in the AES-GCM Advanced Encryption Function**

![](_page_904_Figure_4.jpeg)

<span id="page-904-1"></span>**Figure 11-16. Inclusion of the PCRC Mechanism in the AES-GCM Advanced Decryption Function**

![](_page_904_Figure_6.jpeg)

### <span id="page-905-0"></span>11.3.4 Cryptographic Keys and IV

Initialization of a CXL.cachemem IDE Stream involves multiple steps. It is possible that some of these steps can be merged or performed in a different order. The first step is to establish the authenticity and identity of the components that contain the two ports that operate as endpoints for a CXL.cachemem IDE Stream. The second step is to establish the IDE Stream keys. In some cases, these two steps may be combined. Third, the IDE is configured. Finally, the establishment of the IDE Stream is triggered.

CXL.cachemem IDE may make use of CXL.io IDE mechanisms for device attestation and key exchange using a standard mechanism, as described in [Section 11.4](#page-917-2).

*IV* construction of CXL.cachemem IDE is described below. A 96-bit *IV* of deterministic construction is used as per NIST Special Publication 800-38D for AES-GCM.

All ports shall support the Default *IV* Construction. The default *IV* construction is as follows:

- A fixed field is located at bits 95:64 of the *IV*, where bits 95:92 contain the substream identifier, 1000b, and bits 91:64 are all 0s. The same sub-stream encoding is used for both transmitted and received flits; however, the keys that the port uses during transmit and receive flows must be distinct.
- Bits 63:0 of the *IV* are referred to as the invocation field. The invocation field contains a monotonically incrementing counter with rollover properties. The invocation field is initially set to the value 0000 0001h for each sub-stream upon establishment of the IDE Stream including a rekeying flow. If the CXL.cachemem IV Generation Capable bit in CXL\_QUERY\_RESP returns the value of 1, the port is capable of initially setting *IV* to a value other than what is generated via the Default *IV* Construction. See the CXL\_KEY\_PROG message definition (see [Section 11.4.5\)](#page-922-0) for details.

In either case, the invocation field is incremented every time an *IV* is consumed. Neither the transmitter nor the receiver are required to detect *IV* rollover1 and are not required to take any special action when the *IV* rolls over.

### <span id="page-905-1"></span>11.3.5 CXL.cachemem IDE Modes

CXL.cachemem IDE supports two modes of operation:

- Containment mode: In Containment mode, the data is released for further processing only after the integrity check passes. This mode impacts both latency and bandwidth. The latency impact is due to the need to buffer several flits until the integrity value has been received and checked. The bandwidth impact comes from the fact that integrity value is sent quite frequently. If Containment mode is supported and enabled, the devices (and hosts) shall use an Aggregation Flit Count of 5 in 68B Flit mode and 2 in 256B Flit mode.
- Skid mode: Skid mode allows the data to be released for further processing without waiting for the integrity value to be received and checked. This allows for lessfrequent transmission of the integrity value. Skid mode allows for near-zero latency overhead and low bandwidth overhead. In this mode, data modified by an adversary is potentially consumed by software; however, such an attack will subsequently be detected when the integrity value is received and checked. If Skid mode is supported and enabled, all devices (and hosts) shall use an Aggregation Flit Count of 128 in 68B Flit mode and of 32 in 256B Flit mode. When using this mode, the software and application stack must be capable of tolerating attacks within a narrow time window, or the result is undefined.

<sup>1.</sup> For a x16 link operating at 32 GT/s, a 64-bit *IV* will take longer than 1000 years to roll over.

#### <span id="page-906-0"></span>11.3.5.1 Discovery of Integrity Modes and Settings

Each port shall enumerate the modes that the port supports and other capabilities via registers in the CXL IDE Capability Structure (see [Section 8.2.4.22](#page-577-1)). All devices adherent to this specification shall support Containment mode.

#### <span id="page-906-1"></span>11.3.5.2 Negotiation of Operating Mode and Settings

The operating mode and timing parameters are configured in the CXL IDE Capability Structure (see [Section 8.2.4.22](#page-577-1)) prior to enabling of CXL.cachemem IDE.

#### <span id="page-906-2"></span>11.3.5.3 Rules for MAC Aggregation

The rules for generation and transfer of MAC are as follows:

- MAC epoch: A MAC epoch is defined as the set of consecutive flits that are part of a given aggregation unit. The IDE mode (see [Section 11.3.5\)](#page-905-1) determines the number of flits in a standard MAC epoch. This number is known as Aggregation Flit Count (referred to as N below). Every MAC epoch with the exception of early MAC termination (see [Section 11.3.6\)](#page-909-0) carries N flits. A given MAC header shall contain the tag for exactly one MAC epoch. The transmitter shall accumulate the integrity value over flits in exactly one MAC epoch (that is at most N flits) prior to transmitting the MAC epoch.
- In all cases, the transmitter must send MACs in the same order as MAC epochs.
- [Figure 11-17](#page-907-0) shows an example of MAC generation and transmission for one MAC epoch in the presence of back-to-back protocol traffic for the 68B flit format. [Figure 11-17](#page-907-0) (a) shows that the earliest MAC may be transmitted, assuming that the transmitter completes MAC computation (and gets MAC ready) one cycle after the MAC epoch completes. The earliest flit to be transmitted or received is shown on the top of the figure. Thus, Flits 0 to N-1 (shown in yellow) belonging to MAC Epoch 1 are transmitted in that order. The MAC is calculated over Flits 0 to N-1.

<span id="page-907-0"></span>**Figure 11-17. MAC Epochs and MAC Transmission in Case of Back-to-Back Traffic (a) Earliest MAC Header Transmit (b) Latest MAC Header Transmit in the Presence of Multi-Data Header**

![](_page_907_Figure_3.jpeg)

- The transmitter shall send the MAC header that contains this integrity value at the earliest possible time. Protocol flits belonging to the next MAC epoch are permitted to be sent between the last flit of the current epoch and the transmission of the MAC header for the current epoch. This is needed to handle the transmission of alldata flits and is also useful for avoiding bandwidth bubbles due to MAC calculation latency. It is recommended that the transmitter send the MAC header on the first available Slot 0 header immediately after the MAC calculations are complete.
- On the receiver side, the receiver may expect the MAC header to come in on any protocol flit, from first to sixth protocol flits, after the last flit of the previous MAC epoch (see [Figure 11-17](#page-907-0) (b)).

<span id="page-908-0"></span>**Figure 11-18. Example of MAC Header Being Received in the First Flit of the Current MAC Epoch**

![](_page_908_Figure_3.jpeg)

- In Containment mode, the receiver must not release flits of a given MAC epoch for consumption until the MAC header that contains the integrity value for those flits has been received and the integrity check has passed. In 68B Flit mode, because the receiver can receive up to 5 protocol flits that belong to the current MAC epoch before receiving the MAC header for the previous MAC epoch, the receiver shall buffer the current MAC epoch's flits to ensure that there is no data loss. For example, referring to [Figure 11-17](#page-907-0) (b), both the yellow and green flits are buffered until MAC Epoch 1's MAC header is received and the integrity check passes. If the check passes, the yellow flits can be released for consumption. The green flits cannot, however, be released until the green MAC flit has been received and the integrity verified. [Section 11.3.8](#page-912-1) defines the receiver behavior upon integrity check failure.
- In Skid mode, the receiver may decrypt and release the flits for consumption as soon as they are received. The MAC value shall be accumulated as needed and then checked when the MAC header for the flits in the MAC epoch arrives. Again, referring to [Figure 11-17](#page-907-0) (b), both the yellow and green flits may be decrypted and released for consumption without waiting for the MAC header for MAC Epoch 1 to be received and verified. When MAC Epoch 1's MAC header is received, the header is verified. If the check passes, there is no action to be taken. If the MAC header is not received within 6 protocol flits after the end of the previous MAC epoch, the receiver shall treat the absence of MAC as an error. [Section 11.3.8](#page-912-1) defines the receiver behavior upon integrity check failure, a missing MAC header, or a delayed MAC header.
- In 68B Flit mode, in all cases (including the cases with multi-data headers), at most 5 protocol flits belonging to the current MAC epoch are allowed to be transmitted prior to the transmission of the MAC for the previous MAC epoch. If the MAC header is not received within 6 protocol flits after the end of the previous MAC epoch, the receiver shall treat the absence of MAC as an error.

• In 256B Flit mode, in all cases, at most 1 protocol flit that belongs to the current MAC epoch is allowed to be transmitted prior to the transmission of the MAC for the previous MAC epoch. If the MAC header is not received within 2 protocol flits after the end of the previous MAC epoch, the receiver shall treat the absence of MAC as an error.

> **IMPLEMENTATION NOTE**

In Containment mode, the receiver must not release any decrypted flits for consumption unless their associated MAC check has been performed and passed. This complies with the algorithm for the AES-GCM Authenticated Decryption Function as defined in NIST Special Publication 800-38D.

In Skid mode, the receiver is permitted to release any decrypted flits for consumption without waiting for their associated MAC check to be performed. Unless there are additional device-specific mechanisms to prevent this consumption, the use of Skid mode will not meet the requirements of the above-mentioned algorithm.

Solution stack designers must carefully weigh the benefits vs. the constraints when choosing between Containment mode and Skid mode. Containment mode guarantees that potentially corrupted data will not be consumed. Skid mode provides data privacy and eventual detection of data integrity loss, with significantly less latency impact and link-bandwidth loss compared to Containment mode. However, the use of Skid mode may be more vulnerable to security attacks and will require additional device-specific mechanisms if it is necessary to prevent corrupt data from being consumed.

### <span id="page-909-0"></span>11.3.6 Early MAC Termination

A transmitter is permitted to terminate the MAC epoch early and transmit the MAC for the flits in a truncated MAC epoch when fewer than the Aggregation Flit Count of flits have been transmitted in the current MAC epoch. This can occur as part of link idle handling. The link may be ready to go idle after the transmission of a number of protocol flits, less than the Aggregation Flit Count, in the current MAC epoch.

The following rules shall apply to the early MAC epoch termination and the MAC transmission.

- The transmitter is permitted to terminate the MAC epoch early if and only if the number of protocol flits in the current MAC epoch is less than Aggregation Flit Count. The MAC for this truncated MAC epoch shall be transmitted by itself in the IDE.TMAC Link Layer Control flit (see [Table 4-10\)](#page-214-1). This subtype is referred to as a Truncated MAC flit within this specification.
- Any subsequent protocol flits would become part of a new MAC epoch and would be transmitted after the Truncated MAC flit.
- The MAC for the truncated MAC epoch is calculated identically to the MAC calculation for normal cases, except that it is accumulated over fewer flits.

[Figure 11-20](#page-910-1) shows an example of truncating the current MAC epoch after 3 protocol flits. Flits in current MAC epoch can contain any valid protocol flit including a header flit that contains the MAC for the previous MAC epoch. The MAC for the current MAC epoch shall be sent using a Truncated MAC flit. The Truncated MAC flit will be transmitted following the three protocol flits of the current MAC epoch with no other intervening protocol flits from the next MAC epoch.

<span id="page-910-0"></span>**Figure 11-19. Early Termination and Transmission of Truncated MAC Flit**

![](_page_910_Figure_3.jpeg)

<span id="page-910-1"></span>**Figure 11-20. CXL.cachemem IDE Transmission with Truncated MAC Flit**

![](_page_910_Figure_5.jpeg)

In the case where the link goes idle after sending exactly the Aggregation Flit Count number of flits in the MAC epoch, then the Truncated MAC flit as defined above must not be used. The MAC header must be part of the next MAC epoch. This new MAC epoch is permitted to be terminated early using the Truncated MAC flit (see [Figure 11-21](#page-911-0)).

<span id="page-911-0"></span>**Figure 11-21. Link Idle Case after Transmission of Aggregation Flit Count Number of Flits**

![](_page_911_Figure_3.jpeg)

After the transmitter sends out the MAC flit for all the previous flits that were in flight, the transmitter may go idle. The receiver is permitted to go idle after the MAC flit that corresponds to previously received flits has been received and verified. IDE.Idle control flits are retryable and may be resent as part of replay.

After early MAC termination and transmittal of the Truncated MAC, the transmitter must send at least TruncationDelay number of IDE.Idle flits before it can transmit any protocol flits. TruncationDelay is defined via the following equation:

**Equation 11-1.**

<span id="page-911-1"></span>TruncationDelay = Min(Remaining Flits, Tx Truncation Transmit Delay)

Tx Truncation Transmit Delay (see [Section 8.2.4.22.8](#page-580-2)) is a configuration parameter to account for the potential discarding of any precalculated AES keystream values for the current MAC epoch that need to be discarded. Remaining Flits represent the number of flits remaining to complete the current MAC epoch and is calculated as follows:

### Equation 11-2.

Remaining Flits = Aggregation Flit Count - Number of protocol flits transmitted in current MAC epoch

### <span id="page-912-0"></span>11.3.7 Handshake to Trigger the Use of Keys

<span id="page-912-3"></span>Each port exposes a register interface that software can use to program the transmit and receive keys and their associated parameters. These programmed keys remain pending in registers until activation. While the keys are in the process of being exchanged and configured in the Upstream and Downstream Ports, the link may actively be using a previously configured key. The new keys shall not take effect until the actions described below are taken.

The mechanism described below is used to switch the backup keys to the active state. This is needed to ensure that the Transmitter and Receiver change to using the programmed keys in a coordinated manner.

After the keys are programmed into pending registers on both sides of the link, receipt of the CXL\_K\_SET\_GO request shall cause each transmitter on each port to trigger the transmission of an IDE.Start Link Layer Control flit (see [Table 4-3](#page-197-1)).

After the IDE.Start flit has been sent, all future protocol flits shall be protected by the new keys. To allow the receiver to prepare to receive the flits protected by the new key, the Transmitter is required to send IDE.Idle flits, as defined in [Table 4-10](#page-214-1) for the number of flits specified by the Tx Key Refresh Time field in the Key Refresh Time Control register (see [Section 8.2.4.22.7](#page-580-3)) prior to sending any protocol flits with the new key. These IDE.Idle flits are not encrypted or integrity protected. To prepare to use the new keys, the Tx Key Refresh Time in the transmitter must be configured to a value that is higher than the worst-case latency in the receiver, which is advertised by the receiver via Rx Min Key Refresh Time field in the Key Refresh Time Capability register (see [Section 8.2.4.22.5\)](#page-580-4) or Rx Min Key Refresh Time2 field in the Key Refresh Time Capability2 register (see [Section 8.2.4.22.9\)](#page-581-3), depending on the Flit mode.

After receiving the IDE.Start flit, the receiver must change to using the new keys if the transmitter has met the AES-GCM requirements. During key refresh, it is recommended that the transmitter send an IDE.TMAC before sending an IDE.Start.

It is also permissible for the transmitter to send an IDE.Start after the MAC epoch ends but before the corresponding MAC header is transmitted. In this scenario, the receiver must use the old keys to decrypt the message and to check the MAC.

The transmitter must not send an IDE.Start in the middle of a MAC epoch because doing so violates the fundamental AES-GCM requirement that a single key be used as the input. If the IDE.Start is received in the middle of a MAC epoch, then the receiver shall drop the IDE.Start. The receiver may also set the Rx Error Status field in the CXL IDE Error Status register (see [Section 8.2.4.22.4](#page-579-1)) to CXL.cachemem IDE Establishment Security error and may transition to Insecure State upon detecting this condition.

The IDE.Start flit shall be ordered with respect to the protocol flits. In case of link-level retries, the receiver shall complete retries of previously sent protocol flits before handling the IDE.Start flit and changing to the new key. Other events such as link retraining can occur in the middle of this flow as long as the ordering specified above is maintained.

### <span id="page-912-1"></span>11.3.8 Error Handling

<span id="page-912-2"></span>CXL IDE does not impact or require any changes to the link CRC error handling and the link retry flow.

CXL.cachemem IDE error conditions are enumerated and logged in the Rx Error Status field, Tx Error Status or Unexpected IDE.Stop received fields in the CXL IDE Error Status register (see [Section 8.2.4.22.4\)](#page-579-1). When a CXL.cachemem IDE error is detected, the appropriate bits in the Uncorrectable Error Status register (see [Section 8.2.4.17.1\)](#page-548-3) are also set and the error is signaled using the standard CXL.cachemem protocol error signaling mechanism.

Unless stated otherwise, errors logged in Rx Error Status field or Tx Error Status field cause the CXL.cachemem IDE stream to transition from Active State to Insecure State if it is Active at the time of the error. Note that some of the error conditions that are logged under CXL.cachemem IDE Establishment may not always result in termination of CXL.cachemem IDE stream.

Upon transition to Insecure state:

- Any buffered protocol flits are dropped and all subsequent protocol traffic is dropped until the link is reset.
- Components shall prevent any leakage of keys or user data. The component may need to implement mechanisms to clear the data/state or have access control to prevent leakage of secrets. Such mechanisms and actions are component specific and beyond the scope of this specification.

### <span id="page-913-0"></span>11.3.9 Switch Support

CXL switches that support CXL.cachemem IDE may optionally support CXL.io IDE and may support link IDE or selective IDE streams for CXL.io traffic, including flow through. If supporting CXL.io IDE, CXL switches should follow PCIe IDE switch rules for CXL.io traffic.

A CXL switch may also optionally support Selective Stream IDE for CXL.io traffic, including flow-through Selective IDE Streams. A CXL switch may only support Selective Stream IDE in flow-through mode for CXL.io traffic. In this case, CXL.cachemem IDE cannot be enabled on the host side. In the case of multi-VCS capable switches, CXL IDE may be enabled on a per-root port basis. However, after any root port has enabled CXL IDE, the downstream link from the switch to the MLDs that support CXL IDE, must also have Link IDE enabled. Thus, the traffic from a root port which has not enabled CXL IDE that is targeting an MLD that has enabled CXL IDE would be encrypted and integrity protected between the switch and the device.

**IMPLEMENTATION NOTE: IDE CONFIGURATION OF CXL SWITCHES**

The following examples describe three different models for configuring the CXL.cachemem IDE and performing key exchanges with the CXL switches and the devices attached to them.

**Model A**

Host performs key exchange with the CXL switch and enables CXL IDE. The host will then enumerate the Downstream Ports in the CXL switch and perform key exchange with those downstream devices that support CXL IDE. The Host then programs the keys into the respective Downstream Ports of the switch and enables CXL IDE.

### Model B

Host performs key exchange with the CXL switch and enables CXL IDE. In parallel, CXL switch will enumerate downstream devices and then perform key exchange with those downstream devices that support CXL IDE. The Switch then programs the keys into the respective Downstream Ports of the switch and enables CXL IDE. Host may obtain a report from the CXL switch regarding the enabling of CXL IDE for downstream devices, which includes information about the public key that was used to attest to the device EP. Host may directly obtain an attestation from the device Endpoint and confirm that the Endpoint in question has the same public key that the Switch used as part of the key exchange.

**Model C**

<span id="page-914-1"></span>An out-of-band agent may configure keys into the host, switch, and devices via outof-band means and then directly enable CXL IDE.

### <span id="page-914-0"></span>11.3.10 IDE Termination Handshake

This section describes a mechanism that disables IDE on both the transmitter and receiver. This is accomplished via IDE.Stop control flit (see [Table 4-20](#page-256-1)). This optional capability for 256B Flit mode simplifies the software synchronization and quiescing requirements. This ensures that the transmitter and receiver disable CXL.cachemem IDE in a coordinated manner.

After IDE is enabled and functional, receipt of a CXL\_K\_SET\_STOP request shall cause each transmitter on each IDE.Stop capable port to trigger the transmission of an IDE.Stop Link Layer Control flit (see [Table 4-20](#page-256-1)) if enabled by programming CXL IDE Control register (see [Section 8.2.4.22.2](#page-578-0)). The transmitter shall ensure that the currently active MAC epoch is terminated using an IDE.TMAC prior to sending an IDE.Stop message with no intervening protocol flits. IDE.TMAC sent before IDE.Stop shall follow the standard rules for early MAC termination defined in [Section 11.3.6](#page-909-0). If a valid TMAC sequence is not received before IDE.Stop, the IDE.Stop shall be dropped and Unexpected IDE.Stop received bit in the CXL IDE Error Status register (see [Section 8.2.4.22.4\)](#page-579-1) shall be set.

After the IDE.Stop is sent, all future protocol flits shall not be IDE protected. To allow the receiver to cleanly clear any pending IDE states, including precomputed information, the transmitter is required to send IDE.Idle flits, as defined in [Table 4-10,](#page-214-1) for the number of flits specified by the Tx Key Refresh Time field in the Key Refresh Time Control register (see [Section 8.2.4.22.7](#page-580-3)) prior to sending any protocol flits without IDE protection.

After receiving an IDE.Stop flit, the receiver must complete all pending actions for the currently active MAC epoch prior to disabling IDE.

Any IDE.Stop message that is received prior to a successful CXL\_K\_SET\_STOP shall be dropped and the Unexpected IDE.Stop received bit in the CXL IDE Error Status register (see [Section 8.2.4.22.4\)](#page-579-1) shall be set.

If the IDE.Stop is received by a receiver that is IDE.Stop Capable but is not configured to process IDE.Stop, it shall drop the IDE.Stop flit and the Unexpected IDE.Stop received bit in the CXL IDE Error Status register (see [Section 8.2.4.22.4](#page-579-1)) shall be set. If the Rx port receives an IDE.Stop while the IDE stream is inactive, the Rx port shall drop the IDE.Stop flit and set the Unexpected IDE.Stop received bit in the CXL IDE Error Status register (see [Section 8.2.4.22.4](#page-579-1)).

### <span id="page-915-0"></span>11.3.11 Poison handling

The CXL.cachemem protocol has two mechanisms for conveying poison:

- Use the poison bit in the headers that have poisoned data associated with them (see the poison bit in the CXL.cache D2H Data Header, H2D Request and the CXL.mem flit definitions).
- Utilize 256 byte flits with the LLCTRL message with Subtype Poison. This message can be carried in an H slot for standard flits and in an H or HS slot for LOpt flits (see the link layer Late Poison description in section 4.3.6.3 ). The LLCTRL message includes a payload encoding that indicates the data message offset where the poison applies. Since multiple data messages can be outstanding at the same time, there can be multiple in-band LLCTRL Poison messages outstanding at the same time.

In general, IDE does not apply to LLCTRL messages. However, the Poison message needs to have integrity protection by CXL.cachemem IDE. Otherwise, an adversary can inject/delete an in-band LLCTRL Poison message without detection by IDE. Injection of a LLCTRL Poison message is not a concern as it only impacts the availability of the TCB (which an adversary has many other simpler ways to achieve). However, deleting or modifying an in-band LLCTRL Poison message is problematic as it can lead to silent consumption of data that should have been poisoned.

When LLCTRL Poison is present in the H slot of a flit, the payload information of the message shall be treated as additional bits of AAD. There are 4 bits of payload defined in the specification. Each LLCTRL Poison message shall result in 32 bits of AAD (4 bits of payload along with 28 bits of padding). The remaining slots of the flit carrying the poison indication shall be considered reserved and those slots shall not be encrypted, or integrity protected. This AAD value shall be treated as additional AAD for the next protocol flit. Thus, the flit carrying LLCTRL Poison in the H slot does not count towards MAC Epoch (see [Figure 11-22](#page-916-0) & [Figure 11-23](#page-916-1) below). The MAC Epoch is still defined based on the protocol flits. Since the poison payload is incorporated into the integrity calculations as AAD, it can be authenticated without impacting IDE encryption.

<span id="page-916-0"></span>**Figure 11-22. Containment Mode example illustrating the AAD construction for the case of two protocol flits that are part of the current MAC Epoch with an in-band LLCTRL Poison sent prior to first flit of the MAC Epoch**

![](_page_916_Figure_3.jpeg)

<span id="page-916-1"></span>**Figure 11-23. Containment Mode example illustrating the AAD construction for the case of two protocol flits that are part of the current MAC Epoch with an in-band LLCTRL Poison message sent after first flit of the MAC Epoch**

![](_page_916_Figure_5.jpeg)

When a LLCTRL Poison message is present in an HS slot of a flit, and the rest of the flit already contains valid protocol information, then there is no change required to the current IDE definition as the HS slot is already authenticated.

#### <span id="page-917-0"></span>11.3.11.1 Late poison with CRC corruption flow

There is a variant of late poison in the case where all of the data that needs to be poisoned is packed into the current flit (see the link layer Late Poison description in [Section 4.3.6.3](#page-258-3)). In this case, the CRC of the flit is corrupted before transmission. This ensures a retry condition will be triggered. When the retry request is received, the LLCTRL Poison message is sent first, followed by the original flit, without CRC corruption. The approach described previously will work with the late poison flow for standard flits and LOpt flits where the CRC of the first half of the flit is corrupted and the LLCTRL Poison message is carried in the H slot of the flit. The transmitter shall ensure that the original flit with the corrupted CRC, the LLCTRL Poison flit, and the original flit with good CRC are sent sequentially, with no intervening protocol flits. The transmitter shall also ensure that the MAC for the current MAC Epoch that includes the CRC corrupted flit is not transmitted ahead of the CRC corruption flow, as the MAC will need to be recomputed to include the AAD values from the LLCRTL Poison payload.

As noted in Viral Injection and Containment (see [Section 4.3.6.2\)](#page-257-3), IDE cannot be supported with the LOpt flit with CRC corruption of the second half of the flit. When IDE is enabled, any error containment shall be either detected sufficiently early enough to corrupt the CRC of the first half of flit or must be injected as an HS slot LLCTRL Poison message without needing to corrupt the CRC of the second half of the flit.

#### <span id="page-917-1"></span>11.3.11.2 Support of authenticated LLCTRL Poison messages

Devices supporting the inclusion of the LLCTRL Poison message in the AAD shall declare support by setting the IDE Protect LLCTRL Poison Message Capable bit in the CXL IDE Capability register. Hosts wishing to enable this feature on the device shall set the IDE Protect LLCTRL Poison Message Enable bit in the CXL IDE Control register.

## <span id="page-917-2"></span>11.4 CXL.cachemem IDE Key Management (CXL\_IDE\_KM)

System software or system firmware may follow this specification to configure the ports at both ends of a CXL link that have matching CXL.cachemem IDE keys, Initial *IV*, and other settings, in an interoperable way. The software or firmware entity that performs this activity is referred to as CXL.cachemem IDE Key Management Agent (CIKMA).

The port pairs, also called the partner ports, may consist of the following:

- A CXL RP and a CXL USP
- A CXL RP and a CXL EP
- A CXL DSP and a CXL EP

CXL root port CXL.cachemem IDE key programming may be performed via host-specific method and may not use the programming steps described in this section.

The CXL.cachemem IDE Establishment flow consists of three major steps:

- 1. CIKMA reads CXL IDE capability registers on both ends of the CXL link and configures various CXL.cachemem IDE control registers on both ends of the CXL link. See [Section 8.2.4.21](#page-576-5) for definition of these registers and the programming guidelines.
- 2. CIKMA sets up an SPDM secure session with each of the partner ports that are being set up. This is accomplished by issuing SPDM key exchange messages over transports such as PCIe DOE or MCTP. If one of the partner ports is an RP and the RP supports a proprietary IDE programming flow, an SPDM secure session with RP may not be needed.
- 3. CIKMA queries port capabilities, optionally obtains locally generated key and *IV* from each port if they are capable, configures CXL.cachemem IDE Rx/Tx keys/*IV*, and enables CXL.cachemem IDE using CXL\_IDE\_KM messages that are defined in

[Section 11.4.1.](#page-918-0) These messages are secured using the SPDM session key that was established by CIKMA via the previous step.

<span id="page-918-1"></span>**Figure 11-24. Various Interface Standards that are Referenced by this Specification and their Lineage**

![](_page_918_Figure_4.jpeg)

### <span id="page-918-0"></span>11.4.1 CXL\_IDE\_KM Protocol Overview

<span id="page-918-2"></span>CXL\_IDE\_KM Messages are constructed as SPDM vendor-defined requests and SPDM vendor-defined responses. All request messages begin with a standard Request Header (see [Table 11-2](#page-920-1)) and all response messages carry a standard Response Header (see [Table 11-3\)](#page-920-2). For the definition of individual fields in the Request and Response Header, please refer to DSP0274. Unless specified otherwise, the behaviors specified in DSP0236, DSP0237, DSP0238, DSP0274, DSP0275, DSP0276, DSP0277, and PCIe Base Specification apply.

CXL\_IDE\_KM Messages shall be confidentiality and integrity protected in accordance with DSP0277. These secured messages may be sent over a variety of transports, including Secured CMA/SPDM Messages over DOE (see PCIe Base Specification) or Secured Messages over MCTP (see DSP0276).

All CXL.cachemem IDE-capable CXL Switches and Endpoints shall support CMA/SPDM and Secured CMA/SPDM Data Object types over PCIe DOE mailbox. The specific rules regarding the placement of the DOE mailbox are governed by PCIe Base Specification. These data object types are defined in PCIe Base Specification. All CXL.cachemem IDEcapable switches and devices shall support CXL\_IDE\_KM protocol and CXL\_IDE\_KM being sent as Secured CMA/SPDM Data Objects.

CXL.cachemem IDE-capable switches and devices may optionally support CXL\_IDE\_KM messages over MCTP.

The maximum amount of time that the Responder has to provide a response to a CXL\_IDE\_KM request is 1 second. The requester shall wait for 1 second plus the transport-specific, round-trip transport delay prior to concluding that the request resulted in an error.

### <span id="page-919-0"></span>11.4.2 Secure Messaging Layer Rules

<span id="page-919-1"></span>CXL\_IDE\_KM messages shall not be issued before an SPDM secure session has been established between the two ports. Any CXL\_IDE\_KM messages that are not secured shall be silently dropped by the receiver. The first CXL\_IDE\_KM request message after the SPDM secure session setup shall be CXL\_QUERY.

After a successful response to CXL\_QUERY, this SPDM session may be used to establish a CXL.cachemem IDE Stream. While this SPDM Session is in progress, any CXL\_IDE\_KM messages received using a different Session ID shall be silently dropped and shall not generate a CXL\_IDE\_KM response. Any CXL\_IDE\_KM messages that fail integrity check shall be silently dropped and shall not generate a CXL\_IDE\_KM response. The act of terminating this SPDM Session or establishment of a different SPDM Secure session by themselves shall not affect the state of the CXL.cachemem IDE stream.

If SPDM Session S1 is used to establish a CXL.cachemem IDE Stream I1, termination of SPDM Session S1 followed by receipt of any valid CXL\_IDE\_KM message with a new Session S2 shall transition CXL.cachemem IDE Stream I1 to Insecure State. The transition shall occur prior to processing the newly received CXL\_IDE\_KM message unless the receiver can ensure, via mechanisms not defined here, that S1 and S2 were set up by the same entity; otherwise, the receiver drops the CXL\_IDE\_KM message with a new Session S2. If the CXL.cachemem IDE stream enters Insecure State due to this condition, the receiver shall set the Rx Error Status field in the CXL IDE Error Status register (see [Section 8.2.4.22.4](#page-579-1)) to CXL.cachemem IDE Establishment Security error.

It is permitted for a single DOE mailbox instance be used to service CXL\_IDE\_KM messages as well as CXL.io IDE\_KM messages. It is permitted for a single SPDM session be used to set up CXL.io IDE stream as well as CXL.cachemem IDE stream with a component. The operation and the establishment of CXL.cachemem IDE stream is independent of the operation and establishment of CXL.io IDE stream. It is permitted for a component to support CXL.io IDE but not CXL.cachemem IDE, and vice versa. If a component supports both CXL.io IDE and CXL.cachemem IDE, it may be operated in a mode where only one of the two is active. It is permitted for CXL\_IDE\_KM messages to be interleaved with IDE\_KM messages. CIKMA shall ensure there is at most one outstanding SPDM request of any kind at any time in accordance with DSP0274.

### <span id="page-920-0"></span>11.4.3 CXL\_IDE\_KM Common Data Structures

For consistency and reuse reasons, the names of the individual messages follow PCIe Base Specification except for the addition of the prefix CXL, and the message contents closely match PCIe Base Specification.

Unless specified otherwise, all fields are defined as little-endian.

Please refer to DSP0274 for definitions of the fields in the CXL\_IDE\_KM Request header and Response header.

<span id="page-920-1"></span>**Table 11-2. CXL\_IDE\_KM Request Header**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                          |
|-------------|--------------------|--------------------------------------------------------------------------------------------------------------------------------------|
| 0h          | 1                  | SPDMVersion                                                                                                                          |
| 1h          | 1                  | RequestResponseCode: Value is 0FEh (VENDOR_DEFINED_REQUEST).                                                                         |
| 2h          | 1                  | Reserved                                                                                                                             |
| 3h          | 1                  | Reserved                                                                                                                             |
| 4h          | 2                  | StandardsID: Value is 03h (PCI-SIG), indicating that the Vendor ID is assigned by the PCI-SIG.                                       |
| 6h          | 1                  | Length of Vendor ID: Value is 02h.                                                                                                   |
| 7h          | 2                  | Vendor ID: Value is 1E98h (CXL).                                                                                                     |
| 9h          | 2                  | Request Length: The number of bytes in the message that follow this field. Varies based on the<br>operation that is being requested. |

<span id="page-920-2"></span>**Table 11-3. CXL\_IDE\_KM Successful Response Header**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                      |
|-------------|--------------------|----------------------------------------------------------------------------------------------------------------------------------|
| 0h          | 1                  | SPDMVersion                                                                                                                      |
| 1h          | 1                  | RequestResponseCode: Value is 07Eh (VENDOR_DEFINED_RESPONSE).                                                                    |
| 2h          | 1                  | Reserved                                                                                                                         |
| 3h          | 1                  | Reserved                                                                                                                         |
| 4h          | 2                  | StandardsID: Value is 03h (PCI-SIG), indicating that the Vendor ID is assigned by the PCI-SIG.                                   |
| 6h          | 1                  | Length of Vendor ID: Value is 02h.                                                                                               |
| 7h          | 2                  | Vendor ID: Value is 1E98h (CXL).                                                                                                 |
| 9h          | 2                  | Response Length: The number of bytes in the message that follow this field. Varies based on<br>the operation that was requested. |

[Table 11-4](#page-920-3) lists the various generic error conditions that a responder may encounter during the processing of CXL\_IDE\_KM messages and how the conditions are handled.

<span id="page-920-3"></span>**Table 11-4. CXL\_IDE\_KM Generic Error Conditions**

| Error Condition                                                                      | Response                                                      | Effect on an<br>Active CXL.cachemem IDE Stream |  |
|--------------------------------------------------------------------------------------|---------------------------------------------------------------|------------------------------------------------|--|
| CXL_IDE_KM message carries an Object<br>ID that is not defined in this specification | No response is generated. The request is<br>silently dropped. | No change                                      |  |
| Unrecognized SPDM major version                                                      |                                                               |                                                |  |

### <span id="page-921-0"></span>11.4.4 Discovery Messages

The CXL\_QUERY request is used to discover the CXL.cachemem IDE capabilities and the current configuration of a port. The port supplies this information in the form of CXL\_QUERY\_RESP response. CIKMA shall not issue another type of CXL\_IDE\_KM request after CXL\_QUERY until CIKMA has received a successful CXL\_QUERY\_RESP response. If CXL\_QUERY request is not successful, CIKMA is permitted to retry it.

CIKMA may cross-check the CXL IDE Capability Structure contents that are returned by CXL\_QUERY\_RESP against the component's CXL IDE Capability Structure register values. CIKMA shall abort the CXL.cachemem IDE Establishment flow if CIKMA detects a mismatch.

<span id="page-921-1"></span>**Table 11-5. CXL\_QUERY Request**

| Byte Offset | Length<br>in Bytes | Description                                          |
|-------------|--------------------|------------------------------------------------------|
| 0h          | Bh                 | Standard Request Header: See Table 11-2.             |
| Bh          | 1                  | Protocol ID: Value is 0.                             |
| Ch          | 1                  | Object ID: Value is 0, indicating CXL_QUERY request. |
| Dh          | 1                  | Reserved                                             |
| Eh          | 1                  | PortIndex: See PCIe Base Specification.              |

[Table 11-6](#page-921-2) lists the various error conditions that a responder may encounter that are unique to CXL\_QUERY and how the conditions are handled.

<span id="page-921-2"></span>**Table 11-6. CXL\_QUERY Processing Errors**

| Error Condition                               | Response                                                      | Effect on an<br>Active CXL.cachemem IDE Stream |  |
|-----------------------------------------------|---------------------------------------------------------------|------------------------------------------------|--|
| Protocol ID is nonzero                        | No response is generated. The<br>request is silently dropped. |                                                |  |
| Invalid Request Length                        |                                                               | No change                                      |  |
| PortIndex does not correspond to a valid port |                                                               |                                                |  |

<span id="page-921-3"></span>**Table 11-7. Successful CXL\_QUERY\_RESP Response (Sheet 1 of 2)**

| Byte Offset | Length<br>in Bytes | Description                                           |
|-------------|--------------------|-------------------------------------------------------|
| 00h         | Bh                 | Standard Response Header: See Table 11-3.             |
| 0Bh         | 1                  | Protocol ID: Value is 0.                              |
| 0Ch         | 1                  | Object ID: Value is 1, indicating CXL_QUERY response. |
| 0Dh         | 1                  | Reserved                                              |
| 0Eh         | 1                  | PortIndex: See PCIe Base Specification.               |
| 0Fh         | 1                  | Dev/Fun Number: See PCIe Base Specification.          |
| 10h         | 1                  | Bus Number: See PCIe Base Specification.              |
| 11h         | 1                  | Segment: See PCIe Base Specification.                 |
| 12h         | 1                  | MaxPortIndex: See PCIe Base Specification.            |

**Table 11-7. Successful CXL\_QUERY\_RESP Response (Sheet 2 of 2)**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
|-------------|--------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 13h         | 1                  | •<br>Bits[3:0]: CXL IDE Capability Version: Must be set to 1. See Section 8.2.4.7.<br>•<br>Bit[4]: CXL.cachemem IV Generation Capable:<br>— 0 = Port is not capable of locally generating the 96-bit IV and shall always use the<br>default IV construction.<br>— 1 = Port is capable of locally generating the 96-bit IV. If a CXL_KEY_PROG message<br>indicates Use Default IV=0, the port shall use the Locally generated CXL.cachemem<br>IV in the Tx path and shall use the IV value supplied as part of the CXL_KEY_PROG<br>message in the Rx path. The port shall return the Locally generated CXL.cachemem<br>IV as part of CXL_GETKEY_ACK response.<br>•<br>Bit[5]: CXL.cachemem IDE Key Generation Capable:<br>— 0 = Port is not capable of locally generating an IDE key.<br>— 1 = Port is capable of locally generating the IDE key, shall use that key in the Tx<br>path, and then return that key as part of the CXL_GETKEY_ACK response.<br>•<br>Bit[6]: CXL_K_SET_STOP Capable:<br>— 0 = Port does not support CXL_K_SET_STOP.<br>— 1 = Port supports CXL_K_SET_STOP.<br>•<br>Bit[7]: Reserved |
| 14h         | Varies             | CXL IDE Capability Structure: For CXL IDE Capability Version=1, the length shall be 20h.<br>Carries the contents of the CXL IDE Capability Structure of this port (see Section 8.2.4.21).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |

### <span id="page-922-0"></span>11.4.5 Key Programming Messages

Each CXL.cachemem IDE-capable port shall be capable of storing four keys - Rx active, Tx active, Rx pending, and Tx pending. If CXL.cachemem IDE is active, the Tx active key is used to encrypt the flits and generate the MAC. If CXL.cachemem IDE is active, the Rx active key is used to decrypt the flits and verify the MAC in the Rx direction. This specification does not define a mechanism for directly updating the active keys. A Conventional Reset shall reset the active CXL.cachemem IDE Stream and transition the stream to Insecure State. A CXL reset shall reset the active CXL.cachemem IDE Stream and transition the stream to Insecure State. Transition of the CXL.cachemem IDE session to Insecure State shall clear all the keys, make the keys unreadable, and then mark the keys as invalid. An FLR shall not affect an active CXL.cachemem IDE Stream or the CXL.cachemem IDE keys.

The CXL\_KEY\_PROG request is used to supply the pending keys. Offset 11h, Bit 1, is used to select between the Rx and the Tx. If CXL.cachemem IV Generation Capable=1, the CXL\_KEY\_PROG request may also be used to establish the Initial CXL.cachemem IDE IV value to be used with the new IDE session including the rekeying flow.

If both ports (Port1 and Port2) return CXL.cachemem IV Generation Capable=1 in QUERY\_RSP, it is recommended that CIKMA issue a CXL\_GETKEY request to both ports and obtain Locally generated CXL.cachemem IV values. When issuing a CXL\_KEY\_PROG message to Port1 Rx and Port2 Tx, CIKMA should initialize the Initial CXL.cachemem IDE IV field (Offset 13h+KSIZE) to match the Port2 Locally generated CXL.cachemem IV and set Default IV=0. When issuing a CXL\_KEY\_PROG message to Port1 Tx and Port2 Rx, CIKMA should initialize the Initial CXL.cachemem IDE IV field (Offset 13h+KSIZE) to match the Port1 Locally generated CXL.cachemem IV and set Default IV=0.

If either port returns CXL.cachemem IV Generation Capable=0 in QUERY\_RSP, CIKMA should set Use Default IV=1 in the CXL\_KEY\_PROG messages to both ports to indicate that the ports should use the default *IV* construction in Rx directions and Tx directions.

If Port1 and Port2 are partner ports and if Port1 returns CXL.cachemem IDE Key Generation Capable=1 in QUERY\_RSP, it is recommended that CIKMA issue a CXL\_GETKEY request to Port1 and obtain its Locally generated CXL.cachemem IDE Key. When issuing the CXL\_KEY\_PROG message to Port1 Tx and Port2 Rx, CIKMA should initialize the CXL.cachemem IDE Key field to match the Port1 Locally generated CXL.cachemem IDE Key. If Port2 returns CXL.cachemem IDE Key Generation

Capable=1 in QUERY\_RSP, it is recommended that CIKMA issue a CXL\_GETKEY request to Port2 and obtain its Locally generated CXL.cachemem IDE Key. When issuing a CXL\_KEY\_PROG message to Port2 Tx and Port1 Rx, CIKMA should initialize the CXL.cachemem IDE Key field to match the Port2 Locally generated CXL.cachemem IDE Key. The port is expected to return a different IDE key during every CXL\_GETKEY\_ACK response. Therefore, CIKMA should ensure that the CXL.cachemem IDE Key supplied during a CXL\_KEY\_PROG request matches the locally generated CXL.cachemem IDE Key from the previous CXL\_GETKEY\_ACK responses from that port.

<span id="page-923-0"></span>**Table 11-8. CXL\_KEY\_PROG Request**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                               |
|-------------|--------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 00h         | Bh                 | Standard Request Header: See Table 11-2.                                                                                                                                                                                                                                                                                  |
| 0Bh         | 1                  | Protocol ID: Value is 0.                                                                                                                                                                                                                                                                                                  |
| 0Ch         | 1                  | Object ID: Value is 2, indicating CXL_KEY_PROG request.                                                                                                                                                                                                                                                                   |
| 0Dh         | 2                  | Reserved                                                                                                                                                                                                                                                                                                                  |
| 0Fh         | 1                  | Stream ID: Value is 0.                                                                                                                                                                                                                                                                                                    |
| 10h         | 1                  | Reserved                                                                                                                                                                                                                                                                                                                  |
| 11h         | 1                  | •<br>Bit[0]: Reserved<br>•<br>Bit[1]: RxTxB:<br>— 0 = Rx<br>— 1 = Tx<br>•<br>Bit[2]: Reserved<br>•<br>Bit[3]: Use Default IV:<br>— 0 = Port shall use the Initial IV specified at Offset 13h+KSIZE<br>— 1 = Port shall use the Default IV construction<br>•<br>Bits[7:4]: Key Sub-stream: Value is 1000b.                 |
| 12h         | 1                  | PortIndex: See PCIe Base Specification.                                                                                                                                                                                                                                                                                   |
| 13h         | KSIZE              | CXL.cachemem IDE Key: Program the Pending Key with this value. KSIZE must be 32 for<br>this version of the specification. For layout, see PCIe Base Specification.                                                                                                                                                        |
| 13h+KSIZE   | 12h                | Initial CXL.cachemem IDE IV: Overwrites the Pending Initial IV.<br>This field must be ignored if Use Default IV=1.<br>Byte Offsets 16h+KSIZE:13h+KSIZE carry the IV DWORD, IV[95:64].<br>Byte Offsets 20h+KSIZE:17h+KSIZE carry the IV DWORD, IV[63:32].<br>Byte Offsets 24h+KSIZE:21+KSIZE carry the IV DWORD, IV[31:0]. |

[Table 11-9](#page-924-0) lists the various error conditions that a responder may encounter that are unique to CXL\_KEY\_PROG and how the conditions are handled. When these conditions are detected, the responder shall respond with a CXL\_KP\_ACK and set the Status field to a nonzero value.

<span id="page-924-0"></span>**Table 11-9. CXL\_KEY\_PROG Processing Errors**

| Error Condition                                                                                                                                                                                                                                                         | Response                                                               | Effect on an Active<br>CXL.cachemem IDE Stream |
|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------|------------------------------------------------|
| Invalid Request Length                                                                                                                                                                                                                                                  |                                                                        |                                                |
| PortIndex does not correspond to a valid port                                                                                                                                                                                                                           |                                                                        | No change                                      |
| Protocol ID is nonzero                                                                                                                                                                                                                                                  |                                                                        |                                                |
| Stream ID is nonzero                                                                                                                                                                                                                                                    |                                                                        |                                                |
| Key Sub-stream is not 1000b                                                                                                                                                                                                                                             |                                                                        |                                                |
| CXL_KEY_PROG received prior to CXL_QUERY                                                                                                                                                                                                                                |                                                                        |                                                |
| Request to set the Tx Key, but the input Tx key is identical<br>to the current Rx Pending Key. This check is optional.                                                                                                                                                  |                                                                        |                                                |
| Request to set the Rx Key, but the input Rx key is identical<br>to the current Tx Pending Key. This check is optional.                                                                                                                                                  | Do not update the key and IV.<br>Return CXL_KP_ACK with<br>Status=01h. |                                                |
| Request to program the key failed because the pending key<br>slot has a valid key                                                                                                                                                                                       |                                                                        |                                                |
| Request to update Tx key, but the supplied key does not<br>match the locally generated CXL.cachemem IDE key<br>returned during the last CXL_GETKEY_ACK response.                                                                                                        |                                                                        |                                                |
| Request to update Tx IV, but the supplied IV does not<br>match the Locally generated CXL.cachemem IV returned<br>during the last CXL_GETKEY_ACK response.<br>The port returned IV Generation Capable=0 in QUERY_RSP,<br>but Use Default IV in CXL_KEY_PROG was not set. |                                                                        |                                                |

Upon successful processing of CXL\_KEY\_PROG, the responder shall acknowledge by sending the CXL\_KP\_ACK response with Status=0. The nonzero Status values not listed here are reserved by this specification but should be interpreted as an error condition by the requester.

<span id="page-924-1"></span>**Table 11-10. CXL\_KP\_ACK Response**

| Byte Offset | Length in<br>Bytes | Description                                                                                                                                            |  |
|-------------|--------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|--|
| 00h         | Bh                 | Standard Response Header: See Table 11-3.                                                                                                              |  |
| 0Bh         | 1                  | Protocol ID: Value is 0.                                                                                                                               |  |
| 0Ch         | 1                  | Object ID: Value is 3, indicating CXL_KP_ACK response.                                                                                                 |  |
| 0Dh         | 2                  | Reserved                                                                                                                                               |  |
| 0Fh         | 1                  | Stream ID: Value is 0.                                                                                                                                 |  |
| 10h         | 1                  | Status: See Table 11-9.                                                                                                                                |  |
| 11h         | 1                  | •<br>Bit[0]: Reserved<br>•<br>Bit[1]: RxTxB: See PCIe Base Specification<br>•<br>Bits[3:2]: Reserved<br>•<br>Bits[7:4]: Key Sub-stream: Value is 1000b |  |
| 12h         | 1                  | PortIndex: See PCIe Base Specification.                                                                                                                |  |

### <span id="page-925-0"></span>11.4.6 Activation/Key Refresh Messages

<span id="page-925-1"></span>The CXL\_K\_SET\_GO request is used to prepare an Rx port for a CXL.cachemem IDE Stream. The port shall respond with a CXL\_K\_GOSTOP\_ACK message to indicate that the port is ready.

The CXL\_K\_SET\_GO request is also used to instruct a Tx port to generate an IDE.Start Link Layer Control flit and to start a CXL.cachemem IDE Stream that is protected with the pending Tx key as outlined in [Section 11.3.7](#page-912-0). As part of successful CXL\_K\_SET\_GO processing, the Tx port shall copy the pending key to be the active key and mark the pending key slot as invalid. If CXL.cachemem IV Generation Capable=1 and the last CXL\_KEY\_PROG request indicated Use Default IV=0, the Initial CXL.cachemem IDE IV shall also be re-initialized to the value supplied as part of the CXL\_KEY\_PROG request. If CXL.cachemem IV Generation Capable=0 or the last CXL\_KEY\_PROG request indicated Use Default IV=1, Default *IV* construction shall be used. All subsequent protocol flits shall be protected by the new active key until the port enters Insecure State.

Upon receipt of an IDE.Start Link Layer Control flit, the Rx port shall copy the pending key to the active key slot and then mark the pending key slot as invalid. If CXL.cachemem IV Generation Capable=1 and the last CXL\_KEY\_PROG request indicated Use Default IV=0, the Initial CXL.cachemem IDE IV shall also be re-initialized to the value supplied as part of the CXL\_KEY\_PROG request. If CXL.cachemem IV Generation Capable=0 or the last CXL\_KEY\_PROG request indicated Use Default IV=1, Default *IV* construction shall be used. All subsequent protocol flits shall be protected by the new active key until the port enters Insecure State.

If the Rx port receives an IDE.Start Link Layer Control flit prior to a successful CXL\_KEY\_PROG since the last Conventional Reset, the Rx port shall drop the IDE.Start flit and then optionally set the Rx Error Status field in the CXL IDE Error Status register (see [Section 8.2.4.22.4\)](#page-579-1) to CXL.cachemem IDE Establishment Security error. If the Rx port receives an IDE.Start Link Layer Control flit while CXL.cachemem IDE is active, but prior to a successful CXL\_KEY\_PROG since the last IDE.Start, the Rx port shall either (1) drop the IDE.Start flit and then optionally program Rx Error Status=8h to CXL.cachemem IDE Establishment Security error or (2) set the Rx Error Status field in the CXL IDE Error Status register (see [Section 8.2.4.22.4](#page-579-1)) to CXL.cachemem IDE Establishment Security error and then transition to Insecure State.

If the Rx port receives an IDE.Start Link Layer Control flit prior to a successful CXL\_K\_SET\_GO since the last Conventional Reset, the Rx port shall drop the IDE.Start flit and then optionally set the Rx Error Status field in the CXL IDE Error Status register (see [Section 8.2.4.22.4\)](#page-579-1) to CXL.cachemem IDE Establishment Security error. If the Rx port receives an IDE.Start Link Layer Control flit while CXL.cachemem IDE is active, but prior to a successful CXL\_K\_SET\_GO since the last IDE.Start, the Rx port shall either (1) drop the IDE.Start flit and then optionally set the Rx Error Status field in the CXL IDE Error Status register (see [Section 8.2.4.22.4](#page-579-1)) to CXL.cachemem IDE Establishment Security error or (2) program Rx Error Status=8h to CXL.cachemem IDE Establishment Security error and then transition to Insecure State.

Offset 11h, Bit 1, is used to select between the Rx and Tx. Offset 11h, Bit 3, controls whether the CXL.cachemem IDE operates in Skid mode or Containment mode.

CIKMA should issue a CXL\_K\_SET\_GO request message to an Rx port and wait for success before issuing a CXL\_K\_SET\_GO request message to the partner Tx port.

<span id="page-926-0"></span>**Table 11-11. CXL\_K\_SET\_GO Request**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                    |  |
|-------------|--------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--|
| 00h         | Bh                 | Standard Request Header: See Table 11-2.                                                                                                                                                                                       |  |
| 0Bh         | 1                  | Protocol ID: Value is 0.                                                                                                                                                                                                       |  |
| 0Ch         | 1                  | Object ID: Value is 4, indicating CXL_K_SET_GO structure.                                                                                                                                                                      |  |
| 0Dh         | 2                  | Reserved                                                                                                                                                                                                                       |  |
| 0Fh         | 1                  | Stream ID: Value is 0.                                                                                                                                                                                                         |  |
| 10h         | 1                  | Reserved                                                                                                                                                                                                                       |  |
| 11h         | 1                  | •<br>Bit[0]: Reserved<br>•<br>Bit[1]: RxTxB: See PCIe Base Specification<br>•<br>Bit[2]: Reserved<br>•<br>Bit[3]: CXL IDE Mode:<br>— 0 = Skid mode<br>— 1 = Containment mode<br>•<br>Bits[7:4]: Key Sub-stream: Value is 1000b |  |
| 12h         | 1                  | PortIndex: See PCIe Base Specification.                                                                                                                                                                                        |  |

[Table 11-12](#page-926-1) lists the various error conditions that a responder may encounter that are unique to CXL\_K\_SET\_GO and how the conditions are handled.

<span id="page-926-1"></span>**Table 11-12. CXL\_K\_SET\_GO Error Conditions**

| Error Condition                                                                                                                                                        | Response                                                      | Effect on an<br>Active CXL.cachemem IDE Stream |
|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------|------------------------------------------------|
| Port receives CXL_K_SET_GO<br>request, and pending key is invalid                                                                                                      |                                                               |                                                |
| If a port receives CXL_K_SET_GO<br>request with an IDE mode that is<br>not supported                                                                                   |                                                               |                                                |
| If a port receives CXL_K_SET_GO<br>request while IDE is active and the<br>current IDE mode does not match<br>Byte Offset 11, bit 3, in the new<br>CXL_K_SET_GO request | No response is generated.<br>The request is silently dropped. | No change                                      |
| Protocol ID is nonzero                                                                                                                                                 |                                                               |                                                |
| Stream ID is nonzero                                                                                                                                                   |                                                               |                                                |
| Key Sub-stream is not 1000b                                                                                                                                            |                                                               |                                                |
| PortIndex does not correspond to a<br>valid port                                                                                                                       |                                                               |                                                |
| Invalid Request Length                                                                                                                                                 |                                                               |                                                |

When a port receives a valid CXL\_K\_SET\_STOP request, the port shall clear the active and pending CXL.cachemem IDE keys and then transition to IDE Insecure State. No errors shall be logged in the IDE Status register when an IDE stream is terminated in response to CXL\_K\_SET\_STOP because this is not an error condition. If both ports support the IDE.Stop message as advertised by the CXL IDE Capability register (see [Section 8.2.4.22.1\)](#page-577-2), CIKMA may enable IDE.Stop on both ends of the link by programming the CXL IDE Control register (see [Section 8.2.4.22.2](#page-578-0)). If IDE.Stop is enabled on both ends, it is unnecessary to quiesce the CXL.cache and CXL.mem traffic prior to issuing the CXL\_K\_SET\_STOP request. If IDE.Stop is enabled, CIKMA is required to issue a CXL\_K\_SET\_STOP to the Rx and then wait for an acknowledgment of CXL\_K\_SET\_STOP before issuing a CXL\_K\_SET\_STOP to the Tx. If IDE.Stop is not enabled, the Software is expected to quiesce the CXL.cache and CXL.mem traffic prior

to issuing a CXL\_K\_SET\_STOP request to a port that is actively participating in CXL.cachemem IDE to prevent spurious CXL.cachemem IDE errors. The port shall respond with a CXL\_K\_GOSTOP\_ACK message after the port has successfully processed a CXL\_K\_SET\_STOP request.

If the Rx port receives an IDE.Stop Link Layer Control flit while the CXL.cachemem IDE is active, but prior to a successful CXL\_K\_SET\_STOP since the last IDE.Start or any other CXL IDE Key Programming message, the Rx port shall drop the IDE.Stop flit, set the Unexpected IDE.Stop received bit in the CXL IDE Error Status register (see [Section 8.2.4.22.4\)](#page-579-1) but not transition to Insecure State.

<span id="page-927-0"></span>**Table 11-13. CXL\_K\_SET\_STOP Request**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                                            |  |
|-------------|--------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|--|
| 00h         | Bh                 | Standard Request Header: See Table 11-2.                                                                                                               |  |
| 0Bh         | 1                  | Protocol ID: Value is 0.                                                                                                                               |  |
| 0Ch         | 1                  | Object ID: Value is 5, indicating CXL_K_SET_STOP structure.                                                                                            |  |
| 0Dh         | 2                  | Reserved                                                                                                                                               |  |
| 0Fh         | 1                  | Stream ID: Value is 0.                                                                                                                                 |  |
| 10h         | 1                  | Reserved                                                                                                                                               |  |
| 11h         | 1                  | •<br>Bit[0]: Reserved<br>•<br>Bit[1]: RxTxB: See PCIe Base Specification<br>•<br>Bits[3:2]: Reserved<br>•<br>Bits[7:4]: Key Sub-stream: Value is 1000b |  |
| 12h         | 1                  | PortIndex: See PCIe Base Specification.                                                                                                                |  |

[Table 11-14](#page-927-1) lists the various error conditions that a responder may encounter that are unique to CXL\_K\_SET\_STOP and how the conditions are handled.

<span id="page-927-1"></span>**Table 11-14. CXL\_K\_SET\_STOP Error Conditions**

| Error Condition                                                    | Response                         | Effect on an<br>Active CXL.cachemem IDE Stream |  |
|--------------------------------------------------------------------|----------------------------------|------------------------------------------------|--|
| Port does not support CXL_K_SET_STOP<br>(CXL_K_SET_STOP Capable=0) |                                  | No change                                      |  |
| Protocol ID is nonzero                                             |                                  |                                                |  |
| Stream ID is nonzero                                               | No response is generated.        |                                                |  |
| Key Sub-stream is not 1000b                                        | The request is silently dropped. |                                                |  |
| PortIndex does not correspond to a valid port                      |                                  |                                                |  |
| Invalid Request Length                                             |                                  |                                                |  |

<span id="page-927-2"></span>**Table 11-15. CXL\_K\_GOSTOP\_ACK Response (Sheet 1 of 2)**

| Byte Offset | Length<br>in Bytes | Description                                                   |
|-------------|--------------------|---------------------------------------------------------------|
| 00h         | Bh                 | Standard Response Header: See Table 11-3.                     |
| 0Bh         | 1                  | Protocol ID: Value is 0.                                      |
| 0Ch         | 1                  | Object ID: Value is 6, indicating CXL_K_GOSTOP_ACK structure. |
| 0Dh         | 2                  | Reserved                                                      |
| 0Fh         | 1                  | Stream ID: Value is 0.                                        |

**Table 11-15. CXL\_K\_GOSTOP\_ACK Response (Sheet 2 of 2)**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                                            |  |
|-------------|--------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|--|
| 10h         | 1                  | Reserved                                                                                                                                               |  |
| 11h         | 1                  | •<br>Bit[0]: Reserved<br>•<br>Bit[1]: RxTxB: See PCIe Base Specification<br>•<br>Bits[3:2]: Reserved<br>•<br>Bits[7:4]: Key Sub-stream: Value is 1000b |  |
| 12h         | 1                  | PortIndex: See PCIe Base Specification.                                                                                                                |  |

### <span id="page-928-0"></span>11.4.7 Get Key Messages

If the QUERY\_RSP response message from the port indicates CXL.cachemem IDE Key Generation Capable=1 or CXL.cachemem IV Generation Capable=1, the port shall support the CXL\_GETKEY message.

The CXL\_GETKEY message is used to get the Locally generated CXL.cachemem IDE Key from the port and Locally generated CXL.cachemem IV.

<span id="page-928-1"></span>**Table 11-16. CXL\_GETKEY Request**

| Byte Offset | Length<br>in Bytes | Description                                                                |  |
|-------------|--------------------|----------------------------------------------------------------------------|--|
| 00h         | Bh                 | Standard Request Header: See Table 11-2.                                   |  |
| 0Bh         | 1                  | Protocol ID: Value is 0.                                                   |  |
| 0Ch         | 1                  | Object ID: Value is 7, indicating CXL_GETKEY request.                      |  |
| 0Dh         | 2                  | Reserved                                                                   |  |
| 0Fh         | 1                  | Stream ID: Value is 0.                                                     |  |
| 10h         | 1                  | Reserved                                                                   |  |
| 11h         | 1                  | •<br>Bits[3:0]: Reserved<br>•<br>Bits[7:4]: Key Sub-stream: Value is 1000b |  |
| 12h         | 1                  | PortIndex: See PCIe Base Specification.                                    |  |

[Table 11-17](#page-928-2) lists the various error conditions that a responder may encounter that are unique to CXL\_GETKEY and how the conditions are handled.

<span id="page-928-2"></span>**Table 11-17. CXL\_GETKEY Processing Error**

| Error Description                             | Error Code                                                    | Effect on an<br>Active CXL.cachemem IDE Stream |  |
|-----------------------------------------------|---------------------------------------------------------------|------------------------------------------------|--|
| Invalid Request Length                        |                                                               |                                                |  |
| PortIndex does not correspond to a valid port |                                                               | No change                                      |  |
| Protocol ID is nonzero                        |                                                               |                                                |  |
| Stream ID is nonzero                          | No response is generated.<br>The request is silently dropped. |                                                |  |
| Key Sub-stream is not 1000b                   |                                                               |                                                |  |
| CXL_GETKEY received prior to CXL_QUERY        |                                                               |                                                |  |
| Port does not support CXL_GETKEY              |                                                               |                                                |  |

Upon successful processing of CXL\_GETKEY, the responder shall acknowledge by sending the CXL\_GETKEY\_ACK response.

<span id="page-929-1"></span>**Table 11-18. CXL\_GETKEY\_ACK Response**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                                                                              |  |
|-------------|--------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--|
| 00h         | Bh                 | Standard Response Header: See Table 11-3.                                                                                                                                                                                                                                                                                                                                |  |
| 0Bh         | 1                  | Protocol ID: Value is 0.                                                                                                                                                                                                                                                                                                                                                 |  |
| 0Ch         | 1                  | Object ID: Value is 8, indicating CXL_GETKEY_ACK response.                                                                                                                                                                                                                                                                                                               |  |
| 0Dh         | 2                  | Reserved                                                                                                                                                                                                                                                                                                                                                                 |  |
| 0Fh         | 1                  | Stream ID: Value is 0.                                                                                                                                                                                                                                                                                                                                                   |  |
| 10h         | 1                  | Reserved                                                                                                                                                                                                                                                                                                                                                                 |  |
| 11h         | 1                  | •<br>Bits[3:0]: Reserved<br>•<br>Bits[7:4]: Key Sub-stream: Value is 1000b                                                                                                                                                                                                                                                                                               |  |
| 12h         | 1                  | PortIndex: See PCIe Base Specification.                                                                                                                                                                                                                                                                                                                                  |  |
| 13h         | KSIZE              | Locally Generated CXL.cachemem IDE Key: The KSIZE must be 32 for this version of the<br>specification. For layout, see PCIe Base Specification. This field must be ignored if the<br>QUERY_RSP response message from the port indicates CXL.cachemem IDE Key Generation<br>Capable=0.                                                                                    |  |
| 13h+KSIZE   | 12                 | Locally Generated CXL.cachemem IV: This field must be ignored if the QUERY_RSP<br>response message from the port indicates CXL.cachemem IV Generation Capable=0.<br>Byte Offsets 16h+KSIZE:13h+KSIZE carry the IV DWORD, IV[95:64].<br>Byte Offsets 20h+KSIZE:17h+KSIZE carry the IV DWORD, IV[63:32].<br>Byte Offsets 24h+KSIZE:21h+KSIZE carry the IV DWORD, IV[31:0]. |  |

[Figure 11-25](#page-929-0) illustrates various key states and their transitions. Note that this figure is not meant to be exhaustive and does not include several legal transition arrows for simplicity.

<span id="page-929-0"></span>**Figure 11-25. Active and Pending Key State Transitions**

![](_page_929_Figure_7.jpeg)

> **IMPLEMENTATION NOTE**

**Establishing CXL.cachemem IDE between a DSP and EP - Example**

In this example, host software plays the role of the CIKMA. The switch implementation is such that the USP implements the DOE capability on behalf of all the DSPs and the specific DSP that is involved here is referenced as Port 4. Further, it is also assumed that the desired mode of operation is Skid mode. Host Software reads and configures the CXL IDE capability registers on the DSP and on the EP. See [Section 8.2.4.21](#page-576-5) for the definition of these registers and programming guidelines.

- 1. Host Software sets up independent SPDM secure sessions with the USP and the EP. This is accomplished by issuing SPDM key exchange messages over PCIe DOE.
- 2. All subsequent messages are secured as per DSP0277. The messages to/from the USP are secured using the SPDM session key established with the USP. The messages to/from the EP are secured using the session key established with the EP.
  - a. Host Software sends a CXL\_QUERY (PortIndex=4) message to the USP DOE mailbox. The USP returns a CXL\_QUERY\_RESP. Host Software compares the CXL\_QUERY\_RESP contents against the CXL IDE Capability structure associated with the DSP. Host Software exits with an error if there is a mismatch or a timeout. In this example, the USP reports that it supports Locally generated CXL.cachemem IV and Locally generated CXL.cachemem IDE Key.
  - b. Host Software sends a CXL\_QUERY (PortIndex=0) message to the EP DOE mailbox. The EP returns a CXL\_QUERY\_RESP. Host Software compares the CXL\_QUERY\_RESP contents against the CXL IDE Capability structure associated with the EP. Host Software exits with an error if there is a mismatch or a timeout. In this example, the EP reports that it supports Locally generated CXL.cachemem IV and Locally generated CXL.cachemem IDE Key.
  - c. Host Software issues a CXL\_GETKEY request to the USP and saves the Locally generated CXL.cachemem IDE Key from the response as KEY2 and the Locally generated CXL.cachemem IV from the response as IV2. Host Software issues CXL\_GETKEY request to the EP and saves the Locally generated a CXL.cachemem IDE Key from the response as KEY1 and the Locally generated Tx IV from the response as IV1.
  - d. Host Software programs the Rx pending key in the EP by sending a CXL\_KEY\_PROG(RxTxB=0, Use Default IV=0, KEY2, IV2) message to the EP DOE mailbox. Host Software programs the Tx pending keys in the DSP by sending a CXL\_KEY\_PROG(PortIndex=4, RxTxB=1, Use Default IV=0, KEY2, IV2) message to the USP DOE mailbox. Host Software programs the Rx pending keys in the DSP by sending a CXL\_KEY\_PROG(PortIndex=4, RxTxB=0, Use Default IV=0, KEY1, IV1) message to the USP DOE mailbox. Host Software programs the Tx pending key in the EP by sending a CXL\_KEY\_PROG(RxTxB=1, Use Default IV=0, KEY1, IV1) message to the EP DOE mailbox. These 4 steps can be performed in any order. Host Software exits with an error if the CXL\_KP\_ACK indicates an error or if there is a timeout.

> **IMPLEMENTATION NOTE**



- e. Host Software instructs DSP Rx to be ready by sending a CXL\_K\_SET\_GO(PortIndex=4, Skid mode, RxTxB=0) to the USP DOE mailbox. Host Software instructs the EP Rx to be ready by sending a CXL\_K\_SET\_GO(Skid mode, RxTxB=0) to the EP DOE mailbox. Host Software exits with an error if either CXL\_K\_SET\_GO request times out.
- f. Host Software instructs DSP Tx to enable CXL.cachemem IDE by sending a CXL\_K\_SET\_GO(PortIndex=4, Skid mode, RxTxB=1) to the USP DOE mailbox. DSP sends an IDE.Start Link Layer Control flit to EP and thus initiating IDE in one direction using KEY1 and Starting IV=IV1. Host Software exits with an error if the CXL\_K\_SET\_GO request times out.
- g. Host Software instructs EP Tx to enable CXL.cachemem IDE by sending a CXL\_K\_SET\_GO(Skid mode, RxTxB=1) to the EP DOE mailbox. EP sends an IDE.Start Link Layer Control flit to the DSP and thus initiates IDE in the other direction, using KEY2 and Starting IV=IV2. Host Software exits with an error if CXL\_K\_SET\_GO request times out.
- h. At the end of these steps, all the CXL.cachemem protocol flits traveling between the DSP and EP are protected by IDE.

If both ports support Locally generated CXL.cachemem IDE Key and Locally generated CXL.cachemem IV, the following sequence will result in a programming error and should be avoided:

- 1. CIKMA issues CXL\_GETKEY request to Port1 and saves the key, KEY1
- 2. CIKMA issues another CXL\_GETKEY request to Port1 and saves the *IV*, IV1
- 3. CIKMA issues CXL\_KEY\_PROG request to Port1 Tx and passes in KEY1 and IV1.
<span id="page-931-2"></span>- 4. Port1 returns a CXL\_KP\_ACK with Status=08h because the 2nd CXL\_GETKEY request changed its locally CXL.cachemem IDE generated key to KEY2, which is not equal to KEY1.

## <span id="page-931-0"></span>11.5 CXL Trusted Execution Environments Security Protocol (TSP)

### <span id="page-931-1"></span>11.5.1 Overview

Virtualization-based Trusted Execution Environments (TEE) are used to host confidential computing workloads that are isolated from hosting environments. This specification refers to such TEE as Trusted Execution Environment VMs (TVMs) to distinguish them from traditional virtual machines.

The PCI-SIG TEE Device Interface Security Protocol (TDISP) ECR specifies the architecture of a framework for trusted I/O virtualization to include PCIe devices within the TVM trust boundary. The CXL TEE Security Protocol (CXL-TSP), complements the PCI-SIG TDISP specification by specifying mechanisms to include direct attached CXL memory devices within the TVM trust boundary specifically for confidential computing scenarios.

### <span id="page-932-0"></span>11.5.2 Scope

This CXL security content scope focuses on features that are needed for confidential computing utilizing CXL Type 3 memory expander devices, referred to as targets in the TSP, directly connected to CXL Root Ports owned by the host which is an initiator in TSP. TSP defines the security objectives, capabilities, and interfaces, and the host, initiator, and target behaviors that are required to create a secure CXL memory hierarchy that meets the needs of confidential computing. The scope does not include details on initiator or target security implementation.

- This scope includes support for the following:
  - SPDM 1.2 or newer for authentication and attestation
  - Directly connected LDs, SLDs, and MH-SLDs
  - Dynamic Capacity devices
  - HDM-H memory
  - HDM-DB memory
  - 256B and PBR flit format
  - Memory pooling Multiple initiators accessing the same physical memory on a device but not sharing access to it
  - Comprehensive Trust security model
  - Selective Trust security model
  - Implicit 64B Cacheline TE State Access Control
  - Explicit TE State Access Control
- This scope does not include the following:
  - CXL switches
    - Devices connected via a CXL switch, including MLDs, GFDs
    - Direct P2P using CXL.mem
    - Direct P2P using UIO over CXL.io
  - Type 1 and Type 2 accesses to Type 3 HDM memory
  - HDM-D memory
  - 68B flit format
  - Memory sharing Multiple initiators accessing the same physical memory on a device and simultaneously sharing access to it

### <span id="page-932-1"></span>11.5.3 Threat Model

This version of TSP shall focus on providing confidential computing support for direct attached CXL memory. Direct attached memory shall be defined as using the CXL protocol to communicate with a memory device, or target and the CXL Root Ports of the host, without intermediaries in the middle of the two. Within the context of extending CXL for confidential computing, one of TSP's objectives is to minimize the Trusted Computing Base (TCB). The TSP supports both a selective trust and comprehensive trust security model.

#### <span id="page-932-2"></span>11.5.3.1 Definitions

The following additional terms are utilized in this threat model section:

- **Attacker**: Entity that wants to extract information from a communication or influence a computation by modifying information that flows between two participants.
- **Confidential Computing**: Confidential Computing protects Data in Use, Data in Transit and Data at Rest. Data at Rest applies to the CXL memory device and Data in Transit is applies to TSP Transport Security such as CXL IDE. Trusted Execution Environments (TEEs) prevent unauthorized access or modification of applications and data while in use, thereby increasing the security assurances for organizations that manage sensitive and regulated data.
- **Covert Channel**: Method for an accomplice inside a trusted entity to signal to an attacker outside a trusted entity.
- **Target**: Participant in the protocol that does not forward packets to other participants. The memory device.
- **Host**: Location in which multiple participants concurrently reside. The host is an initiator that contains CXL Root Ports.
- **Information**: Data or properties of the data exchanged between two participants that would allow the attacker to take or cause an adverse action. Examples include cryptographic keys, questions being considered, decisions of the TEE, results of a database query, etc.
- **Intermediary/switch**: Participant in the protocol that routes or forwards packets to targets. TSP initially focuses on direct attached confidential computing scenarios; thus, switch support in the threat model is beyond the scope of this specification.
- **Participant**: Initiator or target in a communication that utilizes a correct and error free implementation of the protocol.
- **Peer Device**: The peer device is an initiator that contains no CXL Root Ports.
- **Protocol Secrets**: Secrets that shall be protected, from users of the protocol and/ or attackers, to maintain the TEE.
- **Side Channel**: Ability of an attacker to extract information without the knowledge of the participating parties.
- **Trusted Execution Environment (TEE)**: Execution environment designed to provide secure separation between itself and any other computation. The environment may include or be extended to multiple devices.

#### <span id="page-933-0"></span>11.5.3.2 Assumptions

The threat model described below is based on the following assumptions:

- CXL does not guarantee that messages arrive in order. It requires initiator ordering. If the initiator has two messages that must be ordered, Message A and Message B, the initiator shall wait until Message A is acknowledged before submitting Message B.
- CXL relies on industry-standard secure protocols: SPDM and PCIe.
- CXL relies on industry-standard capabilities: Secure boot, trusted boot, and attestation.
- There are no errors in the implementation of the protocol, regardless of whether implemented in hardware, software, or firmware.
- An implementation of the protocol shall not disclose protocol secrets to an attacker. The participants shall have a secure location in which to store and/or retain this information.
- For confidential computing, everything inside the TEE shall not be observable by an attacker outside the TEE.

- When data is securely delivered to an attached target, the target shall protect that data from attacks. The TSP protocol facilitates multiple means of protecting the data. How the device implements such protections is beyond the scope of the threat model and TSP.
- There are non-overlapping resources for distinct hosts.
- Hardware in the host is trusted to maintain protocol separation between TEEs and keep TEEs isolated from one another.
- Hardware in the host is trusted to maintain protocol separation and isolation between Root Ports. Root Ports shall not accept incorrectly formatted transactions. If a host has a single port through which multiple sessions flow, the host hardware shall keep the sessions isolated and reliably deliver the transactions to the session owners, as defined by the hardware configuration.
- A correct implementation of the protocol. This means that the attacker cannot be inside the protocol.
- The protocol cannot defend against an attacker from within the TEE. Host hardware shall be responsible for defending the TEE from an attacker inside a host. An attacker in an initiator or target can use the protocol but is constrained by the requirements of this threat model.
- The target is directly connected to the host or peer device, either one acting as the initiator; thus, there are no attackers in the intermediaries in the TSP threat model. Targets connected via CXL switches have not been evaluated and the presence of switches are considered to be outside the threat model. Fabric-attached memory may require initiator-based memory encryption to keep the intermediaries out of the TCB and shall be addressed in a future version of the TSP.
- TEEs that require confidentiality of the information flowing between the initiator and the target, shall enable a CXL-approved Transport Security such as CXL IDE.
- A target can concurrently hold data for a computation for multiple initiators, resulting in data from multiple participants residing concurrently on the target. The target shall be responsible for keeping each initiator's data or computations separate and isolated. If the target has multiple ports, the target hardware shall keep the ports isolated and independent.
- If a target has a single port through which multiple sessions flow, the target hardware shall keep the sessions isolated and reliably deliver the transactions to their respective session owners, as defined by the hardware configuration. The target determines the threats from which initiator data is protected.
- Initiators and targets shall utilize an SPDM 1.2 or newer connection to authenticate and attest the target. For authenticated and trusted direct attached targets, multiple initiators can communicate with the same target without leaking information to other initiators.
- The protocol shall carry sufficient information to allow the target to maintain separation between initiators, Additionally, the protocol shall contain sufficient information to enable the target to enforce ciphertext hiding if needed.
- The protocol supports both initiator-based and target-based memory encryption so it shall carry sufficient information for the memory device to prevent access by non-TEEs to TEE memory.
- The protocol shall minimize the number of bits transmitted in the clear. These bits can be utilized as a covert channel if an application inside an initiator is compromised. PBR removes this exposure because all address bits can be encrypted; however, this is beyond the scope of the initial TSP.

#### <span id="page-935-0"></span>11.5.3.3 Threats and Mitigations

[Table 11-19](#page-935-3) outlines the security threats considered as part of the threat model and how the threat is mitigated.

<span id="page-935-3"></span>**Table 11-19. Security Threats and Mitigations**

| Primary Threat of Attacker                                                                 | Threat Mitigation                                                                                                                                                                                                                                                                                                                                                                                       |
|--------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Extract protocol secrets                                                                   | •<br>Transport Security such as CXL IDE<br>•<br>TSP initiator-based or target-based memory encryption                                                                                                                                                                                                                                                                                                   |
| Masquerade as a legitimate initiator or target                                             | •<br>SPDM attestation and authentication<br>•<br>SPDM mutual authentication                                                                                                                                                                                                                                                                                                                             |
| Insert itself between an initiator and target as a manipulator<br>in-the-middle            | •<br>Prevent physical attack<br>•<br>SPDM attestation and authentication<br>•<br>Transport Security such as CXL IDE                                                                                                                                                                                                                                                                                     |
| Derive actionable data or information from observed packets<br>(side channel)              | •<br>Minimize the number of address bits transmitted in the<br>clear (possibly 0)<br>•<br>Transport security such as CXL IDE                                                                                                                                                                                                                                                                            |
| Insert data and/or requests/responses into an initiator target<br>communication            | Transport Security such as CXL IDE                                                                                                                                                                                                                                                                                                                                                                      |
| Modify data and/or requests/responses exchanged in an<br>initiator target communication    | Transport Security such as CXL IDE                                                                                                                                                                                                                                                                                                                                                                      |
| Remove data and/or requests/responses from an initiator<br>target communication            | Transport Security such as CXL IDE                                                                                                                                                                                                                                                                                                                                                                      |
| Replay legitimate packets                                                                  | Transport Security such as CXL IDE                                                                                                                                                                                                                                                                                                                                                                      |
| A non-TEE reading or writing of TEE data                                                   | TSP TE State checking for access control                                                                                                                                                                                                                                                                                                                                                                |
| A TEE reading or writing unauthorized non-TEE data                                         | TEE is correctly configured to allow access only to memory for<br>which the TEE is authorized to access                                                                                                                                                                                                                                                                                                 |
| One TEE reading or writing another TEE's data                                              | •<br>TEE is correctly configured to allow access only to memory<br>for which the TEE is authorized to access<br>•<br>TSP initiator-based or target-based memory encryption to<br>protect each TEE's data from other TEEs                                                                                                                                                                                |
| A TEE on one host reading and/or writing resources that belong<br>to a TEE of another host | •<br>Hosts shall maintain separation and isolation between<br>TEEs<br>•<br>TSP initiator-based or target-based memory encryption                                                                                                                                                                                                                                                                        |
| A target on one port being able to send requests and/or<br>responses on another port       | Hardware within the host is trusted to maintain protocol<br>separation and isolation between RPs. RPs shall not accept<br>incorrectly formatted transactions. If a host has a single port<br>through which multiple sessions flow, the host hardware shall<br>keep the sessions isolated and reliably deliver the transactions<br>to the session owners, as defined by the hardware's<br>configuration. |

### <span id="page-935-1"></span>11.5.4 Reference Architecture

The reference architecture covers the security requirements and behaviors that are needed to support confidential computing use cases and covers the architectural scope, detecting TSP support, CMA/SPDM, attestation and authentication, memory encryption, transport security, access control, configuration, and Dynamic Capacity.

#### <span id="page-935-2"></span>11.5.4.1 Architectural Scope

[Figure 11-26](#page-936-2) outlines the major components that the TSP considers to be inside the TCB or outside the TCB, the different connections between the TEE-capable initiator and TEE-capable target memory device, and those connections that are specified by the TSP. Hosts are the only initiators defined for the original CXL 3.1 version of the TSP architecture for support of direct attached confidential computing in the TSP

architecture. With the addition of HDM-DB support to the TSP, CXL direct attached peer devices or accelerators are also considered initiators and may be utilized for confidential computing.

<span id="page-936-2"></span>**Figure 11-26. Reference Architecture**

![](_page_936_Figure_4.jpeg)

For implementations that utilize initiator-based memory encryption or target-based memory encryption, it is recommended to enable Transport Security (such as CXL IDE) as discussed in [Section 11.5.4.7](#page-951-0).

Securing CXL.io is optional from a TSP perspective.

#### <span id="page-936-0"></span>11.5.4.2 Determining TSP Support

For targets that support the TSP, the DVSEC CXL Capability register TSP Capable bit (see [Section 8.1.3.1\)](#page-502-1) shall be set by the target to indicate support for the TSP requests and responses detailed in the following sections. This bit also indicates to the initiator that the target supports the MemRdFill memory request which is required for deadlock prevention with partial writes and initiator-based encryption.

#### <span id="page-936-1"></span>11.5.4.3 CMA/SPDM

CMA/SPDM 1.2 or later secure sessions are utilized with CXL Vendor defined payloads for all TSP request and response payloads defined herein. The Protocol ID in the first byte of the Vendor Defined Payload identifies TSP requests independently from IDE or other requests that may also be defined by CXL. [Figure 11-27](#page-937-0) outlines the encapsulation of the TSP-defined payloads in a CMA/SPDM message, which is similar to those defined in the PCI-SIG TDISP, with the following changes to establish CXL control of the message interpretation:

- The DOE Data Object type shall report Vendor ID 0001h and Data Object Type 02h to point to Secured CMA/SPDM.
- The CMA/SPDM vendor defined message Standards ID shall utilize 0003h to indicate that PCI-SIG is the body that assigned the CMA/SPDM Message Vendor ID.

- The CMA/SPDM vendor defined message Vendor ID shall utilize 1E98h, indicating that the CXL Consortium assigned the interpretation of the CMA/SPDM vendor defined payload.
- The first byte in the CXL vendor defined payload is the Protocol ID. All CXL.cachemem IDE Key Management requests shall utilize Protocol ID = 00h. All TSP request and response messages shall utilize Protocol ID = 01h.

The encapsulation of TSP requests and responses inside an encrypted SPDM session is shown in [Figure 11-27.](#page-937-0)

<span id="page-937-0"></span>**Figure 11-27. CMA/SPDM, CXL IDE, and CXL TSP Message Relationship**

![](_page_937_Figure_6.jpeg)

CXL TSP messages shall not be issued before an SPDM secure session has been established between the initiator and the target. Any CXL TSP messages received by the target that are not secured shall be silently dropped by the target.

The Session ID that precedes the CMA/SPDM payload contains the TSP session utilized for each request or response payload. The TSP specification utilizes two types of sessions:

- **PrimarySession**: Required CMA/SPDM session that is established between the host and the target.
  - Utilized to configure and lock the target as defined by TSP.
  - For target-based memory encryption, this session may be utilized to set or clear memory encryption keys. The session utilized to set a key shall be the same session that is utilized to clear the same key.
  - PrimarySession is the CMA/SPDM session that is utilized to receive the Set Target Configuration Response request to an unlocked device. The target shall terminate any existing SecondarySession(s) anytime a new PrimarySession is established.
  - If a Transport Security (such as the CXL IDE IDE\_KM) session and TSP are required:
    - The PrimarySession shall be the same as the Transport Security session.
    - There shall be no ordering dependency between sending of Transport Security messages and CXL TSP messages. The Transport Security session may be established first and later the same session utilized as the PrimarySession or vice versa.
    - Once the SPDM session has been started, for any Transport Security messages received with a different session ID, the target shall silently drop the request and not generate a response.

- Once the SPDM session has been started, for any TSP messages received with a different SPDM session ID, the target shall drop the request and generate an Error Response of No Privilege.
- If the SPDM session has been terminated, any valid Transport Security message received with a different SPDM session ID shall cause the target to transition the CXL.cachemem IDE to Insecure State and transition the TSP state to ERROR.
- If the SPDM session has been terminated, any valid TSP message received with a different SPDM Session ID shall cause the target to transition the CXL.cachemem IDE to Insecure State and transition the TSP state to ERROR.
- Primary SPDM Session shall be utilized to provision PSK Key Material for establishing each Secondary SPDM Session(s)
- The acts of terminating the PrimarySession or establishing a different PrimarySession by themselves shall not affect the state of the TEE or TSP.
- Features that are enabled with Set Target Configuration to be allowed after the target is locked and require an SPDM session (e.g enabling Locked Target FW Update) shall utilize the PrimarySession.
- **SecondarySession(s)**: Optional CMA/SPDM sessions that are generated from the PrimarySession by utilizing CMA/SPDM PSK\_EXCHANGE between the host and the target.
  - For target-based memory encryption, this session may be utilized to set or clear memory encryption keys. Some host implementations may need to utilize a separate but related SPDM SecondarySession for setting and clearing memory keys independently from the PrimarySession that is utilized to configure and lock the configuration. The session utilized to set a key shall be the same session that is utilized to clear the same key.
  - Target advertises the number of SecondarySession(s) that it supports in Get Target Capabilities.
  - Initiator can configure the number of SecondarySession(s) to utilize and the type of TEE opcode checking each will use through Set Target Configuration.
  - PrimarySession is independent of these sessions. The termination or closing of any SecondarySession(s) shall have no effect on the PrimarySession.
  - These sessions are independent of the PrimarySession. Termination or closing of the PrimarySession shall have no effect on these sessions. However, if a new PrimarySession is started, the target shall terminate these sessions since new secondary sessions will need to be generated based on the new primary session key material.
  - CMA/SPDM session that successfully completes the CMA/SPDM PSK that utilizes the correct PSK hint shall be considered a valid SecondarySession.
  - The acts of terminating a SecondarySession or establishing a different SecondarySession by themselves shall not affect the state of the TEE or TSP.
  - Any TSP requests sent over a session that is not the PrimarySession or one of the SecondarySession(s) shall be failed with Error Response, No Privilege. See [Section 11.5.5.3, "Request Response and CMA/SPDM Sessions."](#page-970-0)

[Figure 11-28](#page-939-2) outlines the high-level sequence for creating the PrimarySession and how TMVSession PSK Key Material is utilized by the target to generate keys for a secure CMA/SPDM SecondarySession(s).

<span id="page-939-2"></span>**Figure 11-28. CMA/SPDM Sessions Creation Sequence**

![](_page_939_Figure_3.jpeg)

#### <span id="page-939-0"></span>11.5.4.4 Authentication and Attestation

<span id="page-939-3"></span>Because the TSP interface requires requests and responses to utilize a CMA/SPDM 1.2 (or later) secure session, target attestation and authentication is accomplished using the CMA/SPDM-defined secure session setup sequence.

#### <span id="page-939-1"></span>11.5.4.5 TE State Changes and Access Control

The TEE Exclusive State (TE State) of memory indicates whether the content of the memory is for TEE or non-TEE data.

Initiators that generate memory accesses shall determine the TEE status of each memory transaction, referred to as the TEE Intent. TEEs are permitted to access both exclusive and non-exclusive memory, while non-TEE entities are permitted to access only memory that is not intended for the exclusive use of a TEE.

Access control is outlined in the following sections and is defined as the verification of the TEE Intent against the TE State of the memory being accessed and the resulting target behavior when the verification fails. Access control is split in to Write Access Control and Read Access Control that can be supported by the target independently and enabled independently by the initiator.

Initiators shall not generate memory accesses with TEE Intent if those accesses do not arise within the execution context of a TEE. Initiators that generate memory accesses that originate within the execution context of a TEE shall understand the request's TEE Intent, based on the specific design of the TEE architecture, and shall express the correct TEE Intent. Because each request carries the correct TEE Intent, it is unnecessary for a request to indicate whether it originates from a TEE.

Initiators shall convey TEE Intent in a request by utilizing the TEE-specific M2S Req and M2S RwD opcodes specified in the CXL Transaction Layer. Targets shall convey the TE state by utilizing the S2M NDR and S2M DRS response opcodes specified in the CXL Transaction Layer. The specific opcodes utilized are specified in the tables provided later in this section.

Hosts that support implicit and explicit TE State changes:

- May enable either mechanism individually or both mechanisms at the same time on the target. When enabling implicit and explicit in-band TE State changes simultaneously, the TE State granularity utilized for explicit in-band TE State changes shall be 64B.
- Shall account for interleaving and send a single TE State change request to each target for a given interleave set.

Targets that have TE State changes enabled:

- Shall change the TE State of memory at a 64B cacheline granularity for implicit changes and at a 64B or greater granularity for explicit changes.
- Shall support explicit in-band TE State changes with a granularity of 64B when supporting implicit TE State changes
- Shall utilize implicit and/or explicit TE State changes as enabled by the host.
- Shall support the TEUpdate memory transaction when implicit or explicit in-band TE State changes are enabled.
- Shall return the current TE State saved for the memory location being accessed
- For memory reads that result in an uncorrectable error in the TE State storage specifically, the target shall treat the read as a TE State mismatch and behave as specified in the following sections. This behavior is independent of and in addition to handling of uncorrectable errors that occur in the data storage, which are governed by the CXL.cachemem device error handling protocol (see [Section 12.2.3\)](#page-1002-2). If uncorrectable errors occur in both the TE State storage and the data storage for the same access, then TE State mismatch handling and device error handling shall both be executed.
- For memory writes with poison:
  - When utilizing Implicit TE State changes, the target shall update the TE State whether poison is present or not
  - When Write Access Control is utilized, the target shall enforce the TE State mismatch rules whether poison is present or not

Targets that have TE State changes disabled and CKID-based memory encryption disabled:

• Shall return the TEE Intent from the memory request in the response opcode

Targets that have read and/or write access control enabled:

- Shall implement TE State changes
- Shall follow the rules defined below for implicit or explicit target behavior for updating TE State, verifying TE State, and responding to access control state verification

Targets optionally provide an event log entry of all dropped writes or failed reads that occur in response to failed TE State checks to aid in root-cause analysis of unexpected behavior by reporting a General Media or DRAM Event Record with a Memory Event Type of TE State Violation.

Targets that implement CKID-based target encryption shall perform CKID-type checks as described in [Section 11.5.4.6.2.1.](#page-948-0)

The granularity utilized for TE State changes shall be consistent with the interleave granularity being configured. For example, if the host utilizes a 4K TE State change granularity on each target that is part of a 16-way interleave set with a 256B interleave granularity, each target will utilize 256B of DPA space to change 4K of TE State.

If the target was configured with no TE State storage in the device, by utilizing Set Features with Metabits Storage, then it is assumed the target has no TE State tracking capabilities and the target shall disable the following in Get Target Capabilities Response:

- Implicit TE State Change
- Explicit In-band TE State Change when TE State Granularity is set to 64B
- Explicit Out-of-band TE State Change when TE State Granularity is set to 64B

##### 11.5.4.5.1 TEUpdate Memory Transaction

The TEUpdate memory transaction shall utilize the flit's 3-bit SnpType field to provide a Length Index to preconfigured fixed granularities of TE State.

Length Index encodings 1 through 6 are configurable. Length Index encodings 0 and 7 are fixed, where 0 is defined as 64B and 7 is defined as the target's entire memory space.

Targets that support implicit TE State changes or in-band explicit TE State changes shall support this transaction with Length Index = 0 and may support a Length Index of 7 as reported in Get Target Capabilities. If the target only supports implicit TE State changes, then Length Index encodings 1 through 6 shall be reserved.

The HPA present in the TEUpdate transaction shall be decoded by the target to the correct HDM decoder and the starting HPA, HDM decoder Interleave Granularity (IG), and HDM decoder Interleave Ways (IW) are utilized by the target to change the TE State of those HPA ranges within the granularity determined from the SnpType field.

The CKID field is reserved for the TEUpdate transaction and shall be ignored by the target.

There is no mechanism for the target to reject an explicit TEUpdate transaction.

##### <span id="page-941-0"></span>11.5.4.5.2 Implicit TE State Changes

Implicit state changes shall always occur on a cacheline write and shall not utilize Write Access Control.

When utilizing implicit TE State changes, the target shall also support explicit in-band TE State changes with Length Index 0 to indicate a 64B length.

Implicit TE State changes and Write Access Control are mutually exclusive features, and at most, one shall be enabled.

[Table 11-20](#page-942-0) outlines the expected target behavior for implementing implicit TE State changes.

<span id="page-942-0"></span><span id="page-942-2"></span>

| Table 11-20. |  |  | Target Behavior for Implicit TE State Changes |
|--------------|--|--|-----------------------------------------------|
|--------------|--|--|-----------------------------------------------|

|                               | Target's TE State<br>Associated |                                                                                                                                  | TEE Intent of Memory Transaction Received by the Target                                                                                  |  |
|-------------------------------|---------------------------------|----------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------|--|
| with Memory<br>Access Address | TEE Opcodes1                    | Non-TEE Opcodes2                                                                                                                 |                                                                                                                                          |  |
|                               | TE 0                            | •<br>Writes:<br>— Full cacheline write shall cause an<br>implicit state change to TE=1<br>— S2M NDR TEE opcode shall be returned | •<br>Writes:<br>— No change to TE State<br>— S2M NDR non-TEE opcode shall be<br>returned                                                 |  |
|                               | TE 1                            | •<br>Writes:<br>— No change to TE State<br>— S2M NDR TEE opcode shall be returned                                                | •<br>Writes:<br>— Full cacheline writes shall cause an<br>implicit state change to TE=0<br>— S2M NDR non-TEE opcode shall be<br>returned |  |

- 1. MemWrTEE, MemWrPtlTEE.
- 2. MemWr, MemWrPtl.

###### 11.5.4.5.2.1 Partial Write Handling with Implicit TE State Changes

Full cacheline writes are required to change the TE State implicitly.

Initiator-based memory encryption shall be handled as follows:

• A partial write shall be treated as an under fill read, merging of partial write data with under fill read data, followed by a full cacheline write. The under fill read shall utilize the same TEE intent as the full cacheline write that follows.

Target-based memory encryption shall be handled as follows:

- A partial write shall be treated as an under fill read, merging of partial write data with under fill read data, followed by a full cacheline write. The under fill read shall utilize the same TEE intent as the full cacheline write that follows.
<span id="page-942-1"></span>- • The under fill read shall follow the rules for reads and the full cacheline write shall follow the rules for writes.

##### 11.5.4.5.3 Explicit TE State Changes

If explicit state changes are supported, the target shall support utilizing the TEUpdate memory transaction for in-band state changes and/or the CMA/SPDM secure session TSP request, Set Target TE State, for out-of-band changes. For explicit TE State changes > 64B, the target shall pre-allocate resources for a single explicit state change request to avoid head-of-line blocking.

The target shall be configured to enable explicit in-band TE State changes or explicit out-of-band TE State changes and either may be enabled individually or both may be enabled at the same time. If the host is utilizing both simultaneously, the host shall maintain coherency between them.

Explicit TE State changes shall be initiated from the host. The host shall ensure that memory affected by the TE state change is flushed from caches before initiating the explicit state change request.

The host shall be responsible for maintaining coherency for accesses to memory ranges that are also executing an explicit state change.

While the explicit TE State change request is executing, the target shall handle memory transactions as follows:

• The target shall continue to process unrelated memory transactions while the state change is executing

- For explicit TE State changes > 64B:
  - For writes to memory ranges that are undergoing the state change, the target shall drop the write and return the inverted TEE Intent in the write completion
  - For reads to memory ranges that are undergoing the state change, the target shall return all 1s and the inverted TEE Intent in the read completion

When executing out-of-band explicit TE State changes that cover a large amount of data, the target may require extra execution time and may utilize the Delayed Response to prevent request timeouts as described in [Section 11.5.5.9.](#page-993-0)

The target shall report optional support to sanitize the contents of memory with 0s anytime the explicit TE State change request is received. If enabled by the host, the target shall complete the overwrite of the affected range before the explicit state change is considered complete. This sanitize capability is reported in Get Target Capabilities and the host may enable its use with Set Target Configuration. Sanitizing large amounts of memory may require extra execution time and targets may utilize the Delayed Response to prevent request timeouts as described in [Section 11.5.5.9.](#page-993-0)

If in-band and out-of-band explicit state changes overlap, the host shall ensure that those requests have non-overlapping address ranges. Otherwise, an indeterminate result could occur. If the target can detect this overlap, the target should generate an appropriate event record to aid in debug.

For explicit updates > 64B: A single explicit state change shall be sent to every target in the same interleave set. Explicit state changes specify a starting address and length that cover the entire range to be changed. The target shall change the state for all portions of the range that land on its portion of the interleave.

###### 11.5.4.5.3.1 Optional Explicit In-band TE State Change

For explicit in-band TE State changes:

- The in-band mechanism shall utilize the TEUpdate memory transaction.
- The association of length index in the SnpType field to a given granularity is configured by the initiator utilizing Set Target Configuration. This is done to minimize the size of the TEUpdate flit to a single slot to minimize Transaction Layer complications.
- Length Index value of 0 is reserved for 64B state changes.
- Length Index value of 7 is reserved for state changes affecting the entire memory space of the target.
- Length Index values 1-6 are host configurable to any supported length utilizing Set Target Configuration.
- If the in-band TE State change granularity is > 64B, the host shall only issue a single explicit in-band state change request at a time.
- If the in-band TE State change granularity is 64B, the host may issue multiple explicit in-band TE State change requests to non-overlapping address ranges and the target shall queue those requests waiting to execute.

[Figure 11-29](#page-944-0) outlines the association between the Explicit In-band TE State Granularity specified in Set Target Configuration and the Length Index specified in the TEUpdate transaction SnpType field.

<span id="page-944-0"></span>**Figure 11-29. Optional Explicit In-band TE State Change Architecture**

![](_page_944_Figure_3.jpeg)

<span id="page-944-2"></span>[Table 11-21](#page-944-1) outlines the expected target behavior for utilizing explicit in-band TE State changes.

<span id="page-944-1"></span>**Table 11-21. Target Behavior for Explicit In-band TE State Changes**

| Target's TE State<br>Associated | TEE Intent of Memory Transaction Received by the Target                                                                                                                   |  |
|---------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--|
| with Memory<br>Access Address   | TEE Opcodes1                                                                                                                                                              |  |
| TE 0                            | •<br>TEUpdate(TE = 0):<br>— No change in TE state<br>•<br>TEUpdate(TE = 1):<br>— This shall cause an explicit state change to TE=1 for the affected memory<br>granularity |  |
| TE 1                            | •<br>TEUpdate(TE = 0):<br>— This shall cause an explicit state change to TE=0 for the affected memory<br>granularity<br>•<br>TEUpdate(TE = 1):<br>— No change in TE state |  |

<sup>1.</sup> TEUpdate.

###### 11.5.4.5.3.2 Optional Explicit Out-of-Band TE State Change

For explicit out-of-band TE State changes:

- Out-of-band mechanism utilizes the Set TE State TSP request and supports a robust set of possible TE State change granularities reported in Get Target Capabilities that cannot be utilized with the limitations of the in-band mechanism
- Host shall only issue a single explicit out-of-band state change request at a time
- Target shall reject any request to set TE State when another TE State change request is already executing

[Table 11-22](#page-945-0) outlines the expected target behavior for utilizing explicit out-of-band TE State changes.

<span id="page-945-0"></span>**Table 11-22. Target Behavior for Explicit Out-of-band TE State Changes**

| Target's TE State<br>Associated<br>with Memory<br>Access Address | TE State of Set Target TE State Received By the Target                                                                                                                                                              |  |
|------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--|
| TE 0                                                             | •<br>SetTargetTEState(TE State = 0):<br>— No change in TE state<br>•<br>SetTargetTEState (TE State = 1):<br>— This shall cause an explicit state change to TE=1 for the affected memory<br>address and granularity  |  |
| TE 1                                                             | •<br>SetTargetTEState (TE State = 0):<br>— This shall cause an explicit state change to TE=0 for the affected memory<br>address and granularity<br>•<br>SetTargetTEState (TE State = 1):<br>— No change in TE state |  |

##### 11.5.4.5.4 Write Access Control

<span id="page-945-2"></span>[Table 11-23](#page-945-1) outlines the required target behavior when Write Access Control is enabled on the target.

<span id="page-945-1"></span>**Table 11-23. Target Behavior for Write Access Control**

| Target's TE State<br>Associated | TEE Intent of Memory Transaction Received by the Target                                                                                       |                                                                                                                                        |  |
|---------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------|--|
| with Memory<br>Access Address   | TEE Opcodes1                                                                                                                                  | Non-TEE Opcodes2                                                                                                                       |  |
| TE 0                            | •<br>Writes:<br>— Full/Partial cacheline write shall be<br>dropped<br>— S2M NDR non-TEE opcode shall be<br>returned<br>— Optionally log event | •<br>Writes:<br>— Full/Partial cacheline write allowed<br>— S2M NDR non-TEE opcode shall be<br>returned                                |  |
| TE 1                            | •<br>Writes:<br>— Full/Partial cacheline write allowed<br>— S2M NDR TEE opcode shall be returned                                              | •<br>Writes:<br>— Full/Partial cacheline write shall be<br>dropped<br>— S2M NDR TEE opcode shall be returned<br>— Optionally log event |  |

- 1. MemWrTEE, MemWrPtlTEE.
- 2. MemWr, MemWrPtl.

If Write Access Control is not enabled on the target, the target shall not check write requests for possible access control violations. See [Section 11.5.4.5.2](#page-941-0) for implicit TE State changes and required target behavior.

If Write Access Control is enabled on the target, the target shall clear the TE State to 0 for all addressable memory in response to the Lock Target Configuration Request and before generating a Lock Target Configuration Response.

Write Access Control requires the target to also support explicit TE State changes. The target shall reject attempts to enable Write Access Control without one or more explicit TE State change mechanisms also being enabled.

The target shall not perform Write Access Control when updating MetaValue. See [Section 11.5.4.5.6](#page-946-1) for requirements for handling MetaValue updates.

If enabled, the target shall perform Write Access Control when updating Extended Metadata (EMD). See [Section 11.5.4.5.7](#page-947-1) for requirements for handling EMD updates.

Implicit TE State changes and Write Access Control are mutually exclusive features, and at most, one shall be enabled.

###### 11.5.4.5.4.1 Partial Write Handling with Write Access Control

Target-based memory encryption shall be handled as follows:

- A partial write shall be treated as an under fill read, merging of partial write data with under fill read data, followed by a full cacheline write.
- The under fill read shall follow the rules for reads and the full cacheline write shall follow the rules for writes. In case of a TEE mismatch between the TE State obtained in the under fill read and the TEE Intent of the request, the target shall drop the write.

##### 11.5.4.5.5 Read Access Control

<span id="page-946-2"></span>[Table 11-24](#page-946-0) outlines the required target behavior when Read Access Control is enabled on the target.

<span id="page-946-0"></span>**Table 11-24. Target Behavior for Read Access Control**

| Target's TE State<br>Associated | TEE Intent of Memory Transaction Received by the Target                                                                             |                                                                                                                              |  |
|---------------------------------|-------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------|--|
| with Memory<br>Access Address   | TEE Opcodes1                                                                                                                        | Non-TEE Opcodes2                                                                                                             |  |
| TE 0                            | •<br>Reads:<br>— Reads shall return fixed data of all 1s<br>— S2M DRS non-TEE opcode shall be<br>returned<br>— Optionally log event | •<br>Reads:<br>— Allowed<br>— S2M DRS non-TEE opcode shall be<br>returned                                                    |  |
| TE 1                            | •<br>Reads:<br>— Allowed<br>— S2M DRS TEE opcode shall be returned                                                                  | •<br>Reads:<br>— Reads shall return fixed data of all 1s<br>— S2M DRS TEE opcode shall be returned<br>— Optionally log event |  |

- 1. MemRdTEE, MemRdDataTEE, MemRdFillTEE, and MemSpecRdTEE.
- 2. MemRd, MemRdData, MemRdFill, and MemSpecRd.

If Read Access Control is not enabled on the target, the target shall not check read requests for possible access control violations.

The target shall not perform Read Access Control when updating MetaValue. See [Section 11.5.4.5.6](#page-946-1) for requirements for handling MetaValue updates.

If enabled, the target shall perform Read Access Control when updating Extended Metadata (EMD). See [Section 11.5.4.5.7](#page-947-1) for requirements for handling EMD updates.

##### <span id="page-946-1"></span>11.5.4.5.6 MetaValue Updates for HDM-H

MetaValue is a property of the memory address and unrelated to any of the data associated with that address. Consequently, the target shall not perform access control checks on MetaValue updates.

**TEUpdate:**

• TEUpdate uses the MetaValue to convey the TE State and does not update MetaValue

For all other (non-TEUpdate) transactions:

- There is no TE State associated with MetaValue
- Targets that implement access control shall ignore access control checks when updating the MetaValue and shall allow MetaValue updates, even if the associated read or write request fails access control checks.

Initiators are responsible for ensuring that changes to MetaValue do not negatively affect data coherency. How an initiator guarantees this is beyond the scope of CXL.

##### <span id="page-947-1"></span>11.5.4.5.7 Extended Metadata Updates

Extended Metadata (EMD) is a property of the data and is updated using the same flows and transactions as data. Consequently, TE State and access control, if enabled, shall be utilized when updating EMD.

If Write Access Control checks fail, the target shall not update EMD.

If Read Access Control checks fail, the target shall return fixed data of all 1s for EMD.

#### <span id="page-947-0"></span>11.5.4.6 Memory Encryption

Protecting data at rest in the target memory device is required for confidential computing and requires memory encryption. The TSP supports both initiator-based and target-based memory encryption capabilities, and an initiator shall utilize one or the other when adding a target to the TCB. If target-based memory encryption is not enabled by the initiator, it shall be the initiator's responsibility to utilize initiator-based memory encryption.

This version of the TSP specification is focused on direct attached CXL devices. In such a configuration, there is a single initiator for a given memory range and all transactions to that memory region shall flow through that initiator. When initiator-based encryption is utilized, it is the initiator's responsibility to ensure that the cryptographic keys are correct for all initiators and to maintain data coherency. Initiator-based encryption implementations that utilize partial writes require the initiator to perform a read of a complete cacheline, update the corresponding bytes, and write the complete cacheline back to the target. The target cannot modify any blocks that are encrypted by an initiator and thus cannot perform the RMW (read-modify-write) that is required to perform partial writes.

Target-based encryption requires Transaction Layer and Link Layer protocol changes to pass a CKID to the target so that the target can correctly choose the key that is utilized for the encryption/decryption of data associated with each transaction.

Both initiator-based and target-based memory encryption are optional. The target reports its supported memory encryption capabilities, and the initiator selects the memory encryption that it needs to utilize.

##### 11.5.4.6.1 Initiator-based Memory Encryption

Initiator-based memory encryption may be utilized, independent of target-based memory encryption being enabled or disabled, as follows:

- Target shall support the MemRdFill memory request, which is required for deadlock prevention with partial writes and initiator-based encryption. Support for this request is a target requirement when indicating TSP Capable support in the DVSEC CXL Capability register.
- If target-based CKID memory encryption is not enabled, the CKID field in the memory transaction is reserved and ignored by the target.

##### 11.5.4.6.2 Target-based Memory Encryption

Targets are not required to implement memory encryption. When memory encryption is implemented on the target, the following applies:

• Encryption shall be implemented using one of the Memory Encryption Algorithms Supported that are reported in Get Target Capabilities Response.

- TSP supports two target-based memory encryption mechanisms:
  - CKID-based encryption requires use of the CKID field in the Transaction Layer to identify a specific key to be utilized when encrypting/decrypting memory contents for a given transaction. This feature requires the use of TEE opcodes in the memory transaction to perform the proper CKID type checking.
  - Range-based encryption utilizes memory range registers that are configured to associate a particular encryption key with a specific memory range and does not rely on the CKID field in the transaction.
  - Host may enable CKID-based or range-based target memory encryption, but shall not enable both.
  - Target shall reject attempts to enable both target-based encryption methods.

###### <span id="page-948-0"></span>11.5.4.6.2.1 CKID-based Memory Encryption

When CKID-based target memory encryption is implemented, the following applies:

- For CKID-based encryption, the initiator and target shall utilize the CKID field in the Transaction Layer for memory requests.
- Each host Root Port has a unique 13-bit CKID value to be utilized across all targets. A host may choose to share CKID values across Root Ports.
- Target shall accept the entire range of the 13-bit CKID field defined in the Transaction Layer.
- CKIDs that are configured on each target can start and end anywhere within the CKID space supported by the protocol.
- Target reports the Number of CKIDs that it supports in Get Target Capabilities. How the target maps the supported number of CKIDs to the 13-bit CKID field in the transaction is target implementation specific.
- Number of CKIDs that the target supports may be sparsely distributed across the 13-bit range, or optionally the target may require that the CKIDs be assigned a contiguous range starting at a specific CKID Base.
- If the target does not require a CKID Base:
  - CKID specified in Set Target CKID Specific Key, Set Target CKID Random Key, and Clear Target CKID Key shall not cause the target to utilize more than the Number of CKIDs that the target supports
- If the target requires a CKID Base to be utilized:
  - Target shall indicate that a range of CKIDs using a CKID Base and Number of CKIDs is required in Get Target Capabilities
  - Host shall configure a contiguous range of CKIDs on the target by specifying the CKID Base and Number of CKIDs that the target shall utilize with Set Target Configuration. The Number of CKIDs enabled by the host shall be <= Number of CKIDs reported by the target.
  - CKID in the Transaction Layer memory requests from the initiator shall be CKID Base <= CKID < CKID Base + Number of CKIDs configured on the target. See [Table 11-25](#page-950-0) for the target behavior if the CKID in the transaction is outside the configured CKID of the target.
  - CKID specified by the host in Set Target CKID Specific Key, Set Target CKID Random Key, and Clear Target CKID Key shall be CKID Base <= CKID < CKID Base + Number of CKIDs configured on the target.
- Initiator may configure a specific CKID to a specific initiator-supplied key by utilizing Set Target CKID Specific Key.
- Initiator may configure a specific CKID to a random target-generated key with optional initiator-supplied key entropy by utilizing Set Target CKID Random Key.

- Initiator may clear a previously configured key to allow the CKID to be recycled for another key by utilizing Clear Target CKID Key sent on the same session that was utilized to set the key. If the session utilized to set the key has terminated or closed then the target may need to be reset to break the memory encryption key to CKID association.
- Target implements the mapping of keys to CKIDs.
- Each CKID shall be a TVMCKID or OSCKID that is configured utilizing the CMA/ SPDM PrimarySession or SecondarySession(s) (see [Figure 11-30](#page-949-0), which describes this partitioning). See the description below on how the target utilizes the CKID Type to verify memory transactions and the behavior of the target when the verification fails.
- When utilizing target CKID-based memory encryption, the initiator's transactions that contain TVMCKIDs shall utilize TEE opcodes and those that contain OSCKIDs shall utilize non-TEE opcodes. The target shall verify that the opcodes are correct for accessing each CKID Type.
- If target CKID-based encryption has not yet been enabled, the CKID field in the memory transaction shall be ignored by the target.
- If target CKID-based encryption has been enabled and the CKID field in the received memory transaction does not reference a CKID that has been previously set using Set Target CKID \* Key, the target's response shall follow the existing CXL.cachemem NXM (non-existent memory) handling.

[Figure 11-30](#page-949-0) demonstrates the target mixing of TVMCKIDs and OSCKIDs in a single range of possible CKIDs that utilize the CKID Base and Number of CKIDs.

![](_page_949_Figure_9.jpeg)

<span id="page-949-0"></span>**Figure 11-30. CKID-based Memory Encryption Utilizing CKID Base**

The target stores the CKID Type along with the CKID and key. The target shall verify that each incoming memory transaction passes the following checks:

- The memory transaction CKID is within the valid configured range of the target
- The memory transaction has a non-TEE opcode and the CKID is an OSCKID OR the memory transaction has a TEE opcode and the CKID is a TVMCKID

If any of these checks fail, the target should provide an event log entry to aid in rootcause analysis of unexpected behavior by reporting a General Media or DRAM Event Record with Memory Event Type of CKID Violation.

<span id="page-950-2"></span>[Table 11-25](#page-950-0) outlines the target behavior for memory transactions that request a CKID that is outside the configured range of the target.

<span id="page-950-0"></span>**Table 11-25. Target Behavior for Invalid CKID Ranges**

| CKID                           | Memory Transaction Received by the Target                                                                                      |                                                                                                               |  |
|--------------------------------|--------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------|--|
|                                | Read Opcodes                                                                                                                   | Write Opcodes                                                                                                 |  |
| Within<br>Configured<br>Range  | •<br>Allowed                                                                                                                   | •<br>Allowed                                                                                                  |  |
| Outside<br>Configured<br>Range | •<br>Reads shall return fixed data of all 1's<br>•<br>S2M NDR non-TEE opcode shall be<br>returned<br>•<br>Optionally log event | •<br>Writes shall be dropped<br>•<br>S2M NDR non-TEE opcode shall be<br>returned<br>•<br>Optionally log event |  |

<span id="page-950-3"></span>[Table 11-26](#page-950-1) outlines the target behavior for the CKID-type verification checks based on TEE Intent using TEE opcodes and non-TEE opcodes, which is described in [Section 11.5.4.5.](#page-939-1)

<span id="page-950-1"></span>**Table 11-26. Target Behavior for Verifying CKID Type**

| Target's CKID type<br>Associated                   | TEE Intent of Memory Transaction Received by the Target                                                                             |                                                                                                                              |
|----------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------|
| with CKID<br>Contained in<br>Memory<br>Transaction | TEE Opcodes1                                                                                                                        | Non-TEE Opcodes2                                                                                                             |
| OSCKID                                             | •<br>Writes:<br>— Writes shall be dropped<br>— S2M NDR non-TEE opcode shall be<br>returned<br>— Optionally log event                | •<br>Writes:<br>— Full/Partial cacheline write allowed<br>— S2M NDR non-TEE opcode shall be<br>returned                      |
|                                                    | •<br>Reads:<br>— Reads shall return fixed data of all 1s<br>— S2M DRS non-TEE opcode shall be<br>returned<br>— Optionally log event | •<br>Reads:<br>— Allowed<br>— S2M DRS non-TEE opcode shall be<br>returned                                                    |
| TVMCKID                                            | •<br>Writes:<br>— Full/Partial cacheline write allowed<br>— S2M NDR TEE opcode shall be returned                                    | •<br>Writes:<br>— Writes shall be dropped<br>— S2M NDR TEE opcode shall be returned<br>— Optionally log event                |
|                                                    | •<br>Reads:<br>— Allowed<br>— S2M DRS TEE opcode shall be returned                                                                  | •<br>Reads:<br>— Reads shall return fixed data of all 1s<br>— S2M DRS TEE opcode shall be returned<br>— Optionally log event |

- 1. MemWrTEE, MemWrPtlTEE, MemRdTEE, MemRdDataTEE, MemRdFillTEE, and MemSpecRdTEE.
- 2. MemWr, MemWrPtl, MemRd, MemRdData, MemRdFill, and MemSpecRd.

###### 11.5.4.6.2.2 Range-based Memory Encryption

- The initiator may configure a specific HPA memory range to use a specific initiatorsupplied key that utilizes Set Target Range Specific Key.
- The initiator may configure a specific HPA memory range to use a random targetgenerated key with optional initiator-supplied key entropy that utilizes Set Target Range Random Key.

- The initiator may clear a previously configured key to allow the memory range to be recycled for another key by utilizing Clear Target Range Key sent on the same session that was utilized to set the key. If the session utilized to set the key has terminated or closed, then the target may need to be reset to break the memory encryption key to memory range association.
- The target advertises the Memory Encryption Number of Range Based Keys that it supports in Get Target Capabilities, and the initiator assigns a Range ID and HPA range at the time the key is programmed. The target shall verify that the HPA memory ranges and Range IDs do not overlap. The HPA contained within the memory request shall be compared to the programmed memory ranges by the target to retrieve the correct key to utilize in the encryption. The Range ID specified in Set Target Range Specific Key and Set Target Range Random Key shall be 0<= Range ID < Memory Encryption Number of Range Based Keys.
- The PrimarySession or SecondarySession(s) shall be utilized for setting and clearing range based keys. The session utilized to set a range based key shall be the same session utilized to clear the same range based key.
- If target range-based encryption has not yet been enabled, the address range in the memory transaction shall be ignored by the target for range-based memory encryption.
- If target range-based encryption has been enabled and the memory address in the received memory transaction does not reference a memory range that has been previously set using Set Target Range \* Key, the target's response shall follow the existing CXL.cachemem NXM (non-existent memory) handling.

[Figure 11-31](#page-951-1) outlines range-based memory encryption utilizing the HPA.

<span id="page-951-1"></span>**Figure 11-31. Range-based Memory Encryption**

#### <span id="page-951-0"></span>11.5.4.7 Transport Security

Transport security is optional for TSP. If supported and enabled, a CXL-approved Integrity and Data Encryption (IDE) mechanism shall be used. It is up to the TEE policy to decide whether targets that do not support transport security invalidates their use for confidential computing scenarios.

Currently hop-by-hop CXL IDE is the only defined CXL transport security mechanism, and determining the target's IDE capabilities or enabling IDE modes is done through CXL IDE-defined registers. There are no Transport Security-specific TSP interfaces defined at this time.

*Warning:* Although Transport Security is optional, disabling of Transport Security adds additional exposure to physical attacks such as device removal and manipulator-in-the-middle because the binding provided by Transport Security is not utilized. If these attacks are considered part of the threat model for the TEE and cannot be protected via other methods, then Transport Security shall be enabled for confidential computing scenarios.

#### <span id="page-952-0"></span>11.5.4.8 Configuration

The PrimarySession shall be utilized to configure the security for each target in the CXL hierarchy that utilizes TSP, supported CXL Transport Security mechanisms, and other interfaces to setup the TCB. After the targets are correctly configured, the PrimarySession shall be utilized to lock the target to disable initiator access to registers that could cause data coherency issues, loss of data, reveal TVM data to an untrusted VM, and/or otherwise compromise the TCB. After the target is locked, trusted memory transactions are allowed, and the target or initiator shall perform access verification by utilizing the TE State.

[Figure 11-32](#page-952-1) outlines the defined target security states that are utilized by TSP.

<span id="page-952-1"></span>**Figure 11-32. TSP Target Security States**

![](_page_952_Figure_8.jpeg)

![](_page_952_Figure_9.jpeg)

**• CONFIG\_UNLOCKED**

- Default security state after Conventional Reset (see [Section 11.5.4.8.3](#page-957-0) for details).
- TSP security configuration is performed in this state.
- TEE opcode transactions are not allowed by the target in this state (see [Section 11.5.4.10.1\)](#page-959-2).
- Non-TEE opcode transactions are allowed as discussed in [Section 11.5.4.5.](#page-939-1)
- Transition to CONFIG\_LOCKED state:
  - After successfully locking the target.

**• CONFIG\_LOCKED**

- Restrictions placed on register accesses, CCI commands to protect the TCB. See the Lock Target Configuration interface description (see [Section 11.5.5.6.7](#page-982-2) and [Section 11.5.5.6.8\)](#page-983-2) for more details on target behavior after locking.
- Target shall save TE State and if enabled, enforce TE State checking.
- Assigning keys to CKIDs or memory ranges, clearing of keys allowed in this state.
- Non-TEE opcode transactions are allowed as discussed in [Section 11.5.4.5.](#page-939-1)
- TEE opcode transactions allowed as discussed in [Section 11.5.4.5.](#page-939-1)
- Transition to ERROR state:
  - The following are treated as errors that shall transition the target to the ERROR state: Transport Security failures (e.g., CXL IDE becoming insecure), CXL Reset (which doesn't reset the entire device), and/or other cases in which the link can no longer be trusted or only a portion of the device is affected by the error (see [Section 11.5.4.8.3](#page-957-0) for details).
- Transition to CONFIG\_UNLOCKED state:
  - Upon receipt of a Conventional Reset (see [Section 11.5.4.8.3](#page-957-0) for details).

### • ERROR

- The target shall continue to protect all TVM data when in the error state.
- After the target enters the error state, the target shall stop accepting all future TEE memory transactions. For transactions that were accepted prior to going to the error state, it is permissible to handle those transactions as normal. See [Section 11.5.4.8.3](#page-957-0) for details.
- Non-TEE opcode transactions are allowed as discussed in [Section 11.5.4.5.](#page-939-1)
- Transition to CONFIG\_UNLOCKED state:
  - The target shall automatically transition from the ERROR to the CONFIG\_UNLOCKED state after it has cleaned up the current secure sessions and data (see [Section 11.5.4.8.3](#page-957-0) for details).
  - Upon receipt of a Conventional Reset (see [Section 11.5.4.8.3](#page-957-0) for details).

Use of these states and the target's behavior in each state are further detailed in [Section 11.5.5.](#page-968-0)

- The TSP architecture assumes that a single authority model shall be utilized for configuration and locking of the target:
  - The host owns all configuration policies
  - The host establishes and locks the security configuration for all targets within its domain
  - MH-SLDs implement separate target configurations for each host, thereby allowing each host to independently configure its SLDs

##### <span id="page-953-0"></span>11.5.4.8.1 Locking the Target

As a pre-condition to performing the memory security checks, the DSM shall first lock the configuration to ensure that it cannot be modified during or after completion of the memory security checks. The mechanisms used by the DSM to lock the memory controller configuration, HDM decoder configuration, and other configuration context specific to the target micro-architecture are beyond the scope of this specification.

The target shall implement configuration and security checks that verify the locked configuration before successfully responding to the lock configuration request. Memory security checks are mechanisms that the target implements to verify whether its configuration is locked down and are acceptable to meet the confidential computing security objectives of protecting the TVM data. The TSM RoT relies on the DSM for these memory security checks.

- General Assumptions:
  - Any target operation mode that exposes internal data or allows data logging or tracing is disabled
  - Any register that can lead to data corruption shall be locked for writing.
  - Registers leading to reset events that are guaranteed to transition the DSM to ERROR or CONFIG\_UNLOCKED state are not required to be locked for writing.
  - Reading of security-sensitive registers shall be blocked. Reading of nonsecurity-sensitive registers do not need to be blocked.
  - Transport Security cannot be assumed to be enabled.
- As part of the memory security checks, the DSM shall ensure the following:
  - HDM decoders in the target are configured consistently and with no aliases. These decoders are specific to the target's implementation. An alias is present if two HPAs decode to the same DPA.
  - Memory controllers and other logic in the target are configured consistently to meet the confidential computing security objectives. Such configuration shall be specific to the target implementation. Examples of such configuration include the DIMM population registers, interleave configuration, error-detection capabilities, ECC mode configuration, debug capabilities such as error/pattern injection logic, target row refresh controls, etc.
  - HDM decoders of the LD are in a consistent state and do not have aliases or overlaps. The HDM decoders shall be locked with the Lock on Commit bit in the HDM Decoder Control register set to 1.
  - Addresses that are decoded by the HDM decoders shall not overlap with addresses that are decoded as PCIe memory space for MMIO. The target shall prevent the overlapping of PCIe BARs.
  - Error-detection capabilities required to ensure security of TVM data shall be enabled in the Uncorrectable Error Mask register of the CXL RAS Capability structure.
  - CXL link-specific registers for the enabled TSP Transport Security mechanism control registers are programmed with parameters that are validated to be safe to support the confidential computing security objectives.
  - If the target is configured to utilize Transport Security, all target CXL.cachemem links shall have Transport Security enabled to protect the security of the transport.
  - PCIe DVSEC for CXL target shall be locked by asserting CONFIG\_LOCK.
  - PCIe DVSEC for Test Capability, if implemented, shall be locked by asserting TestLock and no test algorithms, test capabilities, and/or error injection methods are currently active.
  - No test algorithms, test capabilities, and/or error injection methods are currently active or configured through the compliance DOE mailbox.
  - The compliance DOE shall be disabled and register writes to enable the compliance DOE shall be blocked.
  - Other target implementation-specific configuration checks as defined by the micro-architecture of the target.

- CXL Capabilities are configured on the target to prevent the leaking of cypher text from the target after a CXL Reset, as discussed in [Section 11.5.4.8.3](#page-957-0).
- Successfully locking the target should result in the following target behavior:
  - The TEE's memory range associated with the target is locked by making the HDM decoder configuration immutable after the target is locked.
  - The target shall limit supported TSP requests to the subset of requests that are allowed when the target is in the CONFIG\_LOCKED state. See [Table 11.5.5.1](#page-968-1) for the TSP requests that are allowed on a locked target.
  - Prevention of surprise changes to the target configuration that would allow unauthorized access to data that was written by a TVM, cause the target or initiator to break the data coherency model, and/or otherwise compromise TEE integrity. This may require the target to drop host writes to PCIe or CXL registers after the target is locked.
  - The Get Target Configuration Report request and response (see [Section 11.5.5.6.6\)](#page-982-3) shall allow the initiator to securely retrieve and verify the content of specific PCIe and CXL configuration registers, after the target is locked. This allows the TSM RoT to check the configuration, securely independent of standard insecure PCIe or CXL register accesses.
  - The following actions shall be prevented by making the associated registers immutable after the target is locked:
    - Memory aliasing
      - CXL HDM Decoder Global Control register: Changing the HDM Decoder Enable state at runtime could allow an attacker to change the address for a write transaction, potentially affecting the data coherency and/or the TE State maintained on the target.
      - CXL HDM Decoder [n] Low/High, Size Low/High, and DPA Skip Low/ High Registers: Changing the HDM decoder programming at runtime could allow an attacker to change the address for a write transaction, potentially affecting the data coherency and/or the TE State maintained on the target.
      - The host shall lock all target HDM decoders that were programmed for interleave sets that are within the TEE, utilizing the Commit On Lock feature. Register writes to locked HDM decoders are dropped.
      - Writes to HDM decoders that are unlocked, not already programmed (size and skip = 0), and not considered part of the TEE, need to be allowed by the target. However, the target shall perform alias checking of those register writes to ensure that they do not alias address ranges that are already locked and considered to be in the TEE, independent of whether the host has set the Commit On Lock bit during decoder programming. The target shall treat aliased HDM decoders as a programming failure and shall behave the same way as if the Commit On Lock bit was set when the HDM decoder alias checks failed. The failed checks shall have no effect on the target, the TEE, and/or inflight transactions between them.
    - Altering target behavior at runtime
      - CXL HDM Decoder Global Control register: Disabling the Poison On Decode Error Enable bit at runtime could cause an attacker to affect the data coherency of the target and allow the initiator to potentially consume invalid data and/or a fixed data pattern as valid data.
      - CXL Control register.
      - CXL Control2 register.
      - CXL Range 1 Base High/Low registers.

- CXL Range 2 Base High/Low registers.
- Altering TEE memory interleave configuration at runtime
  - CXL HDM Decoder [n] Control register(s): Altering IG, IW, Range Type, BI, UIO, UIG, UIW, and/or ISP at runtime could allow an attacker to steer transactions to another target and/or memory range, potentially affecting the data coherency and/or the memory integrity of the TE State stored in the target.
- Altering link or Transaction Layer behavior at runtime
  - PCIe DVSEC for Flex Bus Port registers.
  - CXL Timeout and Isolation Control register.
  - CXL IDE Control register (if utilizing CXL IDE for Transport Security): Altering PCRC Disable or IDE.StopEnable at runtime could allow the link to operate incorrectly if there is a mismatch with the initiator. This should result in a MAC error which should cause the IDE on the link to transition to Insecure State (if IDE is enabled) and is indicated in the CXL IDE Error Status register, bit[1] and bit[7]. When IDE transitions to Insecure State, the target shall transition to the ERROR state.
- Prevention of CCI commands that could allow untrusted access to data that was written by a TVM, cause the target or initiator to break the data coherency model, and/or otherwise compromise TEE integrity (see [Section 11.5.4.9](#page-959-0) for details).
- TEE opcodes shall be allowed by the target as outlined in the Access Control section (see [Section 11.5.4.5\)](#page-939-1).
- Enforce Read and/or Write Access Control if enabled (see [Section 11.5.4.8\)](#page-952-0).
- Prevention of surprise changes to the target configuration for any target implementation-specific or vendor-implementation-specific registers or CCI commands that could allow untrusted access to data that was written by a TVM, cause the target or initiator to break the data coherency model, and/or otherwise compromise TEE integrity. This requires implementation-specific analysis and is beyond the scope of the TSP.

##### 11.5.4.8.2 Considerations for Securing the Host

- The host is responsible for securing the Root Ports to secure the TEE environment, and such mechanism is beyond the scope of the TSP.
- The host should prevent surprise changes to the host configuration that would allow unauthorized access to data that was written by a TVM, cause the target and/ or host to break the data coherency model, and/or otherwise compromise TEE integrity.
- Some PCIe and CXL Root Port registers that should be protected by the host are outlined here (this is not an exhaustive list, but an example of some of the registers that affect the initiator's link to the locked target):
  - Memory aliasing
    - CXL HDM Decoder Global Control register: Changing the HDM Decoder Enable state at runtime could allow an attacker to change the address for a write transaction, potentially affecting the data coherency and/or the TE State maintained on the target.
    - CXL HDM Decoder [n] Low/High, Size Low/High, and Target List Low/High registers: Changing the HDM decoder programming at runtime could allow an attacker to change the address for a write transaction, potentially affecting the data coherency and/or the TE State maintained on the target.

- The host shall lock all HDM decoders that were programmed for interleave sets that are within the TEE, utilizing the Commit On Lock feature. Register writes to locked HDM decoders are dropped.
- Writes to HDM decoders that are unlocked, not already programmed (size and skip = 0), and not considered part of the TEE need to be allowed by the initiator.
- Altering host behavior at runtime
  - CXL HDM Decoder [n] Global Control register: Disabling the Poison On Decode Error Enable bit at runtime could cause an attacker to affect the data coherency of the target and allow the host to potentially consume invalid data and/or a fixed data pattern as valid data.
  - CXL BI Decoder Control register: Toggling of BI Enable during runtime could affect data coherency of HDM-DB memory. If BI Decoder Commit is not toggled after reassigning bus numbers, data could be steered to the wrong location, thereby causing HDM-DB memory coherency issues.
  - CXL Cache ID RT Control register: If Cache ID RT Commit toggles at runtime and the Route Table contains invalid routing information, this could cause transactions to be steered to the wrong location, thereby causing data coherency issues.
  - CXL Cache ID Target register: Not toggling Valid and Port Number after a Route Table change could cause transactions to be steered to the wrong location, thereby causing data coherency issues.
- Altering memory interleave configuration at runtime
  - CXL HDM Decoder [n] Control register(s): Altering IG, IW, Range Type, BI, UIO, UIG, UIW, and/or ISP at runtime could allow an attacker to steer transactions to another target and/or memory range, potentially affecting the data coherency and/or the memory integrity of the TE State stored in the target.
- Altering link or Transaction Layer behavior at runtime
  - PCIe DVSEC for Flex Bus Port registers
  - CXL IDE Control register (if utilizing CXL IDE for Transport Security): Altering PCRC Disable or IDE.StopEnable at runtime could allow the link to operate incorrectly if there is a mismatch with the initiator. This should result in a MAC error which should cause the IDE on the link to transition to Insecure State (if IDE is enabled) and is indicated in the CXL IDE Error Status register, bit[1] and bit[7]. When IDE transitions to Insecure State, the target shall transition to the ERROR state.
- Configuring CXL Capabilities on the target to prevent the leaking of cypher text from the target after a CXL Reset, as discussed in [Section 11.5.4.8.3.](#page-957-0)

##### <span id="page-957-0"></span>11.5.4.8.3 Reset and Error Handling Behavior of the Target

This section outlines the expected target TSP behavior to Conventional Reset, CXL Reset, Transport Security Failures, and changes in secure sessions. All other resets, including FLR, do not affect the secured link or Transport Security (i.e., CXL IDE) and therefore do not change the target's TSP security state.

###### 11.5.4.8.3.1 Conventional Reset and Link Failures

Because a Conventional Reset or a Link Failure shall take down the CXL links to the target, all transactions shall immediately terminate. The target shall perform the following after receiving a Conventional Reset or on link failure:

• Terminate the CMA/SPDM SecondarySession(s) and PrimarySession

- Clear CMA/SPDM secure session keys to 0
- Target shall ensure that all TE State = 1 clear text data cannot be leaked
- If implementing target-based encryption:
  - Clear association of CKID to encryption keys
  - Clear association of HPA ranges to encryption keys
  - Clear memory encryption keys
- Transition to CONFIG\_UNLOCKED state

###### 11.5.4.8.3.2 CXL Reset, Transport Security Failures, SecondarySession(s) Termination, and PrimarySession Restart

CXL Reset, Transport Security failures such as IDE going insecure, SecondarySession(s) terminating, and/or a new PrimarySession being started all affect the target but do not take down the link. For these conditions, the target shall support the following additional requirements:

- Transition to ERROR state
- Target shall stop accepting all future TEE memory transactions
  - **Writes**: TEE opcode writes shall be dropped and S2M NDR non-TEE opcode shall be returned for the write response.
  - **Reads**: TEE opcode reads return a fixed data pattern of all 1s. S2M DRS non-TEE opcode shall be returned for the read response.
- Terminate the CMA/SPDM SecondarySession(s) and PrimarySession
- Clear CMA/SPDM secure session keys to 0
- Target shall ensure that all TE State = 1 clear text data cannot be leaked
- If implementing target-based encryption:
  - Clear association of CKID to encryption keys
  - Clear association of HPA ranges to encryption keys
  - Clear memory encryption keys
- Transition to CONFIG\_UNLOCKED state

Prevention of the leaking of cypher text from the target after a CXL Reset:

- Data on the target is encrypted using initiator-based or target-based memory encryption. Clear text data is protected; however, the cipher text stored on the target could be leaked after a CXL Reset, which should be avoided.
- Target should support clearing or randomizing of volatile HDM data on reset and indicate this capability by setting CXL Reset Mem Clr Capable in DVSEC CXL Capability to 1 and by setting Default Volatile HDM State after Cold Reset, Default Volatile HDM State after Warm Reset, and Default Volatile HDM State after Hot Reset to 1 in DVSEC CXL Capability3.
- Target should set Volatile HDM State after Hot Reset Configurability in DVSEC CXL Capability3 to 0 to indicate that the target is not capable of preserving volatile HDM state across Hot Reset.
- Target shall support resetting all TE State to 0 when enabling the ability to clear or randomize all data in response to a CXL Reset.
- If the target sets CXL Reset Mem Clr Capable to 1, the host should allow the target clear memory during CXL Reset by setting CXL Reset Mem Clr Enable in DVSEC CXL Control2.

#### <span id="page-959-0"></span>11.5.4.9 Component Command Interfaces

When the target is locked, Component Command Interface (CCI) commands that allow the target's configuration to be altered, new features to be set, maintenance operations to be executed, target memory partitioning changes, injecting and clearing of poison, sanitizing, and/or secure erasing shall be rejected by the target by returning Invalid Security State status.

Likewise, FM requests that can change the Dynamic Capacity configuration at runtime shall be rejected by the target by returning Invalid Security State status.

See [Section 8.2.10](#page-631-1) for the following command-specific additions that are relevant to TSP support:

- Transfer FW, Activate FW
- Set Features
- Perform Maintenance
- Set Partition Info
- Inject Poison, Clear Poison
- Sanitize, Secure Erase, Passphrase Secure Erase, Security Send
- Release Dynamic Capacity

See [Section 7.6.7.6.3](#page-379-2) for the following command-specific addition that is relevant to TSP support:

• Set DC Region Configuration

#### <span id="page-959-1"></span>11.5.4.10 Dynamic Capacity

As described above, CXL security requires the device to implement configuration locking to prevent tampering with the trusted configuration at runtime. Dynamic Capacity allows for memory capacity to be added or released from one or more hosts at runtime but relies on a static maximum capacity configuration to have been configured at initialization time.

The following sections outline specific areas in which there are additional requirements for targets that implement both Dynamic Capacity and TSP.

##### <span id="page-959-2"></span>11.5.4.10.1 TE State Changes

For Dynamic Capacity targets that implement TE State changes, there are additional responsibilities:

• Before a target adds any Dynamic Capacity to a host and before adding capacity to one host after releasing the capacity from a different host, the target shall overwrite or cryptographically clear the memory contents and reset the TE State to 0 for memory ranges described in extents that will be added to a host in response to an Add Dynamic Capacity command (see [Section 8.2.10.9.9.3](#page-752-3)). By overwriting those ranges and resetting the TE State, the extents that will be added shall be reset to an untrusted state to prevent stale trusted data released from one host from being exposed to a trusted entity when adding that memory to another host.

##### 11.5.4.10.2 Multiple Host Considerations

For Dynamic Capacity implementations that utilize multiple hosts, only a single host may generate transactions to a specific DPA range at any given time.

• Target shall maintain an association between the host in which the Dynamic Capacity is being added and the target that is providing the memory. The target shall not allow other hosts to access the memory until the memory has been released from the current host, at which point the host to target association is removed and the TE State is reset as described above.

• Note that implementing Dynamic Capacity on a target already requires the target to maintain this host to target association and the target shall correctly reject transactions from hosts that do not currently own the Dynamic Capacity. This behavior is described in [Section 9.13.3.](#page-843-3)

#### <span id="page-960-0"></span>11.5.4.11 HDM-DB

<span id="page-960-1"></span>The following sections describe the additional challenges with utilizing HDM-DB memory with the TSP and the resulting initiator and target requirements and behaviors needed for confidential computing with this type of memory.

With HDM-H memory the host is responsible for maintaining the cache coherency state of memory. With HDM-DB memory, the target owning the HDM-DB memory maintains the cache coherency state for the memory. The initiator and target utilize the BISnp and BIRsp channels to resolve coherency.

HDM-DB support in TSP enables the following with confidential computing:

• Target side compute

The target HDM Decoders shall be programmed before the target is locked through TSP. This allows the target to utilize the BI indicator in the programmed HDM decoders to determine if HDM-DB specific requirements and behaviors outlined here are to be utilized. It will also allow the host TEE architecture to ensure HDM-DB support is only enabled if it is capable of supporting such a configuration.

To correctly pass TEE Intent and TE State, additional request and response opcodes are required as outlined below. The new opcodes required for HMD-DB are defined in the M2S Req Memory Opcodes definitions, S2M BISnp Opcodes definitions, S2M NDR Opcodes definitions, and [Appendix C.](#page-1216-2)

For the TSP to operate correctly with the HDM-DB protocol, the following sub-sections outline additional requirements, initiator behaviors and target behaviors that define HDM-DB use with confidential computing. This includes:

- New initiator and target requirements for handling requestor cache state and TE State changes
- New M2S request opcodes to carry TEE Intent in support of HDM-DB.
  - MemInvTEE
  - MemInvP/MemInvPTEE Memory invalidation requiring precise TE State
  - MemClnEvctU Memory clean eviction with unknown TE State
  - MemClnEvctTEE
- New S2M BISnp opcodes to carry TEE Intent in support of HDM-DB.
  - BISnpCurTEE
  - BISnpDataTEE
  - BISnpInvTEE
  - BISnpCurBlkTEE
  - BISnpDataBlkTEE
  - BISnpInvBlkTEE
- New S2M NDR response opcodes to report TE State
  - MemInvP/MemInvPTEE returns Cmp, CmpTEE, CmpTEE-S, or CmpTEE-E

##### 11.5.4.11.1 Determining TSP Support with HDM-DB

A target's support of HDM-DB memory is determined by looking at the BI bit in each HDM Decoder Control Register. HDM ranges with the BI flag set are enabled for HDM-DB. The target reports support for TSP with the TSP Capable bit in the DVSEC CXL Capability register.

Targets that report HDM-DB support and are TSP capable, shall support all of the request and response opcodes that are described here.

##### 11.5.4.11.2 Requestor Coherency State (RCS)

The Requestor Coherency State (RCS) is the cache state maintained by the initiator. There are a variety of existing initiator implementations that handle RCS in fundamentally different ways. The following requirements take that into account and outline the expected initiator behaviors for maintaining RCS with HDM-DB and TSP, independent of implementation.

TSP behaviors for HDM-DB initiators:

- Initiators may update RCS without regard to the TE State. These initiators may utilize implicit and/or explicit TE State changes on the target.
- Initiators may update RCS by TE State. These initiators shall utilize explicit TE State changes on the target.
- When receiving a BISnp command, initiators may invalidate all RCS for a given address, regardless of whether the TE State specified in the BISnp command matches the TE State held in the RCS. However, initiators may safely retain RCS that does not match the TE State following a BISnp, as long as the initiator can guarantee that no internal or external entity can observe stale cache data.
- Initiators shall take additional actions (i.e. software-initiated cache flushes) to ensure RCS consistency on the target after a TE State mismatch when the target reports this requirement in the Additional Capabilities of Get Target Capabilities Response.

##### 11.5.4.11.3 Device Tracked Requestor Coherency State (DTRCS)

The Device Tracked Requestor Coherency State (DTRCS) is the initiators cache state that is maintained by the target. There are a variety of existing target implementations that handle DTRCS in fundamentally different ways. The following requirements take that into account and outline the expected initiator and target behaviors for maintaining DTRCS with HDM-DB and TSP, independent of implementation.

TSP behaviors for HDM-DB initiators and targets:

- Targets that update DTRCS after a TE State mismatch shall require no special handling.
- Targets that do not update DTRCS after a TE State mismatch shall require one of the following target behaviors:
  - When the target receives a request on the M2S Req channel that results in a TE State mismatch, the target completes the request, then issues a BISnp with the current TE State being tracked for the address in the request, and blocks all new M2S Req requests to the address (including requests internal to the device) from the time the request causing the mismatch is processed until the BISnp completion is received, OR
  - The target requires the initiator to take additional actions after a TE State mismatch occurs.
    - The target indicates this dependency by setting Initiator Actions Required Following TE State Mismatch in Get Target Capabilities Response.

- When this is indicated, the initiator is responsible for ensuring the coherency is maintained after the mismatch. Initiator responsibilities may include software-initiated target cache flushes or disallowing the mismatched line from allocating in the initiator's cache.
- Targets shall relax buried state rules to avoid unexpected state downgrade on MemRd, MemRdTEE, MemRdData, and MemRdDataTEE that result in a TE State mismatch as described in the buried state section that follows and the HDM-DB updates to [Appendix C](#page-1216-2).

##### 11.5.4.11.4 TE State Changes

TSP behaviors for HDM-DB targets:

- Targets shall support explicit and/or implicit TE State changes as specified in [Section 11.5.4.5.](#page-939-1)
- Targets shall snoop back all addresses affected by a TE State change using BISnp, before any memory contents or TE State is updated. While the snoop-back cycle is in progress:
  - The target shall block access to the affected memory (it is legal to block the request channel for short amounts of time without causing timeouts, but the RwD channel cannot be blocked without risk of deadlock), OR
  - The target shall handle the received transactions that address the same memory region that is undergoing the snoop back as a TE State mismatch and shall follow the mismatch behavior outlined in the TE State Changes and Access Control [Section 11.5.4.5](#page-939-1) and the following subsections.

TSP behaviors for HDM-DB initiators:

• Initiators that retain the data following a BISnp that was requested with a TE State mismatch, shall utilize an explicit TE State change command.

##### 11.5.4.11.5 BISnp S2M Requests with TE State

The BISnp requests are extended to encode a TE State. HDM-DB targets shall include TE State when sending BISnp. This is provided for initiators that may require accurate TE State to correctly resolve RCS for the target.

The TE State contained in the BISnp request shall match the current TE State tracked by the target for the address being snooped.

If the BISnp is occurring in response to an explicit TE update, then all the BISnp associated with the TE State update shall complete before the TE State is updated.

All HDM-DB capable targets utilizing TSP shall support reporting TE State with all BISnp request opcodes.

The following table outlines the required BISnp request opcodes the targets shall support:

| S2M Request opcode                                                                                | TEE State | Description                                         |
|---------------------------------------------------------------------------------------------------|-----------|-----------------------------------------------------|
| BISnpCur<br>BISnpData<br>BISnpInv<br>BISnpCurBlk<br>BISnpDataBlk<br>BISnpInvBlk                   | 0         | Back invalidate the memory with current TE State 0. |
| BISnpCurTEE<br>BISnpDataTEE<br>BISnpInvTEE<br>BISnpCurBlkTEE<br>BISnpDataBlkTEE<br>BISnpInvBlkTEE | 1         | Back invalidate the memory with current TE State 1. |

##### 11.5.4.11.6 MemRd M2S Requests with TEE Intent

MemRd requests shall include TEE Intent utilizing MemRd or MemRdTEE request opcodes. The intent is provided for targets that may require an accurate TE State to process the read request. The existing MemRd request is utilized for TE Intent = 0 and the new MemRdTEE request is utilized for TE Intent = 1.

All HDM-DB capable targets utilizing TSP shall support the MemRd/MemRdTEE request opcodes.

The following table outlines the required MemRd request opcodes the target shall support:

| M2S Request opcode | TEE Intent | Target behavior                |
|--------------------|------------|--------------------------------|
| MemRd              | 0          | Read memory with TEE Intent 0. |
| MemRdTEE           | 1          | Read memory with TEE Intent 1. |

##### 11.5.4.11.7 MemRd S2M Responses with TE State

MemRd/MemRdTEE S2M DRS responses shall return TE State utilizing MemData or MemDataTEE. The target shall respond with the current TE State associated with the underlying data being read.

MemRd/MemRdTEE with MetaValue I is not supported when the target has been locked with TSP. If this request is received while TSP is enabled, the target shall respond with MemData with all 1's data, optionally return poison and no TE State shall be inferred by the initiator. This allows differentiation in behavior from a valid MemRd with MetaValue I that is received when TSP is not utilized.

All HDM-DB capable targets utilizing TSP shall support the MemData/MemDataTEE responses for MemRd/MemRdTEE request opcodes.

There are additional requirements for targets that maintain DTRCS that if a TE State mismatch is detected when executing the MemRd/MemRdTEE, the target shall not degrade the final DTRCS when handling the response. See [Appendix C](#page-1216-2) for special cases for not downgrading DTRCS on a TE State mismatch.

The following table outlines the valid MemRd S2M DRS response opcodes the target shall support when the current TE State matches the TEE Intent of the MemRd:

| M2S Request opcode | Valid S2M DRS<br>Response | Target behavior                    |
|--------------------|---------------------------|------------------------------------|
| MemRd              | MemData                   | •<br>Memory read with TE State = 0 |
| MemRdTEE           | MemDataTEE                | •<br>Memory read with TE State = 1 |

The following table outlines the valid MemRd S2M DRS response opcodes the target shall support when the current TE State does not match the TEE Intent of the MemRd:

| M2S Request opcode | Valid S2M DRS<br>Response | Target behavior                                                |
|--------------------|---------------------------|----------------------------------------------------------------|
| MemRd              | MemDataTEE                | •<br>Memory read with TEE Intent = 0 resulted in a<br>mismatch |
| MemRdTEE           | MemData                   | •<br>Memory read with TEE Intent =1 resulted in a mismatch     |

##### 11.5.4.11.8 MemInv M2S Requests with TEE Intent

MemInv requests shall include TEE Intent utilizing MemInv or MemInvTEE request opcodes. TEE Intent is provided for targets that may require an accurate TE State in order to change the state of the cache line. The existing MemInv request is utilized for TEE Intent = 0 and the new MemInvTEE request is utilized for TEE Intent = 1. The TEE Intent shall indicate the intended TE State of memory following the DTRCS update.

The MemInv/MemInvTEE S2M NDR response does not convey TE State and shall not be utilized as an indicator of TE State. Initiators requiring precise TE State in the response shall utilize MemInvP/MemInvPTEE requests.

All HDM-DB capable targets utilizing TSP shall support the MemInv/MemInvTEE request opcodes.

The following table outlines the required MemInv request opcodes the target shall support:

| M2S Request opcode | TEE Intent | Target behavior                                                                                                     |
|--------------------|------------|---------------------------------------------------------------------------------------------------------------------|
| MemInv             | 0          | Invalidate the memory with TEE Intent 0. Initiator does not<br>require TE State in the response as described below. |
| MemInvTEE          | 1          | Invalidate the memory with TEE Intent 1. Initiator does not<br>require TE State in the response as described below. |

##### 11.5.4.11.9 MemInvP M2S Requests with TEE Intent

MemInvP/MemInvPTEE are new MemInv request opcodes defined to indicate the TEE Intent of the invalidate and that the initiator requires a precise TE State to accompany the MemInvP/MemInvPTEE completion response. TEE Intent is provided for targets that may require an accurate TEE Intent in order to change the DTRCS of the cacheline. The TEE Intent shall indicate the intended TE State of memory following the DTRCS update.

Initiators that retain RCS following a BISnp shall utilize MemInvP/MemInvPTEE if knowledge of the TE State being invalidated is required for that initiators cache implementation.

Targets shall determine the current TE State of the memory being invalidated before responding to these requests.

All HDM-DB capable targets utilizing TSP shall support the MemInvP/MemInvPTEE request opcodes.

The following outlines the required MemInvP request opcodes the target shall support:

| M2S Request opcode | TEE Intent | Target behavior                                                                                                |
|--------------------|------------|----------------------------------------------------------------------------------------------------------------|
| MemInvP            | 0          | <ul><li>Invalidate the memory with TEE Intent 0</li><li>Report the precise TE State in the response.</li></ul> |
| MemInvPTEE         | 1          | <ul><li>Invalidate the memory with TEE Intent 1</li><li>Report the precise TE State in the response</li></ul>  |

##### 11.5.4.11.10 MemInv & MemInvP S2M Responses with TE State

MemInvP/MemInvPTEE S2M NDR responses shall return TE State utilizing Cmp or CmpTEE. The target shall respond with the current TE State associated with the underlying data being invalidated. This may require the responding target to look up the TE State prior to completing the MemInv request even though no data will be returned.

All HDM-DB capable targets utilizing TSP shall support the Cmp/CmpTEE responses for MemInvP/MemInvPTEE request opcodes.

The following table outlines the valid MemInv S2M NDR response opcodes the target shall support when the current TE State matches the TEE Intent of the MemInv:

| M2S Request opcode | Valid S2M NDR<br>Response      | Target behavior                                                |
|--------------------|--------------------------------|----------------------------------------------------------------|
| MemInv             | Cmp<br>Cmp-S<br>Cmp-E          | Memory invalidated     Return no TE State in the response      |
| MemInvTEE          |                                |                                                                |
| MemInvP            | Cmp<br>Cmp-S<br>Cmp-E          | Memory invalidated     Return current TE State in the response |
| MemInvPTEE         | CmpTEE<br>CmpTEE-S<br>CmpTEE-E |                                                                |

The following table outlines the valid MemInv S2M NDR response opcodes the target shall support when the current TE State does not match the TEE Intent of the MemInv:

| M2S Request opcode | Valid S2M NDR<br>Response      | Target behavior                                                                                                                                                              |
|--------------------|--------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| MemInv             | Cmp<br>Cmp-S<br>Cmp-E          | Memory invalidated (since precise TE State is not required there is no reason not to invalidate the memory for the mismatch case)     Return Cmp     Optionally log an event |
| MemInvTEE          |                                |                                                                                                                                                                              |
| MemInvP            | CmpTEE<br>CmpTEE-S<br>CmpTEE-E | Do not invalidate the memory     Return current TE State     Optionally log an event                                                                                         |
| MemInvPTEE         | Cmp<br>Cmp-S<br>Cmp-E          |                                                                                                                                                                              |

**11.5.4.11.11MemRdData M2S Req Requests with TEE Intent**

MemRdData requests shall include TEE Intent utilizing MemRdData or MemRdDataTEE request opcodes. The intent is provided for targets that may require an accurate TE State to process the read request. The existing MemRdData request is utilized for TE Intent = 0 and the new MemRdDataTEE request is utilized for TE Intent = 1.

All HDM-DB capable targets utilizing TSP shall support the MemRdData/MemRdDataTEE request opcodes.

The following table outlines the required MemRdData request opcodes the target shall support:

| M2S Request opcode | TEE Intent | Target behavior                |
|--------------------|------------|--------------------------------|
| MemRdData          | 0          | Read memory with TEE Intent 0. |
| MemRdDataTEE       | 1          | Read memory with TEE Intent 1. |

**11.5.4.11.12MemRdData S2M DRS Responses with TE State**

MemRdData/MemRdDataTEE S2M DRS responses shall return TE State utilizing MemData or MemDataTEE. The target shall respond with the current TE State associated with the underlying data being read.

All HDM-DB capable targets utilizing TSP shall support the MemData/MemDataTEE responses for MemRdData/MemRdDataTEE request opcodes.

There are additional requirements for targets that maintain DTRCS that if a TE State mismatch is detected when executing the MemRdData/MemRdDataTEE, the target shall not degrade the final DTRCS when handling the response. See [Appendix C](#page-1216-2) for special cases for not downgrading DTRCS on a TE State mismatch.

The following table outlines the valid MemRdData S2M DRS response opcodes the target shall support when the current TE State matches the TEE Intent of the MemRdData:

| M2S Request opcode | Valid S2M DRS<br>Response | Target behavior                    |
|--------------------|---------------------------|------------------------------------|
| MemRdData          | MemData                   | •<br>Memory read with TE State = 0 |
| MemRdDataTEE       | MemDataTEE                | •<br>Memory read with TE State = 1 |

The following table outlines the valid MemRdData S2M DRS response opcodes the target shall support when the current TE State does not match the TEE Intent of the MemRdData:

| M2S Request opcode | Valid S2M DRS<br>Response | Target behavior                                                 |
|--------------------|---------------------------|-----------------------------------------------------------------|
| MemRdData          | MemDataTEE                | •<br>Memory read with TEE Intent = 0 resulted in a mis<br>match |
| MemRdDataTEE       | MemData                   | •<br>Memory read with TEE Intent = 1 resulted in a<br>mismatch  |

**11.5.4.11.13MemSpecRd M2S Req Requests with TEE Intent**

MemSpecRd requests shall include TEE Intent utilizing MemSpecRd or MemSpecRdTEE request opcodes. The intent is provided for targets that may require an accurate TE State to process the speculative read request. The existing MemSpecRd request is utilized for TEE Intent = 0 and the new MemSpecRdTEE request is utilized for TEE Intent = 1.

All HDM-DB capable targets utilizing TSP shall support the MemSpecRd/MemSpecRdTEE request opcodes.

The following table outlines the required MemSpecRd request opcodes the target shall support:

| M2S Request opcode | TEE Intent | Target behavior                              |
|--------------------|------------|----------------------------------------------|
| MemSpecRd          | 0          | Speculatively read memory with TEE Intent 0. |
| MemSpecRdTEE       | 1          | Speculatively read memory with TEE Intent 1. |

**11.5.4.11.14MemClnEvct M2S Req Requests without TEE Intent**

MemClnEvctU is a new memory request opcode that may be utilized by initiators that don't know the TE State of the memory being clean evicted. The MemClnEvctU M2S req request does not convey TE State and shall not be utilized as an indicator of TE State.

Initiators should avoid MemClnEvctU and should utilize MemClnEvct or MemClnEvctTEE whenever possible for best performance. Initiators that utilize MemClnEvctU shall not track TE State when maintaining RCS.

HDM-DB targets that require an accurate TE State in order to process eviction requests and receive MemClnEvctU may evict utilizing current TE State, may evict both TE States, or may not evict anything. Initiators that require specific target behavior should utilize MemClnEvct or MemClnEvctTEE.

Targets should take extra measures to find and clean the DTRCS associated with the eviction request since failure to complete a clean eviction may result in extra BISnp requests, potentially impacting system performance.

All HDM-DB capable targets utilizing TSP shall support the MemClnEvctU.

**11.5.4.11.15MemClnEvct M2S Req Requests with TEE Intent**

MemClnEvct requests shall include TE Intent utilizing MemClnEvct or MemClnEvctTEE request opcodes. TEE Intent is provided for targets that may require the TE State in order to process the eviction request and reset the state of the cacheline. The MemClnEvct request is utilized for TEE Intent 0 and the request MemClnEvctTEE is utilized for TEE Intent 1.

All HDM-DB capable targets utilizing TSP shall support the MemClnEvct and MemClnEvctTEE request opcodes.

The following table outlines the required MemClnEvct request opcodes that target shall support:

| M2S Request opcode | TEE Intent | Target behavior                             |  |  |  |
|--------------------|------------|---------------------------------------------|--|--|--|
| MemClnEvctU        | N/A        | Perform clean evict independent of TE State |  |  |  |
| MemClnEvct         | 0          | Perform clean evict using TEE Intent 0      |  |  |  |
| MemClnEvctTEE<br>1 |            | Perform clean evict using TEE Intent 1      |  |  |  |

**11.5.4.11.16MemClnEvct S2M NDR Responses with TE State**

Since MemClnEvctU/MemClnEvct/MemClnEvctTEE are provided for performance and not correctness, none of these requests require TE State to be reported in the response.

The following table outlines the valid MemClnEvct S2M NDR response opcodes the target shall support when the current TE State matches or mismatches the TEE Intent of the MemClnEvct:

| M2S Request opcode | Valid S2M NDR<br>Response                                      | Target behavior                                         |  |
|--------------------|----------------------------------------------------------------|---------------------------------------------------------|--|
| MemClnEvctU        |                                                                | The current state of the memory evicted is unknown      |  |
| MemClnEvct         | Cmp<br>The current state of the memory evicted is TE State = 0 |                                                         |  |
| MemClnEvctTEE      |                                                                | The current state of the memory evicted is TE State = 1 |  |

**11.5.4.11.17Buried State Behavior**

For targets that maintain DTRCS and support TE State tracking, if the target detects a TE State mismatch when the initiator is requesting S state, shall not downgrade the final DTRCS. MemRd, MemRdTEE and MemRdData, MemRdDataTEE shall not downgrade DTRCS for a TE State mismatch and is outlined in [Appendix C.](#page-1216-2)

Targets that don't update DTRCS after a TE State mismatch and rely on additional host actions to correct RCS may leave the final device cache and/or DTRCS unchanged after the mismatch occurs, relying on software actions to correct any coherency issues. See the "UCM" cases in the Device Cache and DTRCS columns of [Appendix C.](#page-1216-2)

### <span id="page-968-0"></span>11.5.5 TSP Requests and Responses

<span id="page-968-3"></span>Each TSP Request sent over the secure CMA/SPDM session shall result in exactly one TSP Response, the Delayed Response if the request will take significant time to complete, or the Error Response if the request could not be executed.

#### <span id="page-968-1"></span>11.5.5.1 TSP Request Overview

[Table 11-27](#page-968-2) outlines the TSP Request payloads, defined in the sections that follow.

<span id="page-968-2"></span>**Table 11-27. TSP Request Overview (Sheet 1 of 2)**

| TSP Request Message |                                 | Message<br>Support1        | Payload |                                           |                    |
|---------------------|---------------------------------|----------------------------|---------|-------------------------------------------|--------------------|
| Opcode              | Name                            | HDM-H<br>HDM-DB<br>Devices | Size    | Legal TSP State                           | TSP Usage          |
| 81h                 | Get Target TSP Version          |                            | 4       | CONFIG_UNLOCKED<br>CONFIG_LOCKED<br>ERROR |                    |
| 82h                 | Get Target Capabilities         |                            | 4       |                                           |                    |
| 83h                 | Set Target Configuration        | M                          | C2h+    | CONFIG_UNLOCKED                           | Target config      |
| 84h                 | Get Target Configuration        |                            | 4       | CONFIG_UNLOCKED<br>CONFIG_LOCKED          |                    |
| 85h                 | Get Target Configuration Report |                            | 8       |                                           |                    |
| 86h                 | Lock Target Configuration       |                            | 4       | CONFIG_UNLOCKED                           | Target config lock |

Table 11-27. TSP Request Overview (Sheet 2 of 2)

| TSP Request Message |                                 | Message<br>Support <sup>1</sup>           | Payload |                 |                                                     |
|---------------------|---------------------------------|-------------------------------------------|---------|-----------------|-----------------------------------------------------|
| Opcode              | Name                            | HDM-H<br>HDM-DB<br>Devices                | Size    | Legal TSP State | TSP Usage                                           |
| 87h                 | Set Target CKID Specific Key    | O - CKID-based                            | 10h+    | CONFIG_LOCKED   | Runtime CKID-based target memory encryption         |
| 88h                 | Set Target CKID Random Key      | target memory                             | 10h+    |                 |                                                     |
| 89h                 | Clear Target CKID Key           | encryption                                | 8       |                 |                                                     |
| 8Ah                 | Set Target Range Specific Key   | O - Range-based                           | 20h+    |                 | Runtime range-based target memory encryption        |
| 8Bh                 | Set Target Range Random Key     | target memory                             | 20h+    |                 |                                                     |
| 8Ch                 | Clear Target Range Key          | encryption                                | 8       |                 |                                                     |
| 8Dh                 | Set Target TE State             | O - Explicit TE<br>State changes          | 20h+    |                 | Runtime explicit state changes                      |
| 8Eh                 | Check Target Delayed Completion | O - Delayed<br>completion of a<br>request | 4       |                 | Checking for completion of a long executing request |

<sup>1.</sup> M = Mandatory message, O = Optional message. Targets shall return a Error Response of Unsupported Request if the target does not support the request.

#### <span id="page-969-0"></span>11.5.5.2 TSP Response Overview

Table 11-28 outlines the TSP Response payloads, defined in the sections that follow.

<span id="page-969-1"></span>Table 11-28. TSP Response Overview

| TSP Response Message |                                          | Message Support <sup>1</sup>             |                             |  |
|----------------------|------------------------------------------|------------------------------------------|-----------------------------|--|
| Opcode               | Name                                     | HDM-H<br>HDM-DB<br>Devices               | Payload Size                |  |
| 01h                  | Get Target TSP Version Response          |                                          | 5+                          |  |
| 02h                  | Get Target Capabilities Response         |                                          | 34h                         |  |
| 03h                  | Set Target Configuration Response        | M                                        | 4                           |  |
| 04h                  | Get Target Configuration Response        | IVI                                      | COh                         |  |
| 05h                  | Get Target Configuration Report Response |                                          | 8+                          |  |
| 06h                  | Lock Target Configuration Response       |                                          | 4                           |  |
| 07h                  | Set Target CKID Specific Key Response    |                                          | 4                           |  |
| 08h                  | Set Target CKID Random Key Response      | O - CKID-based target memory encryption  | 4                           |  |
| 09h                  | Clear Target CKID Key Response           | 3 - 3                                    | 4                           |  |
| 0Ah                  | Set Target Range Specific Key Response   |                                          | 4                           |  |
| 0Bh                  | Set Target Range Random Key Response     | O - Range-based target memory encryption | 4                           |  |
| 0Ch                  | Clear Target Range Key Response          |                                          | 4                           |  |
| 0Dh                  | Set Target TE State Response             | O - Explicit TE State changes            | 4                           |  |
| 0Eh                  | Check Target Delayed Completion Response | O - Delayed completion of                | O - Delayed completion of 4 |  |
| 7Eh                  | Delayed Response                         | a request                                | 8                           |  |
| 7Fh                  | Error Response                           | M                                        | 0Ch+                        |  |

<sup>1.</sup> M = Mandatory message, O = Optional message.

#### <span id="page-970-0"></span>11.5.5.3 Request Response and CMA/SPDM Sessions

Table 11-29 outlines which TSP-defined Request and Response payloads are allowed on a given TSP-defined CMA/SPDM session and which are prohibited.

<span id="page-970-2"></span>**Table 11-29. TSP Request Response and CMA/SPDM Sessions**

| TSP Request Response Message                                                | SPDM<br>PrimarySession | SPDM<br>SecondarySession(s) | Other<br>non-TSP-related<br>SPDM Session |
|-----------------------------------------------------------------------------|------------------------|-----------------------------|------------------------------------------|
| Get Target TSP Version<br>Get Target TSP Version Response                   |                        | Allowed                     | Allowed                                  |
| Get Target Capabilities<br>Get Target Capabilities Response                 |                        | Allowed                     | Allowed                                  |
| Set Target Configuration<br>Set Target Configuration Response               |                        | Prohibited                  | Prohibited                               |
| Get Target Configuration<br>Get Target Configuration Response               |                        | Allowed                     | Prohibited                               |
| Get Target Configuration Report<br>Get Target Configuration Report Response |                        | Allowed                     | Prohibited                               |
| Lock Target Configuration<br>Lock Target Configuration Response             |                        | Prohibited                  | Prohibited                               |
| Set Target TE State<br>Set Target TE State Response                         |                        | Allowed                     | Prohibited                               |
| Check Target Delayed Completion<br>Check Target Delayed Completion Response | Allowed                | Allowed                     | Prohibited                               |
| Set Target CKID Specific Key<br>Set Target CKID Specific Key Response       |                        | Allowed                     | Prohibited                               |
| Set Target CKID Random Key<br>Set Target CKID Random Key Response           |                        | Allowed                     | Prohibited                               |
| Clear Target CKID Key<br>Clear Target CKID Key Response                     |                        | Allowed                     | Prohibited                               |
| Set Target Range Specific Key<br>Set Target Range Specific Key Response     |                        | Allowed                     | Prohibited                               |
| Set Target Range Random Key<br>Set Target Range Random Key Response         |                        | Allowed                     | Prohibited                               |
| Clear Target Range Key<br>Clear Target Range Key Response                   |                        | Allowed                     | Prohibited                               |
| Delayed Response                                                            |                        | Allowed                     | Allowed                                  |
| Error Response                                                              |                        | Allowed                     | Allowed                                  |

#### <span id="page-970-1"></span>11.5.5.4 Version

##### 11.5.5.4.1 TSP Version Negotiation

The PrimarySession shall be utilized to perform the following process to negotiate TSP version with TSP-capable targets:

- Initiator shall send Get Target TSP Version request with Major Version Number = 1h.
- DSM shall support Get Target TSP Version request with Major Version Number = 1h and shall return Get Target TSP Version Response with a list of all supported versions.
- Initiator shall select a common (typically highest) version supported and utilize this version number in all subsequent messages to the target.

• Initiator shall not issue requests to the target other than Get Target TSP Version until the initiator has received a successful Get Target TSP Version Response and selected a common version that is supported by both the initiator and the target.

##### 11.5.5.4.2 Get Target TSP Version

The initiator shall utilize Get Target TSP Version to discover the TSP versions that the target supports.

Possible Error Response, Error Codes:

• None

<span id="page-971-1"></span>**Table 11-30. Get Target TSP Version**

| Byte<br>Offset | Length<br>in Bytes | Description                           |
|----------------|--------------------|---------------------------------------|
| 00h            | 1                  | TSP Version: V1.0 = 10h.              |
| 01h            | 1                  | Opcode: Get Target TSP Version = 81h. |
| 02h            | 2                  | Reserved                              |

##### 11.5.5.4.3 Get Target TSP Version Response

If no error condition is detected, the DSM shall respond to the Get Target TSP Version with a Get Target TSP Version Response message.

<span id="page-971-2"></span>**Table 11-31. Get Target TSP Version Response**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                     |  |
|----------------|--------------------|-------------------------------------------------------------------------------------------------------------------------------------------------|--|
| 00h            | 1                  | TSP Version: V1.0 = 10h.                                                                                                                        |  |
| 01h            | 1                  | Opcode: Get Target TSP Version Response= 01h.                                                                                                   |  |
| 02h            | 2                  | Reserved                                                                                                                                        |  |
| 04h            | 1                  | Version Number Entry Count: The number of version entries, N, that follow. Shall be<br>> 0.                                                     |  |
| 05h            | N                  | Version Number Entry: 8-bit version entry formatted as:<br>•<br>Bits[7:4]: Major Version Number = 1<br>•<br>Bits[3:0]: Minor Version Number = 0 |  |

#### <span id="page-971-0"></span>11.5.5.5 Target Capabilities

The following request and response payload defines the TSP security features that the target supports.

##### 11.5.5.5.1 Get Target Capabilities

Any SPDM session may utilize the Get Target Capabilities request to discover the target's memory encryption, access control, and configuration capabilities.

Possible Error Response, Error Codes:

• Version Mismatch

<span id="page-972-0"></span>**Table 11-32. Get Target Capabilities**

| Byte<br>Offset | Length<br>in Bytes | Description                            |
|----------------|--------------------|----------------------------------------|
| 00h            | 1                  | TSP Version: V1.0 = 10h.               |
| 01h            | 1                  | Opcode: Get Target Capabilities = 82h. |
| 02h            | 2                  | Reserved                               |

##### 11.5.5.5.2 Get Target Capabilities Response

If no error condition is detected, the DSM shall respond to the Get Target Capabilities request with a Get Target Capabilities Response message.

<span id="page-972-1"></span>**Table 11-33. Get Target Capabilities Response (Sheet 1 of 3)**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
|----------------|--------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 00h            | 1                  | TSP Version: V1.0 = 10h.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| 01h            | 1                  | Opcode: Get Target Capabilities Response = 02h.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| 02h            | 2                  | Memory Encryption Features Supported: Memory encryption related features that the target<br>supports. Zero or more bits may be set. 1 indicates supported, 0 indicates not supported.<br>•<br>Bit[0]: Encryption: When set, memory encryption for data at rest is implemented on the target.<br>•<br>Bit[1]: CKID-based Encryption: When set, the target supports the CKID-based TSP requests and<br>responses for memory encryption, Encryption shall be set, and the CKID Base Required and Number<br>of CKIDs fields shall be valid. When cleared, the target does not support the CKID field in Transaction<br>Layer requests.<br>•<br>Bit[2]: Range-based Encryption: When set, the target supports the range-based TSP requests and<br>responses, Encryption shall also be set, and Memory Encryption Number of Range Based Keys shall<br>be valid.<br>•<br>Bit[3]: Initiator Supplied Entropy: The target supports initiator-supplied entropy when generating<br>a random key.<br>•<br>Bit[4]: CKID Base Required: Valid only when CKID-based Encryption is set. When set, the target<br>requires a CKID Base and Number of CKIDs to be programmed. When cleared, the target supports<br>any CKID value within the 13-bit field.<br>•<br>Bits[15:5]: Reserved. |
| 04h            | 4                  | Memory Encryption Algorithms Supported: Valid only if Encryption is set in Memory Encryption<br>Features Supported. 1 indicates supported, 0 indicates not supported. If target memory encryption is<br>supported, one or more bits shall be set.<br>•<br>Bit[0]: AES-XTS-128<br>•<br>Bit[1]: AES-XTS-256<br>•<br>Bits[30:2]: Reserved<br>•<br>Bit[31]: Vendor Specific Algorithm: When set, all other bits in this field are vendor specific<br>Memory Encryption Number of Range Based Keys: Valid only if Range-based Encryption is set in                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| 08h            | 2                  | Memory Encryption Features Supported. This is the maximum Range ID that can be utilized with the<br>range-based memory encryption requests. Targets that do not support range-based memory encryption<br>shall report 0.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| 0Ah            | 2                  | Reserved                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |

**Table 11-33. Get Target Capabilities Response (Sheet 2 of 3)**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
|----------------|--------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0Ch            | 2                  | TE State Change and Access Control Features Supported: The TE State change and access control<br>features that the target supports. Zero or more bits may be set. 1 indicates supported, 0 indicates not<br>supported.<br>•<br>Bit[0]: Write Access Control: When set, indicates that the target supports dropping writes that fail<br>the verification of TEE Intent to stored TE State. When set, explicit state changes shall be supported<br>and one or more of bits[4:3] shall also be set.<br>•<br>Bit[1]: Read Access Control: When set, indicates that the target supports returning all 1s for read<br>data in response to reads that fail the verification of TEE Intent to stored TE State. When set, one or<br>more of bits[4:2] shall also be set.<br>•<br>Bit[2]: Implicit TE State Change: When set, indicates that the target supports implicit TE State<br>changes using a 64B granularity, Explicit In-band TE State Change shall be set, and Explicit In-band<br>TE State Granularity support for 64B shall be set.<br>•<br>Bit[3]: Explicit Out-of-band TE State Change: When set, indicates that the target supports the<br>CMA/SPDM out-of-band explicit Set Target TE State change message and the Supported Explicit Out<br>of-band TE State Granularity field shall be valid. Support is optional for targets that support implicit<br>TE State changes or explicit in-band TE State changes.<br>•<br>Bit[4]: Explicit In-band TE State Change: When set, indicates that the target supports explicit TE<br>State changes utilizing the TEUpdate memory transaction and the Supported Explicit In-band TE<br>State Granularity field shall be valid. Support is required for targets that support implicit TE State<br>changes and optional for targets that support explicit out-of-band TE State changes.<br>•<br>Bit[5]: Explicit TE State Change Sanitize: When set, indicates that the target supports overwriting<br>data that is affected by the explicit state change with 0s when the explicit request is received and<br>before the change is considered complete by the target. When set, one or more of bits[4:3] shall also<br>be set.<br>•<br>Bits[15:6]: Reserved. |
| 0Eh            | 1                  | Additional Capabilities: Other security related features and capabilities of the target.<br>•<br>Bit[0]: Initiator Actions Required Following TE State Mismatch: When set, indicates that the HDM-DB<br>capable target will require initiator actions (i.e. software-initiated cache flushes) to ensure correct<br>DTRCS is maintained on the target following a TE State mismatch. When clear, the target does not<br>require additional initiator actions to maintain DTRCS following a TE State mismatch. This bit is only<br>valid if the target reports Device Coherent for Supported Coherency Models in the HDM Decoder<br>Capability Register and BI is supported in the HDM Decoder Control Register.<br>•<br>Bits[7:1]: Reserved.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| 0Fh            | 1                  | Reserved                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| 10h            | 4                  | Supported Explicit Out-of-band TE State Granularity: The granularity the target supports for explicit<br>out-of-band TE State changes and verification in powers of 2, starting with 64B. Valid only if Explicit Out<br>of-band TE State Change is set in TE State Change and Access Control Features Supported. One or more<br>bits shall be set. 1 indicates target support, 0 indicates no target support.<br>•<br>Bit[0]: 64B<br>•<br>…<br>•<br>Bit[6]: 4K<br>•<br>…<br>•<br>Bit[15]: 2MB<br>•<br>…<br>•<br>Bit[24]: 1GB<br>•<br>…<br>•<br>Bit[31]: 128GB                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |

**Table 11-33. Get Target Capabilities Response (Sheet 3 of 3)**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
|----------------|--------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 14h            | 4                  | Supported Explicit In-band TE State Granularity: The granularity the target supports for explicit in<br>band TE State changes and verification in powers of 2 starting with 64B. Valid only if Explicit In-band TE<br>State Change is set in TE State Change and Access Control Features Supported. One or more bits shall be<br>set. 1 indicates target support, 0 indicates no target support.<br>•<br>Bit[0]: 64B<br>•<br>Bit[1]: 128B<br>•<br>Bit[2]: 256B<br>•<br>Bit[3]: 512B<br>•<br>Bit[4]: 1KB<br>•<br>Bit[5]: 2KB<br>•<br>Bit[6]: 4KB<br>•<br>Bit[7]: 8KB<br>•<br>Bit[8]: 16KB<br>•<br>Bit[9]: 32KB<br>•<br>Bit[10]: 64KB<br>•<br>Bits[30:11]: Reserved<br>•<br>Bit[31]: The entire memory space of the device. When set, the target supports TEUpdate using<br>Length Index 7 to change the TE State for the entire address range. When cleared, the target does<br>not support use of Length Index value of 7. |
| 18h            | 2                  | Configuration Features Supported: The configuration features that the target supports. Zero or more<br>bits may be set. 1 indicates supported, 0 indicates not supported.<br>•<br>Bit[0]: Locked Target FW Update: When set, the target supports FW updates after the target is<br>locked. When cleared to 0, the target does not support FW updates after the target is locked.<br>•<br>Bit[1]: Target Supports Additional CMA/SPDM Sessions: The target supports using CMA/SPDM<br>PSK to set up one or more SecondarySession(s). If this bit is set, then Number of Secondary Sessions<br>shall be valid. When cleared, the target does not support secondary SPDM sessions.<br>•<br>Bits[15:2]: Reserved.                                                                                                                                                                                                              |
| 1Ah            | 2                  | Reserved                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| 1Ch            | 4                  | Number of CKIDs: Total number of CKIDs that the target supports. Valid only if CKID-based Encryption<br>is set in Memory Encryption Features Supported. Shall be >=2 and < 2^13.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| 20h            | 1                  | Number of Secondary Sessions: Total number of additional SPDM SecondarySessions that the target<br>supports. When valid, this shall be > 0 and <= 4.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| 21h            | 13h                | Reserved                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |

#### <span id="page-974-0"></span>11.5.5.6 Target Configuration

The following request and response payloads provide TSP configuration, locking, and register reporting of the target.

##### 11.5.5.6.1 Set Target Configuration

The PrimarySession is utilized with the Set Target Configuration request to place the target in the preferred transport configuration. This includes providing SecondarySession CMA/SPDM PSK Key Material that shall be utilized by the Target to generate random keys for this additional session.

Possible Error Response, Error Codes:

- Version Mismatch
- Invalid Request
  - Entropy was not supplied
  - Number of CKIDs being enabled is > Number of CKIDs the target reported in Get Target Configuration
  - CKID Base is >= 2 ^ 13

- CKID Base + Number of CKIDs >= 2^13
- TE State Granularity specified is not supported by the target
- Length Indexes are not unique
- Length Index 0 or 7 was specified but the TE State Granularity was not 0
- Implicit TE State Change is enabled and Explicit In-band TE State Change is not enabled or no Explicit In-band TE State Granularity Entries enable Length Index 0
- CKID-based Encryption and Range-based Encryption are both enabled
- Write Access Control and Implicit TE State Change are both enabled
- No Privilege
  - A PrimarySession is already established and this request was not received on the PrimarySession
  - If Transport Security is required with TSP: A Transport Security session is already established, and this request was not received on that session
- Invalid Security State
- Target not in CONFIG\_UNLOCKED state

The following structure shall be utilized for associating explicit TE State lengths to specific indexes that are utilized with the TEUpdate memory transaction. Implementations that do not utilize explicit in-band TE State changes do not need to include valid information in the response payload for these entries.

<span id="page-975-0"></span>**Table 11-34. Explicit In-band TE State Granularity Entry**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
|----------------|--------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 00h            | 8                  | TE State Granularity: The number of bytes of contiguous HPA space to which the explicit in-band TE<br>state change will apply when the TEUpdate memory transaction is received by the target. Shall be one<br>of the values reported by the target in Supported Explicit In-band TE State Granularity reported in Get<br>Target Capabilities. When specifying Length Index 0 or 7, this field shall be 0 because the length is<br>predefined. This field is ignored when Length Index is FFh. |
| 08h            | 1                  | Length Index: The 3-bit length index that shall be utilized to represent the TE State Length in the<br>SnpType portion of the TEUpdate memory transaction. Value shall be >= 0 and <= 7 for valid Explicit<br>In-band TE State Granularity Entries. Each length entry specified shall utilize a unique Length Index.<br>Value FFh is reported for unused Explicit In-band TE State Granularity Entries.                                                                                       |
| 09h            | 7                  | Reserved                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |

<span id="page-975-1"></span>**Table 11-35. Set Target Configuration (Sheet 1 of 4)**

| Byte<br>Offset | Length<br>in Bytes | Description                             |
|----------------|--------------------|-----------------------------------------|
| 000h           | 1                  | TSP Version: V1.0 = 10h.                |
| 001h           | 1                  | Opcode: Set Target Configuration = 83h. |

**Table 11-35. Set Target Configuration (Sheet 2 of 4)**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
|----------------|--------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 002h           | 2                  | Memory Encryption Features Enable: Enable the memory encryption features for the target. Zero or<br>more bits may be set. 1 indicates to enable, 0 indicates to disable.<br>•<br>Bit[0]: Encryption: When set, memory encryption for data at rest shall be enabled on the target.<br>When cleared, target memory encryption shall be disabled.<br>•<br>Bit[1]: CKID-based Encryption: When set, CKID-based encryption shall be enabled on the target,<br>Encryption shall be set, and the CKID Base Required field shall be valid. When set, Range-based<br>Encryption shall be cleared. When cleared, the target shall disable use of the CKID field in the<br>Transaction Layer requests.<br>•<br>Bit[2]: Range-based Encryption: When set, range-based encryption shall be enabled on the target<br>and Encryption shall also be set. When set, CKID-based Encryption shall be cleared. When cleared,<br>the target shall disable use of range-based target memory encryption.<br>•<br>Bit[3]: CKID Base Required: Valid only when CKID-based Encryption is set. When set, the target<br>shall enable a valid CKID range and CKID Base and Number of CKIDs fields shall be valid. When<br>cleared, the target shall enable any CKID value within the 13-bit field.<br>•<br>Bits[15:4]: Reserved.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| 004h           | 4                  | Memory Encryption Algorithm Select: Valid only if Encryption is set in Memory Encryption Features<br>Enable. Select the target memory encryption algorithm to utilize. Only one bit shall be set. 1 indicates<br>selected, 0 indicates not selected.<br>•<br>Bit[0]: AES-XTS-128<br>•<br>Bit[1]: AES-XTS-256<br>•<br>Bits[30:2]: Reserved<br>•<br>Bit[31]: Vendor Specific Algorithm: When set, all other bits in this field are vendor specific                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| 008h           | 4                  | Reserved                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| 00Ch           | 2                  | TE State Change and Access Control Features Enable: Enable the TE State change and access<br>control features for the target. Zero or more bits may be set. 1 indicates to enable, 0 indicates to disable.<br>•<br>Bit[0]: Write Access Control: When set, the target shall enable dropping writes that fail the<br>verification of TEE Intent to stored TE State. When set, explicit state changes shall be enabled, one or<br>more of bits[4:3] shall also be set and Implicit TE State Change shall be cleared.<br>•<br>Bit[1]: Read Access Control: When set, the target shall enable returning all 1s for read data in<br>response to reads that fail the verification of TEE Intent to stored TE State. When set, one or more of<br>bits[4:2] shall also be set.<br>•<br>Bit[2]: Implicit TE State Change: When set, implicit TE State changes shall be enabled on the<br>target using 64B granularity, Explicit In-band TE State Change shall be set, at least one Explicit In<br>band TE State Granularity Entry with Length Index 0 shall be enabled, and Write Access Control shall<br>be cleared. When cleared, implicit TE State changes shall be disabled on the target.<br>•<br>Bit[3]: Explicit Out-of-band TE State Change: When set, the target shall be enabled to utilize the<br>explicit CMA/SPDM out-of-band explicit Set Target TE State change request and Explicit Out-of-band<br>TE State Change Granularity shall be valid.<br>•<br>Bit[4]: Explicit In-band TE State Change: When set, the target shall be enabled for explicit in<br>band TE State changes utilizing the TEUpdate memory transaction and Explicit In-band TE State<br>Change Granularity Entries shall be valid.<br>•<br>Bit[5]: Explicit TE State Change Sanitize: When set, the target shall be enabled to overwrite data<br>that is affected by the explicit state change with 0s when the explicit request is received and before<br>the change is considered complete by the target. When set, one or more of bits[4:3] shall also be set.<br>•<br>Bits[15:6]: Reserved. |
| 00Eh           | 2                  | Reserved                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| 010h           | 4                  | Explicit Out-of-band TE State Granularity: The granularity that the initiator is requesting the target to<br>utilize for explicit out-of-band TE State changes in powers of 2, starting with 64B. Valid only if Explicit<br>Out-of-band TE State Change is set in TE State Change and Access Control Features Enable. Only one bit<br>shall be set. 1 indicates target shall enable, 0 indicates target shall disable.<br>•<br>Bit[0]: 64B<br>•<br>…<br>•<br>Bit[6]: 4 KB<br>•<br>…<br>•<br>Bit[15]: 2 MB<br>•<br>…<br>•<br>Bit[24]: 1 GB<br>•<br>…<br>•<br>Bit[31]: 128 GB                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |

**Table 11-35. Set Target Configuration (Sheet 3 of 4)**

| 014h<br>4<br>Reserved<br>be set. 1 indicates to enable, 0 indicates to disable.<br>•<br>locked. When cleared, the target shall disable FW updates after the target is locked.<br>•<br>018h<br>2<br>as general-purpose memory. Accelerator devices shall set this to indicate the exposed memory<br>EFI Memory Type and Attribute of EfiConventionalMemory EFI_MEMORY_SP for the corresponding<br>general-purpose memory.<br>•<br>Bits[15:2]: Reserved.<br>01Ah<br>2<br>Reserved<br>CKID Base: The lowest CKID that the target shall enable. Valid only if CKID Base Required is set in<br>01Ch<br>4<br>Memory Encryption Features Enable. Shall be < 2^13.<br>Number of CKIDs: Number of contiguous CKID that the target shall enable starting at the CKID Base.<br>020h<br>4<br>Valid only if CKID Base Required is set in Memory Encryption Features Enable. Shall be <= Number of<br>CKIDs reported by the target in Get Target Capabilities. CKID Base + Number of CKIDs shall be < 2^13.<br>024h<br>0Ch<br>Reserved<br>030h<br>10h<br>Explicit In-band TE State Granularity Entry 0<br>040h<br>10h<br>Explicit In-band TE State Granularity Entry 1<br>050h<br>10h<br>Explicit In-band TE State Granularity Entry 2<br>060h<br>10h<br>Explicit In-band TE State Granularity Entry 3<br>070h<br>10h<br>Explicit In-band TE State Granularity Entry 4<br>080h<br>10h<br>Explicit In-band TE State Granularity Entry 5<br>090h<br>10h<br>Explicit In-band TE State Granularity Entry 6<br>0A0h<br>10h<br>Explicit In-band TE State Granularity Entry 7<br>0B0h<br>10h<br>Reserved<br>Configuration Validity Flags: Indicators of which fields are valid in the remaining portion of this<br>request. Zero or more bits may be set.<br>•<br>Bit[0]: Secondary Session 0: When set, the Secondary Session 0 PSK Key Material field and<br>a key for use when a SecondarySession0 is created utilizing CMA/SPDM PSK. When cleared, no<br>SecondarySession0 is allowed by the target. This bit shall be set only if Get Target Capabilities,<br>Number of Secondary Sessions is > 0.<br>•<br>Bit[1]: Secondary Session 1: When set, the Secondary Session 1 PSK Key Material field and<br>a key for use when a SecondarySession1 is created utilizing CMA/SPDM PSK. When cleared, no<br>SecondarySession1 is allowed by the target. This bit shall be set only if Get Target Capabilities,<br>Number of Secondary Sessions is > 1.<br>0C0h<br>2<br>•<br>Bit[2]: Secondary Session 2: When set, the Secondary Session 2 PSK Key Material field and<br>a key for use when a SecondarySession2 is created utilizing CMA/SPDM PSK. When cleared, no<br>SecondarySession2 is allowed by the target. This bit shall be set only if Get Target Capabilities,<br>Number of Secondary Sessions is > 2.<br>•<br>Bit[3]: Secondary Session 3: When set, the Secondary Session 3 PSK Key Material field and<br>a key for use when a SecondarySession3 is created utilizing CMA/SPDM PSK. When cleared, no<br>SecondarySession3 is allowed by the target. This bit shall be set only if Get Target Capabilities,<br>Number of Secondary Sessions is > 3.<br>•<br>Bits[15:4]: Reserved. | Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------|--------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |                |                    |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
|                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |                |                    | Configuration Features Enable: Enable the configuration features for the target. Zero or more bits may<br>Bit[0]: Locked Target FW Update: When set, the target shall enable FW updates after the target is<br>Bit[1]: Special Purpose Memory: When set, memory reported to the initiator should not be treated<br>capacity cannot be utilized as general-purpose memory by the initiator. The target should also report<br>memory ranges in the CDAT DSEMTS. When cleared, the initiator may utilize the memory capacity as |
|                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |                |                    |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
|                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |                |                    |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
|                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |                |                    |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
|                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |                |                    |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
|                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |                |                    |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
|                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |                |                    |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
|                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |                |                    |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
|                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |                |                    |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
|                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |                |                    |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
|                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |                |                    |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
|                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |                |                    |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
|                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |                |                    |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
|                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |                |                    |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
|                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |                |                    | Secondary Session 0 CKID Type field shall both be valid and shall be utilized by the target to generate<br>Secondary Session 1 CKID Type field shall both be valid and shall be utilized by the target to generate<br>Secondary Session 2 CKID Type field shall both be valid and shall be utilized by the target to generate<br>Secondary Session 3 CKID Type field shall both be valid and shall be utilized by the target to generate                                                                                     |
|                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | 0C2h           | 0Eh                | Reserved                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |

**Table 11-35. Set Target Configuration (Sheet 4 of 4)**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
|----------------|--------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0D0h           | 1                  | Secondary Session CKID Type: The CKID Type to assign to a SecondarySession.<br>•<br>Bit[0]: Secondary Session 0 CKID Type: When set, the CKID shall be considered a TVMCKID.<br>When cleared, the CKID shall be considered an OSCKID. This field shall be valid if the Validity Flags,<br>Secondary Session 0 is set.<br>•<br>Bit[1]: Secondary Session 1 CKID Type: When set, the CKID shall be considered a TVMCKID.<br>When cleared, the CKID shall be considered an OSCKID. This field shall be valid if the Validity Flags,<br>Secondary Session 1 is set.<br>•<br>Bit[2]: Secondary Session 2 CKID Type: When set, the CKID shall be considered a TVMCKID.<br>When cleared, the CKID shall be considered an OSCKID. This field shall be valid if the Validity Flags,<br>Secondary Session 2 is set.<br>•<br>Bit[3]: Secondary Session 3 CKID Type: When set, the CKID shall be considered a TVMCKID.<br>When cleared, the CKID shall be considered an OSCKID. This field shall be valid if the Validity Flags,<br>Secondary Session 3 is set.<br>•<br>Bits[7:4]: Reserved. |
| 0D1h           | 0Fh                | Reserved                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| 0E0h           | 20h                | Secondary Session 0 PSK Key Material: The CMA/SPDM PSK key material that the target shall utilize<br>for key derivation for use when the SecondarySession0 CMA/SPDM secure session is created. This field<br>shall be valid if the Validity Flags, Secondary Session 0 is set. When this PSK key material is used to set<br>up the CMA/SPDM SecondarySession0, the associated CMA/SPDM PSK Hint entry in the CMA/SPDM<br>PSK_EXCHANGE request shall be "SECONDARY_SESSION_0_PSK" string with NUL terminator.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| 100h           | 20h                | Secondary Session 1 PSK Key Material: The CMA/SPDM PSK key material that the target shall utilize<br>for key derivation for use when the SecondarySession1 CMA/SPDM secure session is created. This field<br>shall be valid if the Validity Flags, Secondary Session 1 is set. When this PSK key material is used to set<br>up the CMA/SPDM SecondarySession1, the associated CMA/SPDM PSK Hint entry in the CMA/SPDM<br>PSK_EXCHANGE request shall be "SECONDARY_SESSION_1_PSK" string with NUL terminator.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| 120h           | 20h                | Secondary Session 2 PSK Key Material: The CMA/SPDM PSK key material that the target shall utilize<br>for key derivation for use when the SecondarySession2 CMA/SPDM secure session is created. This field<br>shall be valid if the Validity Flags, Secondary Session 2 is set. When this PSK key material is used to set<br>up the CMA/SPDM SecondarySession2, the associated CMA/SPDM PSK Hint entry in the CMA/SPDM<br>PSK_EXCHANGE request shall be "SECONDARY_SESSION_2_PSK" string with NUL terminator.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| 140h           | 20h                | Secondary Session 3 PSK Key Material: The CMA/SPDM PSK key material that the target shall utilize<br>for key derivation for use when the SecondarySession3 CMA/SPDM secure session is created. This field<br>shall be valid if the Validity Flags, Secondary Session 3 is set. When this PSK key material is used to set<br>up the CMA/SPDM SecondarySession3, the associated CMA/SPDM PSK Hint entry in the CMA/SPDM<br>PSK_EXCHANGE request shall be "SECONDARY_SESSION_3_PSK" string with NUL terminator.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |

##### 11.5.5.6.2 Set Target Configuration Response

If no error condition is detected, the DSM shall respond to the Set Target Configuration request with a Set Target Configuration Response message.

<span id="page-978-0"></span>**Table 11-36. Set Target Configuration Response**

| Byte<br>Offset | Length<br>in Bytes | Description                                      |
|----------------|--------------------|--------------------------------------------------|
| 00h            | 1                  | TSP Version: V1.0 = 10h.                         |
| 01h            | 1                  | Opcode: Set Target Configuration Response = 03h. |
| 02h            | 2                  | Reserved                                         |

##### 11.5.5.6.3 Get Target Configuration

The PrimarySession or SecondarySession(s) shall utilize the Get Target Configuration request to verify that the target is in the correct security mode after the target is locked. While it is possible to report the configuration with this request before the target is locked, the content cannot be trusted to be immutable until this request is executed after the target is successfully locked.

Possible Error Response, Error Codes:

- Version Mismatch
- No Privilege
  - The request was not received on the PrimarySession or SecondarySession(s)
- Invalid Security State
  - Target not in CONFIG\_LOCKED or CONFIG\_UNLOCKED state

<span id="page-979-0"></span>**Table 11-37. Get Target Configuration**

| Byte<br>Offset | Length<br>in Bytes | Description                             |
|----------------|--------------------|-----------------------------------------|
| 00h            | 1                  | TSP Version: V1.0 = 10h.                |
| 01h            | 1                  | Opcode: Get Target Configuration = 84h. |
| 02h            | 2                  | Reserved                                |

##### 11.5.5.6.4 Get Target Configuration Response

If no error condition is detected, the DSM shall respond to the Get Target Configuration request with a Get Target Configuration Response message.

<span id="page-979-1"></span>**Table 11-38. Get Target Configuration Response (Sheet 1 of 3)**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
|----------------|--------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 00h            | 1                  | TSP Version: V1.0 = 10h.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| 01h            | 1                  | Opcode: Get Target Configuration Response = 04h.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| 02h            | 2                  | Memory Encryption Features Enabled: The memory encryption features that are enabled for the<br>locked target. Zero or more bits may be set. 1 indicates to enable, 0 indicates to disable.<br>•<br>Bit[0]: Encryption: When set, memory encryption for data at rest is enabled on the target.<br>•<br>Bit[1]: CKID-based Encryption: When set, CKID-based encryption is enabled on the target,<br>Encryption shall be set, and the CKID Base Required field shall be valid. When set, Range-based<br>Encryption shall be cleared. When cleared, the target has disabled use of the CKID field in the<br>Transaction Layer requests.<br>•<br>Bit[2]: Range-based Encryption: When set, range-based encryption is enabled on the target and<br>Encryption shall also be set. When set, CKID-based Encryption shall be cleared. When cleared, the<br>target has disabled use of range-based target memory encryption.<br>•<br>Bit[3]: CKID Base Required: Valid only when CKID-based Encryption is set. When set, the target<br>has been enabled for a valid CKID range and CKID Base and Number of CKIDs fields shall be valid.<br>When cleared, the target has enabled any CKID value within the 13-bit field.<br>•<br>Bits[15:4]: Reserved. |
| 04h            | 4                  | Memory Encryption Algorithm Selected: Valid only if Encryption is set in Memory Encryption Features<br>Enabled. The target memory encryption algorithm that is selected. Only one bit may be set. 1 indicates<br>selected, 0 indicates not selected.<br>•<br>Bit[0]: AES-XTS-128<br>•<br>Bit[1]: AES-XTS-256<br>•<br>Bits[30:2]: Reserved<br>•<br>Bit[31]: Vendor Specific Algorithm: When set, all other bits in this field are vendor specific                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| 08h            | 4                  | Reserved                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |

**Table 11-38. Get Target Configuration Response (Sheet 2 of 3)**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                                                                                                                  |
|----------------|--------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|                |                    | TE State Change and Access Control Features Enabled: The TE State change and access control<br>features that are enabled for the locked target. Zero or more bits may be set. 1 indicates enabled, 0                                                                                                                                                                                                         |
|                |                    | indicates disabled.<br>•<br>Bit[0]: Write Access Control: When set, dropping writes that fail the verification of TEE Intent to<br>stored TE State is enabled on the target. When set, explicit state changes shall be enabled and one or<br>more of bits[4:3] shall also be set.                                                                                                                            |
|                |                    | •<br>Bit[1]: Read Access Control: When set, returning all 1s for read data in response to reads that fail<br>the verification of TEE Intent to stored TE State is enabled on the target. When set, one or more of<br>bits[4:2] shall also be set.                                                                                                                                                            |
| 0Ch            | 2                  | •<br>Bit[2]: Implicit TE State Change: When set, the implicit TE State change feature has been enabled<br>on the target, Explicit In-band TE State Change shall be enabled, and at least one Explicit In-band TE<br>State Granularity Entry with Length Index 0 shall be enabled. When cleared, the implicit TE State<br>change feature has been disabled on the target.                                     |
|                |                    | •<br>Bit[3]: Explicit Out-of-band TE State Change: When set, use of the explicit CMA/SPDM out-of<br>band Set Target TE State change request is enabled on the target and Explicit Out-of-Band TE State<br>Change Granularity shall be valid.                                                                                                                                                                 |
|                |                    | •<br>Bit[4]: Explicit In-band TE State Change: When set, explicit in-band TE State changes utilizing the<br>TEUpdate memory transaction is enabled on the target and Explicit In-band TE State Change<br>Granularity Entries shall be valid.                                                                                                                                                                 |
|                |                    | •<br>Bit[5]: Explicit TE State Change Sanitize: When set, the target is enabled to overwrite data that is<br>affected by the explicit state change with 0s when the explicit request is received and before the<br>change is considered complete by the target. When set, one or more of bits[4:3] shall also be set.<br>•<br>Bits[15:6]: Reserved.                                                          |
| 0Eh            | 2                  | Reserved                                                                                                                                                                                                                                                                                                                                                                                                     |
|                |                    | Explicit Out-of-band TE State Granularity Enabled: The granularity that has been enabled on the<br>target to utilize for explicit TE State changes in powers of 2, starting with 64B. Valid only if Explicit Out-of<br>band TE State Change is set in TE State Change and Access Control Features Enabled. Only one bit shall<br>be set. 1 indicates selected, 0 indicates not selected.<br>•<br>Bit[0]: 64B |
| 10h            | 4                  | •<br>…<br>•<br>Bit[6]: 4 KB<br>•<br>…                                                                                                                                                                                                                                                                                                                                                                        |
|                |                    | •<br>Bit[15]: 2 MB<br>•<br>…<br>•<br>Bit[24]: 1 GB                                                                                                                                                                                                                                                                                                                                                           |
|                |                    | •<br>…<br>•<br>Bit[31]: 128 GB                                                                                                                                                                                                                                                                                                                                                                               |
| 14h            | 4                  | Reserved                                                                                                                                                                                                                                                                                                                                                                                                     |
|                |                    | Configuration Features Enabled: The configuration features that are enabled for the locked target.                                                                                                                                                                                                                                                                                                           |
| 18h            | 2                  | Zero or more bits may be set. 1 indicates to enable, 0 indicates to disable.<br>•<br>Bit[0]: Locked Target FW Update: When set, FW updates after the target is locked are enabled on<br>the target. When cleared, FW updates after the target is locked are disabled on the target.<br>•<br>Bits[15:1]: Reserved.                                                                                            |
| 1Ah            | 2                  | Reserved                                                                                                                                                                                                                                                                                                                                                                                                     |
| 1Ch            | 4                  | CKID Base: The lowest CKID that the target enabled. Valid only if CKID Base Required is set in Memory<br>Encryption Features Enabled. Shall be < 2^13.                                                                                                                                                                                                                                                       |
| 20h            | 4                  | Number of CKIDs: Number of contiguous CKID that the target enabled starting at the CKID Base. Valid<br>only if CKID Base Required is set in Memory Encryption Features Enabled. CKID Base + Number of CKIDs<br>shall be < 2^13.                                                                                                                                                                              |
| 24h            | 1                  | Current TSP State<br>•<br>00h = CONFIG_UNLOCKED<br>•<br>01h = CONFIG_LOCKED<br>•<br>02h = ERROR                                                                                                                                                                                                                                                                                                              |
| 25h            | 0Bh                | •<br>All other encodings are reserved<br>Reserved                                                                                                                                                                                                                                                                                                                                                            |
| 030h           | 10h                | Explicit In-band TE State Granularity Entry 0                                                                                                                                                                                                                                                                                                                                                                |
|                |                    |                                                                                                                                                                                                                                                                                                                                                                                                              |

**Table 11-38. Get Target Configuration Response (Sheet 3 of 3)**

| Byte<br>Offset | Length<br>in Bytes | Description                                   |
|----------------|--------------------|-----------------------------------------------|
| 040h           | 10h                | Explicit In-band TE State Granularity Entry 1 |
| 050h           | 10h                | Explicit In-band TE State Granularity Entry 2 |
| 060h           | 10h                | Explicit In-band TE State Granularity Entry 3 |
| 070h           | 10h                | Explicit In-band TE State Granularity Entry 4 |
| 080h           | 10h                | Explicit In-band TE State Granularity Entry 5 |
| 090h           | 10h                | Explicit In-band TE State Granularity Entry 6 |
| 0A0h           | 10h                | Explicit In-band TE State Granularity Entry 7 |
| 0B0h           | 10h                | Reserved                                      |

##### 11.5.5.6.5 Get Target Configuration Report

The PrimarySession shall be utilized with the Get Target Configuration Report request to return specific CXL.mem configuration register TSP Report content that is utilized to verify the locked target's configuration. [Section 11.5.4.8](#page-952-0) describes the checks that can be conducted on the TSP Report response payload that is returned from this request.

This request allows select CXL configuration register contents on the endpoint target to be returned for verification through the secure PrimarySession, and is modeled after the TDISP Get Interface Report request.

While it is possible to read the configuration with this request, before the target is locked, the content cannot be trusted to be immutable until this request is executed after the target is successfully locked.

Possible Error Response, Error Codes:

- Version Mismatch
- No Privilege
  - Request was not received on the PrimarySession or SecondarySession(s)
- Invalid Security State
  - Target not in CONFIG\_LOCKED or CONFIG\_UNLOCKED state

<span id="page-981-0"></span>**Table 11-39. Get Target Configuration Report**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
|----------------|--------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 00h            | 1                  | TSP Version: V1.0 = 10h.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| 01h            | 1                  | Opcode: Get Target Configuration Report = 85h.                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| 02h            | 2                  | Reserved                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| 04h            | 2                  | Offset: Offset in bytes from the start of the report to where this request message<br>begins. For the first Get Target Configuration Report request, the initiator shall clear<br>this field to all 0s. For non-first requests, the offset is the sum of Portion Length values<br>reported in all the previous Get Target Configuration Report Responses.                                                                                                                                                                    |
| 06h            | 2                  | Length: The length of the report in bytes to be returned in the corresponding<br>response. Length is an unsigned 16-bit integer. This value is the smaller of the<br>following values:<br>•<br>Capacity of the initiator's internal buffer for receiving the target's report<br>•<br>Remainder Length of the preceding Get Target Configuration Report response<br>If the Length is > Remainder Length, the target shall transfer the remaining Report<br>Data, Portion Length, and a Remainder Length of 0 in the response. |

##### <span id="page-982-3"></span>11.5.5.6.6 Get Target Configuration Report Response

If no error condition is detected, the DSM shall respond to the Get Target Configuration Report request with a Get Target Configuration Report Response message.

<span id="page-982-0"></span>**Table 11-40. Get Target Configuration Report Response**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                           |
|----------------|--------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 00h            | 1                  | TSP Version: V1.0 = 10h.                                                                                                                                                                                                                                                                                              |
| 01h            | 1                  | Opcode: Get Target Configuration Report Response = 05h.                                                                                                                                                                                                                                                               |
| 02h            | 2                  | Reserved                                                                                                                                                                                                                                                                                                              |
| 04h            | 2                  | Portion Length: Number of bytes of this portion of the TSP Report. This shall be less<br>than or equal to Length received as part of the request. The target is permitted to set<br>this field to a value that is less than the Length received in the request due to<br>limitations on the target's internal buffer. |
| 06h            | 2                  | Remainder Length: Number of bytes of the TSP Report that have not been sent yet<br>after the current response. For the last response, the target shall clear this field to all<br>0s as an indication to the initiator that the entire TSP Report has been sent.                                                      |
| 08h            | Portion<br>Length  | Report Data: Requested contents of TSP Report.                                                                                                                                                                                                                                                                        |

[Table 11-41](#page-982-1) presents the TSP Report structure.

<span id="page-982-1"></span>**Table 11-41. TSP Report**

| Byte Offset | Length in<br>Bytes | Description                                                                                                                                                                                                      |
|-------------|--------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 00h         | 1                  | Valid TSP Report Fields: More than one bit may be set.<br>•<br>Bit[0]: CXL IDE Capability Structure Valid: When set, the TSP Report<br>contains a valid CXL IDE Capability Structure<br>•<br>Bits[7:1]: Reserved |
| 01h         | 3                  | Reserved                                                                                                                                                                                                         |
| 04h         | 3Ch                | PCIe DVSEC for CXL Devices: See Section 8.1.                                                                                                                                                                     |
| 40h         | 20h                | PCIe DVSEC for Flex Bus Port: See Section 8.2.                                                                                                                                                                   |
| 60h         | 38h                | CXL Link Capability Structure: See Section 8.2.4.19.                                                                                                                                                             |
| 98h         | 10h                | CXL Timeout and Isolation Capability Structure: See Section 8.2.4.24.                                                                                                                                            |
| A8h         | 10h + k*20h        | CXL HDM Decoder Capability Structure: The number of HDM decoders<br>(k) is specified in the Decoder Count field in the CXL HDM Decoder Capability<br>register. See Section 8.2.4.20.                             |
| B8h + k*20h | 24h                | CXL IDE Capability Structure: Structure for optionally reporting the CXL<br>IDE Transport Security configuration. Valid if CXL IDE Capability Structure<br>Valid is set.                                         |

##### <span id="page-982-2"></span>11.5.5.6.7 Lock Target Configuration

The PrimarySession shall be utilized with the Lock Target Configuration request to lock the target configuration that is relevant to protecting the TEE configuration and TVM data, and perform memory security checks before responding to this request. The locked configuration includes the security configuration set, utilizing the Set Target Configuration request in addition to CXL and PCIe target registers that need to be made immutable to protect TEE integrity. This request does not lock configuration registers and other registers that are not part of protecting the TEE configuration and TVM data.

Once locked, the configuration shall be immutable until a subsequent Conventional Reset of the target.

The target shall reject requests to lock when already in the CONFIG\_LOCKED state.

If Write Access Control is enabled on the target, the target shall clear the TE State to 0 for all addressable memory in response to the Lock Target Configuration Request and before generating a Lock Target Configuration Response. The target may require extra execution time to clear the initial TE State and may utilize the Delayed Response to prevent request timeouts, as described in [Section 11.5.5.9.](#page-993-0)

If target-based memory encryption is enabled on the target, the target shall clear any association between previous encryption keys and CKIDs or memory ranges, in response to the Lock Target Configuration Request and before generating a Lock Target Configuration Response.

See [Section 11.5.4.8.1](#page-953-0) for expected target locking behavior before successfully responding to this request.

Possible Error Response, Error Codes:

- Version Mismatch
- Invalid Security State
  - Target not in CONFIG\_UNLOCKED state
- No Privilege
  - Request was not received on the PrimarySession
- Invalid Security Configuration
  - Locking security configuration failed due to memory security check failures
- Already Locked
  - The target is already in CONFIG\_LOCKED state

<span id="page-983-0"></span>**Table 11-42. Lock Target Configuration**

| Byte<br>Offset | Length<br>in Bytes | Description                              |
|----------------|--------------------|------------------------------------------|
| 00h            | 1                  | TSP Version: V1.0 = 10h.                 |
| 01h            | 1                  | Opcode: Lock Target Configuration = 86h. |
| 02h            | 2                  | Reserved                                 |

##### <span id="page-983-2"></span>11.5.5.6.8 Lock Target Configuration Response

The DSM responds with a Lock Target Configuration Response in response to Lock Target Configuration request if the target security checks and lock operations were successful, and the target transitioned to the CONFIG\_LOCKED state. An Error Response shall be returned if the memory security checks failed, the configuration could not be locked, and/or other errors occurred.

See [Section 11.5.4.8.1](#page-953-0) for expected target behavior before sending this successful response to the lock request.

<span id="page-983-1"></span>**Table 11-43. Lock Target Configuration Response**

| Byte<br>Offset | Length<br>in Bytes | Description                                       |
|----------------|--------------------|---------------------------------------------------|
| 00h            | 1                  | TSP Version: V1.0 = 10h.                          |
| 01h            | 1                  | Opcode: Lock Target Configuration Response = 06h. |
| 02h            | 2                  | Reserved                                          |

#### <span id="page-984-0"></span>11.5.5.7 Optional Explicit TE State Change Requests and Responses

If the target supports explicit TE State changes, it shall support receiving a Set Target TE State request out-of-band that utilizes the CMA/SPDM secure PrimarySession/ SecondarySession(s) OR the TEUpdate in-band memory request opcode OR both. The target reports its supported explicit TE State change mechanisms in Get Target Capabilities. The host that supports explicit TE State changes shall enable explicit changes, utilizing Set Target Configuration. The explicit TE State change request shall be sent by the host to the target before the memory range is to be accessed, ensuring that the target has the correct TE State to perform the access checks before receiving the memory transactions that it will verify.

##### 11.5.5.7.1 Set Target TE State (Out-of-band)

Targets that utilize explicit TE State change notifications from the host shall implement the following request and response for updating the TE State based on memory range. The target shall change the TE State as specified for all memory locations covered by the Starting Address and Length that are relevant to the target for the interleave set configured.

If the target is enabled to sanitize memory affected by a state change, the target shall overwrite all data affected by this state change with 0s before generating the response.

This request could take a significant amount of time to complete if sanitization of a large amount of memory is required and is handled as follows:

- If the request can be completed without an excessive delay that could cause an SPDM timeout, the target shall respond with Set Target TE State Response, once the request is complete.
- If the target is not capable of executing the request due to the execution time required or does not support delaying the request's completion, it may fail this request with a Long Execution Time Error Response.
- Otherwise, if the target is capable of executing the request and the request will take a significant amount of time to complete, the target shall respond with Delayed Response with a nonzero Delay Time in microseconds (us). The host should wait the prescribed amount of time and issue the Check Target Delayed Completion request to verify the state change is complete.

If the target is already executing a state change request and another state change request is received, it shall fail the new request with Busy for Error Response.

Possible Error Response, Error Codes:

- Version Mismatch
- Invalid Request
  - Number of Memory Ranges is 0
  - One or more Memory Range Starting Address and Length is invalid for the target
  - One or more Memory Range Starting Address is not aligned to Explicit Out-ofband TE State Granularity Selected reported in Get Target Configuration Response
  - One or more Memory Range Length is not an exact multiple of the Explicit Outof-band TE State Granularity Selected reported in Get Target Configuration Response
  - One or more Memory Range Starting Address and Length spans TEE and non-TEE ranges
- No Privilege

- Request was not received on the PrimarySession or SecondarySession(s)
- Invalid Security State
  - Target not in CONFIG\_LOCKED state
- Busy
  - Target is currently executing another state change.
- Long Execution Time
  - Target cannot execute the request due to the amount of execution time required

<span id="page-985-0"></span>**Table 11-44. Memory Range**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                  |
|----------------|--------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 00h            | 8                  | Starting Address: HPA to start re-initializing the TE State. This address shall be<br>aligned to the Explicit Out-of-band TE State Granularity enabled in Set Target<br>Configuration.                                       |
| 08h            | 8                  | Length: The length of the memory range, in bytes, at which to re-initialize the TE<br>State. This number shall be an exact multiple of the Explicit Out-of-band TE State<br>Granularity enabled in Set Target Configuration. |

<span id="page-985-1"></span>**Table 11-45. Set Target TE State**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                                                                                     |
|----------------|--------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 00h            | 1                  | TSP Version: V1.0 = 10h.                                                                                                                                                                                                                                                                                                                                                        |
| 01h            | 1                  | Opcode: Set Target TE State = 8Dh.                                                                                                                                                                                                                                                                                                                                              |
| 02h            | 1                  | TE State: The new target TE State to set for the included memory ranges. Only one bit<br>shall be set.<br>•<br>Bit[0]: TE State: When set to 1, the target shall set the TE State for all included<br>memory ranges to TEE Exclusive. When cleared to 0, the target shall set the TE<br>State for all included memory ranges to non-TEE Exclusive.<br>•<br>Bits[7:1]: Reserved. |
| 03h            | 1                  | Number of Memory Ranges: The number of Memory Range structures (N) that are<br>included in this payload. This shall be <= 32 and > 0.                                                                                                                                                                                                                                           |
| 04h            | Ch                 | Reserved                                                                                                                                                                                                                                                                                                                                                                        |
| 10h            | 10h * N            | List of Memory Range structures.                                                                                                                                                                                                                                                                                                                                                |

##### 11.5.5.7.2 Set Target TE State Response (Out-of-band)

If no error condition is detected and the state change request has completed execution on the target, the DSM shall respond to the Set Target TE State request with a Set Target TE State Response message.

<span id="page-985-2"></span>**Table 11-46. Set Target TE State Response**

| Byte<br>Offset | Length<br>in Bytes | Description                                 |
|----------------|--------------------|---------------------------------------------|
| 00h            | 1                  | TSP Version: V1.0 = 10h.                    |
| 01h            | 1                  | Opcode: Set Target TE State Response = 0Dh. |
| 02h            | 2                  | Reserved                                    |

#### <span id="page-986-0"></span>11.5.5.8 Optional Target-based Memory Encryption Requests and Responses

The following interfaces are optionally supported by the target for use when target memory encryption is enabled. The target reports support for these interfaces in the Memory Encryption Features Supported reported in the Get Target Capabilities Response.

##### 11.5.5.8.1 Set Target CKID Specific Key

The PrimarySession or SecondarySession(s) shall be utilized with the Set Target CKID Specific Key request to define a specific CKID as a Memory Encryption Features Supported reported and associate that CKID with specific key material. This request is utilized with CKID-based target memory encryption. Once set, the association between an initiator CKID and the target's keys are immutable and attempts to set a new key for the CKID shall fail. To change the association, the CKID shall be explicitly cleared by the initiator, utilizing Clear Target CKID Key before the CKID can be set for new keys using this request. The Attributes CKID Type shall be utilized by the target to ensure that each memory transaction TEE Intent matches the CKID Type (TVMCKID or OSCKID) as described in [Section 11.5.4.6.2.1](#page-948-0).

Possible Error Response, Error Codes:

- Version Mismatch
- Unsupported Request
  - Target does not support CKID-based memory encryption
- Invalid Security State
  - Target not in CONFIG\_LOCKED state
- No Privilege
  - Request was not received on the PrimarySession or SecondarySession(s).
- Invalid CKID
  - More CKIDs have been assigned to the target than the Number of CKIDs reported in Get Target Capabilities.
  - Requested CKID is outside the range of CKID Base to CKID Base + Number of CKIDs configured in Set Target Configuration.
  - CKID already has a key associated with it. Clear Target CKID Key shall be utilized to reset the CKID association before the CKID can be set again.

<span id="page-986-1"></span>**Table 11-47. Set Target CKID Specific Key (Sheet 1 of 2)**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                   |
|----------------|--------------------|-----------------------------------------------------------------------------------------------------------------------------------------------|
| 00h            | 1                  | TSP Version: V1.0 = 10h.                                                                                                                      |
| 01h            | 1                  | Opcode: Set Target CKID Specific Key = 87h.                                                                                                   |
| 02h            | 2                  | Reserved                                                                                                                                      |
| 04h            | 4                  | CKID: The CKID assigned by the initiator to this encryption key. The attribute CKID<br>Type defines whether the CKID is an OSCKID or TVMCKID. |
| 08h            | 1                  | CKID Type: The type of CKID to utilize:<br>•<br>00h = TVMCKID<br>•<br>01h = OSCKID<br>•<br>All other encodings are reserved                   |
| 09h            | 6                  | Reserved                                                                                                                                      |

**Table 11-47. Set Target CKID Specific Key (Sheet 2 of 2)**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                         |
|----------------|--------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0Fh            | 1                  | Validity Flags: Indicators of which fields are valid in the remaining portion of this<br>request. More than one bit may be set.<br>•<br>Bit[0]: When set, the Data Encryption Key field is valid<br>•<br>Bit[1]: When set, the Tweak Key field is valid<br>•<br>Bits[7:2]: Reserved |
| 10h            | 20h                | Data Encryption Key: The memory encryption key to utilize with the CKID.                                                                                                                                                                                                            |
| 30h            | 20h                | Tweak Key: The memory encryption tweak key to utilize with the CKID. If the<br>configured encryption algorithm does not require a tweak key, then this field shall be<br>ignored.                                                                                                   |

##### 11.5.5.8.2 Set Target CKID Specific Key Response

If no error condition is detected, the DSM shall respond to the Set Target CKID Specific Key request with a Set Target CKID Specific Key Response message.

<span id="page-987-0"></span>**Table 11-48. Set Target CKID Specific Key Response**

| Byte<br>Offset | Length<br>in Bytes | Description                                         |
|----------------|--------------------|-----------------------------------------------------|
| 00h            | 1                  | TSP Version: V1.0 = 10h.                            |
| 01h            | 1                  | Opcode: Set Target CKID Specific Key Response= 07h. |
| 02h            | 2                  | Reserved                                            |

##### 11.5.5.8.3 Set Target CKID Random Key

The PrimarySession or SecondarySession(s) shall be utilized with the Set Target CKID Random Key request to define a specific CKID as an OSCKID or TVMCKID and associate the CKID with a random target-generated key utilizing optional initiator-generated entropy. This request is utilized with CKID-based target memory encryption. Once set, the association between an initiator CKID and the target's keys are immutable and attempts to set a new key for the CKID shall fail. To change the association, the CKID shall be explicitly cleared by the initiator, utilizing Clear Target CKID Key before the CKID can be set for new keys using this request. The Attributes CKID Type shall be utilized by the target to ensure that each memory transaction TEE Intent matches the CKID Type (OSCKID or TVMCKID) as described in [Section 11.5.4.6.2.1](#page-948-0).

When the target is utilizing the initiator-generated entropy, the target should generate a unique key, even if the initiator-supplied entropy is equivalent to the entropy provided in a previous request.

Possible Error Response, Error Codes:

- Version Mismatch
- Unsupported Request
  - Target does not support CKID-based memory encryption.
- Invalid Security State
  - Target not in CONFIG\_LOCKED state.
- No Privilege
  - Request was not received on the PrimarySession or SecondarySession(s).
- Invalid CKID

- More CKIDs have been assigned to the target than the Number of CKIDs reported in Get Target Capabilities.
- Requested CKID is outside the range of CKID Base to CKID Base + Number of CKIDs configured in Set Target Configuration.
- CKID already has a key associated with it. Clear Target CKID Key shall be utilized to reset the CKID association before the CKID can be set again.
- No Entropy
  - The target was not able to obtain enough entropy to generate a random key.

<span id="page-988-0"></span>**Table 11-49. Set Target CKID Random Key**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                                                     |
|----------------|--------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 00h            | 1                  | TSP Version: V1.0 = 10h.                                                                                                                                                                                                                                                                                                                        |
| 01h            | 1                  | Opcode: Set Target CKID Random Key = 88h.                                                                                                                                                                                                                                                                                                       |
| 02h            | 2                  | Reserved                                                                                                                                                                                                                                                                                                                                        |
| 04h            | 4                  | CKID: The CKID assigned by the initiator to this encryption key. The attribute CKID<br>Type defines whether the CKID is an OSCKID or TVMCKID.                                                                                                                                                                                                   |
| 08h            | 1                  | Attributes: Additional attributes of the CKID. Only one bit shall be set.<br>•<br>Bit[0]: CKID Type: When set, the CKID is considered a TVMCKID. If cleared, the<br>CKID is considered an OSCKID.<br>•<br>Bits[7:1]: Reserved.                                                                                                                  |
| 09h            | 6                  | Reserved                                                                                                                                                                                                                                                                                                                                        |
| 0Fh            | 1                  | Validity Flags: Indicators of which fields are valid in the remaining portion of this<br>request. More than one bit may be set.<br>•<br>Bit[0]: When set, the Data Encryption Key Entropy field is valid<br>•<br>Bit[1]: When set, the Tweak Key Entropy field is valid<br>•<br>Bits[7:2]: Reserved                                             |
| 10h            | 20h                | Data Encryption Key Entropy: Optional initiator-supplied memory encryption key<br>entropy for the target to utilize when generating a random data encryption key for the<br>CKID. This field shall be ignored if Initiator Supplied Entropy is not set in Memory<br>Encryption Features Supported reported in Get Target Capabilities Response. |
| 30h            | 20h                | Tweak Key Entropy: Optional initiator-supplied memory encryption tweak key<br>entropy for the target to utilize when generating a random tweak key for the CKID. This<br>field shall be ignored if Initiator Supplied Entropy is not set in Memory Encryption<br>Features Supported reported in Get Target Capabilities Response.               |

##### 11.5.5.8.4 Set Target CKID Random Key Response

If no error condition is detected, the DSM shall respond to the Set Target CKID Random Key request with a Set Target CKID Random Key Response message.

<span id="page-988-1"></span>**Table 11-50. Set Target CKID Random Key Response**

| Byte<br>Offset | Length<br>in Bytes | Description                                       |
|----------------|--------------------|---------------------------------------------------|
| 00h            | 1                  | TSP Version: V1.0 = 10h.                          |
| 01h            | 1                  | Opcode: Set Target CKID Random Key Response= 08h. |
| 02h            | 2                  | Reserved                                          |

##### 11.5.5.8.5 Clear Target CKID Key

The PrimarySession or SecondarySession(s) shall be utilized with the Clear Target CKID Key request to clear any association on the target between the previously set CKID and random or specific keys that may have been programmed. This request is utilized with

CKID-based target memory encryption. This request is utilized by the initiator to clear the association between an initiator's CKID and the target's keys and allows a CKID to be utilized with a set of new keys. Once a CKID has been cleared the CKID Type is no longer a TVMCKID and encryption utilizing that CKID is bypassed.

The target shall break the association of CKID to key and shall clear the associated key to 0.

The same SPDM session that was utilized to set the key for the CKID shall be the same session that is utilized to clear the CKID. If the SPDM session utilized to set the key has been terminated or closed, then a Conventional Reset or CXL Reset shall be utilized to clear the CKID association with the key material.

Possible Error Response, Error Codes:

- Version Mismatch
- Unsupported Request
  - Target does not support CKID-based memory encryption
- Invalid Security State
  - Target not in CONFIG\_LOCKED state
- No Privilege
  - Request was not received on the PrimarySession or SecondarySession(s)
  - CKID was not set on the same SPDM session
- Invalid CKID
  - Requested CKID is outside the range of CKID Base to CKID Base + Number of CKIDs configured in Set Target Configuration
  - CKID is not currently programmed in the target

<span id="page-989-0"></span>**Table 11-51. Clear Target CKID Key**

| Byte<br>Offset | Length<br>in Bytes | Description                                           |
|----------------|--------------------|-------------------------------------------------------|
| 00h            | 1                  | TSP Version: V1.0 = 10h.                              |
| 01h            | 1                  | Opcode: Clear Target CKID Key = 89h.                  |
| 02h            | 2                  | Reserved                                              |
| 04h            | 4                  | CKID: The CKID for which to clear the encryption key. |

##### 11.5.5.8.6 Clear Target CKID Key Response

If no error condition is detected, the DSM shall respond to the Clear Target CKID Key request with a Clear Target CKID Key Response message.

<span id="page-989-1"></span>**Table 11-52. Clear Target CKID Key Response**

| Byte<br>Offset | Length<br>in Bytes | Description                                   |
|----------------|--------------------|-----------------------------------------------|
| 00h            | 1                  | TSP Version: V1.0 = 10h.                      |
| 01h            | 1                  | Opcode: Clear Target CKID Key Response = 09h. |
| 02h            | 2                  | Reserved                                      |

##### 11.5.5.8.7 Set Target Range Specific Key

The PrimarySession or SecondarySession(s) shall be utilized with the Set Target Range Specific Key request to associate a specific memory range with initiator-specified key material. This request is utilized with range-based target memory encryption. Once set, the association between an initiator HPA memory range and the target's keys are immutable and attempts to set a new key for the same or subset of the same HPA range shall fail. To change the association, the memory range shall be explicitly cleared by the initiator, utilizing Clear Target Range Key before the memory range can be set for new keys using this request.

Possible Error Response, Error Codes:

- Version Mismatch
- Invalid Request
  - The memory Range Base and Range Size is invalid for the target.
  - The memory Range Base is not aligned to the Range Size.
  - The Range Size is not a power of 2.
  - The Range ID is >= Memory Encryption Number of Range Based Keys reported in Get Target Capabilities.
  - The memory range register specified by the Range ID requested is already associated with keys.
  - The request attempted to change a memory range or subset of the range already configured. Clear Target Range Key shall be utilized to reset the memory range association.
- Unsupported Request
  - The target does not support range-based memory encryption.
- Invalid Security State
  - Target not in CONFIG\_LOCKED state.
- No Privilege
  - The request was not received on the PrimarySession or SecondarySession(s).

<span id="page-990-0"></span>**Table 11-53. Set Target Range Specific Key (Sheet 1 of 2)**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                          |
|----------------|--------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 00h            | 1                  | TSP Version: V1.0 = 10h.                                                                                                                                                             |
| 01h            | 1                  | Opcode: Set Target Range Specific Key = 8Ah.                                                                                                                                         |
| 02h            | 2                  | Reserved                                                                                                                                                                             |
| 04h            | 4                  | Range ID: The range ID assigned to this encryption key. Shall be within the range<br>specified in Get Target Capabilities Response, Memory Encryption Number of Range<br>Based Keys. |
| 08h            | 8                  | Range Start: HPA of the first 4-KB-aligned block within the range.<br>•<br>Bits[11:0]: Reserved<br>•<br>Bits[63:12]: Start HPA for the range, HPA[63:12]                             |
| 10h            | 8                  | Range End: HPA of the last 4-KB-aligned block within the range.<br>•<br>Bits[11:0]: Reserved<br>•<br>Bits[63:12]: End HPA for the range, HPA[63:12]                                  |
| 18h            | 7                  | Reserved                                                                                                                                                                             |

**Table 11-53. Set Target Range Specific Key (Sheet 2 of 2)**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                         |
|----------------|--------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1Fh            | 1                  | Validity Flags: Indicators of which fields are valid in the remaining portion of this<br>request. More than one bit may be set.<br>•<br>Bit[0]: When set, the Data Encryption Key field is valid<br>•<br>Bit[1]: When set, the Tweak Key field is valid<br>•<br>Bits[7:2]: Reserved |
| 20h            | 20h                | Data Encryption Key: The memory encryption key to utilize with the range.                                                                                                                                                                                                           |
| 40h            | 20h                | Tweak Key: The memory encryption tweak key to utilize with the range. If the<br>configured encryption algorithm does not require a tweak key, then this field shall be<br>ignored.                                                                                                  |

##### 11.5.5.8.8 Set Target Range Specific Key Response

If no error condition is detected, the DSM shall respond to the Set Target Range Specific Key request with a Set Target Range Specific Key Response message.

<span id="page-991-0"></span>**Table 11-54. Set Target Range Specific Key Response**

| Byte<br>Offset | Length<br>in Bytes | Description                                          |
|----------------|--------------------|------------------------------------------------------|
| 00h            | 1                  | TSP Version: V1.0 = 10h.                             |
| 01h            | 1                  | Opcode: Set Target Range Specific Key Response= 0Ah. |
| 02h            | 2                  | Reserved                                             |

##### 11.5.5.8.9 Set Target Range Random Key

The PrimarySession or SecondarySession(s) shall be utilized with the Set Target Range Random Key request to associate a specific memory range with initiator-specified entropy material. This request is utilized with range-based target memory encryption. Once set, the association between an initiator HPA memory range and the target's keys are immutable and attempts to set a new key for the same or subset of the same HPA range shall fail. To change the association, the memory range shall be explicitly cleared by the initiator, utilizing Clear Target Range Key before the memory range can be set for new keys using this request.

Possible Error Response, Error Codes:

- Version Mismatch
- Invalid Request
  - Memory Range Base and Range Size is invalid for the target.
  - Memory Range Base is not aligned to the Range Size.
  - Range Size is not a power of 2.
  - Range ID is >= Memory Encryption Number of Range Based Keys reported in Get Target Capabilities.
  - Memory range register specified by the Range ID is already associated with keys.
  - Request attempted to change a memory range or subset of the range already configured. Clear Target Range Key shall be utilized to reset the memory range association.
- Unsupported Request
  - Target does not support range-based memory encryption.

- Invalid Security State
  - Target not in CONFIG\_LOCKED state.
- No Privilege
  - Request was not received on the PrimarySession or SecondarySession(s).

<span id="page-992-0"></span>**Table 11-55. Set Target Range Random Key**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                         |
|----------------|--------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 00h            | 1                  | TSP Version: V1.0 = 10h.                                                                                                                                                                                                                                                                            |
| 01h            | 1                  | Opcode: Set Target Range Random Key = 8Bh.                                                                                                                                                                                                                                                          |
| 02h            | 2                  | Reserved                                                                                                                                                                                                                                                                                            |
| 04h            | 4                  | Range ID: The range ID assigned to this encryption key. Shall be in the range<br>specified in Get Target Capabilities Response, Memory Encryption Number of Range<br>Based Keys.                                                                                                                    |
| 08h            | 8                  | Range Start: HPA of the first 4-KB-aligned block within the range.<br>•<br>Bits[11:0]: Reserved<br>•<br>Bits[63:12]: Start HPA for the range, HPA[63:12]                                                                                                                                            |
| 10h            | 8                  | Range End: HPA of the last 4-KB-aligned block within the range.<br>•<br>Bits[11:0]: Reserved<br>•<br>Bits[63:12]: End HPA for the range, HPA[63:12]                                                                                                                                                 |
| 18h            | 7                  | Reserved                                                                                                                                                                                                                                                                                            |
| 1Fh            | 1                  | Validity Flags: Indicators of which fields are valid in the remaining portion of this<br>request. More than one bit may be set.<br>•<br>Bit[0]: When set, the Data Encryption Key Entropy field is valid<br>•<br>Bit[1]: When set, the Tweak Key Entropy field is valid<br>•<br>Bits[7:2]: Reserved |
| 20h            | 20h                | Data Key Entropy: Optional initiator-supplied data key entropy that is utilized by the<br>target when generating an encryption key for the range.                                                                                                                                                   |
| 40h            | 20h                | Tweak Key Entropy: Optional initiator-supplied memory encryption tweak key<br>entropy that is utilized by the target when generating a tweak key for the range. If the<br>configured encryption algorithm does not require a tweak key, then this field shall be<br>ignored.                        |

##### 11.5.5.8.10 Set Target Range Random Key Response

If no error condition is detected, the DSM shall respond to the Set Target Range Random Key request with a Set Target Range Random Key Response message.

<span id="page-992-1"></span>**Table 11-56. Set Target Range Random Key Response**

| Byte<br>Offset | Length<br>in Bytes | Description                                         |
|----------------|--------------------|-----------------------------------------------------|
| 00h            | 1                  | TSP Version: V1.0 = 10h.                            |
| 01h            | 1                  | Opcode: Set Target Range Random Key Response = 0Bh. |
| 02h            | 2                  | Reserved                                            |

##### 11.5.5.8.11 Clear Target Range Key

The PrimarySession or SecondarySession(s) shall be utilized with the Clear Target Range Key request to clear any association between a previously set HPA memory range and random or specific keys that may have been programmed. This request is utilized with range-based target memory encryption. This request is utilized by the initiator to clear the association between an initiator's memory range and the target's keys and allows a memory range to be utilized with a new set of keys. The target shall break the association of HPA memory range to key, shall clear the associated key to 0 and memory encryption utilizing the cleared memory range shall be bypassed.

The same SPDM session that was utilized to set the key for the range shall be the same session that is utilized to clear the range. If the SPDM session utilized to set the key has been terminated or closed, then a Conventional Reset or CXL Reset shall be utilized to clear the memory range association with the key material.

Possible Error Response, Error Codes:

- Version Mismatch
- Unsupported Request
  - The target does not support range-based memory encryption
- Invalid Security State
  - Target not in CONFIG\_LOCKED state
- No Privilege
  - The request was not received on the PrimarySession or SecondarySession(s)
  - The range was not set on the same SPDM session
- Invalid Request
  - Range-based encryption is not supported by the target
  - The range specified is not currently set

<span id="page-993-1"></span>**Table 11-57. Clear Target Range Key**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                          |
|----------------|--------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 00h            | 1                  | TSP Version: V1.0 = 10h.                                                                                                                                                             |
| 01h            | 1                  | Opcode: Clear Target Range Key = 8Ch.                                                                                                                                                |
| 02h            | 2                  | Reserved                                                                                                                                                                             |
| 04h            | 4                  | Range ID: The range ID assigned to this encryption key. Shall be within the range<br>specified in Get Target Capabilities Response, Memory Encryption Number of Range<br>Based Keys. |

##### 11.5.5.8.12 Clear Target Range Key Response

If no error condition is detected, the DSM shall respond to the Clear Target Range Key request with a Clear Target Range Key Response message.

<span id="page-993-2"></span>**Table 11-58. Clear Target Range Key Response**

| Byte<br>Offset | Length<br>in Bytes | Description                                    |
|----------------|--------------------|------------------------------------------------|
| 00h            | 1                  | TSP Version: V1.0 = 10h.                       |
| 01h            | 1                  | Opcode: Clear Target Range Key Response = 0Ch. |
| 02h            | 2                  | Reserved                                       |

#### <span id="page-993-0"></span>11.5.5.9 Optional Delayed Completion Requests and Responses

TSP provides a simple polling mechanism for requests that may take a significant amount of time to complete. If the time it takes for the target to execute the request might cause an SPDM timeout, the target may return a Delayed Response. This will notify the initiator that the request passed all the syntax checks, has started execution on the target, and will take additional time to complete.

The initiator utilizes the returned Delay Time to check on the completion of the request by sending the Check Target Delayed Completion request after waiting the prescribed amount of time. If the request has completed the target shall send a Check Target Delayed Completion Response. If the request is still executing the target shall respond with another Delayed Response with the updated time the initiator is expected to wait.

##### 11.5.5.9.1 Delayed Response

The response that the target has started executing a request that could take a significant amount of time to complete. The target shall return the number of microseconds (us) that it expects the initiator to wait before checking the completion of the request.

<span id="page-994-0"></span>**Table 11-59. Delayed Response**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                          |
|----------------|--------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 00h            | 1                  | TSP Version: V1.0 = 10h.                                                                                                                                             |
| 01h            | 1                  | Opcode: Delayed Response = 7Eh.                                                                                                                                      |
| 02h            | 2                  | Reserved                                                                                                                                                             |
| 04h            | 4                  | Delay Time: Estimated number of microseconds (us) that the initiator should delay<br>before checking for the completion of the long executing command. Shall be > 0. |

##### 11.5.5.9.2 Check Target Delayed Completion

This request shall only utilized by the initiator if a request returns a Delayed Response. It is utilized to verify the completion of a long executing request. If the request has completed execution, the target shall return a Check Target Delayed Completion Response. If the request is still executing, the target shall respond with Delayed Response with the new Delay Time that the initiator should wait before issuing this request again. If Delayed Response was not returned for a request, there is no delayed completion, and this request shall be failed by the target.

Possible Error Response, Error Codes:

- Version Mismatch
- Invalid Request
  - No request is outstanding that would result in a delayed completion

<span id="page-994-1"></span>**Table 11-60. Check Target Delayed Completion**

| Byte<br>Offset | Length<br>in Bytes | Description                                    |
|----------------|--------------------|------------------------------------------------|
| 00h            | 1                  | TSP Version: V1.0 = 10h.                       |
| 01h            | 1                  | Opcode: Check Target Delayed Completion = 8Eh. |
| 02h            | 2                  | Reserved                                       |

##### 11.5.5.9.3 Check Target Delayed Completion Response

If no error condition is detected and the execution of the long executing request has completed, the DSM shall respond to the Check Target Delayed Completion request with a Check Target Delayed Completion Response message. This indicates that the previously delayed completion of the request is now complete.

<span id="page-995-1"></span>**Table 11-61. Get Target TE State Change Completion Response** 

| Byte<br>Offset | Length in Bytes | Description                                                     |  |
|----------------|-----------------|-----------------------------------------------------------------|--|
| 00h            | 1               | <b>TSP Version</b> : V1.0 = 10h.                                |  |
| 01h            | 1               | <b>Opcode</b> : Check Target Delayed Completion Response = 0Eh. |  |
| 02h            | 2               | Reserved                                                        |  |

#### <span id="page-995-0"></span>11.5.5.10 Error Response

The Error Response is permitted to be used by the target to complete any of the requests issued to the target.

<span id="page-995-2"></span>**Table 11-62. Error Response**

| Byte<br>Offset | Length<br>in Bytes | Description                           |  |
|----------------|--------------------|---------------------------------------|--|
| 00h            | 1                  | <b>TSP Version</b> : V1.0 = 10h.      |  |
| 01h            | 1                  | <b>Opcode</b> : Error Response = 7Fh. |  |
| 02h            | 2                  | Reserved                              |  |
| 04h            | 4                  | Error Code: See Table 11-63.          |  |
| 08h            | 4                  | Error Data: See Table 11-63.          |  |
| 0Ch            | Varies             | Extended Error Data: See Table 11-63. |  |

<span id="page-995-3"></span>**Table 11-63. Error Response — Error Code, Error Data, Extended Error Data (Sheet 1 of 2)**

| Error<br>Code | Definition                                                                                                                                  | Error Data                                          | Extended<br>Error Data     |
|---------------|---------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------|----------------------------|
| 0000h         | Reserved                                                                                                                                    | 0000h                                               | None                       |
| 0001h         | Invalid Request: One or more fields in the request are invalid.                                                                             | 0000h                                               | None                       |
| 0002h         | <b>Busy</b> : The target could not process the request but the target may be able to process the request if it is sent again in the future. | 0000h                                               | None                       |
| 0003h         | Unspecified: An unspecified error occurred.                                                                                                 | 0000h                                               | None                       |
| 0004h         | <b>Unsupported Request</b> : The Message Type in the command is unsupported.                                                                | Unsupported Message Type                            | None                       |
| 0005h         | Version Mismatch: The version in the request is not supported.                                                                              | Highest TSP version number that the target supports | None                       |
| 0006h         | Vendor Specific Error: A vendor defined error occurred.                                                                                     | Length of Extended Error Data                       | Vendor specific error data |
| 0007h         | <b>No Privilege</b> : The requested Session ID has no privilege to generate the request.                                                    | SPDM Session ID                                     | None                       |
| 0008h         | <b>No Entropy</b> : Target failed to generate random numbers to execute the request.                                                        | 0000h                                               | None                       |
| 0009h         | Invalid CKID: The request contains an invalid CKID.                                                                                         | 0000h                                               | None                       |
| 000Ah         | <b>Invalid Security Configuration</b> : Target security checks failed due to an invalid configuration.                                      | Length of Extended Error Data                       | Vendor specific error data |

Table 11-63. Error Response — Error Code, Error Data, Extended Error Data (Sheet 2 of 2)

| Error<br>Code | Definition                                                                                                                                   | Error Data | Extended<br>Error Data |
|---------------|----------------------------------------------------------------------------------------------------------------------------------------------|------------|------------------------|
| 000Bh         | <b>Invalid Security State</b> : The target was not in the correct TSP state to execute the request.                                          | 0000h      | None                   |
| 000Ch         | <b>Long Execution Time</b> : The target did not start the execution of the request as it may cause SMTP timeouts waiting for the completion. | 0000h      | None                   |
| 000Dh         | <b>Already Locked</b> : An initiator is attempting to lock an already locked target.                                                         | 0000h      | None                   |
