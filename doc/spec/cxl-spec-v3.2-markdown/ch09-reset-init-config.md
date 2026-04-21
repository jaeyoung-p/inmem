# <span id="page-798-0"></span>9.0 Reset, Initialization, Configuration, and Manageability

## <span id="page-798-1"></span>9.1 CXL Boot and Reset Overview

### <span id="page-798-2"></span>9.1.1 General

<span id="page-798-4"></span><span id="page-798-3"></span>Boot and Power-up sequencing of CXL devices follows the applicable form-factor specifications and as such, will not be discussed in detail in this section.

CXL devices can encounter three types of resets.

- Hot Reset Triggered via link (via LTSSM or Link Down)
- Warm Reset Triggered via external signal, PERST# (or equivalent, form-factorspecific mechanism)
- Cold Reset Involves main Power removal and PERST# (or equivalent, formfactor-specific mechanism)

These three reset types are labeled as Conventional Reset. Function Level Reset (see [Section 9.5](#page-802-0)) and CXL Reset (see [Section 9.7\)](#page-804-0) are not considered to be Conventional Resets. These definitions are consistent with PCIe\* Base Specification.

Flex Bus Physical Layer link states across cold reset, warm reset, surprise reset, and Sx entry match PCIe Physical Layer link states.

This chapter highlights the differences that exist between CXL and native PCIe for these reset operations.

A PCIe device generally cannot determine which system-level flow triggered a Conventional Reset. System-level reset and Sx-entry flows require coordinated coherency domain shutdown before the sequence can progress. Therefore, the CXL flow will adhere to the following rules:

- Warnings shall be issued to all CXL devices before the system initiates system-level reset and Sx-entry transitions.
- CXL PM messages shall be used to communicate between the host and the device. Devices must respond to these messages with the correct acknowledge, even if no actions are actually performed on the device. To prevent deadlock in cases where one or more downstream components do not respond, the host must implement a timeout, after which the host proceeds as if the response has been received.
- A device shall correctly process the reset trigger regardless of whether they are preceded by these warning messages. Not all device resets are preceded by a warning message. For example, setting Secondary Bus Reset bit in a Downstream Port above the device results in a device hot-reset, but it is not preceded by any warning message. It is also possible that the PM VDM warning message may be lost due to an error condition.

Sx states are system Sleep States and are enumerated in ACPI Specification.

### <span id="page-799-0"></span>9.1.2 Comparing CXL and PCIe Behavior

Table 9-1 summarizes the difference in event sequencing and signaling methods across System Reset and Sx flows, for CXL.io, CXL.cache, CXL.mem, and PCIe.

The terms used in the table are as follows:

- · Warning: An early notification of the upcoming event. Devices with coherent cache or memory are required to complete outstanding transactions, flush internal caches as needed, and then place memory in a safe state such as Self-refresh as required. Devices are required to complete all internal actions and then respond with a correct Ack to the processor
<span id="page-799-4"></span>- Signaling: Actual initiation of the state transition, using either wires and/or linklayer messaging

<span id="page-799-2"></span>**Table 9-1. Event Sequencing for Reset and Sx Flows**

| Case                           | PCIe                                                                    | CXL                                                                                                          |
|--------------------------------|-------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------|
| System Reset<br>Entry          | Warning: None. Signaling: LTSSM Hot Reset.                              | Warning: PM2IP (ResetWarn, System Reset) <sup>1</sup> . Signaling: LTSSM Hot Reset.                          |
| Surprise System<br>Reset Entry | Warning: None. Signaling: LTSSM detect-entry or PERST#.                 | Warning: None. Signaling: LTSSM detect-entry or PERST#.                                                      |
| System Sx Entry                | Warning: PME_Turn_Off/Ack. Signaling: PERST# (Main power will go down). | Warning: PM2IP (ResetWarn, Sx) <sup>1</sup> . PME_Turn_Off/Ack. Signaling: PERST# (Main power will go down). |
| System Power<br>Failure        | Warning: None.                                                          | <b>Warning</b> : PM2IP (GPF Phase 1 and Phase 2) <sup>1</sup> ; see Section 9.8.                             |

<span id="page-799-6"></span><span id="page-799-5"></span><sup>1.</sup> CXL PM VDM with different encodings for different events. If CXL.io devices do not respond to the CXL PM VDM, the host may still end up in the correct state due to timeouts.

#### <span id="page-799-1"></span>9.1.2.1 Switch Behavior

When a CXL Switch (physical or virtual) is present, the Switch shall forward PM2IP messages received on its primary interface to CXL components on the secondary interface subject to rules specified below. The Switch shall aggregate IP2PM messages from the secondary interface prior to responding on its primary interface subject to rules specified below. (See Table 3-1 for PM Commands.) When communicating with a pooled device, these messages shall carry LD-ID TLP Prefix in both directions.

<span id="page-799-3"></span>**Table 9-2.** CXL Switch Behavior Message Aggregation Rules (Sheet 1 of 2)

| PM Logical<br>Opcode Value    | PM Command | Action                                                                                                                                                                                                                                               |
|-------------------------------|------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0                             | AGENT_INFO | <ul> <li>Do not forward PM2IP messages to downstream Devices.</li> <li>Execute Credits and PM Initialization flow against the downstream entity whenever a link trains up in CXL mode.</li> <li>Save CAPABILITY_VECTOR from the response.</li> </ul> |
| 2 RESETPREP • Forward PM2IP m |            | <ul> <li>Never forward PM2IP messages to PCIe links.</li> <li>Forward PM2IP messages to all active downstream CXL links.</li> <li>Gather the IP2PM messages from all active downstream CXL links.</li> </ul>                                         |

**Table 9-2. CXL Switch Behavior Message Aggregation Rules (Sheet 2 of 2)**

| PM Logical<br>Opcode Value | PM Command | Action                                                                                                                                                                                                                                                                                                                                                           |  |  |
|----------------------------|------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--|--|
| 4<br>PMREQ                 |            | •<br>Never forward PM2IP messages to PCIe links.<br>•<br>Forward PM2IP messages to all active downstream CXL links.<br>•<br>Gather the IP2PM messages from all active downstream CXL links. "Conglomerate"<br>Latency Tolerance Reporting (LTR) requests from all Devices by following the rules<br>defined in LTR Mechanism section in PCIe Base Specification. |  |  |
| 6                          | GPF        | •<br>Never forward PM2IP messages to PCIe links.<br>•<br>Never forward PM2IP messages to all downstream CXL links that returned<br>CAPABILITY_VECTOR[1]=0.<br>•<br>Forward PM2IP messages to all downstream CXL links that returned<br>CAPABILITY_VECTOR[1]=1 and gather the IP2PM responses from all such links.                                                |  |  |
| FEh                        | CREDIT_RTN | •<br>Do not forward PM2IP message to downstream Devices.<br>•<br>PM Credit management on the primary interface is independent of PM credit<br>management on the secondary interface.                                                                                                                                                                             |  |  |

<span id="page-800-2"></span>**Figure 9-1. PMREQ/RESETPREP Propagation by CXL Switch**

![](_page_800_Figure_5.jpeg)

## <span id="page-800-0"></span>9.2 CXL Device Boot Flow

CXL devices shall follow the appropriate form factor specification regarding the boot flows.

This specification uses the terms "Warm Reset" and "Cold Reset" in a manner that is consistent with PCIe Base Specification.

## <span id="page-800-1"></span>9.3 CXL System Reset Entry Flow

In an OS-orchestrated reset flow, it is expected that the CXL devices are already in an Inactive State with their contexts flushed to the system memory or CXL-attached memory before the platform reset flow is triggered.

In a platform-triggered reset flow (e.g., due to a fatal error), a CXL device may not be in an Inactive State when the device receives the ResetPrep message.

During system reset flow, the host shall issue a CXL PM VDM (see [Table 3-1](#page-87-1)) to the downstream CXL components with the following values:

- PM Logical Opcode[7:0]=RESETPREP
- Parameter[15:0]=REQUEST
- ResetType = System Reset
- PrepType = General Prep

The CXL device shall flush any relevant context to the host, clean up the data serving the host, and then place any CXL device connected memory into a safe state such as self-refresh. The CXL device shall take any additional steps that are necessary for the CXL host to enter LTSSM Hot Reset. After all the Reset preparation is complete, the CXL device shall issue a CXL PM VDM with the following value:

- PM Logical Opcode[7:0]=RESETPREP
- Parameter[15:0]=RESPONSE
- ResetType = System Reset
- PrepType = General Prep

The CXL device may have PERST# asserted after the reset handshake is complete. On PERST# assertion, the CXL device should clear any sticky content internal to the device unless they are on auxiliary power. The CXL device's handling of sticky register state is consistent with PCIe Base Specification.

To prevent a deadlock in the case where one or more downstream components do not respond with an Ack, the host must implement a timeout, after which the host proceeds as if the response has been received.

<span id="page-801-1"></span>**Figure 9-2. CXL Device Reset Entry Flow**

![](_page_801_Figure_16.jpeg)

## <span id="page-801-0"></span>9.4 CXL Device Sleep State Entry Flow

Since OS is always the orchestrator of Sx entry flows, it is expected that the CXL devices are already in an Inactive State with their contexts flushed to the CPU-attached memory or CXL-attached memory before the Sx entry flow is triggered.

During Sx entry flow, the host shall issue a CXL PM VDM (see [Table 3-1](#page-87-1)) to the downstream components with the following values:

- PM Logical Opcode[7:0]=RESETPREP
- Parameter[15:0]=REQUEST

- ResetType = System transition from S0 to Sx (S1, S3, S4, or S5)
- PrepType = General Prep

The CXL device shall flush any relevant context to the host, clean up the data serving the host, and then place any CXL device connected memory into a safe state such as self-refresh. The CXL device shall take any additional steps that are necessary for the CXL host to initiate an L2 entry flow. After all the Sx preparation is complete, the CXL device shall issue a CXL PM VDM with the following values:

- PM Logical Opcode[7:0]=RESETPREP
- Parameter[15:0]=RESPONSE
- ResetType = System transition from S0 to Sx (based on the target sleep state)
- PrepType = General Prep

PERST# to the CXL device may be asserted any time after this handshake is complete. On PERST# assertion, the CXL device should clear any sticky content internal to the device unless they are on auxiliary power. The CXL device's handling of sticky register state is consistent with PCIe Base Specification.

CXL.mem-capable adapters may need auxiliary power to retain memory context across S3.

*Note:* PERST# shall always be asserted for CXL Sx Entry flows.

<span id="page-802-1"></span>**Figure 9-3. CXL Device Sleep State Entry Flow**

![](_page_802_Figure_13.jpeg)

## <span id="page-802-0"></span>9.5 Function Level Reset (FLR)

The PCIe FLR mechanism enables software to quiesce and reset Endpoint hardware with Function-level granularity. CXL devices expose one or more PCIe functions to host software. These functions can expose FLR capability and existing PCIe-compatible software can issue an FLR to these functions. PCIe Base Specification provides specific

guidelines regarding the impact of an FLR on PCIe function level state and control registers. For compatibility with existing PCIe software, CXL PCIe functions shall follow those guidelines if the Functions support FLR. For example, any software-readable state that potentially includes secret information associated with any preceding use of the Function must be cleared by an FLR.

FLRs do not affect the CXL.cache and CXL.mem protocols. Any CXL.cache-related and CXL.mem-related control registers, including CXL DVSEC structures and state held by the CXL device, are not affected by FLRs. The memory controller that hosts the HDM is not reset by an FLR. After an FLR, all address translations associated with the corresponding Function are invalidated in accordance with PCIe Base Specification. Since the CXL Function accesses cache using the system physical address held in the address translation cache, the Function is unable to access any cachelines after the FLR until software explicitly re-enables ATS. The device is not required to write back its cache during an FLR flow. To avoid an adverse effect on the performance of other Functions, it is strongly recommended that the device not write back its cache content during an FLR if the cache is shared by multiple functions. Cache coherency must be maintained.

In some cases, system software may use an FLR to attempt error recovery. In the context of CXL devices, errors in CXL.cache logic and in CXL.mem logic cannot be recovered by an FLR. An FLR may succeed in recovering from CXL.io domain errors.

In a CXL device other than an eRCD, all Functions that participate in CXL.cache or CXL.mem are required to support either FLR or CXL Reset (see [Section 9.7](#page-804-0)).

## <span id="page-803-0"></span>9.6 Cache Management

A CXL-unaware OS or PCIe bus driver is unaware of CXL.cache capability. The device driver is expected to be aware of this CXL.cache capability and may manage the CXL.cache. Software shall not assume that lines in device cache that map to HDM will be flushed by CPU cache flush instructions. The behavior may vary from one host to another.

System software may wish to ensure that a CXL.cache-capable device does not contain any valid cachelines without resetting the system or the entire device. Since a device is not required to clear cache contents upon FLR, separate control and status bits are defined for this purpose. This capability is highly recommended for CXL.cache-capable eRCDs and mandatory for all other CXL.cache-capable devices. The capability is advertised via the Cache Writeback and Invalidate Capable flag in the DVSEC CXL Capability register (see [Section 8.1.3.1](#page-502-1)).

Software shall take the following steps to ensure that the Device does not contain any valid cachelines:

- 1. Set Disable Caching=1. This bit is located in the DVSEC CXL Control2 register (see [Section 8.1.3.4](#page-504-2)).
- 2. Set Initiate Cache Write Back and Invalidation=1. This step may be combined with the previous step as a single configuration space register write to the DVSEC CXL Control2 register (see [Section 8.1.3.4](#page-504-2)).
- 3. Wait until Cache Invalid=1. This bit is located in the DVSEC CXL Status2 register (see [Section 8.1.3.5](#page-505-1)). Software may leverage the cache size reported in the DVSEC CXL Capability2 register (see [Section 8.1.3.7](#page-506-3)) to compute a suitable timeout value.

Software is required to Set Disable Caching=0 to re-enable caching. When the Disable Caching bit transitions from 1 to 0, the device shall transition the Cache Invalid bit to 0 if it was previously set to 1.

## <span id="page-804-0"></span>9.7 CXL Reset

<span id="page-804-1"></span>CXL.cache resources and CXL.mem resources such as controllers, buffers, and caches are likely to be shared at the device level. CXL Reset is a mechanism that is used to reset all CXL.cache states and CXL.mem states in addition to CXL.io in all non-Virtual Functions that support CXL.cache protocols and/or CXL.mem protocols. Reset of CXL.io has the same scope as FLR. [Section 9.5](#page-802-0) describes FLR in the context of CXL devices. CXL Reset will not affect non-CXL Functions or the physical link. Non-CXL Function Map DVSEC capability is used to advertise to the System Software which non-Virtual Functions are considered non-CXL (i.e., they neither participate in CXL.cache nor in CXL.mem).

All Functions in an SLD that participate in CXL.cache or CXL.mem are required to support either FLR or CXL Reset. MLDs, on the other hand, are required to support CXL Reset.

Capability, Control, and Status fields for CXL Reset are exposed in configuration space of Function 0 of a CXL device but these affect all physical and virtual functions within the device that participate in CXL.cache or CXL.mem.

The system software is responsible for quiescing all the Functions that are impacted due to reset of the CXL.cache state and CXL.mem state in the device and offlining any associated HDM ranges. Once the CXL Reset is complete, all CXL Functions on the device must be re-initialized prior to use.

CXL Reset may be issued by the System Software or the Fabric Manager. To quiesce the impacted non-virtual Functions prior to issuing CXL Reset, the System Software shall complete the following actions for each of the CXL non-virtual Functions:

- 1. Offline any volatile or persistent HDM Ranges. When offlining is complete, there shall be no outstanding or new CXL.mem transactions to the affected CXL Functions.
- 2. Configure these Functions to stop initiating new CXL.io requests. This procedure is identical to that for FLR.

The FM may issue CXL Reset for various cases described in [Chapter 7.0](#page-318-4). In the case of the FM use of CXL Reset, there may be outstanding commands in the device which shall be silently discarded.

CXL.io reset of the device shall follow the definition of FLR in PCIe Base Specification. Note that only PCIe-mapped memory shall be cleared or randomized by the non-virtual Functions during FLR.

Reset of the CXL.cache state and CXL.mem state as part of the CXL Reset flow at the device level has the following behavior:

- All outstanding or new CXL.mem reads shall be silently discarded. Previously accepted writes to persistent HDM ranges shall be persisted. Writes to volatile HDM ranges may be discarded.
- The device caches (Type 1 Devices and Type 2 Devices) shall be written back and invalidated by the device. Software is not required to write back and invalidate the device cache (see [Section 9.6\)](#page-803-0) prior to issuing the CXL Reset.
- No new CXL.cache requests shall be issued except for the above cache-flushing operation. Snoops shall continue to be serviced.
- Contents of volatile HDM ranges may or may not be retained and the device may optionally clear or randomize these ranges if this capability is supported and is requested during CXL Reset (see the CXL Reset Mem Clr Capable bit in the DVSEC CXL Capability register and the CXL Reset Mem Clr Enable bit in the DVSEC CXL Control2 register in [Section 8.1.3.1](#page-502-1) and [Section 8.1.3.4](#page-504-2), respectively). Contents of the persistent HDM ranges will be retained by the device.

- Any errors during a CXL Reset shall be logged in the error status registers in the usual manner. Failure to complete a CXL Reset shall result in the CXL Reset Error bit in the DVSEC CXL Status2 Register being set. The system software may choose to retry CXL Reset, assert other types of device resets, or restart the system in response to a CXL Reset failure.
- Unless specified otherwise, all non-sticky registers defined in this specification shall be initialized to their default values upon CXL Reset. The CONFIG\_LOCK bit in the DVSEC Config Lock register (see [Section 8.1.3.6](#page-506-5)) and any register fields that are locked by CONFIG\_LOCK shall not be affected by CXL Reset. Any sticky registers, such as the error status registers, shall be preserved across CXL Reset. If the device is in the viral state, it shall remain in that state after a CXL Reset.

If the device is unable to complete CXL Reset within the specified timeout period, the System Software shall consider this a failure and may choose to take action similar to when the CXL Reset Error bit is set.

A pooled Type 3 device (MLD) must ensure that only the LD assigned to the host that is issuing CXL Reset is impacted. This includes the clearing or randomizing of the volatile HDM ranges on the device. Other LDs must continue to operate normally.

### <span id="page-805-0"></span>9.7.1 Effect on the Contents of the Volatile HDM

Because ownership of the volatile HDM ranges may change following a CXL Reset, it is important to ensure that there is no leak of volatile memory content that was present prior to the CXL Reset. (This condition does not apply to persistent memory content whose security is ensured by other means not discussed here.)

There are two cases to consider:

- The device remains bound to the same host and the System Software reallocates the volatile HDM ranges to a different software entity. The System Software is often responsible for ensuring that the memory range is re-initialized prior to any allocation. The device may implement an optional capability to perform clearing or randomizing of all impacted volatile HDM ranges. This may be invoked using the optional Secure Erase function (see [Section 8.2.10.9.5.2](#page-740-1)). Optionally, the device may be capable of clearing or randomizing volatile HDM content as part of CXL Reset. If this capability is available, the System Software may take advantage of it. However, since this is an optional capability, the System Software should not depend on it.
- The device is migrated to a different host with FM involvement as described in [Chapter 7.0.](#page-318-4) The FM must use either Secure Erase operation (see [Section 8.2.10.9.5.2\)](#page-740-1) or utilize CXL Reset if the CXL Reset Mem Clr capability exists to clear or randomize any volatile HDM ranges prior to re-assigning device to a different host.

Capability for clearing and randomizing volatile HDM ranges in the device is reported by the CXL Reset Mem Clr Capable bit in the DVSEC CXL Capability register. If present, this capability may optionally be used by setting the CXL Reset Mem Clr Enable bit in the DVSEC CXL Control2 register.

### <span id="page-805-1"></span>9.7.2 Software Actions

System Software or Fabric Manager shall follow these steps while performing CXL Reset:

- 1. Verify that the device supports CXL Reset by consulting the CXL Reset Capable bit in the DVSEC CXL Capability register (see [Section 8.1.3.1](#page-502-1)).
- 2. Prepare the system for CXL Reset as described in [Section 9.7.](#page-804-0)

- 3. Determine whether the device supports the CXL Reset Mem Clr capability bit by consulting the DVSEC CXL Capability register (see [Section 8.1.3.1](#page-502-1)).
- 4. If the device supports the CXL Reset Mem Clr capability, program the CXL Reset Mem Clr Enable bit in the DVSEC CXL Control2 register (see [Section 8.1.3.4\)](#page-504-2) as required.
- 5. Determine the timeout for completion by consulting the CXL Reset Timeout field in the DVSEC CXL Capability register.
- 6. Set the Initiate CXL Reset=1 in the DVSEC CXL Control2 register.
- 7. Wait for CXL Reset Complete=1 or CXL Reset Error=1 in the DVSEC CXL Status2 register (see [Section 8.1.3.5\)](#page-505-1) for up to the timeout period.

System Software should follow these steps while re-initializing and onlining a device:

- 1. Set up the device as required to enable functions impacted by CXL Reset.
- 2. Optionally check whether the device performed clearing or randomizing of memory during the CXL Reset. If yes, skip software-based initialization prior to reallocation. If not, perform software-based initialization.

### <span id="page-806-0"></span>9.7.3 CXL Reset and Request Retry Status (RRS)

The device must successfully complete the configuration write that triggered the CXL Reset. The device behavior in response to Configuration Space access to the device within 100 ms of initiating a CXL Reset is undefined. After 100 ms from the issuance of CXL Reset, the CXL Function is permitted to return RRS for all Configuration Space accesses except to the CXL Status2 register. After 100 ms from the issuance of CXL Reset, software should not access any device register other than the CXL Status2 register until CXL Reset completion, timeout, or error.

## <span id="page-806-1"></span>9.8 Global Persistent Flush (GPF)

Global Persistent Flush (GPF) is a hardware-based mechanism associated with persistent memory that is used to flush cache and memory buffers to a persistence domain. A persistence domain is defined as a location that is guaranteed to preserve the data contents across a restart of the device containing the data. GPF operation is global in nature because all CXL agents that are part of a cache coherency domain participate in the GPF flow. A CXL.cache coherency domain consists of one or more hosts, all CXL Root Ports that belong to these hosts, and the virtual hierarchies associated with these Root Ports.

GPF may be triggered in response to an impending non-graceful shutdown such as a sudden power loss. The host may initiate GPF to ensure that any in-flight data is written back to persistent media prior to a power loss. GPF may also be triggered upon other asynchronous or synchronous events that may or may not involve power loss. The complete list of such events, the mechanisms by which the host is notified, and coordination across CXL Root Ports are beyond the scope of this specification.

### <span id="page-806-2"></span>9.8.1 Host and Switch Responsibilities

With the exception of eRCHs, all hosts and all CXL switches shall support GPF as outlined in this section.

GPF flow consists of two phases, GPF Phase 1 and GPF Phase 2. During Phase 1, the devices are expected to stop injecting new traffic and write back their caches. During Phase 2, the persistent devices are expected to flush their local write buffers to a persistence domain. This two-phase approach ensures that a device does not receive any new traffic while it is flushing its local memory buffers. The host shall enforce a

barrier between the two phases. The host shall ensure that it stops injecting new CXL.cache transactions and that its local caches are written back prior to entering GPF Phase 2.

In certain configurations, the cache write back step may be skipped during GPF Phase 1. There are various possible reasons for implementing this mode of operation that are beyond the scope of this specification. One possible reason could be that the host does not have the required energy to write back all the caches before the power loss. When operating in this mode, the system designer may use other means, beyond the scope of this specification, to ensure that the data that is meant to be persistent is not lost. The host shall set the Payload[1] flag in the GPF Phase 1 request to indicate that the devices shall write back their caches during Phase 1. The host uses a host-specific mechanism to determine the correct setting of Payload[1].

During each phase, the host shall transmit a CXL GPF PM VDM request to each GPFcapable device or Switch that is connected directly to each of its Root Ports and then wait for a response. [Table 3-1](#page-87-1) describes the format of these messages. The Switch's handling of a GPF PM VDM is described in [Section 9.1.2.1.](#page-799-1) The CXL Root Ports and CXL downstream Switch Ports shall implement timeouts to prevent a single device from blocking GPF forward progress. These timeouts are configured by system software (see [Section 8.1.6](#page-521-3)). A host or a Switch may assume that the GPF timeouts configured across Downstream Ports at the same level in the hierarchy are identical. If a Switch detects a timeout, it shall set the Payload[8] in the response to indicate an error condition. This enables a CXL Root Port to detect GPF Phase 1 errors anywhere in the virtual hierarchy it spawns. If an error is detected by any Root Port in the coherency domain, the host shall set the Payload[8] flag during the Phase 2 flow, thereby informing every CXL device of an error during GPF Phase 1. Persistent devices may log this indication in a device-specific manner and make this information available to system software. If the host is positively aware that the GPF event will be followed by a power failure, it should set Payload[0] in the GPF Phase 1 request message. If the host cannot guarantee that the GPF event will be followed by a power failure, it shall not set Payload[0] in the GPF Phase 1 request message.

The CXL devices and switches must be able to receive and process GPF messages without dependency on any other PM messages. GPF messages do not use a credit, and CREDIT\_RTN messages are not expected in response to a GPF request.

The host may reset the device any time after GPF Phase 2 completes.

If the host detection or processing of a GPF event and a reset event overlap, the host may process either event and ignore the other event. If the host detection or processing of a GPF event and an Sx event overlap, the host may process either event and ignore the other event. If host detects a GPF event while it is entering a lower power state, the host is required to process the GPF event in a timely manner.

### <span id="page-807-0"></span>9.8.2 Device Responsibilities

If a device supports GPF, it shall set bit 1 of the CAPABILITY\_VECTOR field in its AGENT\_INFO response (see [Table 3-1](#page-87-1)). All CXL devices with the exception of eRCDs shall support GPF. An eRCD may support GPF functionality. If a device supports GPF, the Device shall respond to all GPF request messages regardless of whether the Device is required to take any action. The host may interpret a lack of response within a software-configured timeout window as an error. For example, a Type 3 device may or may not take any specific action during GPF Phase 1 other than generating a GPF Phase 1 response message.

Upon receiving a GPF Phase 1 request message, a CXL device shall execute the following steps in the specified order:

1. Stop injecting new CXL.cache transactions except for cache write backs described in step 3.

- 2. If CXL.cache capable and Payload[1]=1, disable caching. This will ensure that the device no longer caches any coherent memory and thereby not cache any writes that are received over the CXL interface in its CXL.cache.
- 3. If CXL.cache capable and Payload[1]=1, write back all modified lines in the device cache. The memory destination may be local or remote.
  - To minimize GPF latency, the device should ignore lines that are not dirty.
  - To minimize GPF latency, the device should not write back lines that it knows are mapped to volatile memory. The mechanism by which the device obtains this knowledge is beyond the scope of this specification.
  - The device must use device internal mechanisms to write back all dirty lines that are mapped to its local persistent HDM.
  - The device must write back all dirty lines that are not mapped to its local HDM and may be of persistent type. Each such dirty line must be written back to the destination HDM in two steps:
    - i. Issue DirtyEvict request to the host (see [Section 3.2.4.2.15](#page-121-0)).
    - ii. Issue CLFlush request to the host (see [Section 3.2.4.2.13\)](#page-120-0).
- 4. Indicate that the device is ready to move to GPF Phase 2 by sending a GPF Phase 1 response message. Set the Payload[8] flag in the response if the Phase 1 processing was unsuccessful.

A device may take additional steps to reduce power draw from the system if the Payload[0] flag is set in the request message indicating that power failure is imminent. For example, a device may choose to not wait for responses to the previously issued reads before initiating the write back operation [step 3] above as long as the read responses do not impact persistent memory content.

Until the GPF Phase 2 request message is received, the device must respond to and complete any accesses that it receives over the CXL interface. This is to ensure that the other requesters can continue to make forward progress through the GPF flow.

Upon receiving a GPF Phase 2 request, a CXL device shall execute the following steps in the specified order:

- 1. If it is a persistent memory device and the Payload[8] flag is set, increment the Dirty Shutdown Count (see [Section 8.2.10.9.3.1\)](#page-725-5).
- 2. Flush internal memory buffers to local memory if applicable.
- 3. Acknowledge the request by sending a GPF Phase 2 response message.
- 4. Enter the lowest possible power state.

As this exchange may be performed in the event of an impending power loss, it is important that any flushing activity in either phase is performed in an expedient manner, and that the acknowledgment of each phase is sent as quickly as possible.

A device may have access to an alternate power source (e.g., a device with a large memory buffer may include a charged capacitor or battery) and may acknowledge GPF Phase 2 requests as soon as it has switched over to the alternate power source. Such a device shall ensure that PERST# assertion does not interfere with the local flush flow and shall correctly handle a subsequent power-up sequence even if the local flush is in progress.

A device is not considered to be fully operational after it receives a GPF Phase 1 Request. In this state, a device shall correctly process a Conventional Reset request, and return to operational state upon successful completion of these resets.

If the device detection or processing of a GPF event and a reset event overlap, the device may process either event and ignore the other event. If the device detection or processing of a GPF event and an Sx event overlap, the device may process either event and ignore the other event. If a device receives a GPF request while it is entering a lower power state, it shall process the GPF request in a timely manner.

A pooled device is composed of multiple LDs that are assigned to different Virtual Hierarchies. Because a GPF event may or may not be coordinated across these hierarchies, each LD shall be capable of independently processing GPF messages targeting that individual LD, without affecting any other LD within the MLD. An MLD cannot enter a lower power state until all LDs associated with the device have indicated that they are ready to enter the lower power state. In addition, the MLD must be able to process multiple GPF events (from different VCS targeting unique LDs).

If a device receives a GPF Phase 2 request message without a prior GPF Phase 1 request message, it shall respond to that GPF Phase 2 request message.

### <span id="page-809-0"></span>9.8.3 Energy Budgeting

It is often necessary to assess whether a system has sufficient energy to handle GPF during a power failure scenario. System software may use the information available in various CXL DVSEC registers along with its knowledge of the remainder of the system to make this determination.

This information may also be used to calculate appropriate GPF timeout values at various points in the CXL hierarchy. See the implementation note below. The timeout values are configured through GPF DVSEC for CXL Ports (see [Section 8.1.6\)](#page-521-3).

> **IMPLEMENTATION NOTE**

System software may determine the total energy needs during power failure GPF. There may always be a nonzero possibility that power failure GPF may not successfully complete (e.g., under unusual thermal conditions or fatal errors). The goal of the system designer is to ensure that the probability of failure is sufficiently low and meets the system design objectives.

The following high-level algorithm may be followed for calculating timeouts and energy requirements

- 1. Iterate through every CXL device and calculate T1 and T2 as defined in Column "Time needed" in [Table 9-3.](#page-810-0)
- 2. Calculate T1MAX and T2MAX.
  - a. T1MAX = MAX of T1 values calculated for all devices plus propagation delay, host-side processing delays, and any other host/system-specific delays.
  - b. T2MAX = MAX of T2 values calculated for all devices in the hierarchy plus propagation delay, host-side processing delays, and any other host/systemspecific delays. This could be same as GPF Phase 2 timeout at RC.
- 3. Calculate E1 and E2 for each device. See Column "Energy needed" in [Table 9-3](#page-810-0).
- 4. Do summation over all CXL devices (E1+E2). Add energy needs for host and non-CXL devices during this window.

> **IMPLEMENTATION NOTE**



The GPF timeout registers in the root port and the Downstream Switch Port CXL Port GPF Capability structure may be programmed to T1MAX and T2MAX, respectively. Device active power is the amount of power that the device consumes in D0 state and may be reported by the device via Power Budgeting Extended Capability as defined in PCIe Base Specification. Cache size is reported via PCIe DVSEC for CXL devices (Revision 1). This computation may have to be redone periodically as some of these factors may change. When a CXL device is hot-added/removed, it may warrant recomputation. Refer to [Table 9-3.](#page-810-0)

Cache size, T2, and GPF Phase 2 Power parameters are reported by the device via GPF DVSEC for CXL devices (see [Section 8.1.7\)](#page-523-4). The other parameters are system dependent. System software may use ACPI HMAT to determine average persistent memory bandwidth, but the software could apply additional optimizations if it is aware of the specific persistent device the accelerator is operating on. In some cases, System Firmware may be the one performing this computation. Since System Firmware may or may not be aware of workloads, it may make conservative assumptions.

If the system determines that it does not have sufficient energy to handle all CXL devices, it may be able to take certain steps, such as to reconfigure certain devices to stay within the system budget by reducing the size of cache allocated to persistent memory or limit persistent memory usages. Several system level and device-level optimizations are possible:

- Certain accelerators may always operate on volatile memory and could skip the flush. For these accelerators, T1 would be 0.
- Device could partition cache among volatile vs. non-volatile memory and thus lower T1. Such partitioning may be accomplished with assistance from system software.
- A device could force certain blocks (e.g., execution engines) into a lower power state upon receiving a GPF Phase 1 request.
- Device may include a local power source and therefore could lower its T1 and T2.
- System software may configure all devices so that all T1s and T2s are roughly equal. This may require performance and/or usage model trade-offs.

<span id="page-810-0"></span>**Table 9-3. GPF Energy Calculation Example**

| Device Step                                      | Time Needed                                                                                                      | Energy Needed                   |  |
|--------------------------------------------------|------------------------------------------------------------------------------------------------------------------|---------------------------------|--|
| Stop traffic generation                          | Negligible                                                                                                       | Negligible                      |  |
| Disable caching                                  | Negligible                                                                                                       | Negligible                      |  |
| Write back cache content to<br>persistent memory | T1= Cache size * % of lines in cache<br>mapped to persistent memory / worst<br>case persistent memory bandwidth. | E1= T1MAX * device active Power |  |
| Flush local Memory buffers<br>to local memory    | T2                                                                                                               | E2= T2 * GPF Phase 2 Power      |  |

## <span id="page-811-0"></span>9.9 Hot-Plug

<span id="page-811-1"></span>By definition, RCDs and RCHs do not support Hot-Plug.

CXL Root Ports and CXL Downstream Switch Ports may support Hot-Add and managed Hot-Remove. All CXL Ports shall be designed to avoid electrical damage upon surprise Hot-Remove. All CXL switches and CXL devices, with the exception of eRCDs, shall be capable of being Hot-Plugged, subject to the Form Factor limitations. In a managed Hot-Remove flow, software is notified of a hot removal request. This provides CXLaware system software the opportunity to write back device cachelines and to offline device memory prior to removing power. During a Hot-Add flow, CXL-aware system software discovers the CXL.cache and CXL.mem capabilities of the adapter and initializes them so they are ready to be used.

CXL leverages PCIe Hot-Plug model and Hot-Plug elements as defined in PCIe Base Specification and the applicable form-factor specifications.

CXL isolation is the mechanism that is used for graceful handling of Surprise Hot-Remove of CXL adapters. If a CXL adapter that holds modified lines in its cache is removed without any prior notification and CXL.cache isolation is not enabled, subsequent accesses to those addresses may result in timeouts that may be fatal to host operation. If a CXL adapter with HDM is removed without any prior notification and CXL.mem isolation is not enabled, subsequent accesses to HDM locations may result in timeouts that may be fatal to host operation.

All CXL Downstream Ports, including RCH Downstream Ports, shall hardwire the Hot-Plug Surprise bit in the Slot Capabilities register to 0. Software may leverage Downstream Port Containment capability of the Downstream Port to gracefully handle surprise hot removal of PCIe adapters or contain errors that result from surprise hot removal or Link Down of CXL adapters.

Support for Coherent Device Attribute Table (CDAT) by way of ReadTable DOE (see [Section 8.1.11\)](#page-527-6) is optional for eRCDs, but mandatory for all other CXL devices and is also mandatory for CXL switches. Software may use this interface to learn about performance and other attributes of the device or the Switch.

The Host Bridge and Upstream Switch Ports implement the HDM Decoder Capability structure. Software may program these to account for the HDM capacity with an appropriate interleaving scheme (see [Section 9.13.1\)](#page-832-1). Software may choose to leave the decoders unlocked for maximum flexibility and use other protections (e.g., page tables) to limit access to the registers. All unused decoders are unlocked by definition and software may claim these to decode additional HDM capacity during a Hot-Add flow.

All CXL.cache-capable devices, with the exception of eRCDs, shall implement the Cache Writeback and Invalidation capability (see [Section 9.6\)](#page-803-0). Software may use this capability to ensure that a CXL.cache-capable device does not have any modified cachelines prior to removing power.

Software shall ensure that the device has completed Power Management Initialization (see [Section 8.1.3.5\)](#page-505-1) prior to enabling its CXL.cache capabilities or CXL.mem capabilities if the device reports PM Init Completion Reporting Capable=1.

Software shall ensure that it does not enable a CXL.cache device below a given Root Port if the Root Port does not support CXL.cache. The Root Port's capabilities are exposed via the DVSEC Flex Bus Port Capability register. All CXL.cache-capable devices should expose the size of their cache via the DVSEC CXL Capability2 register. Software may cross-check this against the host's effective snoop filter capabilities (see [Section 8.2.4.23.2\)](#page-581-2) during Hot-Add of CXL.cache-capable device. Software may configure the Cache\_SF\_Coverage field in the DVSEC CXL Control register to indicate to the device how much snoop filter capacity it should use (0 being a legal value). In extreme scenarios, software may disable CXL.cache devices to avoid snoop filter oversubscription.

During Hot-Add, System Software may reassess the GPF energy budget and take corrective action if necessary.

Hot-Add of an eRCD may result in unpredictable behavior if the device is exposed to software. The following mechanisms are defined to ensure that an eRCD that is hotadded in runtime is not discoverable by standard PCIe software:

- For Root Ports connected to Hot-Plug capable slots, it is recommended that System Firmware set the Disable\_RCD\_Training bit (see [Section 8.2.1.3.2\)](#page-537-0) after System Firmware PCIe enumeration completion, but before OS hand-off. This will ensure that a CXL root port will fail link training if an eRCD is hot-added. A Hot-Plug event may be generated in these cases, and the Hot-Plug handler may be invoked. The Hot-Plug handler may treat this condition as a failed Hot-Plug, notify the user, and then power down the slot.
- A Downstream Switch Port may itself be hot-added and cannot rely on System Firmware setting the Disable\_RCD\_Training bit. A Switch shall not report a Link Up condition and shall not report presence of an adapter when it is connected to an eRCD. System Firmware or CXL-aware software may still consult DVSEC Flex Bus Port Status (see [Section 8.2.1.3.3](#page-538-0)) and discover that the Port is connected to an eRCD.

> **IMPLEMENTATION NOTE**

**CXL Type 3 device Hot-Add flow**

- 1. System Firmware may prepare the system for a future Hot-Add (e.g., pad resources to accommodate the needs of an adapter to be hot-added).
- 2. User hot-adds a CXL memory expander in an empty slot. Downstream Ports bring up the link in CXL VH mode.
- 3. PCIe Hot-Plug interrupt is generated.
- 4. Bus driver performs the standard PCIe Hot-Add operations, thus enabling CXL.io. This process assigns BARs to the device.
- 5. CXL-aware software (e.g., CXL bus driver in OS, the device driver, or other software entity) probes CXL DVSEC capabilities on the device and ensures that the HDM is active. Memory may be initialized either by hardware, by the FW on the adapter or the device driver.
- 6. CXL-aware software configures the CXL DVSEC structures on the device, switches, and Host Bridge (e.g., GPF DVSEC, HDM decoders).
- 7. CXL-aware software notifies the OS memory manager about the new memory and its attributes such as latency and bandwidth. Memory manager processes a request and adds the new memory to its allocation pool.
- 8. The user may be notified via attention indicator or some other user interface of successful completion.

> **IMPLEMENTATION NOTE**

### CXL Type 3 device-managed Hot-Remove flow

- 1. User initiates a Hot-Remove request via attention button or some other user interface.
- 2. The standard PCIe Hot-Remove flow is triggered (e.g., via Hot-Plug interrupt if attention button was used).
- 3. CXL-aware software (e.g., CXL bus driver in OS, the device driver, or other software entity) probes CXL DVSEC capabilities on the device and determines active memory ranges.
- 4. CXL-aware software requests the OS memory manager to vacate these ranges.
- 5. If the Memory Manager is unable to fulfill this request (e.g., because of presence of pinned pages), CXL-aware software will return an error to the Hot-Remove handler, which will notify the user that the operation has failed.
- 6. If the Memory Manager is able to fulfill this request, CXL-aware system software reconfigures HDM Decoders in CXL switches and Root Ports. This is followed by the standard PCIe Hot-Remove flow that will process CXL.io resource deallocation.
- 7. If the PCIe Hot-Remove flow fails, the user is notified that the Hot-Remove operation has failed; otherwise, the user is notified that the Hot-Remove flow has successfully completed.

> **IMPLEMENTATION NOTE**

### CXL Type 1 device Hot-Add flow

- 1. System Firmware may prepare the system for a future Hot-Add (e.g., pad MMIO resources to accommodate the needs of an adapter to be hot-added).
- 2. The user Hot-Adds a CXL Type 1 device in an empty slot. The Downstream Port brings up the link in CXL VH operation with 68B Flit mode.
- 3. A PCIe Hot-Plug interrupt is generated.
- 4. The bus driver performs the standard PCIe Hot-Add operations, thus enabling CXL.io. This process assigns BARs to the device.
- 5. CXL-aware software (e.g., CXL bus driver in OS, the device driver, or other software entity) probes CXL DVSEC capabilities on the device. If the device is hotadded below a Root Port that cannot accommodate a CXL.cache-enabled device, Hot-Add is rejected. If the device has a cache that is larger than what the host snoop filter can handle, Hot-Add is rejected. The user may be notified via attention indicator or some other user interface of this.
- 6. If the above checks pass, CXL-aware software configures the CXL DVSEC structures on the device and switches (e.g., GPF DVSEC).
- 7. The Hot-Add flow is complete. The user may be notified via attention indicator or some other user interface of successful completion.

## <span id="page-814-0"></span>9.10 Software Enumeration

This section describes two types of CXL device enumeration flows. Although discovery of CXL devices follows the PCIe model, there are some important differences:

- RCD Enumeration: As the name suggests, RCD mode (see [Section 9.11.1](#page-814-2)) imposes some restrictions and leads to a much-simpler enumeration flow. Each RCD is exposed to host software as one or more PCIe Root Complex Integrated Endpoints as indicated by setting PCI Express Capabilities Register.Device/Port Type=RCiEP. Each RCD creates a new PCIe enumeration hierarchy that is compatible with an ACPI-defined PCIe Host Bridge (PNP ID PNP0A08). The RCD enumeration flow is described in [Section 9.11.](#page-814-1)
- CXL VH enumeration: A CXL root port is the root of a CXL VH. A CXL VH may include zero or more CXL switches, zero or more PCIe switches, zero or more PCIe devices, and one or more CXL devices that are not in RCD mode. A CXL VH represents a software view and may differ from the physical topology. The CXL VH enumeration flow is described in [Section 9.12.](#page-822-0)

<span id="page-814-4"></span>A CXL device cannot claim I/O resources because it is not a Legacy Endpoint. For the definition of Legacy Endpoint, see PCIe Base Specification.

## <span id="page-814-1"></span>9.11 RCD Enumeration

### <span id="page-814-2"></span>9.11.1 RCD Mode

<span id="page-814-3"></span>Restricted CXL device (RCD) mode is a CXL operating mode with the following restrictions:

- Hot-Plug is not supported
- CXL devices operating in this mode always set the Device/Port Type field in the PCI Express Capabilities register to RCiEP
- Flit modes other than 68B Flit mode are not supported
- Routing types other than HBR are not supported
- Link is not visible to non-CXL-aware software

### <span id="page-815-0"></span>9.11.2 PCIe Software View of an RCH and RCD

<span id="page-815-3"></span>**Figure 9-4. PCIe Software View of an RCH and RCD**

![](_page_815_Figure_4.jpeg)

Because the CXL link is not exposed to CXL-unaware OSs, the System Firmware view of the hierarchy is different than that of the CXL-unaware OS.

### <span id="page-815-1"></span>9.11.3 System Firmware View of an RCH and RCD

The functionality of the RCH Downstream Port and the RCD Upstream Port can be accessed via memory mapped registers. These will not show up in a standard PCIe bus scan by CXL-unaware OSs. The base addresses of these registers are set up by System Firmware and System Firmware can use that knowledge to configure CXL.

System Firmware configures the RCH Downstream Port to decode the memory resource needs of the CXL device as expressed by PCIe BARs and Upstream Port BAR(s). PCIe BARs are not to be configured to decode any HDM that are associated with the CXL device.

### <span id="page-815-2"></span>9.11.4 OS View of an RCH and RCD

Each RCH-RCD pair is presented as one ACPI Host bridge. The \_BBN method for this Host Bridge matches the bus number that hosts the RCD.

This ACPI Host Bridge spawns a legal PCIe hierarchy. All PCIe Endpoints located in the RCD are children of this ACPI Host Bridge. These Endpoints may appear directly on the Root bus number or may appear behind a Root Port located on the Root bus.

The \_CRS method for PCIe root bridge returns bus and memory resources claimed by the CXL Endpoints. \_CRS response does not include HDM on CXL.mem-capable devices, and does not comprehend any Upstream Port BARs (hidden from OS).

![](_page_816_Picture_1.jpeg)

A CXL-aware OS may use CXL Early Discovery Table (CEDT) or \_CBR object in ACPI namespace to locate the Downstream Port registers and Upstream Port registers. CEDT enumerates all CXL Host Bridges that are present at the time of OS hand-off and \_CBR is limited to CXL Host Bridges that are hot-added.

### <span id="page-816-0"></span>9.11.5 System Firmware-based RCD Enumeration Flow

Because RCDs do not support Hot-Add, RCDs can be fully enumerated by System Firmware prior to OS hand-off.

In the presence of RCD mode, the hardware autonomous mode selection flow cannot automatically detect the number of retimers. If the system includes retimers, the System Firmware shall follow these steps to ensure that the number of retimers is correctly configured:

- 1. Prior to the link training, the System Firmware should set the DVSEC Flex Bus Port control register, based on the available information, to indicate whether there are 0, 1, or 2 retimers present. (It is possible that retimers on a CXL add-in card or a backplane may not be detected by the System Firmware prior to link training and the initial programming may not account for all retimers in the path.)
- 2. After the link training completes successfully or fails, the System Firmware should read the Retimer Presence Detected and Two Retimers Presence Detected values logged in the PCIe standard Link Status 2 register and determine whether they are consistent with what was set in the Flex Bus Port DVSEC in the previous step. If they are different, the System Firmware should bring the Link Down by setting the Link Disable bit in the Downstream Port, update the Retimer1\_Present and Retimer2\_Present bits in the Flex Bus Port DVSEC, and then re-initiate link training.

### <span id="page-816-1"></span>9.11.6 RCD Discovery

- 1. Parse configuration space of Device 0, Function 0 on the Secondary bus # and discover CXL-specific attributes. These are exposed via PCIe DVSEC for CXL Devices Capability structures. See [Section 8.1.3.](#page-500-5)
- 2. If the device supports CXL.cache, configure the CPU coherent bridge and then set the Cache\_Enable bit in the DVSEC CXL Control register.
- 3. If the device supports CXL.mem, check Mem\_HwInit\_Mode by reading the DVSEC CXL Capability register and determine the number of supported HDM ranges by reading the HDM\_Count field in the same register.
- 4. If Mem\_HwInit\_Mode=1:
  - The device must set the Memory\_Info\_Valid bit in each applicable DVSEC CXL Range X Size Low register (X=1, 2) within 1 second of reset deassertion.
  - The device must set the Memory\_Active\_Valid bit in each applicable DVSEC CXL Range X Size Low register (X=1, 2) within the Memory\_Active\_Timeout duration of reset deassertion.
  - When Memory\_Info\_Valid is 1, System Firmware reads the Memory\_Size\_High and Memory\_Size\_Low fields for each supported HDM range. If System Firmware cannot delay boot until the Memory\_Active bit is set, the System Firmware may continue with HDM base assignment and may delay OS hand-off until the Memory\_Active bit is set.
  - System Firmware computes the size of each HDM range and maps those in system address space.
  - System Firmware programs the Memory\_Base\_Low and the Memory\_Base\_High fields for each HDM range.
  - System Firmware programs the ARB/MUX arbitration control registers if necessary.

- System Firmware sets CXL.mem Enable. Once Memory\_Active=1, Any subsequent accesses to HDM are decoded and routed to the local memory by the device.
- Each HDM range is later exposed to the OS as a separate, memory-only NUMA node via ACPI SRAT.
- System Firmware obtains CDAT from the UEFI device driver or directly from the device via Table Access DOE (see [Section 8.1.11](#page-527-6)) and then uses this information during construction of the memory map, ACPI SRAT, and ACPI HMAT. See ACPI Specification, CDAT Specification, and UEFI Specification for further details.

### 5. If Mem\_HwInit\_Mode =0

- The device must set the Memory\_Info\_Valid bit in each applicable DVSEC CXL Range X Size Low register (X=1, 2) within 1 second of reset deassertion.
- When Memory\_Info\_Valid is 1, System Firmware reads the Memory\_Size\_High and Memory\_Size\_Low fields for supported HDM ranges.
- System Firmware computes the size of each HDM range and maps those in system address space.
- System Firmware programs the Memory\_Base\_Low and the Memory\_Base\_High fields for each HDM range.
- System Firmware programs the ARB/MUX arbitration control registers if necessary.
- System Firmware sets CXL.mem Enable. Any subsequent accesses to the HDM ranges are decoded and completed by the device. The reads shall return all 1s and the writes will be dropped.
- Each HDM range is later exposed to the OS as a separate, memory-only NUMA node via ACPI SRAT.
- If the memory is initialized prior to OS boot by UEFI device driver:
  - The UEFI driver is responsible for causing Memory\_Active to be set. The driver can accomplish that by device-specific methods, such as by setting a device-specific register bit.
  - After Memory\_Active is set, any subsequent accesses to the HDM range are decoded and routed to the local memory by the device.
  - System Firmware uses the information supplied by UEFI driver or Table Access DOE (see [Section 8.1.11\)](#page-527-6) during construction of the memory map and ACPI HMAT. See UEFI Specification for further details.
- If the memory is initialized by an OS device driver post OS boot:
  - System Firmware may use the information supplied by UEFI driver or Table Access DOE (see [Section 8.1.11\)](#page-527-6) during construction of the memory map and ACPI HMAT. See UEFI Specification for further details. In the future, a CXL-aware OS may extract this information directly from the device via Table Access DOE.
  - At OS hand-off, System Firmware reports that the memory size associated with HDM NUMA node is 0.
  - The OS device driver is responsible for causing the Memory\_Active bit to be set to 1 by using device-specific methods after memory initialization is complete. Any subsequent accesses to the HDM are decoded and routed to the local memory by the device.
  - Memory availability is signaled to the OS via an OS-specific mechanism.

CXL.io resource needs are discovered as part of PCIe enumeration. PCIe Root Complex registers, including Downstream Port registers, are appropriately configured to decode these resources. CXL Downstream Ports and Upstream Ports require MMIO resources. These are also accounted for during this process.

System Firmware programs the memory base and limit registers in the Downstream Port to decode CXL Endpoint MMIO BARs, CXL Downstream Port MMIO BARs, and CXL Upstream Port MMIO BARs.

### <span id="page-818-0"></span>9.11.7 eRCDs with Multiple Flex Bus Links

This section is applicable only to eRCDs that are directly connected to an eRCH. It does not apply to CXL VH. Also, it does not apply to eRCDs that are connected to CXL switches.

#### <span id="page-818-1"></span>9.11.7.1 Single CPU Topology

<span id="page-818-2"></span>**Figure 9-5. One CPU Connected to a Dual-Headed RCD by Two Flex Bus Links**

![](_page_818_Figure_8.jpeg)

In this configuration, the System Firmware shall report two PCIe Host Bridges to the OS, one that hosts Device 0, Function 0 on the left, and a second one that hosts Device 0, Function 0 on the right. Both Device 0, Function 0 instances implement PCIe DVSEC for CXL Devices and a Device Serial Number PCIe Extended Capability. A Vendor ID and serial number match indicates that the two links are connected to a single CXL device, which enables System Firmware to perform certain optimizations.

In some cases, the CXL device may expose a single CXL device function that is managed by the CXL device's driver, whereas the other Device 0, Function 0 represents a dummy device. In this configuration, application software may submit work to the single CXL device instance. However, the CXL device hardware is free to use both links for traffic and snoops as long as the programming model is not violated.

The System Firmware maps the HDM into system address space using the rules listed in [Table 9-4](#page-819-2).

<span id="page-819-2"></span>**Table 9-4. Memory Decode Rules in Presence of One CPU/Two Flex Bus Links**

| Left D0, F0<br>Mem_Capable | Left D0, F0<br>Mem_Size | Right D0, F0<br>Mem_Capable | Right D0, F0<br>Mem_Size | System Firmware Requirements                                                                                            |
|----------------------------|-------------------------|-----------------------------|--------------------------|-------------------------------------------------------------------------------------------------------------------------|
| 0                          | N/A                     | 0                           | N/A                      | No HDM.                                                                                                                 |
| 1                          | M                       | 0                           | N/A                      | Range of size M decoded by Left Flex Bus<br>link. Right Flex Bus link does not receive<br>CXL.mem traffic.              |
| 0                          | N/A                     | 1                           | N                        | Range of size N decoded by Right Flex Bus<br>link. Left Flex Bus link does not receive<br>CXL.mem traffic.              |
| 1                          | M                       | 1                           | N                        | Two ranges set up, Range of size M decoded<br>by Left Flex Bus link, Range of size N decoded<br>by Right Flex Bus link. |
| 1                          | M                       | 1                           | 0                        | Single range of size M. CXL.mem traffic is<br>interleaved across two links.                                             |
| 1                          | 0                       | 1                           | N                        | Single range of size N. CXL.mem traffic is<br>interleaved across two links.                                             |

#### <span id="page-819-0"></span>9.11.7.2 Multiple CPU Topology

<span id="page-819-1"></span>**Figure 9-6. Two CPUs Connected to One CXL Device by Two Flex Bus Links**

<span id="page-819-3"></span>![](_page_819_Figure_6.jpeg)

In this configuration, System Firmware shall report two PCIe Host Bridges to the OS, one that hosts Device 0, Function 0 on the left, and a second one that hosts Device 0, Function 0 on the right. Both Device 0, Function 0 instances implement PCIe DVSEC for CXL Devices and a Device Serial Number PCIe Extended Capability. A Vendor ID and serial number match indicates that the two links are connected to a single accelerator, which enables System Firmware to perform certain optimizations.

In some cases, the accelerator may choose to expose a single accelerator function that is managed by the accelerator device driver and handles all work requests. This may be necessary if the accelerator framework or applications do not support distributing work across multiple accelerator instances. Even in this case, both links should spawn a legal

PCIe Host Bridge hierarchy with at least one PCIe function. However, the accelerator hardware is free to use both links for traffic and snoops as long as the programming model is not violated. To minimize the snoop penalty, the accelerator needs to be able to distinguish between the system memory range decoded by CPU 1 vs. CPU 2. The device driver can obtain this information via ACPI SRAT and communicate it to the accelerator using device-specific mechanisms.

The System Firmware maps the HDM into system address space using the following rules. Unlike the single CPU case, the System Firmware shall never interleave the memory range across the two Flex Bus links.

<span id="page-820-1"></span>**Table 9-5. Memory Decode Rules in Presence of Two CPU/Two Flex Bus Links**

| Left D0, F0<br>Mem_Capable | Left D0, F0<br>Mem_Size | Right D0, F0<br>Mem_Capable | Right D0, F0<br>Mem_Size | System Firmware Requirements                                                                                            |  |
|----------------------------|-------------------------|-----------------------------|--------------------------|-------------------------------------------------------------------------------------------------------------------------|--|
| 0                          | N/A                     | 0                           | N/A                      | No HDM                                                                                                                  |  |
| 1                          | M                       | 0                           | N/A                      | Range of size M decoded by Left Flex Bus                                                                                |  |
| 1                          | M                       | 1                           | 0                        | link. Right Flex Bus link does not receive<br>CXL.mem traffic.                                                          |  |
| 0                          | N/A                     | 1                           | N                        | Range of size N decoded by Right Flex Bus<br>link. Left Flex Bus link does not receive<br>CXL.mem traffic.              |  |
| 1                          | 0                       | 1                           | N                        |                                                                                                                         |  |
| 1<br>M                     |                         | 1                           | N                        | Two ranges set up, Range of size M decoded<br>by Left Flex Bus link, Range of size N<br>decoded by Right Flex Bus link. |  |

### <span id="page-820-0"></span>9.11.8 CXL Devices Attached to an RCH

When an eRCD is attached to an RCH, the register layout matches [Figure 9-4](#page-815-3).

When a CXL device other than an eRCD is attached to a CXL RP or a CXL DSP, the device's Upstream Port registers are accessed via the CXL Device's PCIe Configuration space and BAR. A CXL device may be designed so that the layout of the device's Upstream Port and Component Registers follow [Figure 9-4](#page-815-3) when connected to an RCH. For such a device, some of these registers must be remapped so that they are accessible via an RCD Upstream Port RCRB (see [Section 8.2.1.2,](#page-533-1) [Section 8.2.1.3](#page-535-2), and [Section 8.2.2](#page-540-2)). This register remapping is illustrated in [Figure 9-7.](#page-821-0) The left half shows the register layout when a CXL device with a single PCIe Function is connected to a CXL Root Port or CXL DSP. The right half shows the register layout when the same device is connected to an RCH. Such a device shall capture the upper address bits [63:12] of the first memory read received after link initialization as the base address of the Upstream Port RCRB (see [Section 8.2.1.2](#page-533-1)).

<span id="page-821-0"></span>**Figure 9-7. CXL Device Remaps Upstream Port and Component Registers**

![](_page_821_Figure_3.jpeg)

A CXL device may be designed so that the layout of the device's Upstream Port and Component Registers still follows the CXL device layout for a CXL VH when connected to an RCH. In that case, the register remapping is unnecessary. This is illustrated in [Figure 9-8.](#page-822-1) The left half shows the register layout when a CXL device with a single PCIe Function is connected to a CXL Root Port or a CXL DSP. The right half shows the register layout when the same device is connected to an RCH. Such a device shall capture the upper address bits [63:12] of the first memory read received after link initialization as the base address of the Upstream Port RCRB, but all reads to the Upstream Port RCRB range shall return all 1s. Additionally, all writes shall be completed, but silently dropped by such a device. The software may rely upon this behavior to detect a device. Note that the DWORD read to RCRB Base + 4 KB is guaranteed to return a value other than FFFF FFFFh when directed at an eRCD or a CXL device that follows the [Figure 9-4](#page-815-3) register layout when connected to an RCH (see [Figure 8-10\)](#page-534-1). An RCD is also permitted to implement the register mapping scheme shown in the right half of [Figure 9-8](#page-822-1). In both cases, the RCD appears as an RCiEP.

<span id="page-822-1"></span>**Figure 9-8. CXL Device that Does Not Remap Upstream Port and Component Registers**

> **IMPLEMENTATION NOTE**

**Host Firmware/Software Flow for detecting the RCD Registers Mapping Scheme**

- 1. System Firmware reads DVSEC Flex Bus Port Status register (see [Section 8.2.1.3.3](#page-538-0)) in the Downstream Port to determine whether the link trained up in RCD mode. If the Cache\_Enabled bit or Mem\_Enabled bit is set to 1, but the CXL 68B Flit and VH Enabled bit is cleared to 0, it indicates RCD mode.
- 2. If an RCD is detected, System Firmware programs the Downstream Port registers to decode the 8-KB RCRB range among other memory ranges.
- 3. System Firmware issues a DWORD read to the address RCRB Base + 4 KB. As explained in [Section 8.2.1.2,](#page-533-1) the device captures the address and assigns it as the base of RCRB. The device implementation may rely on a read to RCRB Base + 4 KB since the CXL 1.1 specification requires such a read.
- 4. If the returned data is not FFFF FFFFh, the System Firmware assumes that the register layout follows the right side of [Figure 9-7](#page-821-0) and enumerates the device accordingly.
<span id="page-822-2"></span>- 5. If the returned data is FFFF FFFFh and the Register Locator DVSEC includes a pointer to the Component Registers, the System Firmware assumes that the register layout follows the right side of [Figure 9-8](#page-822-1) and enumerates the device accordingly.

## <span id="page-822-0"></span>9.12 CXL VH Enumeration

At the top level, a CXL system may be represented to the system software as zero or more CXL Host bridges, and zero or more PCIe Host Bridges. A CXL Host Bridge is a software concept that represents one of the following:

• A collection of CXL Root Ports that share some logic, such as CHBCR

- An RCH-RCD pair
- One or more CXL Root Complex Integrated Endpoints, all of which are part of the Root Complex and appear at the same bus number

Enumeration of PCIe Host Bridges and PCIe hierarchy underneath them is governed by PCIe Base Specification. Enumeration of CXL Host Bridges is described below.

In an ACPI-compliant system, CXL Host Bridges are identified with an ACPI Hardware ID (HID) of "ACPI0016". CXL Early Discovery Table (CEDT) may be used to differentiate between the three software concepts listed above. RCD enumeration is described in [Section 9.11.](#page-814-1)

### <span id="page-823-0"></span>9.12.1 CXL Root Ports

Each CXL Host Bridge is associated with a Base Bus Number. If the Host Bridge is not associated with RCDs or CXL RCiEPs, that bus number shall contain one or more CXL Root Ports. These Root Ports appear in PCIe configuration space with a Type 1 header, and the Device/Port Type field in the PCIe Capabilities Register shall identify these as standard PCIe Root Ports. Unless specified otherwise, CXL Root Ports may implement all Capabilities that are defined in PCIe Base Specification as legal for PCIe Root Ports. These Root Ports can be in one of four states:

- Disconnected
- Connected to an eRCD
- Connected to CXL Device that is not an eRCD, or connected to a CXL Switch
- Connected to a PCIe Device/Switch

[Section 9.12.3](#page-824-0) describes how software can determine the current state of a CXL Root Port and the corresponding enumeration algorithm.

### <span id="page-823-1"></span>9.12.2 CXL Virtual Hierarchy

CXL Root Ports may be directly connected to a CXL device that is not an eRCD, or a CXL Switch. These Root Ports spawn a CXL Virtual Hierarchy (VH). Enumeration within a CXL VH is described below.

These CXL devices appear as a standard PCIe Endpoints with a Type 0 Header. The CXL device's primary function (Function 0) shall carry one instance of CXL DVSEC ID 0 with Revision 1 or greater. Software may use this DVSEC instance to distinguish a CXL device from an ordinary PCIe device. Unless specified otherwise, CXL devices may implement all Capabilities that are defined in PCIe Base Specification as legal for PCIe devices.

A CXL VH may include zero or more CXL switches. Specific configuration constraints are documented in [Chapter 7.0.](#page-318-4) From an enumeration software perspective, each CXL Switch consists of one Upstream Switch Port and one or more Downstream Switch Ports.

The configuration space of the Upstream Switch Port of a CXL Switch has a Type 1 header and the Device/Port Type field in the PCIe Capabilities Register shall identify it as an Upstream Port of a PCIe Switch. The configuration space carries one instance of the CXL DVSEC ID 3 and one instance of DVSEC ID 7. The DVSEC Flex Bus Port Status register in CXL DVSEC ID 7 structure of the peer Port shall indicate that CXL VH operation with 68B Flit mode was negotiated with the Upstream Switch Port during link training. Unless specified otherwise, CXL Upstream Switch Ports may implement all Capabilities that are defined in PCIe Base Specification as legal for PCIe Upstream Switch Ports.

The configuration space of a Downstream Switch Port of CXL Switch also has a Type 1 header, but the Device/Port Type field in the PCIe Capabilities Register shall identify these as a Downstream Port of a PCIe Switch. Unless specified otherwise, CXL Downstream Switch Ports may implement all Capabilities that are defined in PCIe Base Specification as legal for PCIe Downstream Switch Ports. All these Ports are CXL capable and can be in one of four states, just like the CXL Root Ports:

- Disconnected
- Connected to an eRCD
- Connected to CXL Device that is not an eRCD, or connected to a CXL Switch
- Connected to a PCIe Device/Switch

[Section 9.12.3](#page-824-0) describes how software can determine the current state of a CXL Downstream Switch Port and the corresponding enumeration algorithm.

A CXL Downstream Switch Port may be connected to another CXL Switch or a CXL device. The rules for enumerating CXL switches and CXL devices are already covered earlier in this section.

### <span id="page-824-0"></span>9.12.3 Enumerating CXL RPs and DSPs

Software may use the combination of the Link Status registers and the CXL DVSEC ID 7 capability in root port or DSP configuration space to determine which state a CXL Downstream Port is in, as follows:

- 1. CXL root port or DSP is in the Disconnected state when they do not have an active link. The status of the link can be detected by following PCIe Base Specification. If the link is not up, software shall ignore the CXL DVSEC ID 3 and the CXL DVSEC ID 7 capability structures. A Hot-Add event may transition a Disconnected Port to a CXL Connected state or a PCIe Connected state. Hot-adding an eRCD adapter will transition the Port to an Undefined state.
- 2. CXL root port or DSP connected to a CXL device that is not an RCD or connected to a CXL switch shall expose one instance of the CXL DVSEC ID 3 and one instance of the CXL DVSEC ID 7 capability structures. The DVSEC Flex Bus Port Status register in the CXL DVSEC ID 7 structure shall indicate that CXL VH operation with 68B Flit mode was successfully negotiated during link training. System Firmware may leave the Unmask SBR and the Unmask Link Disable bits in the Port Control register of the Downstream Port at the default (0) values to prevent CXL-unaware PCIe software from resetting the device and the link, respectively.
- 3. CXL root port or DSP connected to an eRCD shall expose one instance of the CXL DVSEC ID 3 and one instance of the CXL DVSEC ID 7 capability structures. The DVSEC Flex Bus Port Status register in the CXL DVSEC ID 7 structure shall indicate that CXL VH operation with 68B Flit mode was not negotiated, but that either the CXL.cache protocol or the CXL.mem protocol was negotiated during link training. There are two possible substates:
  - a. Not Operating with RCH Downstream Port addressing Immediately after the link negotiation, the Port registers appear in the PCIe configuration space with a Type 1 header.
  - b. Operating with RCH Downstream Port addressing System Firmware may program the RCRB Base register in the Port's CXL DVSEC ID 3 capability structure to transition the Port to this mode. Once the Port is in this mode, it can only transition out of the mode after a reset. A Downstream Port operating in this mode shall ignore hot reset requests received from the Upstream Port.
- 4. CXL root port or DSP connected to a PCIe device/switch may or may not expose the CXL DVSEC ID 3 and the CXL DVSEC ID 7 capability structures.

- a. If the PCIe root port configuration space contains an instance of the CXL DVSEC ID 3 structure, it shall also contain an instance of the CXL DVSEC ID 7 structure.
- b. If the PCIe root port configuration space contains an instance of the CXL DVSEC ID 7 structure, the DVSEC Flex Bus Port Status register shall indicate that this Port did not train up in CXL mode. Software shall ignore the contents of the CXL DVSEC ID 3 structure for such a Port.

<span id="page-825-2"></span>**Figure 9-9. CXL Root Port/DSP State Diagram**

![](_page_825_Figure_5.jpeg)

If the Port is in the disconnected state, the branch does not need further enumeration.

If the Port is connected to a CXL device other than an eRCD or connected to a CXL switch, the software follows [Section 9.12.2](#page-823-1) for further enumeration until it reaches the leaf endpoint.

If the Port is connected to an RCD, the software follows [Section 9.12.4](#page-825-0) to enumerate the device.

<span id="page-825-3"></span>If the Port is connected to a PCIe device/switch, the enumeration flow is governed by PCIe Base Specification.

### <span id="page-825-0"></span>9.12.4 eRCD Connected to a CXL RP or DSP

An eRCD may be connected to a CXL Root Port or a CXL Downstream Switch Port. Each RCD Function must report itself as an RCiEP and therefore cannot appear, to software, to be below a PCIe-enumerable Downstream Port. System Firmware is responsible for detecting such a case and reconfiguring the CXL Ports in the path so that the RCD appears to software to be directly connected to an RCH Downstream Port and not in a CXL VH.

#### <span id="page-825-1"></span>9.12.4.1 Boot time Reconfiguration of CXL RP or DSP to Enable an eRCD

1. At reset, the Downstream Port registers are visible in the PCIe configuration space with a Type 1 header. During enumeration, System Firmware shall identify all the Downstream Ports that are connected to the eRCD by reading the DVSEC ID 7 register instead of the Link status registers.

- If the link training was successful, the DVSEC Flex Bus Port Status register in the CXL DVSEC ID 7 structure shall indicate that CXL VH operation with 68B Flit mode was not negotiated, but shall indicate that either the CXL.cache protocol or the CXL.mem protocol was negotiated during link training.
- If the link training was unsuccessful, the DVSEC Flex Bus Port Received Modified TS Data Phase1 Register in the CXL DVSEC ID 7 structure shall indicate that the device is CXL capable but not CXL VH capable. A DSP shall not report link-up status in the PCIe Link Status register when the DSP detects an eRCD on the other end to prevent the CXL-unaware software from discovering the eRCD.
- 2. System Firmware identifies MMIO and bus resource needs for all RCDs below a CXL root port. System Firmware adds MMIO resources needed for the RCH Downstream Port RCRB and RCD Upstream Port RCRB (8-KB MMIO per link) and CXL Component registers (128-KB MMIO per link).
- 3. System Firmware assigns MMIO and bus resources and programs the Alternate MMIO Base/Limit and Alternate Bus Base/Limit registers in all the Root Ports and the Switch Ports in the path and the eRCD BARs except the Downstream Ports that are directly connected to eRCDs. These Alternate decoders are described in [Section 8.1.5](#page-516-4).
- 4. System Firmware sets the Alt BME and Alt Memory and ID Space Enable bits in all the Root Ports and the Switch Ports in the path of every eRCD.
- 5. For each Downstream Port that is connected to an eRCD, System Firmware programs the CXL RCRB Base Address. System Firmware then writes 1 to the CXL RCRB Enable bit, which transitions the port addressing to RCH addressing. The Downstream Port registers now appear in MMIO space at CXL RCRB Base and not in configuration space. System Firmware issues a read to the address CXL RCRB Base + 4 KB. The RCD Upstream Port captures its RCRB Base as described in [Section 8.1.5](#page-516-4). System Firmware configures Upstream Port and Downstream Port registers, as necessary. If this is a DSP, the Downstream Port shall ignore any hot reset requests received from the Upstream Port.
- 6. System Firmware configures the eRCD, using the algorithm described in [Section 9.11.6.](#page-816-1)

The System Firmware shall report each RCD under a separate Host Bridge and not as part of the CXL VH.

The Switch shall ensure that there is always a DSP visible at Device 0, Function 0.

These concepts are illustrated by the configuration shown in [Figure 9-10](#page-827-0). In this configuration, eRCD F and D are attached to a CXL Switch. The Switch DSPs are labeled E and C. The Switch USP and the CXL Root Port are labeled B and A, respectively. The left half of [Figure 9-10](#page-827-0) represents the address map and how the normal decoders and the Alt Mem decoders of A, B, C, and E are configured.

If the host accesses an MMIO address belonging to D, the access flows through A, B, and C as follows:

- 1. Host issues a read.
- 2. A Alt Decoder positively decodes the access and sends to B because A's Alt MSE=1.
- 3. B Alt Decoder positively decodes the access because B's Alt MSE=1.
- 4. C normal decoder positively decodes the access and forwards it to D because C MSE=1.
- 5. D positively decodes and responds because D MSE=1.

<span id="page-827-0"></span>**Figure 9-10. eRCD MMIO Address Decode - Example**

<span id="page-827-1"></span>![](_page_827_Figure_3.jpeg)

The left half of [Figure 9-11](#page-828-0) represents the configuration space map for the same configuration as in [Figure 9-10](#page-827-0) and how the bus decoders and the Alt Mem decoders of A, B, C, and E are configured.

If the host accesses configuration space of F, the access flows through A, B, and E as follows:

- 1. Host issues configuration read to F's configuration space
- 2. A's Alt Decoder positively decodes, forwards to B as Type 1
- 3. B's Alt Decoder positively decodes, forwards down as Type 1
- 4. E's RCRB regular decoder positively decodes, forwards to F as Type 0 because the bus number matches E's RCRB Secondary Bus number
- 5. F positively decodes and responds

If D detects a protocol or link error, the error signal will flow to the system via the following path:

- 1. D issues ERR\_ message with the Requester ID of D.
- 2. C shall not expose DPC capability.
- 3. C forwards ERR\_ message to B.
- 4. B forwards the message to A.
- 5. A forwards the message to RCEC in the Root Complex because the requester's bus number hits Alt Bus Decoder.
- 6. RCEC generates MSI if enabled.

- 7. Root Complex Event Collector Endpoint Association Extended Capability of RCEC describes that it can handle errors from bus range = Alt Bus Decoder in RP.
<span id="page-828-1"></span>- 8. A shall not trigger DPC upon ERR\_ message. Because the requester's bus number hits Alt Bus Decoder, it is treated differently than a normal ERR\_ message.

<span id="page-828-0"></span>**Figure 9-11. eRCD Configuration Space Decode - Example**

![](_page_828_Figure_5.jpeg)

### <span id="page-829-0"></span>9.12.5 CXL eRCD below a CXL RP and DSP - Example

[Figure 9-12](#page-829-1) represents the physical connectivity of a host with four Root Ports, one Switch, and 5 devices. The corresponding software view is shown in [Figure 9-13](#page-830-1). Note that the numbers (e.g., the "1" in PCIe Device 1) in this diagram do not represent the device number or the function number.

<span id="page-829-1"></span>**Figure 9-12. Physical Topology - Example**

![](_page_829_Figure_5.jpeg)

As shown in [Figure 9-12,](#page-829-1) the Switch makes eRCD 1, below its DSP (DSP 1), appear as an RCiEP under an RCH. eRCD 1 is exposed as a separate Host Bridge to the Operating System. The device hosts a CXL DVSEC ID 0 instance in Device 0, Function 0 Configuration Space. The RCH Downstream Port registers and the RCD Upstream Port registers appear in MMIO space as expected.

When a CXL Root Port detects a PCIe device (PCIe Device 1), the Root Port trains up in PCIe mode. The Root Port configuration space (Type 1) may include the CXL DVSEC ID 3 and the CXL DVSEC ID 7. If present, the DVSEC ID 7 instance will indicate that the link trained up in PCIe mode. Other CXL DVSEC ID structures may be present as well.

If a CXL Root Port (RP 2) is connected to an empty slot, its configuration space (Type 1) hosts the CXL DVSEC ID 3 and the CXL DVSEC ID 7, but the DVSEC ID 7 shall indicate no CXL connectivity and the PCIe Link status register shall indicate that there is no PCIe connectivity. Other CXL DVSEC ID structures may be present as well. The user can hot-add a CXL device other than eRCD, a CXL Switch, or a PCIe device in this slot.

A CXL Root Port (RP 3) connected to a CXL Switch spawns a CXL VH. The Root Port as well as the Upstream Switch Port configuration space (Type 1) each host an instance of CXL DVSEC ID 3 and an instance of CXL DVSEC ID 7, but the DVSEC ID 7 instance will indicate that these Ports are operating in CXL VH operation with 68B Flit mode. Other CXL DVSEC ID structures may be present as well.

If a CXL Downstream Switch Port (DSP 2) is connected to a CXL device that is not an eRCD, DSP 2's configuration space (Type 1) hosts an instance of CXL DVSEC ID 3 and an instance of CXL DVSEC ID 7, but the DVSEC ID 7 instance will indicate that this Port is connected to a CXL device and is part of a CXL VH. Other CXL DVSEC ID structures may be present as well.

In this example, CXL Downstream Switch Port (DSP 3) is connected to a PCIe device and its configuration space (Type 1) does not host an instance of CXL DVSEC ID 7. Absence of a CXL DVSEC ID 7 indicates that this Port is not operating in the CXL mode. Note that it is legal for DSP 3 to host a DVSEC ID 7 instance as long as the DVSEC Flex Bus Port Status Register in the DVSEC ID 7 structure reports that the link is not operating in CXL mode.

If a CXL Root Port (RP 4) is connected to an eRCD, the Root Port operates as an RCH Downstream Port. eRCD 2 appears as an RCiEP under its own Host Bridge. This device hosts an instance of the CXL DVSEC ID 0 in Device 0, Function 0 Configuration Space. The RCH Downstream Port registers and the RCD Upstream Port registers appear in MMIO space as expected.

If the Switch is Hot-Pluggable, System Firmware may instantiate a \_DEP object in the ACPI namespace to indicate that Device 1 is dependent on the CXL USP. A legacy PCIe bus driver interprets that to mean that the Switch hot removal has a dependency on eRCD 1, even though the ACPI/PCIe hierarchy does not show such a dependency.

<span id="page-830-1"></span>**Figure 9-13. Software View**

![](_page_830_Figure_6.jpeg)

### <span id="page-830-0"></span>9.12.6 Mapping of Link and Protocol Registers in CXL VH

In the presence of an eRCD, the link and protocol registers appear in MMIO space (RCRB and Component registers in the Downstream Port and the Upstream Port). See [Figure 9-7](#page-821-0) and [Figure 9-8.](#page-822-1)

Because a CXL Virtual Hierarchy appears as a true PCIe hierarchy, the Component Register block is mapped using a standard BAR of CXL components.

Each CXL Host Bridge that is not an RCH includes CHBCR, which includes the registers that are common to all Root Ports under that Host Bridge. In an ACPI-compliant system, the base address of this register block is discovered via ACPI CEDT or the \_CBR method. The CHBCR includes the HDM Decoder registers.

Each CXL Root Port carries a single BAR that maps the associated Component Register block. The offset within that BAR is discovered via the CXL DVSEC ID 8. See [Section 8.1.9](#page-524-4). The layout of the Component Register Block is shown in [Section 8.2.3.](#page-540-3)

Each CXL device that is not an RCD can map its Component Register Block to any of its 6 BARs and a 64-KB-aligned offset within that BAR. The BAR number and the offset are discovered via CXL DVSEC ID 8. A Type 3 device Component Register Block includes HDM Decoder registers.

Each CXL USP carries a single BAR that maps the associated Component Register block. The offset within that BAR is discovered via CXL DVSEC ID 8. The Upstream Switch Port Component Register Block contains the registers that are not associated with a particular Downstream Port, such as HDM Decoder registers.

<span id="page-831-2"></span>Each CXL DSP carries a single BAR that points to the associated CHBCR, the format of which closely mirrors that of a Root Port. The offset within that BAR is discovered via CXL DVSEC ID 8.

<span id="page-831-0"></span>**Figure 9-14. CXL Link/Protocol Register Mapping in a CXL VH**

![](_page_831_Figure_7.jpeg)

<span id="page-831-3"></span><span id="page-831-1"></span>**Figure 9-15. CXL Link/Protocol Registers in a CXL Switch**

![](_page_831_Figure_9.jpeg)

## <span id="page-832-0"></span>9.13 Software View of HDM

HDM is exposed to the OS/VMM as normal memory. However, HDM likely has different performance/latency attributes compared to host-attached memory. Therefore, a system with CXL.mem devices can be considered as a heterogeneous memory system.

ACPI HMAT was introduced for such systems and can report memory latency and bandwidth characteristics associated with different memory ranges. ACPI Specification version 6.2 and later carry the definition of revision 1 of HMAT. As of August 2018, ACPI WG has decided to deprecate revision 1 of HMAT because it had a number of shortcomings. As a result, the subsequent discussion refers to revision 2 of HMAT. In addition, ACPI has introduced a new type of Affinity structure called Generic Affinity (GI) Structure. GI structure is useful for describing execution engines such as accelerators that are not processors. CXL.mem-capable accelerators will result in two SRAT entries - One GI entry to represent the accelerator cores and one memory entry to represent the attached HDM. GI entry is especially useful when describing the CXL.cache accelerator. Previous to the introduction of GI, the CXL.cache accelerator could not be described as a separate entity in SRAT/HMAT and had to be combined with the attached CPU. With this specification change, the CXL.cache accelerator can be described as a separate proximity domain. \_PXM method can be used to identify the proximity domain associated with the PCIe device. Since Legacy OSs do not understand GI, System Firmware is required to return the processor domain that is most closely associated with the I/O device when running such an OS. ASL code can use bit 17 of Platform-Wide \_OSC Capabilities DWORD 2 to detect whether the OS supports GI.

System Firmware must construct and report SRAT and HMAT to the OS in systems with CXL.cache devices and CXL.mem devices. Since System Firmware is not aware of HDM properties, that information must come from the CXL device in the form of CDAT. A device may export CDAT via Table Access DOE or via a UEFI driver.

System Firmware combines the information that it has about the host and CXL connectivity with CDAT content obtained from various CXL components during construction of SRAT and HMAT.

### <span id="page-832-1"></span>9.13.1 Memory Interleaving

Memory interleaving allows consecutive memory addresses to be mapped to different CXL devices at a uniform interval. eRCDs may support a limited form of interleaving as described in [Section 9.11.7.1,](#page-818-1) whereby memory is interleaved across the two links between a CPU and a dual-headed device.

The CXL 2.0 specification introduced a mechanism for interleaving across different devices. The set of devices that are interleaved together is known as the Interleave Set.

An Interleave Set is identified by the following:

- Base HPA Multiple of 256 MB
- Size Also a Multiple of 256 MB
- Interleave Way
- Interleave Granularity
- Targets (applicable only to Root Ports and Upstream Switch Ports)

These terms are described below.

**Interleave Way**: A CXL Interleave Set may contain either 1, 2, 3, 4, 6, 8, 12, or 16 CXL devices. 1-way Interleave is equivalent to no interleaving. The number of devices in an Interleave set is known as Interleave Ways (IW).

**Interleave Granularity**: Each device in an Interleave Set decodes a specific number of consecutive bytes, called Chunk, in HPA Space. The size of Chunk is known as Interleave Granularity (IG). The starting address of each Chunk is a multiple of IG.

- CXL Host Bridges (except RCH) and CXL switches must support the following IG values:
  - 256 Bytes (Interleaving on HPA[8])
  - 512 Bytes (Interleaving on HPA[9])
  - 1024 Bytes (Interleaving on HPA[10])
  - 2048 Bytes (Interleaving on HPA[11])
  - 4096 Bytes (Interleaving on HPA[12])
  - 8192 Bytes (Interleaving on HPA[13])
  - 16384 Bytes (Interleaving on HPA[14])
- CXL memory devices must support at least one of the two IG groups as reported via the CXL HDM Decoder Capability register (see [Section 8.2.4.20.1](#page-565-0)):
  - Group 1: Interleaving on HPA[8], HPA[9], HPA[10], and HPA[11]
  - Group 2: Interleaving on HPA[12], HPA[13], and HPA[14]

**Target**: The HDM Decoders in the CXL Host Bridge are responsible for looking up the incoming HPA in a CXL.mem transaction and forwarding the HPA to the appropriate Root Port Target. The HDM Decoders in the CXL Upstream Switch Port are responsible for looking up the incoming HPA in a CXL.mem transaction and forwarding the HPA to the appropriate Downstream Switch Port Target.

An HDM Decoder in a device is responsible for converting HPA into DPA by stripping off specific address bits. These flows are described in [Section 8.2.4.20.13](#page-573-1).

An Interleave Set is established by programing an HDM Decoder and committing it (see [Section 8.2.4.20.12\)](#page-572-1). The number of decoders implemented by a component are enumerated via the CXL HDM Decoder Capability register (see [Section 8.2.4.20.1\)](#page-565-0). HDM Decoders within a component must be configured in a congruent manner and the Decoder Commit flow performs certain self-consistency checks to assist with correct programming.

Software is responsible for ensuring that HDM Decoders located inside the components along the path of a transaction must be configured in a consistent manner.

[Figure 9-16](#page-834-0) illustrates a simple memory fan-out topology with 4 memory devices behind a CXL Switch. A single HDM Decoder in each Device as well as the Upstream Switch Port is configured to decode the HPA range 16 to 20 TB, at 1-KB granularity. The leftmost Device receives 1-KB ranges starting with HPAs 16 TB, 16 TB + 4 KB, 16 TB+8KB, …, 20 TB - 4 KB (every 4th Chunk). The Root Complex does not participate in the interleaving process.

<span id="page-834-0"></span>**Figure 9-16. One-level Interleaving at Switch - Example**

<span id="page-834-2"></span>![](_page_834_Figure_3.jpeg)

<span id="page-834-3"></span>Multiple-level interleaving is supported as long as all the levels use different, but consecutive, HPA bits to select the target and no Interleave Set has more than 8 devices. This is illustrated in [Figure 9-17](#page-834-1) and [Figure 9-18.](#page-835-0)

<span id="page-834-1"></span>**Figure 9-17. Two-level Interleaving**

![](_page_834_Figure_6.jpeg)

[Figure 9-17](#page-834-1) illustrates a two-level Interleave scheme where the Host Bridge as well as the switch participates in the interleaving process. This topology has 4 memory devices behind each CXL Switch. One HDM Decoder in each of the 8 devices, both Upstream Switch Ports and the Host Bridge are configured to decode the HPA range 16 to 20 TB. The Host Bridge partitions the address range in two halves at 4-KB granularity (based on HPA[12]), with each half directed to a Root Port. Each Upstream Switch Port further splits each half into 4 subranges at 1-KB granularity (based on HPA[11:10]). To each device, it appears as though the HPA range 16-20 TB is 8-way interleaved at 1-KB granularity based on HPA[12:10]. The leftmost Device receives 1-KB ranges starting with HPAs 16 TB, 16 TB+8KB, 16 TB+16KB, …, 20 TB-8KB.

[Figure 9-18](#page-835-0) illustrates a three-level Interleave scheme where the cross-host Bridge logic, the Host Bridge, and the switch participate in the interleaving process. The crosshost Bridge logic is configured to interleave the address range in two halves, using host proprietary registers at 4-KB granularity. One HDM Decoder in 8 devices, 4 Upstream Switch Ports, and 2 Host Bridges are configured to decode the HPA range 16 to 20 TB. The Host Bridge further subdivides the address range in two at 2-KB granularity (using HPA[11]). The Upstream Switch Port in every switch further splits HPA space into 2 subranges at 1-KB granularity (using HPA[10]). To each device, it appears as though the HPA range 16-20 TB is 8-way interleaved at 1-KB granularity based on HPA[12:10]. Similar to [Figure 9-17](#page-834-1), the leftmost Device receives 1-KB ranges starting with HPAs 16 TB, 16 TB+8KB, 16 TB+16KB, …, 20 TB-8KB.

<span id="page-835-0"></span>**Figure 9-18. Three-level Interleaving Example**

<span id="page-835-1"></span>![](_page_835_Figure_5.jpeg)

#### <span id="page-836-0"></span>9.13.1.1 Legal Interleaving Configurations: 12-way, 6-way, and 3-way

This section describes the legal 12-way, 6-way, and 3-way interleaving configurations. The term IGB represents the interleave granularity in number of bytes. The cross-host Bridge Interleaving logic selects the target Host Bridge according to the configurations specified in [Table 9-6,](#page-836-2) [Table 9-7](#page-836-3), and [Table 9-8](#page-836-4), respectively. The Root Complex and the switch select the target port as described in [Section 9.18.1](#page-863-1).

<span id="page-836-2"></span>**Table 9-6. 12-Way Device-level Interleave at IGB**

| Cross-host Bridge Logic Interleaving | CXL Root Complex-level<br>Interleaving | CXL Switch-level Interleaving |
|--------------------------------------|----------------------------------------|-------------------------------|
| 12 way at IGB                        | No interleaving                        | No interleaving/Absent        |
| 6 way at 2*IGB                       | 2 way at IGB                           | No interleaving/Absent        |
| 6 way at 2*IGB                       | No interleaving                        | 2 way at IGB                  |
| 3 way at 4*IGB                       | 4 way at IGB                           | No interleaving               |
| 3 way at 4*IGB                       | No interleaving                        | 4 way at IGB                  |
| 3 way at 4*IGB                       | 2 way at IGB                           | 2 way at 2*IGB                |
| 3 way at 4*IGB                       | 2 way at 2*IGB                         | 2 way at IGB                  |

<span id="page-836-3"></span>**Table 9-7. 6-Way Device-level Interleave at IGB**

| Cross-host Bridge Logic Interleaving | CXL Host Bridge-level Interleaving | CXL Switch-level Interleaving |
|--------------------------------------|------------------------------------|-------------------------------|
| 6 way at IGB                         | No interleaving                    | No interleaving/Absent        |
| 3 way at 2*IGB                       | 2 way at IGB                       | No interleaving               |
| 3 way at 2*IGB                       | No interleaving                    | 2 way at IGB                  |

<span id="page-836-4"></span>**Table 9-8. 3-Way Device-level Interleave at IGB**

| Cross-host Bridge Logic Interleaving | CXL Host Bridge-level Interleaving | CXL Switch-level Interleaving |
|--------------------------------------|------------------------------------|-------------------------------|
| 3 way at IGB                         | No interleaving                    | No interleaving/Absent        |

### <span id="page-836-1"></span>9.13.2 CXL Memory Device Label Storage Area

<span id="page-836-5"></span>CXL memory devices that provide volatile memory, such as DRAM, may be exposed with different interleave geometries each time the system is booted. This can happen due to the addition or removal of other devices or changes to the platform's default interleave policies. For volatile memory, these changes to the interleave usually do not impact host software since there's generally no expectation that volatile memory contents are preserved across reboots. However, with persistent memory, the exact preservation of the interleave geometry is critical so that the persistent memory contents are presented to host software the same way each time the system is booted.

Similar to the interleaving configuration, persistent memory devices may be partitioned into *namespaces*, which define volumes of persistent memory. These namespaces must also be reassembled the same way each time the system is booted to prevent data loss.

[Section 8.2.10](#page-631-1) defines mailbox operations for reading and writing the *Label Storage Area* (LSA) on CXL memory devices: Get LSA and Set LSA. In addition, the Identify Memory Device mailbox command exposes the size of the LSA for a given CXL memory device. The LSA allows both interleave and namespace configuration details to be stored persistently on all the devices involved, so that the configuration data "follows

the device" if the device is moved to a different socket or machine. The use of an LSA is analogous to how disk RAID arrays write configuration information to a reserved area of each disk in the array so that the geometry is preserved across configuration changes.

A CXL memory device may contribute to multiple persistent memory interleave sets, limited by interleave resources such as HDM decoders or other platform resources. Each persistent memory Interleave Set may be partitioned into multiple namespaces, limited by resources such as label storage space and supported platform configurations.

The LSA format and the rules for updating and interpreting the LSA are specified in this section. CXL memory devices do not directly interpret the LSA, they just provide the storage area and mailbox commands for accessing it. Software configuring Interleave Sets and namespaces, such as pre-boot firmware or host operating systems shall follow the LSA rules specified here to correctly inter-operate with CXL-compliant memory devices.

#### <span id="page-837-0"></span>9.13.2.1 Overall LSA Layout

The LSA consists of two Label Index Blocks followed by an array of label slots. As shown in [Figure 9-19,](#page-837-1) the Label Index Blocks are always a multiple of 256 bytes in size, and each label slot is exactly 256 bytes in size.

<span id="page-837-1"></span>**Figure 9-19. Overall LSA Layout**

![](_page_837_Figure_8.jpeg)

The LSA size is implementation dependent and software must discover the size using the Identify Memory Device mailbox command. The minimum allowed size is two index blocks, 256-bytes each in length, two label slots (providing space for a minimal one region label and one namespace label), and one free slot to allow for updates. This makes the total minimum LSA size 1280 bytes. It is recommended (but not required) that a device provides for configuration flexibility by implementing an LSA large enough for two region labels per device and one namespace label per 8 GB of persistent memory capacity available on the device.

All updates to the LSA shall follow the update rules laid out in this section, which guarantee that the LSA remains consistent in the face of interruptions such as power loss or software crashes. There are no atomicity requirements on the Set LSA mailbox operation – it simply updates the range of bytes provided by the caller. Atomicity and consistency of the LSA is achieved using checksums and the principle that only free slots (currently unused) are written to – in-use data structures are never written, avoiding the situation where an interrupted update to an in-use data structure makes it

inconsistent. Instead, all updates are made by writing to a free slot and then following the rules laid out in this section to atomically swap the in-use data structure with the newly written copy.

The LSA layout uses *Fletcher64* checksums. [Figure 9-20](#page-838-1) shows a Fletcher64 checksum implementation that produces the correct result for the data structures in this specification when run on a 64-bit system. When performing a checksum on a structure, any multi-byte integer fields shall be in little-endian byte order. If the structure contains its own checksum, as is commonly the case, that field shall contain 0 when this checksum routine is called.

<span id="page-838-1"></span>**Figure 9-20. Fletcher64 Checksum Algorithm in C**

```
/*
 * checksum -- compute a Fletcher64 checksum
 */
uint64_t
checksum(void *addr, size_t len)
{
 uint32_t *p32 = addr;
 uint32_t *p32end = addr + len;
 uint32_t lo32 = 0;
 uint32_t hi32 = 0;
 while (p32 < p32end) {
 lo32 += *p32++;
 hi32 += lo32;
 }
 return (uint64_t)hi32 << 32 | lo32;
}
```

The algorithm for updating the LSA is single-threaded. Software is responsible for protecting a device's LSA so that only a single thread is updating the LSA at any time. This is typically done with a common mutex lock.

#### <span id="page-838-0"></span>9.13.2.2 Label Index Blocks

[Table 9-9](#page-839-1) shows the layout of a Label Index Block.

<span id="page-839-1"></span>**Table 9-9. Label Index Block Layout**

| Field     | Byte Offset | Length<br>in Bytes | Description                                                                                                                                                         |
|-----------|-------------|--------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Sig       | 00h         | 10h                | Signature indicating a Label Index Block. Shall be set to<br>"NAMESPACE_INDEX\0".                                                                                   |
| Flags     | 10h         | 3                  | No flags defined yet, shall be 0.                                                                                                                                   |
| LabelSize | 13h         | 1                  | Shall be 1. This indicates the size of labels in this LSA in multiples of 256<br>bytes (e.g., 1 for 256, 2 for 512, etc.).                                          |
| Seq       | 14h         | 4                  | Sequence number. Only the two least significant bits of this field are used<br>and shown in Figure 9-21. All other bits shall be 0.                                 |
| MyOff     | 18h         | 8                  | Offset of this index block in the LSA. Label Index Block 0 shall have 0 in this<br>field, Label Index Block 1 shall have the size of the index block as its offset. |
| MySize    | 20h         | 8                  | Size of an index block in bytes. Shall be a multiple of 256.                                                                                                        |
| OtherOff  | 28h         | 8                  | Offset of the other index block paired with this one.                                                                                                               |
| LabelOff  | 30h         | 8                  | Offset of the first slot where labels are stored.                                                                                                                   |
| NSlot     | 38h         | 4                  | Total number of label slots.                                                                                                                                        |
| Major     | 3Ch         | 2                  | The major version number of this layout. Shall be 2.                                                                                                                |
| Minor     | 3Eh         | 2                  | The minor version number of this layout. Shall be 1.                                                                                                                |
| Checksum  | 40h         | 8                  | Fletcher64 checksum of all fields in this Label Index Block. This field is<br>assumed to be 0 when the checksum is calculated.                                      |
| Free      | 48h         | Varies             | NSlot bits, padded with 0s to align index block to 256 bytes.                                                                                                       |

When reading Label Index Blocks, software shall consider index blocks to be valid only when their Sig, MyOff, OtherOff, and Checksum fields are correct. In addition, any blocks with Seq cleared to 0 are discarded as invalid. Finally, if more than 1 Label Index Block is found to be valid, the one with the older sequence number (immediately counterclockwise to the other, according to [Figure 9-21](#page-839-0)) is discarded. If all checks pass and the sequence numbers match, the index block at the higher offset shall be considered the valid block. If no valid Label Index Blocks are found, the entire LSA is considered uninitialized.

<span id="page-839-0"></span>**Figure 9-21. Sequence Numbers in Label Index Blocks**

![](_page_839_Figure_6.jpeg)

When updating the Label Index Block, the current valid block, according to the rules above, is never directly written to. Instead, the alternate block is updated with the appropriate fields and a sequence number that is immediately clockwise as shown in [Figure 9-21](#page-839-0)). It is the appearance of a new block that passes all the checks and has a higher sequence number that makes this update atomic in the face of interruption.

Using this method of atomic update, software can allocate and deallocate label slots, even multiple slots, in a single, atomic operation. This is done by setting the Free bits to indicate which slots are free and which are in-use, and then updating the Label Index Block atomically as described above. To ensure that it is always possible to update a label atomically, there must always be at least one free label slot. That way, any used

label slots can be updated by writing the new contents to the free slot and using the Label Index Block update algorithm to mark the new version and in-use and the old version and free in one atomic operation. For this reason, software must report a "label storage area full" error when a caller tries to use the last label slot.

The Free field contains an array of NSlot bits, indicating which label slots are currently free. The Label Index Block is then padded with 0 bits until the total size is a multiple of 256 bytes. This means that up to 1472 label slots are supported by Label Index Blocks that are 256 bytes in length. For 1473 to 3520 label slots, the Label Index Block size must be 512 bytes in length, and so on.

#### <span id="page-840-0"></span>9.13.2.3 Common Label Properties

Three types of labels may occupy the label slots in the LSA: Region Labels, Namespace Labels, and Vendor Specific Labels. The first two are identified by type fields containing UUIDs as specified in the following sections. Vendor Specific Labels contain a type UUID determined by the vendor per IETF RFC 4122. Software shall ignore any labels with unknown types. In this way, the Type field in the labels provides a *major version number*, where software can assume that a UUID that it expects to find indicates a label that it understands, since only backward-compatible changes are allowed to the label layout from the point where that UUID first appears in a published CXL specification.

Region Labels and Namespace Labels contain a 4-byte Flags field, used to indicate the existence of new features. Since those features must be backward compatible, software may ignore unexpected flags encountered in this field (no error generated). Software should always write 0s for Flags bits that were not defined at the time of implementation. In this way, the Flags field provide a *minor version number* for the label.

It is sometimes necessary to update labels atomically across multiple CXL devices. For example, when a Region or Namespace is being defined, the labels are written to every device that contributes to it. Region Labels and Namespace Labels define a flag, UPDATING, that indicates a multi-device update is in-progress. Software shall follow this flow when creating or updates a set of labels across devices:

- 1. Write each label across all devices with the UPDATING flag set.
- 2. Update each label, using the update algorithm described in the previous section, clearing the UPDATING flag.

Any time software encounters a set of labels with any UPDATING flags, it shall execute these rules:

- If there are missing labels (some components with the expected UUID are missing), then the entire set of labels is rolled-back due to the update operation being interrupted before all labels are written. The roll-back means marking each label in the set as free, following the update algorithm described in the previous section.
- If there are no missing labels, then the entire set of labels is rolled-forward, completing the interrupted update operation by removing the UPDATING flag from all labels in the set, following the update algorithm described in the previous section.

When sets of Region Labels or Namespace Labels are found to have missing components, software shall consider them invalid and not attempt to configure the regions or surface the namespaces with these errors. Exactly how these errors are reported and how users recover from them is implementation-specific, but it is recommended that software first report the missing components, providing the opportunity to correct the misconfiguration, before deleting the erroneous regions or namespaces.

#### <span id="page-841-0"></span>9.13.2.4 Region Labels

Region labels describe the geometry of a persistent memory Interleave Set (the term "region" is synonymous with "Interleave Set" in this section). Once software has configured a functional Interleave Set for a set of CXL memory devices, region labels are added to the LSA for each device that contributes capacity to it. [Table 9-10](#page-841-1) shows the layout of a Region Label.

<span id="page-841-1"></span>**Table 9-10. Region Label Layout**

| Field                     | Byte Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
|---------------------------|-------------|--------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Type                      | 00h         | 16                 | Shall contain this UUID: 529d7c61-da07-47c4-a93f-ecdf2c06f444. In the<br>future, if a new, incompatible Region Label is defined, it shall be assigned a<br>new UUID in the CXL specification defining it.                                                                                                                                                                                                                                                                                                                                                                 |
| UUID                      | 10h         | 16                 | UUID of this region per RFC 4122. This field is used to match up labels on<br>separate devices that together describe a region.                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| Flags                     | 20h         | 4                  | Boolean attributes of the region:<br>•<br>0000 0008h = UPDATING<br>The UPDATING flag is used to coordinate Region Label updates across<br>multiple CXL devices, as described in Section 9.13.2.3.<br>All bits below 0000 0008h are reserved and shall be written as 0 and ignored<br>when read.<br>All bits above 0000 0008h are currently unused and shall be written as 0.<br>The intention is to indicate the existence of backward-compatible features<br>added in the future, so any unexpected 1s in this area shall be ignored (i.e.,<br>not treated as an error). |
| NLabel                    | 24h         | 2                  | Total number of devices in this Interleave Set (interleave ways).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| Position                  | 26h         | 2                  | Position of this device in the Interleave Set, starting with the first device in<br>position 0 and counting up from there.                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| DPA                       | 28h         | 8                  | The DPA where the region begins on this device.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| RawSize                   | 30h         | 8                  | The capacity this device contributes to the Interleave Set (bytes).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| HPA                       | 38h         | 8                  | If nonzero, this region needs to be mapped at this HPA. This field is for<br>platforms that need to restore an Interleave Set to the same location in the<br>system memory map each time. A platform that does not support this shall<br>report an error when a nonzero HPA field is encountered.                                                                                                                                                                                                                                                                         |
| Slot                      | 40h         | 4                  | Slot index of this label in the LSA.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| Interleave<br>Granularity | 44h         | 4                  | The number of consecutive bytes that are assigned to this device:<br>•<br>0 = 256 Bytes<br>•<br>1 = 512 Bytes<br>•<br>2 = 1024 Bytes (1 KB)<br>•<br>3 = 2048 Bytes (2 KB)<br>•<br>4 = 4096 Bytes (4 KB)<br>•<br>5 = 8192 Bytes (8 KB)<br>•<br>6 = 16384 Bytes (16 KB)<br>•<br>All other encodings are reserved                                                                                                                                                                                                                                                            |
| Alignment                 | 48h         | 4                  | The desired region alignment in multiples of 256 MB:<br>•<br>0 = No desired alignment<br>•<br>1 = 256-MB desired alignment<br>•<br>2 = 512-MB desired alignment<br>•<br>etc.                                                                                                                                                                                                                                                                                                                                                                                              |
| Reserved                  | 4Ch         | ACh                | Shall be 0.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| Checksum                  | F8h         | 8                  | Fletcher64 checksum of all fields in this Region Label. This field is assumed<br>to be 0 when the checksum is calculated.                                                                                                                                                                                                                                                                                                                                                                                                                                                 |

#### <span id="page-842-0"></span>9.13.2.5 Namespace Labels

Namespace labels describe partitions of persistent memory that are exposed as volumes to software, analogous to NVMe\* namespaces or SCSI logical unit numbers (LUNs). Exactly how an operating system uses these volumes is beyond the scope of this specification – namespaces may be exposed to applications directly, exposed via file systems, or used internally by the operating system. [Table 9-11](#page-842-1) shows the layout of a Namespace Label.

<span id="page-842-1"></span>**Table 9-11. Namespace Label Layout**

| Field                      | Byte Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
|----------------------------|-------------|--------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Type                       | 00h         | 10h                | Shall contain this UUID: 68bb2c0a-5a77-4937-9f85-3caf41a0f93c. In the<br>future, if a new, incompatible Namespace Label is defined, it shall be<br>assigned a new UUID in the CXL specification defining it.                                                                                                                                                                                                                                                                                                                                                                 |
| UUID                       | 10h         | 10h                | UUID of this namespace per IETF RFC 4122. All labels for this namespace<br>shall contain matching UUIDs.                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| Name                       | 20h         | 40h                | "Friendly name" for the namespace, null-terminated UTF-8 characters. This<br>field may be cleared to all 0s if no name is desired.                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| Flags                      | 60h         | 4                  | Boolean attributes of the region:<br>•<br>0000 0008h = UPDATING<br>The UPDATING flag is used to coordinate Namespace Label updates across<br>multiple CXL devices, as described in Section 9.13.2.3.<br>All bits below 0000 0008h are reserved and shall be written as 0 and ignored<br>when read.<br>All bits above 0000 0008h are currently unused and shall be written as 0.<br>The intention is to indicate the existence of backward-compatible features<br>added in the future, so any unexpected 1s in this area shall be ignored (i.e.,<br>not treated as an error). |
| NRange                     | 64h         | 2                  | Number of discontiguous ranges that this device contributes to namespace,<br>used when the capacity contributed by this device is not contiguous. Each<br>contiguous range will be described by a label and NRange described how<br>many labels were required.                                                                                                                                                                                                                                                                                                               |
| Position                   | 66h         | 2                  | Position of this device in the range set, starting with zero for the first label<br>and counting up from there.                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| DPA                        | 68h         | 8                  | The DPA where the namespace begins on this device.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| RawSize                    | 70h         | 8                  | The capacity this range contributes to the namespace (bytes).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| Slot                       | 78h         | 4                  | Slot index of this label in the LSA.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| Alignment                  | 7Ch         | 4                  | The desired region alignment in multiples of 256 MB:<br>•<br>0 = No desired alignment<br>•<br>1 = 256-MB desired alignment<br>•<br>2 = 512-MB desired alignment<br>•<br>etc.                                                                                                                                                                                                                                                                                                                                                                                                 |
| RegionUUID                 | 80h         | 10h                | UUID of the region that contains this namespace. If a valid region does not<br>exist with this UUID, then this namespace is also considered unusable.                                                                                                                                                                                                                                                                                                                                                                                                                        |
| AddressAbstra<br>ctionUUID | 90h         | 10h                | If nonzero, the address abstraction used by this namespace. Software<br>defines the UUIDs used in this field and their meaning in software-specific<br>and beyond the scope of this specification.                                                                                                                                                                                                                                                                                                                                                                           |
| LBASize                    | A0h         | 2                  | If nonzero, logical block size of this namespace.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| Reserved                   | A2h         | 56h                | Shall be 0.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| Checksum                   | F8h         | 8                  | Fletcher64 checksum of all fields in this Namespace Label. This field is<br>assumed to be 0 when the checksum is calculated.                                                                                                                                                                                                                                                                                                                                                                                                                                                 |

#### <span id="page-843-0"></span>9.13.2.6 Vendor-specific Labels

[Table 9-12](#page-843-2) shows the layout of a Vendor-specific Label. Other than the Type field and the Checksum field, the vendor is free to store anything in the remaining 232 (E8h) bytes of the label.

<span id="page-843-2"></span>**Table 9-12. Vendor Specific Label Layout**

| Field    | Byte Offset | Length<br>in Bytes | Description                                                                                                                        |
|----------|-------------|--------------------|------------------------------------------------------------------------------------------------------------------------------------|
| Type     | 00h         | 10h                | Vendor-specific UUID.                                                                                                              |
|          | 10h         | E8h                | Vendor-specific content.                                                                                                           |
| Checksum | F8h         | 8                  | Fletcher64 checksum of all fields in this Vendor-specific Label. This field is<br>assumed to be 0 when the checksum is calculated. |

### <span id="page-843-1"></span>9.13.3 Dynamic Capacity Device (DCD)

<span id="page-843-3"></span>Dynamic Capacity is a feature of a CXL memory device that allows memory capacity to change dynamically without the need for resetting the device. A DCD is a CXL memory device that implements Dynamic Capacity. Unlike a traditional DPA range that a CXL memory device might support, a Dynamic Capacity DPA range is subdivided into 1 to 8 DC Regions, each of which is subdivided by the DCD into a number of fixed-size blocks, referred to as DC blocks. The host software is expected to program the maximum potential capacity utilizing one or more HDM decoders to span the entire DPA range of all configured regions. The DCD controls the allocation of these DC blocks to the host and utilizes events to signal the host when changes to the allocation of these DC blocks occurs. The DCD communicates the state of these DC blocks through an Extent List that describes the starting DPA and length of all DC blocks the host can access. The Extent List does not contain extents that are still pending acceptance from the host via the Add Dynamic Capacity Response command (see [Section 8.2.10.9.9.3](#page-752-3)). Similarly, the Extent List does contain extents that are still pending release acceptance from the host via the Release Dynamic Capacity command (see [Section 8.2.10.9.9.4\)](#page-754-1). [Figure 9-22](#page-844-0) illustrates a typical Extent List. [Figure 9-23](#page-844-1) illustrates an Extent List in which the DC blocks are shared by multiple hosts. Adding and releasing capacity utilizes the Extent List to control the host's access to portions of the memory without the need to alter the HDM programming of the total potential Dynamic Capacity.

<span id="page-844-0"></span>**Figure 9-22. Extent List Example (No Sharing)**

![](_page_844_Figure_3.jpeg)

<span id="page-844-1"></span>**Figure 9-23. Shared Extent List Example**

![](_page_844_Figure_5.jpeg)

Dynamic Capacity is organized into 1 to 8 DC Regions as defined by the device. [Figure 9-24](#page-845-0) illustrates this. Each DC Region has a unique maximum potential capacity, supported block size, and memory attributes. While the beginning and end of each region is 256 MB aligned, the start of the first block of data within each region is controlled by the DCD and aligned to the Dynamic Capacity block size configured for that region. Because the Extent List is DPA based, a single list can describe the extents in all regions. When the host fetches the current Extent List using the Get Dynamic Capacity Extent List mailbox command, the returned Extent List contains the deviceassigned starting DPA and length for each extent that is assigned to the host. Regions are used in increasing-DPA order, with Region 0 being used for the lowest DPA of Dynamic Capacity and Region 7 for the highest DPA.

The DCD controls which DPA range it assigns to each region for each host. The DPA ranges exposed by the device to each host are independent of one another.

If the host issues a read to a DPA that is not allocated to the host, the device behavior is specified in [Table 8-27](#page-566-1). If the host issues a write to a DPA that is not allocated to the host, the device shall drop the write and send an NDR (see [Section 3.3.9\)](#page-158-3) as a response. If the host issues a write to any DPA in a read-only DC Region, the device shall drop the write and send an NDR (see [Section 3.3.9](#page-158-3)) as a response.

<span id="page-845-0"></span>**Figure 9-24. DCD DPA Space Example**

<span id="page-845-1"></span>![](_page_845_Figure_6.jpeg)

The attributes associated with each region are described in the device's CDAT. The device associates each supported region with a specific DSMAS instance so the host can determine the memory attributes associated with each given region. A device that supports Dynamic Capacity shall report its configured regions in one or more CDAT DSMAS structures and shall set the Dynamic Capacity DSMAS Flag in each structure to indicate a Dynamic Capacity supported range. When reporting the region configuration, the DCD shall supply the DSMAD Handle with which each region is associated.

Devices that instantiate multiple LDs, including MLDs and Multi-Headed devices, share certain region configuration parameters, as defined in [Table 7-67](#page-380-2), across all LDs in that device.

The basic sequence to utilize Dynamic Capacity include:

• Utilize Get Supported Logs sub-list (see [Section 8.2.10.5.6](#page-690-4)) or Get Supported Logs (see [Section 8.2.10.5.1\)](#page-674-5) and Get Log (see [Section 8.2.10.5.2](#page-675-3)) to retrieve the Command Effects Log (CEL). Verify that the necessary Dynamic Capacity commands are returned in the CEL, indicating Dynamic Capacity is supported by the device.

- Issue Get Dynamic Capacity Configuration command: The device reports its number of available regions and each region's base address, length, block size, and DSMAD Handle (see [Section 8.2.10.9.9.1\)](#page-750-5).
- Program the HDM decoders appropriately for each region's base and length from Get Dynamic Capacity Configuration data. The host may utilize one or more HDM decoders to span the current configuration of Dynamic Capacity reported by the device. It is strongly recommended that the host provide adequate decoder size to cover all of the regions that are enabled. If not, the host may not be able to accept some of the Add Dynamic Capacity offers from the DCD.
- Retrieve the initial Extent List with one or more calls to Get Dynamic Capacity Extent List (see [Section 8.2.10.9.9.2\)](#page-751-3). If the list contains extents, then that memory can be utilized immediately.

The basic sequence to add Dynamic Capacity to a host:

- The DCD adds an Add Capacity Event Record (see [Section 8.2.10.2.1.6](#page-653-2)) to the device's Dynamic Capacity Event Log containing the extent of the capacity being added, sets the Dynamic Capacity Event Log bit in the Event Status register and, if enabled, generates an interrupt to alert the host to the new event record. The DCD does this for each extent in the Add Capacity operation being performed, using the More flag as necessary (see [Table 8-62\)](#page-653-1), avoiding overflow, and allowing the host to consume the events as necessary to complete the operation. If the Dynamic Capacity Event Log overflows at any point, the host shall utilize Get Dynamic Capacity Extent List to retrieve the current list of host accessible DC blocks.
- When the host software retrieves the Add Capacity event record containing the extent of the capacity to be added, it responds back to the device with the updated extent for the exact capacity it added with a single call to Add Dynamic Capacity Response (see [Section 8.2.10.9.9.3](#page-752-3)). This allows the host to control exactly how much of the added capacity it wishes to utilize, which may be less than the amount of capacity sent in the add capacity event, or even 0.
- If supported by the device, the host may utilize Get Poison List or Scan Media with the Starting DPA and Length of the added capacity extent to check for poisoned addresses.

The basic sequence to release Dynamic Capacity from a host:

- The DCD adds a Release Capacity Event Record to the device's Dynamic Capacity Event Log (see [Section 8.2.10.2.1.6](#page-653-2)) containing the extent of the capacity it is requesting to be released, sets the Dynamic Capacity Event Log bit in the Event Status register and, if enabled, generates an interrupt to alert the host to the new event record. The DCD does this for each extent in the Release Capacity operation being performed, using the More flag as necessary (see [Table 8-62](#page-653-1)), avoiding overflow, and allowing the host to consume the events as necessary to complete the operation. If the Dynamic Capacity Event Log overflows at any point, the host shall utilize Get Dynamic Capacity Extent List to retrieve the current list of host accessible DC blocks.
- When the host software retrieves the Release Capacity event record containing the extent of the capacity to be released, the host software releases some or all of the capacity from use and responds back to the device with the updated Extent List for the exact capacity it released using the Release Dynamic Capacity command (see [Section 8.2.10.9.9.4\)](#page-754-1). If desired, the host may choose to make unavailable the contents of the capacity being released by whatever means it chooses, including but not limited to issuing the Sanitize or Secure Erase commands, if supported by the device, before the Release Dynamic Capacity command. The host may call Release Dynamic Capacity multiple times, returning different portions of the total capacity over time, in response to the Release Capacity event record. This allows the host to control exactly how much of the released capacity it wishes to release and when it is released.

Prior to issuing Release Dynamic Capacity command, the host software is required to off-line the capacity and complete the necessary coherence management actions.

The basic sequence to release Dynamic Capacity asynchronously from a host (not associated with an event from the device):

• The host may release Dynamic Capacity back to the device, at any time, without receiving a Release Capacity Event Record by calling Release Dynamic Capacity (see [Section 8.2.10.9.9.4](#page-754-1)) with an Extent List containing specific released capacity.

Devices may forcefully release Dynamic Capacity from a host:

• Host access to the released capacity may be immediately disabled and the DCD behaves as if the capacity is no longer allocated to the host. The DCD adds a Forced Capacity Release Event Record to the device's Dynamic Capacity Event Log containing the extent of the capacity being released, sets the Dynamic Capacity Event Log bit in the Event Status Register and, if enabled, generates an interrupt to alert the host to the new event record. If the Dynamic Capacity Event Log overflows at any point, the forced removal still occurs and the host shall utilize Get Dynamic Capacity Extent List to retrieve a new list of host accessible DC blocks.

LD-FAM based DCD shall forcefully release any shared Dynamic Capacity associated with an LD upon a Conventional Reset or a CXL Reset of that LD. MH-SLD or MH-MLD based DCD shall forcefully release shared Dynamic Capacity associated with all associated hosts upon a Conventional Reset of a head. LD-FAM based DCD shall forcefully release shared Dynamic Capacity associated with all associated hosts upon a Conventional Reset of the entire DCD. No Forced Capacity Release Event Record is created when capacity is released as a result of a reset and all entries in the Dynamic Capacity Event Log shall be cleared by the DCD.

The host retrieves the Release Capacity event record containing the extent of the capacity that has been released. The host may respond back to the device with the updated Extent List for the released capacity using the Release Dynamic Capacity command. The host may call Release Dynamic Capacity multiple times, returning different portions of the total capacity over time. Host responses to this event are optional and shall not influence the device's release of the capacity.

#### <span id="page-847-0"></span>9.13.3.1 DCD Management By FM

LD-FAM DCDs implement multiple LDs to support multiple host interfaces and can dynamically assign and reassign memory capacity among those LDs. All G-FAM Devices (GFDs) are DCDs since GFDs exclusively use Dynamic Capacity mechanisms for their capacity management.

The FM is responsible for discovering a DCD's capabilities and for configuring memory assignment.

- 1. The FM issues Get DCD Info (see [Section 7.6.7.6.1\)](#page-377-2) to discover the number of supported hosts, supported features, and dynamic memory capacity. The current assignment of capacity to a specific host is queried with Get Host DC Region Configuration and Get DC Region Extent Lists (see [Section 7.6.7.6.2](#page-378-1) and [Section 7.6.7.6.4](#page-380-1), respectively). See [Section 8.2.10.9.10](#page-755-2) for the equivalent GFD commands.
- 2. Resources are assigned to each host using Initiate Dynamic Capacity Add and Initiate Dynamic Capacity Release (see [Section 7.6.7.6.5](#page-381-3) and [Section 7.6.7.6.6](#page-383-2), respectively). The device generates a Dynamic Capacity Event Record (see [Section 8.2.10.9.9.4\)](#page-754-1) to notify the FM of any host responses. See [Section 7.7.2](#page-393-3) and [Section 7.7.14](#page-482-4) for the equivalent GFD commands and policies.

#### <span id="page-848-0"></span>9.13.3.2 Setting up Memory Sharing

The FM may use the following sequence to set up sharing between hosts, where all hosts are able to read and write to the shared capacity:

<span id="page-848-4"></span><span id="page-848-3"></span><span id="page-848-7"></span>- 1. Issue Initiate Dynamic Capacity Add Request with the Selection Policy set to Free or Contiguous or Prescriptive with the Host ID associated with the first host. The region number must correspond to a region that is advertised as sharable.
<span id="page-848-5"></span>- 2. If the above request is successful as indicated by a new Add Capacity Response event in the Dynamic Capacity Event record, issue Initiate Dynamic Capacity Add Request with Selection Policy=Enable Shared access with the Host ID associated with the second host. The Tag field must match the Tag value used in step [1](#page-848-4).
- 3. Repeat step [2](#page-848-5) for any other hosts that need to share this memory range.

The FM may use the following example sequence to allocate a set of tagged capacity and allow it to be initialized by a host and then shared with one or more hosts as readonly.

- 1. Issue Initiate Dynamic Capacity Add Request with the Selection Policy set to Free or Contiguous or Prescriptive with the Host ID associated with the first host. The region number must correspond to a region that is advertised as writable and sharable.
- 2. If the above request is successful, the tagged shared capacity can be initialized by the first host.
- 3. Issue a Dynamic Capacity Add Reference Request for the tag associated with the capacity. Holding this Reference prevents the tagged capacity from being freed and sanitized in step [4](#page-848-6).
<span id="page-848-6"></span>- 4. After the first host has initialized the tagged shared capacity, issue an Initiate Dynamic Capacity Release Request for the tag associated with the capacity, and then await completion.
<span id="page-848-8"></span>- 5. If the request in step [4](#page-848-6) is successful as indicated by a new Release Capacity Response event in the Dynamic Capacity Event record, the capacity associated with the Tag is preserved but not mapped to any hosts.
- 6. Issue an Initiate Dynamic Capacity Add Request with Selection Policy=Enable Shared Access with the Host ID associated with the second host, specifying a Region that is Sharable and read-only. The Tag field must match the Tag value used in step [1](#page-848-7).
- 7. Repeat step [5](#page-848-8) for any other hosts that need to share the tagged capacity.
- 8. Issue a Dynamic Capacity Remove Reference Request to remove the FM reference to the tagged capacity.
- 9. To withdraw the shared capacity, issue a Initiate Dynamic Capacity Release command for each host.
<span id="page-848-2"></span>- 10. When the tagged capacity has been released from all hosts, if the FM does not hold a reference, the tagged capacity will be sanitized (if appropriate) and freed, at which point the tag no longer exists and the capacity is available for future use.

#### <span id="page-848-1"></span>9.13.3.3 Extent List Tracking

The storage of extent list information, including individual extents and their associated tags, consumes resources in a DCD. As such, DCDs are permitted to limit the number of extents and number of tags of which they are capable of tracking. This capability is reported in a DCD's **Get Host DC Region Configuration** and **Get Dynamic Capacity Configuration** responses.

A DCD is responsible for tracking all extents and tags that comprise extent lists in the following states:

- **Pending**: Defining capacity specified in an **Initiate Dynamic Capacity Add** request that has not been responded to by a host. This includes extents that form part of **Dead Extent Groups**, those that have been Force Removed whilst in pending state.
- **Added**: Defining capacity that has been accepted by a host as part of an **Add Dynamic Capacity** request and is present in the extent list returned to the host in the response to a **Get Dynamic Capacity Extent List** request
- **FM-referenced**: Defining capacity to which an FM reference has been added, as reported by the **FM Holds Reference** bit in the response to **Dynamic Capacity List Tags**

A DCD reports its **Number of Available Extents** and **Number of Available Tags** as its total capacity minus all extents and tags tracked for capacity in the Pending, Added, and FM-referenced states, respectively.

### <span id="page-849-0"></span>9.13.4 Capacity or Performance Degradation

A CXL device may detect an unrecoverable error during its initialization and may be able to operate with a reduced capacity or reduced performance. If this failure results in capacity degradation and it is detected prior to Memory\_Info\_Valid=1, the device shall update the Memory\_Size fields in the corresponding DVSEC CXL Range Size registers (see [Section 8.1.3.8.1](#page-507-1), [Section 8.1.3.8.2,](#page-507-2) [Section 8.1.3.8.5](#page-510-1), and [Section 8.1.3.8.6](#page-510-2)), CDAT DSMAS structures, response to Identify Memory Device command, and response to Get Partition Info command to report the reduced size. It is recommended that the device also set the Memory Capacity Degraded flag in the Health Status field (see [Table 8-148\)](#page-726-1).

If the failure results in performance degradation and it is detected prior to Memory\_Info\_Valid=1, the CDAT DSLBIS structure shall be updated and the Performance Degraded flag in the Health Status field (see [Table 8-148](#page-726-1)) should be set. If Mem\_HwInit\_Mode=1, Memory\_Active bit(s) shall be set when the memory range is fully initialized and available for software use.

If this failure is detected after the Memory\_Info\_Valid bit is set, but before the Memory\_Active bit is set, the device shall not set the Memory\_Active bit. The device updates the CDAT in the following manner:

- CDAT sequence number shall be incremented to indicate to SW that CDAT content has changed.
- If the failure results in capacity degradation, the CDAT DSEMTS entries shall mark the bad memory as "EFIUnusableMemory" indicating to the SW that it shall not use the associated DPA range on this device. The Memory Capacity Degraded flag in the Health Status field (see [Table 8-148\)](#page-726-1) shall be set.
- If the failure results in performance degradation, the CDAT DSLBIS structure shall be updated and the Performance Degraded flag in the Health Status field (see [Table 8-148](#page-726-1)) shall be set.

If Mem\_HwInit\_Mode=1, Memory\_Active\_Degraded shall be set when the reduced capacity is fully initialized and available for software use.

The device capacity reported by Identify Memory Device (see [Section 8.2.10.9.1.1](#page-721-2)) and Get Partition Info (see [Section 8.2.10.9.2.1\)](#page-722-1) commands shall be consistent with capacity advertised by CDAT that is not marked as EFIUnusableMemory.

## <span id="page-849-1"></span>9.14 Back-Invalidate Configuration

<span id="page-849-2"></span>This section describes how System Software may discover whether a component supports Back-Invalidate and how BI-IDs are assigned.

### <span id="page-850-0"></span>9.14.1 Discovery

Back-Invalidate (BI) messages require the link to operate in 256B Flit mode. Alternate Protocol Negotiation flow establishes the optimal Flit mode and PCIe DVSEC for Flex Bus Port registers (see [Section 8.2.1.3](#page-535-2)) identifies the negotiated Flit mode. The presence of the CXL BI Decoder Capability Structure indicates that the component is capable of supporting BI.

### <span id="page-850-1"></span>9.14.2 Configuration

<span id="page-850-4"></span>Before enabling a device to issue BI requests, System Software must ensure that the device, the host, and any switch(es) in the path are capable of BI and that the link(s) between the device and the host are operating in 256B Flit mode.

BI-capable Downstream Ports and devices advertise the CXL BI Decoder Capability Structure (see [Section 8.2.4.27](#page-590-1)). System Software configures them to enable BI functionality. The BI-ID of a device must be unique within a VH. This is ensured by using the device's Bus Number as the BI-ID. The Downstream Port decode functionality is described in [Table 9-13](#page-850-2) and [Table 9-14](#page-850-3).

<span id="page-850-5"></span><span id="page-850-2"></span>**Table 9-13. Downstream Port Handling of BISnp**

| BI Enable<br>Value | BI Forward<br>Value | Behavior                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
|--------------------|---------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0                  | 0                   | Discard                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| 0                  | 1                   | Forward upstream as is                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| 1                  | 0                   | Perform the following checks:<br>•<br>Locate the HDM decoder in the USP or RC that decodes the BISnp<br>address.<br>•<br>Verify that the BI bit in that HDM decoder is set.<br>•<br>Optionally, verify that the Target Port that corresponds to the BISnp<br>address matches the port that generated the BISnp request.<br>If this is a DSP:<br>•<br>If above checks pass, Set BI-ID= Secondary Bus Number and forward<br>upstream; otherwise, discard.<br>If this is a root port:<br>•<br>If above checks pass, forward upstream; otherwise, discard. Root port<br>may use host proprietary mechanisms to initialize BI-ID and route the<br>associated BIRsp messages. |
| 1                  | 1                   | Discard (Invalid setting)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |

<span id="page-850-6"></span><span id="page-850-3"></span>**Table 9-14. Downstream Port Handling of BIRsp**

| BI Enable<br>Value | BI Forward<br>Value | Behavior                                                                                                                                                                                                                                                                            |
|--------------------|---------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0                  | 0                   | Discard                                                                                                                                                                                                                                                                             |
| 0                  | 1                   | Forward downstream as is                                                                                                                                                                                                                                                            |
| 1                  | 0                   | If this is a DSP:<br>•<br>If BI-ID=Secondary Bus Number, forward downstream; otherwise,<br>discard.<br>If this is a root port:<br>•<br>Use host-specific checks to ensure correct routing of the BISnp<br>response. Forward downstream if these checks pass; otherwise,<br>discard. |
| 1                  | 1                   | Discard (Invalid setting)                                                                                                                                                                                                                                                           |

The USP in a BI-capable Switch may advertise the CXL BI Route Table capability Structure (see [Section 8.2.4.26](#page-588-1)). If a USP receives an M2S BIRsp message, the USP shall look up the Port Number associated with the Bus Number that is carried in the message's BI-ID field, and then forward the message to that Port. The BI-ID is guaranteed to correspond to a valid BI-capable device, specifically the one that generated the BISnp request. If the Port Number does not match any DSP due to incorrect programming, the BIRsp message shall be dropped.

If a USP receives an S2M BISnp message, the USP may look up the Port Number associated with the Bus Number that is carried in the message's BI-ID field, and then verify that the Port Number matches the Port Number of the originating DSP before forwarding the BISnp message upstream. If the Port Number derived from this structure does not match the DSP's Port Number, the BISnp message may be dropped.

> **IMPLEMENTATION NOTE**

System software may use the following sequence to configure a BI-capable Device D below a Switch S as follows:

- 1. Verify that all the CXL link(s) between Device D and the host are operating in 256B Flit mode.
- 2. Ensure the device has been assigned a valid Bus number.
- 3. Enable BI on the DSP of Switch S that is directly connected to Device D:
  - a. BI Forward=0.
  - b. BI Enable=1.
- 4. If the DSP's BI Decoder Capability register indicates Explicit BI Decoder Commit Required=1, commit the BI-ID changes via the following sequence:
  - a. BI Decoder Commit=0 to rearm.
  - b. BI Decoder Commit=1.
  - c. Poll bits 0 and 1 of the BI Decoder Status register until timeout or one of them is set. The timeout value is reported in the BI Decoder Status register.
  - d. If BI Decoder Committed=1, the changes were committed. Proceed to step 5.
  - e. If BI Decoder Error Not Committed=1, the changes were not committed. Software should treat this as an error condition.
  - f. If neither bit is set and the timeout is reached, Software should treat this as an error condition.
- 5. If the USP implements CXL BI Route Table Capability Structure and Explicit BI RT Commit Required=1, commit the BI-ID changes as follows:
  - a. BI RT Decoder Commit=0 to rearm.
  - b. BI RT Decoder Commit=1.
  - c. Poll bits 0 and 1 of the BI RT Status register until timeout or one of them is set. The timeout value is reported in the BI RT Status register.
  - d. If BI RT Error Not Committed=1, the changes were not committed. Software should treat this as an error condition.
  - e. If BI RT Committed=1, the changes were committed. Proceed to step 6.
  - f. If neither bit is set and the timeout is reached, Software should treat this as an error condition.
- 6. If the previous steps were successful, configure the Root Port that is directly connected to Switch S to forward BI messages if it isn't already set up that way:
  - a. If BI Forward=0, set BI Forward=1.
  - b. Ensure BI Enable=0.
- 7. If the previous steps were successful, configure Device D to enable BI:
  - a. BI Enable=1.
- 8. If the previous steps were successful, inform the device driver that Device D may now issue BI requests.

> **IMPLEMENTATION NOTE**

System software may use the following sequence to deallocate the BI-ID B that was previously assigned to Device D below Switch S as follows:

- 1. Notify Device D's device driver that Device D is no longer allowed to issue BI requests and then wait for acknowledgment.
- 2. Configure Device D to disable BI:
  - a. BI Enable=0.
- 3. Configure the DSP of Switch S that is directly connected to Device D to unassign BI-ID B as follows:
  - a. BI Forward=0.
  - b. BI Enable=0.
- 4. If the DSP's CXL BI Decoder Capability register indicates Explicit BI Decoder Commit Required=1, commit the BI-ID changes as follows:
  - a. BI Decoder Commit=0 to rearm.
  - b. BI Decoder Commit=1.
  - c. Poll bits 0 and 1 of the BI Decoder Status register until timeout or one of them is set. The timeout value is reported in the BI Decoder Status register.
  - d. If BI Decoder Error Not Committed=1, the changes were not committed. Software should treat this as an error condition.
  - e. If BI Decoder Committed=1, the changes were committed. Proceed to step 5.
  - f. If neither bit is set and the timeout is reached, Software should treat this as an error condition.
- 5. If the USP implements CXL BI Route Table Capability Structure and Explicit BI RT Commit Required=1, commit the BI-ID changes as follows:
  - a. BI RT Commit=0 to rearm.
  - b. BI RT Commit=1.
  - c. Poll bits 0 and 1 of the BI RT Status register until timeout or one of them is set. The timeout value is reported in the BI RT Status register
  - d. If BI RT Error Not Committed=1, the changes were not committed. Software should treat this as an error condition.
  - e. If BI RT Committed=1, the changes were committed. Proceed to step 6.
  - f. If neither bit is set and the timeout is reached, Software should treat this as an error condition.
- 6. If the previous steps were successful, and no other devices in this VCS have been assigned a BI-ID, configure the Root Port that is directly connected to Switch S to stop forwarding BI messages as follows:
  - a. BI Forward=0.

Ensure BI Enable=0.

### <span id="page-853-0"></span>9.14.3 Mixed Configurations

This section describes scenarios where a BI-capable device is plugged into a system that does not support BI.

#### <span id="page-854-0"></span>9.14.3.1 BI-capable Type 2 Device

If a BI-capable Type 2 device is connected to a Downstream Port that does not support 256B Flit mode, the device is able to detect this condition during the Hardware Autonomous Mode Negotiation (see [Section 6.4.1.1](#page-305-6)) and fall back to another mode (e.g., Type 2 HDM-D mode or PCIe mode) based on the device vendor's policy.

If a BI-capable Type 2 device is connected to a switch that supports BI, but the host does not support BI, the device cannot be operated in BI mode. In this case, the System Software or the System Firmware may choose to reconfigure the Type 2 device to operate in a fallback mode.

It is legal for BI-capable Type 2 devices to not support HDM-D flow; however, such a device must support fallback to either operate as a PCIe device, Type 1 device, or a Type 3 device. These flows are described in [Section 9.14.3.2](#page-854-1).

If a Type 2 device advertises support for HDM-D flow via the BI Decoder Capability register (see [Section 8.2.4.27.1](#page-591-0)), the device is operated in that mode as long as the number of Type 2 devices using HDM-D flow does not exceed the host's capabilities and the CXL specification restrictions. A CXL Type 2 device that supports HDM-D flow may be unable to operate in that mode due to system configuration restrictions. In many scenarios, the device may be unable to make that determination on its own and may require assistance from System Software or System Firmware. See [Section 9.14.3.2](#page-854-1).

#### <span id="page-854-1"></span>9.14.3.2 Type 2 Device Fallback Modes

[Table 9-15](#page-854-2) describes the actions that System Software or System Firmware may take when a Type 2 device cannot be operated in either HDM-DB mode or in HDM-D mode, based on the Fallback Capability field value in the DVSEC CXL Capability2 register (see [Section 8.1.3.7](#page-506-3)).

<span id="page-854-2"></span>**Table 9-15. CXL Type 2 Device Behavior in Fallback Operation Mode**

| Register Value1 | Behavior                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
|-----------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 00b             | The device can be operated as an RCD.<br>If the device does not support HDM-DB flow, it supports HDM-D flow.<br>If the device supports HDM-DB flow, it also supports HDM-D flow and must return<br>HDM-D Capable=1 (see Section 8.2.4.27.1).<br>If the device cannot be operated as a Type 2 device, it must be disabled.                                                                                                                                                                      |
| 01b             | The device supports either HDM-DB flow or HDM-D flow or both. In addition, it can<br>operate as a PCIe device.<br>If the device cannot be operated in either HDM-DB mode or in HDM-D mode,<br>System Firmware or System Software may disable Alternate Protocol Negotiation<br>by programming the DSP registers and issuing a Secondary Bus Reset so that the<br>link comes up in PCIe mode.                                                                                                   |
| 10b             | The device supports either HDM-DB flow or HDM-D flow or both. In addition, it can<br>operate as a CXL Type 1 device.<br>If the device cannot be operated in either HDM-DB mode or in HDM-D mode,<br>System Firmware or System Software may reconfigure the DVSEC Flex Bus Port<br>Control register (see Section 8.2.1.3.2) in the Downstream Port above the device<br>to not advertise CXL.mem and then issue a Secondary Bus Reset, thereby bringing<br>up the device as a CXL Type 1 device. |
| 11b             | The device supports either HDM-DB flow or HDM-D flow or both. In addition, it can<br>operate as a CXL Type 3 device.<br>If the device cannot be operated in either HDM-DB mode or in HDM-D mode,<br>System Firmware or System Software may reconfigure the Flex Bus Port Control<br>register (see Section 8.2.1.3.2) in the Downstream Port above the device to not<br>advertise CXL.cache and then issue a Secondary Bus Reset, thereby bringing up the<br>device as a CXL Type 3 device.     |

<sup>1.</sup> Fallback Capability field values in the DVSEC CXL Capability2 register (see [Section 8.1.3.7\)](#page-506-3).

![](_page_855_Picture_1.jpeg)

More-complex policies, such as configuring the Device to operate in CXL.io only mode or another mode based on peer devices, are possible; however, those policies are beyond the scope of this specification.

#### <span id="page-855-0"></span>9.14.3.3 BI-capable Type 3 Device

A BI-capable Type 3 device is required to operate correctly when System Software has not enabled BI. In this case, the device functionality that is dependent on BI will not be available.

If a BI-capable Type 3 device is connected to a Downstream Port that does not support 256B Flit mode, the device may continue to advertise BI capability via the CXL BI Decoder Capability Structure (see [Section 8.2.4.27](#page-590-1)). The System Software shall ensure that the BI bit in none of the HDM decoders in the device, the switch, or the host that spans the device's HDM is set. If a BI-capable Type 3 device is present in a system where the host does not support BI, the System Software shall ensure that the BI bit in none of the HDM decoders in the device, the switch, or the host that spans the device's HDM is set. In both cases, the System Software is responsible for ensuring that the BI bit in the CXL BI Decoder Control register (see [Section 8.2.4.27.2](#page-591-1)) in the device, as well as the Downstream Port it is connected to, is programmed to 0.

## <span id="page-855-1"></span>9.15 Cache ID Configuration and Routing

The CXL 3.0 specification introduces protocol enhancements that allow for more than one active CXL.cache agent per VCS. The identity of the CXL.cache agent is carried via the CacheID field in the CXL.cache messages. If the CXL link is operating in 256B Flit mode, the CXL.cache messages can carry 4 CacheID bits. Before enabling more than one CXL.cache device per VCS, Software must ensure that the host and any switch(es) in the path advertise the CXL Cache ID Decoder Capability Structure, and that all the link(s) between the lowest-level switch and the host are operating in 256B Flit mode.

Downstream Ports advertise the CXL Cache ID Decoder Capability structure to indicate that the Downstream Ports can assign and decode the CacheID field in CXL.cache messages (see [Section 8.2.4.29\)](#page-595-1). Software configures the Downstream Ports to enable CacheID forwarding functionality and assign a CacheID to the device. The CacheID must be unique within a VH and must account for the constraints placed by the Flit mode and the host capabilities.

Any CXL.cache device can operate correctly in a system that is capable of supporting more than one active CXL.cache agent per VCS; however, System Firmware or System Software that is aware of this new capability and capable of correctly configuring the switch and/or host is required to take advantage of this capability.

### <span id="page-855-2"></span>9.15.1 Host Capabilities

The host requires dedicated resources to track each CacheID source. As such, it is necessary to account for host constraints when assigning CacheID. The host constraints are expressed in terms of the total number of CacheIDs that the host can track per CXL Host Bridge. This information is conveyed via the Cache ID Target Count field in the CXL Cache ID Route Table Capability register (see [Section 8.2.4.28.1\)](#page-593-0) associated with the Host Bridge.

### <span id="page-855-3"></span>9.15.2 Downstream Port Decode Functionality

<span id="page-855-4"></span>Downstream Port decode functionality is described in [Table 9-16](#page-856-1) and [Table 9-17](#page-856-2). The associated registers are defined in [Section 8.2.4.14](#page-547-4).

<span id="page-856-1"></span>**Table 9-16. Downstream Port Handling of D2H Request Messages**

| Assign<br>Cache ID<br>Value | Forward<br>Cache ID<br>Value | Behavior                                                                                                                                                                                                                                                   |  |
|-----------------------------|------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--|
| 0                           | 0                            | Discard                                                                                                                                                                                                                                                    |  |
| 0                           | 1                            | Forward upstream. If the message was received over a link operating in<br>68B Flit mode, the request is processed as if CacheID field is 0.                                                                                                                |  |
| 1                           | 0                            | Set CacheID=Local Cache ID and forward upstream.<br>The link between the device and the Downstream Port may be operating in<br>68B Flit mode, in which case the D2H request message received by the<br>Downstream Port does not contain the CacheID field. |  |
| 1                           | 1                            | Discard (Invalid setting)                                                                                                                                                                                                                                  |  |

In addition to the checks documented in [Table 9-16](#page-856-1), the root port shall implement the following steps before forwarding the message upstream:

- If HDM-D Type 2 Device Present=1, compare CacheID with the HDM-D Type 2 Device Cache ID field. If there is a match, identify this device as a Type 2 device that is using HDM-D flows. The host shall follow the HDM-D flows when responding to this device, which includes enforcing the setting in the CXL.cache Trust Level field of the Root Port Security Policy register (see [Table 8-29\)](#page-576-4).
- If the Requester is using HDM-DB flows, abort the request if Block CXL.cache HDM-DB=1.

<span id="page-856-2"></span>**Table 9-17. Downstream Port Handling of H2D Response Message and H2D Request Message**

| Assign<br>Cache ID<br>Value | Forward<br>Cache ID<br>Value | Behavior                                                                                                                                                                                                                                                                                                                             |
|-----------------------------|------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0                           | 0                            | Discard                                                                                                                                                                                                                                                                                                                              |
| 0                           | 1                            | Forward downstream as is                                                                                                                                                                                                                                                                                                             |
| 1                           | 0                            | If CacheID=Local CacheID, forward downstream; otherwise, discard. The<br>link between the device and the Downstream Port may be operating in 68B<br>Flit mode, in which case the H2D message received by the device does not<br>contain the CacheID field.<br>The device shall ignore the CacheID field in H2D messages, if present. |
| 1                           | 1                            | Discard (Invalid setting)                                                                                                                                                                                                                                                                                                            |

D2H response messages and D2H data messages do not carry CacheID and are always routed back to the host.

### <span id="page-856-0"></span>9.15.3 Upstream Switch Port Routing Functionality

<span id="page-856-3"></span>When a USP receives a D2H request message from a DSP, the USP shall forward the message upstream. A USP may look up the Port Number associated with the CacheID field in the message from the CXL Cache ID Route Table and may compare that to the Port Number of the DSP that the message came from before forwarding the message.

When a USP receives an H2D request message, H2D data message or an H2D response message, the USP shall use the message's CacheID field to look up the corresponding CXL Cache ID Target N register (see [Section 8.2.4.28.4\)](#page-594-0). If the Valid bit in the Cache ID Target register is 0, the H2D message shall be discarded without a response. If the Valid bit is 1, the message shall be forwarded to the local DSP based on the Port Number field that is programmed in the CXL Cache ID Target N register.

D2H response messages and D2H data messages do not carry CacheID and are always routed back to the host.

If a USP receives CXL.cache message over a link operating in 68B Flit mode, it shall process the request as if the CacheID field is 0. A switch that is not capable of decoding CacheID field must be configured such that no more than one DSP is enabled for CXL.cache traffic (indicated by Cache\_Enable=1 in the DVSEC Flex Bus Port Status register; see [Section 8.2.1.3.3\)](#page-538-0). The USP shall direct all H2D traffic to that DSP.

### <span id="page-857-0"></span>9.15.4 Host Bridge Routing Functionality

<span id="page-857-1"></span>When the Host Bridge receives the equivalent of an H2D request or an H2D response message from the host, the Host Bridge logic shall use the CacheID field to look up the corresponding CXL Cache ID Target N register (see [Section 8.2.4.28.4](#page-594-0)). If the Valid bit is 0, the H2D message is discarded. If the Valid bit is 1, the message is forwarded to the local root port based on the Port Number field that is programmed in the CXL Cache ID Target N register.

When the Host Bridge receives a D2H request message from the root port, the Host Bridge shall forward the message to the host, using host-specific mechanisms. The Host Bridge may optionally look up the root port that is associated with the CacheID and discard the message if the message was received from a different root port.

> **IMPLEMENTATION NOTE**

System Software may use the following sequence to allocate a Cache ID to a BIcapable CXL.cache Device D below a Switch S and enable the Device to generate CXL.cache transactions that target any memory:

- 1. Verify that the CXL link between Switch S and the host is operating in 256B Flit mode.
- 2. Identify an unused and legal CacheID value, c, and allocate it to Device D. Software must take into account the current Flit mode, as well as the Cache ID Target Count fields, while assigning Cache IDs to devices.
- 3. Configure the DSP of Switch S that is directly connected to Device D to assign Cache ID=c to Device D:
  - a. Forward Cache ID=0.
  - b. Local Cache ID=c.
  - c. Assign Cache ID=1.
- 4. If the above DSP of Switch S reports Explicit Cache ID Decoder Commit Required=1, commit the Cache ID changes as follows:
  - a. Cache ID Decoder Commit=0 to rearm.
  - b. Cache ID Decoder Commit=1.
  - c. Poll bits 0 and 1 of the Cache ID Decoder Status register until timeout or one of them is set. The timeout value is reported in the Cache ID Decoder Status register.
  - d. If Cache ID Decoder Error Not Committed=1, the changes were not committed. Software should treat this as an error condition.
  - e. If Cache ID Decoder Committed=1, the changes were committed. Proceed to Step 5.
  - f. If neither bit is set and the timeout is reached, software should treat this as an error condition.
- 5. Configure the USP of Switch S to route Cache ID c:
  - a. Route Table[c]= Port Number register of the DSP that is connected directly to Device D.
- 6. If the USP reports Explicit Cache ID RT Commit Required=1, commit the Cache ID changes as follows:
  - a. Cache ID RT Commit=0 to rearm.
  - b. Cache ID RT Commit=1.
  - c. Poll bits 0 and 1 of the Cache ID RT Status register until timeout or one of them is set. The timeout value is reported in the Cache ID RT Status register.
  - d. If Cache ID RT Error Not Committed=1, the changes were not committed. Software should treat this as an error condition.
  - e. If Cache ID RT Committed=1, the changes were committed. Proceed to Step 7.
  - f. If neither bit is set and the timeout is reached, software should treat this as an error condition.
- 7. Configure the Root Port, R, that is directly connected to Switch S to decode the CXL.cache messages from Device D:
  - a. If Forward Cache ID=0, set Forward Cache ID=1.
  - b. Ensure Assign Cache ID=0.
- 8. If the previous steps were successful, configure the CXL Cache ID Route Table (see [Section 8.2.4.28.1](#page-593-0)) in the Host Bridge:
  - a. Route Table[c].Port Number=Port Number register of Root Port R.
- 9. If the previous steps were successful, inform the device driver that Device D may now issue CXL.cache requests.

## <span id="page-859-0"></span>9.16 UIO Direct P2P to HDM

CXL.mem devices that can complete UIO requests that target its HDM, advertise the capability via the UIO Capable bit in the CXL HDM Decoder Capability register (see [Section 8.2.4.20.1\)](#page-565-0). CXL switches may allow routing of UIO accesses to HDM in the same VH as the UIO requester and advertise this capability via the same bit. CXL Host Bridges may allow routing of UIO accesses to host memory or HDM below another root ports in the same Host Bridge and advertise this capability via this bit. Prior to setting up a UIO path from a UIO requester to an HDM or to host memory, the Software must consult the capabilities of the target device and any switches or Host Bridges in the path.

[Figure 9-25](#page-859-1) shows a configuration with four CXL.mem devices that form three separate interleave sets and how a UIO requester is able to access the HDM range. UIO accesses to UIO Target 1 and UIO Target 2 are directly routed by the switch, whereas UIO accesses to UIO Target 3 and UIO Target 4 are routed through the host. As shown, UIO Target 1 and UIO Target 2 participate in a 2-way interleave set. The UIO requester can efficiently access this interleave set without going through the host.

<span id="page-859-1"></span>**Figure 9-25. UIO Direct P2P to Interleaved HDM**

![](_page_859_Figure_6.jpeg)

The HDM that is a target of P2P UIO accesses must be part of either a 1-way, 2-way, 4 way, 8-way, or 16-way interleave set. Any HDM that is part of a 3-way, 6-way, or 12 way interleave arrangement cannot be a P2P UIO target. The HDM address must be carved out of a CFMWS entry with Interleave Arithmetic=Standard Modulo arithmetic (see [Table 9-22](#page-865-0)). In addition, P2P UIO traffic may be protected by Selective IDE Streams.

In addition, Software must configure the switch and Host Bridge HDM decoders with additional information regarding any HDM interleaving calculations that are performed upstream to it before setting the UIO bit in that HDM decoder. The UIG, UIW, and ISP fields allow the switch and the Host Bridge to determine whether the UIO target

address belongs to itself or to a peer component. The rules regarding the processing of UIO Direct P2P to HDM requests are described in [Table 9-18](#page-860-2). The ISP field in the target CXL.mem device allow the device to determine how it should respond.

These requirements are in addition to the UIO related requirements that are defined in PCIe Base Specification.

### <span id="page-860-0"></span>9.16.1 Processing of UIO Direct P2P to HDM Messages

This section describes how CXL components handle UIO Direct P2P accesses to HDM.

<span id="page-860-3"></span>UIO To HDM Enable bit is defined in [Section 8.1.5.2](#page-518-1) and allows System Software to control whether a requester below a switch can use UIO to access HDM.

<span id="page-860-2"></span>**Table 9-18. Handling of UIO Accesses**

| Received by                                                                              | UIO Address                                                                             | Behavior                                                                                                                                       |
|------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------|
| CXL.mem device<br>that reports UIO<br>Capable=1 (see<br>Section 8.2.4.20.1)              | Complete match with an HDM<br>decoder with UIO=1                                        | Respond to the UIO request per PCIe Base<br>Specification                                                                                      |
|                                                                                          | Complete match with an HDM<br>decoder with UIO=0                                        | Return Completer Abort, do not commit data if it<br>is a UIO write                                                                             |
|                                                                                          | Partial match with an HDM decoder,<br>irrespective of the UIO bit                       | Return Completer Abort, do not commit data if it<br>is a UIO write                                                                             |
|                                                                                          | Mismatch                                                                                | Handle per PCIe Base Specification                                                                                                             |
| USP ingress of a<br>CXL Switch that<br>reports UIO                                       | Either Partial or Complete match<br>with an HDM decoder, irrespective<br>of the UIO bit | Identify the port number of the target DSP and<br>forward                                                                                      |
| Capable=1 (see<br>Section 8.2.4.20.1)                                                    | Mismatch                                                                                | Handle per PCIe Base Specification                                                                                                             |
| DSP ingress of a<br>CXL Switch that<br>reports UIO                                       | Complete match with an HDM<br>decoder with UIO=11 and UIO To<br>HDM Enable=1            | Identify the port number of the target DSP and<br>forward to that peer port regardless of ACS<br>configuration including egress control vector |
|                                                                                          | Complete match with an HDM<br>decoder with UIO=0 and UIO To<br>HDM Enable=1             | Forward toward the host regardless of ACS<br>configuration including egress control vector                                                     |
| Capable=1 (see<br>Section 8.2.4.20.1)                                                    | Partial match with an HDM decoder<br>and UIO To HDM Enable=1                            | Forward toward the host regardless of ACS<br>configuration including egress control vector                                                     |
|                                                                                          | Complete or Partial match, and UIO<br>To HDM Enable=0                                   | Return Completer Abort                                                                                                                         |
|                                                                                          | Mismatch                                                                                | Handle per PCIe Base Specification                                                                                                             |
| RP ingress of a Host<br>Bridge that reports<br>UIO Capable=1 (see<br>Section 8.2.4.20.1) | Complete match with an HDM<br>decoder with UIO=1                                        | Identify the port number of the target RP and<br>forward to that peer port, subject to host<br>specific access controls                        |
|                                                                                          | Complete match with an HDM<br>decoder with UIO=0                                        | Handle via host-specific mechanisms                                                                                                            |
|                                                                                          | Partial match with an HDM decoder                                                       | Handle via host-specific mechanisms                                                                                                            |
|                                                                                          | Mismatch                                                                                | Handle via host-specific mechanisms                                                                                                            |

<sup>1.</sup> Because the DSP does not take length into account during this check, transactions that cross an interleave boundary get forwarded to the device that owns the starting address. They are aborted by the device because the device checks the length field. If the UIO traffic is encrypted using Stream IDE, some of the address bits may be encrypted and the switch may unknowingly forward these to the wrong device, which will issue a Completer Abort.

#### <span id="page-860-1"></span>9.16.1.1 UIO Address Match (DSP and Root Port)

For a DSP or a root port, UIO address is considered a complete match if there exists an HDM Decoder[n] (see [Section 8.2.4.20](#page-564-1) and [Section 8.2.4.30](#page-596-1)) for which the following conditions are true:

- 1. AT field in the UIO request indicates that it is carrying a translated address.
- 2. UIO.Address[63:2] ≥ Decoder[n].Base[63:2].
- 3. UIO.Address[63:2]+UIO.Length[63:2] ≤ Decoder[n].Base[63:2]+ Decoder[n].Size[63:2].
- 4. Either of these sub-conditions are true:
  - a. Decoder[n].UIW=0
  - b. UIO.Address[Decoder[n].UIW+Decoder[n].UIG+7:Decoder[n].UIG+8]=ISP

where UIO.Address[63:2] is derived from the Address field in the UIO TLP request, and UIO.Length[63:2] is derived from the Length field in the UIO TLP request.

DSP calculations use the HDM decoders in the corresponding USP. The root port calculations make use of the HDM decoders in the associated Host Bridge.

The first condition is in place because HDM decoder operates on translated address. The second and the third condition ensures that all addresses fall within one of the HDM decoders. The fourth condition ensures that the interleave set positions match (i.e., a CXL.mem request from the host to the start address would ordinarily be decoded by this component). 4a is the trivial case where the memory is not interleaved.

If the first three conditions are met but the fourth condition is not met, it is considered a partial match. If the first three conditions are not met, it is considered a mismatch.

#### <span id="page-861-0"></span>9.16.1.2 UIO Address Match (CXL.mem Device)

For a CXL.mem device, UIO address is considered a complete match if there exists an HDM Decoder[n] (see [Section 8.2.4.20](#page-564-1) and [Section 8.2.4.30](#page-596-1)) for which the following conditions are true:

- 1. AT field in the UIO request indicates it is carrying a translated address.
- 2. UIO.Address[63:2] ≥ Decoder[n].Base[63:2].
- 3. UIO.Address[63:2]+UIO.Length[63:2] ≤ Decoder[n].Base[63:2]+ Decoder[n].Size[63:2].
- 4. Either of these sub-conditions are true:
  - a. Decoder[n].UIW=0
  - b. UIO.Address[Decoder[n].IW+Decoder[n].IG+7:Decoder[n].IG+8]=ISP
- 5. UIO.Address[Decoder[n].IG+7:2] + UIO.Length[Decoder[n].IG+7:2] <= (2\*\* IG+8).

The first three conditions are identical to the DSP case. The terms involved in the fourth check are different, but it serves the same purpose (i.e., ensures that a CXL.mem request from the host to the start address would ordinarily be decoded by this component). The fifth condition ensures that the access does not cross an interleave boundary, thus ensuring that all the addresses that are referenced by the request are owned by the device.

If the first three conditions are met but either of the other two conditions are not met, it is considered a partial match. If the first three conditions are not met, it is considered a mismatch.

## <span id="page-862-0"></span>9.17 Direct P2P CXL.mem for Accelerators

The Direct P2P CXL.mem feature enables accelerators to use .mem semantics to access peer Type 3 devices. This feature is supported only by PBR Fabrics, and each accelerator and peer Type 3 device must be attached directly to an Edge Port. Configuration of the Fabric and Edge Ports is performed by the host and FM.

Through mechanisms beyond the scope of this specification, the FM is preconfigured or informed of which Type 3 device(s) (i.e., SLD, MLD, or GFD) are to be configured for Direct P2P CXL.mem access by a given accelerator.

### <span id="page-862-1"></span>9.17.1 Peer SLD Configuration

Host software and the FM may use the following high-level flow to configure Direct P2P CXL.mem communication between an accelerator and a peer Type 3 SLD:

- 1. The FM binds the SLD's Edge Port to the host VH of the accelerator, setting the vPPB.root.PID field to the PBR ID (PID) of the accelerator's Edge Port. This enables the host to configure the SLD, but the accelerator to carry out CXL.mem transactions with the SLD.
- 2. Using the **Set LDST Segment Entries** command (see [Section 7.7.13.16\)](#page-475-3), the host configures the LDST in the accelerator's Edge Port with one or more LDST Segments for the HPA range of the SLD, specifying the vPPB of the SLD's Edge Port.
- 3. Host software configures the SLD, notably its HDM Decoders, on behalf of the accelerator. HDM addresses in the SLD are HPAs.

### <span id="page-862-2"></span>9.17.2 Peer MLD Configuration

Host software and the FM may use the following high-level flow to configure Direct P2P CXL.mem communication between one or more accelerators that belong to the host and a peer Type 3 MLD:

- 1. The FM binds a vPPB in the MLD's Edge Port to the host VH of its accelerator(s) and an additional vPPB for each accelerator under that host that will be accessing the MLD. Each of these will have a distinct LD-ID. For each vPPB assigned to an accelerator, the vPPB.root.PID field is set to the PID of the accelerator's Edge Port.
- 2. Using the **Set LDST Segment Entries** command (see [Section 7.7.13.16\)](#page-475-3), the host configures the LDST in each accelerator's Edge Port with one or more LDST Segments for the HPA range of the accelerator's LD, specifying the accelerator's vPPB in the MLD's Edge Port.
- 3. Host software configures its LDs in the MLD, notably their HDM Decoders, on behalf of itself and its accelerator(s). HDM addresses in the LD of the host and the LD(s) of the accelerator(s) are HPAs.

### <span id="page-862-3"></span>9.17.3 Peer GFD Configuration

Host software and the FM may use the following high-level flow to configure Direct P2P CXL.mem communication between one or more accelerators that belong to a host and a peer Type 3 GFD:

- 1. The FM configures the GFD for host access normally, while configuring each of the host's accelerators as an additional RPID within the GFD.
- 2. Using the **Set FAST Segment Entries** command (see [Section 7.7.14.7](#page-489-3)), the host configures the FAST decoder in its Edge Port as well as each accelerator's Edge Port with one or more FAST Segments for the HPA range, specifying the GFD's PID.

## <span id="page-863-0"></span>9.18 CXL OS Firmware Interface Extensions

### <span id="page-863-1"></span>9.18.1 CXL Early Discovery Table (CEDT)

<span id="page-863-6"></span>CXL Early Discovery Table enables OSs to locate CXL Host Bridges and the location of Host Bridge registers early during the boot (i.e., prior to parsing of ACPI namespace). The information in this table may be used by early boot code to perform preinitialization of CXL hosts, such as configuration of CXL.cache and CXL.mem.

#### <span id="page-863-2"></span>9.18.1.1 CEDT Header

The pointer to CEDT is found in RSDT or XSDT, as described in ACPI Specification. An ACPI specification-compliant CXL system shall support CEDT and shall include a CHBS entry for every CXL host bridge that is present at boot.

CEDT begins with the following header.

<span id="page-863-4"></span>**Table 9-19. CEDT Header**

| Field             | Length<br>in Bytes | Byte Offset | Description                                             |
|-------------------|--------------------|-------------|---------------------------------------------------------|
| Header:           |                    |             |                                                         |
| Signature         | 4                  | 00h         | 'CEDT'. Signature for the CXL Early Discovery<br>Table. |
| Length            | 4                  | 04h         | Length, in bytes, of the entire CEDT.                   |
| Revision          | 1                  | 08h         | Value is 2.                                             |
| Checksum          | 1                  | 09h         | Entire table must sum to 0.                             |
| OEM ID            | 6                  | 0Ah         | OEM ID                                                  |
| OEM Table ID      | 8                  | 10h         | Manufacturer Model ID                                   |
| OEM Revision      | 4                  | 18h         | OEM Revision                                            |
| Creator ID        | 4                  | 1Ch         | Vendor ID of the utility that created the table.        |
| Creator Revision  | 4                  | 20h         | Revision of the utility that created the table.         |
| CEDT Structure[n] | Varies             | 24h         | A list of CEDT structures for this<br>implementation.   |

<span id="page-863-5"></span>**Table 9-20. CEDT Structure Types**

| Value | Description                                        |
|-------|----------------------------------------------------|
| 0     | CXL Host Bridge Structure (CHBS)                   |
| 1     | CXL Fixed Memory Window Structure (CFMWS)          |
| 2     | CXL XOR Interleave Math Structure (CXIMS)          |
| 3     | RCEC Downstream Port Association Structure (RDPAS) |
| 4     | CXL System Description Structure (CSDS)1           |
| 5-255 | Reserved                                           |

<span id="page-863-7"></span><sup>1.</sup> Introduced in Revision 2 of CEDT.

#### <span id="page-863-3"></span>9.18.1.2 CXL Host Bridge Structure (CHBS)

The CHBS structure describes a CXL Host Bridge.

In an ACPI-compliant system, there shall be one instance of the CXL Host Bridge Device object in ACPI namespace (HID="ACPI0016") for every CHBS entry. The \_UID object under a CXL Host Bridge object, when evaluated, shall match the UID field in the associated CHBS entry.

<span id="page-864-1"></span>**Table 9-21. CHBS Structure**

| Field         | Length<br>in Bytes | Byte Offset | Description                                                                                                                                                                                                                     |
|---------------|--------------------|-------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Type          | 1                  | 00h         | =0 to indicate that this is a CHBS entry                                                                                                                                                                                        |
| Reserved      | 1                  | 01h         | Reserved                                                                                                                                                                                                                        |
| Record Length | 2                  | 02h         | Length of this record (20h).                                                                                                                                                                                                    |
| UID           | 4                  | 04h         | CXL Host Bridge Unique ID. Used to associate a CHBS<br>instance with a CXL Host Bridge instance. The value of this<br>field shall match the output of _UID under the associated<br>CXL Host Bridge in ACPI namespace.           |
| CXL Version   | 4                  | 08h         | •<br>0000 0000h: RCH<br>•<br>0000 0001h: Host Bridge that is associated with one or<br>more CXL root ports                                                                                                                      |
| Reserved      | 4                  | 0Ch         | Reserved                                                                                                                                                                                                                        |
| Base          | 8                  | 10h         | •<br>If CXL Version = 0000 0000h, this represents the base<br>address of the RCH Downstream Port RCRB<br>•<br>If CXL Version = 0000 0001h, this represents the base<br>address of the CHBCR<br>See Table 8-17 for more details. |
| Length        | 8                  | 18h         | •<br>If CXL Version = 0000 0000h, this field must be set to<br>8 KB (2000h)<br>•<br>If CXL Version = 0000 0001h, this field must be set to<br>64 KB (1 0000h)                                                                   |

#### <span id="page-864-0"></span>9.18.1.3 CXL Fixed Memory Window Structure (CFMWS)

The CFMWS structure describes zero or more Host Physical Address (HPA) windows that are associated with each CXL Host Bridge. Each window represents a contiguous HPA range that may be interleaved across one or more targets, some of which are CXL Host Bridges. Associated with each window are a set of restrictions that govern its usage. It is the OSPM's responsibility to utilize each window for the specified use.

The HPA ranges described by CFMWS may include addresses that are currently assigned to CXL.mem devices. Before assigning HPAs from a fixed-memory window, the OSPM must check the current assignments and avoid any conflicts.

For any given HPA, it shall not be described by more than one CFMWS entry.

<span id="page-865-0"></span>**Table 9-22. CFMWS Structure (Sheet 1 of 3)**

| Field                                              | Length<br>in Bytes | Byte<br>Offset | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |  |
|----------------------------------------------------|--------------------|----------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--|
| Type                                               | 1                  | 00h            | 1 = indicates this is a CFMWS entry                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |  |
| Reserved                                           | 1                  | 01h            | Reserved                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |  |
| Record Length                                      | 2                  | 02h            | Length of this record = 024h + 4 * NIW.<br>NIW is the raw count of Interleave ways whereas ENIW is the encoded value:<br>•<br>If ENIW<8, NIW=2**ENIW<br>•<br>If ENIW≥8, NIW=3* 2**(ENIW-8)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |  |
| Reserved                                           | 4                  | 04h            | Reserved                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |  |
| Base HPA                                           | 8                  | 08h            | Base of this HPA range. This value shall be a 256-MB-aligned address.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |  |
| Window Size                                        | 8                  | 10h            | The total number of consecutive bytes of HPA this window represents. This value<br>shall be a multiple of NIW*256 MB.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |  |
| Encoded Number<br>of Interleave<br>Ways (ENIW)     | 1                  | 18h            | The encoded number of targets with which this window is interleaved. The valid<br>encoded values are specified in the Interleave Ways field of the CXL HDM Decoder<br>n Control register (see Section 8.2.4.20.7). This field determines the number of<br>entries in the Interleave Target List, starting at Offset 24h.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |  |
| Interleave<br>Arithmetic                           | 1                  | 19h            | This field defines the arithmetic used for mapping HPA to an interleave target in<br>the Interleave Target List:<br>•<br>00h = Standard Modulo arithmetic<br>•<br>01h = Modulo arithmetic combined with XOR<br>•<br>All other encodings are reserved                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |  |
| Reserved                                           | 2                  | 1Ah            | Reserved                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |  |
| Host Bridge<br>Interleave<br>Granularity<br>(HBIG) | 4                  | 1Ch            | The number of consecutive bytes within the interleave that are decoded by each<br>target in the Interleave Target List represented in an encoded format. The valid<br>values are specified in the Interleave Granularity field of the CXL HDM Decoder n<br>Control register (see Section 8.2.4.20.7).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |  |
| Window<br>Restrictions                             | 2                  | 20h            | A bitmap describing the restrictions being placed on the OSPM's use of the<br>window. It is the OSPM's responsibility to adhere to these restrictions. Failure to<br>adhere to these restrictions results in undefined behavior. More than one bit<br>within this field may be set:<br>•<br>Bit[0]: Device Coherent: Formerly known as CXL Type 2 Memory:<br>— 1 = Window is configured to expose device-coherent memory (HDM-D<br>if Bit[5]=0 ; HDM-DB if Bit[5]=1).<br>•<br>Bit[1]: Host-only Coherent: Formerly known as CXL Type 3 Memory:<br>— 1 = Window is configured to expose host-only coherent memory (HDM<br>H). If an HDM decoder that is mapped to this windows has the BI bit<br>set, it will result in undefined behavior.<br>•<br>Bit[2]: Volatile:<br>— 1 = Window is configured for use with volatile memory.<br>•<br>Bit[3]: Persistent:<br>— 1 = Window is configured for use with persistent memory.<br>•<br>Bit[4]: Fixed Device Configuration:<br>— 1 = Any device ranges that have been assigned an HPA from this<br>window must not be reassigned.<br>•<br>Bit[5]: BI:<br>— 1 = Window is configured for use with Back-Invalidate flows.<br>•<br>Bits[15:6]: Reserved |  |
| QTG ID                                             | 2                  | 22h            | The ID of the QoS Throttling Group associated with this window. The _DSM for<br>retrieving QTG ID is utilized by the OSPM to determine to which QTG a device<br>HDM range should be assigned.<br>This field must not exceed the Max Supported QTG ID returned by the _DSM for<br>retrieving QTG.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |  |

**Table 9-22. CFMWS Structure (Sheet 2 of 3)**

| Field                     | Length<br>in Bytes | Byte<br>Offset | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |  |
|---------------------------|--------------------|----------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--|
| Interleave Target<br>List | 4*NIW              | 24h            | A list of all the Interleave Targets. The number of entries in this list shall match<br>the Number of Interleave Ways (NIW). The order of the targets reported in this<br>List indicates the order in the Interleave Set.<br>For Interleave Sets that only span CXL Host Bridges, this is a list of CXL Host<br>Bridge _UIDs that are part of the Interleave Set. In this case, for each _UID value<br>in this list, there must exist a corresponding CHBS structure.<br>If the Interleave Set spans non-CXL domains, this list may contain values that do<br>not match _UID field in any CHBS structures. These entries represent Interleave<br>Targets that are not CXL Host Bridges.<br>The set of HPAs decoded by Entry N in the Interleave Target List shall satisfy the<br>following equations:<br>1.<br>Base HPA <= HPA < Base HPA + Windows Size: where the Base HPA and<br>Window size shall be multiple of NIW. If (Interleave Arithmetic==0):<br>a.<br>If ENIW=0<br>N=0<br>b.<br>If ENIW=1<br>N= HPA[8+HBIG]<br>c.<br>If ENIW<8 AND ENIW>1<br>N = HPA[7+HBIG+ENIW:8+HBIG]<br>d.<br>If NIW = 8<br>// 3 way<br>N = HPA[51:8+HBIG] MOD 3<br>e.<br>If NIW=9<br>// 6 way<br>N = HPA[8+HBIG]<br>+ 2* HPA[51:9+HBIG] MOD 3<br>f.<br>If NIW=10<br>//12 way<br>N = HPA[9+HBIG:8+HBIG]<br>+ 4* HPA[51:10+HBIG] MOD 3<br>2.<br>If (Interleave Arithmetic==1):<br>a.<br>If NIW=0 //1 way<br>N=0<br>b.<br>If NIW =1<br>// 2 way<br>N = XORALLBITS (HPA AND XORMAP[0])<br>If NIW=2<br>// 4 way<br>N = XORALLBITS (HPA AND XORMAP[0]) +<br>2* XORALLBITS (HPA AND XORMAP[1]) |  |

**Table 9-22. CFMWS Structure (Sheet 3 of 3)**

| Field                     | Length<br>in Bytes | Byte<br>Offset | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |  |
|---------------------------|--------------------|----------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--|
| Interleave Target<br>List | 4*NIW              | 24h            | c.<br>If NIW=3<br>// 8 way<br>N = XORALLBITS (HPA AND XORMAP[0]) +<br>* XORALLBITS (HPA AND XORMAP[1]) +<br>* XORALLBITS (HPA AND XORMAP[2])<br>d.<br>If NIW=4<br>//16 way<br>N = XORALLBITS (HPA AND XORMAP[0])+<br>2* XORALLBITS (HPA AND XORMAP[1]) +<br>4* XORALLBITS (HPA AND XORMAP[2]) +<br>8* XORALLBITS (HPA AND XORMAP[3])<br>e.<br>If NIW =8<br>// 3 way, same as Interleave Arithmetic=0<br>N = HPA[51:8+HBIG] MOD 3<br>f.<br>If NIW =9<br>// 6 way<br>N = XORALLBITS (HPA AND XORMAP[0])<br>+ 2* HPA[51:9+HBIG] MOD 3<br>g.<br>If NIW=10<br>// 12 way<br>N = XORALLBITS (HPA AND XORMAP[0])<br>+ 2* XORALLBITS (HPA AND XORMAP[1])<br>+ 4* HPA[51:10+HBIG] MOD 3<br>N is 0 based (0<= N <niw).<br>Where XORALLBITS is an operation that outputs a single bit by XORing all the bits<br/>in the input. AND is a standard bitwise AND operation and XORMAP[m] is the mth<br/>element (m is 0 based) in the XORMAP array that is part of the CXIMS entry with</niw).<br> |  |

#### <span id="page-867-0"></span>9.18.1.4 CXL XOR Interleave Math Structure (CXIMS)

If a CFMWS entry reports Interleave Arithmetic=1, there must be one CXIMS entry associated with the HBIG value in the CFMWS. CXIMS carries an array of bitmaps. Each bitmap represents the bits that are XORed together to calculate the individual bits of the Interleave Way as described in the definition of the Interleave Target List field in CFMWS. The host implementation is responsible for selecting an XOR function that generates even distribution of addresses and does not lead to address aliasing.

<span id="page-867-1"></span>**Table 9-23. CXIMS Structure**

| Field                             | Length<br>in Bytes | Byte<br>Offset | Description                                                                                                                            |
|-----------------------------------|--------------------|----------------|----------------------------------------------------------------------------------------------------------------------------------------|
| Type                              | 1                  | 00h            | 2 = Indicates that this is a CXIMS entry                                                                                               |
| Reserved                          | 1                  | 01h            | Reserved                                                                                                                               |
| Record Length                     | 2                  | 02h            | Length of this record = 8 + 8 * NIB.                                                                                                   |
| Reserved                          | 2                  | 04h            | Reserved                                                                                                                               |
| HBIG                              | 1                  | 06h            | Host Bridge Interleave Granularity to which this CXIMS<br>instance corresponds. See Table 9-22 for the definition of<br>the term HBIG. |
| Number of Bitmap<br>Entries (NIB) | 1                  | 07h            | The number of entries in the XORMAP list.                                                                                              |
| XORMAP List                       | 8 * NIB            | 08h            | A list of Bitmaps. XORMAP[0] is the first entry.                                                                                       |

#### <span id="page-868-0"></span>9.18.1.5 RCEC Downstream Port Association Structure (RDPAS)

<span id="page-868-4"></span>RDPAS structure enables error handler to locate the Downstream Port(s) that report errors to a given RCEC. For every RCEC, zero or more entries of this type are permitted.

<span id="page-868-2"></span>**Table 9-24. RDPAS Structure**

| Field                  | Length<br>in Bytes | Byte<br>Offset | Description                                                                                                                                                                                                                       |
|------------------------|--------------------|----------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Type                   | 1                  | 00h            | 3 = Indicates that this is an RDPAS entry                                                                                                                                                                                         |
| Reserved               | 1                  | 01h            | Reserved                                                                                                                                                                                                                          |
| Record Length          | 2                  | 02h            | Length of this record = 14h                                                                                                                                                                                                       |
| RCEC Segment<br>Number | 2                  | 04h            | The PCIe segment number associated with this RCEC                                                                                                                                                                                 |
| RCEC BDF               | 2                  | 06h            | •<br>Bits[2:0]: RCEC Function Number<br>•<br>Bits[7:3]: RCEC Device Number<br>•<br>Bits[15:8]: RCEC Bus Number                                                                                                                    |
| Base Address           | 8                  | 08h            | If Protocol Type = CXL.io, this field shall be the RCRB base<br>associated with the Downstream Port.<br>If Protocol Type = CXL.cachemem, this will be the<br>Component Base Register Base associated with the<br>Downstream Port. |
| Protocol Type          | 1                  | 10h            | •<br>00h = The error source is CXL.io<br>•<br>01h = The error source is CXL.cachemem                                                                                                                                              |
| Reserved               | 3                  | 11h            | Reserved                                                                                                                                                                                                                          |

> **IMPLEMENTATION NOTE**

CXL-aware software may take the following steps upon observing an Uncorrected Internal Error or an Corrected Internal Error being logged in an RCEC at Segment Number S and BDF=B.

If the CEDT contains RDPAS structures:

- For all RDPAS structures where RCEC Segment Number=S and RCEC BDF= B:
  - If Protocol Type=CXL.io, read the Base Address field and use that information to access the RCRB AER registers and determine whether any errors are logged there
  - If Protocol Type=CXL.cachemem, read the Base Address field and use that information to access the Component Register RAS Capability registers (see [Section 8.2.4.17\)](#page-548-2) and determine whether any errors are logged there

**Else:**

<span id="page-868-3"></span>• Probe all CXL Downstream Ports and determine whether they have logged an error in the CXL.io or CXL.cachemem status registers

#### <span id="page-868-1"></span>9.18.1.6 CXL System Description Structure (CSDS)

The CSDS describes CXL System Wide Description and Configuration.

In a system, there shall be only one instance of the CSDS in the CEDT.

<span id="page-869-1"></span>**Table 9-25. CSDS Structure**

| Field               | Length<br>in Bytes | Byte<br>Offset | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
|---------------------|--------------------|----------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Type                | 1                  | 00h            | 4 = Indicates that this is a CSDS entry                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| Reserved            | 1                  | 01h            | Reserved                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| Record Length       | 2                  | 02h            | Length of this record = 08h                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| System Capabilities | 2                  | 04h            | A bitmap that describes system-wide capabilities. More<br>than one bit within this field is permitted to be set.<br>•<br>Bit[0]: Cmp-M:<br>— 1 = System is configured for use with devices<br>that return modified data using the Cmp-M<br>response.<br>•<br>Bit[1]: No Clean Writeback: Specifies the clean<br>writeback behavior of the host.<br>— 0 = The host may or may not generate clean<br>writebacks<br>— 1 = The host guarantees to never generate clean<br>writeback transactions at the host's cacheline<br>granularity<br>•<br>Bit[2]: Viral Policy: If 1, the system policy is to<br>enable Viral.<br>•<br>Bits[5:3]: Metabits Storage Configuration. Upon<br>hot-add, the OS may configure the device to match<br>host metadata storage requirements<br>— 0h: 2 bits of Metadata<br>— 1h: No Metadata<br>— 2h: 1 bit of Metadata, bit-0 of Meta0-State Value<br>— 3h: 1 bit of Metadata, bit-1 of Meta0-State Value<br>— 4h: 2 bits of Metadata + 1 TE State bit<br>— 5h: No Metadata + 1 TE State bit<br>— 6h: 1 bit of Metadata, bit-0 of Meta0-State Value<br>+ 1 TE State bit<br>— 7h: 1 bit of Metadata, bit-1 of Meta0-State Value<br>+ 1 TE State bit<br>•<br>Bits[15:6]: Reserved |
| Reserved            | 2                  | 06h            | Reserved                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |

### <span id="page-869-0"></span>9.18.2 CXL \_OSC

<span id="page-869-2"></span>According to ACPI Specification, \_OSC (Operating System Capabilities) is a control method that is used by OSs to communicate to the System Firmware the capabilities supported by the OS and to negotiate ownership of specific capabilities.

The \_OSC interface defined in this section applies only to "Host Bridge" ACPI devices that originate CXL hierarchies. As specified in [Section 9.12](#page-822-0), these ACPI devices must have an \_HID of (or a \_CID that includes) EISAID("ACPI0016"). CXL \_OSC is required for a CXL VH. CXL \_OSC is optional for an RCD. A CXL Host Bridge also originates a PCIe hierarchy and will have a \_CID of EISAID("PNP0A08"). As such, a CXL Host Bridge device may expose both CXL \_OSC and PCIe \_OSC.

The \_OSC interface for a CXL Host Bridge is identified by the Universal Unique Identifier (UUID) 68f2d50b-c469-4d8a-bd3d-941a103fd3fc.

A revision ID of 1 encompasses fields defined within this section, composed of 5 DWORDs, as listed in [Table 9-26.](#page-870-0)

<span id="page-870-0"></span>**Table 9-26. \_OSC Capabilities Buffer DWORDs**

| _OSC Capabilities<br>Buffer DWORD # | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
|-------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1                                   | Contains bits that are generic to _OSC and defined by ACPI. These include status and<br>error information.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| 2                                   | PCIe Support Field as defined by PCI Firmware Specification.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| 3                                   | PCIe Control Field as defined by PCI Firmware Specification.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| 4                                   | CXL Support Field: Bits defined in the CXL Support Field provide information<br>regarding CXL features supported by the OS. Just like the PCIe Support field, contents<br>in the CXL Support Field are passed in a single direction; the OS will disregard any<br>changes to this field when returned.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| 5                                   | CXL Control Field: Just like the PCIe Control Field, bits defined in the CXL Control<br>Field are used to submit OS requests for control/handling of the associated feature,<br>typically including but not limited to features that utilize native interrupts or events<br>that are handled by an OS-level driver. If any bits in the CXL Control Field are returned<br>cleared (i.e., masked to 0) by the _OSC control method, the respective feature is<br>designated as unsupported by the platform and must not be enabled by the OS. Some<br>of these features may be controlled by System Firmware prior to OS boot or during<br>runtime for an OS that is unaware of these features, while others may be disabled/<br>inoperative until native OS support for such features is available.<br>If the CXL _OSC control method is absent from the scope of a Host Bridge device, then<br>the OS must not enable or attempt to use any features defined in this section for the<br>hierarchy originated by the Host Bridge. Doing so could conflict with System Firmware<br>operations, or produce undesired results. It is recommended that a machine with<br>multiple Host Bridge devices should report the same capabilities for all Host Bridges,<br>and also negotiate control of the features described in the CXL Control Field in the<br>same way for all Host Bridges. |

<span id="page-870-1"></span>**Table 9-27. Interpretation of CXL \_OSC Support Field**

| Support Field<br>Bit Offset | Interpretation                                                                                                                                                                                                                                                                                                                                                                                                                              |
|-----------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0                           | RCD and RCH Port Register Access Supported<br>The OS sets this bit to 1 if it supports access to RCD and RCH Port registers as defined in<br>Section 9.11. Otherwise, the OS clears this bit to 0.                                                                                                                                                                                                                                          |
| 1                           | CXL VH Register Access Supported<br>The OS sets this bit to 1 if it supports access to CXL VH component registers as defined in<br>Section 9.12. If this bit is 1, bit 0 must also be 1. Otherwise, the OS clears this bit to 0.                                                                                                                                                                                                            |
| 2                           | CXL Protocol Error Reporting Supported<br>The OS sets this bit to 1 if it supports handling of CXL Protocol Errors. Otherwise, the OS<br>clears this bit to 0.<br>If the OS sets this bit, it must also set either bit 0 or bit 1 above.<br>Note: Firmware may retain control of AER if the OS does not support CXL Protocol Error<br>reporting because the owner of AER owns CXL Protocol error management.                                |
| 3                           | CXL Native Hot-Plug Supported<br>The OS sets this bit to 1 if it supports CXL hot-add and managed CXL Hot-Remove without<br>firmware assistance. Otherwise, the OS clears this bit to 0.<br>If the OS sets this bit, it must request PCIe Native Hot-Plug control. If PCIe Native Hot-Plug<br>control is granted to the OS, such an OS must natively handle CXL Hot-Plug as well.<br>If the OS sets this bit, it must also set bit 1 above. |
| 4-31                        | Reserved                                                                                                                                                                                                                                                                                                                                                                                                                                    |

<span id="page-871-1"></span>**Table 9-28. Interpretation of CXL \_OSC Control Field, Passed in via Arg3**

| Control Field<br>Bit Offset | Interpretation                                                                                                                                                                                       |  |  |  |
|-----------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--|--|--|
| 0                           | CXL Memory Error Reporting Control                                                                                                                                                                   |  |  |  |
|                             | The OS sets this bit to 1 to request control over CXL Memory Error Reporting i.e. Set Event<br>Interrupt Policy command for devices that implement Memory Device Commands (see<br>Section 8.2.10.9). |  |  |  |
|                             | If the OS sets this bit, the OS must also set either bit 0 or bit 1 in the CXL _OSC Support Field<br>(see Table 9-26).                                                                               |  |  |  |
| 1-31                        | Reserved                                                                                                                                                                                             |  |  |  |

<span id="page-871-2"></span>**Table 9-29. Interpretation of CXL \_OSC Control Field, Returned Value**

| Control Field<br>Bit Offset | Interpretation                                                                                                                                                                                                                                                                                                                                                      |  |  |  |
|-----------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--|--|--|
| 0                           | CXL Memory Error Reporting Control                                                                                                                                                                                                                                                                                                                                  |  |  |  |
|                             | The firmware sets this bit to 1 to grant control over CXL Memory Expander Error Reporting<br>i.e. Set Event Interrupt Policy command for devices that implement Memory Device<br>Commands (see Section 8.2.10.9). If firmware grants control of this feature, firmware must<br>ensure that these devices are not configured in Firmware First error reporting mode. |  |  |  |
|                             | If control of this feature was requested and denied or was not requested, firmware returns<br>this bit cleared to 0.                                                                                                                                                                                                                                                |  |  |  |
| 1-31                        | Reserved                                                                                                                                                                                                                                                                                                                                                            |  |  |  |

#### <span id="page-871-0"></span>9.18.2.1 Rules for Evaluating \_OSC

This section defines when and how the OS must evaluate \_OSC, as well as restrictions on firmware implementations.

##### 9.18.2.1.1 Query Support Flag

If the Query Support Flag (\_OSC Capabilities Buffer DWORD 1, bit 0) is set by the OS while evaluating \_OSC, hardware settings are not permitted to be changed by firmware in the context of the \_OSC call. It is strongly recommended that the OS evaluate \_OSC with the Query Support Flag set until \_OSC returns the Capabilities Masked bit cleared to negotiate the set of features to be granted to the OS for native support. A platform may require a specific combination of features to be natively supported by an OS before granting native control of a given feature.

##### 9.18.2.1.2 Evaluation Conditions

The OS must evaluate \_OSC under the following conditions:

- During initialization of any driver that provides native support for features described in the section above. These features may be supported by one or many drivers, but should be evaluated only by the main bus driver for that hierarchy. Secondary drivers must coordinate with the bus driver to install support for these features. Drivers shall not relinquish control of previously obtained features. That is, bits set in \_OSC Capabilities Buffer DWORD 3 and DWORD 5 after the negotiation process must be set on all subsequent negotiation attempts.
- When a Notify(<device>, 8) is delivered to the CXL Host Bridge device.
- Upon resume from S4, System Firmware will handle context restoration when resuming from S1 through S3.

If a CXL Host Bridge device exposes CXL \_OSC, CXL-aware OSPM shall evaluate CXL \_OSC and not evaluate PCIe \_OSC.

##### 9.18.2.1.3 Sequence of \_OSC Calls

The following rules govern sequences of calls to \_OSC that are issued to the same Host Bridge and occur within the same boot:

- The OS is permitted to evaluate OSC an arbitrary number of times.
- If the OS declares support of a feature in the Status Field in one call to \_OSC, then it must preserve the set state of that bit (and thereby declare support for that feature) in all subsequent calls.
- If the OS is granted control of a feature in the Control Field in one call to \_OSC, then it must preserve the set state of that bit (requesting that feature) in all subsequent calls.
- Firmware shall not reject control of any feature it has previously granted control to.
- There is no mechanism for the OS to relinquish control of a previously requested and granted feature.

##### 9.18.2.1.4 ASL Example

```
Device(CXL0)
      Name( HID, EISAID("ACPI0016")) // CXL Host Bridge
      Name(_CID, Package(2)
                  EISAID("PNP0A03"), // PCI Compatible Host Bridge
                  EISAID("PNP0A08") // PCI Express Compatible Host Bridge
            })
     Name(SUPP,0) // PCI _OSC Support Field value Name(CTRL,0) // PCI _OSC Control Field value Name(SUPC,0) // CXL _OSC Support Field value Name(CTRC,0) // CXL _OSC Control Field value
      Method(_OSC,4)
{    // Check for proper UUID
    If(LEqual(Arg0,TOUUID("68f2d50b-c469-4d8a-bd3d-941a103fd3fc ")))
                        // Create DWord-adressable fields from the Capabilities Buffer CreateDWordField(Arg3,0,CDW1)
CreateDWordField(Arg3,4,CDW2)
CreateDWordField(Arg3,8,CDW3)
CreateDWordField(Arg3,12,CDW4)
CreateDWordField(Arg3,16,CDW5)
// Save Capabilities DWord2, 3. 4. 5
                         Store(CDW2,SUPP)
                        Store (CDW3, CTRL)
                        Store(CDW4,SUPC)
                        Store(CDW4,CTRc)
                   } Else
                         Or(CDW1,4,CDW1) // Unrecognized UUID
                        Return(Arg3)
            // End
                         OSC
    Other methods such as _BBN, _CRS, PCIe _OSC
//End CXL0
```

### <span id="page-872-0"></span>9.18.3 CXL Root Device Specific Methods (\_DSM)

DSM is a control method that enables devices to provide device-specific functions for the benefit of the device driver. See ACPI Specification for details. Table 9-30 lists the \_DSM Functions that are associated with the CXL Root Device (HID="ACPI0017").

<span id="page-873-1"></span>**Table 9-30. \_DSM Definitions for CXL Root Device**

| UUID                                 | Revision | Function  | Description                            |
|--------------------------------------|----------|-----------|----------------------------------------|
| F365F9A6-A7DE-4071-A66A-B40C0B4F8E52 | 1        | 1         | Retrieve QTG ID (see Section 9.18.3.1) |
|                                      | -        | All other | Reserved                               |

All other Function values are reserved. The Revision field represents the version of the individual \_DSM Function. The Revision associated with a \_DSM Function is incremented whenever that \_DSM Function is extended to add more functionality. Backward compatibility shall be maintained during this process. Specifically, for all values of n, a \_DSM Function with Revision n+1 may extend Revision ID n by assigning meaning to the fields that are marked as reserved in Revision n but must not redefine the meaning of existing fields and must not change the size or type of I/O parameters. Software that was written for a lower Revision may continue to operate on \_DSM Functions with a higher Revision but will not be able to take advantage of new functionality. It is legal for software to invoke a \_DSM Function and pass in any nonzero Revision ID value that does not exceed the Revision ID defined in this specification for that \_DSM Function.

For example, if the most-current version of this specification defines Revision ID=4 for \_DSM Function Index f, software is permitted to invoke the \_DSM Function with Function Index f with a Revision ID value that belongs to the set {1, 2, 3, 4}.

#### <span id="page-873-0"></span>9.18.3.1 \_DSM Function for Retrieving QTG ID

This section describes how the OSPM can request the firmware to determine the optimum QoS Throttling Group (QTG) to which a device HDM range should be assigned, based on its performance characteristics. It is strongly recommended that OSPM evaluate this \_DSM Function to retrieve QTG recommendations and map the device HDM range to an HPA range that is described by a CFMWS entry that follows the platform recommendations.

For each Device Scoped Memory Affinity Structure (DSMAS) in the Device CDAT, the OSPM should calculate the Read Latency, Write Latency, Read Bandwidth, and Write Bandwidth from the CXL Root Port within the same VCS. The term DSMAS is defined in Coherent Device Attribute Table Specification. This calculation must consider the latency and bandwidth contribution of any intermediate switches. The OSPM should call this \_DSM with the performance characteristics for the Device HDM range thus calculated, utilize the return ID value(s) to pick an appropriate CFMWS, and then map the DSMAS DPA range to HPAs that are covered by that CFMWS. This process may be repeated for each DSMAS memory range that the OSPM wishes to utilize from the device.

**Location:**

This object shall be a child of the CXL Root Device (HID="ACPI0017").

### Arguments:

Arg0: UUID: f365f9a6-a7de-4071-a66a-b40c0b4f8e52

Arg1: Revision ID: 1

Arg2: Function Index: 01h

Arg3: A package of memory device performance characteristic. The package consists of 4 DWORDs.

Package { Read Latency Write Latency Read Bandwidth Write Bandwidth }

### Return:

A package containing two elements - a WORD that returns the maximum throttling group that the platform supports, and a package containing the QTG ID(s) that the platform recommends.

```
Package {
Max Supported QTG ID
Package {QTG Recommendations}
}
```

<span id="page-874-0"></span>**Table 9-31. \_DSM for Retrieving QTG, Inputs, and Outputs**

| Field                          | Size                                                                                                                                                                                                                                                             | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |  |  |
|--------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--|--|
| Input Package:                 |                                                                                                                                                                                                                                                                  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |  |  |
| Read Latency                   | DWORD                                                                                                                                                                                                                                                            | The best-case read latency as measured from the CXL root port within<br>the same VCS, expressed in picoseconds.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |  |  |
| Write Latency                  | DWORD                                                                                                                                                                                                                                                            | The best-case write latency as measured from the CXL root port within<br>the same VCS, expressed in picoseconds.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |  |  |
| Read Bandwidth                 | DWORD                                                                                                                                                                                                                                                            | The best-case read bandwidth as measured from the CXL root port within<br>the same VCS, expressed in MB/s.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |  |  |
| Write Bandwidth                | The best-case write bandwidth as measured from the CXL root port<br>DWORD<br>within the same VCS, expressed in MB/s.                                                                                                                                             |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |  |  |
| Return Package:                |                                                                                                                                                                                                                                                                  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |  |  |
| Max Supported QTG ID           | The highest QTG ID supported by the platform. The platform must be<br>capable of supporting all QTGs whose ID, Q, satisfies the following<br>equation:<br>WORD<br>0 > Q ≥ Max Supported QTG ID<br>For every value of Q, there may be zero or more CFMWS entries. |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |  |  |
| QTG Recommendations<br>Package |                                                                                                                                                                                                                                                                  | A package that consists of 0 or more WORD elements. It is a prioritized<br>list of QTG IDs that are considered acceptable by the platform for the<br>specified performance characteristics. If the package contains more than<br>one element, element[n] is preferred by the platform over element[n+1].<br>If the package is empty, the platform is unable to find any suitable QTGs<br>for this set of input values. If the OSPM does not follow platform QTG<br>recommendations, it may result in severe performance degradation.<br>Every element in this package must be no greater than the Max<br>Supported QTG ID above.<br>For example, if QTG Recommendations = Package () {2, 1}, the OSPM<br>should first attempt to assign from QTG ID 2, and then attempt to assign<br>QTG ID 1 if an assignment cannot be found in QTG ID 2. |  |  |

## <span id="page-875-0"></span>9.19 Manageability Model for CXL Devices

<span id="page-875-2"></span>Manageability is the set of capabilities that a managed entity exposes to a management entity. In the context of CXL, a CXL device is the managed entity. These capabilities are generally classified in sensors and effectors. An Event Log is an example of a sensor, whereas the ability to update the device firmware is an example of an effector. Sensors and effectors can either be accessed in-band (i.e., by OS/VMM resident software), or out-of-band (i.e., by firmware running on a management controller that is OS independent).

In-band software can access a CXL device's manageability capabilities by issuing PCIe configuration read/write or MMIO read/write transactions to its Mailbox registers. These accesses are generally mediated by the CXL device driver. This is consistent with how PCIe adapters are managed.

Out-of-band manageability in S0 state can leverage transports for which an MCTP binding specification has been defined. This assumes that the CXL.io path will decode and forward MCTP over PCIe VDMs in both directions. Form factors, such as PCIe CEM Specification, provision two SMBUS pins (clock and data). The SMBUS path can be used for out-of-band manageability in Sx state or in the Link Down case. This is consistent with PCIe adapters. CXL components may also support additional management capabilities defined in other specifications, such as Platform-Level Data Model (PLDM).

## <span id="page-875-1"></span>9.20 Component Command Interface

<span id="page-875-3"></span>Runtime management of CXL components is facilitated by a Component Command Interface (CCI). A CCI represents a command target that is used to process management and configuration commands that are issued to the component. [Table 8-49,](#page-633-1) [Table 8-141](#page-718-1), and [Table 8-230](#page-793-1) define the commands that a CCI can support.

A component can implement multiple CCIs of varying types that operate independently of one another and that have a uniquely defined list of supported commands. There are 2 types of CCIs:

- CXL Mailbox Registers: A component can expose up to 2 CXL mailboxes through its Mailbox registers for every instance of CXL Device Registers, as defined in [Section 8.2.9.4](#page-623-2). Each mailbox represents a unique CCI instance.
- MCTP-based CCIs: Components with MCTP-capable interconnects can expose up to 1 CCI per interconnect. There is a 1:1 relationship between the component's MCTPbased CCIs and MCTP-capable interconnects. Transfer of commands via MCTP uses the transport protocol defined in [Section 7.6.3.](#page-346-3)

All CCIs shall comply with the properties described in [Section 9.20.1.](#page-876-0)

> **IMPLEMENTATION NOTE**

The CXL mailbox is derived from the PCIe standard MMIO Mailbox Capability (MMB) with extensions defined in [Section 8.2.9.4](#page-623-2) for supporting CXL defined commands. Therefore, the CXL mailbox may also support PCI-SIG defined commands (MMB Command Opcode Vendor ID = 0001h) or commands defined by other entities. However, non-CXL defined commands are not reported in the CXL CEL and discovery of those commands is outside of the scope of this specification.

CXL components that need to be compatible with non-CXL aware software may advertise both the CXL Primary Mailbox (Vendor ID = 1E98h or 0000h, ID = 0002h) and the PCIe MMB (Vendor ID = 0001h, ID = 0001h). However, they are required to alias the PCIe MMB header to the CXL Primary Mailbox registers. Refer to [Section 8.2.9](#page-618-2), [Figure 8-12](#page-619-1). CXL components that do not need to be compatible with non-CXL aware software should only advertise the CXL Primary Mailbox and not the PCIe MMB.

### <span id="page-876-0"></span>9.20.1 CCI Properties

Components that implement more than one CCI shall process commands from those CCIs in a manner that avoids starvation so that commands submitted to one CCI do not prevent commands from other CCIs from being handled. The exact algorithm for accepting commands from multiple CCIs is implementation specific. Each CCI within a component reports its supported command list through the Command Effects Log (CEL), as described in [Section 8.2.10.5.2.1](#page-676-3).

Interface-specific properties of commands, background operation, and timeouts are defined in [Section 8.2.9.4](#page-623-2) for mailbox CCIs and in [Section 9.20.2](#page-877-0) for MCTP-based CCIs. Each CCI can support the execution of only one background command at a time.

When a command is successfully started as a background operation, the component shall return the Background Command Started return code defined in [Section 8.2.9.4.5.1](#page-627-4). While the command is executing in the background, the component should update the percentage complete at least once per second.

A component may return the Busy return code if a command is sent to initiate a Background Operation while a Background Operation is already running on any other CCI.

An ongoing background command may be aborted by issuing a Request Abort Background Operation command on the same CCI (see [Section 8.2.10.1.5\)](#page-638-6).

Each CCI within a component shall maintain a unique context with respect to the following capabilities:

• CEL content

With respect to the following capabilities, the Primary and Secondary Mailbox Registers CCI instance pairs shall share the context, but the MCTP CCI within a component shall have a unique context

• Events, including reading contents, clearing entries, and configuring interrupt settings

> **IMPLEMENTATION NOTE**

It is recommended that components with multiple CCIs that support commands that run as Background Operations only advertise support for those commands on one CCI.

Coordination between management entities attempting concurrent commands over separate CCIs that have component-level impact (e.g., FW update, etc.) is beyond the scope of this specification.

### <span id="page-877-0"></span>9.20.2 MCTP-based CCI Properties

The CCI command timeout is 2 seconds, measured from when the command has been received by the component to when the component has started to transmit its response. Components should respond within this time limit; otherwise, requesters may timeout. Requesters must account for round-trip transmission time in addition to the command timeout.

> **IMPLEMENTATION NOTE**

MCTP-based CCIs are intended to provide a dedicated management interface that operates independently from the state of any of the component's CXL interfaces; it is strongly recommended, but not required, that commands initiated on MCTP-based CCIs are not interrupted by Conventional Resets or any other changes of state of a component's CXL interface(s).

MCTP-based CCIs report background operation status using the Background Operation Status command as defined in [Section 8.2.10.1.2](#page-636-2).

In the event of a command timeout, the requester may retransmit the request. New Message Tags shall be used every time that a request is retransmitted. Requesters may discard responses that arrive after the command timeout period has lapsed.

Commands sent to MCTP-based CCIs on MLD components are processed by the FMowned LD.
