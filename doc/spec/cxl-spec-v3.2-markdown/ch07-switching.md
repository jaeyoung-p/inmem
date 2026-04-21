# <span id="page-318-0"></span>7.0 Switching

## <span id="page-318-1"></span>7.1 Overview

<span id="page-318-4"></span>This section provides an architecture overview of different CXL switch configurations.

### <span id="page-318-2"></span>7.1.1 Single VCS

A single VCS consists of a single CXL Upstream Port and one or more Downstream Ports as illustrated in [Figure 7-1](#page-318-3).

<span id="page-318-3"></span>**Figure 7-1. Example of a Single VCS**

![](_page_318_Figure_8.jpeg)

A Single VCS is governed by the following rules:

- Must have a single USP
- Must have one or more DSPs
- DSPs must support operating in CXL mode or PCIe\* mode
- All non-MLD (includes PCIe and SLD) ports support a single Virtual Hierarchy below the vPPB
- Downstream Switch Port must be capable of supporting RCD mode
- Must support the CXL Extensions DVSEC for Ports (see [Section 8.1.5\)](#page-516-4)
- The DVSEC defines registers to support CXL.io decode to support RCD below the Switch and registers for CXL Memory Decode. The address decode for CXL.io is in addition to the address decode mechanism supported by vPPB.
- Fabric Manager (FM) is optional for a Single VCS

### <span id="page-319-0"></span>7.1.2 Multiple VCS

A Multiple VCS consists of multiple Upstream Ports and one or more Downstream Ports per VCS as illustrated in [Figure 7-2.](#page-319-1)

<span id="page-319-1"></span>**Figure 7-2. Example of a Multiple VCS with SLD Ports**

![](_page_319_Figure_5.jpeg)

A Multiple VCS is governed by the following rules:

- Must have more than one USP.
- Must have one or more DS vPPBs per VCS.
- The initial binding of upstream (US) vPPB to physical port and the structure of the VCS (including number of vPPBs, the default vPPB capability structures, and any initial bindings of downstream (DS) vPPBs to physical ports) is defined using switch vendor specific methods.
- Each DSP must be bound to a PPB or vPPB.
- FM is optional for Multiple VCS. An FM is required for a Multiple VCS that requires bind/unbind, or that supports MLD ports. Each DSP can be reassigned to a different VCS through the managed Hot-Plug flow orchestrated by the FM.
- When configured, each USP and its associated DS vPPBs form a Single VCS Switch and operate as per the Single VCS rules.
- DSPs must support operating in CXL mode or PCIe mode.
- All non-MLD, non-Fabric, and non-GFD HBR ports support a single Virtual Hierarchy below the Downstream Switch Port.
- DSPs must be capable of supporting RCD mode.

### <span id="page-320-0"></span>7.1.3 Multiple VCS with MLD Ports

A Multiple VCS with MLD Ports consists of multiple Upstream Ports and a combination of one or more Downstream MLD Ports, as illustrated in [Figure 7-3.](#page-320-2)

<span id="page-320-2"></span>**Figure 7-3. Example of a Multiple Root Switch Port with Pooled Memory Devices**

![](_page_320_Figure_5.jpeg)

A Multiple VCS with MLD Ports is governed by the following rules:

- More than one USP.
- One or more Downstream vPPBs per VCS.
- Each SLD DSP can be bound to a Single VCS.
- An MLD-capable DSP can be connected to up to 16 USPs.
- Each of the SLD DSPs can be reassigned to a different VCS through the managed Hot-Plug flow orchestrated by the FM.
- Each of the LD instances in an MLD component can be reassigned to a different VCS through the managed Hot-Plug flow orchestrated by the FM.
- When configured, each USP and its associated vPPBs form a Single VCS, and operate as per the Single VCS rules.
- DSPs must support operating in CXL mode or PCIe mode.
- All non-MLD ports support a single Virtual Hierarchy below the DSP.
- DSPs must be capable of supporting RCD mode.

### <span id="page-320-1"></span>7.1.4 vPPB Ordering

vPPBs within a VCS are ordered in the following sequence: the USP vPPB, then the DSP vPPBs in increasing Device Number, Function Number order. This means Function 0 of all vPPBs in order of Device Number, then all vPPBs enumerated at Function 1 in order of Device Number, etc.

For a switch with 65 DSP vPPBs whose USP vPPB was assigned a Bus Number of 3, that would result in the following vPPB ordering:

| vPPB # | PCIe ID    |
|--------|------------|
| 0      | USP 3:0.0  |
| 1      | DSP 4:0.0  |
| 2      | DSP 4:1.0  |
| 3      | DSP 4:2.0  |
|        | …          |
| 32     | DSP 4:31.0 |
| 33     | DSP 4:0.1  |
| 34     | DSP 4:1.1  |
|        | …          |
| 64     | DSP 4:31.1 |
| 65     | DSP 4:0.2  |

This ordering also applies in cases where multi-function vPPBs exist but not all 32 Device Numbers are assigned. For example, a switch with 8 DSP vPPBs whose USP vPPB was assigned a Bus Number of 3 could present its DSP vPPBs in such a way that the host enumeration would result in the following vPPB ordering:

| vPPB # | PCIe ID   |
|--------|-----------|
| 0      | USP 3:0.0 |
| 1      | DSP 4:0.0 |
| 2      | DSP 4:1.0 |
| 3      | DSP 4:2.0 |
| 4      | DSP 4:0.1 |
| 5      | DSP 4:1.1 |
| 6      | DSP 4:2.1 |
| 7      | DSP 4:0.2 |
| 8      | DSP 4:1.2 |

## <span id="page-321-0"></span>7.2 Switch Configuration and Composition

This section describes the CXL switch initialization options and related configuration and composition procedures.

### <span id="page-321-1"></span>7.2.1 CXL Switch Initialization Options

The CXL switch can be initialized using three different methods:

- Static
- FM boots before the host(s)
- FM and host boot simultaneously

#### <span id="page-322-0"></span>7.2.1.1 Static Initialization

[Figure 7-4](#page-322-1) shows a statically initialized CXL switch with 2 VCSs. In this example, the downstream vPPBs are statically bound to ports and are available to the host at boot. Managed hot-add of Devices is supported using standard PCIe mechanisms.

<span id="page-322-1"></span>**Figure 7-4. Static CXL Switch with Two VCSs**

![](_page_322_Figure_5.jpeg)

Static Switch Characteristics:

- No support for MLD Ports
- No support for rebinding of ports to a different VCS
- No FM is required
- At switch boot, all VCSs and Downstream Port bindings are statically configured using switch vendor defined mechanisms (e.g., configuration file in SPI Flash)
- Supports RCD mode, CXL VH mode, or PCIe mode
- VCSs, including vPPBs, behave identically to a PCIe switch, along with the addition of supporting CXL protocols
- Each VCS is ready for enumeration when the host boots
- Hot-add and managed hot-remove are supported
- No explicit support for Async removal of CXL devices; Async removal requires that root ports implement CXL Isolation (see [Section 12.3](#page-1005-2))

A switch that provides internal Endpoint functions is beyond the scope of this specification.

#### <span id="page-323-0"></span>7.2.1.2 Fabric Manager Boots First

In cases where the FM boots first (prior to host(s)), the switch is permitted to be initialized as described in the example shown in [Figure 7-5.](#page-323-1)

<span id="page-323-1"></span>**Figure 7-5. Example of CXL Switch Initialization when FM Boots First**

![](_page_323_Figure_5.jpeg)

- 1. FM boots while hosts are held in reset.
- 2. All attached DSPs link up and are bound to FM-owned PPBs.
- 3. DSPs link up and the switch notifies the FM using a managed hot-add notification.

<span id="page-324-0"></span>**Figure 7-6. Example of CXL Switch after Initialization Completes**

![](_page_324_Figure_3.jpeg)

As shown in the example above in [Figure 7-6](#page-324-0), the following steps are taken to configure the switch after initialization completes:

- 1. FM sends bind command BIND (VCS0, vPPB1, PHY\_PORT\_ID1) to the switch. The switch then configures virtual to physical binding.
- 2. Switch remaps vPPB virtual port numbers to physical port numbers.
  - Virtual port number is the index of the vPPB (as specified in the Bind vPPB command discussed in [Section 7.6.7.2.2](#page-361-1)) per virtual hierarchy.
- 3. Switch remaps vPPB connector definition (PERST#, PRSNT#) to physical connector.
- 4. Switch disables the link using PPB Link Disable.
- 5. At this point, all Physical downstream PPB functionality (e.g., Capabilities, etc.) maps directly to the vPPB including Link Disable, which releases the port for linkup.
- 6. The FM-owned PPB no longer exists for this port.
- 7. When the hosts boot, the switch is ready for enumeration.

#### <span id="page-325-0"></span>7.2.1.3 Fabric Manager and Host Boot Simultaneously

<span id="page-325-1"></span>**Figure 7-7. Example of Switch with Fabric Manager and Host Boot Simultaneously**

![](_page_325_Figure_4.jpeg)

In the case where the switch, FM, and host boot at the same time:

- 1. VCSs are statically defined.
- 2. DSP vPPBs within each VCS are unbound and presented to the host as Link Down.
- 3. Switch discovers downstream devices and presents them to the FM.
- 4. Host enumerates the VH and configures the DVSEC registers.
- 5. FM performs port binding to vPPBs.
- 6. Switch performs virtual to physical binding.
- 7. Each bound port results in a hot-add indication to the host.

<span id="page-326-1"></span>**Figure 7-8. Example of Simultaneous Boot after Binding**

![](_page_326_Figure_3.jpeg)

### <span id="page-326-0"></span>7.2.2 Sideband Signal Operation

The availability of slot sideband control signals is decided by the form-factor specifications. Any form factor can be supported, but if the form factor supports the signals listed in [Table 7-1,](#page-326-2) the signals must be driven by the switch or connected to the switch for correct operation.

All other sideband signals have no constraints and are supported exactly as in PCIe.

<span id="page-326-2"></span>**Table 7-1. CXL Switch Sideband Signal Requirements**

| Signal Name | Signal Description                                                                                     | Requirement                                                                              |  |
|-------------|--------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------|--|
| USP PERST#  | PCIe Reset provides a fundamental reset to<br>the VCS                                                  | This signal must be connected to the<br>switch if implemented                            |  |
| USP ATTN#   | Attention button indicates a request to the<br>host for a managed hot-remove of the switch             | If hot-remove of the switch is supported,<br>this signal must be generated by the switch |  |
| DSP PERST#  | PCIe Reset provides a power-on reset to the<br>downstream link partner                                 | This signal must be generated by the<br>switch if implemented                            |  |
| DSP PRSNT#  | Out-of-band Presence Detect indicates that a<br>device has been connected to the slot                  | This signal must be connected to the<br>switch if implemented                            |  |
| DSP ATTN#   | Attention button indicates a request to the<br>host for a managed hot-remove of the<br>downstream slot | If managed hot-remove is supported, this<br>signal must be connected to the switch       |  |

This list provides the minimum sideband signal set to support managed Hot-Plug. Other optional sidebands signals such as Attention LED, Power LED, Manual Retention Latch, Electromechanical Lock, etc. may also be used for managed Hot-Plug. The behavior of these sideband signals is identical to PCIe.

### <span id="page-327-0"></span>7.2.3 Binding and Unbinding

This section describes the details of Binding and Unbinding of CXL devices to a vPPB.

#### <span id="page-327-1"></span>7.2.3.1 Binding and Unbinding of a Single Logical Device Port

A Single Logical Device (SLD) port refers to a port that is bound to only one VCS. That port can be linked up with a PCIe device or a CXL Type 1, Type 2, or Type 3 SLD component. In general, the vPPB bound to the SLD port behaves the same as a PPB in a PCIe switch. An exception is that a vPPB can be unbound from any physical port. In this case the vPPB appears to the host as if it is in a Link Down state with no Presence Detect indication. If optional rebinding is desired, this switch must have an FM API support and FM connection. The Fabric Manager can bind any unused physical port to the unbound vPPB. After binding, all the vPPB port settings are applied to that physical port.

[Figure 7-9](#page-327-2) shows a switch with bound DSPs.

<span id="page-327-2"></span>**Figure 7-9. Example of Binding and Unbinding of an SLD Port**

![](_page_327_Figure_8.jpeg)

[Figure 7-10](#page-328-0) shows the state of the switch after the FM has executed an unbind command to vPPB2 in VCS0. Unbind of the vPPB causes the switch to assert Link Disable to the port. The port then becomes FM-owned and is controlled by the PPB settings for that physical port. Through the FM API, the FM has CXL.io access to each FM-owned SLD port or FM-owned LD within an MLD component. The FM can choose to prepare the logical device for rebinding by triggering FLR or CXL Reset. The switch prohibits any CXL.io access from the FM to a bound SLD port and any CXL.io access from the FM to a bound LD within an MLD component. The FM API does not support FM generation of CXL.cache or CXL.mem transactions to any port.

<span id="page-328-0"></span>**Figure 7-10. Example of CXL Switch Configuration after an Unbind Command**

![](_page_328_Figure_3.jpeg)

[Figure 7-11](#page-329-1) shows the state of the switch after the FM executes the bind command to connect VCS1.vPPB1 to the unbound physical port. The successful command execution results in the switch sending a hot-add indication to Host 1. Enumeration, configuration, and operation of the host and Type 3 device is identical to a hot-add of a device.

<span id="page-329-1"></span>**Figure 7-11. CXL Switch State after FM Bind Command Execution for SLD Device**

![](_page_329_Figure_2.jpeg)

![](_page_329_Figure_3.jpeg)

#### <span id="page-329-0"></span>7.2.3.2 Binding and Unbinding of a Pooled Device

A pooled device contains multiple Logical Devices so that traffic over the physical port can be associated with multiple DS vPPBs. The switch behavior for binding and unbinding of an MLD component is similar to that of an SLD component, but with some notable differences:

- 1. The physical link cannot be impacted by binding and unbinding of a Logical Device within an MLD component. Thus, PERST#, Hot Reset, and Link Disable cannot be asserted, and there must be no impact to the traffic of other VCSs during the bind or unbind commands.
- 2. The physical PPB for an MLD port is always owned by the FM. The FM is responsible for port link control, AER, DPC, etc., and manages it using the FM API.
- 3. The FM may need to manage the pooled device to change memory allocations, enable the LD, etc.

[Figure 7-12](#page-330-0) shows a CXL switch after boot and before binding of any LDs within the pooled device. Note that the FM is not a PCIe Root Port and that the switch is responsible for enumerating the FMLD after any physical reset since the switch is responsible for proxying commands from FM to the device. The PPB of an MLD port is always owned by the FM since the FM is responsible for configuration and error handling of the physical port. After linkup the FM is notified that it is a Type 3 pooled device.

<span id="page-330-0"></span>**Figure 7-12. Example of a CXL Switch before Binding of LDs within Pooled Device**

![](_page_330_Figure_3.jpeg)

The FM configures the pooled device for Logical Device 1 (LD 1) and sets its memory allocation, etc. The FM performs a bind command for the unbound vPPB 2 in VCS 0 to LD 1 in the Type 3 pooled device. The switch performs the virtual-to-physical translations such that all CXL.io and CXL.mem transactions that target vPPB 2 in VCS 0 are routed to the MLD port with LD-ID set to 1. Additionally, all CXL.io and CXL.mem transactions from LD 1 in the pooled device are routed according to the host configuration of VCS 0. After binding, the vPPB notifies the VCS 0 host of a hot-add the same as if it were binding a vPPB to an SLD port.

[Figure 7-13](#page-331-0) shows the state of the switch after binding LD 1 to VCS 0.

<span id="page-331-0"></span>**Figure 7-13. Example of a CXL Switch after Binding of LD-ID 1 within Pooled Device**

![](_page_331_Figure_4.jpeg)

The FM configures the pooled device for Logical Device 0 (LD 0) and sets its memory allocation, etc. The FM performs a bind command for the unbound vPPB 1 in VCS 1 to LD 0 in the Type 3 pooled device. The switch performs the virtual to physical translations such that all CXL.io and CXL.mem transactions targeting the vPPB in VCS 1 are routed to the MLD port with LD-ID set to 0. Additionally, all CXL.io and CXL.mem transactions from LD-ID = 0 in the pooled device are routed to the USP of VCS 1. After binding, the vPPB notifies the VCS 1 host of a hot-add the same as if it were binding a vPPB to an SLD port.

[Figure 7-14](#page-332-1) shows the state of the switch after binding LD 0 to VCS 1.

<span id="page-332-1"></span>**Figure 7-14. Example of a CXL Switch after Binding of LD-IDs 0 and 1 within Pooled Device**

![](_page_332_Figure_4.jpeg)

After binding LDs to vPPBs, the switch behavior is different from a bound SLD Port with respect to control, status, error notification, and error handling. [Section 7.3.4](#page-342-5) describes the differences in behavior for all bits within each register.

### <span id="page-332-0"></span>7.2.4 PPB and vPPB Behavior for MLD Ports

An MLD port provides a virtualized interface such that multiple vPPBs can access LDs over a shared physical interface. As a result, the characteristics and behavior of a vPPB that is bound to an MLD port are different than the behavior of a vPPB that is bound to an SLD port. This section defines the differences between them. If not mentioned in this section, the features and behavior of a vPPB that is bound to an MLD port are the same as those for a vPPB that is bound to an SLD port.

This section uses the following terminology:

- Hardwire to 0 refers to status and optional control register bits that are initialized to 0. Writes to these bits have no effect.
- The term 'Read/Write with no Effect' refers to control register bits where writes are recorded but have no effect on operation. Reads to those bits reflect the previously written value or the initialization value if it has not been changed since initialization.

#### <span id="page-333-0"></span>7.2.4.1 MLD Type 1 Configuration Space Header

<span id="page-333-3"></span>**Table 7-2. MLD Type 1 Configuration Space Header**

| Register                   | Register Fields                                                           | FM-owned PPB  | All Other vPPBs                               |  |
|----------------------------|---------------------------------------------------------------------------|---------------|-----------------------------------------------|--|
|                            | Parity Error Response Enable                                              | Supported     | Hardwire to 0s                                |  |
| Bridge Control<br>Register | SERR# Enable Supported Read/Write with no effect                          |               | Read/Write with no effect                     |  |
|                            | ISA Enable                                                                | Not supported | Not supported                                 |  |
|                            | Secondary Bus Reset<br>(see Section 7.5 for SBR<br>details for MLD ports) | Supported     | Read/Write with no effect. Optional FM Event. |  |

#### <span id="page-333-1"></span>7.2.4.2 MLD PCIe-compatible Configuration Registers

<span id="page-333-4"></span>**Table 7-3. MLD PCIe-compatible Configuration Registers**

| Register/Capability<br>Structure | Capability Register Fields | FM-owned PPB                          | All vPPBs Bound to<br>the MLD Port |
|----------------------------------|----------------------------|---------------------------------------|------------------------------------|
| Command Register                 | I/O Space Enable           | Hardwire to 0s                        | Hardwire to 0s                     |
|                                  | Memory Space Enable        | Supported                             | Supported per vPPB                 |
|                                  | Bus Master Enable          | Supported                             | Supported per vPPB                 |
|                                  | Parity Error Response      | Supported                             | Read/Write with no effect          |
|                                  | SERR# Enable               | Supported                             | Supported per vPPB                 |
|                                  | Interrupt Disable          | Supported                             | Hardwire to 0s                     |
| Status Register                  | Interrupt Status           | Hardwire to 0 (INTx is not supported) | Hardwire to 0s                     |
|                                  | Master Data Parity Error   | Supported                             | Hardwire to 0s                     |
|                                  | Signaled System Error      | Supported                             | Supported per vPPB                 |
|                                  | Detected Parity Error      | Supported                             | Hardwire to 0s                     |

#### <span id="page-333-2"></span>7.2.4.3 MLD PCIe Capability Structure

<span id="page-333-5"></span>**Table 7-4.** MLD PCIe Capability Structure (Sheet 1 of 3)**

| Register/Capability<br>Structure | Capability Register Fields                | FM-owned PPB                                                                                                         | All vPPBs Bound to the MLD Port |
|----------------------------------|-------------------------------------------|----------------------------------------------------------------------------------------------------------------------|---------------------------------|
| Device Capabilities<br>Register  | Max_Payload_Size Supported                | Configured by the FM to<br>the max value supported<br>by switch hardware and<br>min value configured in<br>all vPPBs | Mirrors PPB                     |
|                                  | Phantom Functions Supported               | Hardwire to 0s                                                                                                       | Hardwire to 0s                  |
|                                  | Extended Tag Field Supported              | Supported                                                                                                            | Mirrors PPB                     |
| Device Control Register          | Max_Payload_Size                          | Configured by the FM to<br>Max_Payload Size<br>Supported                                                             | Read/Write with no effect       |
| Link Capabilities<br>Register    | Link Bandwidth Notification<br>Capability | Hardwire to 0s                                                                                                       | Hardwire to 0s                  |

**Table 7-4. MLD PCIe Capability Structure (Sheet 2 of 3)** 

| Register/Capability<br>Structure  | Capability Register Fields                    | FM-owned PPB               | All vPPBs Bound to the MLD Port                                                         |
|-----------------------------------|-----------------------------------------------|----------------------------|-----------------------------------------------------------------------------------------|
| Link Capabilities                 | ASPM Support                                  | No LOs support             | No LOs support                                                                          |
|                                   | Clock Power Management                        | No PM L1 Substates support | No PM L1 Substates support                                                              |
|                                   | ASPM Control                                  | Supported                  | Switch only enables ASPM if all vPPBs that are bound to this MLD have enabled ASPM      |
|                                   | Link Disable                                  | Supported                  | Switch handles it as an unbind by discarding all traffic to/from this LD-ID             |
|                                   | Retrain Link                                  | Supported                  | Read/Write with no effect                                                               |
| 1                                 | Common Clock Configuration                    | Supported                  | Read/Write with no effect                                                               |
| Link Control                      | Extended Synch                                | Supported                  | Read/Write with no effect                                                               |
| Link Control                      | Hardware Autonomous Width Disable             | Supported                  | Read/Write with no effect                                                               |
|                                   | Link Bandwidth Management<br>Interrupt Enable | Supported                  | Read/Write with no effect                                                               |
|                                   | Link Autonomous Bandwidth<br>Interrupt Enable | Supported                  | Supported per vPPB. Each host can be notified of autonomous speed change                |
|                                   | DRS Signaling Control                         | Supported                  | Switch sends DRS after receiving DRS on the link and after binding of the vPPB to an LD |
|                                   | Current Link Speed                            | Supported                  | Mirrors PPB                                                                             |
|                                   | Negotiated Link Width                         | Supported                  | Mirrors PPB                                                                             |
| 1                                 | Link Training                                 | Supported                  | Hardwire to 0s                                                                          |
| Link Status register              | Slot Clock Configuration                      | Supported                  | Mirrors PPB                                                                             |
|                                   | Data Link Layer Active                        | Supported                  | Mirrors PPB                                                                             |
|                                   | Link Autonomous Bandwidth<br>Status           | Supported                  | Supported per vPPB                                                                      |
| Slot Capabilities                 | Hot-Plug Surprise                             | Hardwire to 0s             | Hardwired to 0s                                                                         |
| Register                          | Physical Slot Number                          | Supported                  | Mirrors PPB                                                                             |
| Slot Status Register              | Attention Button Pressed                      | Supported                  | Mirrors PPB or is set by the switch on unbind                                           |
|                                   | Power Fault Detected                          | Supported                  | Mirrors PPB                                                                             |
|                                   | MRL Sensor Changed                            | Supported                  | Mirrors PPB                                                                             |
|                                   | Presence Detect Changed                       | Supported                  | Mirrors PPB or is set by the switch on unbind                                           |
|                                   | MRL Sensor State                              | Supported                  | Mirrors PPB                                                                             |
|                                   | Presence Detect State                         | Supported                  | Mirrors PPB or set by the switch on bind or unbind                                      |
|                                   | Electromechanical Interlock<br>Status         | Supported                  | Mirrors PPB                                                                             |
|                                   | Data Link Layer State Changed                 | Supported                  | Mirrors PPB or set by the switch on bind or unbind                                      |
| Device Capabilities 2<br>Register | OBFF Supported                                | Hardwire to 0s             | Hardwire to 0s                                                                          |

Table 7-4. MLD PCIe Capability Structure (Sheet 3 of 3)

| Table 7-4. MLD Pole Capability Structure (Sheet 3 of 3) |                                             |                |                                                                                         |
|---------------------------------------------------------|---------------------------------------------|----------------|-----------------------------------------------------------------------------------------|
| Register/Capability<br>Structure                        | Capability Register Fields                  | FM-owned PPB   | All vPPBs Bound to the MLD Port                                                         |
| Device Control 2<br>Register                            | ARI Forwarding Enable                       | Supported      | Supported per vPPB                                                                      |
|                                                         | Atomic Op Egress Blocking                   | Supported      | Mirrors PPB. Read/Write with no effect                                                  |
|                                                         | LTR Mechanism Enabled                       | Supported      | Supported per vPPB                                                                      |
|                                                         | Emergency Power Reduction<br>Request        | Supported      | Read/Write with no effect. Optional FM notification.                                    |
|                                                         | End-End TLP Prefix Blocking                 | Supported      | Mirrors PPB. Read/Write with no effect                                                  |
|                                                         | Target Link Speed                           | Supported      | Read/Write with no effect. Optional FM notification.                                    |
|                                                         | Enter Compliance                            | Supported      | Read/Write with no effect                                                               |
| Link Control 2 Register                                 | Hardware Autonomous Speed<br>Disable        | Supported      | Read/Write with no effect. Optional FM notification.                                    |
|                                                         | Selectable De-emphasis                      | Supported      | Read/Write with no effect                                                               |
|                                                         | Transmit Margin                             | Supported      | Read/Write with no effect                                                               |
|                                                         | Enter Modified Compliance                   | Supported      | Read/Write with no effect                                                               |
|                                                         | Compliance SOS                              | Supported      | Read/Write with no effect                                                               |
|                                                         | Compliance Preset/De-<br>emphasis           | Supported      | Read/Write with no effect                                                               |
|                                                         | Current De-emphasis Level                   | Supported      | Mirrors PPB                                                                             |
|                                                         | Equalization 8.0 GT/s Complete              | Supported      | Mirrors PPB                                                                             |
| Link Status 2 Register                                  | Equalization 8.0 GT/s Phase 1<br>Successful | Supported      | Mirrors PPB                                                                             |
|                                                         | Equalization 8.0 GT/s Phase 2<br>Successful | Supported      | Mirrors PPB                                                                             |
|                                                         | Equalization 8.0 GT/s Phase 3<br>Successful | Supported      | Mirrors PPB                                                                             |
|                                                         | Link Equalization Request 8.0 GT/s          | Supported      | Read/Write with no effect                                                               |
|                                                         | Retimer Presence Detected                   | Supported      | Mirrors PPB                                                                             |
|                                                         | Two Retimers Presence<br>Detected           | Supported      | Mirrors PPB                                                                             |
|                                                         | Crosslink Resolution                        | Hardwire to 0s | Hardwire to 0s                                                                          |
|                                                         | Downstream Component<br>Presence            | Supported      | Reflects the binding state of the vPPB                                                  |
|                                                         | DRS Message Received                        | Supported      | Switch sends DRS after receiving DRS on the link and after binding of the vPPB to an LD |

#### <span id="page-336-0"></span>7.2.4.4 MLD PPB Secondary PCIe Capability Structure

All fields in the Secondary PCIe Capability Structure for a Virtual PPB shall behave identically to PCIe except the following:

<span id="page-336-2"></span>**Table 7-5.** MLD Secondary PCIe Capability Structure**

| Register/Capability<br>Structure           | Capability Register Fields                    | FM-owned PPB | All vPPBs Bound to<br>the MLD Port |
|--------------------------------------------|-----------------------------------------------|--------------|------------------------------------|
| Link Control 3 Register                    | Perform Equalization                          | Supported    | Read/Write with no effect          |
|                                            | Link Equalization Request<br>Interrupt Enable | Supported    | Read/Write with no effect          |
|                                            | Enable Lower SKP OS<br>Generation Vector      | Supported    | Read/Write with no effect          |
| Lane Error Status<br>Register              | All fields                                    | Supported    | Mirrors PPB                        |
| Lane Equalization<br>Control Register      | All fields                                    | Supported    | Read/Write with no effect          |
| Data Link Feature<br>Capabilities Register | All fields                                    | Supported    | Hardwire to 0s                     |
| Data Link Feature<br>Status Register       | All fields                                    | Supported    | Hardwire to 0s                     |

#### <span id="page-336-1"></span>7.2.4.5 MLD Physical Layer 16.0 GT/s Extended Capability

All fields in the Physical Layer 16.0 GT/s Extended Capability Structure for a Virtual PPB shall behave identically to PCIe except the following:

<span id="page-336-3"></span>**Table 7-6. MLD Physical Layer 16.0 GT/s Extended Capability**

| Register/Capability<br>Structure                                       | Capability Register Fields                      | FM-owned PPB | All vPPBs Bound to<br>the MLD Port |
|------------------------------------------------------------------------|-------------------------------------------------|--------------|------------------------------------|
| 16.0 GT/s Status<br>Register                                           | All fields                                      | Supported    | Mirrors PPB                        |
| 16.0 GT/s Local Data<br>Parity Mismatch Status<br>Register             | Local Data Parity Mismatch<br>Status Register   | Supported    | Mirrors PPB                        |
| 16.0 GT/s First Retimer<br>Data Parity Mismatch<br>Status Register     | First Retimer Data Parity<br>Mismatch Status    | Supported    | Mirrors PPB                        |
| 16.0 GT/s Second<br>Retimer Data Parity<br>Mismatch Status<br>Register | Second Retimer Data Parity<br>Mismatch Status   | Supported    | Mirrors PPB                        |
| 16.0 GT/s Lane<br>Equalization Control<br>Register                     | Downstream Port 16.0 GT/s<br>Transmitter Preset | Supported    | Mirrors PPB                        |

#### <span id="page-337-0"></span>7.2.4.6 MLD Physical Layer 32.0 GT/s Extended Capability

<span id="page-337-2"></span>**Table 7-7. MLD Physical Layer 32.0 GT/s Extended Capability**

| Register/Capability<br>Structure                   | Capability Register Fields                               | FM-owned PPB | All vPPBs Bound to the MLD Port |
|----------------------------------------------------|----------------------------------------------------------|--------------|---------------------------------|
| 32.0 GT/s Capabilities<br>Register                 | All fields                                               | Supported    | Mirrors PPB                     |
| 32.0 GT/s Control<br>Register                      | All fields                                               | Supported    | Read/Write with no effect       |
| 32.0 GT/s Status<br>Register                       | Link Equalization Request 32.0 GT/s                      | Supported    | Read/Write with no effect       |
|                                                    | All fields except Link<br>Equalization Request 32.0 GT/s | Supported    | Mirrors PPB                     |
| Received Modified TS<br>Data 1 Register            | All fields                                               | Supported    | Mirrors PPB                     |
| Received Modified TS<br>Data 2 Register            | All fields                                               | Supported    | Mirrors PPB                     |
| Transmitted Modified TS Data 1 Register            | All fields                                               | Supported    | Mirrors PPB                     |
| 32.0 GT/s Lane<br>Equalization Control<br>Register | Downstream Port 32.0 GT/s<br>Transmitter Preset          | Supported    | Mirrors PPB                     |

#### <span id="page-337-1"></span>7.2.4.7 MLD Lane Margining at the Receiver Extended Capability

<span id="page-337-3"></span>**Table 7-8. MLD Lane Margining at the Receiver Extended Capability**

| Register/Capability<br>Structure   | Capability Register<br>Fields | FM-owned PPB | All vPPBs Bound to<br>the MLD Port                                  |
|------------------------------------|-------------------------------|--------------|---------------------------------------------------------------------|
| Margining Port Status<br>Register  | All fields                    | Supported    | Always indicates Margining<br>Ready and Margining<br>Software Ready |
| Margining Lane Control<br>Register | All fields                    | Supported    | Read/Write with no effect                                           |

### <span id="page-338-0"></span>7.2.5 MLD ACS Extended Capability

CXL.io Requests and Completions are routed to the USP.

<span id="page-338-3"></span>Table 7-9. MLD ACS Extended Capability

| Register/Capability<br>Structure | Capability Register Fields              | FM-owned PPB   | All vPPBs Bound to the MLD Port                        |
|----------------------------------|-----------------------------------------|----------------|--------------------------------------------------------|
| ACS Capability Register          | All fields                              | Supported      | Supported because a vPPB can be bound to any port type |
|                                  | ACS Source Validation Enable            | Hardwire to 0  | Read/Write with no effect                              |
|                                  | ACS Translation Blocking Enable         | Hardwire to 0  | Read/Write with no effect                              |
| ACS Control Register             | ACS P2P Request Redirect Enable         | Hardwire to 1  | Read/Write with no effect                              |
|                                  | ACS P2P Completion Redirect Enable      | Hardwire to 1  | Read/Write with no effect                              |
|                                  | ACS Upstream Forwarding Enable          | Hardwire to 0  | Read/Write with no effect                              |
|                                  | ACS P2P Egress Control Enable           | Hardwire to 0  | Read/Write with no effect                              |
|                                  | ACS Direct Translated P2P Enable        | Hardwire to 0  | Read/Write with no effect                              |
|                                  | ACS I/O Request Blocking Enable         | Hardwire to 0  | Read/Write with no effect                              |
|                                  | ACS DSP Memory Target Access<br>Control | Hardwire to 0s | Read/Write with no effect                              |
|                                  | ACS Unclaimed Request Redirect Control  | Hardwire to 0  | Read/Write with no effect                              |

### <span id="page-338-1"></span>7.2.6 MLD PCIe Extended Capabilities

All fields in the PCIe Extended Capability structures for a vPPB shall behave identically to PCIe.

### <span id="page-338-2"></span>7.2.7 MLD Advanced Error Reporting Extended Capability

<span id="page-338-4"></span>AER in an MLD port is separated into Triggering, Notifications, and Reporting. Triggering and AER Header Logging is handled at switch ingress and egress using switch-vendor-specific means. Notification is also switch-vendor specific, but it results in the vPPB logic for all vPPBs that are bound to the MLD port being informed of the AER errors that have been triggered. The vPPB logic is responsible for generating the AER status and error messages for each vPPB based on the AER Mask and Severity registers.

vPPBs that are bound to an MLD port support all the AER Mask and Severity configurability; however, some of the Notifications are suppressed to avoid confusion.

The PPB has its own AER Mask and Severity registers and the FM is notified of error conditions based on the Event Notification settings.

Errors that are not vPPB specific are provided to the host with a header log containing all 1s data. The hardware header log is provided only to the FM through the PPB.

[Table 7-10](#page-339-1) lists the AER Notifications and their routing indications for PPBs and vPPBs.

<span id="page-339-1"></span>**Table 7-10. MLD Advanced Error Reporting Extended Capability**

| Hardware Triggers | AER Error                                        | FM-owned PPB | All vPPBs Bound to<br>the MLD Port         |
|-------------------|--------------------------------------------------|--------------|--------------------------------------------|
|                   | Data Link Protocol Error                         | Supported    | Supported per vPPB                         |
|                   | Surprise Down Error                              | Supported    | Supported per vPPB                         |
|                   | Poisoned TLP Received                            | Supported    | Hardwire to 0                              |
|                   | Flow Control Protocol Error                      | Supported    | Supported per vPPB                         |
|                   | Completer Abort                                  | Supported    | Supported to the vPPB<br>that generated it |
|                   | Unexpected Completion                            | Supported    | Supported to the vPPB<br>that received it  |
|                   | Receiver Overflow                                | Supported    | Supported per vPPB                         |
|                   | Malformed TLP                                    | Supported    | Supported per vPPB                         |
|                   | ECRC Error                                       | Supported    | Hardwire to 0                              |
|                   | Unsupported Request                              | Supported    | Supported per vPPB                         |
|                   | ACS Violation                                    | Supported    | Hardwire to 0                              |
|                   | Uncorrectable Internal Error                     | Supported    | Supported per vPPB                         |
| AER Notifications | MC1 Blocked                                      | Supported    | Hardwire to 0                              |
|                   | Atomic Op Egress Block                           | Supported    | Hardwire to 0                              |
|                   | E2E TLP Prefix Block                             | Supported    | Hardwire to 0                              |
|                   | Poisoned TLP Egress block                        | Supported    | Hardwire to 0                              |
|                   | Bad TLP (correctable)                            | Supported    | Supported per vPPB                         |
|                   | Bad DLLP (correctable)                           | Supported    | Supported per vPPB                         |
|                   | Replay Timer Timeout<br>(correctable)            | Supported    | Supported per vPPB                         |
|                   | Replay Number Rollover<br>(correctable)          | Supported    | Supported per vPPB                         |
|                   | Other Advisory Non-Fatal<br>(correctable)        | Supported    | Supported per vPPB                         |
|                   | Corrected Internal Error Status<br>(correctable) | Supported    | Supported per vPPB                         |
|                   | Header Log Overflow Status<br>(correctable)      | Supported    | Supported per vPPB                         |

<sup>1.</sup> Refers to Multicast.

### <span id="page-339-0"></span>7.2.8 MLD DPC Extended Capability

Downstream Port Containment has special behavior for an MLD Port. The FM configures the AER Mask and Severity registers in the PPB and also configures the AER Mask and Severity registers in the FMLD in the pooled device. As in an SLD port an unmasked uncorrectable error detected in the PPB and an ERR\_NONFATAL and/or ERR\_FATAL received from the FMLD can trigger DPC.

Continuing the model of the ultimate receiver being the entity that detects and reports errors, the ERR\_FATAL and ERR\_NONFATAL messages sent by a Logical Device can trigger a virtual DPC in the PPB. When a virtual DPC is triggered, the switch discards all traffic received from and transmitted to that specific LD. The LD remains bound to the vPPB and the FM is also notified. Software triggered DPC also triggers virtual DPC on a vPPB.

When the DPC trigger is cleared the switch autonomously allows passing of traffic to/from the LD. Reporting of the DPC trigger to the host is identical to PCIe.

<span id="page-340-3"></span>**Table 7-11. MLD PPB DPC Extended Capability**

| Register/ Capability<br>Structure | Capability Register Fields | FM-owned PPB | All vPPBs Bound<br>to the MLD Port                                                  |
|-----------------------------------|----------------------------|--------------|-------------------------------------------------------------------------------------|
| DPC Control Register              | DPC Trigger Enable         | Supported    | Switch internally detected unmasked uncorrectable errors do not trigger virtual DPC |
|                                   | DPC Trigger Reason         | Supported    | Unmasked uncorrectable error is not a valid value                                   |

### <span id="page-340-0"></span>7.2.9 Switch Mailbox CCI

CXL Switch Mailbox CCIs optional. They are exposed as PCIe Endpoints with a Type 0 configuration space. In Single VCS and Multiple VCS, the Mailbox CCI is optional. If implemented, the Mailbox CCI shall be exposed to the Host in one of two possible configurations. In the first, it is exposed as an additional PCIe function in the Upstream Switch Port, as illustrated in Figure 7-15.

<span id="page-340-1"></span>**Figure 7-15. Multi-function Upstream vPPB**

**Figure 7-16.**

![](_page_340_Figure_8.jpeg)

Switch Mailbox CCIs may also be exposed in a VCS with no vPPBs. In this configuration, the Mailbox CCI device is the only PCIe function that is present in the Upstream Port, as illustrated in Figure 7-16.

<span id="page-340-2"></span>Figure 7-16. Single-function Mailbox CCI

![](_page_340_Figure_11.jpeg)

## <span id="page-341-0"></span>7.3 CXL.io, CXL.cachemem Decode and Forwarding

### <span id="page-341-1"></span>7.3.1 CXL.io

Within a VCS, the CXL.io traffic must obey the same request, completion, address decode, and forwarding rules for a Switch as defined in PCIe Base Specification. There are additional decode rules that are defined to support an eRCD connected to a switch (see [Section 9.12.4\)](#page-825-3).

#### <span id="page-341-2"></span>7.3.1.1 CXL.io Decode

When a TLP is decoded by a PPB, it determines the destination PPB to route the TLP based on the rules defined in PCIe Base Specification. Unless specified otherwise, all rules defined in PCIe Base Specification apply for routing of CXL.io TLPs. TLPs must be routed to PPBs within the same VCS. Routing of TLPs to and from an FM-owned PPB need to follow additional rules as defined in [Section 7.2.3.](#page-327-0) P2P inside a Switch complex is limited to PPBs within a VCS.

#### <span id="page-341-3"></span>7.3.1.2 RCD Support

RCDs are not supported behind ports that are configured to operate as FM-owned PPBs. When connected behind a switch, RCDs must appear to software as RCiEP devices. The mechanism defined in this section enables this functionality.

<span id="page-341-5"></span>**Figure 7-17. CXL Switch with a Downstream Link Auto-negotiated to Operate in RCD Mode**

![](_page_341_Figure_10.jpeg)

The CXL Extensions DVSEC for Ports (see [Section 8.1.5\)](#page-516-4) defines the alternate MMIO and Bus Range Decode windows for forwarding of requests to eRCDs connected behind a Downstream Port.

### <span id="page-341-4"></span>7.3.2 CXL.cache

If the switch does not support CXL.cache protocol enhancements that enable multidevice scaling (as described in [Section 8.2.4.28\)](#page-592-1), only one of the CXL SLD ports in the VCS is allowed to be enabled to support Type 1 devices or Type 2 devices. Requests and Responses received on the USP are routed to the associated DSP and vice-versa. Therefore, additional decode registers are not required for CXL.cache for such switches.

![](_page_342_Picture_1.jpeg)

If the switch supports CXL.cache protocol enhancements that enable multi-device scaling, more than one of the CXL SLD ports in the VCS can be configured to support Type 1 devices or Type 2 devices. [Section 9.15.2](#page-855-4) and [Section 9.15.3](#page-856-3) describe how such a CXL switch routes CXL.cache traffic.

CXL.cache is not supported over FM-owned PPBs.

#### <span id="page-342-0"></span>7.3.2.1 CXL.Cache Reserved bit forwarding

A switch shall forward 256B Flit messages reserved bits between the ingress port and the egress port. Both HBR and PBR formats are defined for 256B flit messages where a switch can translate between those formats. When performing the translation between HBR and PBR formats defined for 256B flits the Reserved bits shall be preserved. When a switch with 256B flit capability sends to a port with 68B flit format the Reserved bits shall be set to zero. Similarly, messages received as 68B flit formats shall never have reserved bits forwarded to a port with 256B flit messages.

*Note:* The reason for forwarding of reserved bits is to allow new features to be supported without requiring changes to existing switches. The reason for not forwarding in 68B flit format is that new features are expected to be added only to 256B flit formats so there is no need to support the complexity of translating reserved bits to/from 68B flits.

### <span id="page-342-1"></span>7.3.3 CXL.mem

The HDM Decode DVSEC capability contains registers that define the Memory Address Decode Ranges for Memory. CXL.mem requests originate from the Host/RP and flow downstream to the Devices through the switch. CXL.mem responses originate from the Device and flow upstream to the RP.

#### <span id="page-342-2"></span>7.3.3.1 CXL.mem Request Decode

All CXL.mem Requests received by the USP target one of the Downstream PPBs within the VCS. The address decode registers in the VCS determine the downstream VCS PPB to route the request. The VCS PPB may be a VCS-owned PPB or an FM-owned PPB. See [Section 7.3.4](#page-342-5) for additional routing rules.

#### <span id="page-342-3"></span>7.3.3.2 CXL.mem Response Decode

CXL.mem Responses received by the DSP target one and only one Upstream Port. For VCS-owned PPB the responses are routed to the Upstream Port of that VCS. Responses received on an FM-owned PPB go through additional decode rules to determine the VCS ID to route the requests to. See [Section 7.3.4](#page-342-5) for additional routing rules.

#### <span id="page-342-4"></span>7.3.3.3 CXL.Mem Reserved bit forwarding

CXL.mem follows the same rules as CXL.cache as defined in [Section 7.3.2.1](#page-342-0).

### <span id="page-342-5"></span>7.3.4 FM-owned PPB CXL Handling

All PPBs are FM-owned. A PPB can be connected to a port that is disconnected or linked up. SLD components can be bound to a host or unbound. Unbound SLD components can be accessed by the FM using CXL.io transactions via the FM API. LDs within an MLD component can be bound to a host or unbound. Unbound LDs are FM-owned and can be accessed through the switch using CXL.io transactions via the FM API.

For all CXL.io transactions driven by the FM API, the switch acts as a virtual Root Complex for PPBs and Endpoints. The switch is responsible for enumerating the functions associated with that port and sending/receiving CXL.io traffic.

## <span id="page-343-0"></span>7.4 CXL Switch PM

### <span id="page-343-1"></span>7.4.1 CXL Switch ASPM L1

ASPM L1 for switch Ports is as defined in [Chapter 10.0.](#page-878-6)

### <span id="page-343-2"></span>7.4.2 CXL Switch PCI-PM and L2

A vPPB in a VCS operates the same as a PCIe vPPB for handling of PME messages.

### <span id="page-343-3"></span>7.4.3 CXL Switch Message Management

CXL VDMs are of the "Local - Terminate at Receiver" type. When a switch is present in the hierarchy, the switch implements the message aggregation function and therefore all Host-generated messages terminate at the switch. The switch aggregation function is responsible for regenerating these messages on the Downstream Port. All messages and responses generated by the directly attached CXL components are aggregated and consolidated by the DSP and consolidated messages or responses are generated by the USP.

The PM message credit exchanges occur between the Host and Switch Aggregation port, and separately between the Switch Aggregation Port and device.

<span id="page-343-5"></span>**Table 7-12. CXL Switch Message Management**

| Message Type         | Type             | Switch Message Aggregation and<br>Consolidation Responsibility                      |  |
|----------------------|------------------|-------------------------------------------------------------------------------------|--|
| PM Reset Messages    |                  |                                                                                     |  |
| Sx Entry             | Host Initiated   | Host-generated requests terminate at<br>Upstream Port, broadcast messages to all    |  |
| GPF Phase 1 Request  |                  | ports within VCS hierarchy                                                          |  |
| GPF Phase 2 Request  |                  |                                                                                     |  |
| PM Reset Acknowledge |                  |                                                                                     |  |
| Sx Entry             | Device Responses | Device-generated responses terminate at<br>Downstream Port within VCS hierarchy.    |  |
| GPF Phase 1 Response |                  | Switch aggregates responses from all other<br>connected ports within VCS hierarchy. |  |
| GPF Phase 2 Response |                  |                                                                                     |  |

## <span id="page-343-4"></span>7.5 CXL Switch RAS

**Figure 7-18.**

<span id="page-343-6"></span>**Table 7-13. CXL Switch RAS (Sheet 1 of 2)**

| Triggering Action               | Description                 | Switch Action for<br>Non-pooled Devices | Switch Action for<br>Pooled Devices                                                                                             |
|---------------------------------|-----------------------------|-----------------------------------------|---------------------------------------------------------------------------------------------------------------------------------|
| Switch boot                     | Optional power-on reset pin | Assert PERST#<br>Deassert PERST#        | Assert PERST#<br>Deassert PERST#                                                                                                |
| Upstream PERST# assert          | VCS fundamental reset       | Send Hot Reset                          | Write to MLD DVSEC to trigger LD<br>Hot Reset of the associated LD<br>Note: Only the FMLD provides<br>the MLD DVSEC capability. |
| FM issues port reset<br>command | Reset of an FM-owned DSP    | Send Hot Reset                          | Send Hot Reset                                                                                                                  |
| PPB Secondary Bus Reset         | Reset of an FM-owned DSP    | Send Hot Reset                          | Write to MLD DVSEC to trigger LD<br>Hot Reset of all LDs                                                                        |

Table 7-13. CXL Switch RAS (Sheet 2 of 2)

| Triggering Action               | Description           | Switch Action for<br>Non-pooled Devices | Switch Action for<br>Pooled Devices                             |
|---------------------------------|-----------------------|-----------------------------------------|-----------------------------------------------------------------|
| USP receives Hot Reset          | VCS fundamental reset | Send Hot Reset                          | Write to MLD DVSEC to trigger LD Hot Reset of the associated LD |
| USP vPPB Secondary Bus<br>Reset | VCS US SBR            | Send Hot Reset                          | Write to MLD DVSEC to trigger LD Hot Reset of the associated LD |
| DSP vPPB Secondary Bus<br>Reset | VCS DS SBR            | Send Hot Reset                          | Write to MLD DVSEC to trigger LD Hot Reset of the associated LD |
| Host writes FLR                 | Device FLR            | No switch involvement                   | No switch involvement                                           |
| Switch watchdog timeout         | Switch fatal error    | Equivalent to power-on reset            | Equivalent to power-on reset                                    |

Because the MLD DVSEC only exists in the FMLD, the switch must use the FM LD-ID in the CXL.io configuration write transaction when triggering LD reset.

## <span id="page-344-0"></span>7.6 Fabric Manager Application Programming Interface

This section describes the Fabric Manager Application Programming Interface.

### <span id="page-344-1"></span>7.6.1 CXL Fabric Management

CXL devices can be configured statically or dynamically via a Fabric Manager (FM), an external logical process that queries and configures the system's operational state using the FM commands defined in this specification. The FM is defined as the logical process that decides when reconfiguration is necessary and initiates the commands to perform configurations. It can take any form, including, but not limited to, software running on a host machine, embedded software running on a BMC, embedded firmware running on another CXL device or CXL switch, or a state machine running within the CXL device itself.

### <span id="page-344-2"></span>7.6.2 Fabric Management Model

CXL devices are configured by FMs through the Fabric Manager Application Programming Interface (FM API) command sets, as defined in Section 8.2.10.10, through a CCI. A CCI is exposed through a device's Mailbox registers (see Section 8.2.9.4) or through an MCTP-capable interface. See Section 9.19 for details on the CCI processing of these commands.

<span id="page-345-0"></span>Figure 7-18. Example of Fabric Management Model

![](_page_345_Figure_3.jpeg)

FMs issue request messages and CXL devices issue response messages. CXL components may also issue the "Event Notification" request if notifications are supported by the component and the FM has requested notifications from the component using the Set MCTP Event Interrupt Policy command. See Section 7.6.3 for transport protocol details.

The following list provides a number of examples of connectivity between an FM and a component's CCI, but should not be considered a complete list:

- An FM directly connected to a CXL device through any MCTP-capable interconnect can issue FM commands directly to the device. This includes delivery over MCTPcapable interfaces such as SMBus as well as VDM delivery over a standard PCIe tree topology where the responder is mapped to a CXL attached device.
- An FM directly connected to a CXL switch may use the switch to tunnel FM commands to MLD components directly attached to the switch. In this case, the FM issues the "Tunnel Management Command" command to the switch specifying the switch port to which the device is connected. Responses are returned to the FM by the switch. In addition to MCTP message delivery, the FM command set provides the FM with the ability to have the switch proxy config cycles and memory accesses to a Downstream Port on the FM's behalf.
- An FM or part of the overall FM functionality may be embedded within a CXL component. The communication interface between such an embedded FM FW module and the component hardware is considered a vendor implementation detail and is not covered in this specification.

### <span id="page-346-0"></span>7.6.3 CCI Message Format and Transport Protocol

<span id="page-346-4"></span><span id="page-346-3"></span>CCI commands are transmitted across MCTP-capable interconnects as MCTP messages using the format defined in [Figure 7-19](#page-346-1) and listed in [Table 7-14.](#page-346-2)

<span id="page-346-1"></span>**Figure 7-19. CCI Message Format**

![](_page_346_Picture_5.jpeg)

<span id="page-346-2"></span>**Table 7-14. CCI Message Format**

| Byte<br>Offset | Length in<br>Bytes | Description                                                                                                                                                                                                                                                                              |
|----------------|--------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h             | 1                  | •<br>Bits[3:0]: Message Category: Type of CCI message:<br>— 0h = Request<br>— 1h = Response<br>— All other encodings are reserved<br>•<br>Bits[7:4]: Reserved                                                                                                                            |
| 1h             | 1                  | Message Tag: Tag number assigned to request messages by the Requester<br>used to track response messages when multiple request messages are<br>outstanding. Response messages shall use the tag number from the<br>corresponding Request message.                                        |
| 2h             | 1                  | Reserved                                                                                                                                                                                                                                                                                 |
| 3h             | 2                  | Command Opcode[15:0]: As defined in Table 8-49, Table 8-141, and<br>Table 8-230.                                                                                                                                                                                                         |
| 5h             | 2                  | Message Payload Length[15:0]: Expressed in bytes. As defined in<br>Table 8-49, Table 8-141, and Table 8-230.                                                                                                                                                                             |
| 7h             | 1                  | •<br>Bits[4:0]: Message Payload Length[20:16]: Expressed in bytes. As<br>defined in Table 8-49, Table 8-141, and Table 8-230.<br>•<br>Bits[6:5]: Reserved.<br>•<br>Bit[7]: Background Operation (BO): As defined in Section 8.2.9.4.6.                                                   |
| 8h             | 2                  | Return Code[15:0]: As defined in Table 8-46. Must be 0 for Request<br>messages.                                                                                                                                                                                                          |
| Ah             | 2                  | Vendor Specific Extended Status[15:0]: As defined in Section 8.2.9.4.6.<br>Must be 0 for Request messages.                                                                                                                                                                               |
| Ch             | Varies             | Message Payload: Variably sized payload for message in little-endian<br>format. The length of this field is specified in the Message Payload<br>Length[20:0] fields above. The format depends on Opcode and Message<br>Category, as defined in Table 8-49, Table 8-141, and Table 8-230. |

Commands from the FM API Command Sets may be transported as MCTP messages as defined in CXL Fabric Manager API over MCTP Binding Specification (DSP0234). All other CCI commands may be transported as MCTP messages as defined by the respective binding specification, such as CXL Type 3 Component Command Interface over MCTP Binding (DSP0281).

#### <span id="page-347-0"></span>7.6.3.1 Transport Details for MLD Components

MLD components that do not implement an MCTP-capable interconnect other than their CXL interface shall expose a CCI through their CXL interface(s) using MCTP PCIe VDM Transport Binding Specification (DSP0238). FMs shall use the Tunnel Management Command to pass requests to the FM-owned LD, as illustrated in [Figure 7-20](#page-347-4).

<span id="page-347-4"></span>**Figure 7-20. Tunneling Commands to an MLD through a CXL Switch**

![](_page_347_Figure_5.jpeg)

### <span id="page-347-1"></span>7.6.4 CXL Switch Management

Dynamic configuration of a switch by an FM is not required for basic switch functionality, but is required to support MLDs or CXL fabric topologies.

#### <span id="page-347-2"></span>7.6.4.1 Initial Configuration

The non-volatile memory of the switch stores, in a vendor-specific format, all necessary configuration settings that are required to prepare the switch for initial operation. This includes:
**Figure 7-21.**


- Port configuration, including direction (upstream or downstream), width, supported rates, etc.
- Virtual CXL Switch configuration, including number of vPPBs for each VCS, initial port binding configuration, etc.
- CCI access settings, including any vendor-defined permission settings for management.

#### <span id="page-347-3"></span>7.6.4.2 Dynamic Configuration

After initial configuration is complete and a CCI on the switch is operational, an FM can send Management Commands to the switch.

An FM may perform the following dynamic management actions on a CXL switch:

- Query switch information and configuration details
- Bind or Unbind ports
- Register to receive and handle event notifications from the switch (e.g., Hot-Plug, surprise removal, and failures)

When a switch port is connected to a downstream PCIe switch, and that port is bound to a vPPB, the management of that PCIe switch and its downstream device will be handled by the VCS's host, not the FM.

#### <span id="page-348-0"></span>7.6.4.3 MLD Port Management

A switch with MLD Ports requires an FM to perform the following management activities:

- MLD discovery
- LD binding/unbinding
- · Management Command Tunneling

### <span id="page-348-1"></span>7.6.5 MLD Component Management

The FM can connect to an MLD over a direct connection or by tunneling its management commands through the CCI of the CXL switch to which the device is connected. The FM can perform the following operations:

- Memory allocation and QoS Telemetry management
- · Security (e.g., LD erasure after unbinding)
- Error handling

<span id="page-348-3"></span>Figure 7-21. Example of MLD Management Requiring Tunneling

![](_page_348_Figure_13.jpeg)

### <span id="page-348-2"></span>7.6.6 Management Requirements for System Operations

This section presents examples of system use cases to highlight the role and responsibilities of the FM in system management. These use case discussions also serve to itemize the FM commands that CXL devices must support to facilitate each specific system behavior.

#### <span id="page-349-0"></span>7.6.6.1 Initial System Discovery

As the CXL system initializes, the FM can begin discovering all direct attached CXL devices across all supported media interfaces. Devices supporting the FM API may be discovered using transport specific mechanisms such as the MCTP discovery process, as defined in MCTP Base Specification (DSP0236).

When a component is discovered, the FM shall issue the Identify command (see [Section 8.2.10.1.1\)](#page-635-2) prior to issuing any other commands to check the component's type and its maximum supported command message size. A return of "Retry Required" indicates that the component is not yet ready to accept commands. After receiving a successful response to the Identify request, the FM may issue the Set Response Message Limit command (see [Section 8.2.10.1.4](#page-637-2)) to limit the size of response messages from the component based on the size of the FM's receive buffer. The FM shall not issue any commands with input arguments such that the command's response message exceeds the FM's maximum supported message size. Finally, the FM issues Get Log, as defined in [Section 8.2.10.5.2.1](#page-676-3), to read the Command Effects Log to determine which command opcodes are supported.

#### <span id="page-349-1"></span>7.6.6.2 CXL Switch Discovery

After a CXL switch is released from reset (i.e., PERST# has been deasserted), it loads its initial configuration from non-volatile memory. Ports configured as DS PPBs will be released from reset to link up. Upon detection of a switch, the FM will query its configuration, capabilities, and connected devices. The **Physical Switch Command Set** is required for all switches implementing FM API support. The **Virtual Switch Command Set** is required for all switches that support multiple host ports.

An example of an FM Switch discovery process is as follows:

- 1. FM issues **Identify Switch Device** to check switch port count, enabled port IDs, number of supported LDs, and enabled VCS IDs.
- 2. FM issues **Get Physical Port State** for each enabled port to check port configuration (US or DS), link state, and attached device type. This allows the FM to check for any port link-up issues and create an inventory of devices for binding. If any MLD components are discovered, the FM can begin MLD Port management activities.
- 3. If the switch supports multiple host ports, FM issues **Get Virtual CXL Switch Info** for each enabled VCS to check for all bound vPPBs in the system and create a list of binding targets.

#### <span id="page-349-2"></span>7.6.6.3 MLD and Switch MLD Port Management

MLDs must be connected to a CXL switch to share their LDs among VCSs. If an MLD is discovered in the system, the FM will need to prepare it for binding. A switch must support the **MLD Port Command Set** to support the use of MLDs. All MLD components shall support the MLD Component Command Set.

- 1. FM issues management commands to the device's LD FFFFh using **Tunnel Management Command**.
- 2. FM can execute advanced or vendor-specific management activities, such as encryption or authentication, using the **Send LD CXL.io Configuration Request** and **Send LD CXL.io Memory Request** commands.

#### <span id="page-349-3"></span>7.6.6.4 Event Notifications

Events can occur on both devices and switches. The event types and records are listed in [Section 7.6.8](#page-387-0) for FM API events and in [Section 8.2.10.2](#page-638-2) for component events. The Event Records framework is defined in [Section 8.2.10.2.1](#page-638-3) to provide a standard event

record format that all CXL components shall use when reporting events to the managing entity. The managing entity specifies the notification method, such as MSI/ MSI-X, EFN VDM, or MCTP Event Notification. The Event Notification message can be signaled by a device or by a switch; the notification always flows toward the managing entity. An Event Record is not sent with the Event Notification message. After the managing entity knows that an event has occurred, the entity can use component commands to read the Event Record.

- 1. To facilitate some system operations, the FM requires event notifications so it can execute its role in the process in a timely manner (e.g., notifying hosts of an asserted Attention Button on an MLD during a Managed Hot-Removal). If supported by the device, the FM can check and modify the current event notification settings with the Events command set.
- 2. If supported by the device, the event logs can be read with the **Get Event Records** command to check for any error events experienced by the device that might impact normal operation.

#### <span id="page-350-0"></span>7.6.6.5 Binding Ports and LDs on a Switch

Once all devices, VCSs, and vPPBs have been discovered, the FM can begin binding ports and LDs to hosts as follows:

- 1. FM issues the **Bind vPPB** command specifying a physical port, VCS ID and vPPB index to bind the physical port to the vPPB. An LD-ID must also be specified if the physical port is connected to an MLD. The switch is permitted to initiate a Managed Hot-Add if the host has already booted, as defined in [Section 9.9](#page-811-1).
- 2. Upon completion of the binding process, the switch notifies the FM by generating a **Virtual CXL Switch Event Record**.

#### <span id="page-350-1"></span>7.6.6.6 Unbinding Ports and LDs on a Switch

The FM can unbind devices or LDs from a VCS with the following steps:

- 1. FM issues the **Unbind vPPB** command specifying a VCS ID and vPPB index to unbind the physical port from the vPPB. The switch initiates a Managed Hot-Remove or Surprise Hot-Remove depending on the command options, as defined in PCIe Base Specification.
- 2. Upon completion of the unbinding process, the switch will generate a **Virtual CXL Switch Event Record**.

#### <span id="page-350-2"></span>7.6.6.7 Hot-Add and Managed Hot-Removal of Devices

When a device is Hot-Added to an unbound port on a switch, the FM receives a notification and is responsible for binding as described in the steps below:

- 1. The switch notifies the FM by generating **Physical Switch Event Records** as the Presence Detect sideband signal is asserted or when a Link Up is detected if the PPB does not support Presence Detect.
- 2. FM issues the **Get Physical Port State** command for the physical port that has linked up to discover the connected device type. The FM can now bind the physical port to a vPPB. If it's an MLD, then the FM can proceed with MLD Port management activities; otherwise, the device is ready for binding.

When a device is Hot-Removed from an unbound port on a switch, the FM receives a notification. The switch notifies the FM by generating **Physical Switch Event Records** as the Presence Detect sideband is deasserted and the associated port links down.

1. The switch notifies the FM by generating **Physical Switch Event Records** as the Presence Detect sideband is deasserted and the associated port links down.

When an SLD or PCIe device is Hot-Added to a bound port, the FM can be notified but is not involved. When a Surprise or Managed Hot-Removal of an SLD or PCIe device occurs on a bound port, the FM can be notified but is not involved.

A bound port will not advertise support for MLDs during negotiation, so MLD components will link up as an SLD.

The FM manages managed hot-removal of MLDs as follows:

- 1. When the Attention Button sideband is asserted on an MLD port, the Attention state bit is updated in the corresponding PPB and vPPB CSRs and the switch notifies the FM and hosts with LDs that are bound and below that MLD port. The hosts are notified with the MSI/MSI-X interrupts assigned to the affected vPPB and a **Virtual CXL Switch Event Record** is generated.
- 2. As defined in PCIe Base Specification, hosts will read the Attention State bit in their vPPB's CSR and prepare for removal of the LD. When a host is ready for the LD to be removed, it will set the Attention LED bit in the associated vPPB's CSR. The switch records these CSR updates by generating **Virtual CXL Switch Event Records**. The FM unbinds each assigned LD with the **Unbind vPPB** command as it receives notifications from each host.
- 3. When all host handshakes are complete, the MLD is ready for removal. The FM uses the **Send PPB CXL.io Configuration Request** command to set the Attention LED bit in the MLD port PPB to indicate that the MLD can be physically removed. The timeout value for the host handshakes to complete is implementation specific. There is no requirement for the FM to force the unbind operation, but it can do so using the "Simulate Surprise Hot-Remove" unbinding option in the **Unbind vPPB** command.

#### <span id="page-351-0"></span>7.6.6.8 Surprise Removal of Devices

There are two kinds of surprise removals: physical removal of a device, and surprise Link Down. The main difference between the two is the state of the presence pin, which will be deasserted after a physical removal but will remain asserted after a surprise Link Down. The switch notifies the FM of a surprise removal by generating **Virtual CXL Switch Event Records** for the change in link status and Presence Detect, as applicable.

Three cases of Surprise Removal are described below:

- When a Surprise Removal of a device occurs on an unbound port, the FM must be notified.
- When a Surprise Removal of an SLD or PCIe device occurs on a bound port, the FM is permitted to be notified but must not be involved in any error handling operations.
- When a Surprise Removal of an MLD component occurs, the FM must be notified. The switch will automatically unbind any existing LD bindings. The FM must perform error handling and port management activities, the details of which are considered implementation specific.

### <span id="page-351-1"></span>7.6.7 Fabric Management Application Programming Interface

The FM manages all devices in a CXL system via the sets of commands defined in the FM API. This specification defines the minimum command set requirements for each device type.

*Note:* CXL switches and MLDs require FM API support to facilitate the advanced system

<span id="page-352-1"></span>**Table 7-15. FM API Command Sets**

| Command Set Name                                  | HBR Switch FM API Requirement1 | MLD FM API Requirement1 |
|---------------------------------------------------|--------------------------------|-------------------------|
| Physical Switch<br>(Section 7.6.7.1)              | M                              | P                       |
| Virtual Switch<br>(Section 7.6.7.2)               | O                              | P                       |
| MLD Port<br>(Section 7.6.7.3)                     | O                              | P                       |
| MLD Component<br>(Section 7.6.7.4)                | P                              | M                       |
| Multi-Headed Device<br>(Section 7.6.7.5)          | P                              | P                       |
| DCD Management<br>(Section 7.6.7.6)               | P                              | O                       |
| PBR Switch<br>(Section 7.7.13)                    | P                              | P                       |
| Global Memory Access Endpoint<br>(Section 7.7.14) | P                              | P                       |

<span id="page-352-2"></span><span id="page-363-4"></span><span id="page-363-3"></span><sup>1.</sup> M = Mandatory, O = Optional, P = Prohibited.

capabilities outlined in [Section 7.6.6](#page-348-2). FM API is optional for all other CXL device types.

Command opcodes are listed in [Table 8-230. Table 8-230](#page-793-1) also identifies the minimum command sets and commands that are required to implement defined system capabilities. The following subsections define the commands grouped in each command set. Within each command set, commands are marked as mandatory (M) or optional (O). If a command set is supported, the required commands within that set must be implemented, but only if the Device supports that command set. For example, the Get Virtual CXL Switch Information command is required in the Virtual Switch Command Set, but that set is optional for switches. This means that a switch does not need to support the Get Virtual CXL Switch Information command if it does not support the Virtual Switch Command Set.

All commands have been defined as stand-alone operations; there are no explicit dependencies between commands, so optional commands can be implemented or not implemented on a per-command basis. Requirements for the implementation of commands are driven instead by the desired system functionality.

#### <span id="page-352-0"></span>7.6.7.1 Physical Switch Command Set

<span id="page-352-3"></span>This command set is only supported by and must be supported by CXL switches that have FM API support.

##### 7.6.7.1.1 Identify Switch Device (Opcode 5100h)

This command retrieves information about the capabilities and configuration of a CXL switch.

Possible Command Return Codes:

- Success
- Internal Error
- Retry Required

**Command Effects:**

<span id="page-635-3"></span><span id="page-638-2"></span>• None

<span id="page-353-0"></span>**Table 7-16. Identify Switch Device Response Payload**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                                                                                    |
|----------------|--------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 00h            | 1                  | Ingress Port ID: Ingress CCI port index of the received request message. For<br>CXL/PCIe ports, this corresponds to the physical port number. For non-CXL/<br>PCIe, this corresponds to a vendor-specific index of the buses that the device<br>supports, starting at 0. For example, a request received on the second of 2<br>SMBuses supported by a device would return a 1. |
| 01h            | 1                  | Reserved                                                                                                                                                                                                                                                                                                                                                                       |
| 02h            | 1                  | Number of Physical Ports: Total number of physical ports in the CXL switch,<br>including inactive/disabled ports.                                                                                                                                                                                                                                                              |
| 03h            | 1                  | Number of VCSs: Maximum number of virtual CXL switches that are supported<br>by the CXL switch.                                                                                                                                                                                                                                                                                |
| 04h            | 20h                | Active Port Bitmask: Bitmask that defines whether a physical port is enabled<br>(1) or disabled (0). Each bit corresponds 1:1 with a port, with the least<br>significant bit corresponding to Port 0.                                                                                                                                                                          |
| 24h            | 20h                | Active VCS Bitmask: Bitmask that defines whether a VCS is enabled (1) or<br>disabled (0). Each bit corresponds 1:1 with a VCS ID, with the least significant<br>bit corresponding to VCS 0.                                                                                                                                                                                    |
| 44h            | 2                  | Total Number of vPPBs: The number of virtual PPBs that are supported by<br>the CXL switch across all VCSs.                                                                                                                                                                                                                                                                     |
| 46h            | 2                  | Number of Bound vPPBs: Total number of vPPBs, across all VCSs, that are<br>bound.                                                                                                                                                                                                                                                                                              |
| 48h            | 1                  | Number of HDM Decoders: Number of HDM decoders available per USP.                                                                                                                                                                                                                                                                                                              |

##### 7.6.7.1.2 Get Physical Port State (Opcode 5101h)

<span id="page-353-2"></span>This command retrieves the physical port information.

Possible Command Return Codes:

- Success
- Invalid Input
- Internal Error
- Retry Required

**Command Effects:**

• None

<span id="page-353-1"></span>**Table 7-17. Get Physical Port State Request Payload**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                |
|----------------|--------------------|----------------------------------------------------------------------------|
| 0h             | 1                  | Number of Ports: Number of ports requested.                                |
| 1h             | Varies             | Port ID List: 1-byte ID of requested port, repeated Number of Ports times. |

<span id="page-354-0"></span>**Table 7-18. Get Physical Port State Response Payload**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                |
|----------------|--------------------|------------------------------------------------------------------------------------------------------------|
| 0h             | 1                  | Number of Ports: Number of port information blocks returned.                                               |
| 1h             | 3                  | Reserved                                                                                                   |
| 4h             | Varies             | Port Information List: Port information block as defined in Table 7-19, repeated<br>Number of Ports times. |

<span id="page-354-1"></span>**Table 7-19. Get Physical Port State Port Information Block Format (Sheet 1 of 2)**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
|----------------|--------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h             | 1                  | Port ID                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| 1h             | 1                  | •<br>Bits[3:0]: Current Port Configuration State:<br>— 0h = Disabled<br>— 1h = Bind in progress<br>— 2h = Unbind in progress<br>— 3h = DSP<br>— 4h = USP<br>— 5h = Fabric Port<br>— Fh = Invalid Port_ID; all subsequent field values are undefined<br>— All other encodings are reserved<br>•<br>Bit[4]: GAE Support: Indicates whether GAE support is present (1) or not<br>present (0) on a port. Valid only for PBR switches if Current Port Configuration<br>State is 4h (USP).<br>•<br>Bits[7:5]: Reserved. |
| 2h             | 1                  | •<br>Bits[3:0]: Connected Device Mode: Formerly known as Connected Device CXL<br>Version. This field is reserved for all values of Current Port Configuration State<br>except DSP.<br>— 0h = Connection is not CXL or is disconnected<br>— 1h = RCD mode<br>— 2h = CXL 68B Flit and VH mode<br>— 3h = Standard 256B Flit mode<br>— 4h = CXL Latency-Optimized 256B Flit mode<br>— 5h = PBR mode<br>— All other encodings are reserved<br>•<br>Bits[7:4]: Reserved.                                                |
| 3h             | 1                  | Reserved                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| 4h             | 1                  | Connected Device Type<br>•<br>00h = No device detected<br>•<br>01h = PCIe Device<br>•<br>02h = CXL Type 1 device<br>•<br>03h = CXL Type 2 device or HBR switch<br>•<br>04h = CXL Type 3 SLD<br>•<br>05h = CXL Type 3 MLD<br>•<br>06h = PBR component<br>•<br>All other encodings are reserved<br>This field is reserved if Supported CXL Modes is 00h. This field is reserved for all<br>values of Current Port Configuration State except 3h (DSP) or 5h (Fabric Port).                                          |
| 5h             | 1                  | Supported CXL Modes: Formerly known as Connected CXL Version. Bitmask that<br>defines which CXL modes are supported (1) or not supported (0) by this port:<br>•<br>Bit[0]: RCD Mode<br>•<br>Bit[1]: CXL 68B Flit and VH Capable<br>•<br>Bit[2]: 256B Flit Capable<br>•<br>Bit[3]: CXL Latency-Optimized 256B Flit Capable<br>•<br>Bit[4]: PBR Capable<br>•<br>Bits[7:5]: Reserved for future CXL use<br>Undefined when the value is 00h.                                                                          |

**Table 7-19. Get Physical Port State Port Information Block Format (Sheet 2 of 2)**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                                                                                                                      |
|----------------|--------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 6h             | 1                  | •<br>Bits[5:0]: Maximum Link Width: Value encoding matches the Maximum Link<br>Width field in the PCIe Link Capabilities register in the PCIe Capability structure.<br>•<br>Bits[7:6]: Reserved.                                                                                                                                                                                                                 |
| 7h             | 1                  | •<br>Bits[5:0]: Negotiated Link Width: Value encoding matches the Negotiated<br>Link Width field in PCIe Link Capabilities register in the PCIe Capability structure.<br>•<br>Bits[7:6]: Reserved.                                                                                                                                                                                                               |
| 8h             | 1                  | •<br>Bits[5:0]: Supported Link Speeds Vector: Value encoding matches the<br>Supported Link Speeds Vector field in the PCIe Link Capabilities 2 register in the<br>PCIe Capability structure.<br>•<br>Bits[7:6]: Reserved.                                                                                                                                                                                        |
| 9h             | 1                  | •<br>Bits[5:0]: Max Link Speed: Value encoding matches the Max Link Speed field in<br>the PCIe Link Capabilities register in the PCIe Capability structure.<br>•<br>Bits[7:6]: Reserved.                                                                                                                                                                                                                         |
| Ah             | 1                  | •<br>Bits[5:0]: Current Link Speed: Value encoding matches the Current Link<br>Speed field in the PCIe Link Status register in the PCIe Capability structure.<br>•<br>Bits[7:6]: Reserved.                                                                                                                                                                                                                       |
| Bh             | 1                  | LTSSM State: Current link LTSSM Major state:<br>•<br>00h = Detect<br>•<br>01h = Polling<br>•<br>02h = Configuration<br>•<br>03h = Recovery<br>•<br>04h = L0<br>•<br>05h = L0s<br>•<br>06h = L1<br>•<br>07h = L2<br>•<br>08h = Disabled<br>•<br>09h = Loopback<br>•<br>0Ah = Hot Reset<br>•<br>All other encodings are reserved<br>Link substates should be reported through vendor-defined diagnostics commands. |
| Ch             | 1                  | First Negotiated Lane Number                                                                                                                                                                                                                                                                                                                                                                                     |
| Dh             | 2                  | Link State Flags<br>•<br>Bit[0]: Lane Reversal State:<br>— 0 = Standard lane ordering<br>— 1 = Reversed lane ordering<br>•<br>Bit[1]: Port PCIe Reset State (PERST#):<br>— 0 = Not in reset<br>— 1 = In reset<br>•<br>Bit[2]: Port Presence Pin State (PRSNT#):<br>— 0 = Not present<br>— 1 = Present<br>•<br>Bit[3]: Power Control State:<br>— 0 = Power on<br>— 1 = Power off<br>•<br>Bits[15:4]: Reserved     |
| Fh             | 1                  | Supported LD Count: Number of additional LDs supported by this port. All ports<br>must support at least one LD.                                                                                                                                                                                                                                                                                                  |

##### 7.6.7.1.3 Physical Port Control (Opcode 5102h)

<span id="page-355-0"></span>This command is used by the FM to control unbound ports and MLD ports, including issuing resets and controlling sidebands.

Possible Command Return Codes:

• Success

- Unsupported
- Invalid Input
- Internal Error
- Retry Required

**Command Effects:**

• None

<span id="page-356-0"></span>**Table 7-20. Physical Port Control Request Payload**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                           |
|----------------|--------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h             | 1                  | PPB ID: Physical PPB ID, which corresponds 1:1 to associated physical port number.                                                                                                    |
| 1h             | 1                  | Port Opcode: Code that defines which operation to perform:<br>•<br>00h = Assert PERST#<br>•<br>01h = Deassert PERST#<br>•<br>02h = Reset PPB<br>•<br>All other encodings are reserved |

##### 7.6.7.1.4 Send PPB CXL.io Configuration Request (Opcode 5103h)

<span id="page-356-3"></span>This command sends CXL.io Config requests to the specified physical port's PPB. This command is only processed for unbound ports and MLD ports.

Possible Command Return Codes:

- Success
- Invalid Input
- Internal Error
- Retry Required

**Command Effects:**

• None

<span id="page-356-1"></span>**Table 7-21. Send PPB CXL.io Configuration Request Input Payload**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                                                  |
|----------------|--------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h             | 1                  | PPB ID: Target PPB's physical port.                                                                                                                                                                                                                                                                                                          |
| 1h             | 3                  | •<br>Bits[7:0]: Register Number: As defined in PCIe Base Specification<br>•<br>Bits[11:8]: Extended Register Number: As defined in PCIe Base Specification<br>•<br>Bits[15:12]: First Dword Byte Enable: As defined in PCIe Base Specification<br>•<br>Bits[22:16]: Reserved<br>•<br>Bit[23]: Transaction Type:<br>— 0 = Read<br>— 1 = Write |
| 4h             | 4                  | Transaction Data: Write data. Valid only for write transactions.                                                                                                                                                                                                                                                                             |

<span id="page-356-2"></span>**Table 7-22. Send PPB CXL.io Configuration Request Output Payload**

| Byte<br>Offset | Length<br>in Bytes | Description                                               |
|----------------|--------------------|-----------------------------------------------------------|
| 0h             | 4                  | Return Data: Read data. Valid only for read transactions. |

##### 7.6.7.1.5 Get Domain Validation SV State (Opcode 5104h)

This command is used by the Host to check the state of the secret value.

Possible Command Return Codes:

<span id="page-357-2"></span><span id="page-357-4"></span><span id="page-358-6"></span><span id="page-472-5"></span><span id="page-478-3"></span><span id="page-483-3"></span><span id="page-731-4"></span>- • Success
- Internal Error
- Retry Required

**Command Effects:**

• None

<span id="page-357-0"></span>**Table 7-23. Get Domain Validation SV State Response Payload**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                     |
|----------------|--------------------|---------------------------------------------------------------------------------------------------------------------------------|
| 0h             | 1                  | Secret Value State: State of the secret value:<br>•<br>00h = Not set<br>•<br>01h = Set<br>•<br>All other encodings are reserved |

##### 7.6.7.1.6 Set Domain Validation SV (Opcode 5105h)

<span id="page-357-3"></span>This command is used by the Host to set the secret value of its VCS. The secret value can be set only once. This command will fail with Invalid Input if it is called more than once.

Possible Command Return Codes:

- Success
- Invalid Input
- Internal Error
- Retry Required

**Command Effects:**

• None

<span id="page-357-1"></span>**Table 7-24. Set Domain Validation SV Request Payload**

| Byte<br>Offset | Length<br>in Bytes | Description                                                    |
|----------------|--------------------|----------------------------------------------------------------|
| 0h             | 10h                | Secret Value: UUID used to uniquely identify a host hierarchy. |

##### 7.6.7.1.7 Get VCS Domain Validation SV State (Opcode 5106h)

This command is used by the FM to check the state of the secret value in a VCS.

Possible Command Return Codes:

- • Success
- Internal Error
- Retry Required

**Command Effects:**

<span id="page-358-1"></span>**Table 7-25. Get VCS Domain Validation SV State Request Payload**

| Byte<br>Offset | Length<br>in Bytes | Description                    |
|----------------|--------------------|--------------------------------|
| 0h             | 1                  | VCS ID: Index of VCS to query. |

<span id="page-358-2"></span>**Table 7-26. Get VCS Domain Validation SV State Response Payload**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                     |
|----------------|--------------------|---------------------------------------------------------------------------------------------------------------------------------|
| 0h             | 1                  | Secret Value State: State of the secret value:<br>•<br>00h = Not set<br>•<br>01h = Set<br>•<br>All other encodings are reserved |

##### 7.6.7.1.8 Get Domain Validation SV (Opcode 5107h)

This command is used by the FM to retrieve the secret value from a VCS.

Possible Command Return Codes:

- • Success
- Internal Error
- Retry Required

Command Effects:

• None

<span id="page-358-3"></span>**Table 7-27. Get Domain Validation SV Request Payload**

| Byte<br>Offset | Length<br>in Bytes | Description                    |
|----------------|--------------------|--------------------------------|
| 0h             | 1                  | VCS ID: Index of VCS to query. |

<span id="page-358-4"></span>**Table 7-28. Get Domain Validation SV Response Payload**

| Byte<br>Offset | Length<br>in Bytes | Description                                                    |
|----------------|--------------------|----------------------------------------------------------------|
| 0h             | 10h                | Secret Value: UUID used to uniquely identify a host hierarchy. |

#### <span id="page-358-0"></span>7.6.7.2 Virtual Switch Command Set

This command set is supported only by the CXL switch. It is required for switches that support more than one VCS. The following commands are defined:

<span id="page-358-5"></span>**Table 7-29. Virtual Switch Command Set Requirements**

| Command Name                | Requirement1 |
|-----------------------------|--------------|
| Get Virtual CXL Switch Info | M            |
| Bind vPPB                   | O            |
| Unbind vPPB                 | O            |
| Generate AER Event          | O            |

<sup>1.</sup> M = Mandatory, O = Optional.

##### 7.6.7.2.1 Get Virtual CXL Switch Info (Opcode 5200h)

<span id="page-359-2"></span>This command retrieves information on a specified number of VCSs in the switch. Because of the possibility of variable numbers of vPPBs within each VCS, the returned array has variably sized elements.

Possible Command Return Codes:

- Success
- Invalid Input
- Internal Error
- Retry Required
- Invalid Payload Length

**Command Effects:**

• None

<span id="page-359-0"></span>**Table 7-30. Get Virtual CXL Switch Info Request Payload**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                         |
|----------------|--------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h             | 1                  | Start vPPB: Specifies the ID of the first vPPB for each VCS to include in the vPPB<br>information list in the response (bytes 4 – 7 in Table 7-32). This enables compatibility<br>with devices that have small maximum command message sizes.                       |
| 1h             | 1                  | vPPB List Limit: The maximum number of vPPB information entries to include in the<br>response (bytes 4 – 7 in Table 7-32). This enables compatibility with devices that<br>have small maximum command message sizes. This field shall have a minimum<br>value of 1. |
| 2h             | 1                  | Number of VCSs: Number of VCSs requested. This field shall have a minimum value<br>of 1.                                                                                                                                                                            |
| 3h             | Number<br>of VCSs  | VCS ID List: 1-byte ID of requested VCS, repeated Number of VCSs times.                                                                                                                                                                                             |

<span id="page-359-1"></span>**Table 7-31. Get Virtual CXL Switch Info Response Payload**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                             |
|----------------|--------------------|---------------------------------------------------------------------------------------------------------|
| 0h             | 1                  | Number of VCSs: Number of VCS information blocks returned.                                              |
| 1h             | 3                  | Reserved                                                                                                |
| 4h             | Varies             | VCS Information List: VCS information block as defined in Table 7-32, repeated<br>Number of VCSs times. |

<span id="page-360-0"></span>**Table 7-32. Get Virtual CXL Switch Info VCS Information Block Format**

| Byte<br>Offset                      | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
|-------------------------------------|--------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h                                  | 1                  | Virtual CXL Switch ID                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| 1h                                  | 1                  | VCS State: Current state of the VCS:<br>•<br>00h = Disabled<br>•<br>01h = Enabled<br>•<br>FFh = Invalid VCS ID; all subsequent field values are<br>invalid<br>•<br>All other encodings are reserved                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| 2h                                  | 1                  | USP ID: Physical port ID of the current VCS's Upstream<br>Port, or the current VCS's fabric physical port ID of a<br>Downstream ES VCS. Valid only when the VCS is enabled.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| 3h                                  | 1                  | Number of vPPBs: Total number of vPPBs in the VCS. This<br>value may be larger than the vPPB List Limit field specified<br>in the request. In this case, the length of vPPB information<br>list, starting at byte 4, is defined by 'vPPB List Limit', not by<br>this field. vPPB information list consists of vPPB List Entry<br>Count number of entries and each entry is 4B in length.<br>vPPB List Entry Count=min(vPPB List Limit, Number of<br>vPPBs).                                                                                                                                                                                                |
| 4h                                  | 1                  | vPPB[Start vPPB] Binding Status<br>•<br>00h = Unbound<br>•<br>01h = Bind or unbind in progress<br>•<br>02h = Bound Physical Port<br>•<br>03h = Bound LD<br>•<br>04h = Bound PID<br>•<br>All other encodings are reserved                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| 5h                                  | 2                  | For PBR Switches when Binding Status is 02h or 03h and for<br>HBR Switches:<br>•<br>Bits[7:0]: vPPB[Start vPPB] Bound Port ID:<br>Physical port number of the bound port. Valid only<br>when Binding Status is 02h or 03h.<br>•<br>Bits[15:8]: vPPB[Start vPPB] Bound LD ID: ID of<br>the LD that is bound to the port from the MLD on an<br>associated physical port. Valid only when vPPB[Start<br>vPPB] Binding Status is 03h; otherwise, the value is<br>FFh.<br>For PBR Switches when Binding Status is 04h:<br>•<br>Bits[11:0]: vPPB[Start vPPB] Bound PID: PID of<br>the bound vPPB, as defined in Section 7.7.12.3.<br>•<br>Bits[15:12]: Reserved. |
| 7h                                  | 1                  | Reserved                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| …                                   |                    | …                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| 4 + (vPPB List Entry Count - 1) * 4 | 1                  | vPPB[Start vPPB + vPPB List Entry Count1 - 1]<br>Binding Status: As defined above.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| 5 + (vPPB List Entry Count - 1) * 4 | 1                  | vPPB[Start vPPB + vPPB List Entry Count1 - 1] Bound<br>Port ID: As defined above.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| 6 + (vPPB List Entry Count - 1) * 4 | 1                  | vPPB[Start vPPB + vPPB List Entry Count1 - 1] Bound<br>LD ID: As defined above.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| 7 + (vPPB List Entry Count - 1) * 4 | 1                  | Reserved                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |

<span id="page-360-1"></span><sup>1.</sup> The vPPB information list length is defined by the lesser of the vPPB List Limit field in the command request and the Number of vPPBs field in the command response.

##### <span id="page-361-1"></span>7.6.7.2.2 Bind vPPB (Opcode 5201h)

<span id="page-361-2"></span>This command performs a binding operation on the specified vPPB. If the bind target is a physical port connected to a Type 1, Type 2, Type 3, or PCIe device or a physical port whose link is down, the specified physical port of the CXL switch is fully bound to the vPPB. If the bind target is a physical port connected to an MLD, then a corresponding LD-ID must also be specified.

All binding operations are executed as background commands. The switch notifies the FM of binding completion through the generation of event records, as defined in [Section 7.6.6](#page-348-2).

Possible Command Return Codes:

- Background Command Started
- Unsupported
- Invalid Input
- Internal Error
- Retry Required
- Busy

**Command Effects:**

• Background Operation

<span id="page-361-0"></span>**Table 7-33. Bind vPPB Request Payload**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                       |
|----------------|--------------------|-----------------------------------------------------------------------------------|
| 0h             | 1                  | Virtual CXL Switch ID                                                             |
| 1h             | 1                  | vPPB ID: Index of the vPPB within the VCS specified in the VCS ID.                |
| 2h             | 1                  | Physical Port ID                                                                  |
| 3h             | 1                  | Reserved                                                                          |
| 4h             | 2                  | LD ID: LD-ID if the target port is an MLD port. Must be FFFFh for other EP types. |

##### 7.6.7.2.3 Unbind vPPB (Opcode 5202h)

<span id="page-361-3"></span>This command unbinds the physical port or LD from the virtual hierarchy vPPB. All unbinding operations are executed as background commands. The switch notifies the FM of unbinding completion through the generation of event records, as defined in [Section 7.6.6](#page-348-2).

Possible Command Return Codes:

- Unsupported
- Background Command Started
- Invalid Input
- Internal Error
- Retry Required
- Busy

**Command Effects:**

• Background Operation

<span id="page-362-1"></span>**Table 7-34. Unbind vPPB Request Payload**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                      |
|----------------|--------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h             | 1                  | Virtual CXL Switch ID                                                                                                                                                                                                            |
| 1h             | 1                  | vPPB ID: Index of the vPPB within the VCS specified in the VCS ID.                                                                                                                                                               |
| 2h             | 1                  | •<br>Bits[3:0]: Unbind Option:<br>— 0h = Wait for port Link Down before unbinding<br>— 1h = Simulate Managed Hot-Remove<br>— 2h = Simulate Surprise Hot-Remove<br>— All other encodings are reserved<br>•<br>Bits[7:4]: Reserved |

##### 7.6.7.2.4 Generate AER Event (Opcode 5203h)

<span id="page-362-3"></span>This command generates an AER event on a specified VCS's vPPB (US vPPB or DS vPPB). The switch must respect the Host's AER mask settings.

Possible Command Return Codes:

- Success
- Unsupported
- Invalid Input
- Internal Error
- Retry Required

**Command Effects:**

• None

<span id="page-362-2"></span>**Table 7-35. Generate AER Event Request Payload**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                                                                                                                                       |
|----------------|--------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h             | 1                  | Virtual CXL Switch ID                                                                                                                                                                                                                                                                                                                                                                                                             |
| 1h             | 1                  | vPPB Instance: The value of 0 represents USP. The values of 1 and above<br>represent the DSP vPPBs in increasing Device Number, Function Number order,<br>as defined in Section 7.1.4.                                                                                                                                                                                                                                            |
| 2h             | 2                  | Reserved                                                                                                                                                                                                                                                                                                                                                                                                                          |
| 4h             | 4                  | AER Error<br>•<br>Bits[4:0]:<br>— If Severity=0, bit position of the error type in the AER Correctable<br>Error Status register, as defined in PCIe Base Specification<br>— If Severity=1, bit position of the error type in the AER Uncorrectable<br>Error Status register, as defined in PCIe Base Specification<br>•<br>Bits[30:5]: Reserved<br>•<br>Bit[31]: Severity<br>— 0 = Correctable Error<br>— 1 = Uncorrectable Error |
| 8h             | 20h                | AER Header: TLP Header to place in AER registers, as defined in PCIe Base<br>Specification.                                                                                                                                                                                                                                                                                                                                       |

#### <span id="page-362-0"></span>7.6.7.3 MLD Port Command Set

This command set is applicable to CXL switches and MLDs. The following commands are defined:

<span id="page-363-2"></span>**Table 7-36. MLD Port Command Set Requirements**

|                                      | Requirement |       |  |
|--------------------------------------|-------------|-------|--|
| Command Name                         | Switches1   | MLDs1 |  |
| Tunnel Management Command            | M           | O     |  |
| Send LD CXL.io Configuration Request | M           | P     |  |
| Send LD CXL.io Memory Request        | M           | P     |  |

<sup>1.</sup> M = Mandatory, O = Optional, P = Prohibited.

##### 7.6.7.3.1 Tunnel Management Command (Opcode 5300h)

This command tunnels the provided command to LD FFFFh of the MLD on the specified port, using the transport defined in [Section 7.6.3.1](#page-347-0).

When sent to an MLD, this provided command is tunneled by the FM-owned LD to the specified LD, as illustrated in the example in [Figure 7-22](#page-363-0) of a "Set LSA Request" being tunneled to LD 1 in an MLD.

<span id="page-363-0"></span>**Figure 7-22. Tunneling Commands to an LD in an MLD**

![](_page_363_Figure_9.jpeg)

The Management Command input payload field includes the tunneled command encapsulated in the CCI Message Format, as defined in [Figure 7-19.](#page-346-1) This can include an additional layer of tunneling for commands issued to LDs in an MLD that is accessible only through a CXL switch's MLD Port, as illustrated in [Figure 7-23.](#page-363-1)

<span id="page-363-1"></span>**Figure 7-23. Tunneling Commands to an LD in an MLD through a CXL Switch**

![](_page_363_Figure_12.jpeg)

Response size varies, based on the tunneled FM command's definition. Valid targets for the tunneled commands include switch MLD Ports, valid LDs within an MLD, and the LD Pool CCI in a Multi-Headed device. Tunneled commands sent to any other targets shall be discarded and this command shall return an "Invalid Input" return code. The FMowned LD (LD=FFFFh) is an invalid target in MLDs.

The LD Pool CCI in Multi-Headed devices is targeted using the "Target Type" field, as illustrated in [Figure 7-24.](#page-364-0) This command shall return an "Invalid Input" return code failure if tunneling to the LD Pool CCI is not permitted on the CCI that receives the request.

<span id="page-364-0"></span>**Figure 7-24. Tunneling Commands to the LD Pool CCI in a Multi-Headed Device**

![](_page_364_Figure_5.jpeg)

A Multi-Headed device shall terminate the processing of a request that includes more than 3 layers of tunneling and return the Unsupported return code.

The Tunnel Management Command itself does not cause any Command Effects, but the Management Command provided in the request will cause Command Effects as per its definition.

Possible Command Return Codes:

- Success
- Unsupported
- Invalid Input
- Internal Error
- Retry Required

Command Effects:

<span id="page-365-0"></span>**Table 7-37. Tunnel Management Command Request Payload**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                                                                                     |
|----------------|--------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h             | 1                  | Port or LD ID: Egress port ID for commands sent to a switch, or LD-ID for<br>commands sent to an MLD. Valid only when Target Type is 0.                                                                                                                                                                                                                                         |
| 1h             | 1                  | •<br>Bits[3:0]: Target Type: Specifies the type of tunneling target for this<br>command:<br>— 0h = Port or LD based. Indicates that the "Port or LD ID" field is used<br>to determine the target.<br>— 1h = LD Pool CCI. Indicates that the tunneling target is the LD Pool<br>CCI of a Multi-Headed device.<br>— All other encodings are reserved.<br>•<br>Bits[7:4]: Reserved |
| 2h             | 2                  | Command Size: Number of valid bytes in Management Command.                                                                                                                                                                                                                                                                                                                      |
| 4h             | Varies             | Management Command: Request message formatted in the CCI Message<br>Format as defined in Figure 7-19.                                                                                                                                                                                                                                                                           |

<span id="page-365-1"></span>**Table 7-38. Tunnel Management Command Response Payload**

| Byte offset | Length<br>in Bytes | Description                                                                                          |
|-------------|--------------------|------------------------------------------------------------------------------------------------------|
| 0h          | 2                  | Response Length: Number of valid bytes in Response Message.                                          |
| 2h          | 2                  | Reserved                                                                                             |
| 4h          | Varies             | Response Message: Response message formatted in the CCI Message Format<br>as defined in Figure 7-19. |

##### 7.6.7.3.2 Send LD CXL.io Configuration Request (Opcode 5301h)

<span id="page-365-2"></span>This command allows the FM to read or write the CXL.io Configuration Space of an unbound LD or FMLD. The switch will convert the request into CfgRd/CfgWr TLPs to the target device. Invalid Input Return Code shall be generated if the requested LD is bound.

Possible Command Return Codes:

- Success
- Unsupported
- Invalid Input
- Internal Error
- Retry Required

**Command Effects:**

<span id="page-366-0"></span>**Table 7-39. Send LD CXL.io Configuration Request Payload**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                                                        |
|----------------|--------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h             | 1                  | PPB ID: Target PPB's physical port.                                                                                                                                                                                                                                                                                                                |
| 1h             | 3                  | •<br>Bits[7:0]: Register Number: As defined in PCIe Base Specification<br>•<br>Bits[11:8]: Extended Register Number: As defined in PCIe Base<br>Specification<br>•<br>Bits[15:12]: First Dword Byte Enable: As defined in PCIe Base<br>Specification<br>•<br>Bits[22:16]: Reserved<br>•<br>Bit[23]: Transaction Type:<br>— 0 = Read<br>— 1 = Write |
| 4h             | 2                  | LD ID: Target LD-ID.                                                                                                                                                                                                                                                                                                                               |
| 6h             | 2                  | Reserved                                                                                                                                                                                                                                                                                                                                           |
| 8h             | 4                  | Transaction Data: Write data. Valid only for write transactions.                                                                                                                                                                                                                                                                                   |

<span id="page-366-1"></span>**Table 7-40. Send LD CXL.io Configuration Response Payload**

| Byte<br>Offset | Length<br>in Bytes | Description                                               |
|----------------|--------------------|-----------------------------------------------------------|
| 0h             | 4                  | Return Data: Read data. Valid only for read transactions. |

##### 7.6.7.3.3 Send LD CXL.io Memory Request (Opcode 5302h)

<span id="page-366-2"></span>This command allows the FM to batch read or write the CXL.io Memory Space of an unbound LD or FMLD. The switch will convert the request into MemRd/MemWr TLPs to the target device. Invalid Input Return Code shall be generated if the requested LD is bound.

Possible Command Return Codes:

- Success
- Unsupported
- Invalid Input
- Internal Error
- Retry Required

**Command Effects:**

<span id="page-367-1"></span>**Table 7-41. Send LD CXL.io Memory Request Payload**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                          |
|----------------|--------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 00h            | 1                  | Port ID: Target MLD port.                                                                                                                                                                                                                                                                            |
| 01h            | 2                  | •<br>Bits[11:0]: Reserved<br>•<br>Bits[15:12]: First Dword Byte Enable: As defined in PCIe Base<br>Specification<br>•<br>Bits[19:16]: Last Dword Byte Enable: As defined in PCIe Base<br>Specification<br>•<br>Bits[22:20]: Reserved<br>•<br>Bit[23]: Transaction Type:<br>— 0 = Read<br>— 1 = Write |
| 04h            | 2                  | LD ID: Target LD-ID.                                                                                                                                                                                                                                                                                 |
| 06h            | 2                  | Transaction Length: Transaction length in bytes, up to a maximum of 4 KB<br>(1000h).                                                                                                                                                                                                                 |
| 08h            | 8                  | Transaction Address: The target HPA that points into the target device's<br>MMIO Space.                                                                                                                                                                                                              |
| 10h            | Varies             | Transaction Data: Write data. Valid only for write transactions.                                                                                                                                                                                                                                     |

<span id="page-367-2"></span>**Table 7-42. Send LD CXL.io Memory Request Response Payload**

| Byte<br>Offset | Length<br>in Bytes | Description                                               |
|----------------|--------------------|-----------------------------------------------------------|
| 0h             | 2                  | Return Size: Number of successfully transferred bytes.    |
| 2h             | 2                  | Reserved                                                  |
| 4h             | Varies             | Return Data: Read data. Valid only for read transactions. |

#### <span id="page-367-0"></span>7.6.7.4 MLD Component Command Set

<span id="page-367-4"></span>This command set is only supported by, and must be supported by, MLD components implementing FM API support. These commands are processed by MLDs. When an FM is connected to a CXL switch that supports the FM API and does not have a direct connection to an MLD, these commands are passed to the MLD using the **Tunnel Management Command**. The following commands are defined:

<span id="page-367-3"></span>**Table 7-43. MLD Component Command Set Requirements**

| Command Name         | Requirement1 |
|----------------------|--------------|
| Get LD Info          | M            |
| Get LD Allocations   | M            |
| Set LD Allocations   | O            |
| Get QoS Control      | M            |
| Set QoS Control      | M            |
| Get QoS Status       | O            |
| Get QoS Allocated BW | M            |
| Set QoS Allocated BW | M            |
| Get QoS BW Limit     | M            |
| Set QoS BW Limit     | M            |

<sup>1.</sup> M = Mandatory, O = Optional.

##### 7.6.7.4.1 Get LD Info (Opcode 5400h)

<span id="page-368-2"></span>This command retrieves the configurations of the MLD.

Possible Command Return Codes:

- Success
- Unsupported
- Invalid Input
- Internal Error
- Retry Required

**Command Effects:**

• None

<span id="page-368-0"></span>**Table 7-44. Get LD Info Response Payload**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
|----------------|--------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h             | 8                  | Memory Size: Total device memory capacity.                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| 8h             | 2                  | LD Count: Number of logical devices supported.                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| Ah             | 1                  | QoS Telemetry Capability: Optional QoS Telemetry for memory MLD<br>capabilities for management by an FM (see Section 3.3.4).<br>•<br>Bit[0]: Egress Port Congestion Supported: When set, the associated<br>feature is supported and the Get QoS Status command must be<br>implemented (see Section 3.3.4.3.9).<br>•<br>Bit[1]: Temporary Throughput Reduction Supported: When set, the<br>associated feature is supported (see Section 3.3.4.3.5).<br>•<br>Bits[7:2]: Reserved. |

##### 7.6.7.4.2 Get LD Allocations (Opcode 5401h)

<span id="page-368-3"></span>This command retrieves the memory allocations of the MLD.

Possible Command Return Codes:

- Success
- Unsupported
- Internal Error
- Retry Required
- Invalid Payload Length

**Command Effects:**

• None

<span id="page-368-1"></span>**Table 7-45. Get LD Allocations Request Payload**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                |
|----------------|--------------------|----------------------------------------------------------------------------------------------------------------------------|
| 0h             | 1                  | Start LD ID: ID of the first LD in the LD Allocation List.                                                                 |
| 1h             | 1                  | LD Allocation List Limit: Maximum number of LD information blocks returned.<br>This field shall have a minimum value of 1. |

<span id="page-369-0"></span>**Table 7-46. Get LD Allocations Response Payload**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                                                |
|----------------|--------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h             | 1                  | Number of LDs: Number of LDs enabled in the device.                                                                                                                                                        |
| 1h             | 1                  | Memory Granularity: This field specifies the granularity of the memory sizes<br>configured for each LD:<br>•<br>0h = 256 MB<br>•<br>1h = 512 MB<br>•<br>2h = 1 GB<br>•<br>All other encodings are reserved |
| 2h             | 1                  | Start LD ID: ID of the first LD in the LD Allocation List.                                                                                                                                                 |
| 3h             | 1                  | LD Allocation List Length: Number of LD information blocks returned. This<br>value is the lesser of the request's 'LD Allocation List Limit' and response's<br>'Number of LDs'.                            |
| 4h             | Varies             | LD Allocation List: LD Allocation blocks for each LD, as defined in Table 7-47,<br>repeated LD Allocation List Length times.                                                                               |

<span id="page-369-1"></span>**Table 7-47. LD Allocations List Format**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                |
|----------------|--------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h             | 8                  | Range 1 Allocation Multiplier: Memory Allocation Range 1 for LD. This value<br>is multiplied with Memory Granularity to calculate the memory allocation<br>range in bytes. |
| 8h             | 8                  | Range 2 Allocation Multiplier: Memory Allocation Range 2 for LD. This value<br>is multiplied with Memory Granularity to calculate the memory allocation<br>range in bytes. |

##### 7.6.7.4.3 Set LD Allocations (Opcode 5402h)

<span id="page-369-2"></span>This command sets the memory allocation for each LD. This command will fail if the device fails to allocate any of the allocations defined in the request. The allocations provided in the response reflect the state of the LD allocations after the command is processed, which allows the FM to check for partial success.

### Possible Command Return Codes:

- Success
- Unsupported
- Invalid Input
- Internal Error
- Retry Required
- Invalid Payload Length

**Command Effects:**

- Configuration Change after Cold Reset
- Configuration Change after Conventional Reset
- Configuration Change after CXL Reset
- Immediate Configuration Change
- Immediate Data Change

<span id="page-370-0"></span>**Table 7-48. Set LD Allocations Request Payload**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                               |
|----------------|--------------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| 0h             | 1                  | Number of LDs: Number of LDs to configure. This field shall have a minimum<br>value of 1.                                                 |
| 1h             | 1                  | Start LD ID: ID of the first LD in the LD Allocation List.                                                                                |
| 2h             | 2                  | Reserved                                                                                                                                  |
| 4h             | Varies             | LD Allocation List: LD Allocation blocks for each LD, starting at Start LD ID, as<br>defined in Table 7-47, repeated Number of LDs times. |

<span id="page-370-1"></span>**Table 7-49. Set LD Allocations Response Payload**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                       |
|----------------|--------------------|---------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h             | 1                  | Number of LDs: Number of LDs configured.                                                                                                          |
| 1h             | 1                  | Start LD ID: ID of the first LD in the LD Allocation List.                                                                                        |
| 2h             | 2                  | Reserved                                                                                                                                          |
| 4h             | Varies             | LD Allocation List: Updated LD Allocation blocks for each LD, starting at Start<br>LD ID, as defined in Table 7-47, repeated Number of LDs times. |

##### 7.6.7.4.4 Get QoS Control (Opcode 5403h)

<span id="page-370-3"></span>This command retrieves the MLD's QoS control parameters.

Possible Command Return Codes:

- Success
- Internal Error
- Retry Required
- Invalid Payload Length

**Command Effects:**

• None

<span id="page-370-2"></span>**Table 7-50. Payload for Get QoS Control Response, Set QoS Control Request, and Set QoS Control Response (Sheet 1 of 2)**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                                                          |
|----------------|--------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h             | 1                  | QoS Telemetry Control: Default is 00h.<br>•<br>Bit[0]: Egress Port Congestion Enable: See Section 3.3.4.3.9<br>•<br>Bit[1]: Temporary Throughput Reduction Enable: See Section 3.3.4.3.5<br>•<br>Bits[7:2]: Reserved |
| 1h             | 1                  | Egress Moderate Percentage: Threshold in percent for Egress Port Congestion<br>mechanism to indicate moderate congestion. Valid range is 1-100. Default is 10.                                                       |
| 2h             | 1                  | Egress Severe Percentage: Threshold in percent for Egress Port Congestion<br>mechanism to indicate severe congestion. Valid range is 1-100. Default is 25.                                                           |

**Table 7-50. Payload for Get QoS Control Response, Set QoS Control Request, and Set QoS Control Response (Sheet 2 of 2)**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                         |
|----------------|--------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 3h             | 1                  | Backpressure Sample Interval: Interval in ns for Egress Port Congestion<br>mechanism to take samples. Valid range is 0-15. Default is 8 (800 ns of history for<br>100 samples). Value of 0 disables the mechanism. See Section 3.3.4.3.4.                           |
| 4h             | 2                  | ReqCmpBasis: Estimated maximum sustained sum of requests and recent<br>responses across the entire device, serving as the basis for QoS Limit Fraction. Valid<br>range is 0-65,535. Value of 0 disables the mechanism. Default is 0. See<br>Section 3.3.4.3.7.      |
| 6h             | 1                  | Completion Collection Interval: Interval in ns for Completion Counting<br>mechanism to collect the number of transmitted responses in a single counter. Valid<br>range is 0-255. Default is 64 (1.024 us of history, given 16 counters). See<br>Section 3.3.4.3.10. |

##### 7.6.7.4.5 Set QoS Control (Opcode 5404h)

<span id="page-371-0"></span>This command sets the MLD's QoS control parameters, as defined in [Table 7-50.](#page-370-2) The device must complete the set operation before returning the response. The command response returns the resulting QoS control parameters, as defined in the same table. This command will fail, returning Invalid Input, if any of the parameters are outside their valid range.

Possible Command Codes:

- Success
- Invalid Input
- Internal Error
- Retry Required
- Invalid Payload Length

**Command Effects:**

<span id="page-371-1"></span>• Immediate Policy Change

Payload for Set QoS Control Request and Response is documented in [Table 7-50.](#page-370-2)

##### 7.6.7.4.6 Get QoS Status (Opcode 5405h)

This command retrieves the MLD's QoS Status. This command is mandatory if the Egress Port Congestion Supported bit is set (see [Table 7-44\)](#page-368-0).

Possible Command Return Codes:

- Success
- Unsupported
- Internal Error
- Retry Required
- Invalid Payload Length

**Command Effects:**

<span id="page-372-0"></span>**Table 7-51. Get QoS Status Response Payload**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                 |
|----------------|--------------------|-----------------------------------------------------------------------------------------------------------------------------|
| 0h             | 1                  | Backpressure Average Percentage: Current snapshot of the measured<br>Egress Port average congestion. See Section 3.3.4.3.4. |

##### 7.6.7.4.7 Get QoS Allocated BW (Opcode 5406h)

<span id="page-372-3"></span>This command retrieves the MLD's QoS allocated bandwidth on a per-LD basis (see [Section 3.3.4.3.7](#page-142-2)).

Possible Command Return Codes:

- Success
- Invalid Input
- Internal Error
- Retry Required
- Invalid Payload Length

**Command Effects:**

• None

<span id="page-372-1"></span>**Table 7-52. Payload for Get QoS Allocated BW Request**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                       |
|----------------|--------------------|-----------------------------------------------------------------------------------|
| 0h             | 1                  | Number of LDs: Number of LDs queried. This field shall have a minimum value of 1. |
| 1h             | 1                  | Start LD ID: ID of the first LD in the QoS Allocated BW List.                     |

<span id="page-372-2"></span>**Table 7-53. Payload for Get QoS Allocated BW Response**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                               |
|----------------|--------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h             | 1                  | Number of LDs: Number of LDs queried.                                                                                                                                                                                                     |
| 1h             | 1                  | Start LD ID: ID of the first LD in the QoS Allocated BW List.                                                                                                                                                                             |
| 2h             | Number of LDs      | QoS Allocation Fraction: Byte array of allocated bandwidth fractions<br>for LDs, starting at Start LD ID. The valid range of each array element<br>is 0-255. Default value is 0. Value in each byte is the fraction multiplied<br>by 256. |

##### 7.6.7.4.8 Set QoS Allocated BW (Opcode 5407h)

<span id="page-372-4"></span>This command sets the MLD's QoS allocated bandwidth on a per-LD basis, as defined in [Section 3.3.4.3.7](#page-142-2). The device must complete the set operation before returning the response. The command response returns the resulting QoS allocated bandwidth, as defined in the same table. This command will fail, returning Invalid Input, if any of the parameters are outside their valid range.

Possible Command Return Codes:

- Success
- Invalid Input
- Internal Error

- Retry Required
- Invalid Payload Length

**Command Effects:**

- Configuration Change after Cold Reset
- Configuration Change after Conventional Reset
- Configuration Change after CXL Reset
- Immediate Configuration Change
- Immediate Data Change

<span id="page-373-0"></span>**Table 7-54. Payload for Set QoS Allocated BW Request, and Set QoS Allocated BW Response**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                            |
|----------------|--------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h             | 1                  | Number of LDs: Number of LDs configured.                                                                                                                                                                                               |
| 1h             | 1                  | Start LD ID: ID of the first LD in the QoS Allocated BW List.                                                                                                                                                                          |
| 2h             | Number of LDs      | QoS Allocation Fraction: Byte array of allocated bandwidth fractions for LDs,<br>starting at Start LD ID. The valid range of each array element is 0-255. Default<br>value is 0. Value in each byte is the fraction multiplied by 256. |

##### 7.6.7.4.9 Get QoS BW Limit (Opcode 5408h)

<span id="page-373-3"></span>This command retrieves the MLD's QoS bandwidth limit on a per-LD basis (see [Section 3.3.4.3.7](#page-142-2)).

Possible Command Return Codes:

- Success
- Invalid Input
- Internal Error
- Retry Required
- Invalid Payload Length

**Command Effects:**

• None

<span id="page-373-1"></span>**Table 7-55. Payload for Get QoS BW Limit Request**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                       |
|----------------|--------------------|-----------------------------------------------------------------------------------|
| 0h             | 1                  | Number of LDs: Number of LDs queried. This field shall have a minimum value of 1. |
| 1h             | 1                  | Start LD ID: ID of the first LD in the QoS BW Limit List.                         |

<span id="page-373-2"></span>**Table 7-56. Payload for Get QoS BW Limit Response**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                             |
|----------------|--------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h             | 1                  | Number of LDs: Number of LDs queried.                                                                                                                                                                                                   |
| 1h             | 1                  | Start LD ID: ID of the first LD in the QoS BW Limit List.                                                                                                                                                                               |
| 2h             | Number of LDs      | QoS Limit Fraction: Byte array of allocated bandwidth limit fractions for LDs,<br>starting at Start LD ID. The valid range of each array element is 0-255. Default<br>value is 0. Value in each byte is the fraction multiplied by 256. |

##### 7.6.7.4.10 Set QoS BW Limit (Opcode 5409h)

<span id="page-374-2"></span>This command sets the MLD's QoS bandwidth limit on a per-LD basis, as defined in [Section 3.3.4.3.7](#page-142-2). The device must complete the set operation before returning the response. The command response returns the resulting QoS bandwidth limit, as defined in the same table. This command will fail, returning Invalid Input, if any of the parameters are outside their valid range. This command will fail, returning Internal Error, if the device was able to set the QoS BW Limit for some of the LDs in the request, but not all the LDs.

Possible Command Return Codes:

- Success
- Invalid Input
- Internal Error
- Retry Required
- Invalid Payload Length

**Command Effects:**

- Configuration Change after Cold Reset
- Configuration Change after Conventional Reset
- Configuration Change after CXL Reset
- Immediate Configuration Change
- Immediate Data Change

<span id="page-374-1"></span>**Table 7-57. Payload for Set QoS BW Limit Request, and Set QoS BW Limit Response**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                             |
|----------------|--------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h             | 1                  | Number of LDs: Number of LDs configured.                                                                                                                                                                                                |
| 1h             | 1                  | Start LD ID: ID of the first LD in the QoS BW Limit List.                                                                                                                                                                               |
| 2h             | Number of LDs      | QoS Limit Fraction: Byte array of allocated bandwidth limit fractions for LDs,<br>starting at Start LD ID. The valid range of each array element is 0-255. Default<br>value is 0. Value in each byte is the fraction multiplied by 256. |

#### <span id="page-374-0"></span>7.6.7.5 Multi-Headed Device Command Set

The Multi-Headed device command set includes commands for querying the Head-to-LD mapping in a Multi-Headed device. Support for this command set is required on the LD Pool CCI of a Multi-Headed device.

##### 7.6.7.5.1 Get Multi-Headed Info (Opcode 5500h)

<span id="page-374-3"></span>This command retrieves the number of heads, number of supported LDs, and Head-to-LD mapping of a Multi-Headed device.

Possible Command Return Codes:

- Success
- Unsupported
- Invalid Input
- Internal Error
- Retry Required

Command Effects:

• None

<span id="page-375-0"></span>**Table 7-58. Get Multi-Headed Info Request Payload**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                  |
|----------------|--------------------|--------------------------------------------------------------------------------------------------------------|
| 0h             | 1                  | Start LD ID: ID of the first LD in the LD Map.                                                               |
| 1h             | 1                  | LD Map List Limit: Maximum number of LD Map entries returned. This field<br>shall have a minimum value of 1. |

<span id="page-375-1"></span>**Table 7-59. Get Multi-Headed Info Response Payload**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                                      |
|----------------|--------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h             | 1                  | Number of LDs: Total number of LDs in the LD Pool. This field shall have a<br>minimum value of 1.                                                                                                |
| 1h             | 1                  | Number of Heads: Total number of CXL heads. This field shall have a<br>minimum value of 1.                                                                                                       |
| 2h             | 2                  | Reserved                                                                                                                                                                                         |
| 4h             | 1                  | Start LD ID: ID of the first LD in the LD Map.                                                                                                                                                   |
| 5h             | 1                  | LD Map Length: Number of LD Map entries returned.<br>LD Map Length = Min (LD Map List Limit. (Number of LDs - Start LD ID))                                                                      |
| 6h             | 2                  | Reserved                                                                                                                                                                                         |
| 8h             | LD Map<br>Length   | LD Map: Port number of the head to which each LD is assigned, starting at<br>Start LD ID, repeated LD Map Length times. A value of FFh indicates that LD<br>is not currently assigned to a head. |

##### 7.6.7.5.2 Get Head Info (Opcode 5501h)

<span id="page-375-3"></span>This command retrieves information for one or more heads.

This command fails with the Invalid Input return code if the values of the Start Head and Number of Heads fields request the information for a non-existent head.

Possible Command Return Codes:

- Success
- Unsupported
- Invalid Input
- Internal Error
- Retry Required

**Command Effects:**

• None

<span id="page-375-2"></span>**Table 7-60. Get Head Info Request Payload**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                 |
|----------------|--------------------|-----------------------------------------------------------------------------|
| 0h             | 1                  | Start Head: Specifies the ID of the first head information block requested. |
| 1h             | 1                  | Number of Heads: Number of head information blocks requested.               |

<span id="page-376-0"></span>**Table 7-61. Get Head Info Response Payload**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                |
|----------------|--------------------|------------------------------------------------------------------------------------------------------------|
| 0h             | 1                  | Number of Heads: Number of head information blocks returned.                                               |
| 1h             | 3                  | Reserved                                                                                                   |
| 4h             | Varies             | Head Information List: Head information block as defined in Table 7-62, repeated<br>Number of Heads times. |

<span id="page-376-1"></span>**Table 7-62. Get Head Info Head Information Block Format**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                                                                                                                      |
|----------------|--------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h             | 1                  | Port Number: Value encoding matches the Port Number field in the PCIe Link<br>Capabilities register in the PCIe Capability structure.                                                                                                                                                                                                                                                                            |
| 1h             | 1                  | •<br>Bits[5:0]: Maximum Link Width: Value encoding matches the Maximum Link<br>Width field in the PCIe Link Capabilities register in the PCIe Capability structure<br>•<br>Bits[7:6]: Reserved                                                                                                                                                                                                                   |
| 2h             | 1                  | •<br>Bits[5:0]: Negotiated Link Width: Value encoding matches the Negotiated<br>Link Width field in the PCIe Link Capabilities register in the PCIe Capability<br>structure<br>•<br>Bits[7:6]: Reserved                                                                                                                                                                                                          |
| 3h             | 1                  | •<br>Bits[5:0]: Supported Link Speeds Vector: Value encoding matches the<br>Supported Link Speeds Vector field in the PCIe Link Capabilities 2 register in the<br>PCIe Capability structure<br>•<br>Bits[7:6]: Reserved                                                                                                                                                                                          |
| 4h             | 1                  | •<br>Bits[5:0]: Max Link Speed: Value encoding matches the Max Link Speed field in<br>the PCIe Link Capabilities register in the PCIe Capability structure<br>•<br>Bits[7:6]: Reserved                                                                                                                                                                                                                           |
| 5h             | 1                  | •<br>Bits[5:0]: Current Link Speed: Value encoding matches the Current Link<br>Speed field in the PCIe Link Status register in the PCIe Capability structure<br>•<br>Bits[7:6]: Reserved                                                                                                                                                                                                                         |
| 6h             | 1                  | LTSSM State: Current link LTSSM Major state:<br>•<br>00h = Detect<br>•<br>01h = Polling<br>•<br>02h = Configuration<br>•<br>03h = Recovery<br>•<br>04h = L0<br>•<br>05h = L0s<br>•<br>06h = L1<br>•<br>07h = L2<br>•<br>08h = Disabled<br>•<br>09h = Loopback<br>•<br>0Ah = Hot Reset<br>•<br>All other encodings are reserved<br>Link substates should be reported through vendor-defined diagnostics commands. |
| 7h             | 1                  | First Negotiated Lane Number                                                                                                                                                                                                                                                                                                                                                                                     |
| 8h             | 1                  | Link State Flags<br>•<br>Bit[0]: Lane Reversal State:<br>— 0 = Standard lane ordering<br>— 1 = Reversed lane ordering<br>•<br>Bit[1]: Port PCIe Reset State (PERST#):<br>— 0 = Not in reset<br>— 1 = In reset<br>•<br>Bits[7:2]: Reserved                                                                                                                                                                        |

#### <span id="page-377-0"></span>7.6.7.6 DCD Management Command Set for LD-FAM

The DCD Management command set, described in the following subsections, includes commands for querying and configuring Dynamic Capacity for LD-FAM (SLDs and MLDs). It is used by the FM to manage memory assignment within an LD-FAM DCD. Memory management for G-FAM (GFDs) is defined in [Section 8.2.10.9.10](#page-755-2).

##### 7.6.7.6.1 Get DCD Info (Opcode 5600h)

<span id="page-377-2"></span>This command retrieves the number of supported hosts, total Dynamic Capacity of the device, and supported region configurations for an LD-FAM DCD. To retrieve the corresponding DCD info for a GFD, see [Section 8.2.10.9.10.1](#page-755-3).

Possible Command Return Codes:

- Success
- Unsupported
- Internal Error
- Retry Required

**Command Effects:**

• None

<span id="page-377-1"></span>**Table 7-63. Get DCD Info Response Payload (Sheet 1 of 2)**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
|----------------|--------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 00h            | 1                  | Number of Hosts: Total number of hosts that the device supports. This field<br>shall have a minimum value of 1.                                                                                                                                                                                                                                                                                                                                                                       |
| 01h            | 1                  | Number of Supported DC Regions: The device shall report the total<br>number of Dynamic Capacity Regions available per LD. DCDs shall report<br>between 1 and 8 regions. All other encodings are reserved.                                                                                                                                                                                                                                                                             |
| 02h            | 2                  | Reserved                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| 04h            | 2                  | •<br>Bits[3:0]: Supported Add Capacity Selection Policies: Bitmask that<br>specifies the selection policies, as defined in Section 7.6.7.6.5, that the<br>device supports when capacity is added. At least one policy shall be<br>supported. A value of 1 indicates that a policy is supported, and a value<br>of 0 indicates that a policy is not supported:<br>— Bit[0]: Free<br>— Bit[1]: Contiguous<br>— Bit[2]: Prescriptive<br>— Bit[3]: Must be 0<br>•<br>Bits[15:4]: Reserved |
| 06h            | 2                  | Reserved                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| 08h            | 2                  | •<br>Bits[1:0]: Supported Release Capacity Removal Policies: Bitmask<br>that specifies the removal policies, as defined in Section 7.6.7.6.6, that<br>the device supports when capacity is released. At least one policy shall<br>be supported. A value of 1 indicates that a policy is supported, and a<br>value of 0 indicates that a policy is not supported:<br>— Bit[0]: Tag-based<br>— Bit[1]: Prescriptive<br>•<br>Bits[15:2]: Reserved                                        |
| 0Ah            | 1                  | Sanitize on Release Configuration Support Mask: Bitmask, where bit<br>position corresponds to region number, indicating whether the Sanitize on<br>Release capability is configurable (1) or not configurable (0) for that region.                                                                                                                                                                                                                                                    |
| 0Bh            | 1                  | Reserved                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| 0Ch            | 8                  | Total Dynamic Capacity: Total memory media capacity of the device<br>available for dynamic assignment to any host in multiples of 256 MB.                                                                                                                                                                                                                                                                                                                                             |

**Table 7-63. Get DCD Info Response Payload (Sheet 2 of 2)**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                |
|----------------|--------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 14h            | 8                  | Region 0 Supported Block Size Mask: Indicates the block sizes that the<br>region supports. Each bit indicates a power of 2 supported block size, where<br>bit n being set indicates that block size 2^n is supported. Bits[5:0] and<br>bits[63:52] shall be 0. At least one block size shall be supported. |
| 1Ch            | 8                  | Region 1 Supported Block Size Mask: As defined in Region 0 Supported<br>Block Size Mask. Valid only if Number of Supported Regions > 1.                                                                                                                                                                    |
| 24h            | 8                  | Region 2 Supported Block Size Mask: As defined in Region 0 Supported<br>Block Size Mask. Valid only if Number of Supported Regions > 2.                                                                                                                                                                    |
| 2Ch            | 8                  | Region 3 Supported Block Size Mask: As defined in Region 0 Supported<br>Block Size Mask. Valid only if Number of Supported Regions > 3.                                                                                                                                                                    |
| 34h            | 8                  | Region 4 Supported Block Size Mask: As defined in Region 0 Supported<br>Block Size Mask. Valid only if Number of Supported Regions > 4.                                                                                                                                                                    |
| 3Ch            | 8                  | Region 5 Supported Block Size Mask: As defined in Region 0 Supported<br>Block Size Mask. Valid only if Number of Supported Regions > 5.                                                                                                                                                                    |
| 44h            | 8                  | Region 6 Supported Block Size Mask: As defined in Region 0 Supported<br>Block Size Mask. Valid only if Number of Supported Regions > 6.                                                                                                                                                                    |
| 4Ch            | 8                  | Region 7 Supported Block Size Mask: As defined in Region 0 Supported<br>Block Size Mask. Valid only if Number of Supported Regions > 7.                                                                                                                                                                    |

##### 7.6.7.6.2 Get Host DC Region Configuration (Opcode 5601h)

<span id="page-378-1"></span>This command retrieves the Dynamic Capacity configuration for an LD-FAM DCD, for a specified host.

Possible Command Return Codes:

- Success
- Unsupported
- Invalid Input
- Internal Error
- Retry Required

**Command Effects:**

• None

<span id="page-378-0"></span>**Table 7-64. Get Host DC Region Configuration Request Payload**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                   |
|----------------|--------------------|-----------------------------------------------------------------------------------------------|
| 0h             | 2                  | Host ID: For an LD-FAM device, the LD-ID of the host interface configuration to query.        |
| 2h             | 1                  | Region Count: The maximum number of region configurations to return in the output<br>payload. |
| 3h             | 1                  | Starting Region Index: Index of the first requested region.                                   |

<span id="page-379-0"></span>**Table 7-65. Get Host DC Region Configuration Response Payload**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                 |
|----------------|--------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h             | 2                  | Host ID: For an LD-FAM device, the LD-ID of the host interface configuration<br>returned.                                                                   |
| 2h             | 1                  | Number of Available Regions: As defined in Get Dynamic Capacity Configuration<br>Output Payload.                                                            |
| 3h             | 1                  | Number of Regions Returned: The number of entries in the Region Configuration<br>List.                                                                      |
| 4h             | Varies             | Region Configuration List: DC Region Info for region specified via Starting Region<br>Index input field. The format of each entry is defined in Table 7-66. |
| Varies         | 4                  | Total Number of Supported Extents: Total number of extents that the device<br>supports on this LD.                                                          |
| Varies         | 4                  | Number of Available Extents: Remaining number of extents that the device<br>supports, as defined in Section 9.13.3.3.                                       |
| Varies         | 4                  | Total Number of Supported Tags: Total number of Tag values that the device<br>supports on this LD.                                                          |
| Varies         | 4                  | Number of Available Tags: Remaining number of Tag values that the device<br>supports, as defined in Section 9.13.3.3.                                       |

<span id="page-379-1"></span>**Table 7-66. DC Region Configuration**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
|----------------|--------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 00h            | 8                  | Region Base: As defined in Table 8-180.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| 08h            | 8                  | Region Decode Length: As defined in Table 8-180.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| 10h            | 8                  | Region Length: As defined in Table 8-180.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| 18h            | 8                  | Region Block Size: As defined in Table 8-180.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| 20h            | 1                  | Note: More than one bit may be set at a time.<br>•<br>Bits[1:0]: Reserved<br>•<br>Bit[2]: NonVolatile: As defined in the Flags field of Device Scoped Memory<br>Affinity Structure defined in Coherent Device Attribute Table (CDAT)<br>Specification<br>•<br>Bit[3]: Sharable: As defined in the Flags field of Device Scoped Memory<br>Affinity Structure defined in CDAT Specification<br>•<br>Bit[4]: Hardware Managed Coherency: As defined in the Flags field of<br>Device Scoped Memory Affinity Structure defined in CDAT Specification<br>•<br>Bit[5]: Interconnect specific Dynamic Capacity Management: As<br>defined in the Flags field of Device Scoped Memory Affinity Structure defined<br>in CDAT Specification<br>•<br>Bit[6]: Read-Only: As defined in the Flags field of Device Scoped Memory<br>Affinity Structure defined in CDAT Specification<br>•<br>Bit[7]: Reserved |
| 21h            | 3                  | Reserved                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| 24h            | 1                  | •<br>Bit[0]: Sanitize on Release: As defined in Table 8-180<br>•<br>Bits[7:1]: Reserved                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| 25h            | 3                  | Reserved                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |

##### 7.6.7.6.3 Set DC Region Configuration (Opcode 5602h)

<span id="page-379-2"></span>This command sets the configuration of a DC Region for an LD-FAM DCD. This command shall be processed only when all capacity has been released from the region on all LDs. The device shall generate an Event Record of type Region Configuration Updated upon successful processing of this command.

This command shall fail with Unsupported under the following conditions:

- When all capacity has been released from the DC Region on all hosts, and one or more blocks are allocated to the specified region
- When the Sanitize on Release field does not match the region's configuration, as reported from the Get Host DC Region Configuration, and the device does not support reconfiguration of the Sanitize on Release setting, as advertised by the Sanitize on Release Configuration Support Mask in the Get DCD Info response payload

This command shall fail with Invalid Security State under the following condition:

• In support of confidential computing, if the device has been locked while utilizing secure CXL TSP interfaces, the device shall reject any attempts to change the DCD configuration by returning Invalid Security State status. See [Section 11.5](#page-931-2) for details on locking a device and locked device behavior.

**Possible Command Return Codes:**

- Success
- Unsupported
- Invalid Input
- Internal Error
- Retry Required
- Invalid Security State

**Command Effects:**

- Configuration Change after Cold Reset
- Configuration Change after Conventional Reset
- Configuration Change after CXL Reset
- Immediate Configuration Change
<span id="page-380-2"></span>- • Immediate Data Change

<span id="page-380-0"></span>**Table 7-67. Set DC Region Configuration Request and Response Payload**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                             |
|----------------|--------------------|-----------------------------------------------------------------------------------------|
| 0h             | 1                  | Region ID: Specifies which region to configure. Valid range is from 0 to 7.             |
| 1h             | 3                  | Reserved                                                                                |
| 4h             | 8                  | Region Block Size: As defined in Table 8-180.                                           |
| Ch             | 1                  | •<br>Bit[0]: Sanitize on Release: As defined in Table 8-180<br>•<br>Bits[7:1]: Reserved |
| Dh             | 3                  | Reserved                                                                                |

##### 7.6.7.6.4 Get DC Region Extent Lists (Opcode 5603h)

<span id="page-380-1"></span>This command sets the Dynamic Capacity Extent List for an LD-FAM DCD, for a specified host.

**Possible Command Return Codes:**

- Success
- Unsupported
- Invalid Input

- Internal Error
- Retry Required

**Command Effects:**

• None

<span id="page-381-0"></span>**Table 7-68. Get DC Region Extent Lists Request Payload**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                               |
|----------------|--------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h             | 2                  | Host ID: For an LD-FAM device, the LD-ID of the host interface.                                                                                                                                                                                                                                                           |
| 2h             | 2                  | Reserved                                                                                                                                                                                                                                                                                                                  |
| 4h             | 4                  | Extent Count: The maximum number of extents to return in the output response.<br>The device may not return more extents than requested; however, it can return<br>fewer extents. 0 is valid and allows the FM to retrieve the Total Extent Count and<br>Extent List Generation Number without retrieving any extent data. |
| 8h             | 4                  | Starting Extent Index: Index of the first requested extent. A value of 0 will<br>retrieve the first extent in the list.                                                                                                                                                                                                   |

<span id="page-381-1"></span>**Table 7-69. Get DC Region Extent Lists Response Payload**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                    |
|----------------|--------------------|----------------------------------------------------------------------------------------------------------------|
| 00h            | 2                  | Host ID: For an LD-FAM device, the LD-ID of the host interface query.                                          |
| 02h            | 2                  | Reserved                                                                                                       |
| 04h            | 4                  | Starting Extent Index: Index of the first extent in the list.                                                  |
| 08h            | 4                  | Returned Extent Count: The number of extents returned in Extent List[ ].                                       |
| 0Ch            | 4                  | Total Extent Count: The total number of extents in the list.                                                   |
| 10h            | 4                  | Extent List Generation Number: A device-generated value that is used to<br>indicate that the list has changed. |
| 14h            | 4                  | Reserved                                                                                                       |
| 18h            | Varies             | Extent List[ ]: Extent list for the specified host as defined in Table 8-63.                                   |

##### <span id="page-381-2"></span>7.6.7.6.5 Initiate Dynamic Capacity Add (Opcode 5604h)

<span id="page-381-3"></span>This command initiates the addition of Dynamic Capacity for an LD-FAM DCD, to the specified region on a host. This command shall complete when the device initiates the Add Capacity procedure, as defined in [Section 8.2.10.2.2.](#page-654-1) The processing of the actions initiated in response to this command may or may not result in a new entry or multiple entries grouped via the More flag (see [Table 8-62\)](#page-653-1) in the Dynamic Capacity Event Log. To perform Dynamic Capacity Add on a GFD, see [Section 8.2.10.9.10.7.](#page-763-1)

A Selection Policy is specified to govern the device's selection of which memory resources to add:

- **Free**: Unassigned extents are selected by the device, with no requirement for contiguous blocks
- **Contiguous**: Unassigned extents are selected by the device and shall be contiguous
- **Prescriptive**: Extent list of capacity to assign is included in the request payload
- **Enable Shared Access**: Enable access to extent(s) previously added to another host in a DC Region that reports the "Sharable" flag, as designated by the specified tag value

See [Section 9.13.3.2](#page-848-3) for examples of how this command may be used to set up different types of sharing arrangements.

The command shall fail with Invalid Input under the following conditions:

- When the command is sent with an invalid Host ID, or an invalid region number, or an unsupported Selection Policy
- When the Length field is not a multiple of the Block size and the Selection Policy is either Free or Contiguous

The command, with selection policy Enable Shared Access, shall also fail with Invalid Input under the following conditions:

- When the specified region is not Sharable
- When the tagged capacity is already mapped to any Host ID via a non-Sharable region
- When the tagged capacity cannot be added to the requested region due to deviceimposed restrictions
- When the same tagged capacity is currently accessible by the same LD

The command shall fail with Resources Exhausted when the length of the added capacity plus the current capacity present in all extents associated with the specified region exceeds the decode length for that region, or if there is insufficient contiguous space to satisfy a request with Selection Policy set to Contiguous.

The command shall fail with Invalid Extent List under the following conditions:

- When the Selection Policy is set to Prescriptive and the Extent Count is invalid
- When the Selection Policy is set to Prescriptive and any of the DPAs are already accessible to the same LD

The command shall fail with Resources Exhausted if the Extent List would cause the device to exceed its extent or tag tracking ability.

The command shall fail with Retry Required if its execution would cause the specified LD's Dynamic Capacity Event Log to overflow.

Possible Command Return Codes:

- Success
- Unsupported
- Invalid Input
- Internal Error
- Retry Required
- Invalid Extent List
- Resources Exhausted

**Command Effects:**

- Configuration Change after Cold Reset
- Configuration Change after Conventional Reset
- Configuration Change after CXL Reset
- Immediate Configuration Change
- Immediate Data Change

<span id="page-383-0"></span>**Table 7-70. Initiate Dynamic Capacity Add Request Payload**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                           |
|----------------|--------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 00h            | 2                  | Host ID: For an LD-FAM device, the LD-ID of the host interface to which the<br>capacity is being added.                                                                                                                                                                               |
| 02h            | 1                  | •<br>Bits[3:0]: Selection Policy: Specifies the policy to use for selecting which<br>extents comprise the added capacity:<br>— 0h = Free<br>— 1h = Contiguous<br>— 2h = Prescriptive<br>— 3h = Enable Shared Access<br>— All other encodings are reserved<br>•<br>Bits[7:4]: Reserved |
| 03h            | 1                  | Region Number: Dynamic Capacity Region to which the capacity is being added.<br>Valid range is from 0 to 7. This field is reserved when the Selection Policy is set to<br>Prescriptive.                                                                                               |
| 04h            | 8                  | Length: The number of bytes of capacity to add. Always a multiple of the<br>configured Region Block Size returned in Get DCD Info. Shall be > 0. This field is<br>reserved when the Selection Policy is set to Prescriptive or Enable Shared Access.                                  |
| 0Ch            | 10h                | Tag: Context field utilized by implementations that make use of the Dynamic<br>Capacity feature. This field is reserved when the Selection Policy is set to<br>Prescriptive.                                                                                                          |
| 1Ch            | 4                  | Extent Count: The number of extents in the Extent List. Present only when the<br>Selection Policy is set to Prescriptive.                                                                                                                                                             |
| 20h            | Varies             | Extent List: Extent list of capacity to add as defined in Table 8-63. Present only<br>when the Selection Policy is set to Prescriptive.                                                                                                                                               |

##### <span id="page-383-1"></span>7.6.7.6.6 Initiate Dynamic Capacity Release (Opcode 5605h)

<span id="page-383-2"></span>This command initiates the release of Dynamic Capacity for an LD-FAM DCD, from a host. This command shall complete when the device initiates the Remove Capacity procedure, as defined in [Section 8.2.10.9.9.](#page-750-3) The processing of the actions initiated in response to this command may or may not result in a new entry in the Dynamic Capacity Event Log. To perform Dynamic Capacity removal on a GFD, see [Section 8.2.10.9.10.8.](#page-764-1)

A removal policy is specified to govern the device's selection of which memory resources to remove:

- **Tag-based**: Extents are selected by the device based on tag, with no requirement for contiguous extents
- **Prescriptive**: Extent list of capacity to release is included in request payload

To remove a host's access to the shared extent, the FM issues Initiate Dynamic Capacity Release Request with Selection Policy=Tag-Based with the Host ID associated with that host. The Tag field must match the Tag value used during Capacity Add. The host access can be removed in any order. The physical memory resources and tag associated with a shared extent shall remain assigned and unavailable for re-use until that extent has been released from all hosts that have been granted access.

When the FM issues Initiate Dynamic Capacity Release Request with the Forced Removal flag set in order to release an extent in "Pending" state (as defined in [Section 9.13.3.3\)](#page-848-2), the request shall be fulfilled by the device marking the Extent Group as "Dead" without appending a new entry into the Dynamic Capacity Event Log. The Add Capacity Event records corresponding to the "Dead" Extent Group in the "Pending" list are unmodified. The "Dead" state is tracked internally by the device.

The command shall fail with Invalid Input under the following conditions:

- When the command is sent with an invalid Host ID, or an invalid region number, or an unsupported Removal Policy
- When the command is sent with a Removal Policy of Tag-based and the input Tag does not correspond to any currently allocated capacity
- When Sanitize on Release is set but is not supported by the device
- When the Tag represents sharable capacity, and the Extent List covers only a portion of the capacity associated with the Tag

The command shall fail with Resources Exhausted when the length of the removed capacity exceeds the total assigned capacity for that region or for the specified tag when the Removal Policy is set to Tag-based.

The command shall fail with Invalid Extent List when the Removal Policy is set to Prescriptive and the Extent Count is invalid or when the Extent List includes blocks that are not currently assigned to the region.

The command shall fail with Retry Required if its execution would cause the specified LD's Dynamic Capacity Event Log to overflow, unless the Forced Removal flag is set, in which case the removal occurs regardless of whether an Event is logged.

The command shall fail with Resources Exhausted if the Extent List would cause the device to exceed its extent or tag tracking ability.

The command shall fail with Invalid Physical Address if an extent in the extent list covers non-existening or pending ("Pending" state as defined in [Section 9.13.3.3](#page-848-2)) DPA range and the Forced Removal flag is not set.

Possible Command Return Codes:

- Success
- Unsupported
- Invalid Input
- Internal Error
- Retry Required
- Invalid Extent List
- Resources Exhausted

**Command Effects:**

- Configuration Change after Cold Reset
- Configuration Change after Conventional Reset
- Configuration Change after CXL Reset
- Immediate Configuration Change
- Immediate Data Change

<span id="page-385-0"></span>**Table 7-71. Initiate Dynamic Capacity Release Request Payload**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
|----------------|--------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 00h            | 2                  | Host ID: For an LD-FAM device, the LD-ID of the host interface from which the<br>capacity is being released.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| 02h            | 1                  | Flags<br>•<br>Bits[3:0]: Removal Policy: Specifies the policy to use for selecting which extents<br>comprise the released capacity:<br>— 0h = Tag-based<br>— 1h = Prescriptive<br>— All other encodings are reserved<br>•<br>Bit[4]: Forced Removal:<br>— 1 = Device does not wait for a Release Dynamic Capacity command from the<br>host. Host immediately loses access to released capacity.<br>•<br>Bit[5]: Sanitize on Release:<br>— 1 = Device shall sanitize all released capacity as a result of this request using<br>the method described in Section 8.2.10.9.5.1. If this is a shared capacity, the<br>sanitize operation shall be performed after the last host has released the<br>capacity.<br>•<br>Bits[7:6]: Reserved |
| 03h            | 1                  | Reserved                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| 04h            | 8                  | Length: The number of bytes of capacity to remove. Always a multiple of the<br>configured Region Block Size returned in Get DCD Info. Shall be > 0. This field is<br>reserved when the Removal Policy is set to Prescriptive.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| 0Ch            | 10h                | Tag: Optional opaque context field utilized by implementations that make use of the<br>Dynamic Capacity feature. This field is reserved when the Removal Policy is set to<br>Prescriptive.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| 1Ch            | 4                  | Extent Count: The number of extents in the Extent List. Present only when the<br>Removal Policy is set to Prescriptive.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| 20h            | Varies             | Extent List: Extent list of capacity to release as defined in Table 8-63. Present only<br>when the Removal Policy is set to Prescriptive.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |

##### <span id="page-385-1"></span>7.6.7.6.7 Dynamic Capacity Add Reference (Opcode 5606h)

<span id="page-385-2"></span>This command prevents the tagged sharable capacity for an LD-FAM DCD, from being sanitized, freed, and/or reallocated, regardless of whether it is currently visible to any hosts via extent lists. The tagged capacity will remain allocated, and contents will be preserved even if all DCD Extents that reference it are removed.

This command has no effect and will return Success if the FM has already added a reference to the tagged capacity.

This command shall return Invalid Input if the Tag in the payload does not match an existing sharable tag.

Possible Command Return Codes:

- Success
- Invalid Input
- Internal Error
- Retry Required

**Command Effects:**

- Configuration Change after Cold Reset
- Configuration Change after Conventional Reset
- Configuration Change after CXL Reset
- Immediate Configuration Change

<span id="page-386-0"></span>**Table 7-72. Dynamic Capacity Add Reference Request Payload**

| Byte<br>Offset | Length<br>in Bytes | Description                                                           |
|----------------|--------------------|-----------------------------------------------------------------------|
| 00h            | 10h                | Tag: Tag that is associated with the memory capacity to be preserved. |

##### 7.6.7.6.8 Dynamic Capacity Remove Reference (Opcode 5607h)

<span id="page-386-2"></span>This command removes a reference to tagged sharable capacity for an LD-FAM DCD, that was previously added via Dynamic Capacity Add Reference (see [Section 7.6.7.6.7](#page-385-1)). If there are no remaining extent lists that reference the tagged capacity, the memory will be freed and sanitized if appropriate.

This command shall return Invalid Input if the Tag in the payload does not match an existing sharable tag.

Possible Command Return Codes:

- Success
- Invalid Input
- Internal Error
- Retry Required

**Command Effects:**

- Configuration Change after Cold Reset (if freed)
- Configuration Change after Conventional Reset (if freed)
- Configuration Change after CXL Reset (if freed)
- Immediate Configuration Change (if freed)

<span id="page-386-1"></span>**Table 7-73. Dynamic Capacity Remove Reference Request Payload**

| Byte<br>Offset | Length<br>in Bytes | Description                                           |
|----------------|--------------------|-------------------------------------------------------|
| 00h            | 10h                | Tag: Tag that is associated with the memory capacity. |

##### 7.6.7.6.9 Dynamic Capacity List Tags (Opcode 5608h)

<span id="page-386-3"></span>This command allows an FM to re-establish context for an LD-FAM DCD, by receiving a list of all existing tags, with bitmaps indicating which LDs have access, and a flag indicating whether the FM holds a reference.

Possible Command Return Codes:

- Success
- Invalid Input
- Internal Error

**Command Effects:**

<span id="page-387-1"></span>**Table 7-74. Dynamic Capacity List Tags Request Payload**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                            |
|----------------|--------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 00h            | 04h                | Starting Index: Index of the first tag to return.                                                                                                                      |
| 04h            | 04h                | Max Tags: Maximum number of tags to return in the response payload. If Max Tags is<br>0, no tags list will be returned; however, the Generation Number shall be valid. |

<span id="page-387-2"></span>**Table 7-75. Dynamic Capacity List Tags Response Payload**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                      |  |  |
|----------------|--------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--|--|
| 00h            | 4                  | Generation Number: Generation number of the tags list. This number shall change<br>every time the remainder of the command's payload would change.                                                                                                                                                                                                                                                                                                               |  |  |
| 04h            | 4                  | Total Number of Tags: Maximum number of tags to return in the response payload.                                                                                                                                                                                                                                                                                                                                                                                  |  |  |
| 08h            | 4                  | Number of Tags Returned: Number of tags returned in the Tags List.                                                                                                                                                                                                                                                                                                                                                                                               |  |  |
| 0Ch            | 1                  | Validity Bitmap<br>•<br>Bit[0]: Reference Bitmaps Valid: A value of 1 indicates that the Reference<br>Bitmap fields in the Tags List are valid. This bit shall be 0 for GFDs and 1 for all<br>other device types.<br>•<br>Bit[1]: Pending Reference Bitmaps Valid: A value of 1 indicates that the<br>Pending Reference Bitmap fields in the Tags List are valid. This bit shall be 0 for<br>GFDs and 1 for all other device types.<br>•<br>Bits[7:2]: Reserved. |  |  |
| 0Dh            | 3                  | Reserved                                                                                                                                                                                                                                                                                                                                                                                                                                                         |  |  |
| 10h            | Varies             | Tags List: List of Dynamic Capacity Tag Information structures. The format of each<br>entry is defined in Table 7-76.                                                                                                                                                                                                                                                                                                                                            |  |  |

<span id="page-387-3"></span>**Table 7-76. Dynamic Capacity Tag Information**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                                                                                   |  |
|----------------|--------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--|
| 00h            | 10h                | Tag: Tag that is associated with the memory capacity.                                                                                                                                                                                                                                                                                                                         |  |
| 10h            | 1                  | Flags<br>•<br>Bit[0]: FM Holds Reference: When set, this bit indicates that the FM holds a<br>reference on this Tag.<br>•<br>Bits[7:1]: Reserved.                                                                                                                                                                                                                             |  |
| 11h            | 3                  | Reserved                                                                                                                                                                                                                                                                                                                                                                      |  |
| 14h            | 20h                | Reference Bitmap: Each 1 indicates an LD that has accepted the capacity associated<br>with this tag. Bit 0 of the first byte represents LD 0, and bit 7 of the last byte<br>represents LD 255. This field is reserved if the Reference Bitmaps Valid bit is not set in<br>the Dynamic Capacity List Tags Response Payload (see Table 7-75).                                   |  |
| 34h            | 20h                | Pending Reference Bitmap: Each 1 indicates an LD for which the tagged capacity has<br>been added with no host response yet. Bit 0 of the first byte represents LD 0, and bit 7<br>of the last byte represents LD 255. This field is reserved if the Pending Reference<br>Bitmaps Valid bit is not set in the Dynamic Capacity List Tags Response Payload (see<br>Table 7-75). |  |

### <span id="page-387-0"></span>7.6.8 Fabric Management Event Records

The FM API uses the Event Records framework defined in [Section 8.2.10.2.1.](#page-638-3) This section defines the format of event records specific to Fabric Management activities.

#### <span id="page-388-0"></span>7.6.8.1 Physical Switch Event Records

<span id="page-388-2"></span>Physical Switch Event Records define events that are related to physical switch ports, as defined in [Table 7-77.](#page-388-1)

<span id="page-388-1"></span>**Table 7-77. Physical Switch Events Record Format**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                        |  |  |
|----------------|--------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--|--|
| 00h            | 30h                | Common Event Record: See corresponding common event record fields<br>defined in Section 8.2.10.2.1. The Event Record Identifier field shall be set to<br>77cf9271-9c02-470b-9fe4-bc7b75f2da97, which identifies a Physical Switch<br>Event Record. |  |  |
| 30h            | 1                  | Physical Port ID: Physical Port that is generating the event.                                                                                                                                                                                      |  |  |
| 31h            | 1                  | Event Type: Identifies the type of event that occurred:<br>•<br>00h = Link State Change<br>•<br>01h = Slot Status Register Updated                                                                                                                 |  |  |
| 32h            | 2                  | Slot Status Register: As defined in PCIe Base Specification.                                                                                                                                                                                       |  |  |
| 34h            | 1                  | Reserved                                                                                                                                                                                                                                           |  |  |
| 35h            | 1                  | •<br>Bits[3:0]: Current Port Configuration State: See Table 7-19<br>•<br>Bits[7:4]: Reserved                                                                                                                                                       |  |  |
| 36h            | 1                  | •<br>Bits[3:0] Connected Device Mode: See Table 7-19<br>•<br>Bits[7:4]: Reserved                                                                                                                                                                   |  |  |
| 37h            | 1                  | Reserved                                                                                                                                                                                                                                           |  |  |
| 38h            | 1                  | Connected Device Type: See Table 7-19                                                                                                                                                                                                              |  |  |
| 39h            | 1                  | Supported CXL Modes: See Table 7-19                                                                                                                                                                                                                |  |  |
| 3Ah            | 1                  | •<br>Bits[5:0]: Maximum Link Width: Value encoding matches the Maximum<br>Link Width field in the PCIe Link Capabilities register in the PCIe Capability<br>structure<br>•<br>Bits[7:6]: Reserved                                                  |  |  |
| 3Bh            | 1                  | •<br>Bits[5:0]: Negotiated Link Width: Value encoding matches the<br>Negotiated Link Width field in the PCIe Link Capabilities register in the PCIe<br>Capability structure<br>•<br>Bits[7:6]: Reserved                                            |  |  |
| 3Ch            | 1                  | •<br>Bits[5:0]: Supported Link Speeds Vector: Value encoding matches the<br>Supported Link Speeds Vector field in the PCIe Link Capabilities 2 register in<br>the PCIe Capability structure<br>•<br>Bits[7:6]: Reserved                            |  |  |
| 3Dh            | 1                  | •<br>Bits[5:0]: Max Link Speed: Value encoding matches the Max Link Speed<br>field in the PCIe Link Capabilities register in the PCIe Capability structure<br>•<br>Bits[7:6]: Reserved                                                             |  |  |
| 3Eh            | 1                  | •<br>Bits[5:0]: Current Link Speed: Value encoding matches the Current Link<br>Speed field in the PCIe Link Status register in the PCIe Capability structure<br>•<br>Bits[7:6]: Reserved                                                           |  |  |
| 3Fh            | 1                  | LTSSM State: See Section 7.6.7.1.                                                                                                                                                                                                                  |  |  |
| 40h            | 1                  | First Negotiated Lane Number: Lane number of the lowest lane that has<br>negotiated.                                                                                                                                                               |  |  |
| 41h            | 2                  | Link state flags: See Section 7.6.7.1.                                                                                                                                                                                                             |  |  |
| 43h            | 3Dh                | Reserved                                                                                                                                                                                                                                           |  |  |

#### <span id="page-389-0"></span>7.6.8.2 Virtual CXL Switch Event Records

<span id="page-389-2"></span>Virtual CXL Switch Event Records define events that are related to VCSs and vPPBs, as defined in [Table 7-78](#page-389-1).

<span id="page-389-1"></span>**Table 7-78. Virtual CXL Switch Event Record Format**

| Byte<br>Length<br>Offset<br>in Bytes |     | Description                                                                                                                                                                                                                                                                                                                                                          |  |
|--------------------------------------|-----|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--|
| 00h                                  | 30h | Common Event Record: See corresponding common event record fields<br>defined in Section 8.2.10.2.1. The Event Record Identifier field shall be set to<br>40d26425-3396-4c4d-a5da-3d47263af425, which identifies a Virtual Switch<br>Event Record.                                                                                                                    |  |
| 30h                                  | 1   | VCS ID                                                                                                                                                                                                                                                                                                                                                               |  |
| 31h                                  | 1   | vPPB ID                                                                                                                                                                                                                                                                                                                                                              |  |
| 32h                                  | 1   | Event Type: Identifies the type of event that occurred:<br>•<br>00h = Binding Change<br>•<br>01h = Secondary Bus Reset<br>•<br>02h = Link Control Register Updated<br>•<br>03h = Slot Control Register Updated                                                                                                                                                       |  |
| 33h                                  | 1   | vPPB Binding Status: Current vPPB binding state, as defined in Table 7-32. If<br>Event Type is 00h, this field contains the updated binding state of a vPPB<br>following the binding change. Successful bind and unbind operations generate<br>events to the Informational Event Log. Failed bind and unbind operations<br>generate events to the Warning Event Log. |  |
| 34h                                  | 1   | vPPB Port ID: Current vPPB bound port ID, as defined in Table 7-32. If Event<br>Type is 00h, this field contains the updated binding state of a vPPB following<br>the binding change. Successful bind and unbind operations generate events to<br>the Informational Event Log. Failed bind and unbind operations generate events<br>to the Warning Event Log.        |  |
| 35h                                  | 1   | vPPB LD ID: Current vPPB bound LD-ID, as defined in Table 7-32. If Event<br>Type is 00h, this field contains the updated binding state of a vPPB following<br>the binding change. Successful bind and unbind operations generate events to<br>the Informational Event Log. Failed bind and unbind operations generate events<br>to the Warning Event Log.            |  |
| 36h                                  | 2   | Link Control Register Value: Current Link Control register value, as defined<br>in PCIe Base Specification.                                                                                                                                                                                                                                                          |  |
| 38h                                  | 2   | Slot Control Register Value: Current Slot Control register value, as defined in<br>PCIe Base Specification.                                                                                                                                                                                                                                                          |  |
| 3Ah                                  | 46h | Reserved                                                                                                                                                                                                                                                                                                                                                             |  |

#### <span id="page-390-0"></span>7.6.8.3 MLD Port Event Records

<span id="page-390-4"></span>MLD Port Event Records define events that are related to switch ports connected to MLDs, as defined in [Table 7-79](#page-390-2).

<span id="page-390-2"></span>**Table 7-79. MLD Port Event Records Payload**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                                                                                                           |  |
|----------------|--------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--|
| 00h            | 30h                | Common Event Record: See corresponding common event record fields<br>defined in Section 8.2.10.2.1. The Event Record Identifier field shall be set to<br>8dc44363-0c96-4710-b7bf-04bb99534c3f, which identifies an MLD Port Event<br>Record.                                                                                                                                                          |  |
| 30h            | 1                  | Event Type: Identifies the type of event that occurred:<br>•<br>00h = Error Correctable Message Received. Events of this type shall be<br>added to the Warning Event Log.<br>•<br>01h = Error Non-Fatal Message Received. Events of this type shall be added<br>to the Failure Event Log.<br>•<br>02h = Error Fatal Message Received. Events of this type shall be added to<br>the Failure Event Log. |  |
| 31h            | 1                  | Port ID: ID of the MLD port that is generating the event.                                                                                                                                                                                                                                                                                                                                             |  |
| 32h            | 2                  | Reserved                                                                                                                                                                                                                                                                                                                                                                                              |  |
| 34h            | 8                  | Error Message: The first 8 bytes of the PCIe error message (ERR_COR,<br>ERR_NONFATAL, or ERR_FATAL) that is received by the switch.                                                                                                                                                                                                                                                                   |  |
| 3Ch            | 44h                | Reserved                                                                                                                                                                                                                                                                                                                                                                                              |  |

## <span id="page-390-1"></span>7.7 CXL Fabric Architecture

<span id="page-390-3"></span>The CXL fabric architecture adds new features to scale from a node to a rack-level interconnect to service the growing computational needs in many fields. Machine learning/AI, drug discovery, agricultural and life sciences, materials science, and climate modeling are some of the fields with significant computational demand. The computation density required to meet the demand is driving innovation in many areas, including near and in-memory computing. CXL Fabric features provide a robust path to build flexible, composable systems at rack scale that are able to capitalize on simple load/store memory semantics or Unordered I/O (UIO).

CXL fabric extensions allow for topologies of interconnected fabric switches using 12-bit PIDs (SPIDs/DPIDs) to uniquely identify up to 4096 Edge Ports. The following are the main areas of change to extend CXL as an interconnect fabric for server composability and scale-out systems:

- Expand the size of CXL fabric using Port Based Routing and 12-bit PIDs.
- Enable support for G-FAM devices (GFDs). A GFD is a highly scalable memory resource that is accessible by all hosts and all peer devices.
- Host and device peer communication may be enabled using UIO.

<span id="page-391-2"></span>**Figure 7-25. High-level CXL Fabric Diagram**

![](_page_391_Figure_3.jpeg)

[Figure 7-25](#page-391-2) is a high-level illustration of a routable CXL Fabric. The fabric consists of one or more interconnected fabric switches. In this figure, there are "n" Switch Edge Ports (SEPi ) on the Fabric where each Edge Port can connect to a CXL host root port or a CXL/PCIe device (Dev). As shown, a Fabric Manager (FM) connects to the CXL Fabric and may connect to selected endpoints over an out-of-band management network. The management network may be a simple 2-wire interface, such as SMBus, I2C, I3C, or a complex fabric such as Ethernet. The FM is responsible for the initialization and setup of the CXL Fabric and the assignment of devices to different Virtual Hierarchies. Extensions to FM API (see [Section 7.6](#page-344-0)) to handle cross-domain traffic will be taken up as a future ECN.

Initially, the FM binds a set of devices to the host's Virtual Hierarchies, essentially composing a system. After the system has booted, the FM may add or remove devices from the system using fabric bind and unbind operations. These system changes are presented to the hosts by the fabric switches as managed Hot-Add and Hot-Remove events as described in [Section 9.9](#page-811-1). This allows for dynamic reconfiguration of systems that are composed of hosts and devices.

Root ports on the CXL Fabric may be part of the same or different domains. If the root ports are in different domains, hardware coherency across those root ports is not a requirement. However, devices that support sharing (including MLDs, Multi-Headed devices, and GFDs) may support hardware-managed cache coherency across root ports in multiple domains.

### <span id="page-391-0"></span>7.7.1 CXL Fabric Use Case Examples

Following are a few examples of systems that may benefit from using CXL-switched Fabric for low-latency communication.

#### <span id="page-391-1"></span>7.7.1.1 Machine-learning Accelerators

Accelerators used for machine-learning applications may use a dedicated CXL-switched Fabric for direct communication between devices in different domains. The same Fabric may also be used for sharing GFDs among accelerators. Each host and accelerator of same color shown in [Figure 7-26](#page-392-2) (basically, those that are directly above and below one another) belongs to a single domain. Accelerator devices can use UIO transactions to access memory on other accelerator and GFDs. In such a system, each accelerator is attached to a host and expected to be hardware-cache coherent with the host when using a CXL link. Communication between accelerators across domains is via the I/O coherency model. Device caching of data from another device memory (HDM or PDM) requires software-managed coherency with appropriate cache flushes and barriers. A

Switch Edge ingress port is expected to implement a common set of address decoders that is to be used for Upstream Ports and Downstream Ports. Implementations may enable a dedicated CXL Fabric for accelerators using features available in this revision. However, it is not fully defined by the specification. Peer communication is defined in [Section 7.7.9](#page-441-1).

<span id="page-392-2"></span>**Figure 7-26. ML Accelerator Use Case**

![](_page_392_Figure_4.jpeg)

#### <span id="page-392-0"></span>7.7.1.2 HPC/Analytics Use Case

High-performance computing and Big Data Analytics are two areas that may also benefit from a dedicated CXL Fabric for host-to-host communication and sharing of G-FAM. CXL.mem or UIO may be used to access GFDs. Some G-FAM implementations may enable cross-domain hardware cache coherency. Software cache coherency may still be used for shared-memory implementations. Host-to-host communication is defined in [Section 7.7.3.](#page-405-0)

<span id="page-392-3"></span>NICs may be used to directly move data from network storage to G-FAM devices, using the UIO traffic class. CXL.mem and UIO use fabric address decoders to route to target GFDs that are members of many domains.

**Figure 7-27. HPC/Analytics Use Case**

![](_page_392_Figure_9.jpeg)

#### <span id="page-392-1"></span>7.7.1.3 Composable Systems

Support for multi-level switches with PBR fabric extensions provides additional capabilities for building software-composable systems. In [Figure 7-28](#page-393-2), a leaf/spine switch architecture is shown in which all resources are attached to the leaf switches. Each domain may span multiple switches. All devices must be bound to a host or an FM. Cross-domain traffic is limited to CXL.mem and UIO transactions.

Composing systems from resources within a single leaf switch allows for low-latency implementations. In such implementations, a spine switch is used only for cross-domain and G-FAM accesses.

<span id="page-393-2"></span>Figure 7-28. Sample System Topology for Composable Systems

**Figure 7-28.**

![](_page_393_Figure_4.jpeg)

### <span id="page-393-0"></span>7.7.2 Global-Fabric-Attached Memory (G-FAM)

### <span id="page-393-1"></span>7.7.2.1 Overview

<span id="page-393-3"></span>G-FAM provides a highly scalable memory resource that is accessible by all hosts and peer devices within a CXL fabric. G-FAM ranges can be assigned exclusively to a single host/peer requester or can be shared by multiple hosts/peers. When shared, multi-requester cache coherency can be managed by either software or hardware. Access rights to G-FAM ranges are enforced by decoders in Requester Edge ports and the target GFD.

GFD HDM space can be accessed by hosts/peers from multiple domains using CXL.mem, and by peer devices from multiple domains using CXL.io UIO. GFDs implement no PCIe configuration space, and they are configured and managed instead via Global Memory Access Endpoints (GAEs) in Edge USPs or via out-of-band mechanisms.

Unlike an MLD, which has a separate Device Physical Address (DPA) space for each host/peer interface (LD), a GFD has one DPA space that is common across all hosts and peer devices. The GFD translates the Host Physical Address (HPA)<sup>1</sup> in each incoming request into a DPA, using per-requester translation information that is stored within the GFD Decoder Table. To create shared memory, two or more HPA ranges (each from a different requester) are mapped to the same DPA range. When the GFD needs to issue a BISnp, the GFD translates the DPA into an HPA for the associated host using the same GFD decoder information.

When a GFD receives a request, the requester is identified by the SPID in the request, which is referred to as the Requester PID or RPID. Using this term avoids confusion when describing messages that the GFD sends to the requester, where the RPID is used for the DPID, and the GFD PID is used for the SPID.

<sup>1. &</sup>quot;HPA" is used for peer device requests in addition to host requests, even though "HPA" is a misnomer for some peer-device use cases.

All memory capacity on a GFD is managed by the Dynamic Capacity (DC) mechanisms, as defined in [Section 8.2.10.9.9.](#page-750-3) A GFD allows each requester to access up to 8 RPID non-overlapping decoders, where the maximum number of decoders per SPID is implementation dependent. Each decoder has a translation from HPA space to the common DPA space, a flag that indicates whether cache coherency is maintained by software or hardware, and information about multi-GFD interleaving, if used. For each requester, the FM may define DC Regions in DPA space and convey this information to the host via a GAE. It is expected that the host will program the Fabric Address Segment Table (FAST) decoders and GFD decoders for all RPIDs in its domain to map the entire DPA range of each DC Region that needs to be accessed by the host or by one of its associated accelerators.

G-FAM memory ranges can be interleaved across any power-of-two number of GFDs from 2 to 256, with an Interleave Granularity of 256B, 512B, 1 KB, 2 KB, 4 KB, 8 KB, or 16 KB. GFDs that are located anywhere within the CXL fabric, as defined in [Section 2.7,](#page-82-3) may be used to contribute memory to an Interleave Set.

If a GFD supports UIO Direct P2P to HDM (see [Section 7.7.9.1\)](#page-442-0), all GFD ports shall support UIO, and for each GFD link whose link partner also supports UIO, VC3 shall be auto-enabled by the ports (see [Section 7.7.11.5.1](#page-454-1)).

#### <span id="page-394-0"></span>7.7.2.2 Host Physical Address View

Hosts that access G-FAM shall allocate a contiguous address range for Fabric Address space within their Host Physical Address (HPA) space, as shown in [Figure 7-29.](#page-395-1) The Fabric Address range is defined by the FabricBase and FabricLimit registers. All host requests that fall within the Fabric Address range are routed to a selected CXL port. Hosts that use multiple CXL ports for G-FAM may either address interleave requests across the ports or may allocate a Fabric Address space for each port.

G-FAM requests from a host flow to a PBR Edge USP. In the USP, the Fabric Address range is divided into N equal-sized segments. A segment may be any power-of-two size from 64 GB to 8 TB, and must be naturally aligned. The number of segments implemented by a switch is implementation dependent. Host software is responsible for configuring the segment size so that the number of segments times the segment size fully spans the Fabric Address space. The FabricBase and FabricLimit registers can be programmed to any multiple of the segment size.

Each segment has an associated GFD or Interleave Set of GFDs. Requests whose HPA falls anywhere within the segment are routed to the specified GFD or to a GFD within the Interleave Set. Segments are used only for request routing and may be larger than the accessible portion of a GFD. When this occurs, the accessible portion of the GFD starts at address offset zero within the segment. Any requests within the segment that are above the accessible portion of the GFD will fail to positively decode in the GFD and will be handled as described in [Section 8.2.4.20.](#page-564-1)

Host interleaving across root ports is entirely independent from GFD interleaving. Address bits that are used for root port interleaving and for GFD interleaving may be fully overlapping, partially overlapping, or non-overlapping. When the host uses root port interleaving, FabricBase, FabricLimit, and segment size in the corresponding PBR Edge USPs must be identically configured.

#### <span id="page-395-0"></span>7.7.2.3 G-FAM Capacity Management

<span id="page-395-1"></span>**Figure 7-29. Example Host Physical Address View**

<span id="page-395-2"></span>![](_page_395_Figure_4.jpeg)

GFDs are managed using CCIs like all other classes of CXL components. A GFD requires support for the PBR Link CCI message format, as defined in [Section 7.7.11.6](#page-456-0), on its CXL link and may optionally implement additional MCTP-based CCIs (e.g., SMBus).

G-FAM relies exclusively on the Dynamic Capacity (DC) mechanism for capacity management, as described in [Section 8.2.10.9.9.](#page-750-3) GFDs have no "legacy" static capacity as shown in the left side of [Figure 9-24](#page-845-1) in [Chapter 9.0.](#page-798-3) Dynamic Capacity for G-FAM has much in common with the Dynamic Capacity for LD-FAM:

- Both have identical concepts for DC Regions, Extents, and Blocks
- Both support up to 8 DC Regions per host/peer interface
- DC-related parameters in the CDAT for each are identical
- Mailbox commands for each are highly similar; however, the specific Mailbox access methods are considerably different
  - For LD-FAM, the Mailbox for each host's LD is accessed via LD structures
  - For G-FAM, management for each host is defined in [Section 7.7.2.6](#page-403-0)

An LD-FAM DCD (i.e., DCD-capable SLDs or MLDs) allocates memory capacity and binds it to a specific Host ID in one operation. A GFD allocates Dynamic Capacity to a named Memory Group in one operation and binds specific Host IDs to named Memory Groups in a separate operation. Thus, the GFD requires different DCD Management commands than LD-FAM DCDs.

In contrast to LD-FAM, each GFD has a single DPA space instead of a separate DPA space per host. G-FAM DPA space is organized by Device Media Partitions (DMPs), as shown in [Figure 7-30.](#page-396-0) DMPs are DPA ranges with certain attributes. A fundamental DMP

attribute is the media type (e.g., DRAM or PM). A DMP attribute that is configured by the FM is the DC Block size. DMPs expose all GFD memory that is assignable for host use.

The rules for DMPs are as follows:

- Each GFD contains 1-4 DMPs, whose size is configured by the FM.
- Each DC Region consists of part or all of one DMP assigned to a host/peer. Each DC Region can be mapped into an RPID's HPA space using the GFD Decoder Table.
- Each DC Region inherits associated DMP attributes.

<span id="page-396-0"></span>**Figure 7-30. Example HPA Mapping to DMPs**

![](_page_396_Figure_8.jpeg)
**Figure 7-31. GFD requests may**


[Table 7-80](#page-396-1) lists the key differences between LD-FAM and G-FAM.

<span id="page-396-1"></span>**Table 7-80. Differences between LD-FAM and G-FAM (Sheet 1 of 2)**

| Feature or Attribute                                          | LD-FAM | G-FAM                                         |
|---------------------------------------------------------------|--------|-----------------------------------------------|
| Number of supported hosts                                     | 16 max | 1000s architecturally;<br>100s more realistic |
| Support for DMPs                                              | No     | Yes                                           |
| Architected FM API support for<br>DMP configuration by the FM | N/A    | Yes                                           |

**Table 7-80. Differences between LD-FAM and G-FAM (Sheet 2 of 2)**

| Feature or Attribute                           | LD-FAM                                                                                                                                                                              | G-FAM                                                                                                                                         |  |
|------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------|--|
| Routing and decoders used for<br>HDM addresses | Interleave RP routing by host<br>HDM Decoder<br>Interleave VH routing by USP<br>HDM Decoder<br>Interleave fabric routing by USP<br>LDST/IDT decoder<br>1–10 HDM Decoders in each LD | Interleave RP routing by host HDM<br>Decoder<br>Interleave fabric routing by USP FAST/<br>IDT decoder<br>1–8 GFD Decoders per RPID in the GFD |  |
| Interleave Ways (IW)                           | 1/2/4/8/16 plus 3/6/12                                                                                                                                                              | 2–256 in powers of 2                                                                                                                          |  |
| DC Block Size                                  | Powers of 2, as indicated by<br>Region * Supported Block Size<br>Mask                                                                                                               | 64 MB and up in powers of 2                                                                                                                   |  |

Additional differences exist in how MLDs and GFDs process requests. An MLD has three types of decoders that operate sequentially on incoming requests:

- Per-LD HDM decoders translate from HPA space to a per-LD DPA space, removing the interleaving bits
- Per-LD decoders determine within which per-LD DC Region the DPA resides, and then whether the addressed DC block within the Region is accessible by the LD
- Per-LD implementation-dependent decoders translate from the DPA to the media address

A GFD has two types of decoders that operate sequentially on incoming requests:

- Per-RPID GFD decoders translate from HPA space to a common DPA space, removing the interleaving bits. This DPA may be used as the media address directly or via a simple mapping.
<span id="page-397-1"></span>- • A common decoder determines within which Device Media Partition (DMP) the DPA is located, and then whether the block that is addressed within the DMP is accessible by the RPID.

#### <span id="page-397-0"></span>7.7.2.4 G-FAM Request Routing, Interleaving, and Address Translations

The mechanisms for GFD request routing, interleaving, and address translations within both the Edge ingress port and the GFD are shown in [Figure 7-31](#page-398-0). GFD requests may arrive either at an Edge USP from a host or at an Edge DSP from a peer device. This is referred to as the Edge request port.

<span id="page-398-0"></span>Figure 7-31. G-FAM Request Routing, Interleaving, and Address Translations

![](_page_398_Figure_3.jpeg)

The Edge request port shall decode the request HPA to determine the DPID of the target GFD using the FAST $^1$  and the Interleave DPID Table (IDT). The FAST contains one entry per segment. The FAST depth must be a power-of-two but is implementation dependent. The segment size is specified by the FSegSz[2:0] register as defined in Table 7-81. The FAST entry accessed is determined by bits X:Y of the request address, where Y = log2 of the segment size in bytes and X = Y + log2 of the FAST depth in entries. The maximum Fabric Address space and the HPA bits that are used to address the FAST are shown in Table 7-81 for all supported segment sizes for some example FAST depths. For a host with a 52-bit HPA, the maximum Fabric Address space is 4 PB minus one segment each above and below the Fabric Address space for local memory and for MMIO, as shown in Figure 7-29.

<sup>1.</sup> This section covers using FAST decoders with G-FAM. The LD-FAM Segment Table (LDST) decoders used with LD-FAM have identical functionality with few exceptions. Table 7-81, Table 7-82, and Table 7-83 apply to LD-FAM as well as to G-FAM.

<span id="page-399-0"></span>**Table 7-81. Fabric Segment Size Table<sup>1</sup>**

|             | Fabric<br>Segment Size | FAST Depth (Entries) |                           |                           |                             |
|-------------|------------------------|----------------------|---------------------------|---------------------------|-----------------------------|
| FSegSz[2:0] |                        | 256                  | 1K                        | 4K                        | 16K                         |
| 000b        | 64 GB                  | 16 TB<br>HPA[43:36]  | 64 TB<br>HPA[45:36]       | 256 TB<br>HPA[47:36]      | 1 PB<br>HPA[49:36]          |
| 001b        | 128 GB                 | 32 TB<br>HPA[44:37]  | 128 TB<br>HPA[46:37]      | 512 TB<br>HPA[48:37]      | 2 PB<br>HPA[50:37]          |
| 010b        | 256 GB                 | 64 TB<br>HPA[45:38]  | 256 TB<br>HPA[47:38]      | 1 PB<br>HPA[49:38]        | 4 PB – 512 GB<br>HPA[51:38] |
| 011b        | 512 GB                 | 128 TB<br>HPA[46:39] | 512 TB<br>HPA[48:39]      | 2 PB<br>HPA[50:39]        |                             |
| 100b        | 1 TB                   | 256 TB<br>HPA[47:40] | 1 PB<br>HPA[49:40]        | 4 PB – 2 TB<br>HPA[51:40] |                             |
| 101b        | 2 TB                   | 512 TB<br>HPA[48:41] | 2 PB<br>HPA[50:41]        |                           |                             |
| 110b        | 4 TB                   | 1 PB<br>HPA[49:42]   | 4 PB – 8 TB<br>HPA[51:42] |                           |                             |
| 111b        | 8 TB                   | 2 PB<br>HPA[50:43]   |                           |                           |                             |

<sup>1.</sup> LDST Segment Size (LSegSz) uses the same encodings as those defined for FSegSz.

Each FAST entry contains a valid bit (V), the number of interleaving ways (Intlv), the interleave granularity (Gran), and a DPID or IDT index (DPID/IX). The encodings for the Intlv and Gran fields are defined in [Table 7-82](#page-399-1) and [Table 7-83](#page-400-0), respectively. If the HPA is between FabricBase and FabricLimit inclusive and the FAST entry valid bit is set, then there is a FAST hit, and the FAST is used to determine the DPID. Otherwise, the target device is determined by other architected decoders.

<span id="page-399-1"></span>**Table 7-82. Segment Table Intlv[3:0] Field Encoding**

| Intlv[3:0] | GFD Interleaving Ways    |  |
|------------|--------------------------|--|
| 0h         | Interleaving is disabled |  |
| 1h         | 2-way interleaving       |  |
| 2h         | 4-way interleaving       |  |
| 3h         | 8-way interleaving       |  |
| 4h         | 16-way interleaving      |  |
| 5h         | 32-way interleaving      |  |
| 6h         | 64-way interleaving      |  |
| 7h         | 128-way interleaving     |  |
| 8h         | 256-way interleaving     |  |
| 9h – Fh    | Reserved                 |  |

<span id="page-400-0"></span>**Table 7-83. Segment Table Gran[3:0] Field Encoding**

| Gran [3:0] | GFD Interleave Granularity |
|------------|----------------------------|
| 0h         | 256B                       |
| 1h         | 512B                       |
| 2h         | 1 KB                       |
| 3h         | 2 KB                       |
| 4h         | 4 KB                       |
| 5h         | 8 KB                       |
| 6h         | 16 KB                      |
| 7h – Fh    | Reserved                   |

Note that FabricBase and FabricLimit may be used to restrict the amount of the FAST used. For example, for a host with a 52-bit HPA space, if the FAST is accessed using HPA[51:40] without restriction, then it would consume the entire HPA space. In this case, FabricBase and FabricLimit must be set to restrict the Fabric Address space to the desired range of HPA space. This has the effect of reducing the number of entries in the FAST that are being used.

FabricBase and FabricLimit may also be used to allow the FAST to start at an HPA that is not a multiple of the FAST depth. For example, for a host with a 52-bit HPA space, if 2 PB of Fabric Address space is needed to start at an HPA of 1 PB, then a 4K entry FAST with 512 GB segments can be accessed using HPA[50:39] with FabricBase set to 1 PB and FabricLimit set to 3 PB. HPAs 1 PB to 2 PB-1 will then correspond to FAST entries 2048 to 4095, while HPAs 2 PB to 3 PB-1 will wrap around and correspond to FAST entries 0 to 2047. When programming FabricBase, FabricLimit, and segment size, care must be taken to ensure that a wraparound does not occur that would result in aliasing multiple HPAs to the same segment.

On a FAST hit, if the FAST Intlv field is 0h, then GFD interleaving is not being used for this segment and the DPID/IX field contains the GFD's DPID. If the Intlv field is nonzero, then the Interleave Way is selected from the HPA using the Gran and Intlv fields, and then added to the DPID/IX field to generate an index into the IDT. The IDT defines the set of DPIDs for each Interleave Set that is accessible by the Edge request port. For an N-way Interleave Set, the set of DPIDs is determined by N contiguous entries in the IDT, with the first entry pointed to by DPID/IX which may be anywhere in the IDT. The IDT depth is implementation dependent.

After the GFD's DPID is determined, a request that contains the SPID of the Edge request port and the unmodified HPA is sent to the target GFD. The GFD shall then use the SPID to access the GFD Decoder Table (GDT) to select the decoders that are associated with the requester. Note that a host and its associated CXL devices will each have a unique RPID, and therefore each will use a different entry in the GDT. The GDT provides up to 8 decoders per RPID. Each decoder within a GFD Decoder Table entry contains structures defined in [Section 8.2.10.9.10.19](#page-776-3).

The GFD shall then compare, in parallel, the request HPA against all decoders to determine whether the request hits any decoder's HPA range. To accomplish this, for each decoder, a DPA offset is calculated by first subtracting HPABase from HPA and then removing the interleaving bits. The LSB of the interleaving bits to remove is determined by the interleave granularity and the number of bits to remove is determined by the interleave ways. If offset ≥ 0, offset < DPALen, and the Valid bit is set, then the request hits within that decoder. If only one decoder hits, then the DPA is calculated by adding DPABase to the offset. If zero or multiple decoders hit, then an access error is returned.

After the request HPA is translated to DPA, the RPID and the DPA are used to perform the Dynamic Capacity access check, as described in [Section 7.7.2.5](#page-401-0), and to access the GFD snoop filter. The design of the snoop filter is beyond the scope of this specification.

When the snoop filter needs to issue a back-invalidate to a host/peer, the DPA is translated to an HPA by performing the HPA-to-DPA steps in reverse. The RPID is used to access the GDT to select the decoders for the requester, which may be the host itself or one of its devices that performs Direct P2P. The GFD shall then compare, in parallel, the DPA against all selected decoders to determine whether the back-invalidate hits any decoder's DPA range.

This is accomplished by first calculating DPA offset = DPA – DPABase, and then testing whether offset ≥ 0, offset < DPALen, and the decoder is valid. If only one decoder hits, then the HPA is calculated by inserting the interleaving bits into the offset and then adding it to HPABase. When inserting the interleaving bits, the LSB is determined by interleave granularity, the number of bits is determined by the interleaving ways, and the value of the bits is determined by the way within the interleave set. If zero or multiple decoders hit, then an internal snoop filter error has occurred which will be handled as defined in a future specification update.

After the HPA is calculated, a BISnp with the GFD's SPID and HPA is issued to the Edge Port containing the FAST decoder of the host/peer that owns this HDM-DB Region, using the PID stored in the snoop filter as the DPID. The FAST decoder then optionally checks whether the HPA is located within the FAST decoder's Fabric Address space. The DPID and SPID are then removed, and the BISnp is then issued to the host/peer in HBR format.

> **IMPLEMENTATION NOTE**

It is recommended that a PBR switch size structures to support the typical to full scale of a PBR fabric.

It is recommended that the FAST have 4K to 16K entries.

<span id="page-401-1"></span>It is recommended that the IDT have 4K to 16K entries to support a sufficient number of interleave groups and interleave ways to cover all GFDs in a system.

#### <span id="page-401-0"></span>7.7.2.5 G-FAM Access Protection

G-FAM access protection is available at three levels of the hierarchy (see [Figure 7-32\)](#page-402-0):

- The first level of protection is through the host's (or peer device's) page tables. This fine-grained protection is used to restrict the Fabric Address space that is accessible by each process to a subset of that which is accessible by the host/peer.
- The second level of protection is described in the GAE in the form of the Global Memory Mapping Vector (GMV), described in [Section 7.7.2.6](#page-403-0).
- The third level of protection is at the target GFD itself and is fine grained. This section describes this third level of GFD protection.

<span id="page-402-0"></span>**Figure 7-32. Memory Access Protection Levels**

![](_page_402_Figure_3.jpeg)

The GFD's DPA space is divided into one or more Device Media Partitions (DMPs). Each DMP is defined by a base address within DPA space (DMPBase), a length (DMPLength), and a block size (DMPBlockSize). DMPBase and DMPLength must be a multiple of 256 MB, while DMPBlockSize must be a power-of-two size in bytes. The DMPBlockSize values that are supported by a device are device dependent and are defined in the GFD Supported Block Size Mask register. Each GFD decoder targets the DPA range of a DC Region within a single DMP (i.e., must not straddle DMP boundaries). The DC Region's block size is determined by the associated DMP's block size. The number of DMPs is device-implementation dependent. Unique DMPs are typically used for different media types (e.g., DRAM, NVM, etc.) and to provide sufficient DC block sizes to meet customer needs.

The GFD Dynamic Capacity protection mechanism is shown in [Figure 7-33.](#page-403-1) To support scaling to 4096 CXL requesters, the GFD DC protection mechanism uses a concept called Memory Groups. A Memory Group is a set of DMP blocks that can be accessed by the same set of requesters. The maximum number of Memory Groups (NG) that are supported by a GFD is implementation dependent. Each DMP block is assigned a Memory Group ID (GrpID), using a set of Memory Group Tables (MGTs). There is one MGT per DMP. Each MGT has one entry per DMP block within the DMP, with entry 0 in the MGT corresponding to Block 0 within the DMP. The depth of each MGT is implementation dependent. DPA is decoded to determine within which DMP a request falls, and then that DMP's MGT is used to determine the GrpID. The GrpID width is X = ceiling (log2 (NG) ) bits. For example, a device with 33 to 64 groups would require 6-bit GrpIDs.

In parallel with determining the GrpID for a request, the Request SPID is used to index the SPID Access Table (SAT) to produce a vector that identifies which Memory Groups the SPID is allowed to access (GrpAccVec). After the GrpID for a request is determined, the GrpID is used to select a GrpAccVec bit to determine whether access is allowed.

> **IMPLEMENTATION NOTE**

To support allocation of GFD capacity to hosts in sufficiently small percentages of the GFD, it is recommended that devices implement a minimum of 1K entries per MGT. Implementations may choose to use a separate RAM per MGT, or may use a single partitioned RAM for all MGTs.

To support a sufficient number of memory ranges with different host access lists, it is recommended that devices implement a minimum of 64 Memory Groups.

<span id="page-403-1"></span>**Figure 7-33. GFD Dynamic Capacity Access Protections**

![](_page_403_Figure_6.jpeg)

#### <span id="page-403-0"></span>7.7.2.6 Global Memory Access Endpoint

Access to G-FAM/GIM resources and configuration of the FAST through a PBR fabric edge switch is facilitated by a Global Memory Access Endpoint (GAE) which is a Mailbox CCI that includes support for the Global Memory Access Endpoint Command set and the opcodes required to configure and enable FAST use, including **Get PID Access Vectors** and **Configure FAST**. The GAE is presented to the host as a PCIe Endpoint with a Type 0 configuration space as defined in [Section 7.2.9.](#page-340-0)

There are two configurations under which a host edge port USP will expose a GAE. The first configuration, illustrated in [Figure 7-34,](#page-404-1) provides LD-FAM and G-FAM/GIM resources to a host. In this configuration, the GAE Mailbox CCI is used to configure G-FAM/GIM access for the USP and any DSPs connected to EPs. It may also include support for opcodes necessary to manage the CXL switch capability providing LD-FAM resources.

<span id="page-404-1"></span>**Figure 7-34. PBR Fabric Providing LD-FAM and G-FAM Resources**

![](_page_404_Figure_4.jpeg)

The second configuration, illustrated in [Figure 7-35,](#page-404-2) only provides access to G-FAM/ GIM resources. In this configuration, there is no CXL switch instantiated in the VCS and the GAE is the only PCIe function presented to the host.

<span id="page-404-2"></span>**Figure 7-35. PBR Fabric Providing Only G-FAM Resources**

![](_page_404_Figure_7.jpeg)

A GAE is also required in the vUSP of a Downstream ES VCS. This GAE is used for configuring that VCS, including configuring the FAST and LDST in the Edge DSPs and providing CDAT information, as described in [Section 7.7.12.4](#page-458-1).

Each GAE maintains two access vectors, which are used to control whether the host has access to a particular PID:

- **Global Memory Mapping Vector (GMV)**: 4k bitmask indicating which PIDs have been enabled for G-FAM or GIM access
<span id="page-404-3"></span>- • **VendPrefixL0 Target Vector (VTV)**: 4k bitmask indicating which PIDs have been enabled for VendPrefixL0

#### <span id="page-404-0"></span>7.7.2.7 Event Notifications from GFDs

GFDs do not maintain individual logs for every requester. Instead, events of interest are reported using the Enhanced Event Notifications defined in [Section 8.2.10.2.9](#page-662-1) and [Section 8.2.10.2.10.](#page-666-1) These notifications are transported across the fabric using GAM VDMs, as defined in [Section 3.1.11.6.](#page-103-3)

For event notifications sent to a host, the GAM VDM's DPID is the PID of the host's GAE. When received by the GAE, the GAM VDM's 32B payload is written into the host's GAM Buffer. All GAM VDMs that are received by the GAE are logged into the same GAM Buffer, regardless of their SPID.

The GAM Buffer is a circular buffer in host memory that is configured for 32B entries. Its location in host memory is configured with the Set GAM Buffer request. The GAE writes received GAM VDM payloads into the buffer offset that is specified by the head index reported by the Get GAM Buffer request (see [Section 8.2.10.2.11](#page-667-1)). As the host reads entries, the host increments the tail index using the Set GAM Buffer request (see [Section 8.2.10.2.12\)](#page-668-2). Head and tail indexes wrap to the beginning of the buffer when they increment beyond the buffer size.

The buffer is empty when the head index and tail index are equal. The buffer is full when the head index is immediately before the tail index. Old entries are not overwritten by the GAE until the host removes them from the buffer by incrementing the tail index. The GAE will report a buffer overflow condition if a GAM VDM is received when the buffer is full.

GAM VDMs are not forwarded to peer devices and are instead silently dropped by the peer's edge switch.

### <span id="page-405-0"></span>7.7.3 Global Integrated Memory (GIM)

A host domain may include multiple tiers of memory:

<span id="page-405-1"></span>- • Memory natively attached to a host (e.g., DDR, HBM, etc.)
- Device memory attached to a host CXL link
- Device memory attached to a host through CXL switches

All the memory tiers listed above are managed by a host operating system. CXL devices may be a Type 2 device or Type 3 device and may optionally support backinvalidate channels. A CXL Fabric may be composed of many host domains and G-FAM devices (GFD) as shown in [Figure 7-36](#page-406-1). GFD is a scalable memory resource that is accessible by all hosts and peer devices within a CXL Fabric.

Each host domain may allow other host domains within the CXL Fabric to access locally managed memory at any tier. Global Integrated Memory (GIM) refers to the memory in remote host domains that is mapped into local host physical address space. Hosts and devices are allowed to initiate cross-domain accesses to GIM, utilizing Unordered I/O (UIO) transactions. CXL.mem or CXL.cache must not be used for GIM accesses.

Cross-domain accesses are considered I/O coherent — data is coherent at the time of access. Remote domains may either mark this memory as uncacheable or manage caches with SW mechanisms.

GIM is primarily used for enabling remote DMA and messaging across domains. It is not intended for memory pooling or borrowing use cases.

<span id="page-406-1"></span>**Figure 7-36. CXL Fabric Example with Multiple Host Domains and Memory Types**

![](_page_406_Figure_3.jpeg)

#### <span id="page-406-0"></span>7.7.3.1 Host GIM Physical Address View

Hosts and devices may use proprietary decode mechanisms to identify the target DPID and may bypass address decoders in the switch ingress port. Hosts and devices are typically limited to access between homogeneous peers. See [Section 7.7.3.2](#page-407-0) for ways by which hosts/devices can access Global Integrated Memory (GIM) without using the FAST decoders. This section covers the decode path that uses the FAST decoders.

Hosts that access GIM and rely on address decoders in the switch must map this range in the Fabric Address Space. Hosts that access GIM and GFD must include both ranges in the Fabric Address Space and must use a contiguous address range within the Host Physical Address (HPA) space as shown in [Figure 7-37.](#page-406-2)

<span id="page-406-2"></span>**Figure 7-37. Example Host Physical Address View with GFD and GIM**

![](_page_406_Figure_8.jpeg)

All accesses to GIM regions must only use UIO. It is recommended to map GIM as MMIO instead of a normal write back memory type to avoid potential deadlock. However, implementations may use proprietary methods to guarantee UIO use even when internally using a cacheable memory type. Thus, MMIO mapping of GIM is only a recommendation and not a requirement.

Host and device accesses to GFD and GIM are decoded using a common FAST decoder to determine the target's DPID.

#### <span id="page-407-0"></span>7.7.3.2 Use Cases

ML and HPC applications are typically distributed across many compute nodes and need a scalable and efficient network for low-latency communication and synchronization. [Figure 7-38](#page-407-1) is an example of a system with a compute node composed of a Host, an Accelerator, and a cluster of nodes connected through a CXL switch fabric. Each host may expose a region or all available memory to other compute nodes.

<span id="page-407-1"></span>**Figure 7-38. Example Multi-host CXL Cluster with Memory on Host and Device Exposed as GIM**

![](_page_407_Figure_7.jpeg)

A second example in [Figure 7-39](#page-408-1) shows a CXL Fabric that connects all the accelerators. In this example, only the memory attached to the device is exposed to other devices as GIM. UIO allows flexible implementation options to enable RDMA semantics between devices. Software and security requirements are beyond the scope of this specification. GIM builds a framework for using the same set of capabilities for host-to-host communication, device-to-device communication, host-to-device communication, and device-to-host communication.

<span id="page-408-1"></span>**Figure 7-39. Example ML Cluster Supporting Cross-domain Access through GIM**

![](_page_408_Figure_3.jpeg)

#### <span id="page-408-0"></span>7.7.3.3 Transaction Flows and Rules for GIM

<span id="page-408-3"></span>The flow in [Figure 7-40](#page-408-2) describes how a host can access GIM in another host, using the fabric address model described earlier in this chapter. While [Figure 7-40](#page-408-2) uses host-tohost as the example, the same model works for host-to-device, device-to-device and device-to-host as well. A device that implements GIM as target is expected to have the required functionality that translates the combination of <Address: PID> in the incoming UIO TLP to a local memory address and to provide the required security on cross-domain accesses. This functionality can also use more information than just <Address:PID> from the TLP (e.g., PASID) for additional functionality/security. Designs can chose to reuse the GFD architecture for defining this translation/protection functionality or can implement a proprietary IOMMU-like logic. Details of this functionality are beyond the scope of this Specification.

<span id="page-408-2"></span>**Figure 7-40. GIM Access Flows Using FASTs**

![](_page_408_Figure_7.jpeg)

<span id="page-409-0"></span>**Figure 7-41. GIM Access Flows without FASTs**

![](_page_409_Figure_3.jpeg)

Although the flows described in [Figure 7-40](#page-408-2) and [Figure 7-41](#page-409-0) are self-explanatory, here are the key rules for PBR switches/Hosts/Devices that support the GIM flows:

• FM enables usage of VendPrefixL0 on non-PBR edge ports, using the FM API discussed in [Table 7-187](#page-497-0). By default, VendPrefixL0 usage is disabled on edge ports.

The mechanism that the FM uses to determine on which ports to enable this functionality is beyond the scope of this specification.

##### 7.7.3.3.1 GIM Rules for PBR Switch Ingress Port

- GIM flows are supported only via UIO transactions in this version of the specification. At this time, GIM flows are NOT supported via CXL.cachemem transactions or Non-UIO TLPs.
  - If switch ingress port receives a Non-UIO request with VendPrefixL0, it treats it as a UR.
- At the Non-PBR edge ingress port, for UIO request TLPs that do not have VendPrefixL0 and that are decoded via the FASTs, the switch sets the PTH.PIF bit when forwarding the request into the PBR fabric.
  - For UIO request TLPs that are not decoded via the FASTs, this bit is cleared when forwarded to the PBR fabric.
- At the Non-PBR edge ingress port, if the port is enabled for Ingress Request VendPrefixL0 usage and UIO request TLP has VendPrefixL0 and VendPrefixL0.PID matches one of the allowed PIDs in VTV (see [Section 7.7.2.6\)](#page-403-0), the switch bypasses all decode, sets PTH.DPID=VendPrefixL0.PID, PTH.SPID=Ingress Port PID, and PTH.PIF=1 when forwarding the request to the PBR fabric.
  - If a UIO request TLP is received with VendPrefixL0 but the port is not enabled for Ingress Request VendPrefixL0 usage or if the PID in the prefix does not match any of the allowed PIDs in VTV, the switch treats the request as a UR.
- At the Non-PBR edge ingress port, for UIO completion TLPs, the switch forwards the received VendPrefixL0.PID on PTH.DPID when forwarding the packet to the PBR fabric, if Ingress Completion VendPrefixL0 usage is enabled on the port (see

[Section 7.7.15.5\)](#page-496-1) and VendPrefixL0.PID matches one of the allowed PIDs in VTV (see [Section 7.7.2.6\)](#page-403-0). PTH.SPID on the completion TLP is set to the PID of the ingress port.

- if a UIO completion TLP is received on a Non-PBR edge ingress port when Ingress Completion VendPrefixL0 usage is disabled on the port or if the PID in the prefix does not match any of the allowed PIDs in VTV, the switch must drop the packet and treat it as an Unexpected Completion.
- Switch sets the PIF bit whenever it successfully forwards the received completion TLP to the PBR fabric.

##### 7.7.3.3.2 GIM Rules for PBR Switch Egress Port

- At the Non-PBR edge egress port, for UIO request TLPs with the PTH.PIF bit set, the switch forwards the PTH.SPID field of the request TLP on the VendPrefixL0.PID field if the egress port is enabled for Egress Request VendPrefixL0 usage.
  - If the PTH.PIF bit is set but the egress port is not enabled for Egress Request VendPrefixL0 usage, the switch should treat the request as a UR.
  - If the PTH.PIF bit is cleared in the UIO request TLP, the request TLP is forwarded to the egress link without VendPrefixL0, regardless of whether the port is enabled for Egress Request VendPrefixL0 usage.
- At the Non-PBR edge egress port, the switch does not send VendPrefixL0 on completion TLPs.
- If the Non-PBR edge egress port is in a 'Link Down' state, GIM packets shall be silently dropped.
- Switch forwards the PTH.PIF bit as-is on edge PBR links

##### 7.7.3.3.3 GIM Rules for Host/Devices

- Host/Devices that support VendPrefixL0 semantics and receive a UIO Request TLP with VendPrefixL0 must return the received PID value in the associated completion's VendPrefixL0.
- Host/Devices must always return a value of 0 for Completer ID in the UIO completions.

##### 7.7.3.3.4 Other GIM Rules

- VendPrefixL0 must never be sent on edge PBR links, such as the links connecting to a GFD
- GFD must ignore the PTH.PIF bit on TLPs that the GFD receives
- GFD is permitted to set the PTH.PIF bit on CXL.io request TLPs that the GFD sources and always sets this bit on CXL.io completion TLPs that the GFD sources

**Figure 7-42.**

*Note:* If setting the PTH.PIF bit on request TLPs, the GFD must do so only if it is sure that the ultimate destination (e.g., GIM) needs to be aware of the PID of the source agent that is generating the request (such as for functional/security reasons); otherwise, the GFD should not set the bit.

#### <span id="page-410-0"></span>7.7.3.4 Restrictions with Host-to-Host UIO Usages

Host-to-Host UIO usages can result in deadlock when mixed with UIO traffic going to the host that can route back in the host. To avoid such deadlocks:

• Systems that support Host-to-Host UIO must use a separate VC for Host-to-Host UIO traffic vs. remainder of UIO, on host edge links.

(OR)

• Minimally avoid usages that can cause loopback traffic, either in the host or in switches. Generically, this restriction could mean that UIO accesses do not target MMIO space.

A detailed analysis of restrictions that are needed to make a specific system configuration to work with Host-to-Host UIO enabled is beyond the scope of this specification.

A future ECN may be considered that allows for more deadlock avoidance options beyond the two listed above.

### <span id="page-411-0"></span>7.7.4 Non-GIM Usages with VendPrefixL0

<span id="page-411-2"></span>When Hosts/Devices initiate UIO requests with VendPrefixL0, address decoding is bypassed in the Switch ingress port. This allows for proprietary implementations in which the address/data information in the TLP can potentially be vendor-defined. Such usages are beyond the scope of this specification; however, GIM-related rules enumerated in [Section 7.7.3.3](#page-408-0) allow such implementations as well.

### <span id="page-411-1"></span>7.7.5 HBR and PBR Switch Configurations

<span id="page-411-3"></span>CXL supports two types of switches: HBR (Hierarchy Based Routing) and PBR (Port Based Routing). "HBR" is the shorthand name for the CXL switches introduced in the CXL 2.0 specification and enhanced in subsequent CXL ECNs and specifications. In this section, the interaction between the two will be discussed.

A variety of HBR/PBR switch combinations are supported. The basic rules are as follows:

- Host RP must be connected to an HBR USP, PBR USP, or a non-GFD
- Non-GFD must be connected to an HBR DSP, a PBR DSP, or a Host RP
- PBR USP may be connected only to a host RP; connecting it to an HBR DSP is not supported
- HBR USP may be connected to a host RP, a PBR DSP, or an HBR DSP
- GFD may be connected only to a PBR DSP
- PBR FPort may be connected only to a PBR FPort of a different PBR switch

[Figure 7-42](#page-412-1) illustrates some example supported switch configurations, but should not be considered a complete list.

<span id="page-412-1"></span>Figure 7-42. Example Supported Switch Configurations

![](_page_412_Figure_3.jpeg)

<span id="page-412-0"></span>CXL fabric topology is non-prescriptive when using PBR switches. There is no predefined list of supported topologies. PID-based routing combined with flexible routing tables enables a high degree of freedom in choosing a topology. The PBR portion of the fabric may freely use any topology for which deadlock-free routing can be found.

To name a few examples, a PBR fabric might implement a simple PCIe-like tree topology, more-complex tree topologies such as fat tree (aka folded Clos), or non-tree topologies such as mesh, ring, star, linear, butterfly, or HyperX, as well as hybrids and multi-dimensional variants of these topologies.

Figure 7-43 illustrates an example of fully connected mesh topology (aka 1-dimensional HyperX). It has the notable ability to connect a relatively large number of components while still limiting the number of switch traversals. A direct link exists between each pair of switches, so it is possible for the FM to set up routing tables such that all components connected to the same switch can reach one another with a single switch traversal, and all components connected to different switches can reach one another with two switch traversals.

<span id="page-413-1"></span>**Figure 7-43. Example PBR Mesh Topology**

![](_page_413_Figure_3.jpeg)

#### <span id="page-413-0"></span>7.7.5.1 PBR Forwarding Dependencies, Loops, and Deadlocks

When messages are forwarded through PBR switches from one Fabric Port to another, a dependency is created — acceptance of arriving messages into one PBR Fabric Port is conditional upon the ability to transmit messages out of another PBR Fabric Port. Other arriving traffic commingled on the same inbound link is also affected by the dependency. Thus, traffic waiting to be forwarded can block traffic that needs to exit the PBR portion of the fabric via a USP or DSP of the PBR switch.

Some topologies, such as PCIe tree or fat tree, are inherently free of loops. Thus, the resulting Fabric Port-forwarding dependencies are inherently non-circular. However, in topologies that contain loops, dependencies can form a closed loop, thereby resulting in a deadlock.

The routing table programming in the PBR switches, performed by the FM, must take potential deadlock into account. The dependencies must not be allowed to form a closed loop.

This can be illustrated using the mesh topology presented in [Figure 7-44](#page-414-0).

**Figure 7-45.**

<span id="page-414-0"></span>**Figure 7-44. Example Routing Scheme for a Mesh Topology**

![](_page_414_Figure_4.jpeg)

One simplistic approach for the mesh topology would be to support only minimal routes. Messages traverse at most one inter-switch PBR link en route from any source host or device to any destination host or device. This simplistic solution is deadlock-free because no message forwarding occurs between PBR Fabric Ports of any switch, and thus there are no forwarding dependencies created from which loops may form. The single route choice, however, limits bandwidth.

[Figure 7-44](#page-414-0) illustrates a more-sophisticated routing scheme applied to the same mesh topology as [Figure 7-43.](#page-413-1) Each PBR switch is programmed to support three forwarding paths out of the 6 possible pairings. The arrows show permitted forwarding between Fabric Ports. For example, a message traveling from the lower-left switch to the upperright switch has two route choices:

- Via the direct link
- Indirectly via the upper-left switch

Note that the message cannot travel via the lower-right switch because that switch has no forwarding arrow shown between those Fabric Ports.

The forwarding arrows do not form closed loops; thus, there are no circular dependencies that could lead to deadlock.

This approach to mesh routing (i.e., restricting the choice of intermediate nodes to avoid circular dependencies) can also be applied to larger 1D-HyperX topologies. For a fully connected mesh that contains N switches, there are N-2 potential intermediate

switches to consider for possible indirect routes between any pair of switches. However, this deadlock-avoidance restriction limits the usable intermediate switch choices to one-half of that number ((N-2)/2), rounding down if N is odd.

Multi-dimensional HyperX topologies can be routed deadlock-free by using this technique within each dimension, and implementing dimension-ordered routing.

<span id="page-415-2"></span>Although this section covers some cases for circular dependency avoidance, fully architected deadlock dependency avoidance with topologies that contain fabric loops is beyond the scope of this specification.

### <span id="page-415-0"></span>7.7.6 PBR Switching Details

#### <span id="page-415-1"></span>7.7.6.1 Virtual Hierarchies Spanning a Fabric

Hosts connected to CXL Fabrics (composed of PBR switches) do not require special, fabric-specific discovery mechanisms. The fabric complexities are abstracted, and the host is presented with a simple switching topology that is compliant with PCIe Base Specification. All intermediate Fabric switches are obscured from host view. At most, two layers of Edge Switches (ESs) are presented:

- Host ES: The host discovers a single switch representative of the edge to which it is connected. Any EPs also physically connected to this PBR switch and bound to the host's VH are seen as being directly connected to PPBs within the VCS.
- Downstream ES: As desired, the FM may establish binding connections between the Host ES VCS and one or more remote PBR switches within the Fabric. When such a binding connection is established, the remote switch presents a VCS that is connected to one of the Host ES vPPBs. The Host discovers a single link between a virtualized DSP (vDSP) in the Host ES and a virtualized USP (vUSP) in the Downstream ES, regardless of the number of intermediate fabric switches, if any. The link state is virtualized by the Host ES and is representative of the routing path between the two ESs; if any intermediate ISLs go down, the Host ES will report a surprise Link Down error on the corresponding vPPB.
- If an HBR switch is connected to a PBR DSP, that HBR switch and any HBR switches below it will be visible to the host. HBR switches are not Fabric switches.

A PBR switch's operation as a "Host ES" or a "Downstream ES" per the above descriptions is relative to each host's VH. A PBR switch may simultaneously support Host ES Ports and Downstream ES Ports for different VHs. ISLs within the Fabric are capable of carrying bidirectional traffic for more than one VH at the same time. Edge DSPs support PCIe devices, SLDs, MLDs, GFDs, PCIe switches, and CXL HBR switches.

A Mailbox CCI is required in the vUSP of a Downstream ES VCS for management purposes.

<span id="page-416-1"></span>Figure 7-45. Physical Topology and Logical View

![](_page_416_Figure_3.jpeg)

#### <span id="page-416-0"></span>7.7.6.2 PBR Message Routing across the Fabric

<span id="page-416-2"></span>PBR switches can support both static and dynamic routing for each DPID, as determined by message class.

With static routing, messages of a given message class use a single fixed path between source and destination Edge Ports. Messages that use a vDSP/vUSP binding (see Section 7.7.6.4) always use static routing as well, though the vUSP as a source or destination is always associated with an FPort instead of an Edge Port.

With dynamic routing, messages of a given message class can use different paths between source and destination Edge Ports, dynamically determined by factors such as congestion avoidance, algorithms to distribute traffic across multiple links, or changes with link connectivity. Each DPID supports static routing for those message classes that require it, and it can support either static or dynamic routing for the other message classes.

Dynamic routing is generally preferred when suitable, but in certain cases static routing must be used to ensure in-order delivery of messages as required by ordering rules. Due to its ability to distribute traffic across multiple links, dynamic routing is especially preferred for messages that carry payload data, as indicated in Table 7-84.

Somewhat orthogonal to dynamic vs. static routing, PBR switches support hierarchical and edge-to-edge decoding and routing. With hierarchical routing, a message is decoded and routed within each ES using HBR mechanisms and statically routed between ESs, using vDSP/vUSP bindings. With edge-to-edge routing, a message is routed from a source Edge Port to a destination Edge Port, using a DPID determined at the source Edge Port or GFD. Edge-to-edge routing uses either dynamic or static routing, as determined by the message class.

Table 7-84 summarizes the type of PBR decoding and routing used, by message class.

<span id="page-417-0"></span>**Table 7-84. PBR Fabric Decoding and Routing, by Message Class**

|                 |  | Message Class<br>** Payload Data            | Ordering<br>Rules                                        | Preferred<br>Routing1                              | Decoding and<br>Routing Mechanism                                                        |  |
|-----------------|--|---------------------------------------------|----------------------------------------------------------|----------------------------------------------------|------------------------------------------------------------------------------------------|--|
| CXL.cache       |  | D2H Req                                     |                                                          | Dynamic                                            |                                                                                          |  |
|                 |  | H2D Rsp                                     | I11a: Snoop (H2D Req)<br>push GO (H2D Rsp)               | Static                                             | Edge-to-edge routing using the Cache ID lookups or<br>vPPB bindings                      |  |
|                 |  | H2D DH **                                   |                                                          | Dynamic                                            |                                                                                          |  |
|                 |  | H2D Req                                     | I11a: Snoop (H2D Req)<br>push GO (H2D Rsp)               | Static                                             |                                                                                          |  |
|                 |  | D2H Rsp                                     |                                                          | Dynamic                                            |                                                                                          |  |
|                 |  | D2H DH **                                   |                                                          | Dynamic                                            |                                                                                          |  |
| m<br>me<br>CXL. |  | M2S Req                                     | G8a (HDM-D to Type 2):<br>MemRd*/MemInv* push<br>Mem*Fwd | HDM-H: Dynamic<br>HDM-D: Static<br>HDM-DB: Dynamic | LD-FAM: Edge-to-edge routing if using LDST2<br>Hierarchical routing if using HDM Decoder |  |
|                 |  |                                             |                                                          |                                                    | G-FAM: edge-to-edge routing using FAST                                                   |  |
|                 |  | M2S RwD **                                  | -                                                        | Dynamic                                            | LD-FAM: Edge-to-edge routing if using LDST2<br>Hierarchical routing if using HDM Decoder |  |
|                 |  |                                             |                                                          |                                                    | G-FAM: Edge-to-edge routing using FAST                                                   |  |
|                 |  | S2M NDR                                     | E6a: BI-ConflictAck<br>pushes Cmp*                       | Static                                             |                                                                                          |  |
|                 |  | S2M DRS **                                  | -                                                        | Dynamic                                            | Edge-to-edge routing using vPPB bindings or BI-ID                                        |  |
|                 |  | S2M BISnp                                   | -                                                        | Dynamic                                            | lookups                                                                                  |  |
|                 |  | M2S BIRsp                                   | -                                                        | Dynamic                                            |                                                                                          |  |
| CXL.io          |  | All CXL.io<br>TLPs **<br>except<br>next row | PCIe (many)                                              | Static                                             | Hierarchical decoding within each ES<br>vDSP/vUSP between Host ES and each Downstream ES |  |
|                 |  | UIO Direct<br>P2P to HDM<br>TLPs **         | -                                                        | Dynamic                                            | Edge-to-edge routing using FAST or LDST decoder                                          |  |

- 1. When dynamic routing is preferred, static routing is still permitted.
<span id="page-417-1"></span>- 2. LDST decoders do not support HDM-D.

The Ordering Rules column primarily covers a few special cases with CXL.cachemem messages in which the fabric is required to enforce ordering within a single message class or between two message classes. The alphanumeric identifier refers to ordering summary table entries in [Table 3-57](#page-165-2) and [Table 3-58.](#page-165-3)

With LD-FAM, host software may use either HDM Decoders or LDST decoders, though LDST decoders do not support HDM-D. Host software implemented solely against the CXL 2.0 Specification comprehends only HDM Decoders, and such host software may continue to use them with PBR Fabrics. Newer host software that comprehends and uses LDST decoders can benefit from edge-to-edge routing, which uses dynamic routing for suitable message classes.

For CXL.io TLPs, the PTH.Hie (hierarchical) bit determines when intermediate PBR switches must use static routing. When the PTH.Hie bit is 1, intermediate PBR switches shall use static routing for the TLP; otherwise, such switches are permitted to use dynamic routing for the TLP. When a PTH is pre-pended to a TLP, the Hie bit shall be 1 if the TLP is a vDSP/vUSP message; otherwise, the Hie bit shall be 0.

#### <span id="page-418-0"></span>7.7.6.3 PBR Message Routing within a Single PBR Switch

A message received or converted to PBR format at a PBR switch ingress port is routed to one of the switch's egress ports, as determined by the ingress port's DPID Routing Table (DRT) and its associated Routing Group Table (RGT). Their structures are described in detail in [Section 7.7.13.10](#page-470-0) and [Section 7.7.13.12](#page-472-0), respectively, and this section provides a high-level summary.

A DRT has 4096 entries and is indexed by a DPID. Each DRT entry contains a 2-bit entry type field that indicates whether the entry is valid, and whether the entry contains a single physical port number or an RGT index.

DRT entries that contain an RGT index are required when multiple egress ports need to be specified for use with dynamic routing. An RGT is a power-of-2-sized table with up to 256 entries. Each RGT entry contains an ordered list of up to eight physical port numbers, along with two 3-bit fields that indicate how many in the list are valid and how many of those are primary vs. secondary. This allows one or more primary and zero or more secondary egress ports to be listed. Cases that require static routing must always use the first list entry. The RGT entry also contains a 3-bit dynamic routing mode and 3-bit mix setting. The distinction between primary vs. secondary varies by dynamic routing mode and mix setting.

In routing modes that utilize the mix setting, its value determines the mix of the primary and secondary egress port group usage, assuming that one or more secondary egress ports are specified. Using the mix setting supports egress port selection based on known bandwidth differences that exist elsewhere in the fabric or based on preferred vs. overflow routing paths. Secondary egress ports should be specified only when there are significant differences with primary egress ports; otherwise, all suitable egress ports should be specified as primary. When no secondary egress ports have been specified, the mix setting shall be ignored.

| Mix Setting | % Primary | % Secondary |
|-------------|-----------|-------------|
**Figure 7-46.**

| 0           | 87.5      | 12.5        |
| 1           | 75        | 25          |
| 2           | 62.5      | 37.5        |
| 3           | 50        | 50          |
| 4           | 37.5      | 62.5        |
| 5           | 25        | 75          |
| 6           | 12.5      | 87.5        |
| 7           | Preferred | Overflow    |

<span id="page-418-1"></span>Mix setting [7](#page-418-1) is intended for use in cases where primary and secondary egress port groups represent preferred and overflow ports, respectively. Mix setting [7](#page-418-1) mandates the choice of a primary (preferred) path route whenever flow-control conditions and link state permit.

The term candidate egress port refers to a port that is present in the appropriate RGT entry, where the message can be queued or internally routed immediately. The egress port need not have link credits to send the packet immediately. An implementation may optionally base part of the candidate selection on the egress port state (e.g., link-up or containment states).

The mix dynamic routing mode descriptions that follow describe routing outcomes in terms of probability, consistent with a weighted (pseudo) random implementation. Random selection has the advantage that each routing decision is stateless and independent of one another, and it has high immunity to hot-route problems that might

otherwise arise from repetitive patterns in packet arrivals. The specific random routing implementation is not prescribed. Implementations that achieve the specified mix by deterministic means, such as by weighted round-robin, are permitted.

The architected dynamic routing modes include the optional modes listed in [Table 7-85.](#page-419-1)

<span id="page-419-1"></span>**Table 7-85. Optional Architected Dynamic Routing Modes**

| Mode                             | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |  |  |
|----------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--|--|
| Mix with Random                  | The candidate list is first narrowed to select either the primary or the secondary<br>group based on the configured mix. A random selection is then made within that<br>group. A message class shall stall when the selected subset is empty due to flow<br>control conditions.<br>The FM may choose to select this mode (if supported) as an alternative to Mix with<br>Congestion Avoidance if the latter is not supported.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |  |  |
| Mix with Congestion<br>Avoidance | The candidate list is first narrowed to select either the primary or the secondary<br>group based on the configured mix. A local congestion-avoiding selection is then<br>made within that group. A message class shall stall when the selected subset is<br>empty due to flow-control conditions. Congestion-avoiding candidate selection is<br>based on vendor-specific congestion metrics, favoring the selection of less<br>congested egress ports. For example, the congestion metric might be a measure of<br>egress port backlog, considering all queued traffic for that egress port across the<br>entire switch.<br>The FM may choose to select this mode (if supported) when Advanced Congestion<br>Avoidance mode is inappropriate or not supported, of if fixed-traffic ratio<br>apportionment or preferred/overflow behavior is needed.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |  |  |
| Advanced Congestion<br>Avoidance | A congestion-avoiding selection is made considering both primary and secondary<br>candidate egress ports, ignoring the mix setting value. Egress ports with the minimal<br>remaining hop count should be specified as primary; any suitable egress ports that<br>have higher remaining hop counts should be specified as secondary. Candidate<br>selection is based on vendor-specific metrics, favoring less-congested egress ports<br>in general, and especially avoiding secondary candidates that are already heavily<br>scheduled with primary traffic, regardless of the target DPID.<br>An example congestion metric might be backlog-based, but with different weightings<br>for primary vs. secondary backlogs. Congestion metric values for primary backlogs<br>should be higher than secondary backlogs when assessing the congestion level of a<br>secondary candidate egress port. This discourages the use of secondary candidate<br>ports that have a high primary backlog. In congestion metrics, messages that are<br>queued or internally routed via the physical port number in a DRT or via dynamic<br>routing modes other than Advanced Congestion Avoidance should be considered<br>primary backlog.<br>The FM may choose to select this mode (if supported) for routing egress ports that<br>carry commingled minimal and non-minimal traffic. |  |  |

PBR switches that implement RGTs shall support at least one of the three architected dynamic routing modes (those listed in [Table 7-85\)](#page-419-1) within each RGT.

DRT entries that contain a single physical port instead of an RGT index are useful when there is only one reasonable egress port choice (e.g., routing to an Edge Port). This avoids an RGT look-up and additional processing to determine which egress port to use. This may also help reduce the number of entries that need to be implemented in the associated RGT.

#### <span id="page-419-0"></span>7.7.6.4 PBR Switch vDSP/vUSP Bindings and Connectivity

Within the context of a single VH, the virtual connection between a VCS in the Host ES and a VCS in a Downstream ES is accomplished with a vDSP/vUSP binding. A vDSP is a vPPB in the Host ES VCS that the host sees as a DSP. A vUSP is a vPPB in the Downstream ES VCS that the host sees as a USP. Host software always sees a single virtual link connecting the vDSP and vUSP, even though one or more intermediate Fabric switches may be physically present.

Figure 7-46 shows an example PBR Fabric that consists of one Host ES, one Downstream ES, and an unspecified number of intermediate Fabric switches connecting the two.

<span id="page-420-0"></span>Figure 7-46. Example PBR Fabric

![](_page_420_Figure_4.jpeg)

The rules for vDSP/vUSP bindings are as follows:

- Each active Host ES vDSP is bound to one Host ES FPort and one Downstream ES vLISP
- Each active Downstream ES vUSP is bound to one Downstream ES FPort and one Host ES vDSP
- All messages routed using a vDSP/vUSP binding must contain both a DPID and an SPID
- vDSPs and vUSPs are never assigned PIDs
- Each PID used for vDSP/vUSP bindings may support both static and dynamic routing; however, vDSP/vUSP traffic always uses static routing
- Each vDSP/vUSP binding has a single host USP PID that determines which Host ES FPort will be used to route from vUSP to vDSP
- Each vDSP/vUSP binding has a single Downstream ES PID that determines which Downstream ES FPort will be used to route from vDSP to vUSP

When a Host ES FPort transmits a vDSP/vUSP message downstream in a PBR flit, the message contains the DPID and SPID taken from the vDSP's binding. Assuming no errors, the message traverses any intermediate Fabric switches that are present and is received by an FPort that is bound to the Downstream ES vUSP. A vUSP there claims the message by matching both the DPID and SPID from its binding.

Similarly, when a Downstream ES FPort transmits a vDSP/vUSP message upstream in a PBR flit, the message contains the DPID and SPID taken from the vUSP's binding. Assuming no errors, the message traverses any intermediate Fabric switches that are present and is received by an FPort that is bound to the Host ES vDSP. A vDSP there claims the message by matching both the DPID and SPID from its binding.

#### <span id="page-421-0"></span>7.7.6.5 PID Use Models and Assignments

The example PBR Fabric illustrated in [Figure 7-46](#page-420-0) illustrates key aspects of how PIDs can be assigned and used. PIDs are either assigned by the FM or by static fabric initialization (see [Section 7.7.12.1.1\)](#page-456-3).

A Host ES USP often has one PID but may have multiple PIDs assigned to support multiple vDSP/vUSP bindings in the same Downstream ES. Each vDSP/vUSP binding may use a different Host ES FPort and/or Downstream ES FPort, providing traffic isolation for differentiated quality of service. If multiple vDSP bindings use the same PID for the Downstream ES, different PIDs for the USP can distinguish their bindings.

The Downstream ES FPorts may have one or more PIDs assigned, where each PID can be associated with a different set of FPorts. In an example scenario, there might be one PID for the left set of FPorts for multipathing and another PID for the right set. For a PID assigned to an FPort set for multipathing, DRTs in different USPs can specify different egress ports for static routing, distributing the static routing traffic for certain topologies without requiring additional DS\_ES PIDs.

A DSP may be assigned multiple PIDs, one PID, or no PIDs. A DSP above a non-GFD usually has one PID, but may be assigned multiple PIDs for isolating traffic from multiple senders or for associating a unique PID for each caching or HDM-DB-capable device attached to one or more HBR switches below an Edge Port. DSPs above a multiported GFD may not require dedicated assigned PIDs, relying instead on one or more PIDs assigned to the GFD itself.

A GFD may have one or more PIDs assigned. A multi-ported GFD may have multiple PIDs assigned for differentiated quality of service, though a single PID may be sufficient for congestion avoidance.

As mentioned in the previous section, each vDSP/vUSP binding has two PIDs assigned. For downstream vDSP/vUSP messages that use a given binding, the SPID is a PID associated with the host Edge USP, and the DPID is a PID associated with the Downstream ES FPort. Such messages are always transmitted by the same Host ES FPort and received by the same Downstream ES FPort. Then, the FPort uses various vUSP info decoding mechanisms to route the message to the appropriate Downstream ES vPPB using PBR mechanisms or HBR mechanisms, depending upon the message class. See CXL Switch Message Conversion (see [Section 7.7.6.6\)](#page-422-0). If there are any intermediate Fabric switches, such messages always take a single static path.

Upstream vDSP/vUSP messages are handled in a similar manner, but only involve CXL.io message classes. On a given binding, the SPID is the PID associated with the Downstream ES FPort, and the DPID is the PID associated with the host Edge USP. Such messages are always transmitted by the same Downstream ES FPort and received by the same Host ES FPort. Then, the receiving FPort uses the associated vDSP context to identify the appropriate target using HBR mechanisms. If the target is an egress port, the message is routed there for transmission. If the target is another vDSP, that vDSP

converts the PIDs to its bound PIDs and transmits it from its associated FPort, which may be the same FPort on which it arrived or on a different FPort. If there are any intermediate Fabric switches, such messages always take a single static path.

A PBR switch requires an assigned PID to send and receive management requests, responses, and notifications. Transactions that target this PID are processed by central logic or by FW within the switch.

FMs connected to a PBR switch via an MCTP-based CCI also consume a PID. This PID is communicated to the PBR switch when the FM claims ownership of the device. The PID is used to direct transactions to the FM, such as Event Notifications generated by components owned by the FM.

PID FFFh is reserved and is used to indicate that a transaction should be processed locally. It allows FMs to target devices before they have had a valid PID assigned and when they have an assigned PID of which the FM is unaware.

#### <span id="page-422-0"></span>7.7.6.6 CXL Switch Message Format Conversion

A PBR switch converts messages received from HBR hosts, devices, and switches to the PBR message format for routing across a PBR Fabric. In addition, messages received from the PBR fabric that target the HBR hosts, devices, and switches are converted to messages using the non-PID spaces (i.e., CacheID, BI-ID, and LD-ID). The following subsections provide the conversion flow for each message class.

The FM assigns PIDs to various PBR switch ports, as described in [Section 7.7.6.5](#page-421-0). The DPID value for request messages is determined by a variety of ways, including HDM Decoders, vPPB bindings, and lookup tables or CAMs using non-PID spaces. The DPID value for a response message is often the SPID value from the associated request message but is sometimes determined by one of the ways mentioned for request messages.

With HBR format messages, MLDs support a 4-bit LD-ID field in CXL.mem protocol for selection and routing of MLD messages, and CXL.cache includes a 4-bit CacheID field that is used to allow up to 16 Type 1 Devices or Type 2 Devices below an RP. PBR format messages use 12-bit PIDs to support large Fabrics. This section describes the support required in PBR switches for routing messages from non-fabric-aware hosts and devices that support the 4-bit LD-ID and 4-bit CacheID fields. It also covers BI-IDbased routing.

Considering the wide range of supported PBR/HBR switch topologies, the variety of specific routing techniques for the many different cases of port connectivity is quite complex. Below is a general description for the HBR and PBR switch routing mechanisms that are used by key message classes, followed by port processing tables with more-specific details for both classes of switches.

##### 7.7.6.6.1 CXL.io, Including UIO

An HBR switch routes most CXL.io TLPs between its ports using standard mechanisms defined by PCIe Base Specification. A DSP above an MLD uses LD-ID Prefixes to identify which LD a downstream TLP is targeting or from which LD an upstream TLP came.

UIO Requests that directly target HDM ranges can use enhanced UIO-capable HDM Decoders for their routing. This includes UIO Requests from the host that target devices with HDM, as well as "Direct P2P" cases where UIO Requests from one device target other devices with HDM. UIO Direct P2P to HDM traffic goes upstream, P2P, and downstream along different portions of its path.

![](_page_423_Picture_1.jpeg)

A PBR switch converts PCIe-format TLPs or CXL.io HBR-format TLPs to PBR-format TLPs by pre-pending to each TLP a 4B CXL PBR TLP Header (PTH), which includes an SPID and DPID. Conversion from PBR format to HBR format or PCIe format consists of stripping the CXL PTH from the TLP.

##### 7.7.6.6.2 CXL.cache

A number of CXL.cache messages in 256B HBR format have a 4-bit CacheID field that enables up to 16 caching devices below a single RP. CXL.cache messages in 68B HBR format do not support this feature, and thus never carry a CacheID field. CXL.cache messages in PBR format do support this feature, but convey the necessary information via PIDs instead of a CacheID field. [Table 7-86](#page-423-0) summarizes which message classes contain the CacheID field.

<span id="page-423-0"></span>**Table 7-86. Summary of CacheID Field**

| Msg Class | CacheID Field |          |          |  |
|-----------|---------------|----------|----------|--|
|           | 68B HBR       | 256B HBR | 256B PBR |  |
| D2H Req   | No            | Yes      | No       |  |
| H2D Rsp   | No            | Yes      | No       |  |
| H2D DH    | No            | Yes      | No       |  |
| H2D Req   | No            | Yes      | No       |  |
| D2H Rsp   | No            | No       | No       |  |
| D2H DH    | No            | No       | No       |  |

For HBR format messages that contain a CacheID field, in some cases an HBR or PBR DSP needs to know whether to propagate or assign the CacheID. This information is configured by host software and is contained in the CXL Cache ID Decoder Capability Structure (see [Section 8.2.4.29](#page-595-1)).

[Table 7-87](#page-423-1) summarizes the HBR switch routing for CXL.cache message classes. [Table 7-88](#page-424-0) summarizes the PBR switch routing for CXL.cache message classes.

<span id="page-423-1"></span>**Table 7-87. Summary of HBR Switch Routing for CXL.cache Message Classes**

| Message Class               | Switch Routing                                                                                                                                                                                                                                                   |
|-----------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| D2H Request                 | For HBR switch routing of D2H requests upstream to the bound host, the D2H<br>request to the USP relies on the DSP's vPPB binding at each switch level.<br>CacheID is added to the message by the DSP above the device to enable<br>routing of the H2D response. |
| H2D Response or Data Header | For HBR switch routing of H2D responses or data headers downstream to the<br>DSP, the USP at each switch level looks up the PCIe-defined PortID from the<br>Cache ID Route Table.                                                                                |
| H2D Request                 | For HBR switch routing of H2D requests downstream to the DSP, the USP at<br>each switch level looks up the PCIe-defined PortID from the Cache ID Route<br>Table.                                                                                                 |
| D2H Response or Data Header | For HBR switch routing of D2H responses or data headers upstream to the<br>bound host, the D2H response or data header to the USP relies upon the<br>DSP's vPPB binding at each switch level.                                                                    |

Within a PBR fabric, all CXL.cache messages are routed edge-to-edge, and they never use vDSP/vUSP bindings.

In contrast to most 256B HBR-format CXL.cache messages, PBR-format cache messages never contain a CacheID field, thus the equivalent information when needed must be conveyed via PIDs.

When multiple caching devices are attached to an HBR switch below a PBR fabric, the FM must allocate and assign a unique PID for each such caching device. This enables PBR switches to convert between a caching device's unique PID and CacheID when needed.

<span id="page-424-0"></span>**Table 7-88. Summary of PBR Switch Routing for CXL.cache Message Classes**

| Message Class               | Switch Routing                                                                                                                                                                                                                                                                                                                                                                                                               |  |
|-----------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--|
| D2H Request                 | For PBR switch routing of these messages upstream to the host, Edge DSPs<br>get the Host USP DPID from their vPPB. Those above an SLD get their SPID<br>from their vPPB. Those above an HBR USP look up the SPID from the Cache<br>ID Route Table using the CacheID contained in the HBR-format message.<br>For converting to HBR format at the Edge USP, the USP derives the CacheID<br>from a 16-entry CAM using the SPID. |  |
| H2D Response or Data Header | For PBR switch routing of these messages downstream to the Edge DSP, the<br>Edge USP looks up the DPID from the Cache ID Route Table using the<br>CacheID in the HBR-format message.<br>For converting to HBR format at the Edge DSP, above an SLD the CacheID is<br>unused, and above an HBR USP the Cache ID is derived from a 16-entry CAM<br>match using the DPID.                                                       |  |
| H2D Request                 | For PBR switch routing of these messages downstream to the Edge DSP, the<br>Edge USP looks up the DPID from the CacheID Route Table using the<br>CacheID. The USP gets the SPID from its vPPB.<br>For converting to HBR format at the Edge DSP, above an SLD the CacheID is<br>unused, and above an HBR USP the CacheID is derived from a 16-entry CAM<br>match using the DPID.                                              |  |
| D2H Response or Data Header | For PBR switch routing of these messages upstream to the host, Edge DSPs<br>get the DPID from their vPPB.<br>For converting to HBR format at the Edge USP, the CacheID field is not<br>present in the message.                                                                                                                                                                                                               |  |

At an Edge DSP, when converting a downstream CXL.cache message from PBR to HBR format, if the CacheID field is unused, its value shall be cleared to 0.

##### <span id="page-424-2"></span>7.7.6.6.3 CXL.mem

Several CXL.mem message classes in HBR format have a 4-bit LD-ID field that is used by Type 3 MLDs for determining the targeted LD. This feature is supported by both 68B and 256B HBR formats. PBR format conveys the necessary information via PIDs instead of an LD-ID field. [Table 7-89](#page-424-1) summarizes which message classes contain the LD-ID field.

<span id="page-424-1"></span>**Table 7-89. Summary of LD-ID Field**

| Msg Class |         | LD-ID Field |          |  |  |
|-----------|---------|-------------|----------|--|--|
|           | 68B HBR | 256B HBR    | 256B PBR |  |  |
| M2S Req   | Yes     | Yes         | No       |  |  |
| M2S RwD   | Yes     | Yes         | No       |  |  |
| S2M NDR   | Yes     | Yes         | No       |  |  |
| S2M DRS   | Yes     | Yes         | No       |  |  |
| S2M BISnp | N/A     | In BI-ID    | No       |  |  |
| M2S BIRsp | N/A     | In BI-ID    | No       |  |  |

CXL.mem BISnp/BIRsp messages support the Back-Invalidate feature in 256B HBR format via a 12-bit BI-ID field, which determines the routing for BIRsp. This feature and its associated field are not supported in 68B HBR format. PBR format supports this feature and conveys the necessary information via 12-bit PIDs. [Table 7-90](#page-425-0) summarizes which message classes contain the BI-ID field.

In 256B HBR format over an MLD link, the 12-bit BI-ID field in BISnp/BIRsp carries the 4-bit LD-ID value, and the remaining 8 bits are all 0s. In 256B HBR format over non-MLD links, the 12-bit BI-ID field carries the 8-bit Bus Number of the HDM-DB device, and the remaining 4 bits are all 0s.

<span id="page-425-0"></span>**Table 7-90. Summary of BI-ID Field**

| Msg Class | BI-ID Field |          |          |
|-----------|-------------|----------|----------|
|           | 68B HBR     | 256B HBR | 256B PBR |
| S2M BISnp | N/A         | Yes      | No       |
| M2S BIRsp | N/A         | Yes      | No       |

For messages that contain a BI-ID field, in some cases an HBR or PBR DSP needs to know whether to propagate or assign the BI-ID. This information is configured by host software and is contained in the CXL BI Decoder Capability Structure (see [Section 8.2.4.27\)](#page-590-1).

The Direct P2P CXL.mem for Accelerators use case, supported only by PBR fabrics, is not covered in this section; see [Section 7.7.10.](#page-444-1)

[Table 7-91](#page-425-1) summarizes the HBR switch routing for CXL.mem message classes. [Table 7-92](#page-426-1) summarizes the PBR switch routing for CXL.mem message classes.

<span id="page-425-1"></span>**Table 7-91. Summary of HBR Switch Routing for CXL.mem Message Classes**

| Message Class | Switch Routing                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
|---------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| M2S Request   | For HBR switch routing of M2S requests downstream toward the device, the<br>HDM Decoder at the USP determines the PCIe-defined PortID of the DSP at<br>each switch level. For a DSP above an MLD, there is a vPPB for each LD,<br>which provides the LD-ID to insert in the request message.                                                                                                                                                                    |
| S2M Response  | For HBR switch routing of S2M responses upstream to the USP, the DSP relies<br>on its vPPB binding at each switch level. For a DSP immediately above an<br>MLD, there is a vPPB for each LD, and the LD-ID in the response message<br>identifies the associated vPPB.                                                                                                                                                                                           |
| S2M BISnp     | For HBR switch routing of S2M BISnp requests upstream to the USP, the DSP<br>relies on its vPPB binding at each switch level. For a DSP immediately above<br>an MLD, there is a vPPB for each LD, and the BI-ID in the response message<br>carries an LD-ID that identifies the associated vPPB. The DSP then looks up<br>the BusNum associated with its vPPB, places the BusNum in the BI-ID for<br>later use in routing the associated BIRsp back to the DSP. |
| M2S BIRsp     | For HBR switch routing of M2S BIRsp messages downstream to the DSP<br>immediately above the device, the USP at each switch level relies on the BI<br>ID that carries the BusNum of the target DSP. The HBR switch then uses<br>BusNum routing.                                                                                                                                                                                                                  |

In an HBR switch, when filling in a subset of the bits in the BI-ID field with a value, the remaining bits in the BI-ID field shall be cleared to 0.

Within a PBR fabric, most CXL.mem message classes are routed edge-to-edge and do not use vDSP/vUSP bindings. The exceptions are M2S Req/RwD message classes with LD-FAM when host software has configured HDM Decoders in the Host ES USP to route them, in which case vDSP/vUSP bindings are used. See details regarding PBR Message Routing across the Fabric in [Section 7.7.6.2.](#page-416-0)

When HDM-DB devices are attached to an HBR switch below a PBR fabric, the FM must allocate and assign a unique PID for each HDM-DB device. This enables PBR switches to convert between an HDM-DB device's unique PID and Bus Number when needed.

<span id="page-426-1"></span>**Table 7-92. Summary of PBR Switch Routing for CXL.mem Message Classes**

| Message Class | Switch Routing                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |  |  |
|---------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--|--|
|               | FAST/LDST Decoder Case: For Host ES routing of M2S requests<br>downstream to the Edge DSP, the FAST/LDST decoder at the USP determines<br>the DPID for routing the message edge-to-edge.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |  |  |
| M2S Request   | HDM Decoder Case: For hierarchical routing of M2S requests downstream<br>toward the Edge DSP, the HDM Decoder at the USP of each ES determines<br>the egress vPPB (EvPPB), which contains an appropriate DPID. A vDSP in the<br>Host ES contains the DPID/SPID that is used for targeting its partner<br>Downstream ES vUSP. A DSP vPPB contains its dedicated DPID. Both host<br>and Downstream ESs use PBR routing locally because a DSP above an MLD<br>relies on the request having a valid SPID.                                                                                                                                                                                                          |  |  |
|               | For a DSP immediately above an MLD, a 16-entry CAM match using the SPID<br>returns the associated LD-ID, which determines the LD-specific vPPB to use<br>and is also inserted in the request message. For a DSP above a GFD, the<br>message remains in PBR format.                                                                                                                                                                                                                                                                                                                                                                                                                                             |  |  |
| S2M Response  | For Edge DSP routing of S2M responses upstream to the Edge USP, the Edge<br>DSP's vPPB contains the DPID for routing the message edge-to-edge. For a<br>DSP immediately above an MLD, there is a vPPB for each LD, and the LD-ID<br>in the response message identifies the associated vPPB. For a DSP above a<br>GFD, the message is already in PBR format and remains so.                                                                                                                                                                                                                                                                                                                                     |  |  |
| S2M BISnp     | For Edge DSP routing of S2M BISnp messages upstream to the Edge USP, the<br>Edge DSP's vPPB contains the DPID for routing the message edge-to-edge.<br>For an Edge DSP immediately above an MLD, there is a vPPB for each LD, and<br>the BI-ID in the BISnp carries an LD-ID that identifies the associated vPPB.<br>The Edge DSP uses its vPPB's PID for the SPID.<br>For an Edge DSP above an HBR USP, the BI-ID contains the BusNum                                                                                                                                                                                                                                                                         |  |  |
|               | associated with the HDM-DB device. The Edge DSP uses the BusNum to look<br>up the associated SPID from a 256-entry table.<br>At the Edge USP, the USP converts the BISnp to HBR format, copying the<br>SPID value into the BI-ID.                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |  |  |
| M2S BIRsp     | For Edge USP routing of M2S BIRsp messages downstream to the Edge DSP<br>above the HDM-DB device, the Edge USP converts the BIRsp to PBR format,<br>using the BI-ID value as the DPID, and then routes the BIRsp edge-to-edge.<br>For an Edge DSP immediately above an MLD, a 16-entry CAM match using<br>the SPID returns the associated LD-ID, which determines the LD-specific<br>vPPB to use and is also inserted in the BI-ID field of the BIRsp. For an Edge<br>DSP above an HBR switch USP, the DSP converts the BIRsp to HBR format,<br>looking up the target BusNum in a 4k-entry table using the DPID, then<br>copying it to the BI-ID. For a DSP above a GFD, the message remains in PBR<br>format. |  |  |

At an Edge DSP, when converting a downstream CXL.mem message from PBR to HBR format, if an LD-ID or BI-ID field is unused, its value shall be cleared to 0. Also, when filling in a subset of the bits in the BI-ID field with a value, the remaining bits in the BI-ID field shall be cleared to 0.

#### <span id="page-426-0"></span>7.7.6.7 HBR Switch Port Processing of CXL Messages

[Table 7-93,](#page-427-0) [Table 7-94,](#page-427-1) and [Table 7-95](#page-428-1) summarize how HBR switches perform port processing of CXL.io, CXL.cache, and CXL.mem messages, respectively. A USP is below either an RP, a PBR DSP, or an HBR DSP. A USP can be in only one Virtual Hierarchy. A DSP is above either an HBR switch USP, an SLD, or an MLD.

For conciseness, there are many abbreviations within the tables. US stands for upstream. DS stands for downstream. P2P stands for peer-to-peer. DMA stands for direct memory access. Direct P2P stands for UIO Direct P2P to HDM. BusNum stands for Bus Number. "" stands for assignment (e.g., "LD-ID Prefix vPPB context" means "the LD-ID prefix is assigned a value from the associated vPPB context"). Text beginning with "PCIe" (also shown in gold) means that the routing is defined in PCIe Base Specification.

In the CXL.io table (see Table 7-93), not all TLP types are explicitly covered; however, those not listed are usually handled by standard PCIe routing mechanisms (e.g., PCIe Messages are not explicitly covered, but ID-routed Messages are handled by PCIe ID routing, and address-routed Messages are handled by PCIe Memory Address routing).

<span id="page-427-0"></span>**HBR Switch Port Processing Table for CXL.io Table 7-93.** 

| Message Class                                        | HBR USP below RP<br>or PBR/HBR DSP                         | HBR DSP                                                  |           |                                                                                                                         |  |                                                                                      |
|------------------------------------------------------|------------------------------------------------------------|----------------------------------------------------------|-----------|-------------------------------------------------------------------------------------------------------------------------|--|--------------------------------------------------------------------------------------|
| and Direction                                        |                                                            | Above HBR USP                                            | Above SLD | Above MLD                                                                                                               |  |                                                                                      |
| Cfg Req<br>DS                                        | PCIe ID routing                                            | PCIe ID routing                                          |           | PCIe ID routing                                                                                                         |  | PCIe ID routing LD-ID Prefix←vPPB context                                            |
| Mem Req<br>DS/US/P2P<br>Incl UIO DMA<br>Excl HDM UIO | PCIe Mem addr<br>routing                                   | PCIe Mem addr routing                                    |           | PCIe Mem addr routing US: L vPPB DS: L                                                                                  |  | PCIe Mem addr routing US: LD-ID Prefix identifies vPPB DS: LD-ID Prefix←vPPB context |
| HDM UIO Req<br>Direct P2P and<br>Host Requester      | US: PCIe Mem addr<br>routing<br>DS: HDM Decoder<br>routing | US: PCIe Mem addr routing DS/Direct P2P: USP HDM Decoder |           | US: PCIe Mem addr routing DS/Direct P2P: USP HDM Decoder US: LD-ID Prefix identifies vPPB DS: LD-ID Prefix←vPPB context |  |                                                                                      |
| <b>Cpl</b><br>US                                     | PCIe ID routing                                            | PCIe ID routing                                          |           | LD-ID Prefix identifies vPPB PCIe ID routing                                                                            |  |                                                                                      |
| <b>Cpl</b><br>DS                                     | PCIe ID routing                                            | PCIe ID routing                                          |           | PCIe ID routing                                                                                                         |  | PCIe ID routing LD-ID Prefix←vPPB context                                            |

<span id="page-427-1"></span>**Table 7-94. HBR Switch Port Processing Table for CXL.cache** 

| Message Class<br>and Direction | HBR USP below RP or PBR/HBR DSP                             | HBR DSP                                             |                                                          |           |
|--------------------------------|-------------------------------------------------------------|-----------------------------------------------------|----------------------------------------------------------|-----------|
|                                |                                                             | Above HBR USP                                       | Above SLD                                                | Above MLD |
| D2H Req<br>US                  | Propagate CacheID                                           | Propagate CacheID<br>vPPB binding routing<br>to USP | CacheID←Local Cache ID field vPPB binding routing to USP |           |
| H2D Rsp/DH<br>DS               | Propagate CacheID<br>PortID←Cache ID<br>Route Table         | Propagate CacheID                                   | Propagate Cache ID<br>(SLD should ignore it)             |           |
| H2D Req                        | PortID routing to DSP<br>OS must handle multi-<br>level HBR |                                                     |                                                          |           |
| D2H Rsp/DH<br>US               | -                                                           | vPPB binding routing to USP                         |                                                          |           |

<span id="page-428-1"></span>

|  | Table 7-95. | HBR Switch Port Processing Table for CXL.mem |  |  |  |
|--|-------------|----------------------------------------------|--|--|--|
|--|-------------|----------------------------------------------|--|--|--|

| Message Class<br>HBR USP below RP |                                                               | HBR DSP                                                                                                                                         |                                                      |                                                                                                              |
|-----------------------------------|---------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------|--------------------------------------------------------------------------------------------------------------|
| and Direction                     | or PBR/HBR DSP                                                | Above HBR USP                                                                                                                                   | Above SLD                                            | Above MLD                                                                                                    |
| M2S Req<br>DS                     | PortIDHDM Decoder<br>(HPA)<br>Routing to DSP uses<br>PortID  | Propagate LD-ID (not used by these receivers)                                                                                                   |                                                      | LD-IDvPPB context                                                                                           |
| S2M Rsp<br>US                     | Propagate LD-ID<br>(not used by these<br>receivers)           | vPPB binding routing to USP<br>Propagate LD-ID (not used for internal switch routing)                                                           | LD-ID identifies vPPB<br>vPPB binding routing to USP |                                                                                                              |
| S2M BISnp<br>US                   | BI-ID[7:0] contains<br>BusNum<br>Propagate BI-ID              | Received BI-ID is ignored<br>Propagate BI-ID<br>BI-ID[7:0]<br>BusNum(vPPB)<br>vPPB binding routing<br>to USP<br>vPPB binding routing<br>to USP |                                                      | BI-ID[3:0] contains LD-ID<br>LD-ID identifies vPPB<br>BI-ID[7:0]BusNum(vPPB)<br>vPPB binding routing to USP |
| M2S BIRsp<br>DS                   | Target BusNum<br>BI-ID[7:0]<br>PCIe BusNum routing<br>to DSP | Propagate BI-ID                                                                                                                                 | Propagate BI-ID<br>(SLD should ignore it)            | BI-ID[3:0]LD-ID(vPPB)                                                                                       |

#### <span id="page-428-0"></span>7.7.6.8 PBR Switch Port Processing of CXL Messages

[Table 7-96,](#page-429-0) [Table 7-97,](#page-430-0) and [Table 7-98](#page-431-0) summarize how PBR switches perform port processing of CXL.io, CXL.cache, and CXL.mem messages, respectively. A PBR USP must be below an RP and can be in only one Virtual Hierarchy. A PBR DSP is above either an SLD, an MLD, a GFD, or an HBR switch USP. A PBR FPort can only be connected to another PBR FPort in a different PBR switch.

For conciseness, there are many abbreviations within the tables. US stands for upstream. DS stands for downstream. P2P stands for peer-to-peer. DMA stands for direct memory access. Direct P2P stands for UIO Direct P2P to HDM. EvPPB stands for Egress vPPB. BusNum stands for Bus Number. RT stands for the CacheID Route Table. "" stands for assignment (e.g., "LD-ID Prefix vPPB context" means "the LD-ID prefix is assigned a value from the associated vPPB context"). Also referring to a vPPB context, vPPB.root.PID stands for the PID of the associated Edge USP, and vPPB.self.PID stands for the PID of the vPPB itself. Eg2Eg means Edge-to-Edge. Text beginning with "PCIe" (also shown in gold) means that the routing is defined in PCIe Base Specification.

In the CXL.io table (see [Table 7-96\)](#page-429-0), not all TLP types are explicitly covered; however, those not listed are usually handled by standard PCIe routing mechanisms (e.g., PCIe Messages are not explicitly covered, but ID-routed Messages are handled by PCIe ID routing, and address-routed Messages are handled by PCIe Memory Address routing).

In the CXL.mem table (see [Table 7-98\)](#page-431-0) the Direct P2P CXL.mem for Accelerators use case is not covered; see [Section 7.7.10.3.](#page-447-0)

Table 7-96. PBI Switch Port Processing Table for CXL.io (Sheet 1 of 2)

| Message                       | Edge USP<br>All vays below<br>an RP                                            | Host ES FPort with vDSP(s)                                                                                                                                                  | Downstream ES FPort with vUSP(s)                                                                                                                                     | Edge DSP in Either Host ES or Downstream ES                                                                                                                                 |           |                                                                                          |           |  |
|-------------------------------|--------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------|------------------------------------------------------------------------------------------|-----------|--|
| Class and<br>Direction        |                                                                                |                                                                                                                                                                             |                                                                                                                                                                      | Above HBR<br>Switch USP                                                                                                                                                     | Above SLD | Above MLD                                                                                | Above GFD |  |
|                               | PCIe p routing<br>to DSP or vDSP                                               | vDSP converts to PBR<br>fmt;<br>FPort xmits to vUSP's<br>FPort                                                                                                              | vUSP matches DPID/<br>SPID;<br>vUSP converts to HBR<br>fmt;<br>PCIe ID routing to DSP                                                                                | PCIe ID routing                                                                                                                                                             |           | PCIe ID routing<br>LD-ID Prefix←vPPB LD-ID                                               | N/A       |  |
|                               | PCIe Mem addr<br>routing                                                       | DS: vDSP converts to<br>PBR fmt;<br>FPort xmits to vUSP's<br>FPort<br>US/P2P: vDSP<br>matches DPID/SPID;<br>vDSP converts to HBR<br>fmt;<br>PCIe Mem addr<br>routing        | DS: vUSP matches DPID/SPID; vUSP converts to HBR fmt; PCIe Mem addr routing US: vUSP converts to PBR fmt; FPort xmits to vDSP's FPort                                | PCIe Mem addr routing                                                                                                                                                       |           | PCIe Mem addr routing DS: LD-ID Prefix← vPPB.LD-ID US/P2P: LD-ID Prefix\nidentifies vPPB | N/A       |  |
| Cpl<br>US/P2P<br>Excl HDM UIO | PCI D routing                                                                  | vDSP matches DPID/<br>SPID;<br>vDSP converts to HBR<br>fmt;<br>PCIe ID routing                                                                                              | vUSP converts to PBR<br>fmt;<br>FPort xmits to vDSP's<br>FPort                                                                                                       | PCIe ID routing                                                                                                                                                             |           | LD-ID Prefix identifies vPPB<br>PCIe ID routing                                          | N/A       |  |
|                               | PCIe ID routing<br>o DSP or vDSP                                               | vDSP converts to PBR<br>fmt;<br>FPort xmits to vUSP's<br>FPort                                                                                                              | vUSP matches DPID/<br>SPID;<br>vUSP converts to HBR<br>fmt;<br>PCIe ID routing to DSP                                                                                | PCIe ID routing                                                                                                                                                             |           | PCIe ID routing<br>LD-ID Prefix←vPPB.LD-ID                                               | N/A       |  |
| case for Direct               | Direct P2P: N/A<br>Host Requester (DS):<br>HDM Decoder routes<br>o DSP or vDSP | DS: vDSP converts to<br>PBR fmt;<br>FPort xmits to vUSP's<br>FPort<br>US/P2P: vDSP<br>matches DPID/SPID;<br>vDSP converts to HBR<br>fmt;<br>USP's HDM Decoder<br>routes P2P | DS: vUSP matches<br>DPID/SPID;<br>vUSP converts to HBR<br>fmt;<br>HDM Decoder routes to<br>DSP<br>US: vUSP converts to<br>PBR fmt;<br>FPort xmits to vDSP's<br>FPort | US/P2P: If above MLD, LD-ID Prefix identifies vPPB; USP/vUSP HDM Decoder routes US or P2P within same switch DS: Convert to HBR fmt; if above MLD, LD-ID Prefix +vPPB.LD-ID |           | N/A                                                                                      |           |  |

<span id="page-429-0"></span>![](_page_429_Picture_3.jpeg)

Table 7-96. PBR Switch Port Processing Table for CXL.io (Sheet 2 of 2)

| Message <b>1</b>                                                           | Edge USP                                                                        | Host ES FPort<br>with vDSP(s)                                                  | Downstream ES FPort with vUSP(s)                               | Edge DSP in Either Host ES or Downstream ES                                                                                                                                |           |                                            |                            |
|----------------------------------------------------------------------------|---------------------------------------------------------------------------------|--------------------------------------------------------------------------------|----------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------|--------------------------------------------|----------------------------|
| Class and Direction                                                        | Always below<br>an RP                                                           |                                                                                |                                                                | Above HBR<br>Switch USP                                                                                                                                                    | Above SLD | Above MLD                                  | Above GFD                  |
| HDM UIO Cpl<br>HDM Decoder<br>case for Direct<br>P2P and Host<br>Requester | Direct P2P: N/A Host Requester (US): PCIe D routing                             | vDSP matches DPID/<br>SPID;<br>vDSP converts to HBR<br>fmt;<br>PCIe ID routing | vUSP converts to PBR<br>fmt;<br>FPort xmits to vDSP's<br>FPort | US: If above MLD, LD-ID Prefix identifies vPPB; PCIe ID routing DS: PCIe ID routing; if above MLD, LD-ID Prefix +vPPB.LD-ID                                                |           | N/A                                        |                            |
| FAST/LDST case for Direct P2P and Host Requester                           | Direct P2P: N/A Host Requester (DS): FAST/LDST converts to PBR and routes Eg2Eg | Route Eg2Eg                                                                    | Route Eg2Eg                                                    | US/P2P: If above MLD, LD-ID Prefix identifies vPPB; FAST/LDST converts to PBR and routes Eg2Eg DS: Convert to HBR fmt; if above MLD, LD-ID Prefix←CAM <sub>16</sub> (SPID) |           |                                            | US: N/A<br>DS: Keep in PBR |
| HDM UIO Cpl<br>FAST/LDST<br>case for Direct<br>P2P and Host<br>Requester   | Direct P2P: N/A Host Requester (US): Convert to HBR                             | Route Eg2Eg                                                                    | Route Eg2Eg                                                    | US: If above MLD, LD-ID Prefix identifies vPPB; convert to PBR using UIO ID-based Rerouter; route Eg2Eg DS: Convert to HBR                                                 |           | US: Keep in PBR;<br>route Eg2Eg<br>DS: N/A |                            |

**Table 7-97. PBR switch Port Processing Table for CXL.cache**

| Message<br>Class and | Edge USP<br>Always below                                     | Host ES FPort | Downstream ES FPort | Edge DSP in Either Host ES or Downstream ES                   |                                                                |           |           |  |
|----------------------|--------------------------------------------------------------|---------------|---------------------|---------------------------------------------------------------|----------------------------------------------------------------|-----------|-----------|--|
| Direction            | an RP                                                        | with vDSP(s)  | with vUSP(s)        | Above HBR Switch USP                                          | Above SLD                                                      | Above MLD | Above GFD |  |
| D2H Req<br>US        | Convert to HBR fmt<br>CacheID←CAM <sub>16</sub> (SPID)       | Route Eg2Eg   | Route Eg2Eg         | Convert to PBR fmt DPID←vPPB.root.PID SPID←RT(CacheID)        | Convert to PBR fmt<br>DPID←vPPB.root.PID<br>SPID←vPPB.self.PID |           |           |  |
| H2D Rsp/DH  <br>DS   | Convert to PBR fmt DPID RT(CacheID)                          | Route Eg2Eg   | Route Eg2Eg         | Convert to HBR fmt                                            | Convert to HBR fmt                                             |           |           |  |
| H2D Req              | Convert to PBR fmt<br>DPID←RT(CacheID)<br>SPID←vPPB.self.PID | Route Eg2Eg   | Route Eg2Eg         | 256B: CacheID←CAM <sub>16</sub> (DPID)<br>68B: Has no CacheID | 256B: CacheID←0<br>68B: Has no CacheID                         |           |           |  |
| D2H Rsp/DH<br>US     | Convert to HBR fmt                                           | Route Eg2Eg   | Route Eg2Eg         | Convert to PBR fmt<br>DPID←vPPB.root.PID                      | Convert to PBR fmt DPID←vPPB.root.PID                          |           |           |  |

<span id="page-430-0"></span>![](_page_430_Picture_5.jpeg)

Table 7-98. PB: Switch Port Processing Table for CXL.mem

|                   | Edge USP                                                                                                                   | Host ES FPort<br>with vDSP(s)         | Downstream ES FPort<br>with vUSP(s)                                                                                 | Edge DSP in Either Host ES or Downstream ES                                                       |                                                                |                                                                                                                      |                                 |  |
|-------------------|----------------------------------------------------------------------------------------------------------------------------|---------------------------------------|---------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------|----------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------|---------------------------------|--|
|                   | A ways below<br>an RP                                                                                                      |                                       |                                                                                                                     | Above HBR<br>Switch USP                                                                           | Above SLD                                                      | Above MLD                                                                                                            | Above GFD                       |  |
|                   | FAST or LDST: Convert to PBR fmt DPID (xxST(HPA) SPID (vPPB.self.PID                                                       | Route Eg2Eg                           | Route Eg2Eg                                                                                                         | Convert to HBR fmt LD-ID←0; is unused                                                             |                                                                |                                                                                                                      | LD-ID is N/A<br>Keep in PBR fmt |  |
| M2S Req/Rado      | HDM Decoder: Convert to PBR fmt EvPPB←HDM-Dec(HPA) DPHD←EvPPB.bndg.PID SPID←vPPB.self.PID Route to local DSP or vDSP FPort | vDSP's FPort xmits<br>to vUSP's FPort | vUSP matches DPID/SPID<br>vUSP keeps in PBR fmt<br>EvPPB←HDM-Dec(HPA)<br>DPID←EvPPB.self.PID<br>Route to egress DSP |                                                                                                   |                                                                | LD-ID←CAM <sub>16</sub> (SPID)<br>Convert to HBR MLD fmt                                                             | N/A                             |  |
| S2M NDR/DRS<br>US | Convert to HBR fmt<br>LD-ID←0; is unused                                                                                   | Route Eg2Eg                           | Route Eg2Eg                                                                                                         | LD-ID is unused<br>Convert to PBR fmt<br>DPID ← vPPB.root.PID                                     |                                                                | LD-ID identifies vPPB<br>Convert to PBR fmt<br>DPID←vPPB.root.PID                                                    | Keep in PBR fmt<br>LD-ID is N/A |  |
| S2M BISnp<br>US   | Convert to HBR fmt<br>BI-ID[11:0] ←SPID                                                                                    | Route Eg2Eg                           | Route Eg2Eg                                                                                                         | Convert to PBR fmt<br>DPID←vPPB.root.PID<br>BusNum←BI-ID[7:0]<br>SPID←RAM <sub>256</sub> (BusNum) | Convert to PBR fmt<br>DPID←vPPB.root.PID<br>SPID←vPPB.self.PID | BI-ID[3:0] contains LD-ID<br>LD-ID identifies vPPB<br>Convert to PBR fmt<br>DPID←vPPB.root.PID<br>SPID←vPPB.self.PID | Keep in PBR fmt                 |  |
| M2S BIRsp<br>DS   | Convert to PBR fmt<br>DPID←BI-ID[11:0]                                                                                     | Route Eg2Eg                           | Route Eg2Eg                                                                                                         | Convert to HBR fmt<br>BusNum←RAM <sub>4k</sub> (DPID)<br>BI-ID[7:0]←BusNum                        | Convert to HBR fmt<br>BI-ID is unused                          | Convert to HBR fmt<br>LD-ID←CAM <sub>16</sub> (SPID)<br>BI-ID[3:0]←vPPB.LD-ID                                        | Keep in PBR fmt                 |  |

<span id="page-431-0"></span>![](_page_431_Picture_3.jpeg)

#### <span id="page-432-0"></span>7.7.6.9 PPB and vPPB Behavior of PBR Link Ports

A PBR Link port has two varieties: an Inter-Switch Link (ISL) and a GFD Link.

The ISL case is a downstream-to-downstream crosslink. The DSP on each side of the link is managed by the FM with assistance from switch firmware. The full PCIe capabilities of a DSP shall be available. Bus master enable, AER, DPC, and other capabilities that an host typically controls will be controlled by the FM and/or switch firmware.

Other users of an ISL can be any number of VHs. The ISL (and as many switch hops and additional ISLs as it takes) functions as a single link between vDSP and vUSP. Any one ISL can potentially be shared by multiple VHs. Because a VH shares the link with other VHs, there is no way for a VH to control any of the link physical characteristics. However, the Host ES vDSP shall reflect the physical link settings for the fabric port DSP to which it is bound (e.g., link speed, lane margining, etc.).

A GFD PBR link is similar to an ISL in that many VH can share it. It is different however in that no vDSP nor vUSP is associated with it. The link itself is a simple up-down link, with the switch having an (FM-owned) DSP leading, via the PBR link, to the USP of a GFD. A switch DSP should have full PCIe capabilities, just like for an ISL or any other DSP.

The remainder of this section focuses on the vDSP and vUSP perspective, from the PCIe configuration space, for a variety of capabilities:

- "Supported" means that the PCIe register is available to be read and written by the host
- "Not supported" means that the register is either read-only or the capability is unavailable
- "Mirrors DSP" means that the values reflect the (typically physical link) value in the DSP
- "Read/Write with no effect" implies that the vDSP/vUSP register will be unaffected by reads and writes

It is expected that a fabric port DSP supports all PCIe capabilities required by the PCIe spec for a downstream port. DPC, which is optional for PCIe, is required for CXL for a DSP that is a fabric port.

##### 7.7.6.9.1 ISL Type 1 Configuration Space Header

<span id="page-432-1"></span>**Table 7-99. ISL Type 1 Configuration Space Header**

| Register       | Register Fields                 | FM-owned DSP  | vDSP          | vUSP          |
|----------------|---------------------------------|---------------|---------------|---------------|
|                | Parity Error<br>Response Enable | Supported     | Supported     | Supported     |
| Bridge Control | SERR# Enable                    | Supported     | Supported     | Supported     |
| Register       | ISA Enable                      | Not Supported | Not Supported | Not Supported |
|                | Secondary Bus<br>Reset          | Supported     | Supported     | Supported     |

##### 7.7.6.9.2 ISL PCIe-compatible Configuration Register

<span id="page-433-0"></span>**Table 7-100. ISL PCIe Configuration Space Header**

| Register | Register Fields          | FM-owned DSP  | vDSP      | vUSP      |
|----------|--------------------------|---------------|-----------|-----------|
| Command  | I/O Space Enable         | Hardwire to 0 | Supported | Supported |
|          | Memory Space Enable      | Supported     | Supported | Supported |
|          | Bus Master Enable        | Not Supported | Supported | Supported |
| Command  | Parity Error Response    | Supported     | Supported | Supported |
|          | SERR# Enable             | Supported     | Supported | Supported |
|          | Interrupt Disable        | Supported     | Supported | Supported |
|          | Interrupt Status         | Hardwire to 0 | Supported | Supported |
| Status   | Master Data Parity Error | Supported     | Supported | Supported |
| Status   | Signaled System Error    | Supported     | Supported | Supported |
|          | Detected Parity Error    | Supported     | Supported | Supported |

**ISL PCIe Capability Structure**

<span id="page-433-1"></span>**Table 7-101. ISL PCIe Capability Structure (Sheet 1 of 3)**

| Register            | Register Fields                            | FM-owned DSP       | vDSP                      | vUSP          |
|---------------------|--------------------------------------------|--------------------|---------------------------|---------------|
|                     | Max Payload Size Supported                 | FM Configured      | Mirrors DSP               | Mirrors DSP   |
| Device Capabilities | Phantom Functions Supported                | 0                  | 0                         | 0             |
|                     | Extended Tag Field Supported               | Supported          | Supported                 | Supported     |
| Device Control      | Max Payload Size                           | FM Configured      | Mirrors DSP               | Mirrors DSP   |
|                     | Link Bandwidth Notification Capability     | 0                  | 0                         | 0             |
| Link Capabilities   | ASPM Support                               | No LOs             | no L0s                    | no L0s        |
|                     | Clock Power Management                     | No PM L1 Substates | Mirrors DSP               | Mirrors DSP   |
|                     | ASPM Control                               | Supported          | Not Supported             | Not Supported |
|                     | Link Disable                               | Supported          | Supported                 | Not Supported |
|                     | Retrain Link                               | Supported          | Read/Write with no effect | Not Supported |
|                     | Common Clock Configuration                 | Supported          | Read/Write with no effect |               |
|                     | Extended Synch                             | Supported          | Read/Write with no effect |               |
| Link Control        | Hardware Autonomous Width Disable          | Supported          | Read/Write with no effect |               |
|                     | Link Bandwidth Management Interrupt Enable | Supported          | Read/Write with no effect | Not Supported |
|                     | Link Autonomous Bandwidth Interrupt Enable | Supported          | Supported Not Supporte    |               |
|                     | Flit Mode Disable                          | 0                  | 0                         | 0             |
|                     | DRS Signaling Control                      | Supported          | Supported                 | Not Supported |

**Table 7-101. ISL PCIe Capability Structure (Sheet 2 of 3)**

| Register              | Register Fields                    | FM-owned DSP | vDSP                                       | vUSP                         |
|-----------------------|------------------------------------|--------------|--------------------------------------------|------------------------------|
| Link Status           | Current Link Speed                 | Supported    | Mirrors DSP                                | Mirrors DSP                  |
|                       | Negotiated Link Speed              | Supported    | Mirrors DSP                                | Mirrors DSP                  |
|                       | Link Training                      | Supported    | 0                                          | 0                            |
|                       | Slot Clock Configuration           | Supported    | Mirrors DSP                                | Mirrors DSP                  |
|                       | Data Link Layer Active             | Supported    | Mirrors DSP                                | 0                            |
|                       | Link Bandwidth Management Status   | Supported    | Mirrors DSP                                | 0                            |
|                       | Link Autonomous Bandwidth Status   | Supported    | Mirrors DSP                                | 0                            |
|                       | Hot-Plug Surprise                  | Supported    | Mirrors DSP                                | 0                            |
| Slot Capabilities     | Physical Slot Number               | Supported    | Supported                                  | 0                            |
|                       | Attention Button Pressed           | Supported    | Supported                                  | 0                            |
|                       | Power Fault Detected               | Supported    | Mirrors DSP                                | 0                            |
|                       | MRL Sensor Changed                 | Supported    | Mirrors DSP                                | 0                            |
|                       | Presence Detect Changed            | Supported    | Supported                                  | 0                            |
| Slot Status           | MRL Sensor State                   | Supported    | Mirrors DSP                                | 0                            |
|                       | Presence Detect State              | Supported    | Supported                                  | 0                            |
|                       | Electromechanical Interlock Status | Supported    | Mirrors DSP                                | 0                            |
|                       | Data Link Layer State Changed      | Supported    | Supported                                  | 0                            |
| Device Capabilities 2 | All bits                           | Supported    | Supported                                  | 0                            |
|                       | ARI Forwarding Enable              | Supported    | Supported                                  | 0                            |
|                       | Atomic Op Egress Blocking          | Supported    | Supported                                  | 0                            |
|                       | LTR Mechanism Enabled              | Supported    | Supported                                  | 0                            |
| Device Control 2      | Emergency Power Reduction Request  | Supported    | Read/Write with no<br>effect               | 0                            |
|                       | End-End TLP Prefix Blocking        | Supported    | Mirrors DSP. Read/<br>Write with no effect | 0                            |
|                       | Target Link Speed                  | Supported    | Read/Write with no<br>effect               | Read/Write with no<br>effect |
|                       | Enter Compliance                   | Supported    | Read/Write with no<br>effect               | Read/Write with no<br>effect |
|                       | Hardware Autonomous Speed Disable  | Supported    | Read/Write with no<br>effect               | Read/Write with no<br>effect |
|                       | Selectable De-emphasis             | Supported    | Read/Write with no<br>effect               | Read/Write with no<br>effect |
| Link Control 2        | Transmit Margin                    | Supported    | Read/Write with no<br>effect               | Read/Write with no<br>effect |
|                       | Enter Modified Compliance          | Supported    | Read/Write with no<br>effect               | Read/Write with no<br>effect |
|                       | Compliance SOS                     | Supported    | Read/Write with no<br>effect               | Read/Write with no<br>effect |
|                       | Compliance Preset/De-emphasis      | Supported    | Read/Write with no<br>effect               | Read/Write with no<br>effect |

Table 7-101. ISL PCIe Capability Structure (Sheet 3 of 3)

| Register      | Register Fields                             | FM-owned DSP | vDSP                      | vUSP                      |
|---------------|---------------------------------------------|--------------|---------------------------|---------------------------|
| Link Status 2 | Current De-emphasis Level                   | Supported    | Mirrors DSP               | Mirrors DSP               |
|               | Equalization 8.0 GT/s Complete              | Supported    | Mirrors DSP               | Mirrors DSP               |
|               | Equalization 8.0 GT/s Phase 1<br>Successful | Supported    | Mirrors DSP               | Mirrors DSP               |
|               | Equalization 8.0 GT/s Phase 2<br>Successful | Supported    | Mirrors DSP               | Mirrors DSP               |
|               | Equalization 8.0 GT/s Phase 3<br>Successful | Supported    | Mirrors DSP               | Mirrors DSP               |
|               | Link Equalization Request 8.0 GT/s          | Supported    | Read/Write with no effect | Read/Write with no effect |
|               | Retimer Presence Detected                   | Supported    | Mirrors DSP               | Mirrors DSP               |
|               | Two Retimers Presence Detected              | Supported    | Mirrors DSP               | Mirrors DSP               |
|               | Crosslink Resolution                        | Supported    | All 0s                    | All 0s                    |
|               | Flit Mode Status                            | Supported    | Supported                 | Supported                 |
|               | Downstream Component Presence               | Supported    | Supported                 | 0                         |
|               | DRS Message Received                        | Supported    | Supported                 | 0                         |

##### 7.7.6.9.4 ISL Secondary PCIe Capability Structure

All fields in the Secondary PCIe Capability Structure for a Virtual PPB shall behave identically to PCIe except the following:

<span id="page-435-0"></span>Table 7-102. ISL Secondary PCIe Extended Capability

| Register                           | Register Fields                                  | FM-owned DSP | vDSP                      | vUSP                      |
|------------------------------------|--------------------------------------------------|--------------|---------------------------|---------------------------|
|                                    | Perform<br>Equalization                          | Supported    | Read/Write with no effect | Read/Write with no effect |
| Link Control 3                     | Link Equalization<br>Request Interrupt<br>Enable | Supported    | Read/Write with no effect | Read/Write with no effect |
|                                    | Enable Lower SKP<br>OS Generation<br>Vector      | Supported    | Read/Write with no effect | Read/Write with no effect |
| Lane Error Status                  | All fields                                       | Supported    | Mirrors DSP               | Mirrors DSP               |
| Lane Equalization<br>Control       | All fields                                       | Supported    | Read/Write with no effect | Read/Write with no effect |
| Data Link Features<br>Capabilities | All fields                                       | Supported    | Mirror DSP                | Mirror DSP                |

##### 7.7.6.9.5 ISL Physical Layer 16.0 GT/s Extended Capability

All fields in the Physical Layer 16.0 GT/s Extended Capability Structure for a Virtual PPB shall behave identically to PCIe except the following:

<span id="page-436-0"></span>**Table 7-103. ISL Physical Layer 16.0 GT/s Extended Capability**

| Register                                                   | Register Fields                                    | FM-owned DSP | vDSP        | vUSP        |
|------------------------------------------------------------|----------------------------------------------------|--------------|-------------|-------------|
| 16.0 GT/s Status                                           | All fields                                         | Supported    | Mirrors DSP | Mirrors DSP |
| 16.0 GT/s Local<br>Data Parity<br>Mismatch Status          | Local Data Parity<br>Mismatch Status               | Supported    | Mirrors DSP | Mirrors DSP |
| 16.0 GT/s First<br>Retimer Data Parity<br>Mismatch Status  | First Retimer Data<br>Parity Mismatch<br>Status    | Supported    | Mirrors DSP | Mirrors DSP |
| 16.0 GT/s Second<br>Retimer Data Parity<br>Mismatch Status | Second Retimer<br>Data Parity<br>Mismatch Status   | Supported    | Mirrors DSP | Mirrors DSP |
| 16.0 GT/s Lane<br>Equalization Control                     | Downstream Port<br>16.0 GT/s<br>Transmitter Preset | Supported    | Mirrors DSP | Mirrors DSP |

##### 7.7.6.9.6 ISL Physical Layer 32.0 GT/s Extended Capability

All fields in the Physical Layer 32.0 GT/s Extended Capability Structure for a Virtual PPB shall behave identically to PCIe except the following:

<span id="page-436-1"></span>**Table 7-104. ISL Physical Layer 32.0 GT/s Extended Capability**

| Register                                | Register Fields                                             | FM-owned DSP | vDSP                      | vUSP                      |
|-----------------------------------------|-------------------------------------------------------------|--------------|---------------------------|---------------------------|
| 32.0 GT/s Control Register              | All fields                                                  | Supported    | Read/Write with no effect | Read/Write with no effect |
|                                         | Link Equalization<br>Request 32.0 GT/s                      | Supported    | Read/Write with no effect | Read/Write with no effect |
| 32.0 GT/s Status Register               | All fields except<br>Link Equalization<br>Request 32.0 GT/s | Supported    | Mirrors DSP               | Mirrors DSP               |
| Received Modified<br>TS Data 1 Register | All fields                                                  | Supported    | Mirrors DSP               | Mirrors DSP               |
| Received Modified<br>TS Data 2          | All fields                                                  | Supported    | Mirrors DSP               | Mirrors DSP               |
| Transmitted Modified TS Data 1          | All fields                                                  | Supported    | Mirrors DSP               | Mirrors DSP               |
| 32.0 GT/s Lane<br>Equalization Control  | Downstream Port<br>32.0 GT/s<br>Transmitter Preset          | Supported    | Mirrors DSP               | Mirrors DSP               |

##### 7.7.6.9.7 ISL Physical Layer 32.0 GT/s Extended Capability

All fields in the Physical Layer 64.0 GT/s Extended Capability Structure for a Virtual PPB shall behave identically to PCIe except the following:

<span id="page-437-0"></span>**Table 7-105. ISL Physical Layer 64.0 GT/s Extended Capability**

| Register                                | Register Fields                                             | FM-owned DSP | vDSP                      | vUSP                      |
|-----------------------------------------|-------------------------------------------------------------|--------------|---------------------------|---------------------------|
| 64.0 GT/s Control Register              | All fields                                                  | Supported    | Read/Write with no effect | Read/Write with no effect |
|                                         | Link Equalization<br>Request 64.0 GT/s                      | Supported    | Read/Write with no effect | Read/Write with no effect |
| 64.0 GT/s Status Register               | All fields except<br>Link Equalization<br>Request 64.0 GT/s | Supported    | Mirrors DSP               | Mirrors DSP               |
| Received Modified<br>TS Data 1 Register | All fields                                                  | Supported    | Mirrors DSP               | Mirrors DSP               |
| Received Modified<br>TS Data 2          | All fields                                                  | Supported    | Mirrors DSP               | Mirrors DSP               |
| Transmitted Modified<br>TS Data 1       | All fields                                                  | Supported    | Mirrors DSP               | Mirrors DSP               |
| 64.0 GT/s Lane<br>Equalization Control  | Downstream Port<br>64.0 GT/s<br>Transmitter Preset          | Supported    | Mirrors DSP               | Mirrors DSP               |

##### 7.7.6.9.8 ISL Lane Margining at the Receiver Extended Capability

All fields in the ISL Lane Margining at the Receiver for a Virtual PPB shall behave identically to PCIe except the following:

<span id="page-437-1"></span>**Table 7-106. ISL Lane Margining at the Receiver Extended Capability**

| Register                           | Register Fields | FM-owned DSP | vDSP                      | vUSP                      |
|------------------------------------|-----------------|--------------|---------------------------|---------------------------|
| Margining Port<br>Status Register  | All fields      | Supported    | Mirrors DSP               | Mirrors DSP               |
| Margining Lane<br>Control Register | All fields      | Supported    | Read/Write with no effect | Read/Write with no effect |

##### 7.7.6.9.9 ISL ACS Extended Capability

ACS applies only to a Downstream Port which, for a PBR link, applies to either a DSP above a GFD, a DSP connected to a crosslink, or a vDSP in a VH. All fields in the ISL ACS at the Receiver for a Virtual PPB shall behave identically to PCIe.

##### 7.7.6.9.10 ISL Advanced Error Reporting Extended Capability

AER can apply to a vPPB on any side of a link. FM-owned DSPs, vDSPs, and vUSPs support all AER fields.

##### 7.7.6.9.11 ISL DPC Extended Capability

DPC for both vDSP and vUSP is supported for all fields. The FM-owned DSP above an ISL must have DPC. DPC on the DSP above an ISL shall always be enabled by FM. DPC support is required to provide sufficient delay so that the various software entities — switch firmware, host software, fabric manager — are able to complete DPC event processing at their own pace.

### <span id="page-438-0"></span>7.7.7 Inter-Switch Links (ISLs)

<span id="page-438-3"></span>Inter-Switch Links (ISLs) carry PBR-format flits and must support all message classes and associated sub-channels, including one UIO VC. It is also additionally required that these message classes come up enabled automatically at power on, including the default UIO VC (VC3).

<span id="page-438-2"></span>**Figure 7-47. ISL Message Class Sub-channels**

![](_page_438_Figure_5.jpeg)

#### <span id="page-438-1"></span>7.7.7.1 .io Deadlock Avoidance on ISLs/PBR Fabric

ISLs and PBR switches carry CXL.io Upstream traffic and CXL.io Downstream traffic from different hosts in the same physical direction/queues. To avoid deadlocks, these two traffic types need to be kept independent on ISLs and internally through PBR switches. To assist in maintaining the required independence, each TLP inside the PBR fabric is tagged with a DSAR (Downstream Acceptance Rules) bit. Here are the rules for setting the value of the DSAR bit within the PTH:

- When an Edge DSP converts a received TLP from HBR to PBR format, the Edge DSP shall clear the DSAR bit
- When an Edge USP converts a received TLP from HBR to PBR format, the Edge USP shall set the DSAR bit
- When a Host ES vDSP forwards a TLP P2P, it shall set the DSAR bit
- When a GFD sends a TLP (which is always in PBR format), the GFD shall clear the DSAR bit
- When an Edge DSP above a GFD forwards a TLP to the GFD, the Edge DSP shall set the DSAR bit

For the remainder of this section, traffic with DSAR=0 is referred to as USAR (Upstream Acceptance Rules) traffic, and DSAR=1 traffic is referred to as DSAR (Downstream Acceptance Rules) traffic. On an ISL, this bit is carried in the PTH. Traffic within each VC is required to follow the ordering rules specified in [Table 7-107](#page-439-0) and [Table 7-108](#page-439-1).

<span id="page-439-0"></span>Table 7-107. PBR Fabric .io Ordering Table, Non-UIO

|                  |                           |                               |                             |                               | DSAR       |                   | USAR                        |                               |            |         |
|------------------|---------------------------|-------------------------------|-----------------------------|-------------------------------|------------|-------------------|-----------------------------|-------------------------------|------------|---------|
| Row Pass Column? |                           |                               |                             | Posted<br>uest                |            | Posted<br>Request | Non-Posted<br>Request       |                               |            |         |
|                  |                           | Posted<br>Request             | Read<br>Request             | NP<br>Request<br>with<br>Data | Completion |                   | Read<br>Request             | NP<br>Request<br>with<br>Data | Completion |         |
|                  | Posted Re                 | quest                         |                             |                               |            |                   |                             | Yes Yes Yes Yes               |            | Yes     |
| Read<br>Request  |                           |                               |                             |                               |            |                   | Yes/No                      | Yes                           | Yes        | Yes/No  |
| DSAR Po          | Non-<br>Posted<br>Request | NP<br>Request<br>with<br>data | Per PCIe Base Specification |                               |            |                   | Yes/No                      | Yes                           | Yes        | Yes/No  |
|                  | Completion                |                               |                             |                               |            |                   | Yes                         | Yes                           | Yes        | Yes     |
|                  | Posted Re                 | quest                         | Yes/No                      | Yes                           | Yes        | Yes/No            |                             |                               |            |         |
|                  | Non-                      | Read<br>Request               | Yes/No                      | Yes/No                        | Yes/No     | Yes/No            |                             |                               |            |         |
| USAR Poste       | Posted<br>Request         | NP<br>Request<br>with<br>data | Yes/No                      | Yes/No                        | Yes/No     | Yes/No            | Per PCIe Base Specification |                               |            | ication |
|                  | Completio                 | n                             | Yes/No                      | Yes                           | Yes        | Yes/No            | 7                           |                               |            |         |

<span id="page-439-1"></span>Table 7-108. PBR Fabric .io Ordering Table, UIO

| Row Pass Column? |                   |                                     | DSAR            |                  | USAR                        |                   |          |
|------------------|-------------------|-------------------------------------|-----------------|------------------|-----------------------------|-------------------|----------|
|                  |                   | UIO PR-FC UIO NPR-FC UIO Completion |                 | UIO PR-FC<br>TLP | UIO NPR-FC<br>TLP           | UIO<br>Completion |          |
|                  | UIO PR-FC<br>TLP  |                                     |                 |                  | Yes                         | Yes               | Yes/No   |
| DSAR             | UIO NPR-FC<br>TLP | Per I                               | PCIe Base Speci | fication         | Yes                         | Yes               | Yes/No   |
|                  | UIO<br>Completion |                                     |                 |                  | Yes                         | Yes               | Yes      |
|                  | UIO PR-FC<br>TLP  | Yes/No                              | Yes/No          | Yes/No           |                             |                   |          |
| USAR             | UIO NPR-FC<br>TLP | Yes/No                              | Yes/No          | Yes/No           | Per PCIe Base Specification |                   | fication |
|                  | UIO<br>Completion | Yes                                 | Yes             | Yes/No           |                             |                   |          |

To support the additional ordering requirements stated above, the following rules apply on ISL (also pictorially depicted in Figure 7-48):

<span id="page-440-0"></span>**Figure 7-48. Deadlock Avoidance Mechanism on ISL**

![](_page_440_Figure_3.jpeg)

- PBR Fabric .io ordering rules apply independently within each VC implemented
- On edge HBR/PCIe links and on edge PBR links, PBR Fabric ordering rules do not apply
  - On edge PBR links, PTH bit can be ignored for ordering purposes and only the regular CXL.io ordering rules from PCIe Base Specification apply.
- Nonzero dedicated credits are always required on ISL for each VC, regardless of whether multiple VCs are enabled
- Baseline Shared and Merged FC initialization and usage rules, as described in PCIe Base Specification, apply on ISLs as well, with some new rules/exceptions as noted below:
  - Dedicated buffers are required separately per FC class for DSAR and USAR traffic and they are both the same value as negotiated during FC initialization.
    - As an example, if one Posted HDR and one Posted DATA credit were exchanged for Dedicated buffers during InitFC1/2, the transmitter assumes there is 1 Posted data credit for DSAR traffic and one Posted data credit for USAR traffic and similarly for Posted HDR Credit as well.
    - Shared buffers can be shared between DSAR and USAR traffic.
- Update-FC DLLP is modified as shown in [Figure 7-49,](#page-441-2) to indicate release of DSAR or USAR buffers. Transmitters can use this information on shared credits to implement QoS limiting between DSAR and USAR traffic.
  - This modification is implicitly enabled on ISLs and requires no negotiation

*Note:* To aid debug, Switches are recommended to capture the Hdr and data\_Scale values negotiated at initialization so that debug software can access the values.

> • Optimized\_Update\_FC DLLP applies to USAR traffic only and it is implicit on ISLs. All DSAR traffic's shared buffer credit return occurs only via Update-FC DLLP.

<span id="page-441-2"></span>**Figure 7-49. Update-FC DLLP Format on ISL**

![](_page_441_Figure_6.jpeg)

### <span id="page-441-0"></span>7.7.8 PBR TLP Header (PTH) Rules

<span id="page-441-3"></span>For the purposes of this discussion, a "PBR link" is a link that negotiated to PBR flit format via the physical layer TS "PBR Flit bit" (see [Section 6.4](#page-305-5)). See [Section 3.1.8](#page-92-5) for details of PTH format.

- A PTH is inserted (via an appropriate decode mechanism) on CXL.io TLPs by an Edge Switch or the PTH is directly generated by devices (e.g., GFD) that natively support PBR link
- A PTH is forwarded as-is (unless explicitly noted otherwise as in handling PTH.DSAR bit on an edge PBR link) on a CXL.io TLP if the egress port is connected to a PBR link
- A PTH is removed when its CXL.io TLP exits to an edge non-PBR link
  - Note that some contents of PTH could be transferred to VendPrefixL0 if the egress port is an HBR link and the VendPrefixL0 is supported and enabled on the link. See [Section 7.7.3](#page-405-0) and [Section 7.7.4](#page-411-0).
- A PTH is included in link-IDE Integrity protection, if supported and enabled, when the PTH traverses PBR links.
<span id="page-441-4"></span>- • PTH is not included in .io selective IDE protection.

### <span id="page-441-1"></span>7.7.9 PBR Support for UIO Direct P2P to HDM

PBR switches support special routing mechanisms to enable the UIO Direct P2P to HDM use case with edge-to-edge routing, which often can be much more efficient compared to the hierarchical routing used in HBR switches. For backward compatibility, legacy software unaware of these special PBR routing mechanisms can continue to use HDM decoders, providing limited UIO Direct P2P capability.

An enhanced version of the FAST decoder as defined in [Section 7.7.2.4](#page-397-0) can be implemented in the Edge DSP above the UIO requester, providing edge-to-edge routing for UIO requests that target GFDs.

Another instance of the FAST decoder hardware can provide edge-to-edge routing for UIO requests that target LD-FAM devices. This instance is referred to as an LD-FAM Segment Table (LDST), and it is usually configured with a different segment size and amount of mapped HDM space from any FAST decoders in use.

With LD-FAM devices, UIO completions can be routed edge-to-edge with an ID-Based Re-Router mechanism, which can be implemented in the Edge DSP above each LD-FAM device. The Re-Router matches against the requester's PCI segment number (if applicable) and bus number in the UIO completion to determine the DPID for edge-toedge routing. G-FAM devices automatically use edge-to-edge routing for UIO completions without this mechanism.

FAST decoders, LDST decoders, and ID-Based Re-Routers are each configured by host software using CCI command sets, as documented in [Section 7.7.14](#page-482-0) for FAST decoders, and [7.7.13](#page-460-1) for LDST decoders & ID-based Re-Routers.

GFDs are not associated with any VH, thus they have no PCIe ID (segment, bus, device, function number) assigned by any host. When a GFD sends a UIO completion, the completer segment field (if present) and the completer ID field in the completion are reserved and shall be 0.

#### <span id="page-442-0"></span>7.7.9.1 FAST Decoder Use for UIO Direct P2P to G-FAM

FAST decoder instances in Edge USPs and DSPs have several similarities:

- Both convert requests from HBR format to PBR format, and route edge-to-edge to target GFDs.
- For the SPID, each uses the PID associated with its port.
- Both support CXL.mem and (CXL.io) UIO requests.
- A USP FAST decoder receives HBR format downstream requests coming from the RP. CXL.mem requests result from host accesses to GFDs.
- A DSP FAST decoder receives HBR format upstream requests coming from the requester device. UIO requests result from UIO Direct P2P traffic, where the UIO requester may be directly connected to an Edge DSP, or it may be connected via one or more HBR switches below the Edge DSP. CXL.mem requests result from the Direct P2P CXL.mem for accelerators use case, covered in [Section 7.7.10.](#page-444-1)

A DSP FAST decoder can be configured with a segment size different from the host's USP FAST decoder(s), but it is recommended for all FAST decoders to use the same segment size to avoid software complexity.

A DSP FAST decoder may need to be configured with a different number of segments from the host's USP FAST decoder(s) (e.g., a requester device may not need access to the entire Fabric Address space mapped by the USP FAST decoder). On the other hand, a requester device may need to access the Fabric Address space associated with an entire host Domain, not just a single RP within a host domain.

#### <span id="page-442-1"></span>7.7.9.2 LDST Decoder Use for UIO Direct P2P to LD-FAM

LDST decoder instances in Edge USPs and DSPs have several similarities:

- Both convert requests from HBR format to PBR format, and route edge-to-edge to target LD-FAM devices.
- For the SPID, each uses the PID associated with its port.
- Both support CXL.mem and (CXL.io) UIO requests.
- A USP LDST decoder receives HBR format downstream requests coming from the RP. CXL.mem requests result from host accesses to LD-FAM devices. UIO requests currently have no architected use cases, but they are not prohibited.
- Host software determines whether host accesses to LD-FAM devices use LDST decoders versus HDM Decoders in Edge USPs. For backward compatibility, legacy software that's unaware of LDST decoders can continue to use HDM decoders. For overcoming scaling limitations with the number of HDM decoders supported by

Edge USPs, LDST-aware software can use LDST decoders, though LDST decoders do not support HDM-D.

• A DSP LDST decoder receives HBR format upstream requests coming from the requester device. UIO requests result from UIO Direct P2P traffic. CXL.mem requests result from the Direct P2P CXL.mem for accelerators use case, covered in [Section 7.7.10.](#page-444-1)

A DSP LDST decoder can be configured with a segment size different from the host's USP LDST decoder(s), but it is recommended for all LDST decoders to use the same segment size to avoid software complexity.

A DSP LDST decoder may need to be configured with a different number of segments from the host's USP LDST decoder(s) (e.g., a requester device may not need access to the entire LD-FAM HDM space mapped by the USP LDST decoder). On the other hand, an accelerator may need to access the LD-FAM HDM space associated with the entire host Domain, not a single RP in the host Domain.

When any LDST decoders are in use, host SW needs to configure any HDM decoders mapping the same LD-FAM HDM ranges with decoder characteristics compatible with LDST decoders. This applies to HDM decoders present in the host, PBR switches, HBR switches, or LD-FAM devices. These decoder characteristics include:

- Minimum decoder granularity: 64 GB for LDST
- Interleave Ways (IW): neither HBR nor PBR switches have the special logic required to support 3/6/12, but LDST supports the other architected IW values.

Note that Dynamic Capacity (DC) Block Sizes are not visible to either type of decoder.

LDST decoders insert a requester segment field in UIO requests when necessary. This is described in [Section 7.7.9.3.](#page-443-0)

#### <span id="page-443-0"></span>7.7.9.3 ID-Based Re-Router for UIO Completions with LD-FAM

For UIO Direct P2P to LD-FAM devices, UIO completions by default are routed using hierarchical PCIe ID-based routing, and the ID may include a PCIe segment number in addition to bus, device, and function numbers. If present in the Edge DSP above an LD-FAM device, the ID-Based Re-Router does a CAM match using the PCIe ID, returning the DPID needed for edge-to-edge routing. This mechanism efficiently handles intra-VH cases, and it is especially efficient for cross-VH cases by avoiding P2P through the Root Complex.

PCIe segment numbers in TLPs is a feature added in PCIe Base Specification 6.0, and PCIe segments should not be confused with "segments" in the context of FAST/LDST decoders. LDST decoders support the PCIe convention that requesters generally don't include PCIe segment numbers in requests1 but rely instead on routing mechanisms to add PCIe segment number fields when needed for cross-segment routing. Host software configures LDST decoders to add2 the requester segment field in the request when it targets a different PCIe segment. When the LD-FAM device responds to the UIO request with a UIO completion, it automatically includes segment fields when necessary in the Destination ID and Completer ID. Host software shall configure the ID-Based Re-Router with the PCIe segment number in entries that need it.

<sup>1.</sup> With Selective IDE non-configuration requests, the requester is required to include the requester segment field in the request because a routing element inserting the field would cause an integrity violation with Selective IDE.

<sup>2.</sup> Although PCIe Base Specification forbids PCIe switches from inserting a Requester Segment field, the CXL UIO Direct P2P to HDM mechanisms in CXL switches are beyond the scope of PCIe Base Specification and do not violate the underlying architecture principles.

#### <span id="page-444-0"></span>7.7.9.4 LDST and ID-Based Re-Router Access Protection

LDST and ID-Based Re-Router use is protected by the LDST Access Vector (LAV) to ensure that only valid PIDs are programmed by the host into the LDST and ID-Based Re-Router structures. The LAV is a 4k-bit vector with a similar functionality as the GMVs and VTVs.

The FM is responsible for enabling access to PIDs in the LAV before the host can program those PIDs into the LDST or ID-Based Re-Router structures. For cross-VH use cases, the FM is also responsible for using the Domain Validation SV mechanism, when available, to confirm that every VH that is enabled for cross-VH access belongs to the same host domain.

### <span id="page-444-1"></span>7.7.10 PBR Support for Direct P2P CXL.mem for Accelerators

<span id="page-444-2"></span>Direct P2P CXL.mem provides the ability for an accelerator to access peer Type 3 memory devices using CXL.mem. PBR switches require special routing mechanisms to support this, specifically the FAST and LDST decoders. For Direct P2P CXL.mem, these decoders function essentially the same as they do for supporting the UIO Direct P2P to HDM use case, with the following exceptions:

- They intercept and forward upstream CXL.mem requests instead of UIO requests
- They target only Type 3 (HDM) devices, not Type 2 devices
- The accelerator (requester device) and Type 3 device must each be directly connected to an Edge DSP
- With an MLD (Type 3 device), each accelerator must be assigned a dedicated LD distinct from the host's LD

Note that both types of decoders support .mem requests when they are implemented in Edge USPs, so .mem support is not unique to the Direct P2P CXL.mem use case.

Same as with the UIO Direct P2P use case, a FAST decoder can be implemented in the Edge DSP above an accelerator, providing edge-to-edge routing for .mem requests that target G-FAM devices (GFDs). The same FAST decoder instance can support either the UIO Direct P2P or Direct P2P CXL.mem use case.

Similarly, an LDST decoder can be implemented in the Edge DSP above an accelerator, providing edge-to-edge routing for .mem requests that target LD-FAM devices. The same LDST decoder instance can support either the UIO Direct P2P or Direct P2P CXL.mem use case.

Type 3 devices used with Direct P2P CXL.mem can be mapped under either HDM-H or HDM-DB coherency ranges. If mapped under HDM-DB, peer devices other than the associated accelerator can access the HDM-DB memory using UIO Direct P2P to HDM, in which case the associated accelerator serves the role of the host participating in BI protocol (i.e., the HDM-DB device directs BISnps to the accelerator).

Direct P2P CXL.mem traffic going to or from an MLD (directly connected to an Edge DSP) works essentially the same as with host .mem traffic, as documented in [Section 7.7.6.6.3](#page-424-2) and [Section 7.7.6.8](#page-428-0).

CXL.mem responses for the Direct P2P CXL.mem use case require no special routing mechanism. For S2M responses from G-FAM, the GFD's RPID context for the accelerator contains the DPID needed for edge-to-edge routing back to the accelerator. For S2M responses from LD-FAM, the vPPB in the Edge DSP above the Type 3 device contains the DPID needed for edge-to-edge routing back to the accelerator.

Same as with the UIO Direct P2P use case, FAST decoders and LDST decoders are each configured by host software using CCI command sets, as documented in [Section 7.7.15](#page-493-1) for FAST decoders and [Section 7.7.13](#page-460-1) for LDST decoders.

#### <span id="page-445-0"></span>7.7.10.1 Message Routing for Direct P2P CXL.mem Accesses with GFD

Direct P2P CXL.mem messages are routed using standard PBR mechanisms. [Figure 7-50](#page-445-2) illustrates an example PBR Fabric with a Direct P2P CXL.mem enabled Type 2 accelerator and two peer GFDs accessible to it. The dashed lines indicate the paths taken by the Direct P2P CXL.mem messages. Upstream .mem requests from the accelerator are routed edge-to-edge to the appropriate GFD by the FAST decoder in vPPB 6. Upstream .mem responses from either GFD are routed edge-to-edge back to the accelerator by standard PBR routing.

For an HDM-DB GFD sending a BISnp, the GFD's RPID context for the accelerator contains the DPID that is needed for edge-to-edge routing to the accelerator.

<span id="page-445-2"></span>**Figure 7-50. Example Topology with Direct P2P CXL.mem with GFD**

![](_page_445_Figure_7.jpeg)

#### <span id="page-445-1"></span>7.7.10.2 Message Routing for Direct P2P CXL.mem Accesses with MLD

Direct P2P CXL.mem accesses to an MLD require a distinct LD and associated peer requester LD-ID on the link between the MLD and the Edge DSP to which it is attached. This is accomplished by assigning a vPPB in the DSP in the same Domain as the host that owns the requester. The host and any peer accelerators will each have their own vPPB bound to them, which utilize their individual LD-IDs.

[Figure 7-51](#page-446-0) illustrates an example PBR Fabric with a Direct P2P CXL.mem enabled Type 2 accelerator and two peer MLDs accessible to it. Other than the dashed line to Host 1, the dashed lines indicate the paths taken by the Direct P2P CXL.mem messages. Upstream CXL.mem requests from the accelerator are routed edge-to-edge to the appropriate MLD by the LDST decoder in vPPB 6. Upstream CXL.mem responses from either MLD are routed edge-to-edge back to the accelerator by standard PBR routing using the accelerator's PID, which in each case is retrieved from the accelerator's vPPB in the DSP above the MLD.

<span id="page-446-0"></span>**Figure 7-51. Example Topology with Direct P2P CXL.mem with MLD**

![](_page_446_Figure_4.jpeg)

In this example, the path taken by CXL.mem messages between the host and one MLD is also shown. Downstream CXL.mem requests from the host are routed edge-to-edge to the appropriate MLD by the LDST decoder in vPPB 1. Upstream CXL.mem responses from the MLD are routed edge-to-edge back to the host by standard PBR routing using the host's PID contained in vPPB B.

For an HDM-DB LD-FAM device sending a BISnp, the Edge DSP above the LD-FAM device contains the DPID that is needed for edge-to-edge routing to the accelerator.

#### 7.7.10.3 PBR Switch Port Processing of Direct P2P CXL.mem Messages

109 summarizes how PBR switches perform port processing of CXL.mem messages with the Direct P2P CXL.mem for Accelerators use case. This traffic never flows through Edge USPs or HBR switches. The accelerator (requester) is always an SLD directly connected to an Edge DSP, and each Type 3 memory device is always directly connected to an Edge DSP. All messages in PBR format are routed edge-to-edge.

For sonciseness, there are several abbreviations within the table. Beyond "accel" standing for accelerator, see Section 7.7.6.8 for other abbreviations.

<span id="page-447-2"></span>Table 7-109. PBR Switch Port Processing Table for Direct P2P CXL.mem

| Myssage Claus<br>ant. The Joh      |                | Edge USP        | Host ES FPort<br>or<br>DS ES FPort | Edge DSP in Either Host ES or Downstream ES |                                                                |                                                                                                                      |                                 |  |
|------------------------------------|----------------|-----------------|------------------------------------|---------------------------------------------|----------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------|---------------------------------|--|
|                                    |                | Always below RP |                                    | Above HBR<br>Switch USP                     | Above SLD                                                      | Above MLD                                                                                                            | Above GFD                       |  |
| M2S Req/RwD<br>Direct P2P          |                | N/A             | PBR routing                        | N/A                                         | Convert to PBR fmt using FAST or LDST                          | N/A                                                                                                                  | N/A                             |  |
| CXL.mem                            | DS to Type 3   | N/A             |                                    |                                             | Convert to HBR fmt<br>LD-ID←0; is unused                       | LD-ID←CAM <sub>16</sub> (SPID)<br>Convert to HBR MLD fmt                                                             | LD-ID is N/A<br>Keep in PBR fmt |  |
| S2M NDR/DRS<br>Direct P2P          |                | N/A             | PBR routing                        | N/A                                         | LD-ID is unused<br>Convert to PBR fmt<br>DPID + vPPB.root.PID  | LD-ID identifies vPPB<br>Convert to PBR fmt<br>DPID \( \subseteq vPPB.root.PID \)                                    | Keep in PBR fmt<br>LD-ID is N/A |  |
|                                    |                |                 |                                    |                                             | Convert to HBR fmt<br>LD-ID←0; is unused                       | N/A                                                                                                                  | N/A                             |  |
| S2M BISnp<br>Direct P2P<br>CXL.mem | US from Type 3 | N/A             | PBR routing                        | N/A                                         | Convert to PBR fmt<br>DPID←vPPB.root.PID<br>SPID←vPPB.self.PID | BI-ID[3:0] contains LD-ID<br>LD-ID identifies vPPB<br>Convert to PBR fmt<br>DPID←vPPB.root.PID<br>SPID←vPPB.self.PID | Keep in PBR fmt                 |  |
| -                                  | DS to accel    |                 |                                    |                                             | Convert to HBR fmt<br>BI-ID[11:0]←SPID                         | N/A                                                                                                                  | N/A                             |  |
| M2S BIRsp<br>Direct P2P<br>CXL.mem | US from accel  |                 | PBR routing                        | N/A                                         | Convert to PBR fmt<br>DPID←BI-ID[11:0]<br>SPID←vPPB.self.PID   | N/A                                                                                                                  | N/A                             |  |
|                                    | DS to Type 3   | N/A             |                                    |                                             | Convert to HBR fmt<br>BI-ID←0; is unused                       | Convert to HBR fmt<br>LD-ID←CAM <sub>16</sub> (SPID)<br>BI-ID[3:0]←vPPB.LD-ID                                        | Keep in PBR fmt                 |  |

<span id="page-447-1"></span><span id="page-447-0"></span>![](_page_447_Picture_6.jpeg)

### <span id="page-448-0"></span>7.7.11 PBR Link Events and Messages

<span id="page-448-2"></span>A PBR link can carry traffic from many different VH at the same time. Some events may occur that only affect a single VH, while other events need to apply to all VH sharing the link.

Basic PBR link requirements are discussed in [Section 7.7.11.1](#page-448-1).

A summary of all the CXL Vendor Defined Messages (VDMs) that are PTH routed to the destination is provided in [Section 7.7.11.2.](#page-449-0)

PCIe events for a single VH are discussed in [Section 7.7.11.3](#page-449-1).

PCIe events for multiple VH sharing a link are discussed in [Section 7.7.11.4.](#page-453-0)

Events that occur outside PCIe are discussed in [Section 7.7.11.5.](#page-454-0)

Messaging to and from a host to a GFD is discussed in [Section 3.1.11.1.](#page-98-2)

#### <span id="page-448-1"></span>7.7.11.1 PBR Link Fundamentals

CXL defines two types of PBR links:

- Inter-Switch Link (ISL)
- GFD link

All PBR links must support PBR Flit mode. Because PBR Flit mode relies on PCIe Flit mode, all host-OS-visible DSPs should report PCIe Flit mode as enabled. The DSPs include both a Host Edge Switch vDSP and a DSP above a PBR link that leads to a GFD.

The owner of a PBR link is an FM-managed DSP. Switch firmware may assist the FM in managing the DSP. An ISL is a downstream-to-downstream crosslink and thus has an FM-managed DSP on each side of the link. A GFD link has only one DSP and thus has only one FM-managed DSP. The speed and width of a PBR link is solely controlled by the FM-managed DSP(s) on the link and not by any vDSPs that share the link.

Each side of an ISL is managed separately. Each DSP above an ISL must support DPC, to allow firmware on each side of the link an independent amount of time to process fabric port events. DPC shall be enabled for all cases on ISL except when the ISL is the only path to the FM, in which case the DSP furthest from the FM shall not have DPC enabled.

FM-initiated CXL.io traffic sent across a PBR link shall be limited to DMTF-format VDMs. The PTH.DPID is used to indicate whether the PBR Link Partner should sink the TLP or forward the TLP. If the PTH.DPID = FFFh, the PBR Link Partner must sink the VDM because that is how the initial device discovery occurs and how PIDs are assigned. If the PTH.DPID = the device's PID, then the device must also sink the VDM because that is how the device is accessed by the FM.

**Figure 7-52.**

All VH users of a PBR link have their functionality ride on top of the FM-managed link. For example, a VH's DSP cannot see a Link Up if the fabric link is not up. A VH cannot change the width or speed of its shared link, rather it will inherit the setting of the FMmanaged DSP.

To manage different software response times to events, every vDSP for every VH must support DPC. DPC allows a host to keep its Link Down from its (VH) perspective until it is ready to re-enable it, having cleaned up all the side effects of a Link Down. A Host may or may not choose to enable DPC.

L0p is optional on a PBR link. The FM-managed DSP initiates any L0p transitions via a mechanism that is beyond this specification.

Every CXL.io TLP on a PBR link will carry a 4B PTH. The VDMs described in this section follow the same rule. See [Section 3.1.8.](#page-92-5) There are three fields of note in the PTH that are required for the VDMs described in this section:

- SPID: Source PID
  - From a vDSP: Use vDSP's USP PID
  - From a vUSP: Use vUSP's FPort PID
  - From a switch: Use switch's PID
  - From a downstream edge: Use DSP's PID
  - From a host edge: Use USP's PID
- DPID: Destination PID
  - To a vDSP: Use vDSP's USP PID
  - To a vUSP: Use vUSP's FPort PID
  - To a switch: Use switch's PID
  - To a downstream edge: Use DSP's PID
  - To host edge: Use USP's PID
- DSAR flag

#### <span id="page-449-0"></span>7.7.11.2 CXL VDMs

See [Section 3.1.11](#page-96-3) for a list of VDMs that are used in the PBR fabric.

#### <span id="page-449-1"></span>7.7.11.3 Single VH Events

Events that are contained within a single VH should not affect other VHs that share an ISL.

PCIe visible events that are contained within a single VH include:

- Assert Reset
- Deassert Reset
- Link Up

[Figure 7-52](#page-450-0) shows the virtual hierarchy from a Host 1 perspective (other hierarchies are grayed out). In Switch A, Host 1 finds only a single switch VCS 0. However, in Switch B, two switches VCS 1 and VCS 4 are in the Host 1 hierarchy. Switch B VCS 1 has vUSP 0 connected below Switch A VCS 0 vDSP 2, and Switch B VCS 4 has vUSP 0 below Switch A VCS 0 vDSP 3. Switch C has a GFD with that is accessible by Host 1 devices, but the GFD is not visible to the Host 1 PCIe hierarchy. See [Section 7.7.14](#page-482-0) for more details on control of the GFD.

<span id="page-450-0"></span>Figure 7-52. Single VH

![](_page_450_Figure_3.jpeg)

##### 7.7.11.3.1 Assert Reset VDM

Every PCIe hierarchy supports three levels of Conventional Reset:

- Fundamental cold reset (PERST#): Input pin
- Fundamental warm reset (PERST#): Input pin
- Hot reset due to Link Down, in-band hot reset, USP secondary bus reset, DSP secondary bus reset, or link disabled

CXL Fabric links support propagation of these resets. The ISL link state is not affected by any VH's Assert Reset or Assert PERST# VDM. Assertion of reset is accomplished using one of two different VDM opcodes:

- Assert PERST#: Used for fundamental reset assertion for that VH, Opcode 0
- · Assert Reset: Used for hot reset assertion for that VH, Opcode 1

The separate PERST# message allows for fundamental reset functionality without the need for extra pins between switches.

Assert PERST# should be triggered whenever a VH has its input fundamental reset asserted on a Host ES. Assert Reset should be triggered whenever the Host ES:

- · Receives a hot reset input
- · Has a secondary bus reset on its USP
- · Has a secondary bus reset on its VDSP
- · Has a link disable on its vDSP

The Assert Reset VDMs all are sent from a vDSP to its paired vUSP. The VDM sent will have a PTH with:

- SPID = vDSP's host PID
- DPID = vUSP's FPort PID
- DSAR flag = 1

VDM header fields for Assert Reset VDMs:

- CXL VDM code of 80h
- PBR Opcode 0 or 1 indicates which Assert PERST# or Assert Reset message

It is expected that the Assert Reset VDM will reach a vUSP uniquely identified by the SPID and DPID at the destination switch.

A vDSP, upon sending Assert Reset VDM, will have its link state transition to Hot Reset.

A vUSP, upon receiving an Assert Reset VDM, will have its link state transition to Hot Reset. While in Hot Reset, all Port non-sticky registers and state machines that belong to the VH must return to their initialized state.

A vUSP, upon receiving an Assert PERST# VDM, shall have its link state transition to Hot Reset and also shall clear any sticky bits as outlined by PCIe Base Specification for PERST# behavior.

It is possible to send any number of Assert Reset VDMs or Assert PERST# VDMs.

In [Figure 7-53](#page-453-1), if Host 1 asserts its PERST#, then both Switch A VCS 0 vDSP 2 and Switch A VCS 0 vDSP 3 shall issue an AssertPERST# VDM. The format of the PTH would be (SPID=A01, DPID=B01) for vDSP 2 and (SPID=A11, DPID=B02) for vDSP 3. If Host 1 instead asserted vDSP 2 secondary bus reset, then only vDSP 2 would send an AssertReset VDM with (SPID=A01, DPID=B01).

##### 7.7.11.3.2 Deassert Reset VDM

A Deassert Reset VDM signals a release of reset and an exiting of the Hot Reset state to enter Detect for that VH. This VDM shall be sent from the Host Edge Switch due to a deassertion of the PERST# input resulting from an exit from Hot Reset.

If DSP is enabled the DPC trigger status must be cleared before a Deassert Reset VDM can be sent because DPC triggered prevents any TLPs from egressing that port.

Propagation of reset deassertion over an ISL is enabled via a Deassert Reset VDM, which is used for hot reset deassertion for that VH, Opcode 3.

A Deassert Reset VDM is used to instruct the vUSP to exit Hot Reset and enter Detect. The Deassert Reset VDM sent will have a PTH with:

- SPID = vDSP's host PID
- DPID = vUSP's FPort PID
- DSAR flag = 1

VDM header fields for Deassert Reset VDMs:

- CXL VDM code of 80h
- PBR Opcode 3

**Figure 7-53.**

A vDSP, upon sending a Deassert Reset VDM, will have its link state transition from Hot Reset to Detect. A vUSP, upon receiving a Deassert Reset VDM, will have its link state transition from Hot Reset to Detect. If the link state is not in Hot Reset, a link state change will not occur.

The link for that VH will remain in Detect until the vUSP sends a Link Up VDM and the vDSP receives a Link Up VDM. If a Link Up VDM is not received within 10 ms, a subsequent Deassert Reset VDM shall be sent. This can repeat until 10 Deassert Reset VDMs have been sent. After a tenth Deassert Reset VDM is sent, if a Link Up VDM is still not received within 10 ms, the reset deassertion failed and the FM shall be notified.

In [Figure 7-53,](#page-453-1) if Host 1 clears the secondary bus reset in Switch A VCS 0 vDSP 2, then Switch A VCS 0 vDSP 2 would send a Deassert Reset VDM with (SPID=A01, DPID=B01). Switch B VCS 1 vUSP 0 would exit the hot reset state. As part of the exit from LTSSM Detect and due to the shared link nature of an ISL, Switch B VCS 1 vUSP 0 will bypass the PCIe LTSSM states of Polling and Configuration and transition the vDSPto-vUSP link back to L0 (Link Up) by sending a Response Link Up VDM.

##### 7.7.11.3.3 Link Up VDM

A Link Up VDM signals a transition to L0 active for that VH's link. The Link Up VDM is sent by a vUSP to its paired vDSP to convey a post-Detect state across the shared ISL.

The vUSP sends a Link Up VDM after receiving a Deassert Reset VDM. The vUSP can perform any required post-reset initialization before sending the Link Up VDM. The vUSP may take as long as it needs after Deassert Reset to send the Link Up VDM. Any number of Deassert Reset VDMs may be received by the vUSP; for each Deassert Reset VDM received, a Link Up VDM shall be sent.

The vUSP, after sending a Link Up VDM, shall have its link state transition to L0 from Detect. Polling and Configuration link states are bypassed by the Link Up VDM because the required TS1 and TS2 Ordered Sets cannot be sent over a shared ISL.

A vDSP, after receiving a Link Up VDM, shall have its link state transition to L0 from Detect. If not in Detect, there is no state change. Any number of Link Up VDMs may be received. Polling and Configuration link states are bypassed by the Link Up VDM, with the link directly transitioning from Detect to L0.

Neither a vDSP nor vUSP should ever have their link state reach Polling or Configuration state.

The VDM sent will have a PTH with:

- SPID = vUSP's FPort PID
- DPID = vDSP's host PID
- DSAR flag = 1

VDM header fields for LinkUp VDMs:

- CXL VDM code of 80h
- PBR Opcode 4

##### 7.7.11.3.4 Dynamic vDSP-to-vUSP Bind

See [Section 7.7.12.3](#page-458-0) for more details on the Configure PID Binding API sequence. After Configure PID Bind, the vDSP or vUSP shall be in a Hot Reset state. A vDSP may issue an Assert Reset VDM or a Deassert Reset VDM from the reset state, as dictated by its VH. A vUSP shall remain in Hot Reset until the vUSP receives a Deassert Reset VDM, upon which, after processing the necessary post-reset tasks, the vUSP will send a Link Up VDM.

#### <span id="page-453-0"></span>7.7.11.4 Shared Link Events

Events that affect multiple VHs on the same link need to be reported to the FM. The FM shall take any necessary action.

The FM is required to keep an inventory for each ISL. Figure 7-53 shows how the link from Switch A Port B (indicated by an oval with 1) is shared by both a Host 1 hierarchy and a Host 3 hierarchy. Events on this link will affect both hierarchies. The oval with 2 is another shared link used by multiple hierarchies, of which only a Host 1 hierarchy is colored in but the ISL also includes Host 3 (VCS 2) and two hierarchies of Host 2 (VCS 0 and VCS 3).

<span id="page-453-1"></span>Figure 7-53. Shared Link Events

![](_page_453_Figure_6.jpeg)

##### 7.7.11.4.1 Inter-Switch Link (ISL) Down

An ISL going down may affect one or more VHs.

A switch on each side of the ISL knows if the link had any issues. The fabric port's DPC is used to handle link issues. If DPC triggers, switch firmware will be notified. DPC may trigger due to Link Down or due to other reasons, such as software trigger; the net result is that the ISL will go down. Once the link goes down the switch reports the event to its primary FM. The FM is responsible for resolving the ISL Down event for all involved VHs.

The fabric port's DPC should remain triggered until switch firmware can resolve the side effects of an ISL Down event. When the FM has finished its resolution tasks, the FM will instruct the switch to clear the DPC trigger on the fabric port DSP. DPC trigger clear indicates resolution of the event and also allows the ISL to come back up.

The FM requires an inventory of users of an ISL to correctly resolve an ISL Down event. FM tasks for the resolution of an ISL Down event involves the following:

- Unbinding any affected VHs' vDSP
- Unbinding any affected VHs' vUSP
- Clearing any affected multi-path in a switch's RGT
- Clearing any affected GFD Access Vector in a switch's GAE

For example, if the link at Oval #1 in [Figure 7-53](#page-453-1) breaks, Switch A and an unlabeled PBR fabric switch will both notify their primary FM. The FM will then unbind the following affected vDSPs and vUSPs:

- Switch A VCS 0 vDSP 2 and VCS 2 vUSP 0
- Switch B VCS 1 vUSP 0
- Switch C VCS 0 vDSP 2

As another example, if the link at Oval #2 in [Figure 7-53](#page-453-1) breaks, Switch B and an unlabeled PBR fabric switch will both notify their primary FM. The FM will then unbind the following affected vDSPs and vUSPs:

- Switch A VCS 0 vDSP 2 and VCS 1 vDSP 3 and VCS 1 vDSP 2
- Switch B VCS 0 vUSP 0, VCS 1 vUSP 0, VCS 2 vUSP 0, and VCS 3 vUSP 0
- Switch C VCS 0 vDSP 2

In addition to the unbinding of the vDSP and vUSP pair affected by an ISL Down event, the RGT and GAE GFD access vectors may be updated by the FM. The RGT would be updated to avoid the path leading to the fault. The GFD Access Vector may be updated to remove a GFD that is no longer reachable.

#### <span id="page-454-0"></span>7.7.11.5 Switch Reported Events

Some events are switch specific or are outside normal PCIe reporting methods and thus require switch-specific intervention. These include:

• Link Partner Info

##### <span id="page-454-1"></span>7.7.11.5.1 Link Partner Info VDM

A Link Partner Info VDM is sent on all PBR links immediately after the InitFC process finishes for VC0. Each side of the link will send a Link Partner Info VDM at this time.

A Link Partner Info VDM also is sent whenever a payload field value is updated. Only the side of the link with an updated value needs to send the VDM.

This is a message with payload. For CXL 3.1, the payload is a fixed size of 16 DWORDs.

There are two types of PBR links: ISL and GFD. Both send the same Link Partner Info format but have a different value for the device type of the sender.

The Link Partner Info payload includes the following details about the sender of the VDM:

- 16B Link Partner ID: defined as the first 16 bytes of the Identify Output Payload as specified in [Table 8-50](#page-635-3), for the hardware sourcing the Link Partner Info VDM Payload. Thus, this 16B string is a globally unique ID associated only with the sourcing hardware.
- 1B Physical Port ID: the ID number (port number) of the port sourcing (transmitting) the Link Partner Info VDM payload.
- 12bit PID (if FFFh, indicates sending port's PID is un-initialized)
- 4bit Device Type (0 = PBR switch, 1 = GFD, all other encodings are reserved)

- 1B Standard FC VC list
- 1B UIO FC VC list
- 16B FM Primary UUID. If this value has not been initialized, this value shall read all zeros.
- 16B FM Secondary UUID. If this value has not been initialized, this value shall read all zeros.

<span id="page-455-0"></span>**Table 7-110. Link Partner Info Payload**

| +3                     |                                      | +2                        | +1                                   | +0                                   | Byte   |  |  |  |
|------------------------|--------------------------------------|---------------------------|--------------------------------------|--------------------------------------|--------|--|--|--|
| 7654       | 321076<br>5<br>4 | 3210          | 765432<br>1<br>0 | 765432<br>1<br>0 | Offset |  |  |  |
| DevType[3:0]           | PID[11:0]                            |                           | Reserved[7:0]                        | PortID[7:0]                          | +0     |  |  |  |
|                        |                                      |                           |                                      |                                      |        |  |  |  |
| Link Partner ID[127:0] |                                      |                           |                                      |                                      |        |  |  |  |
|                        |                                      |                           |                                      |                                      | +12    |  |  |  |
|                        |                                      |                           |                                      |                                      | +16    |  |  |  |
|                        | Primary FM UUID[15:0]                |                           | UIO FC VC List[7:0]                  | Standard FC VC List[7:0]             | +20    |  |  |  |
|                        |                                      |                           |                                      |                                      | +24    |  |  |  |
|                        |                                      | Primary FM UUID[111:16]   |                                      |                                      | +28    |  |  |  |
|                        |                                      |                           |                                      |                                      | +32    |  |  |  |
|                        | Secondary FM UUID[15:0]              |                           |                                      | Primary FM UUID[127:112]             | +36    |  |  |  |
|                        |                                      |                           |                                      |                                      | +40    |  |  |  |
|                        |                                      | Secondary FM UUID[111:16] |                                      |                                      | +44    |  |  |  |
|                        |                                      |                           |                                      |                                      | +48    |  |  |  |
|                        | Reserved                             |                           |                                      | Secondary FM UUID[127:112]           | +52    |  |  |  |
| Reserved               |                                      |                           |                                      |                                      |        |  |  |  |
|                        |                                      |                           |                                      |                                      | +60    |  |  |  |

With multibyte fields, the least significant byte of the field starts with the lowest byte offset, and subsequent bytes are strictly increasing in significance. I.e., this is little endian format within each multibyte field as well as the overall payload.

The Link Partner Info VDM.PTH fields are as listed below. This VDM will terminate at the Receiver.

- SPID = Originator's (switch's/GFD's) PID, A value of FFFh indicates the sender's PID is un-initialized.
- DPID = FFFh (fixed value which indicates the receiving port is to process the VDM payload)
- DSAR flag = 1

VDM header fields for LinkPartnerInfo VDMs:

- Type 74h (Message with Data, terminate at Receiver)
- CXL VDM code of 90h
- PBR Opcode 0

A single message is sufficient to carry all the link info for CXL release 3.1.

#### <span id="page-456-0"></span>7.7.11.6 PBR Link CCI Message Format and Transport Protocol

CCI commands are transported on PBR links as defined in [Section 7.6.3](#page-346-0) and its associated binding specifications (see DSP0234, DSP0238, and DSP0281) with some notable caveats and clarifications:

- As with all .io traffic across PBR links, MCTP PCIe VDMs include a PTH whose SPID and DPID define the routing of the message
- PCIe enumeration is not required for ISL PPBs and GFDs
- GFDs do not implement a PCIe Physical Function
- "Requester ID" and "Target ID" fields in the VDM's TLP header are reserved because IDs are not assigned to many elements within the fabric (e.g., FM, ISL PPBs, Switch Management FW, GFDs, etc.)

### <span id="page-456-1"></span>7.7.12 PBR Fabric Management

#### <span id="page-456-2"></span>7.7.12.1 Fabric Boot and Initialization

Much like as outlined for HBR switches in [Section 7.2.1,](#page-321-1) PBR switches may be initialized in one of three different ways:

- Statically
- FM boots before the host(s)
- FM and host boot simultaneously

##### <span id="page-456-3"></span>7.7.12.1.1 Static Fabric Initialization

A static fabric deployment uses statically predefined configuration data to define the fabric configuration settings typically assigned dynamically by an FM.

Static Fabric Characteristics:

- No support for G-FAM or MLD
- No support for dynamic binding changes or DCD
- No FM is required, but may be needed for error handling
- At switch boot, all ports have a PID assigned, DRT and RGT tables are prepopulated, and EP and PID binding settings are predefined as defined by vendorspecific switch configuration data (e.g., configuration file in SPI Flash)
- Each VH is ready for enumeration when the host boots
- Hot-add and managed hot-remove are supported on Downstream Edge Ports

##### 7.7.12.1.2 Fabric Manager Boots First

With this method, the FM configures the fabric binding relationships and access permissions before the host boots and enumerates its VH.

- FM boots while hosts are held in reset
- All attached ISLs and DSPs link up and, when negotiated in PBR mode, exchange the PBR Link Information VDM
- FM discovers fabric topology, claims ownership of all components under its management, and assign PIDs
- FM binds EPs to VCSs and configures GFDs
- FM configures GMV and VTV to enable G-FAM, GIM and Edge-to-edge P2P, as required when available

##### 7.7.12.1.3 Fabric Manager and Host Boot Simultaneously

In the case where the switches, FM, and host boot at the same time:

- VCSs, PID assignment, GFD configuration, and bindings between Host ES to Downstream ES VCSs are statically defined
- Edge vPPBs within each VCS are unbound and presented to the host as Link Down
- Switch discovers downstream devices and presents them to the FM
- Host enumerates the VH and configures the DVSEC registers
- FM performs port binding to edge vPPBs
- Switch performs virtual to physical binding
- Each bound port results in a Presence Detect Change or Link State Change notification to the host
- For G-FAM access, FM updates GMV and VTV access vectors for hosts

#### <span id="page-457-0"></span>7.7.12.2 PBR Fabric Discovery

To effectively manage a PBR fabric, the FM must understand the physical topology through a fabric discovery process. A typical fabric discovery may proceed as follows.

1. FM discovers the component to which it is directly connected and claims primary FM ownership.

Management of a PBR device requires that a primary FM is registered. A PBR device shall accept only the following commands from an FM that is not registered as the primary FM:

- **Identify**
- **Get Supported Logs**
- **Get Log**
- **Identify PBR Component**
- **Claim Ownership**

All other commands shall fail with "Unsupported Request". A PBR device shall only advertise support for the CEL and the CEL shall only advertise the commands in the above list when the supported logs or CEL contents are queried by an FM that is not registered as the primary FM.

If the FM is connected to a switch, crawl out and discovery of the fabric continues.

2. FM explores all switch ports.

As primary FM, the switch capabilities and switch port status can be queried. The **Get Physical Port State** and **Get PBR Link Partner Info** commands provide information on the devices connected to each port.

PBR switches can determine the type of device present at the far end of a link after negotiation using the link state information provided in [Table 7-111.](#page-457-1)

<span id="page-457-1"></span>**Table 7-111. Far End Device Type Detection (Sheet 1 of 2)**

| Device Type | Negotiated<br>Link Direction | Negotiated<br>PBR-Enabled | Negotiated<br>MLD-Enabled | Received<br>"Link Partner<br>Info" Type |
|-------------|------------------------------|---------------------------|---------------------------|-----------------------------------------|
| Host        | USP                          | N                         | N                         | N/A                                     |
| PBR Switch  | DSP-DSP Crosslink            | Y                         | N                         | Switch                                  |

| Device Type                    | Negotiated<br>Link Direction | Negotiated<br>PBR-Enabled | Negotiated<br>MLD-Enabled | Received<br>"Link Partner<br>Info" Type |
|--------------------------------|------------------------------|---------------------------|---------------------------|-----------------------------------------|
| GFD                            | DSP                          | Y                         | N                         | GFD                                     |
| MLD                            | DSP                          | N                         | Y                         | N/A                                     |
| SLD, PCIe EP, or<br>HBR Switch | DSP                          | N                         | N                         | N/A                                     |

3. FM may choose to first continue discovery of any connected switches or to manage devices on the far end of all switch ports.

PBR switch PPBs connected as ISLs are configured by the FM with the **Send PPB CXL.io Configuration Request** command.

The FM uses the **Fabric Crawl Out** command, as defined in [Section 7.7.13.2,](#page-461-0) using switch port number as the target to manage the devices on the far end of each switch port. The FM claims ownership and assigns a PID to each defined as covered in step 1.

Once the far end device has been assigned a PID, the FM must program the PBR switch's DRT to enable routing of that PID to the appropriate switch port. The FM can now use this new assigned PID as the target for subsequent **Fabric Crawl Out** requests.

Steps 1 – 3 are repeated for all PBR switches discovered.

#### <span id="page-458-0"></span>7.7.12.3 Assigning and Binding PIDs

As defined in [Section 7.7.6.5,](#page-421-0) there are many entities within a fabric that require PIDs to be assigned. GFDs and PBR switches are assigned a PID for device management purposes when the FM registers with these devices using the **Claim Ownership** command. A PBR switch reports all additional possible PID assignments with the **Get PID Target List** command.

The FM may start performing binding operations after all required PIDs have been assigned using the **Configure PID Assignment** commands. There are two methods for binding, depending on the location of the source and target of the operation. The **Bind vPPB** command is used to bind a direct attached device or LD to a switch's VCS.

The **Configure PID Binding** command is used to bind Downstream ES VCS vUSPs to Host ES vDSPs in a two-step operation. First, a binding command is sent to the Downstream ES, assigning the PID of the Host edge port to a Downstream ES VCS. Assignment of this PID allows the Downstream ES FPorts to select appropriate decoding and routing logic based on the SPID of incoming transactions. As detailed in [Section 7.7.12.4,](#page-458-1) latency and BW values are configured with this binding so that CDAT information can be generated in the Downstream ES.

A binding command is also sent to the Host ES, assigning the PID of the desired Downstream ES FPort and associating the binding with a specified vDSP. The Host ES uses this as the DPID for downstream transactions.

#### <span id="page-458-1"></span>7.7.12.4 Reporting Fabric Route Performance via CDAT

Hosts require CDAT information that defines the attributes and performance characteristics of regions of memory for all memory interconnect configurations, including PBR fabrics. Special mechanisms are defined for determining and reporting this information in a PBR fabric because hosts have no visibility of intermediate ISLs, as outlined in [Section 7.7.6.1.](#page-415-1) The mechanisms used for LD-FAM differ from those used for G-FAM.

##### 7.7.12.4.1 Accessing CDAT Information for LD-FAM

There are up to three components involved in the path to LD-FAM in a PBR fabric: a Host ES, a Downstream ES, and an LD-FAM device. The Host ES and LD-FAM devices require no special handling and report CDAT information covering their own characteristics as they would in an HBR system deployment. The Downstream ES, however, is required to report CDAT information that covers its own device-level performance factoring in the impact of the fabric routing path, as described below.

Latency and BW values are provided when the binding between a Host ES VCS and Downstream ES VCS is configured with the **Configure PID Binding** command. Routes through a fabric are expected to have symmetric performance characteristics. As such, only one latency and BW value is provided to define the fabric routing path. The Downstream ES adds the latency of the routing path to its own latency and uses the lesser of the BW values.

Hosts access CDAT information for Downstream ES VCSs from a DOE instance present in the vUSP.

##### 7.7.12.4.2 Accessing CDAT Information for G-FAM

The access mechanism for CDAT from G-FAM is necessarily different from LD-FAM as a result of 2 key architectural differences: G-FAM is presented through the FAST, not a switch-based topology, and GFDs do not implement nor expose a DOE instance to the host. CDAT access for G-FAM instead relies on the use of CCI opcodes.

The GAE providing G-FAM access is responsible for producing the CDAT for each segment of the FAST. Latency and BW values are provided when PID access is enabled with the **Configure PID Access** command. The CDAT information is queried by the host using the **Read CDAT** command.

GFDs are responsible for providing CDAT information covering their own characteristics. The host queries CDAT information from GFDs using the **Proxy GFD Management** Command request to initiate the **Read CDAT** command.

#### <span id="page-459-0"></span>7.7.12.5 Configuring CacheID in PBR Fabric

<span id="page-459-1"></span>From the host's perspective, configuration of CacheID for VHs spanning a PBR Fabric is performed identically to such configuration in an exclusively HBR topology. PBR switches automatically exchange ID configuration information in the following manner:

- 1. The Downstream ES presents ID route table capabilities in its vPPBs (see [Section 8.2.4.28](#page-592-1) for details on the CacheID Route Table).
- 2. The host will enumerate and assign all IDs and program the route table capability, triggering the Commit bit to complete the configuration.
- 3. The setting of the Commit bit triggers the Downstream ES to generate one or more RTUpdate VDMs, as defined in [Section 3.1.11.7,](#page-104-2) targeted at the Host PID. The Host ES will intercept this VDM based on its PBR opcode.
- 4. Upon receipt of the VDM, the Host ES programs the necessary ID to PID translation logic in the Host edge port.
- 5. The Host ES acknowledges successful programming of the ID translation logic with an RTUpdateAck VDM, as defined in [Section 3.1.11.8](#page-105-4), sent to the Downstream ES for each RTUpdate VDM that was received and successfully processed.
- 6. Upon receipt of the VDM, the Downstream ES sets the corresponding 'RT Committed' bit in the vUSP.

A downstream HBR switch topology requires PIDs for each unique potential target so that IDs can be translated between CacheID and PID at the fabric edges. For CacheID, the ID is valid if the Valid bit is set in a Cache ID Target entry in the Cache ID Route Table Capability Structure. The corresponding PID used is the PID of the DSP to which the Route Table entry has been configured to map. Multiple PIDs must be assigned to a DSP if multiple IDs map to that DSP.

#### <span id="page-460-0"></span>7.7.12.6 Dynamic Fabric Changes

This section outlines how FMs and PBR switches handle various changes to the system configuration during runtime.

##### 7.7.12.6.1 Hot-Add and Link Up Events

A new Link Up on an unbound edge port is indicated to the FM via a Physical Switch Event Record. The FM uses the **Get Physical Port State** and **Get PBR Link Partner Info** commands to query information on the device connected to the port.

When an SLD or PCIe device is Hot-Added to a bound port, the FM can be notified but is not involved.

##### 7.7.12.6.2 Dynamic Configuration Changes

There are many runtime configuration changes that an FM can trigger on a fabric:

- Binding/Unbinding: New bindings are presented to hosts as hot-add operations. Unbinding an EP is presented as a hot-remove operation.
- Updates to GMV/VTV: The GAE generates a notification to the host when changes are made to the GMV or VTV enabling or disabling access to a particular PID.
- GFD DCD changes: GFDs generate notifications to all impacted GAEs when updates are made to a host group's extent list.

##### 7.7.12.6.3 Hot/Surprise Remove and Link Down Events

The FM is responsible for managing a Link Down event:

- The PBR switch that experienced the Link Down notifies the FM with a Physical Switch Event Record
- EP Link Down events are represented as surprise removes to the host
- The FM manages any required topology changes associated with an ISL Link Down event, including clearing the PID binding between the Upstream ES and Downstream ES VCSs, which is presented to the host as a hot-remove of the Downstream ES VCS
- GFD Link Down events prompt the FM to disable access to the corresponding PID in all impacted hosts' GAE GMV and VTV
- PBR switches drop unroutable transactions

### <span id="page-460-1"></span>7.7.13 PBR Switch Command Set

This command set is only supported by, and must be supported by, PBR switches to facilitate the discovery of a PBR fabric and configuration of routing and bindings.

#### <span id="page-460-2"></span>7.7.13.1 Identify PBR Switch (Opcode 5700h)

<span id="page-460-3"></span>This command provides information to the FM about a PBR switch's fabric capabilities.

Possible Command Return Codes:

- Success
- Unsupported
- Internal Error
- Retry Required

**Command Effects:**

• None

<span id="page-461-1"></span>**Table 7-112. Identify PBR Switch Response Payload**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |  |
|-------------|--------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--|
| 0h          | 8                  | GAE Support Map: Bitmask indicating whether a VCS includes (1) or does not<br>include (0) a GAE instance in the host edge switch USP or downstream edge<br>switch vUSP where bit position corresponds to VCS ID.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |  |
| 8h          | 1                  | Number of DRTs: Total number of DRTs supported by the switch. This value<br>shall be greater than 0.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |  |
| 9h          | 1                  | Number of RGTs: Total number of RGTs supported by the switch.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |  |
| Ah          | 1                  | Reserved                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |  |
| Bh          | 1                  | •<br>Bit[0]: Random Supported: Indicates whether "Random" dynamic routing<br>mode is supported (1) or not supported (0)<br>•<br>Bit[1]: Congestion Avoidance Supported: Indicates whether "Mix with<br>CA" dynamic routing mode is supported (1) or not supported (0)<br>•<br>Bit[2]: Advanced Congestion Avoidance Supported: Indicates whether<br>"Advanced CA" dynamic routing mode is supported (1) or not supported (0)<br>•<br>Bits[5:3]: Reserved<br>•<br>Bit[6]: Vendor-specific Routing Mode 1 Supported: Indicates whether<br>the vendor-specific routing mode configured by dynamic routing mode<br>value 6 is supported (1) or not supported (0)<br>•<br>Bit[7]: Vendor-specific Routing Mode 2 Supported: Indicates whether<br>the vendor-specific routing mode configured by mode value 7 is supported<br>(1) or not supported (0) |  |

#### <span id="page-461-0"></span>7.7.13.2 Fabric Crawl Out (Opcode 5701h)

This command is used to tunnel management commands at components in a PBR fabric in two scenarios:

<span id="page-461-2"></span>- • PBR devices with no assigned PID: Tunneled command is sent to the PBR switch to which the PBR device is attached with a target specifying the PBR switch port to which the PBR device is connected. The receiving switch will transmit the command out the specified port using the reserved DPID FFFh.
- PBR devices with an assigned PID: Tunnel command is sent to a PBR switch with a target specifying the PID assigned to the PBR device.

The transport of these commands across PBR links is defined in [Section 7.7.11.6.](#page-456-0)

<span id="page-462-0"></span>**Figure 7-54. Tunneling Commands to Remote Devices**

![](_page_462_Figure_3.jpeg)

The Management Command input payload field includes the tunneled command encapsulated in the CCI Message Format, as defined in [Figure 7-19.](#page-346-1) This can include an additional layer of tunneling for commands issued to components with no assigned PID, as illustrated in [Figure 7-55](#page-462-1).

<span id="page-462-1"></span>**Figure 7-55. Tunneling Commands to Remote Devices with No Assigned PID**

![](_page_462_Figure_6.jpeg)

Response size varies, based on the tunneled command's definition. Valid targets for the tunneled commands include PBR switch ports, and PBR devices within a fabric.

This command fails with "Invalid Input" if the target specifies a non-existent switch port or a PID with no valid entry in the DRT.

Components shall terminate the processing of a request that includes more than 2 layers of tunneling and provide an "Unsupported" return code.

Possible Command Return Codes:

- Success
- Unsupported
- Invalid Input
- Internal Error

• Retry Required

**Command Effects:**

• None

<span id="page-463-1"></span>**Table 7-113. Fabric Crawl Out Request Payload**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                                                                                        |  |
|-------------|--------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--|
| 0h          | 2                  | Target: Encoding depends on Target Type:<br>•<br>Target Type = 0:<br>— Bits[7:0]: Port Number: Switch shall transmit command out<br>specified egress port.<br>— Bits[15:8]: Reserved.<br>•<br>Target Type = 1:<br>— Bits[11:0]: PBR-ID: Target PID. Switch shall determine egress port<br>using DRT.<br>— Bits[15:12]: Reserved.<br>•<br>All other encodings are reserved          |  |
| 2h          | 1                  | •<br>Bits[3:0]: Target Type: Specifies the type of tunneling target for this<br>command:<br>— 0h = Port Number: Indicates that the tunneling target is a<br>component on the far end of a switch port<br>— 1h = PBR-ID: Indicates that the tunneling target is a component in<br>the PBR fabric address by a PID<br>— All other encodings are reserved<br>•<br>Bits[7:4]: Reserved |  |
| 3h          | 1                  | Reserved                                                                                                                                                                                                                                                                                                                                                                           |  |
| 4h          | 2                  | Command Size: Number of valid bytes in Management Command.                                                                                                                                                                                                                                                                                                                         |  |
| 6h          | Varies             | Management Command: Request message formatted in the CCI Message<br>Format as defined in Figure 7-19.                                                                                                                                                                                                                                                                              |  |

<span id="page-463-2"></span>**Table 7-114. Fabric Crawl Out Response Payload**

| Byte Offset | Length<br>in Bytes | Description                                                                                          |  |
|-------------|--------------------|------------------------------------------------------------------------------------------------------|--|
| 0h          | 2                  | Response Length: Number of valid bytes in Response Message.                                          |  |
| 2h          | 2                  | Reserved                                                                                             |  |
| 4h          | Varies             | Response Message: Response message formatted in the CCI Message Format<br>as defined in Figure 7-19. |  |

#### <span id="page-463-0"></span>7.7.13.3 Get PBR Link Partner Info (Opcode 5702h)

<span id="page-463-3"></span>This command reads the data received from the latest "Link Partner Info" VDM on a PBR link.

Possible Command Return Codes:

- Success
- Unsupported
- Invalid Input
- Internal Error
- Retry Required

**Command Effects:**

<span id="page-464-0"></span>**Table 7-115. Get PBR Link Partner Info Request Payload**

| Byte Offset | Length<br>in Bytes | Description                                                                |
|-------------|--------------------|----------------------------------------------------------------------------|
| 0h          | 1h                 | Number of Ports: Number of ports requested.                                |
| 1h          | Varies             | Port ID List: 1-byte ID of requested port, repeated Number of Ports times. |

<span id="page-464-1"></span>**Table 7-116. Get PBR Link Partner Info Response Payload**

| Byte Offset | Length<br>in Bytes | Description                                                                                                   |
|-------------|--------------------|---------------------------------------------------------------------------------------------------------------|
| 0h          | 1                  | Number of Ports: Number of port information blocks returned.                                                  |
| 1h          | 3                  | Reserved                                                                                                      |
| 4h          | Varies             | Link Partner Info List: Link Partner Info block as defined in Table 7-117,<br>repeated Number of Ports times. |

<span id="page-464-2"></span>**Table 7-117. Get Link Partner Info Block Format**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                       |
|-------------|--------------------|-----------------------------------------------------------------------------------------------------------------------------------|
| 00h         | 1                  | Port ID: Number of the port reporting this Link Partner Info.                                                                     |
| 01h         | 1                  | Far End Port ID: Port number (Port ID) of the source (sender) of the Link<br>Partner Info VDM.                                    |
| 02h         | 2                  | •<br>Bits[11:0]: PID: As reported in Link Partner Info VDM<br>•<br>Bits[15:12]: Device Type: As reported in Link Partner Info VDM |
| 04h         | 10h                | Link Partner ID: As reported in Link Partner Info VDM.                                                                            |
| 14h         | 1                  | Standard FC VC List: As reported in Link Partner Info VDM.                                                                        |
| 15h         | 1                  | UIO FC VC List: As reported in Link Partner Info VDM.                                                                             |
| 16h         | 10h                | Primary FM UUID: As reported in Link Partner Info VDM.                                                                            |
| 26h         | 10h                | Secondary FM UUID: As reported in Link Partner Info VDM.                                                                          |

#### 7.7.13.4 Get PID Target List (Opcode 5703h)

<span id="page-464-3"></span>This command retrieves the list of targets within a PBR switch to which a PID may be assigned. This does not include the PID assigned to the switch itself as part of the **Claim FM Ownership** command. As outlined in [Section 7.7.6.5,](#page-421-0) the following restrictions apply when assigning PIDs:

- A fabric port may be assigned one PID that can be shared among multiple fabric ports
- A Downstream Edge Port may be assigned one PID that must be unique
- A Host Edge Port may be assigned more than one PID, each of which must be unique

Possible Command Return Codes:

- Success
- Unsupported
- Invalid Input
- Internal Error
- Retry Required

Command Effects:

• None

<span id="page-465-1"></span>**Table 7-118. Get PID Target List Request Payload**

| Byte<br>Offset | Length<br>in Bytes | Description                                             |
|----------------|--------------------|---------------------------------------------------------|
| 0h             | 2                  | Start Index: Index of first target to return.           |
| 2h             | 2                  | Number of Targets: Maximum number of targets to return. |

<span id="page-465-2"></span>**Table 7-119. Get PID Target List Response Payload**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                   |
|----------------|--------------------|-------------------------------------------------------------------------------|
| 0h             | 2                  | Total Number of Targets: Total number of PID targets supported by the device. |
| 2h             | 2                  | Number of Targets: Number of targets returned in Target List.                 |
| 4h             | Varies             | Target List: List of PID target as defined in Table 7-120.                    |

<span id="page-465-3"></span>**Table 7-120. Target List Format**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                                  |
|----------------|--------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h             | 2                  | Target ID: ID of PID Target for use in Configure PID Assignment.                                                                                                                             |
| 2h             | 1                  | •<br>Bits[2:0]: Target Type:<br>— 000b = Fabric Port<br>— 001b = Host Edge Port (USP/GAE)<br>— 010b = Downstream Edge Port<br>— All other encodings are reserved<br>•<br>Bits[7:3]: Reserved |
| 3h             | 1                  | Instance ID: Index of PID for targets that can support multiple PIDs.                                                                                                                        |
| 4h             | 1                  | VCS ID: ID of associated VCS. Valid only when Target Type is 1 (Host Edge Port).                                                                                                             |
| 5h             | 1                  | Physical Port ID: Physical port ID of the target.                                                                                                                                            |
| 6h             | 2                  | •<br>Bits[11:0]: PID: Current PID assignment. FFFh if unassigned.<br>•<br>Bits[15:12]: Reserved.                                                                                             |

#### <span id="page-465-0"></span>7.7.13.5 Configure PID Assignment (Opcode 5704h)

<span id="page-465-4"></span>This command is used to assign PIDs to targets within a PBR switch.

*Note:* This command does not update the corresponding DRT entries for assigned or cleared PIDs. The DRT must be updated separately, using the **Set DRT** command as necessary.

This command shall return Invalid Input under the following conditions:

- Specified target is invalid
- PID has already been assigned to another target within the switch

Possible Command Return Codes:

- Success
- Unsupported
- Invalid Input
- Internal Error

• Retry Required

**Command Effects:**

• None

<span id="page-466-1"></span>**Table 7-121. Configure PID Assignment Request Payload**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                                                                       |
|-------------|--------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h          | 1                  | •<br>Bits[2:0]: Operation: Specifies the PID assignment operation:<br>— 000b = Assign PID<br>— 001b = Clear PID<br>— All other encodings are reserved<br>•<br>Bits[7:3]: Reserved |
| 2h          | 2                  | Number of Targets: Number of entries in PID Assignment List.                                                                                                                      |
| 4h          | Varies             | PID Assignment List: List of PID assignments as defined in Table 7-122.                                                                                                           |

<span id="page-466-2"></span>**Table 7-122. PID Assignment**

| Byte Offset | Length<br>in Bytes | Description                                                                               |
|-------------|--------------------|-------------------------------------------------------------------------------------------|
| 0h          | 2                  | •<br>Bits[11:0]: PID: PID to assign to the specified target<br>•<br>Bits[15:12]: Reserved |
| 2h          | 2                  | Target ID: Index of PID target, as reported in Get PID Target List response.              |
| 4h          | 1                  | Instance ID: Index of PID for targets that can support multiple PIDs.                     |

#### <span id="page-466-0"></span>7.7.13.6 Get PID Binding (Opcode 5705h)

<span id="page-466-4"></span>This command reads the binding of Downstream ES PIDs to Upstream ES vDSPs or Upstream ES USP PIDs to Downstream ES vUSPs. The output also includes latency and BW values for the fabric routing path for use in generating associated CDAT information.

Possible Command Return Codes:

- Unsupported
- Invalid Input
- Internal Error
- Retry Required
- Busy

**Command Effects:**

• Background Operation

<span id="page-466-3"></span>**Table 7-123. Get PID Binding Request Payload**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                    |
|----------------|--------------------|------------------------------------------------------------------------------------------------|
| 0h             | 1                  | Target VCS: ID of the VCS to query.                                                            |
| 1h             | 1                  | Target vPPB: Index of the vPPB to query. Reserved when the binding target is a<br>Host ES VCS. |

<span id="page-467-1"></span>**Table 7-124. Get PID Binding Response Payload**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                     |
|----------------|--------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 00h            | 2                  | •<br>Bits[11:0]: PID: PID of the remote binding target. FFFh if unbound.<br>•<br>Bits[15:12]: Reserved.                                                                                                                                         |
| 02h            | 2                  | Reserved                                                                                                                                                                                                                                        |
| 04h            | 8                  | Latency Entry Base Unit: Latency Entry Base Unit for path between host and target<br>device, as defined in ACPI HMAT System Locality Latency and Bandwidth Information<br>Structure. Valid only when the binding target is a Downstream ES VCS. |
| 0Ch            | 2                  | Latency Entry: Latency Entry for path between host and target device, as defined in<br>ACPI HMAT System Locality Latency and Bandwidth Information Structure. Valid only<br>when the binding target is a Downstream ES VCS.                     |
| 0Eh            | 8                  | BW Entry Base Unit: Bandwidth Entry Base Unit for path between host and target<br>device, as defined in ACPI HMAT System Locality Latency and Bandwidth Information<br>Structure. Valid only when the binding target is a Downstream ES VCS.    |
| 16h            | 2                  | BW Entry: Bandwidth Entry for path between host and target device, as defined in<br>ACPI HMAT System Locality Latency and Bandwidth Information Structure. Valid only<br>when the binding target is a Downstream ES VCS.                        |

#### <span id="page-467-0"></span>7.7.13.7 Configure PID Binding (Opcode 5706h)

This command configures the binding of a PID to a target. It is used to bind:

<span id="page-467-3"></span>- • Downstream ES PIDs to Upstream ES vDSPs
- Upstream ES USP PIDs to Downstream ES vUSPs

The command input includes latency and BW values for the fabric routing path for use in generating associated CDAT information.

Possible Command Return Codes:

- Unsupported
- Background Command Started
- Invalid Input
- Internal Error
- Retry Required
- Busy

**Command Effects:**

• Background Operation

<span id="page-467-2"></span>**Table 7-125. Configure PID Binding Request Payload (Sheet 1 of 2)**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                      |
|----------------|--------------------|----------------------------------------------------------------------------------------------------------------------------------|
| 00h            | 1                  | •<br>Bits[2:0]: Operation:<br>— 000b = Bind<br>— 001b = Unbind<br>— All other encodings are reserved<br>•<br>Bits[7:3]: Reserved |
| 01h            | 1                  | Target VCS: ID of the VCS to which the PID is being bound.                                                                       |
| 02h            | 1                  | Target vPPB: Index of the vPPB to which the PID is being bound. Reserved when the<br>binding target is a Downstream ES VCS.      |
| 03h            | 1                  | Reserved                                                                                                                         |

**Table 7-125. Configure PID Binding Request Payload (Sheet 2 of 2)**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                             |
|----------------|--------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 04h            | 2                  | •<br>Bits[11:0]: PID: PID of the remote binding target<br>•<br>Bits[15:12]: Reserved                                                                                                                                                    |
| 06h            | 2                  | Reserved                                                                                                                                                                                                                                |
| 08h            | 8                  | Latency Entry Base Unit: Latency Entry Base Unit for path between host and target<br>device, as defined in ACPI HMAT System Locality Latency and Bandwidth Information<br>Structure. Reserved when the binding target is a Host ES VCS. |
| 10h            | 2                  | Latency Entry: Latency Entry for path between host and target device, as defined in<br>ACPI HMAT System Locality Latency and Bandwidth Information Structure. Reserved<br>when the binding target is a Host ES VCS.                     |
| 12h            | 8                  | BW Entry Base Unit: Bandwidth Entry Base Unit for path between host and target<br>device, as defined in ACPI HMAT System Locality Latency and Bandwidth Information<br>Structure. Reserved when the binding target is a Host ES VCS.    |
| 1Ah            | 2                  | BW Entry: Bandwidth Entry for path between host and target device, as defined in<br>ACPI HMAT System Locality Latency and Bandwidth Information Structure. Reserved<br>when the binding target is a Host ES VCS.                        |

#### <span id="page-468-0"></span>7.7.13.8 Get Table Descriptors (Opcode 5707h)

<span id="page-468-3"></span>This command reads descriptors of the DPID Routing Tables and Routing Group Tables in a PBR Switch.

Possible Command Return Codes:

- Success
- Unsupported
- Invalid Input
- Internal Error
- Retry Required

**Command Effects:**

• None

<span id="page-468-1"></span>**Table 7-126. Get Table Descriptors Request Payload**

| Byte Offset | Length<br>in Bytes | Description                                           |
|-------------|--------------------|-------------------------------------------------------|
| 0h          | 2                  | Start Index: Starting index into list of descriptors. |
| 2h          | 2                  | Number of Descriptors: Number of descriptors to read. |

<span id="page-468-2"></span>**Table 7-127. Get Table Descriptors Response Payload**

| Byte Offset | Length<br>in Bytes | Description                                                                      |
|-------------|--------------------|----------------------------------------------------------------------------------|
| 0h          | 2                  | Start Index: Starting index into list of descriptors.                            |
| 2h          | 2                  | Number of Descriptors: Number of table descriptors.                              |
| 4h          | Varies             | Get Table Descriptors List: List of table descriptors as defined in Table 7-128. |

<span id="page-469-1"></span>**Table 7-128. Get Table Descriptor Format**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                                                 |
|-------------|--------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h          | 1                  | •<br>Bits[1:0]: Table Type:<br>— 00b = DRT<br>— 01b = RGT<br>— All other encodings are reserved<br>•<br>Bits[7:2]: Reserved                                 |
| 1h          | 2                  | Table Index: Index of table.                                                                                                                                |
| 3h          | 20h                | Active Port Mask: Bitmask defining which ports actively use (1) or do not<br>actively use (0) this table. Bit position corresponds to physical port number. |
| 23h         | 4                  | Reserved                                                                                                                                                    |

#### <span id="page-469-0"></span>7.7.13.9 Get DRT (Opcode 5708h)

<span id="page-469-4"></span>This command reads the DPID Routing Tables in a PBR Switch.

Possible Command Return Codes:

- Success
- Unsupported
- Invalid Input
- Internal Error
- Retry Required

**Command Effects:**

• None

<span id="page-469-2"></span>**Table 7-129. Get DRT Request Payload**

| Byte<br>Offset | Length<br>in Bytes | Description                                       |
|----------------|--------------------|---------------------------------------------------|
| 0h             | 1                  | DRT Index: Index of DRT to read.                  |
| 1h             | 1                  | Reserved                                          |
| 2h             | 2                  | Number of Entries: Number of DRT entries to read. |
| 4h             | 2                  | Start Entry: Starting index into DRT entries.     |

<span id="page-469-3"></span>**Table 7-130. Get DRT Response Payload**

| Byte<br>Offset | Length<br>in Bytes | Description                                                         |
|----------------|--------------------|---------------------------------------------------------------------|
| 0h             | 1                  | DRT Index: Index of DRT.                                            |
| 1h             | 1                  | Reserved                                                            |
| 2h             | 2                  | Number of Entries: Number of DRT entries.                           |
| 4h             | 2                  | Start Entry: Starting index into DRT entries.                       |
| 6h             | 1                  | Associated RGT Index: Index of RGT used by this DRT.                |
| 7h             | 1                  | Reserved                                                            |
| 8h             | Varies             | DRT Entry List: List of DRT entry values as defined in Table 7-131. |

<span id="page-470-2"></span>**Table 7-131. DRT Entry Format**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                                               |
|----------------|--------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h             | 1                  | •<br>Bits[1:0]: Entry Type: Type of routing target specifier and M2S Req routing:<br>— 00b = Invalid<br>— 01b = Physical Port number<br>— 10b = RGT index<br>— 11b = Reserved<br>•<br>Bits[7:2]: Reserved |
| 1h             | 1                  | Routing Target: Encoding depends on Entry Type:<br>•<br>00h = Reserved<br>•<br>01h = Physical port number<br>•<br>02h = RGT entry index                                                                   |

#### <span id="page-470-0"></span>7.7.13.10 Set DRT (Opcode 5709h)

<span id="page-470-4"></span>This command sets the DPID Routing Tables in a PBR Switch.

Possible Command Return Codes:

- Success
- Unsupported
- Invalid Input
- Internal Error
- Retry Required

Command Effects:

• None

<span id="page-470-3"></span>**Table 7-132. Set DRT Request Payload**

| Byte<br>Offset | Length<br>in Bytes | Description                                                         |
|----------------|--------------------|---------------------------------------------------------------------|
| 0h             | 1                  | DRT Index: Index of DRT to configure.                               |
| 1h             | 1                  | Reserved                                                            |
| 2h             | 2                  | Number of Entries: Number of DRT entries to configure.              |
| 4h             | 2                  | Start Entry: Starting index into DRT entries.                       |
| 6h             | Varies             | DRT Entry List: List of DRT entry values as defined in Table 7-131. |

#### <span id="page-470-1"></span>7.7.13.11 Get RGT (Opcode 570Ah)

<span id="page-470-5"></span>This command reads the Routing Group Tables in a PBR Switch.

Possible Command Return Codes:

- Success
- Unsupported
- Invalid Input
- Internal Error
- Retry Required

Command Effects:

• None

<span id="page-471-0"></span>**Table 7-133. Get RGT Request Payload**

| Byte Offset | Length<br>in Bytes | Description                                   |
|-------------|--------------------|-----------------------------------------------|
| 0h          | 1                  | RGT Index: Index of RGT.                      |
| 1h          | 1                  | Reserved                                      |
| 2h          | 2                  | Number of Entries: Number of RGT entries.     |
| 4h          | 2                  | Start Entry: Starting index into RGT entries. |

<span id="page-471-1"></span>**Table 7-134. Get RGT Response Payload**

| Byte Offset | Length<br>in Bytes | Description                                                         |
|-------------|--------------------|---------------------------------------------------------------------|
| 0h          | 1                  | RGT Index: Index of RGT.                                            |
| 1h          | 1                  | Reserved                                                            |
| 2h          | 2                  | Number of Entries: Number of RGT entries.                           |
| 4h          | 2                  | Start Entry: Starting index into RGT entries.                       |
| 6h          | Varies             | RGT Entry List: List of RGT entry values as defined in Table 7-135. |

<span id="page-471-2"></span>**Table 7-135. RGT Entry Format**

| Byte<br>Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                                                                                                                     |
|----------------|--------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h             | 1                  | Egress Port[0]: Physical port number.                                                                                                                                                                                                                                                                                                                                                                           |
| 1h             | 1                  | Egress Port[1]: Physical port number.                                                                                                                                                                                                                                                                                                                                                                           |
| 2h             | 1                  | Egress Port[2]: Physical port number.                                                                                                                                                                                                                                                                                                                                                                           |
| 3h             | 1                  | Egress Port[3]: Physical port number.                                                                                                                                                                                                                                                                                                                                                                           |
| 4h             | 1                  | Egress Port[4]: Physical port number.                                                                                                                                                                                                                                                                                                                                                                           |
| 5h             | 1                  | Egress Port[5]: Physical port number.                                                                                                                                                                                                                                                                                                                                                                           |
| 6h             | 1                  | Egress Port[6]: Physical port number.                                                                                                                                                                                                                                                                                                                                                                           |
| 7h             | 1                  | Egress Port[7]: Physical port number.                                                                                                                                                                                                                                                                                                                                                                           |
| 8h             | 1                  | •<br>Bits[2:0]: Highest Valid Entry: Highest index in the Egress Port list that is valid.<br>•<br>Bits[5:3]: Highest Primary Entry: Highest index in the Egress Port list that<br>specifies a primary routing path. Subsequent valid egress ports are considered<br>secondary paths.<br>•<br>Bits[7:6]: Reserved.                                                                                               |
| 9h             | 1                  | •<br>Bits[2:0]: Dynamic Routing Mode: Specifies the dynamic routing mode to be<br>used for this entry:<br>— 000b = Random<br>— 001b = Congestion Avoidance<br>— 010b = Advanced Congestion Avoidance<br>— 011b, 101b = Reserved<br>— 110b, 111b = Vendor-specific<br>•<br>Bits[5:3]: Mix Setting: Specifies the mix used for dynamic routing mode, as<br>defined in Section 7.7.6.3<br>•<br>Bits[7:6]: Reserved |
| Ah             | 2                  | Reserved                                                                                                                                                                                                                                                                                                                                                                                                        |

#### <span id="page-472-0"></span>7.7.13.12 Set RGT (Opcode 570Bh)

<span id="page-472-4"></span>This command configures the Routing Group Tables in a PBR switch.

Possible Command Return Codes:

- Success
- Unsupported
- Invalid Input
- Internal Error
- Retry Required

**Command Effects:**

• None

<span id="page-472-2"></span>**Table 7-136. Set RGT Request Payload**

| Byte Offset | Length<br>in Bytes | Description                                                         |
|-------------|--------------------|---------------------------------------------------------------------|
| 0h          | 1                  | RGT Index: Index of RGT to configure.                               |
| 1h          | 1                  | Reserved                                                            |
| 2h          | 2                  | Number of Entries: Number of RGT entries to configure.              |
| 4h          | 2                  | Start Entry: Starting index into RGT entries.                       |
| 6h          | Varies             | RGT Entry List: List of RGT entry values as defined in Table 7-134. |

#### <span id="page-472-1"></span>7.7.13.13 Get LDST/IDT Capabilities (Opcode 570Ch)

This command retrieves a vPPB's LDST and IDT Capabilities, per [Section 7.7.9.](#page-441-1)

Possible Command Return Codes:

- • Success
- Unsupported
- Invalid Input
- Internal Error
- Retry Required

**Command Effects:**

• None

<span id="page-472-3"></span>**Table 7-137. Get LDST/IDT Capabilities Request Payload**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                                                                            |
|-------------|--------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h          | 1                  | vPPB Instance: The value of 0 represents USP. The values of 1 and above<br>represent the DSP vPPBs in increasing Device Number, Function Number order,<br>as defined in Section 7.1.4. |

<span id="page-473-1"></span>**Table 7-138. Get LDST/IDT Capabilities Response Payload**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                                                                                            |
|-------------|--------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h          | 1                  | vPPB Instance: The value of 0 represents USP. The values of 1 and above<br>represent the DSP vPPBs in increasing Device Number, Function Number order,<br>as defined in Section 7.1.4.                 |
| 1h          | 2                  | Number of Segments: Number of LDST segments that are supported by this<br>LDST/IDT. The number of entries must be 0 or a power of 2.                                                                   |
| 3h          | 1                  | LDST Segment Size<br>•<br>Bits[2:0]: LSegSz per the FSegSz encoding defined in Table 7-81<br>•<br>Bits[7:3]: Reserved<br>The device shall return 0h if this value has not been initialized.            |
| 4h          | 2                  | Number of IDT: Number of Interleave Device Table entries supported by this<br>LDST/IDT.                                                                                                                |
| 6h          | 2                  | Number of Completer ID-Based Re-Routers: Number of Completer ID<br>Based Re-Router entries supported by this LDST/IDT.                                                                                 |
| 8h          | 2                  | •<br>Bits[11:0]: Local PID: PID assigned to this vPPB. FFFh if unassigned.<br>•<br>Bits[15:12]: Reserved.                                                                                              |
| Ah          | 8                  | Fabric Base: Base HPA of this LDST.<br>FabricBase shall be aligned to the programmed LDST Segment Size.<br>The device shall return 0h if this value has not been initialized.                          |
| 12h         | 8                  | Fabric Limit: Upper HPA of this LDST. Shall be greater than FabricBase. Shall<br>be aligned to the programmed LDST Segment Size.<br>The device shall return 0h if this value has not been initialized. |

#### <span id="page-473-0"></span>7.7.13.14 Set LDST/IDT Configuration (Opcode 570Dh)

<span id="page-473-2"></span>This command sets the GAE's LDST and IDT Capabilities, per [Section 7.7.9](#page-441-1). Because the FabricBase and FabricLimit values must be aligned to the programmed LDST Segment Size, all three Host-chosen values are configured in one request.

Possible Command Return Codes:

- Success
- Unsupported
- Invalid Input
- Internal Error
- Retry Required

**Command Effects:**

• Immediate Configuration Change

<span id="page-474-1"></span>**Table 7-139. Set LDST/IDT Configuration Request Payload**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                                                                            |
|-------------|--------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h          | 1                  | vPPB Instance: The value of 0 represents USP. The values of 1 and above<br>represent the DSP vPPBs in increasing Device Number, Function Number order,<br>as defined in Section 7.1.4. |
| 1h          | 1                  | LDST Segment Size<br>•<br>Bits[2:0]: LSegSz per the FSegSz encoding defined in Table 7-81<br>•<br>Bits[7:3]: Reserved                                                                  |
| 2h          | 8                  | FabricBase: Base HPA of this LDST. FabricBase shall be aligned to the<br>programmed LDST Segment Size. The value 0h will disable this LDST/IDT<br>decoder.                             |
| Ah          | 8                  | FabricLimit: Upper HPA of this LDST. Shall be greater than FabricBase. Shall be<br>aligned to the programmed LDST Segment Size. The value 0h will disable this<br>LDST/IDT decoder.    |

#### <span id="page-474-0"></span>7.7.13.15 Get LDST Segment Entries (Opcode 570Eh)

<span id="page-474-3"></span>This command reads the configuration of LDST Segment entries. The Host is responsible for mapping the LD-FAM range of HPAs to the appropriate number of available Segment Entries. Should the Host or the GAE have limited message payload capacity, the Host shall be responsible for breaking up the configuration operation into suitably sized requests.

Possible Command Return Codes:

- Success
- Unsupported
- Invalid Input
- Internal Error
- Retry Required

**Command Effects:**

<span id="page-474-2"></span>**Table 7-140. Get LDST Segment Entries Request Payload**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                                                                                                           |
|-------------|--------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h          | 1                  | vPPB Instance: The value of 0 represents USP. The values of 1 and above<br>represent the DSP vPPBs in increasing Device Number, Function Number order,<br>as defined in Section 7.1.4.                                                                                                                                                                                                                |
| 1h          | 1                  | Reserved                                                                                                                                                                                                                                                                                                                                                                                              |
| 2h          | 2                  | Seg Count: Number of LDST Segment Entries requested. Value should be >0<br>and not more than the lesser of the total Segment table entries available, or<br>that number of entries that can be contained in the maximum message size<br>handled by the host and the target GAE.                                                                                                                       |
| 4h          | 2                  | Starting Segment Index: Index of the first segment being requested. An<br>index of 0 shall designate the configuration of the 1st Segment, corresponding to<br>HPA = FabricBase. The starting index given shall not be larger than the maximum<br>segment entry number supported. The starting index Plus the Seg Count value<br>shall not be larger than the maximum segment entry number supported. |

<span id="page-475-1"></span>**Table 7-141. Get LDST Segment Entries Response Payload**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                                                                                                          |
|-------------|--------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h          | 2                  | Seg Count: Number of LDST Segment Entries described in the Seg<br>Entry_List[ ]. Value should be >0 and not more than the lesser of the total<br>Segment table entries available, or that number of entries that can be contained<br>in the maximum message size handled by the host and the target GAE.                                                                                             |
| 2h          | 2                  | Starting Segment Index: Index of the first segment being returned. An index<br>of 0 shall designate the configuration of the 1st Segment, corresponding to HPA =<br>FabricBase. The starting index given shall not be larger than the maximum<br>segment entry number supported. The starting index Plus the Seg Count value<br>shall not be larger than the maximum segment entry number supported. |
| 4h          | Varies             | Segment List[ ]: List of Segment Entries as defined in Table 7-142.                                                                                                                                                                                                                                                                                                                                  |

<span id="page-475-2"></span>**Table 7-142. LDST Segment Entry Format**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                                                                                                   |
|-------------|--------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h          | 1                  | Valid<br>•<br>Bit[0]: Valid Entry: As per Figure 7-31<br>•<br>Bit[1]: Enable PCIe Segment: Indicates that the target is in a separate<br>PCIe segment, thus the request will include the requester's segment<br>number<br>•<br>Bits[7:2]: Reserved                                                                                                                                            |
| 1h          | 1                  | Intlv<br>•<br>Bits[3:0]: Interleave Mode: As per Table 7-82<br>•<br>Bits[7:4]: Reserved                                                                                                                                                                                                                                                                                                       |
| 2h          | 1                  | Gran<br>•<br>Bits[3:0]: Interleave Granularity: As per Table 7-83<br>•<br>Bits[7:4]: Reserved                                                                                                                                                                                                                                                                                                 |
| 3h          | 1                  | Reserved                                                                                                                                                                                                                                                                                                                                                                                      |
| 4h          | 2                  | DPID/IX: DPID or IDT Index, depending on Intlv field value:<br>•<br>Bits[11:0]:<br>— If Intlv == 0, this is the actual DPID to which the LD-FAM request is<br>to be sent.<br>— Else, this is Index of the IDT entry that contains the DPID of the first<br>EP in the interleave set. See Figure 7-31 and the description of<br>interleaving in Section 7.7.2.4.<br>•<br>Bits[15:12]: Reserved |
| 6h          | 2                  | Reserved                                                                                                                                                                                                                                                                                                                                                                                      |

#### <span id="page-475-0"></span>7.7.13.16 Set LDST Segment Entries (Opcode 570Fh)

<span id="page-475-3"></span><span id="page-489-3"></span>This command is used by the Host to set the configuration of LDST Segment entries. The Host is responsible for mapping the LD-FAM range of HPAs to the appropriate number of available Segment Entries, per [Section 7.7.2.4.](#page-397-0) Should the Host or the GAE have limited message payload capacity, the Host shall be responsible for breaking up the configuration operation into suitably sized requests.

This command fails with Invalid Input if access to the specified DPID is not enabled in the LAV.

Possible Command Return Codes:

- Success
- Unsupported

- Invalid Input
- Internal Error
- Retry Required

**Command Effects:**

• Immediate Configuration Change

<span id="page-476-1"></span>**Table 7-143. Set LDST Segment Entries Request Payload**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                                                                                                            |
|-------------|--------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h          | 1                  | vPPB Instance: The value of 0 represents USP. The values of 1 and above<br>represent the DSP vPPBs in increasing Device Number, Function Number order,<br>as defined in Section 7.1.4.                                                                                                                                                                                                                 |
| 1h          | 1                  | Reserved                                                                                                                                                                                                                                                                                                                                                                                               |
| 2h          | 2                  | Seg Count: Number of LDST Segment Entries described in the Seg<br>Entry_List[ ]. Value should be >0 and not more than the lesser of the total<br>Segment table entries available, or that number of entries that can be contained<br>in the maximum message size handled by the host and the target GAE.                                                                                               |
| 4h          | 2                  | Starting Segment Index: Index of the first segment being configured. An<br>index of 0 shall designate the configuration of the 1st Segment, corresponding to<br>HPA = FabricBase. The starting index given shall not be larger than the maximum<br>segment entry number supported. The starting index Plus the Seg Count value<br>shall not be larger than the maximum segment entry number supported. |
| 6h          | Varies             | Segment List[ ]: List of Segment Entries as defined in Table 7-142.                                                                                                                                                                                                                                                                                                                                    |

#### <span id="page-476-0"></span>7.7.13.17 Get LDST IDT DPID Entries (Opcode 5710h)

<span id="page-476-2"></span>This command reads the configuration of IDT entries that are used by the LDST. The Host is responsible for mapping the capacity of specific devices targeted by LDST into interleaved regions of HPA. Should the Host or the switch mailbox have limited message payload capacity, the Host shall be responsible for breaking up the configuration operation into suitably sized requests.

Possible Command Return Codes:

- Success
- Unsupported
- Invalid Input
- Internal Error
- Retry Required

**Command Effects:**

<span id="page-477-1"></span>**Table 7-144. Get LDST IDT DPID Entries Request Payload**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                        |
|-------------|--------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h          | 1                  | vPPB Instance: The value of 0 represents USP. The values of 1 and above<br>represent the DSP vPPBs in increasing Device Number, Function Number order,<br>as defined in Section 7.1.4.                                                                                                             |
| 1h          | 1                  | Reserved                                                                                                                                                                                                                                                                                           |
| 2h          | 2                  | LDST IDT Entry Count: Number of LDST IDT Entries requested. Value should<br>be >0 and not more than the lesser of the total LDST IDT table entries<br>available, or that number of entries that can be contained in the maximum<br>message size handled by the host and the target switch mailbox. |
| 4h          | 2                  | Starting LDST IDT Entry Index: Index of the first LDST IDT entry being<br>requested. An index of 0 shall designate the configuration of the 1st entry. The<br>starting index Plus the LDST IDT Entry Count value shall not be larger than the<br>maximum LDST IDT entry number supported.          |

<span id="page-477-2"></span>**Table 7-145. Get LDST IDT DPID Entries Response Payload**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                       |
|-------------|--------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h          | 2                  | LDST IDT Entry Count: Number of LDST IDT Entries returned. Value should be<br>>0 and not more than the lesser of the total LDST IDT table entries available, or<br>that number of entries that can be contained in the maximum message size<br>handled by the host and the target switch mailbox. |
| 2h          | 2                  | Starting LDST IDT Entry Index: Index of the first LDST IDT entry being<br>returned. An index of 0 shall designate the configuration of the 1st entry. The<br>starting index Plus the LDST IDT Entry Count value shall not be larger than the<br>maximum LDST IDT entry number supported.          |
| 4h          | Varies             | LDST IDT DPID[ ]: DPID of the target device for the LDST IDT entry. See<br>Figure 7-31 and the description of interleaving in Section 7.7.2.4.<br>Repeats LDST IDT Entry Count number of times.<br>•<br>Bits[11:0]: PID of the target device<br>•<br>Bits[15:12]: Reserved                        |

#### <span id="page-477-0"></span>7.7.13.18 Set LDST IDT DPID Entries (Opcode 5711h)

<span id="page-477-3"></span>This command sets the configuration of IDT entries that are used by the LDST. The Host is responsible for mapping the capacity of specific devices targeted by LDST into interleaved regions of HPA. Should the Host or the switch mailbox have limited message payload capacity, the Host shall be responsible for breaking up the configuration operation into suitably sized requests.

Possible Command Return Codes:

- Success
- Unsupported
- Invalid Input
- Internal Error
- Retry Required

**Command Effects:**

• Immediate Configuration Change

<span id="page-478-1"></span>**Table 7-146. Set LDST IDT DPID Entries Request Payload**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                               |
|-------------|--------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h          | 1                  | vPPB Instance: The value of 0 represents USP. The values of 1 and above<br>represent the DSP vPPBs in increasing Device Number, Function Number order,<br>as defined in Section 7.1.4.                                                                                                                    |
| 1h          | 1                  | Reserved                                                                                                                                                                                                                                                                                                  |
| 2h          | 2                  | LDST IDT Entry Count: Number of LDST IDT Entries being configured. Value<br>should be >0 and not more than the lesser of the total LDST IDT table entries<br>available, or that number of entries that can be contained in the maximum<br>message size handled by the host and the target switch mailbox. |
| 4h          | 2                  | Starting LDST IDT Entry Index: Index of the first LDST IDT entry being<br>configured. An index of 0 shall designate the configuration of the 1st entry. The<br>starting index Plus the LDST IDT Entry Count value shall not be larger than the<br>maximum LDST IDT entry number supported.                |
| 6h          | 2                  | Reserved                                                                                                                                                                                                                                                                                                  |
| 8h          | Varies             | LDST IDT DPID: DPID of the device for the LDST IDT entry. See Figure 7-31<br>and the description of interleaving in Section 7.7.2.4.<br>Repeats LDST IDT Entry Count number of times.<br>•<br>Bits[11:0]: PID of the target device<br>•<br>Bits[15:12]: Reserved                                          |

#### <span id="page-478-0"></span>7.7.13.19 Get Completer ID-Based Re-Router Entries (Opcode 5712h)

This command reads the configuration of Completer ID-Based Re-Router entries.

Possible Command Return Codes:

- • Success
- Unsupported
- Invalid Input
- Internal Error
- Retry Required

Command Effects:

<span id="page-478-2"></span>**Table 7-147. Get Completer ID-Based Re-Router Entries Request Payload**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                                                                                  |
|-------------|--------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h          | 1                  | vPPB Instance: The value of 0 represents USP. The values of 1 and above<br>represent the DSP vPPBs in increasing Device Number, Function Number order,<br>as defined in Section 7.1.4.                                                                                                                                                                                       |
| 1h          | 1                  | Reserved                                                                                                                                                                                                                                                                                                                                                                     |
| 2h          | 2                  | Completer ID-Based Re-Router Entry Count: Number of Completer ID<br>Based Re-Router Entries requested. Value should be >0 and not more than the<br>lesser of the total Completer ID-Based Re-Router table entries available, or that<br>number of entries that can be contained in the maximum message size handled<br>by the host and the target GAE.                       |
| 4h          | 2                  | Starting Completer ID-Based Re-Router Entry Index: Index of the first<br>Completer ID-Based Re-Router entry being requested. An index of 0 shall<br>designate the configuration of the 1st entry. The starting index Plus the Completer<br>ID-Based Re-Router Entry Count value shall not be larger than the maximum<br>Completer ID-Based Re-Router entry number supported. |

<span id="page-479-1"></span>**Table 7-148. Get Completer ID-Based Re-Router Entries Response Payload**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                                                                                 |
|-------------|--------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h          | 2                  | Completer ID-Based Re-Router Entry Count: Number of Completer ID<br>Based Re-Router Entries returned. Value should be >0 and not more than the<br>lesser of the total Completer ID-Based Re-Router table entries available, or that<br>number of entries that can be contained in the maximum message size handled<br>by the host and the target GAE.                       |
| 2h          | 2                  | Starting Completer ID-Based Re-Router Entry Index: Index of the first<br>Completer ID-Based Re-Router entry being returned. An index of 0 shall<br>designate the configuration of the 1st entry. The starting index Plus the Completer<br>ID-Based Re-Router Entry Count value shall not be larger than the maximum<br>Completer ID-Based Re-Router entry number supported. |
| 4h          | Varies             | Completer ID-Based Re-Router Entry List[ ]: As defined in Table 7-149.<br>Repeats Completer ID-Based Re-Router Entry Count number of times.                                                                                                                                                                                                                                 |

<span id="page-479-2"></span>**Table 7-149. Completer ID-Based Re-Router Entry**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                                                                           |
|-------------|--------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h          | 2                  | Completer ID-Based Re-Router DPID[ ]: DPID of the requester for the<br>Completer ID-Based Re-Router entry.<br>•<br>Bits[11:0]: PID of the requester<br>•<br>Bit[12]: Enable PCIe Segment: Indicates that the requester is in a<br>separate PCIe segment, so the request will include the requester's and<br>completer's segment numbers<br>•<br>Bits[15:13]: Reserved |
| 2h          | 1                  | Requester PCIe Segment: PCIe Segment number for the requester. Valid only<br>if Enable PCIe Segment is set.                                                                                                                                                                                                                                                           |
| 3h          | 1                  | Requester Bus Number: PCIe Bus number for requester.                                                                                                                                                                                                                                                                                                                  |
| 4h          | 1                  | •<br>Bits[2:0]: Requester Function Number: PCIe Function number for<br>requester<br>•<br>Bits[7:3]: Requester Device Number: PCIe Device number for requester                                                                                                                                                                                                         |

#### <span id="page-479-0"></span>7.7.13.20 Set Completer ID-Based Re-Router Entries (Opcode 5713h)

<span id="page-479-3"></span>This command sets the configuration of Completer ID-Based Re-Router entries.

This command fails with Invalid Input if access to the specified DPID is not enabled in the LAV.

Possible Command Return Codes:

- Success
- Unsupported
- Invalid Input
- Internal Error
- Retry Required

**Command Effects:**

• Immediate Configuration Change

<span id="page-480-1"></span>**Table 7-150. Set Completer ID-Based Re-Router Entries Request Payload**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
|-------------|--------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h          | 1                  | vPPB Instance: The value of 0 represents USP. The values of 1 and above<br>represent the DSP vPPBs in increasing Device Number, Function Number order,<br>as defined in Section 7.1.4.                                                                                                                                                                                                                                                                                                                 |
| 1h          | 1                  | Reserved                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| 2h          | 2                  | Completer ID-Based Re-Router Entry Count: Number of Completer ID<br>Based Re-Router Entries being configured. Value should be >0 and not more<br>than the lesser of the total Completer ID-Based Re-Router table entries<br>available, or that number of entries that can be contained in the maximum<br>message size handled by the host and the target GAE.                                                                                                                                          |
| 4h          | 2                  | Starting Completer ID-Based Re-Router Entry Index: Index of the first<br>Completer ID-Based Re-Router entry being configured. An index of 0 shall<br>designate the configuration of the 1st entry. The starting index given shall not be<br>larger than the maximum Completer ID-Based Re-Router entry number<br>supported. The starting index Plus the Completer ID-Based Re-Router Entry<br>Count value shall not be larger than the maximum Completer ID-Based Re<br>Router entry number supported. |
| 6h          | Varies             | Completer ID-Based Re-Router Entry List[ ]: As defined in Table 7-149.<br>Repeats Completer ID-Based Re-Router Entry Count number of times.                                                                                                                                                                                                                                                                                                                                                            |

#### <span id="page-480-0"></span>7.7.13.21 Get LDST Access Vector (Opcode 5714h)

<span id="page-480-4"></span>This command is used by the host to query its current LAV.

This command will return Invalid Input when the requested byte range exceeds the size of the access vector buffer, as defined in [Table 7-164.](#page-485-3)

Possible Command Return Codes:

- Success
- Unsupported
- Invalid Input
- Internal Error
- Retry Required

**Command Effects:**

• None

<span id="page-480-2"></span>**Table 7-151. Get LDST Access Vector Request Payload**

| Byte Offset | Length<br>in Bytes | Description                                              |
|-------------|--------------------|----------------------------------------------------------|
| 0h          | 4                  | Start Byte: Offset in bytes into Vector Data.            |
| 4h          | 4                  | Number of Bytes: Size in bytes of Vector Data requested. |

<span id="page-480-3"></span>**Table 7-152. Get LDST Access Vector Response Payload**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                               |
|-------------|--------------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| 0h          | 4                  | Number of Bytes: Size in bytes of Vector Data returned.                                                                                   |
| 4h          | Varies             | Vector Data: Excerpt of data from LDST Access Vector, defined in<br>Table 7-153. Excerpt begins a Start Byte and is Number of Bytes long. |

<span id="page-481-2"></span>**Table 7-153. LDST Access Vector**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                                                     |
|-------------|--------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 000h        | 200h               | LDST Access Vector: 4-Kb vector in which each bit corresponds to the<br>associated PID (i.e., bit n represents PID n). A value of 1 in a bit position<br>indicates that LDST and ID-Based Re-Router access to the corresponding PID is<br>enabled. A value of 0 in a bit position indicates that access to the corresponding<br>PID is blocked. |

#### <span id="page-481-0"></span>7.7.13.22 Get VCS LDST Access Vector (Opcode 5715h)

<span id="page-481-4"></span>This command is used by the FM to query a VCS's current LAV.

This command will return Invalid Input when the requested byte range exceeds the size of the access vector buffer, as defined in [Table 7-164.](#page-485-3)

Possible Command Return Codes:

- Success
- Unsupported
- Invalid Input
- Internal Error
- Retry Required

**Command Effects:**

• None

<span id="page-481-3"></span>**Table 7-154. Get VCS LDST Access Vector Request Payload**

| Byte Offset | Length<br>in Bytes | Description                                              |
|-------------|--------------------|----------------------------------------------------------|
| 0h          | 1                  | VCS ID: ID of VCS to query.                              |
| 1h          | 3                  | Reserved                                                 |
| 4h          | 4                  | Start Byte: Offset in bytes into Vector Data.            |
| 8h          | 4                  | Number of Bytes: Size in bytes of Vector Data requested. |

<span id="page-481-5"></span>The Get VCS LDST Access Vector Response Payload is defined in [Table 7-152.](#page-480-3)

#### <span id="page-481-1"></span>7.7.13.23 Configure VCS LDST Access (Opcode 5716h)

This command is used by the FM to control access to a specified PID as reported in the LAV.

Possible Command return codes:

- Success
- Unsupported
- Invalid Input
- Internal Error
- Retry Required

Command Effects:

• None

<span id="page-482-2"></span>**Table 7-155. Configure VCS LDST Access Request Payload**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                           |
|-------------|--------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h          | 1                  | VCS ID: ID of VCS to configure.                                                                                                                                                                                                                                                                       |
| 1h          | 1                  | Reserved                                                                                                                                                                                                                                                                                              |
| 2h          | 2                  | •<br>Bits[11:0]: PID: PID of LDST or Completer ID-Based Re-Router target<br>•<br>Bits[14:12]: Operation: Specifies which configuration to perform:<br>— 000b = Enable PID access in the LAV<br>— 001b = Disable PID access in the LAV<br>— All other encodings are reserved<br>•<br>Bit[15]: Reserved |

### <span id="page-482-0"></span>7.7.14 Global Memory Access Endpoint Command Set

<span id="page-482-4"></span>This command set is used by a host to discover and manage the structures and devices involved in providing access to G-FAM and GIM resources.

#### <span id="page-482-1"></span>7.7.14.1 Identify GAE (Opcode 5800h)

<span id="page-482-5"></span>This command is used by the Host to query a GAE's capabilities, including maximum number of supported enabled PIDs and maximum number of simultaneous outstanding proxy operations and VendPrefixL0 support. It also reports the remaining number of proxy threads currently available.

Possible Command Return Codes:

- Success
- Unsupported
- Invalid Input
- Internal Error
- Retry Required

**Command Effects:**

• None

<span id="page-482-3"></span>**Table 7-156. Identify GAE Request Payload**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                              |
|-------------|--------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h          | 1                  | Start vPPB Instance: Index of vPPB whose FAST Segment Info should be<br>provided in the first entry in vPPB Global Memory Support Info List. The value of<br>0 represents the GAE. The values of 1 and above represent the DSP vPPBs in<br>increasing Device Number, Function Number order, as defined in Section 7.1.4. |
| 1h          | 1                  | Number of vPPBs: Number of vPPBs in vPPB Global Memory Support Info List.                                                                                                                                                                                                                                                |

<span id="page-483-1"></span>**Table 7-157. Identify GAE Response Payload**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
|-------------|--------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h          | 2                  | •<br>Bits[11:0]: Total Number of Supported Enabled PIDs: Maximum<br>number of PIDs that can be enabled for concurrent use with the Configure<br>VCS PID Access command<br>•<br>Bit[12]: Egress Request/Ingress Completion VendPrefixL0<br>Supported: Indicates whether VendPrefixL0 is supported (1) or not<br>supported (0) for Egress UIO Requests and Ingress UIO completions, as<br>configured by the FM for this host with the Set VendPrefixL0 State<br>command             |
|             |                    | •<br>Bit[13]: Ingress Request VendPrefixL0 Supported: Indicates whether<br>VendPrefixL0 is supported (1) or not supported (0) for Ingress UIO<br>requests, as configured by the FM for this host with the Set VendPrefixL0<br>State command<br>•<br>Bit[14]: G-FAM/GIM Configuration Supported: Indicates whether the<br>switch supports (1) or does not support (0) re-configuration of the GIM<br>Support bit with the Set FAST Segment Entry command<br>•<br>Bit[15]: Reserved |
| 2h          | 2                  | Total Number of Supported Threads: Maximum number of simultaneous<br>proxy operations supported by the GAE.                                                                                                                                                                                                                                                                                                                                                                       |
| 4h          | 2                  | Number of Available Threads: Remaining number of simultaneous proxy<br>operations supported by the GAE.                                                                                                                                                                                                                                                                                                                                                                           |
| 6h          | 1                  | Start vPPB Instance: Index of vPPB whose FAST Segment Info is provided in<br>the first entry in vPPB Global Memory Support Info List.                                                                                                                                                                                                                                                                                                                                             |
| 7h          | 1                  | Number of vPPBs: Number of vPPBs whose FAST Segment Info is provided in<br>the first entry in vPPB Global Memory Support Info List.                                                                                                                                                                                                                                                                                                                                               |
| 8h          | Varies             | vPPB Global Memory Support Info List: List of vPPB Global Memory Support<br>Info, as defined in Table 7-158, for the vPPBs identified with Start vPPB<br>Instance and Number of vPPBs.                                                                                                                                                                                                                                                                                            |

<span id="page-483-2"></span>**Table 7-158. vPPB Global Memory Support Info**

| Byte Offset | Length<br>in Bytes | Description                                                                                  |
|-------------|--------------------|----------------------------------------------------------------------------------------------|
| 0h          | 2                  | Number of FAST Segments: Total number of segments in the FAST for the<br>specified GAE/vPPB. |
| 2h          | 2                  | Reserved                                                                                     |

#### <span id="page-483-0"></span>7.7.14.2 Get PID Interrupt Vector (Opcode 5801h)

This command queries a GAE's PID interrupt vector.

Possible Command Return Codes:

- • Success
- Unsupported
- Invalid Input
- Internal Error
- Retry Required

**Command Effects:**

<span id="page-484-1"></span>**Table 7-159. Get PID Interrupt Vector Request Payload**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                                                               |
|-------------|--------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h          | 4                  | Start Byte: Offset in bytes into PID Interrupt Vector.                                                                                                                                                                                                                                                                                                    |
| 4h          | 4                  | Number of Bytes: Size in bytes of PID Interrupt Vector requested.                                                                                                                                                                                                                                                                                         |
| 8h          | 1                  | •<br>Bit[0]: Clear on Read: A value of 1 indicates that the PID Interrupt Vector<br>should be cleared to all 0s when this command completes. A GAE must<br>ensure that no interrupts are lost in between capturing the current PID<br>Interrupt Vector value for the response payload and clearing the vector's<br>contents.<br>•<br>Bits[7:1]: Reserved. |

<span id="page-484-2"></span>**Table 7-160. Get PID Interrupt Vector Response Payload**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                                                  |
|-------------|--------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h          | 4                  | Number of Bytes: Size in bytes of PID Interrupt Vector returned.                                                                                             |
| 4h          | Varies             | PID Interrupt Vector Data: Excerpt of data from PID Interrupt Vector,<br>defined in Table 7-161. Excerpt begins a Start Byte and is Number of Bytes<br>long. |

<span id="page-484-3"></span>**Table 7-161. PID Interrupt Vector**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                             |
|-------------|--------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 000h        | 200h               | PID Interrupt Vector: 4-Kb vector in which each bit corresponds to the<br>associated PID (i.e., bit n represents PID n). A value of 1 in a bit position<br>indicates that the GAE has received a GAM VDM from the corresponding PID<br>since the PID Interrupt Vector was last cleared. |

#### <span id="page-484-0"></span>7.7.14.3 Get PID Access Vectors (Opcode 5802h)

<span id="page-484-4"></span>This command is used by the Host to query a GAE's current GFD Mapping Vector and VendPrefixL0 Target Vector.

This command will return Invalid Input when the requested byte range exceeds the size of the access vector buffer, as defined in [Table 7-164.](#page-485-3)

Possible Command Return Codes:

- Success
- Unsupported
- Invalid Input
- Internal Error
- Retry Required

**Command Effects:**

<span id="page-485-1"></span>**Table 7-162. Get PID Access Vectors Request Payload**

| Byte Offset | Length<br>in Bytes | Description                                              |
|-------------|--------------------|----------------------------------------------------------|
| 0h          | 4                  | Start Byte: Offset in bytes into Vector Data.            |
| 1h          | 4                  | Number of Bytes: Size in bytes of Vector Data requested. |

<span id="page-485-2"></span>**Table 7-163. Get PID Access Vectors Response Payload**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                              |
|-------------|--------------------|------------------------------------------------------------------------------------------------------------------------------------------|
| 0h          | 4                  | Number of Bytes: Size in bytes of Vector Data returned.                                                                                  |
| 4h          | Varies             | Vector Data: Excerpt of data from PID Access Vector, defined in Table 7-164.<br>Excerpt begins a Start Byte and is Number of Bytes long. |

<span id="page-485-3"></span>**Table 7-164. PID Access Vector**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                                           |
|-------------|--------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 000h        | 200h               | GFD Mapping Vector: 4-Kb vector in which each bit corresponds to the<br>associated PID (i.e., bit n represents PID n). A value of 1 in a bit position<br>indicates that FAST access to the corresponding PID is enabled. A value of 0 in a<br>bit position indicates that access to the corresponding PID is blocked.                 |
| 200h        | 200h               | VendPrefixL0 Target Vector: 4-Kb vector in which each bit corresponds to<br>the associated PID (i.e., bit n represents PID n). A value of 1 in a bit position<br>indicates that VendPrefixL0 access to the corresponding PID is enabled. A value<br>of 0 in a bit position indicates that access to the corresponding PID is blocked. |

#### <span id="page-485-0"></span>7.7.14.4 Get FAST/IDT Capabilities (Opcode 5803h)

<span id="page-485-4"></span>This command is used by the Host to retrieve the GAE's FAST and IDT Capabilities, per [Section 7.7.2.4](#page-397-0).

The host should re-discover the FAST/IDT Capabilities of a vPPB after a Presence Detect Changed notification has been received indicating that an adapter is present if the vPPB supports Presence Detect, or when a Link Up is detected if the vPPB does not support Presence Detect.

Possible Command Return Codes:

- Success
- Unsupported
- Invalid Input
- Internal Error
- Retry Required

**Command Effects:**

<span id="page-486-1"></span>**Table 7-165. Get FAST/IDT Capabilities Request Payload**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                                                                            |
|-------------|--------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h          | 1                  | vPPB Instance: The value of 0 represents GAE. The values of 1 and above<br>represent the DSP vPPBs in increasing Device Number, Function Number order,<br>as defined in Section 7.1.4. |
| 1h          | 3                  | Reserved                                                                                                                                                                               |

<span id="page-486-2"></span>**Table 7-166. Get FAST/IDT Capabilities Response Payload**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                                                                             |
|-------------|--------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h          | 1                  | vPPB Instance: The value of 0 represents USP. The values of 1 and above<br>represent the DSP vPPBs in increasing Device Number, Function Number order,<br>as defined in Section 7.1.4.                                                                                                                                                                                  |
| 1h          | 2                  | Number of Segments: Number of FAST segments that are supported by this<br>FAST/IDT. The number of entries must be 0 or a power of 2.                                                                                                                                                                                                                                    |
| 3h          | 1                  | FAST Segment Size<br>•<br>Bits[2:0]: FSegSz per Table 7-81<br>•<br>Bits[7:3]: Reserved<br>The device shall return 0h if this value has not been initialized.                                                                                                                                                                                                            |
| 4h          | 2                  | Number of IDT: Number of Interleave Device Table entries supported by this<br>FAST/IDT.                                                                                                                                                                                                                                                                                 |
| 6h          | 1                  | vPPB PID List Length: Number of PIDs assigned to this vPPB, as reported in<br>vPPB PID List. Shall be 0 for vDSPs and vUSPs.                                                                                                                                                                                                                                            |
| 7h          | 1                  | •<br>Bit[0]: Egress Request/Ingress Completion VendPrefixL0 Enabled:<br>Indicates whether VendPrefixL0 is enabled (1) or disabled (0) for Egress<br>UIO Requests and Ingress UIO completions<br>•<br>Bit[1]: Ingress Request VendPrefixL0 Enabled: Indicates whether<br>VendPrefixL0 is enabled (1) or disabled (0) for Ingress UIO requests<br>•<br>Bit[7:2]: Reserved |
| 8h          | 2                  | Reserved                                                                                                                                                                                                                                                                                                                                                                |
| Ah          | 8                  | Fabric Base: Base HPA of this FAST.<br>The device shall return 0h if this value has not been initialized.                                                                                                                                                                                                                                                               |
| 12h         | 8                  | Fabric Limit: Upper HPA of this FAST.<br>The device shall return 0h if this value has not been initialized.                                                                                                                                                                                                                                                             |
| 1Ah         | Varies             | vPPB PID: List of PIDs assigned to this vPPB, as defined in Table 7-167.                                                                                                                                                                                                                                                                                                |

<span id="page-486-3"></span>**Table 7-167. vPPB PID List Entry Format**

| Byte Offset | Length<br>in Bytes | Description                                                                       |
|-------------|--------------------|-----------------------------------------------------------------------------------|
| 0h          | 2d                 | •<br>Bits[11:0]: vPPB PID: PID assigned to the vPPB<br>•<br>Bits[15:12]: Reserved |

#### <span id="page-486-0"></span>7.7.14.5 Set FAST/IDT Configuration (Opcode 5804h)

<span id="page-486-4"></span>This command is used by the Host to set the GAE's FAST and IDT Capabilities, per [Section 7.7.2.4](#page-397-0). Because the FabricBase and FabricLimit values must be aligned to the programmed FAST Segment Size, all three Host-chosen values are configured in one request.

Possible Command Return Codes:

- Success
- Unsupported
- Invalid Input
- Internal Error
- Retry Required

**Command Effects:**

• Immediate Configuration Change

<span id="page-487-1"></span>**Table 7-168. Set FAST/IDT Configuration Request Payload**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                                                                             |
|-------------|--------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h          | 1                  | vPPB Instance: The value of 0 represents USP. The values of 1 and above<br>represent the DSP vPPBs in increasing Device Number, Function Number order,<br>as defined in Section 7.1.4.                                                                                                                                                                                  |
| 1h          | 1                  | FAST Segment Size<br>•<br>Bits[2:0]: FSegSz per Table 7-81<br>•<br>Bits[7:3]: Reserved                                                                                                                                                                                                                                                                                  |
| 2h          | 1                  | •<br>Bit[0]: Enable Egress Request/Ingress Completion VendPrefixL0:<br>Configures whether VendPrefixL0 is enabled (1) or disabled (0) for Egress<br>UIO Requests and Ingress UIO completions<br>•<br>Bit[1]: Enable Ingress Request VendPrefixL0: Configures whether<br>VendPrefixL0 is enabled (1) or disabled (0) for Ingress UIO requests<br>•<br>Bit[7:2]: Reserved |
| 3h          | 1                  | Reserved                                                                                                                                                                                                                                                                                                                                                                |
| 4h          | 8                  | FabricBase: Base HPA of this FAST. FabricBase shall be aligned to the<br>programmed FAST Segment Size. The value 0h will disable this FAST/IDT<br>decoder.                                                                                                                                                                                                              |
| Ch          | 8                  | FabricLimit: Upper HPA of this FAST. Shall be greater than FabricBase. Shall be<br>aligned to the programmed FAST Segment Size. The value 0h will disable this<br>FAST/IDT decoder.                                                                                                                                                                                     |

#### <span id="page-487-0"></span>7.7.14.6 Get FAST Segment Entries (Opcode 5805h)

<span id="page-487-2"></span>This command reads the configuration of FAST Segment entries. The Host is responsible for mapping the GFAM range of HPAs to the appropriate number of available Segment Entries. Should the Host or the GAE have limited message payload capacity, the Host shall be responsible for breaking up the configuration operation into suitably sized requests.

Possible Command Return Codes:

- Success
- Unsupported
- Invalid Input
- Internal Error
- Retry Required

**Command Effects:**

<span id="page-488-0"></span>**Table 7-169. Get FAST Segment Entries Request Payload**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                          |
|-------------|--------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h          | 1                  | vPPB Instance: The value of 0 represents USP. The values of 1 and above<br>represent the DSP vPPBs in increasing Device Number, Function Number order,<br>as defined in Section 7.1.4.                                                                                                               |
| 1h          | 1                  | Reserved                                                                                                                                                                                                                                                                                             |
| 2h          | 2                  | Seg Count: Number of FAST Segment Entries requested. Value should be >0<br>and not more than the lesser of the total Segment table entries available, or<br>that number of entries that can be contained in the maximum message size<br>handled by the host and the target GAE.                      |
| 4h          | 2                  | Starting Segment Index: Index of the first segment being requested. An<br>index of 0 shall designate the configuration of the 1st Segment, corresponding to<br>HPA = FabricBase. The starting index Plus the Seg Count value shall not be larger<br>than the maximum segment entry number supported. |

<span id="page-488-1"></span>**Table 7-170. Get FAST Segment Entries Response Payload**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                              |
|-------------|--------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h          | 2                  | Seg Count: Number of FAST Segment Entries described in the Seg<br>Entry_List[ ]. Value should be >0 and not more than the lesser of the total<br>Segment table entries available, or that number of entries that can be contained<br>in the maximum message size handled by the host and the target GAE. |
| 2h          | 2                  | Starting Segment Index: Index of the first segment being returned. An index<br>of 0 shall designate the configuration of the 1st Segment, corresponding to HPA =<br>FabricBase. The starting index Plus the Seg Count value shall not be larger than<br>the maximum segment entry number supported.      |
| 4h          | Varies             | Segment List[ ]: List of Segment Entries as defined in Table 7-171.                                                                                                                                                                                                                                      |

<span id="page-488-2"></span>**Table 7-171. FAST Segment Entry Format**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                                                                                                  |
|-------------|--------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h          | 1                  | Valid<br>•<br>Bit[0]: Valid Entry: As per Figure 7-31<br>•<br>Bit[1]: GIM Segment: Segment used for GIM access<br>•<br>Bits[7:2]: Reserved                                                                                                                                                                                                                                                   |
| 1h          | 1                  | Intlv<br>•<br>Bits[3:0]: Interleave Mode: As per Table 7-82<br>•<br>Bits[7:4]: Reserved                                                                                                                                                                                                                                                                                                      |
| 2h          | 1                  | Gran<br>•<br>Bits[3:0]: Interleave Granularity: As per Table 7-83<br>•<br>Bits[7:4]: Reserved                                                                                                                                                                                                                                                                                                |
| 3h          | 1                  | Reserved                                                                                                                                                                                                                                                                                                                                                                                     |
| 4h          | 2                  | DPID/IX: DPID or IDT Index, depending on Intlv field value:<br>•<br>Bits[11:0]:<br>— If Intlv == 0, this is the actual DPID to which the GFAM request is to<br>be sent.<br>— Else, this is Index of the IDT entry that contains the DPID of the first<br>GFD in the interleave set. See Figure 7-31 and the description of<br>interleaving in Section 7.7.2.4.<br>•<br>Bits[15:12]: Reserved |
| 6h          | 2                  | Reserved                                                                                                                                                                                                                                                                                                                                                                                     |

#### <span id="page-489-0"></span>7.7.14.7 Set FAST Segment Entries (Opcode 5806h)

This command is used by the Host to set the configuration of FAST Segment entries. The Host is responsible for mapping the GFAM range of HPAs to the appropriate number of available Segment Entries, per [Section 7.7.2.4.](#page-397-0) Should the host or the GAE have limited message payload capacity, the Host shall be responsible for breaking up the configuration operation into suitably sized requests.

There are two types of segments: those that access G-FAM, and those that access GIM. Valid PID targets for G-FAM segments are defined in the GMV. Valid targets for GIM segments are defined in the VTV.

This command will complete with an Invalid Input status if the requester is not authorized to access the specified ID, as advertised by the GMV or VTV.

Possible Command Return Codes:

- Success
- Unsupported
- Invalid Input
- Internal Error
- Retry Required

**Command Effects:**

• Immediate Configuration Change

<span id="page-489-2"></span>**Table 7-172. Set FAST Segment Entries Request Payload**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                              |
|-------------|--------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h          | 1                  | vPPB Instance: The value of 0 represents USP. The values of 1 and above<br>represent the DSP vPPBs in increasing Device Number, Function Number order,<br>as defined in Section 7.1.4.                                                                                                                   |
| 1h          | 1                  | Reserved                                                                                                                                                                                                                                                                                                 |
| 2h          | 2                  | Seg Count: Number of FAST Segment Entries described in the Seg<br>Entry_List[ ]. Value should be >0 and not more than the lesser of the total<br>Segment table entries available, or that number of entries that can be contained<br>in the maximum message size handled by the host and the target GAE. |
| 4h          | 2                  | Starting Segment Index: Index of the first segment being configured. An<br>index of 0 shall designate the configuration of the 1st Segment, corresponding to<br>HPA = FabricBase. The starting index Plus the Seg Count value shall not be larger<br>than the maximum segment entry number supported.    |
| 6h          | Varies             | Segment List[ ]: List of Segment Entries as defined in Table 7-171.                                                                                                                                                                                                                                      |

#### <span id="page-489-1"></span>7.7.14.8 Get IDT DPID Entries (Opcode 5807h)

<span id="page-489-4"></span>This command reads the configuration of IDT entries. The Host is responsible for mapping the capacity of specific GFDs into interleaved regions of HPA. Should the Host or the GAE have limited message payload capacity, the Host shall be responsible for breaking up the configuration operation into suitably sized requests.

Possible Command Return Codes:

- Success
- Unsupported
- Invalid Input
- Internal Error

• Retry Required

**Command Effects:**

• None

<span id="page-490-1"></span>**Table 7-173. Get IDT DPID Entries Request Payload**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                              |
|-------------|--------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h          | 1                  | vPPB Instance: The value of 0 represents USP. The values of 1 and above<br>represent the DSP vPPBs in increasing Device Number, Function Number order,<br>as defined in Section 7.1.4.                                                                                   |
| 1h          | 1                  | Reserved                                                                                                                                                                                                                                                                 |
| 2h          | 2                  | IDT Entry Count: Number of IDT Entries requested. Value should be >0 and<br>not more than the lesser of the total IDT table entries available, or that number<br>of entries that can be contained in the maximum message size handled by the<br>host and the target GAE. |
| 4h          | 2                  | Starting IDT Entry Index: Index of the first IDT entry being requested. An<br>index of 0 shall designate the configuration of the 1st entry. The starting index Plus<br>the IDT Entry Count value shall not be larger than the maximum IDT entry<br>number supported.    |

<span id="page-490-2"></span>**Table 7-174. Get IDT DPID Entries Response Payload**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                             |
|-------------|--------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h          | 2                  | IDT Entry Count: Number of IDT Entries returned. Value should be >0 and not<br>more than the lesser of the total IDT table entries available, or that number of<br>entries that can be contained in the maximum message size handled by the<br>host and the target GAE. |
| 2h          | 2                  | Starting IDT Entry Index: Index of the first IDT entry being returned. An<br>index of 0 shall designate the configuration of the 1st entry. The starting index Plus<br>the IDT Entry Count value shall not be larger than the maximum IDT entry<br>number supported.    |
| 4h          | Varies             | IDT DPID[ ]: DPID of the GFD for the IDT entry. See Figure 7-31 and the<br>description of interleaving in Section 7.7.2.4.<br>Repeats IDT Entry Count number of times.<br>•<br>Bits[11:0]: PID of the target GFD<br>•<br>Bits[15:12]: Reserved                          |

#### <span id="page-490-0"></span>7.7.14.9 Set IDT DPID Entries (Opcode 5808h)

This command sets the configuration of IDT entries. The Host is responsible for mapping the capacity of specific GFDs into interleaved regions of HPA. Should the Host or the GAE have limited message payload capacity, the Host shall be responsible for breaking up the configuration operation into suitably sized requests.

Possible Command Return Codes:

- Success
- Unsupported
- Invalid Input
- Internal Error
- Retry Required

**Command Effects:**

• Immediate Configuration Change

<span id="page-491-1"></span>**Table 7-175. Set IDT DPID Entries Request Payload**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                     |
|-------------|--------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h          | 1                  | vPPB Instance: The value of 0 represents USP. The values of 1 and above<br>represent the DSP vPPBs in increasing Device Number, Function Number order,<br>as defined in Section 7.1.4.                                                                                          |
| 1h          | 1                  | Reserved                                                                                                                                                                                                                                                                        |
| 2h          | 2                  | IDT Entry Count: Number of IDT Entries being configured. Value should be >0<br>and not more than the lesser of the total IDT table entries available, or that<br>number of entries that can be contained in the maximum message size handled<br>by the host and the target GAE. |
| 4h          | 2                  | Starting IDT Entry Index: Index of the first IDT entry being configured. An<br>index of 0 shall designate the configuration of the 1st entry. The starting index Plus<br>the IDT Entry Count value shall not be larger than the maximum IDT entry<br>number supported.          |
| 6h          | 2                  | Reserved                                                                                                                                                                                                                                                                        |
| 8h          | Varies             | IDT DPID: DPID of the GFD for the IDT entry. See Figure 7-31 and the<br>description of interleaving in Section 7.7.2.4.<br>Repeats IDT Entry Count number of times.<br>•<br>Bits[11:0]: PID of the target GFD<br>•<br>Bits[15:12]: Reserved                                     |

#### <span id="page-491-0"></span>7.7.14.10 Proxy GFD Management Command (Opcode 5809h)

<span id="page-491-2"></span>This command is used to initiate the transfer of a management command to a GFD, as defined in [Section 3.1.11.1.](#page-98-2)

Only one proxy request may be outstanding per target PID regardless of the number of available proxy threads. A proxy request that targets a PID with an existing outstanding proxy request shall fail with 'Invalid Input'. The command shall fail with 'Resources Exhausted' if there are no available proxy operation threads.

The GAE increments and tracks Command Sequence Number on a per-Target PID basis.

This command will complete with an Invalid Input status if the requester is not authorized to access the specified ID, as advertised by the GMV.

Possible Command Return Codes:

- Success
- Unsupported
- Invalid Input
- Internal Error
- Retry Required
- Resources Exhausted

**Command Effects:**

<span id="page-492-1"></span>**Table 7-176. Proxy GFD Management Command Request Payload**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                                                                  |
|-------------|--------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 00h         | 2                  | •<br>Bits[11:0]: PBR-ID: Target PID for the management command<br>•<br>Bits[15:12]: Reserved                                                                                 |
| 02h         | 8                  | Request Address: Pointer to request message in Host memory that is<br>formatted in the CCI Message Format as defined in Figure 7-19.                                         |
| 0Ah         | 2                  | Request Size: Size of the request at Request Address in bytes.                                                                                                               |
| 0Ch         | 8                  | Response Address: Pointer in Host memory at which the response should be<br>written. The response shall be formatted in the CCI Message Format as defined<br>in Figure 7-19. |
| 14h         | 2                  | Maximum Response Size: Size of the response at Request Address in bytes.                                                                                                     |

<span id="page-492-2"></span>**Table 7-177. Proxy GFD Management Command Response Payload**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                                  |
|-------------|--------------------|----------------------------------------------------------------------------------------------------------------------------------------------|
| 0h          | 1                  | •<br>Bits[2:0]: Command Sequence Number: Proxy thread identifier for use<br>with Get Proxy Thread Status request<br>•<br>Bits[7:3]: Reserved |
| 1h          | 2                  | Number of Available Threads: Remaining number of simultaneous proxy<br>operations supported by the GAE.                                      |

#### <span id="page-492-0"></span>7.7.14.11 Get Proxy Thread Status (Opcode 580Ah)

<span id="page-492-4"></span>This command queries whether the GAE is tracking the specified Command Sequence Number and Target PID as 'In Progress'.

Possible Command Return Codes:

- Success
- Unsupported
- Invalid Input
- Internal Error
- Retry Required

**Command Effects:**

• None

<span id="page-492-3"></span>**Table 7-178. Get Proxy Thread Status Request Payload**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                                                                                                        |
|-------------|--------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h          | 2                  | •<br>Bits[11:0]: PBR-ID: Target PID for the management command<br>•<br>Bits[14:12]: Command Sequence Number: Proxy thread identifier<br>returned by Proxy GFD Management Command request<br>•<br>Bit[15]: Reserved |

<span id="page-493-2"></span>**Table 7-179. Get Proxy Thread Status Response Payload**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                |
|-------------|--------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h          | 1                  | •<br>Bit[0]: In Progress: A value of 1 indicates that the GAE is tracking the<br>specified Thread Handle. A value of 0 indicates that the GAE is not tracking<br>the specified Thread Handle.<br>•<br>Bits[7:1]: Reserved. |
| 1h          | 1                  | Reserved                                                                                                                                                                                                                   |
| 2h          | 2                  | Number of Available Threads: Remaining number of simultaneous proxy<br>operations supported by the GAE.                                                                                                                    |

#### <span id="page-493-0"></span>7.7.14.12 Cancel Proxy Thread (Opcode 580Bh)

<span id="page-493-5"></span>This command effectively cancels a proxy thread that is in progress by instructing the GAE to no longer track the specified thread handle as 'In Progress'. The GAE shall discard any transactions associated with threads that are not being tracked as 'In Progress'.

Possible Command Return Codes:

- Success
- Unsupported
- Invalid Input
- Internal Error
- Retry Required

**Command Effects:**

• None

<span id="page-493-3"></span>**Table 7-180. Cancel Proxy Thread Request Payload**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                                                                                                        |
|-------------|--------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h          | 2                  | •<br>Bits[11:0]: PBR-ID: Target PID for the management command<br>•<br>Bits[14:12]: Command Sequence Number: Proxy thread identifier<br>returned by Proxy GFD Management Command request<br>•<br>Bit[15]: Reserved |

<span id="page-493-4"></span>**Table 7-181. Cancel Proxy Thread Response Payload**

| Byte Offset | Length<br>in Bytes | Description                                                                                             |
|-------------|--------------------|---------------------------------------------------------------------------------------------------------|
| 0h          | 2                  | Number of Available Threads: Remaining number of simultaneous proxy<br>operations supported by the GAE. |

### <span id="page-493-1"></span>7.7.15 Global Memory Access Endpoint Management Command Set

This command set is used by the FM to discover and manage the structures and devices involved in providing access to G-FAM and GIM resources.

#### <span id="page-494-0"></span>7.7.15.1 Identify VCS GAE (Opcode 5900h)

<span id="page-494-3"></span>This command is used by the FM to query a GAE's capabilities, including maximum number of supported enabled PIDs and maximum number of simultaneous outstanding proxy operations and VendPrefixL0 support. It also reports the remaining number of proxy threads currently available.

Possible Command Return Codes:

- Success
- Unsupported
- Invalid Input
- Internal Error
- Retry Required

**Command Effects:**

• None

<span id="page-494-2"></span>**Table 7-182. Identify VCS GAE Request Payload**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                              |
|-------------|--------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h          | 1                  | VCS ID: ID of VCS to query.                                                                                                                                                                                                                                                                                              |
| 1h          | 1                  | Start vPPB Instance: Index of vPPB whose FAST Segment Info should be<br>provided in the first entry in vPPB Global Memory Support Info List. The value of<br>0 represents the GAE. The values of 1 and above represent the DSP vPPBs in<br>increasing Device Number, Function Number order, as defined in Section 7.1.4. |
| 2h          | 1                  | Number of vPPBs: Number of vPPBs whose FAST Segment Info should be<br>provided in vPPB Global Memory Support Info List.                                                                                                                                                                                                  |

<span id="page-494-4"></span>The Identify VCS GAE Response Payload is defined in [Table 7-157.](#page-483-1)

#### <span id="page-494-1"></span>7.7.15.2 Get VCS PID Access Vectors (Opcode 5901h)

This command is used by the FM to query a GAE's current GFD Mapping Vector and VendPrefixL0 Target Vector.

This command will return Invalid Input under the following conditions:

- The requested byte range exceeds the size of the access vector buffer, as defined in [Table 7-164](#page-485-3)
- The specified VCS does not include a GAE

Possible Command Return Codes:

- Success
- Unsupported
- Invalid Input
- Internal Error
- Retry Required

**Command Effects:**

<span id="page-495-1"></span>**Table 7-183. Get VCS PID Access Vectors Request Payload**

| Byte Offset | Length<br>in Bytes | Description                                              |
|-------------|--------------------|----------------------------------------------------------|
| 0h          | 1                  | VCS ID: ID of VCS to query.                              |
| 1h          | 3                  | Reserved                                                 |
| 4h          | 4                  | Start Byte: Offset in bytes into Vector Data.            |
| 8h          | 4                  | Number of Bytes: Size in bytes of Vector Data requested. |

<span id="page-495-3"></span>The Get VCS PID Access Vectors Response Payload is defined in [Table 7-163.](#page-485-2)

#### <span id="page-495-0"></span>7.7.15.3 Configure VCS PID Access (Opcode 5902h)

This command is used by the FM to control access to a specified PID as reported in the GFD Mapping Vector or VendPrefixL0 Target Vector. It is used by the FM to enable or disable access to a PID from a GAE.

Possible Command return codes:

- Success
- Unsupported
- Invalid Input
- Internal Error
- Retry Required

Command Effects:

<span id="page-495-2"></span>**Table 7-184. Configure VCS PID Access Request Payload**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                                                                                                           |
|-------------|--------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h          | 1                  | VCS ID: ID of VCS to configure.                                                                                                                                                                                                                                                                                                                                                                       |
| 1h          | 1                  | Reserved                                                                                                                                                                                                                                                                                                                                                                                              |
| 2h          | 2                  | •<br>Bits[11:0]: PID: PID of GFD or VendPrefixL0 target<br>•<br>Bits[14:12]: Operation: Specifies which configuration to perform:<br>— 000b = Enable PID access in the GMV<br>— 001b = Disable PID access in the GMV<br>— 010b = Enable PID access in the VTV<br>— 011b = Disable PID access in the VTV<br>— 100b = Update Latency/BW<br>— All other encodings are reserved<br>•<br>Bit[15]: Reserved |
| 4h          | 8                  | Latency Entry Base Unit: Latency Entry Base Unit for path between host and<br>target device, as defined in ACPI HMAT System Locality Latency and Bandwidth<br>Information Structure. Reserved when Operation is 001b or 011b.                                                                                                                                                                         |
| Ch          | 2                  | Latency Entry: Latency Entry for path between host and target device, as<br>defined in ACPI HMAT System Locality Latency and Bandwidth Information<br>Structure. Reserved when Operation is 001b or 011b.                                                                                                                                                                                             |
| Eh          | 8                  | BW Entry Base Unit: Bandwidth Entry Base Unit for path between host and<br>target device, as defined in ACPI HMAT System Locality Latency and Bandwidth<br>Information Structure. Reserved when Operation is 001b or 011b.                                                                                                                                                                            |
| 16h         | 2                  | BW Entry: Bandwidth Entry for path between host and target device, as<br>defined in ACPI HMAT System Locality Latency and Bandwidth Information<br>Structure. Reserved when Operation is 001b or 011b.                                                                                                                                                                                                |

#### <span id="page-496-0"></span>7.7.15.4 Get VendPrefixL0 State (Opcode 5903h)

<span id="page-496-4"></span>This command is used by the FM to query the enable state of VendPrefixL0 in a VCS. Support for this command indicates whether a PBR switch supports VendPrefixL0. The **Get VendPrefixL0 State** command shall only be implemented by PBR switches that support VendPrefixL0.

Possible Command Return Codes:

- Success
- Unsupported
- Invalid Input
- Internal Error
- Retry Required

**Command Effects:**

• None

<span id="page-496-2"></span>**Table 7-185. Get VendPrefixL0 State Request Payload**

| Byte Offset | Length<br>in Bytes | Description                                             |
|-------------|--------------------|---------------------------------------------------------|
| 0h          | 1                  | VCS ID: ID of the VCS to which the GAE or vPPB belongs. |

<span id="page-496-3"></span>**Table 7-186. Get VendPrefixL0 State Response Payload**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                                                                                                                                                  |
|-------------|--------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0h          | 1                  | •<br>Bit[0]: Egress Request/Ingress Completion VendPrefixL0 Enabled:<br>Indicates whether support for VendPrefixL0 is enabled (1) or disabled (0)<br>for Egress UIO Requests and Ingress UIO completions in the specified VCS<br>•<br>Bit[1]: Ingress Request VendPrefixL0 Enabled: Indicates whether<br>support for VendPrefixL0 is enabled (1) or disabled (0) for Ingress UIO<br>requests in the specified VCS<br>•<br>Bit[7:2]: Reserved |

#### <span id="page-496-1"></span>7.7.15.5 Set VendPrefixL0 State (Opcode 5904h)

<span id="page-496-5"></span>This command is used by the FM to enable or disable support for VendPrefixL0 in a VCS. Support for this command indicates whether a PBR switch supports VendPrefixL0; it shall be implemented by and shall only be implemented by PBR switches that support VendPrefixL0.

Possible Command Return Codes:

- Success
- Unsupported
- Invalid Input
- Internal Error
- Retry Required

**Command Effects:**

<span id="page-497-0"></span>**Table 7-187. Set VendPrefixL0 State Request Payload**

| Byte Offset | Length<br>in Bytes | Description                                                                                                                                                                                                                                                                                                                                                                                   |  |  |  |  |  |
|-------------|--------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--|--|--|--|--|
| 0h          | 1                  | VCS ID: ID of the VCS to configure.                                                                                                                                                                                                                                                                                                                                                           |  |  |  |  |  |
| 1h          | 1                  | Reserved                                                                                                                                                                                                                                                                                                                                                                                      |  |  |  |  |  |
| 2h          | 1                  | •<br>Bit[0]: Enable Egress Request/Ingress Completion VendPrefixL0:<br>Enables (1) or disables (0) support for VendPrefixL0 for Egress UIO<br>Requests and Ingress UIO completions in the specified VCS<br>•<br>Bit[1]: Enable Ingress Request VendPrefixL0: Enables (1) or disables<br>(0) support for VendPrefixL0 for Ingress UIO requests in the specified VCS<br>•<br>Bit[7:2]: Reserved |  |  |  |  |  |

**§ §**

![](_page_498_Picture_1.jpeg)
