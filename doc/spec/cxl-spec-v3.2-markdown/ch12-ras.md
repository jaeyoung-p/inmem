# <span id="page-997-0"></span>12.0 Reliability, Availability, and Serviceability

<span id="page-997-5"></span>CXL RAS capabilities are built on top of PCIe\*. Additional capabilities are introduced to address cache coherency and memory as listed below.

## <span id="page-997-1"></span>12.1 Supported RAS Features

[Table 12-1](#page-997-4) lists the RAS features supported by CXL and their applicability to CXL.io vs. CXL.cache and CXL.mem.

<span id="page-997-4"></span>**Table 12-1. CXL RAS Features**

| Feature                      | CXL.io                                                                       | CXL.cache and CXL.mem                                                                                                              |
|------------------------------|------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------|
| Link CRC and Retry           | Required                                                                     | Required                                                                                                                           |
| Link Retraining and Recovery | Required                                                                     | Required                                                                                                                           |
| eDPC                         | Optional                                                                     | Leverage CXL.io capability<br>CXL.cache or CXL.mem errors may be<br>signaled via ERR_FATAL or ERR_NONFATAL<br>and may trigger eDPC |
| ECRC                         | Optional                                                                     | N/A                                                                                                                                |
| Hot-Plug                     | Not Supported in RCD mode<br>Managed Hot-Plug is<br>supported in CXL VH mode | Same as CXL.io                                                                                                                     |
| Data Poisoning               | Required                                                                     | Required                                                                                                                           |
| CXL Isolation                | N/A                                                                          | Optional (see Section 12.3)                                                                                                        |
| Viral                        | N/A                                                                          | Required (see Section 12.4)                                                                                                        |

## <span id="page-997-2"></span>12.2 CXL Error Handling

CXL Error handling can be subdivided into two parts:

<span id="page-997-6"></span>- • Link and Protocol Errors, which apply to the CXL component-to-component communication mechanism. These include errors detected by CXL.cache and CXL.mem protocol logic. This is further described in [Section 12.2.1](#page-997-3) and [Section 12.2.2.](#page-1002-0)
- Device Errors, which apply exclusively to the device itself. This is further described in [Section 12.2.3](#page-1002-1).

### <span id="page-997-3"></span>12.2.1 Protocol and Link Layer Error Reporting

Protocol and Link errors are detected and communicated to the Host where the errors can be exposed and handled. Errors may also be reflected to Platform software if so configured. There are no error pins that connect CXL devices to the Host. Errors are communicated between the Host and the CXL device via messages over CXL.io.

CXL Protocol and Link errors detected by components that are part of a CXL VH are escalated and reported using standard PCIe error reporting mechanisms over CXL.io as UIEs and/or CIEs. See PCIe Base Specification for details.

Reporting and logging of CXL Protocol and Link errors in RCD mode is described in this section.

#### <span id="page-998-0"></span>12.2.1.1 RCH Downstream Port-detected Errors

RCH Downstream Port-detected CXL Protocol errors are escalated and reported via the Root Complex error-reporting mechanisms as UIEs and/or CIEs. The various signaling and logging steps are listed below and illustrated in Figure 12-1.

- 1. DP<sub>Δ</sub> CXL.io-detected errors are logged in the local AER Extended Capability in DP<sub>Δ</sub> RCRB. Software must ensure that the Root Port Control register in the DPA AER Extended Capability is not configured to generate interrupts.
- 2. DPA CXL.cache and CXL.mem log errors in the CXL RAS Capability (see Section 8.2.4.17).
- 3. DP<sub>Δ</sub> CXL.cache, CXL.mem, or CXL.io sends error message(s) to RCEC.
- 4. RCEC logs UIEs and/or CIEs. The RCEC Error Source Identification register shall log the RCEC's Bus, Device, and Function Numbers because the RCH Downstream Port is not associated with one.
- 5. RCEC generates an MSI/MSI-X, if enabled.

The OS error handler may begin by inspecting the RCEC AER Extended Capability and following PCIe rules to discover the error source. The RCEC Error Source Identification register is insufficient for identifying the error source. The OS error handler may rely on RDPAS structures (see Section 9.18.1.5), if present, to identify such Downstream Port(s). The Platform Software Error Handler may interrogate the Platform-specific error logs in addition to the error logs defined in PCIe Base Specification and this specification.

<span id="page-999-1"></span>**Figure 12-1. RCH Downstream Port Detects Error**

![](_page_999_Figure_3.jpeg)

#### <span id="page-999-0"></span>12.2.1.2 RCD Upstream Port-detected Errors

RCD Upstream Port-detected CXL protocol errors are also escalated and reported via the RCEC. The various signaling and logging steps are listed below and illustrated in [Figure 12-2](#page-1000-1).

- 1. If a CXL.cache or CXL.mem logic block in UPZ detects a protocol or link error, the block shall log the error in the CXL RAS Capability (see [Section 8.2.4.17\)](#page-548-2).
- 2. Upstream Port RCRB shall not implement the AER Extended Capability.
- 3. UPZ sends an error message to all CXL.io Functions that are affected by this error. (This example shows a device with a single function. The message must include all the details that the CXL.io function needs for constructing an AER record.)
- 4. CXL.io Functions log the received message in their respective AER Extended Capability.
- 5. Each affected CXL.io Function sends an ERR\_ message to UPZ with its own Requester ID.
- 6. UPZ forwards this Error message across the Link without logging.
- 7. DPA forwards the Error message to the RCEC.
- 8. RCEC logs the error in the Root Error Status register and then signals an interrupt, if enabled, in accordance with PCIe Base Specification. The Error Source Identification register in the RCEC shall point to the CXL.io Function that sent the ERR\_ message.

<span id="page-1000-1"></span>**Figure 12-2. RCD Upstream Port Detects Error**

![](_page_1000_Figure_3.jpeg)

#### <span id="page-1000-0"></span>12.2.1.3 RCD RCiEP-detected Errors

CXL protocol errors detected by the RCD RCiEP are also escalated and reported via the RCEC. The various signaling and logging steps are listed below and illustrated in [Figure 12-3](#page-1001-1).

- 1. CXL.cache (or CXL.mem) notifies all affected CXL.io Functions of the errors.
- 2. All affected CXL.io Functions log the UIEs and/or CIEs in their respective AER Extended Capability.
- 3. CXL.io Functions generate PCIe ERR\_ messages on the Link with Tag = 0.
- 4. DPA forwards the ERR\_ messages to the RCEC.
- 5. RCEC logs the errors in the Root Error Status register and then generates an MSI/ MSI-X, if enabled, in accordance with PCIe Base Specification.

<span id="page-1001-1"></span>**Figure 12-3. RCD RCiEP Detects Error**

![](_page_1001_Figure_3.jpeg)

#### <span id="page-1001-0"></span>12.2.1.4 Header Log and Handling of Multiple Errors

Unmasked CXL protocol and link errors are captured in the Uncorrectable Error Status register and the Correctable Error Status register (see [Section 8.2.4.17.1](#page-548-3) and [Section 8.2.4.17.4,](#page-554-0) respectively). In the scenarios where multiple bits are set in the Uncorrectable Error Status register, the First Error Pointer field in the Error Capabilities and Control register (see [Section 8.2.4.17.6](#page-555-1)), if valid, points to the first uncorrectable error that was captured. The First Error Pointer is valid if the associated bit of the Uncorrectable Error Status register is set. Otherwise, it is invalid. By definition, First Error Pointer is considered invalid if bit 5 of that field is set to 1. For certain uncorrectable errors, the specification requires that the component capture part of the message header, called Error Header, in the Header Log register. [Section 8.2.4.17.1](#page-548-3) defines the format of the Error Header for each error.

If the Multiple\_Header\_Recording\_Capability bit in the Error Capabilities and Control register (see [Section 8.2.4.17.6\)](#page-555-1) is set, the component is capable of recording multiple Error Headers in the order in which they are detected. If header logging resources are unavailable when an unmasked uncorrectable error is detected, the corresponding error status bit is set to 1; however, the Error Header is not recorded in the Header Log register. After software has consumed the error to which the First Error Pointer points, software writes 1 to the corresponding error status bit to indicate that. The error status bit may remain set if there was another occurrence of the same error. If any bit in the Uncorrectable Error Status register remains set after this software action, the component must atomically update the Header Log register and the First Error Pointer to point to the next recorded error. If no other error is recorded, the component shall update the First Error Pointer to an invalid value. If

Multiple\_Header\_Recording\_Capability=1, it is recommended that software not clear

![](_page_1002_Picture_1.jpeg)

the Status bit other than the one pointed to by the First Error Pointer. If software violates this condition, the state of the Header Log register in the presence of other recorded errors is undefined.

### <span id="page-1002-0"></span>12.2.2 CXL Root Ports, Downstream Switch Ports, and Upstream Switch Ports

CXL protocol errors detected by CXL root ports, DSPs, and USPs are escalated and reported using PCIe error-reporting mechanisms as UIEs and/or CIEs. It is strongly recommended that CXL.cachemem protocol errors that are detected by a CXL root port be logged as CIEs or UIEs in the root port's AER Extended Capability. The Error Source Identification register logs the Bus, Device, and Function Numbers of the Root Port itself. If the CXL.cachemem protocol errors detected by a CXL root port are logged as CIEs or UIEs in an RCEC's AER Extended Capability, it is recommended that the System Firmware populate an RDPAS record (see [Section 9.18.1.5](#page-868-4)) to establish the association between the RCEC and the root port.

The OS error handler may begin by inspecting the Root Port AER Extended Capability and follow PCIe rules to discover the error source. The Platform Software Error Handler may interrogate the Platform-specific error logs in addition to the error logs defined in PCIe Base Specification and this specification.

If the CXL.cachemem errors are logged in an RCEC and the CEDT includes RDPAS structures (see [Section 9.18.1.5\)](#page-868-4) that reference the RCEC, the OS handler may consult those RDPAS structures to locate the CXL root port that is the error source.

### <span id="page-1002-1"></span>12.2.3 CXL Device Error Handling

<span id="page-1002-2"></span>Whenever a CXL device returns data that is either known to be bad or suspect, the device must ensure that the consumer of the data is made aware of the nature of the data, either at the time of consumption or prior to data consumption. This allows the consumer to take appropriate containment action.

CXL defines two containment mechanisms - poison and viral:

- **Poison**: Return data on CXL.io and CXL.cachemem may be tagged as poisoned.
- **Viral**: CXL.cachemem supports viral, which is mainly used to indicate more-severe error conditions at the device (see [Section 12.4](#page-1007-1)). Any data returned by a device on CXL.cachemem after the device has communicated Viral is considered suspect, even if the data is not explicitly poisoned.

A device must set the MetaField to No-Op in the CXL.cachemem return response when the Metadata is suspect.

If a CXL component is not in the Viral condition, the component shall poison the data message on the CXL interface whenever the data being included is known to be bad or suspect.

If Viral is enabled and a CXL component is in the Viral condition, it is recommended that the component not poison the subsequent data responses on the CXL.cachemem interface to avoid error pollution.

The Host may send poisoned data to the CXL-connected device. How the CXL device responds to Poison is device specific but must follow PCIe guidelines. The device must consciously make a decision about how to handle poisoned data. In some cases, simply ignoring poisoned data may lead to Silent Data Corruption (SDC). A CXL device is required to keep track of any poison data that the device receives on a 64-byte granularity.

Any device errors that cannot be handled with Poison indication shall be signaled by the device back to the Host as messages since there are no error pins. To that end, [Table 12-2](#page-1003-1) shows a summary of the error types and their mappings, and error reporting guidelines for devices that do not implement Memory Error Logging and Signaling Enhancements (see [Section 12.2.3.2\)](#page-1004-0).

For devices that implement Memory Error Logging and Signaling Enhancements, [Section 12.2.3.2](#page-1004-0) describes how memory errors are logged and signaled. Such devices should follow [Table 12-2](#page-1003-1) for dealing with all non-memory errors.

<span id="page-1003-1"></span>**Table 12-2. Device-specific Error Reporting and Nomenclature Guidelines**

| Error Severity             | Definition/Example                                                                                                                      | Signaling Options<br>(SW picks one) | Logging1                                | Host HW/FW/SW<br>Response                                                                                       |
|----------------------------|-----------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------|-----------------------------------------|-----------------------------------------------------------------------------------------------------------------|
| Corrected                  | Memory single bit error<br>corrected via ECC                                                                                            | MSI or MSI-X to Device<br>driver    | Device-specific<br>registers            | Device-specific flow in<br>Device driver                                                                        |
| Uncorrected<br>Recoverable | UC errors from which the<br>Device can recover, with<br>minimal or no software help<br>(e.g., error localized to single<br>computation) | MSI or MSI-X to driver              | Device-specific<br>registers            | Device-specific flow in<br>driver (e.g., discard<br>results of suspect<br>computation)                          |
| Uncorrected<br>NonFatal    | Equivalent to PCIe UCNF,<br>contained by the device<br>(e.g., write failed, memory<br>error that affects many<br>computations)          | MSI or MSI-X to Device<br>Driver    | Device-specific<br>registers            | Device-specific (e.g.,<br>reset affected device) flow<br>in driver. Driver can<br>escalate through<br>software. |
|                            |                                                                                                                                         | PCIe AER Internal Error             | Device-specific<br>registers + PCIe AER | System FW/SW AER flow,<br>ends in reset                                                                         |
| Uncorrected                | Equivalent to PCIe UCF,<br>poses containment risk (e.g.,<br>command/parity error, Power<br>management Unit ROM<br>error)                | PCIe AER Internal error             | Device-specific<br>registers + PCIe AER | System FW/SW AER flow,<br>ends in reset                                                                         |
| Fatal                      |                                                                                                                                         | AER + Viral                         |                                         | System FW/SW Viral flow                                                                                         |

<sup>1.</sup> For CXL devices that implement memory error logging and signaling enhancements (see [Section 12.2.3.2](#page-1004-0)), the memory error logging and signaling mechanisms are defined by the CXL specification.

In keeping with the standard error logging requirements, all error logs should be sticky.

#### <span id="page-1003-0"></span>12.2.3.1 CXL.cache and CXL.mem Errors

If demand accesses to memory result in an uncorrected data error, the CXL device must return data with poison. The requester (processor core or a peer device) is responsible for dealing with the poison indication. The CXL device should not signal an uncorrected error along with the poison. If the processor core consumes the poison, the error will be logged and signaled by the Host.

Any non-demand uncorrected errors detected by a device (e.g., memory scrub logic in CXL device memory controller) that does not support the Memory Error Logging and Signaling Enhancements (see [Section 12.2.3.2\)](#page-1004-0) will be signaled to the device driver via a device MSI or MSI-X. Any corrected memory errors will be signaled to the device driver via a device MSI or MSI-X. The driver may choose to deallocate memory pages that have repeated errors. Neither the platform firmware nor the OS directly deal with these errors. An eRCD may implement the capabilities described in [Section 12.2.3.2,](#page-1004-0) in which case a device driver is not required.

If a CXL component is unable to positively decode a CXL.mem address, the handling is described in [Section 8.2.4.20.2](#page-567-2). If a component does not implement HDM Decoders (see [Section 8.2.4.20\)](#page-564-1), the component shall drop such a write transaction and return all 1s in response to such a read transaction.

#### <span id="page-1004-0"></span>12.2.3.2 Memory Error Logging and Signaling Enhancements

Errors in memory may be encountered during a demand access or independent of any request issued to the memory. It is important to log sufficient data about such errors to enable the use of host platform-level RAS features, such as page retirement, without dependence on a driver.

In addition, general device events that are unrelated to the media, including changes in the device's health or environmental conditions detected by the device, need to be reported using the same general-event logging facility.

[Figure 12-4](#page-1004-1) illustrates a use case where the two methods of signaling supported by a CXL.mem device - VDM and MSI/MSI-X – are used by a host to implement Firmwarefirst and OS-first error handling.

<span id="page-1004-1"></span>**Figure 12-4. CXL Memory Error Reporting Enhancements**

![](_page_1004_Figure_7.jpeg)

A CXL device that supports the Memory Error Logging and Signaling Enhancements capability must log such errors locally and expose the error log to system software via the MMIO Mailbox (see [Section 8.2.9.4.3\)](#page-625-3). Reading an error record from the mailbox will not automatically result in deletion of the error record on the device. An explicit clear operation is required to delete an error record from the device. To support error record access and deletion, the device shall implement the Get Event Records and Clear Event Records commands.

Both operations must execute atomically. Furthermore, all writes or updates to the error records by the CXL.mem device must also execute atomically.

Using these two operations, a host can retrieve an error record as follows:

- 1. The host reads a number of event records using the Get Event Records command.
- 2. When complete, the host clears the event records from the device with the Clear Event Records command, supplying one or more event record handles to clear.

The error records will be owned by the host firmware or OS so that all logged errors are made available to the host to support platform-level RAS features.

Error records stored on the CXL device must be sticky across device resets. The records must not be initialized or modified by a hot reset, an FLR, or CXL Reset (see [Section 9.7](#page-804-1)). Devices that consume auxiliary power must preserve the error records when auxiliary power consumption is enabled. In these cases, the error records are neither initialized nor modified by hot reset, warm reset, or cold reset.

#### <span id="page-1005-0"></span>12.2.3.3 CXL Device Error Handling Flows

RCD errors may be sourced from a Root Port (RP) or Endpoint (RCiEP). For the purpose of differentiation, RCiEP-sourced errors shall use a tag value of 0, whereas RP-sourced errors shall use a tag of nonzero value.

Errors detected by the CXL device shall be communicated to the host via PCIe Error messages across the CXL.io link. Errors that are not related to a specific Function within the device (Non-Function errors) and not reported via an MSI/MSI-X are reported to the Host via PCIe error messages where the errors can be escalated to the platform.

The Upstream Port reports non-function errors to all EPs/RCiEPs where they are logged. Each EP/RCiEP reports the non-function-specific errors to the host via PCIe error messages. Software should be aware that although an RCiEP does not have a softwarevisible link, the RCiEP may still log link-related errors.

At most, one error message of a given severity is generated for a multi-function device. The error message must include the Requester ID of a function that is enabled to send the error message. Error messages with the same Requester ID may be merged for different errors with the same severity. No error message is sent if no function is enabled to do so. If different functions are enabled to send error messages of different severity, at most one error of each severity level is sent.

Errors generated by the RCD RCiEP will be sent to the corresponding RCEC. Each RCiEP must be associated with no more than one RCEC. Errors generated by a CXL component that is part of a CXL VH shall be logged in the CXL Root Port.

## <span id="page-1005-1"></span>12.3 Isolation on CXL.cache and CXL.mem

<span id="page-1005-2"></span>Isolation on CXL.cache and CXL.mem is an optional normative capability of a CXL Root Port. Such isolation halts traffic on the respective protocol. Further, once triggered, the Root Port synthesizes the response for all pending and subsequent transactions on that protocol. This is further described in [Section 12.3.1](#page-1006-0) and [Section 12.3.2](#page-1007-0), respectively.

The specification defines two trigger mechanisms:

- Link Down If a Root Port supports CXL.cache isolation and software enables CXL.cache isolation, a Link Down condition shall unconditionally trigger CXL.cache isolation. If a Root Port supports CXL.mem isolation and software enables CXL.mem isolation, a Link Down condition shall unconditionally trigger CXL.mem isolation.
- Transaction timeout A Root Port that supports CXL.cache isolation may be capable of being configured in such a way that a CXL.cache timeout triggers CXL.cache isolation. A Root Port that supports CXL.mem isolation may be capable of being configured in such a way that a CXL.mem timeout triggers CXL.mem isolation.

*Note:* Transaction Timeout Value settings for CXL.cache and CXL.mem: The system needs to ensure that timeouts are appropriately set up. For example, a timeout should not be so short that isolation is triggered due to a non-erroneous, long-latency access to a CXL device. Software may need to temporarily disable the triggering of isolation upon timeout if one or more devices are being transitioned to a state (e.g., firmware update) where the device may violate the timeout.

> The primary purpose of the isolation action is to complete pending and subsequent transactions that are associated with the isolated root port quickly, with architected semantics, after isolation is triggered. Since system memory and system caches must generally be assumed to be corrupted, software recovery generally relies on software to identify all software threads, VMs, containers, etc., whose system state might be corrupted, and then terminating them. Other software recovery mechanisms are also possible, and they are beyond the scope of this specification.

> A Root Port indicates support for Isolation by implementing the CXL Timeout and Isolation Capability structure (see [Section 8.2.4.24](#page-581-4)). The structure contains the capability, control, and status bits for both Transaction Timeout and Isolation on both CXL.cache and CXL.mem. Both Timeout and Isolation are disabled by default and must be explicitly and individually enabled by software for each protocol before they can be triggered. When Isolation is enabled for either CXL.cache or CXL.mem, software can optionally configure the Root Port to force a Link Down condition if the respective protocol enters Isolation.

> When Isolation is entered, the Root Port, if capable, signals an MSI/MSI-X or send an ERR\_COR Message if enabled. Software may also choose to rely only on mandatory synchronous exception handling (see [Section 12.3.1](#page-1006-0) and [Section 12.3.2\)](#page-1007-0). Software may read the CXL Timeout and Isolation Status register to determine whether a Timeout or Isolation has occurred on CXL.cache and/or CXL.mem and if the Isolation was triggered due to a Timeout or due to a Link Down condition. The software must explicitly clear the corresponding Isolation status bits (see [Section 8.2.4.24.3](#page-586-0)) for the root port to exit Isolation. The link must transition through the Link Down state before software can attempt re-enumeration and device recovery.

### <span id="page-1006-0"></span>12.3.1 CXL.cache Transaction Layer Behavior during Isolation

This section specifies the CXL.cache Transaction Layer's behavior while the Root Port is in Isolation.

The Root Port shall handle host requests that would ordinarily be mapped to (H2D) CXL.cache messages in the following manner.

For each host snoop that would ordinarily be mapped to (H2D) CXL.cache request messages:

- If the host is tracking the device as a possible exclusive owner of the line, then data is treated as poison.
- Else if the host knows the device can only have a Shared or Invalid state for the line, then the device cache is considered Invalid (no data poisoning is needed).

> **IMPLEMENTATION NOTE**

Exclusive vs. Shared/Invalid may be known based on an internal state within the host.

The Root Port timeout detection logic shall account for partial responses. For example, if the Root Port observes that the data is returned on the D2H Data channel in a timely manner, but no D2H Rsp was observed for a sufficient length of time, the Root Port shall treat it as a CXL.cache timeout.

For each pending Pull that is mapped to H2D CXL.cache Response of type \*WritePull\* which expects a data return, the Root Port must treat the returned data as poison.

### <span id="page-1007-0"></span>12.3.2 CXL.mem Transaction Layer Behavior during Isolation

This section specifies the CXL.mem Transaction Layer's behavior while the CXL Root Port is in Isolation.

The Root Port shall handle host requests that it would ordinarily map to (M2S) CXL.mem messages in the following manner:

- For each host request that would ordinarily be mapped to CXL.mem Req and RwD:
  - For Read transactions, the CXL Root Port synthesizes a synchronous exception response. The specific mechanism of synchronous exception response is CXL Root Port implementation specific. An example of a synchronous exception response would be returning data with Poison.
  - For non-read transactions, the CXL Root Port synthesizes a response as appropriate. The specific mechanism of the synthesized response is implementation specific. An example would be returning a completion (NDR) for a write (RwD) transaction.

## <span id="page-1007-1"></span>12.4 CXL Viral Handling

<span id="page-1007-3"></span>CXL links and CXL devices are expected to be Viral compliant. Viral is an errorcontainment mechanism. A platform must choose to enable Viral at boot. The Host implementation of Viral allows the platform to enable the Viral feature by writing into a register. Similarly, a BIOS-accessible control register on the device is written to enable Viral behavior (both receiving and sending) on the device. Viral support capability and control for enabling are reflected in the DVSEC.

When enabled, a Viral indication is generated whenever an Uncorrected\_Fatal error is detected. Viral is not a replacement for existing error-reporting mechanisms. Instead, its purpose is an additional error-containment mechanism. The detector of the error is responsible for reporting the error through AER and generating a Viral indication. Any entity that is capable of reporting Uncorrected\_Fatal errors must also be capable of generating a Viral indication.

CXL.cache and CXL.mem are pre-enabled with the Viral concept. Viral needs to be communicated in both directions. When Viral is enabled and the Host runs into a Viral condition, the Host shall communicate Viral across CXL.cache and/or CXL.mem to all downstream components. The Viral indication must arrive before any data that may have been affected by the error (general Viral requirement). If the host receives a Viral indication from any CXL components, the Host shall propagate Viral to all downstream components.

All types of Conventional Resets shall clear the viral condition. CXL Resets and FLRs shall have no effect on the viral condition.

### <span id="page-1007-2"></span>12.4.1 Switch Considerations

Viral is enabled on a per-vPPB basis and the expectation is that if Viral is enabled on one or more DSPs, then Viral will also be enabled on the USP within a VCS.

A Viral indication received on any port transitions that VCS into the Viral state, but does not trigger a new uncorrected fatal error inside the switch. A Viral indication in one VCS has no effect on other VCSs within the switch component. The switch continues to process all CXL.io traffic targeting the switch and forward all traffic. All CXL.cache and CXL.mem traffic sent to all ports within the VCS is considered to have the Viral bit set. The Viral indication shall propagate from an input port to all output ports in the VCS

faster than any subsequent CXL.cache or CXL.mem transaction. The Viral bit is propagated across upstream links and links connected to SLDs with the Viral LD-ID Vector (see [Table 4-10](#page-214-1)) set to 0 for compatibility with the CXL 1.1 specification.

If the switch detects an uncorrected fatal error, the switch must determine whether that error affects one or multiple VCSs. Any affected VCS enters the Viral state, sets the Viral\_Status bit (see [Section 8.1.3.3](#page-504-3)) to indicate that a Viral condition has occurred, asserts the Viral bit in all CXL.cache and CXL.mem traffic sent to all ports within the VCS, and then sends an AER message. The affected VCS continues to forward all CXL traffic.

Hot-remove and hot-add of devices below DSPs have no effect on the Viral state of the VCS within the switch.

If the switch has configured and enabled MLD ports, then there are additional considerations. When a VCS with an MLD port enters the Viral state, the VCS propagates the Viral indication to LDs within the MLD Component by setting the Viral bit in the Viral LD-ID Vector (see [Table 4-10\)](#page-214-1) for the LDs in that VCS. If an uncorrected fatal error causes one or more VCSs to enter the Viral state, then the corresponding bits in the Viral LD-ID Vector shall be set. An LD within an MLD component that has entered the Viral state sets the Viral bit in CXL.mem traffic with the Viral LD-ID Vector mask set to identify all the LD-IDs associated with all the affected VCSs. The indication from each LD-ID propagates the Viral state to all associated VCSs that have Viral containment enabled.

### <span id="page-1008-0"></span>12.4.2 Device Considerations

Although the device's reaction to Viral is device specific, the device is expected to take error-containment actions that are consistent with Viral requirements. Mainly, the device must prevent bad data from being committed to permanent storage. If the device is connected to any permanent storage or to an external interface that may be connected to permanent storage, then the device is required to self-isolate to be Viral compliant. This means that the device has to take containment actions without depending on help from the Host.

The containment actions taken by the device must not prevent the Host from making forward progress. This is important for diagnostic purposes as well as for avoiding error pollution (e.g., withholding data for read transactions to device memory may cause cascading timeouts in the Hosts). Therefore, on Viral detection, in addition to the containment requirements, the device shall:

- Drop writes to the persistent HDM ranges on the device or connected to the device.
- Always return a Completion response.
- Set MetaField to No-Op in all responses that carry MetaField.
- Fail the Set Shutdown State command (defined in [Section 8.2.10.9.3.5\)](#page-731-4) with an Internal Error when attempting to change the state from "dirty" to "clean".
- Not transition the Shutdown State to "clean" after a GPF flow.
- Commit to the persistent HDM ranges any writes that were completed over the CXL interface before receipt of the viral condition.
- Keep responding to snoops.
- Complete pending writes to Host memory.
- Complete all reads and writes to Device volatile memory.

When the device itself runs into a Viral condition and Viral is enabled, the device shall:

• Set the Viral Status bit to indicate that a Viral condition has occurred

- Containment Take steps to contain the error within the device (or logical device in an MLD component) and follow the Viral containment steps listed above.
- Communicate the Viral condition back up to CXL.cache and CXL.mem, toward the Host.
  - Viral propagates to all devices in the Virtual Hierarchy, including to the host.

Viral Control and Status bits are defined in the DVSEC (see [Chapter 3.0](#page-84-3) for details).

## <span id="page-1009-0"></span>12.5 Maintenance

Maintenance operations may include media maintenance, media testing, module testing, etc. A maintenance operation is identified by a Maintenance Operation Class and a Maintenance Operation Subclass. A Device may support one or more Maintenance Operation Subclasses related to a Maintenance Operation Class. See [Table 8-117](#page-700-1).

The Device may use Event Records to notify the System Software or System Firmware about needing a maintenance operation. When the Device requires maintenance, the Maintenance Needed bit in the Event Record Flags is set to 1, while the class of recommended maintenance operation is indicated by the Maintenance Operation Class field. See [Table 8-55](#page-639-1).

The Perform Maintenance command (see [Section 8.2.10.7.1](#page-698-4)) initiates a maintenance operation. The maintenance operation to be executed is specified in the input payload by the Maintenance Operation Class field and the Maintenance Operation Subclass field.

## <span id="page-1009-1"></span>12.6 CXL Error Injection

The major aim of error-injection mechanisms is to allow system validation and system firmware/software development, etc., the means to create error scenarios and errorhandling flows. To this end, a CXL Upstream Port and Downstream Port are recommended to implement the following error injection hooks to a specified address (where applicable):

- One type of CXL.io UC error (optional similar to PCIe)
  - CXL.io is always present in any CXL connection
- One type of CXL.cache UC error (if applicable)
- One type of CXL.mem UC error (if applicable)
- Link Correctable errors
  - Transient errors and
  - Persistent errors
- Returning Poison on a read to a specified address (CXL.mem only)

Error injection interfaces are documented in [Chapter 14.0.](#page-1019-4)

**§ §**

![](_page_1010_Picture_1.jpeg)
